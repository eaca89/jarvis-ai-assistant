"""Part 5 - Hands: real things JARVIS can do on your PC. The docstrings tell the brain what each one does."""
import os, re, subprocess, urllib.parse, urllib.request, webbrowser
from pathlib import Path
from ddgs import DDGS
import memory

SAFE_FOLDER = Path.home() / "Documents"      # JARVIS may only read files in here
APPS = {"notepad": "notepad", "calculator": "calc", "spotify": "spotify:",
        "explorer": "explorer", "settings": "ms-settings:"}

def open_app(name: str) -> str:
    """Open an app on this Windows PC. name: notepad, calculator, spotify, explorer or settings."""
    target = APPS.get(name.lower())
    if not target:
        return f"I don't know the app '{name}'. I can open: {', '.join(APPS)}."
    if target.endswith(":"):
        os.startfile(target)                     # Windows URI apps
    else:
        subprocess.Popen(target)
    return f"Opened {name}."

PROCESSES = {"notepad": "notepad.exe", "calculator": "CalculatorApp.exe",
             "spotify": "Spotify.exe", "settings": "SystemSettings.exe"}   # never explorer: it's the desktop

def close_app(name: str) -> str:
    """Close every window of an app on this Windows PC. name: notepad, calculator, spotify or settings."""
    process = PROCESSES.get(name.lower())
    if not process:
        return f"I can't close '{name}'. I can close: {', '.join(PROCESSES)}."
    done = subprocess.run(["taskkill", "/IM", process, "/F"], capture_output=True, text=True)
    if done.returncode != 0:
        return f"Failed: {name} doesn't seem to be open."
    return f"Closed {name}."

MEDIA_KEYS = {"volume_up": 0xAF, "volume_down": 0xAE, "mute": 0xAD,
              "play_pause": 0xB3, "next": 0xB0, "previous": 0xB1}

def media(action: str, times: int = 3) -> str:
    """Control sound and music on this PC. action: volume_up, volume_down, mute, play_pause, next or previous.
    times: how many steps for volume (each step is 2%)."""
    import ctypes
    key = MEDIA_KEYS.get(action)
    if key is None:
        return f"Failed: unknown action '{action}'."
    for _ in range(times if action.startswith("volume") else 1):
        ctypes.windll.user32.keybd_event(key, 0, 0, 0)          # press
        ctypes.windll.user32.keybd_event(key, 0, 2, 0)          # release
    return f"Done: {action.replace('_', ' ')}."

def open_website(url: str) -> str:
    """Open a website in the default browser, e.g. youtube.com."""
    webbrowser.open(url if url.startswith("http") else "https://" + url)
    return f"Opened {url}."

def find_youtube_video(query):
    """Return the id of the top YouTube result, or None. No API key needed."""
    url = "https://www.youtube.com/results?search_query=" + urllib.parse.quote_plus(query)
    try:
        page = urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"}),
                                      timeout=8).read().decode("utf-8", "ignore")
        found = re.search(r'"videoId":"([A-Za-z0-9_-]{11})"', page)
        if found:
            return found.group(1)
    except OSError:
        pass
    for result in DDGS().videos(query, max_results=5):          # backup: DuckDuckGo video search
        found = re.search(r"(?:v=|youtu\.be/)([A-Za-z0-9_-]{11})", result.get("content", ""))
        if found:
            return found.group(1)
    return None

def play_youtube(query: str) -> str:
    """Find a YouTube video matching the query and play it in the browser, e.g. 'persian jazz fusion'."""
    video = find_youtube_video(query)
    if not video:
        return f"Failed: no YouTube video found for '{query}'."
    webbrowser.open(f"https://www.youtube.com/watch?v={video}&autoplay=1")
    return f"Playing the top YouTube result for '{query}'."

def web_search(query: str) -> str:
    """Search the web and return the top 3 results (title and snippet)."""
    results = DDGS().text(query, max_results=3)
    return "\n".join(f"- {r['title']}: {r['body']}" for r in results) or "No results."

def read_file(filename: str) -> str:
    """Read a text file from the user's Documents folder."""
    path = (SAFE_FOLDER / filename).resolve()
    if SAFE_FOLDER.resolve() not in path.parents:
        return "I can only read files inside Documents."
    if not path.exists():
        return f"No file called {filename} in Documents."
    return path.read_text(encoding="utf-8", errors="ignore")[:4000]

def remember(fact: str) -> str:
    """Save a lasting fact about the user, e.g. 'likes jazz' or 'works out at 7am'."""
    memory.add_fact(CURRENT_USER, fact)
    return "Saved."

CURRENT_USER = "me"
TOOLS = [open_app, close_app, media, open_website, play_youtube, web_search, read_file, remember]
