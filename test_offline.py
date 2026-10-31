"""Checks memory, tools and the agent loop without a mic, speakers or API key (the model is faked)."""
import os, types as pytypes
os.environ.setdefault("GEMINI_API_KEY", "fake")
from google.genai import types
import brain, memory

class FakeModels:
    """Turn 1: ask for remember(). Turn 2: reply with text."""
    def __init__(self): self.n = 0
    def generate_content(self, model, contents, config):
        self.n += 1
        if self.n == 1:
            part = types.Part(function_call=types.FunctionCall(name="remember", args={"fact": "likes jazz"}))
        else:
            part = types.Part(text="Noted, sir. Jazz it is.")
        return types.GenerateContentResponse(candidates=[types.Candidate(
            content=types.Content(role="model", parts=[part]))])

brain.client = pytypes.SimpleNamespace(models=FakeModels())
print("reply:", brain.think("test", "Remember that I like jazz"))
print("facts:", memory.facts("test"))
assert "likes jazz" in memory.facts("test")
print("system prompt includes fact:", "likes jazz" in brain.system_prompt("test"))
print("OK")

# Busy brain: first model returns 503, backup answers
from google.genai import errors
class BusyModels:
    def generate_content(self, model, contents, config):
        if model == brain.MODEL:
            raise errors.ServerError(503, {"error": {"code": 503, "message": "busy", "status": "UNAVAILABLE"}})
        return types.GenerateContentResponse(candidates=[types.Candidate(
            content=types.Content(role="model", parts=[types.Part(text=f"Answered by {model}, sir.")]))])
brain.client = pytypes.SimpleNamespace(models=BusyModels())
brain.time.sleep = lambda s: None
print("busy test:", brain.think("test", "hello"))
assert brain.BACKUP in brain.think("test", "hello")
print("OK busy")
