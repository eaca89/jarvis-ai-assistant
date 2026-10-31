# JARVIS: run it on your PC (Windows 11, Python 3.13)

The code from the Microlearn video "I Built a JARVIS AI Assistant That Can Talk Back and Control My PC": https://youtu.be/hNjBamiUPD0

100% free: Gemini free tier (brain), faster-whisper on your CPU (ears), Edge voices (mouth), SQLite (memory), DuckDuckGo search, Telegram. No GPU needed.

## 1. Get a free Gemini key (2 min)
1. Go to https://aistudio.google.com/apikey and sign in with Google.
2. Click **Create API key**. Copy it.
3. **Never turn on billing** for that project. Without billing it can't charge you; when you hit the daily limit it simply says "quota exceeded" until the limit resets the next day.
4. Open https://aistudio.google.com/rate-limit to see your limits. They depend on the model (JARVIS uses `gemini-flash-lite-latest`, with `gemini-flash-latest` as the backup), and some models get surprisingly few requests a day.

## 2. Install
In PowerShell, inside this folder:
```
py -3.13 -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
notepad .env          # paste your Gemini key
```
The first run downloads the Whisper "base.en" model (~140 MB) once (set `WHISPER_MODEL=small.en` in `.env` for more accuracy, ~460 MB).

## 3. Run, in this order (each one writes to logs/run.jsonl)
1. `python test_offline.py`: no mic or key needed; should print OK.
2. `python jarvis.py`: say these, one at a time:
   - "Hello JARVIS, can you hear me?"
   - "Remember that I make YouTube videos about AI."
   - "Open notepad."
   - "Search the web for who voiced JARVIS in Iron Man."
   - "What do you know about me?"  (tests memory)
   - "Goodbye."
3. Telegram: make a bot with @BotFather, get your id from @userinfobot, put both in `.env`, then `python telegram_bridge.py` and from your phone send: "Open calculator on my PC", then "What do you know about me?"

## The HUD
`python jarvis.py` opens the JARVIS screen in its own window, always on top of your other windows (set `HUD=browser` in `.env` for a browser tab instead).
Drag the window corner to resize it. The orb follows your voice, turns amber while thinking and pulses while speaking;
the left panel is the conversation, the right panel shows each tool JARVIS runs plus CPU and memory.
The MIC button mutes the microphone (everything turns red).

## Files = chapters
| File | Chapter |
|---|---|
| ears.py | 1 Ears |
| brain.py | 2 Brain (the agent loop) |
| mouth.py | 3 Mouth |
| memory.py | 4 Memory |
| hands.py | 5 Hands |
| telegram_bridge.py | 6 Remote |
| ui.py + hud.html | the JARVIS screen |
| jarvis.py | ties it all together |

## If something breaks
- "No sound device" / mic silent: Windows Settings → Privacy → Microphone → allow desktop apps. In `ears.py`, lower `threshold` to 0.005 if it never hears you.
- "429 / quota exceeded": you hit one of the free limits. If it's the per-minute one, wait a minute; if it's the daily one, wait until it resets the next day (check https://aistudio.google.com/rate-limit). Don't add billing.
- Telegram does nothing: telegram_bridge.py must be running in its own PowerShell window (jarvis.py in another). Its window prints every message it gets.
- "503 high demand": Google's free model is busy. JARVIS now retries, then switches to the backup model (`GEMINI_BACKUP_MODEL`) by itself.
- "model not found": in `.env` set `GEMINI_MODEL` to the Flash model name shown in AI Studio.
- A pip error mentioning two Pythons: use the `.venv` above; it keeps everything on 3.13.
