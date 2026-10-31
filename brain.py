"""Part 2 - Brain: Gemini (free tier) reads what you said and either replies or picks a tool.
Same agent loop as the AI agent video: think -> act -> observe -> repeat."""
import json, os, time
from dotenv import load_dotenv
from google import genai
from google.genai import errors, types
import hands, memory, ui

load_dotenv()
client = genai.Client()                                     # reads GEMINI_API_KEY
MODEL = os.getenv("GEMINI_MODEL", "gemini-flash-lite-latest")       # fastest free model: ~0.6 s
BACKUP = os.getenv("GEMINI_BACKUP_MODEL", "gemini-flash-latest")   # used when MODEL is busy
TOOLS = {f.__name__: f for f in hands.TOOLS}
os.makedirs("logs", exist_ok=True)

def log(event, **data):
    ui.emit(event, **data)                                  # show it on the HUD too
    with open("logs/run.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps({"t": time.strftime("%H:%M:%S"), "event": event, **data}) + "\n")

def system_prompt(user):
    known = "\n".join(f"- {f}" for f in memory.facts(user)) or "- nothing yet"
    return ("You are JARVIS, a calm, witty British assistant. Call the user 'sir'. "
            "Your replies are spoken aloud, so keep them to one or two short sentences, no lists or markdown. "
            "Use a tool whenever the user asks you to do something. "
            "Only say something is done if a tool result says it worked. "
            "If no tool can do it, or a tool failed, say so honestly. "
            f"What you know about the user:\n{known}")

def ask(contents, config):
    """One call to the brain. If Google is busy (503/429), wait, retry, then switch to the backup model."""
    for model, wait in [(MODEL, 0), (MODEL, 2), (BACKUP, 0), (BACKUP, 2)]:
        time.sleep(wait)
        start = time.time()
        try:
            response = client.models.generate_content(model=model, contents=contents, config=config)
            log("brain", model=model, seconds=round(time.time() - start, 1))
            return response
        except errors.APIError as e:
            log("busy", model=model, code=e.code, seconds=round(time.time() - start, 1))
            if e.code not in (429, 500, 503, 504):
                raise
    return None

def think(user, text, max_steps=5):
    hands.CURRENT_USER = user
    ui.emit("state", state="thinking")
    log("heard", user=user, text=text)
    contents = [types.Content(role="user" if r == "user" else "model", parts=[types.Part(text=t)])
                for r, t in memory.recent(user)]
    contents.append(types.Content(role="user", parts=[types.Part(text=text)]))
    config = types.GenerateContentConfig(
        system_instruction=system_prompt(user), tools=hands.TOOLS,
        automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
        http_options=types.HttpOptions(timeout=10_000, retry_options=types.HttpRetryOptions(attempts=1)))

    for step in range(max_steps):                                  # the loop
        response = ask(contents, config)                           # think
        if response is None:
            reply = "Sorry sir, my brain in the cloud is busy. Try again in a moment."
            break
        contents.append(response.candidates[0].content)
        if not response.function_calls:                            # no tool needed: done
            reply = response.text.strip()
            break
        parts = []
        for call in response.function_calls:                       # act
            try:
                result = TOOLS[call.name](**call.args)
            except Exception as e:
                result = f"Error: {e}"
            log("tool", name=call.name, args=dict(call.args), result=result[:300])
            parts.append(types.Part.from_function_response(name=call.name, response={"result": result}))
        contents.append(types.Content(role="user", parts=parts))   # observe
    else:
        reply = "Sorry sir, that took too many steps."

    memory.save_turn(user, "user", text)
    memory.save_turn(user, "model", reply)
    log("reply", user=user, text=reply)
    return reply
