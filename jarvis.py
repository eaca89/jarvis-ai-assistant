"""JARVIS on your PC: listen -> think -> speak, forever. Press Ctrl+C to stop."""
import time
from ears import listen
from brain import think, log
from mouth import speak
import ui

def main():
    print("JARVIS is listening. Say something...")
    speak("Online and ready, sir.")
    while True:
        heard = listen()
        ears = listen.seconds                     # Whisper time only, not your talking
        if not heard:
            continue
        print("You:", heard)
        if "goodbye" in heard.lower().replace(" ", ""):
            speak("Goodbye, sir.")
            return
        t = time.time()
        reply = think("me", heard)
        brain = time.time() - t
        print("JARVIS:", reply)
        t = time.time()
        speak(reply)
        log("timing", whisper=ears, brain=round(brain, 1), first_sound=speak.first_sound, mouth=round(time.time() - t, 1))
        print(f"(whisper {ears:.1f} s, brain {brain:.1f} s, voice starts {speak.first_sound:.1f} s)")

ui.run(main)                                  # JARVIS window on top + the loop
