"""Part 1 - Ears: record from the mic until you stop talking, then turn it into text."""
import os, time
import numpy as np
import sounddevice as sd
from faster_whisper import WhisperModel
import ui

RATE = 16000
model = WhisperModel(os.getenv("WHISPER_MODEL", "base.en"), device="cpu", compute_type="int8")  # base.en: ~3x faster than small.en

def record(max_seconds=15, silence_seconds=0.7, threshold=0.01):
    chunks, quiet, started = [], 0.0, False
    with sd.InputStream(samplerate=RATE, channels=1, dtype="float32") as mic:
        for _ in range(int(max_seconds * 10)):
            chunk, _ = mic.read(RATE // 10)                  # 0.1 s at a time
            volume = float(np.sqrt(np.mean(chunk ** 2)))
            ui.emit("level", level=volume)                   # the orb grows with your voice
            loud = volume > threshold
            started |= loud
            if started:
                chunks.append(chunk)
                quiet = 0.0 if loud else quiet + 0.1
                if quiet >= silence_seconds:                 # you stopped talking
                    break
    return np.concatenate(chunks).flatten() if chunks else np.zeros(0, "float32")

def listen():
    if ui.muted:                                             # HUD mute button
        time.sleep(0.3)
        return ""
    ui.emit("state", state="listening")
    audio = record()
    if audio.size == 0:
        return ""
    start = time.time()
    segments, _ = model.transcribe(audio, language="en", vad_filter=True, beam_size=1,
                                   initial_prompt="Talking to JARVIS, my AI assistant.")  # so it knows the name
    text = " ".join(s.text.strip() for s in segments)    # transcription happens here
    listen.seconds = round(time.time() - start, 1)
    return text
listen.seconds = 0.0
