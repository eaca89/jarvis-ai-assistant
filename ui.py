"""The HUD: a local web page that shows what JARVIS is doing, live.
Python pushes events to the page with Server-Sent Events (built into Python, no extra server)."""
import json, os, queue, threading, webbrowser
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from pathlib import Path
import psutil

PORT = 8765
clients = []
muted = False
started = False

def emit(event, **data):
    """Send one event (state, heard, reply, tool, level) to every open HUD page."""
    if not started:
        return
    for q in list(clients):
        q.put({"event": event, **data})

def _stats():
    while True:
        net = psutil.net_io_counters()
        emit("stats", cpu=psutil.cpu_percent(interval=1), ram=psutil.virtual_memory().percent,
             net=round((net.bytes_sent + net.bytes_recv) / 1e6))

class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def do_GET(self):
        if self.path == "/events":
            self.send_response(200)
            self.send_header("Content-Type", "text/event-stream")
            self.send_header("Cache-Control", "no-cache")
            self.end_headers()
            q = queue.Queue()
            clients.append(q)
            q.put({"event": "mute", "muted": muted})
            try:
                while True:
                    self.wfile.write(f"data: {json.dumps(q.get())}\n\n".encode())
                    self.wfile.flush()
            except OSError:
                clients.remove(q)
        else:
            page = Path(__file__).with_name("hud.html").read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(page)

    def do_POST(self):
        global muted
        if self.path == "/mute":
            muted = not muted
            emit("mute", muted=muted)
            emit("state", state="muted" if muted else "listening")
        self.send_response(204)
        self.end_headers()

def start(open_browser=True):
    global started
    started = True
    global PORT
    for port in [PORT, 8770, 8780, 5050, 0]:      # Windows reserves some ports; 0 = any free port
        try:
            server = ThreadingHTTPServer(("127.0.0.1", port), Handler)
            break
        except OSError:
            continue
    PORT = server.server_address[1]
    print(f"HUD: http://127.0.0.1:{PORT}")
    threading.Thread(target=server.serve_forever, daemon=True).start()
    threading.Thread(target=_stats, daemon=True).start()
    if open_browser:
        webbrowser.open(f"http://127.0.0.1:{PORT}")

def run(loop):
    """Show the HUD in its own window (always on top) and run JARVIS's loop behind it.
    Set HUD=browser in .env to use a browser tab instead."""
    mode = os.getenv("HUD", "app")
    if mode == "app":                              # Edge/Chrome app window: no tabs, fast graphics
        start(open_browser=False)
        url = f"http://127.0.0.1:{PORT}"
        for exe in [r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
                    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
                    r"C:\Program Files\Google\Chrome\Application\chrome.exe"]:
            if os.path.exists(exe):
                import subprocess
                subprocess.Popen([exe, f"--app={url}", "--window-size=1400,820"])
                break
        else:
            webbrowser.open(url)
        return loop()
    use_window = mode == "window"
    start(open_browser=not use_window)
    if use_window:
        try:
            import webview
        except ImportError:
            print("pywebview not installed, opening the browser instead.")
            webbrowser.open(f"http://127.0.0.1:{PORT}")
            use_window = False
    if not use_window:
        return loop()
    webview.create_window("JARVIS", f"http://127.0.0.1:{PORT}", width=1280, height=760,
                          min_size=(900, 560), on_top=True, background_color="#04070c")
    webview.start(lambda: (loop(), os._exit(0)))    # loop runs beside the window; closing either ends JARVIS
    os._exit(0)
