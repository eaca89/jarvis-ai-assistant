"""Part 3 - Mouth: turn JARVIS's reply into speech and play it.
Speaks sentence by sentence: sentence 2 is made while sentence 1 is playing."""
import asyncio, os, re, tempfile, threading, time
import edge_tts
from playsound3 import playsound
import ui

VOICE = "en-GB-RyanNeural"   # a calm British voice, free, no key

def _make(text, path):
    asyncio.run(edge_tts.Communicate(text, VOICE, rate="+10%").save(path))

def speak(text):
    start = time.time()
    sentences = [s for s in re.split(r"(?<=[.!?])\s+", text.strip()) if s]
    paths = [os.path.join(tempfile.gettempdir(), f"jarvis_{i}.mp3") for i in range(len(sentences))]
    _make(sentences[0], paths[0])
    speak.first_sound = round(time.time() - start, 1)      # what feels slow: silence before JARVIS starts
    ui.emit("state", state="speaking")
    for i in range(len(sentences)):
        nxt = None
        if i + 1 < len(sentences):                       # make the next one in the background
            nxt = threading.Thread(target=_make, args=(sentences[i + 1], paths[i + 1]))
            nxt.start()
        playsound(paths[i])
        if nxt:
            nxt.join()

speak.first_sound = 0.0
