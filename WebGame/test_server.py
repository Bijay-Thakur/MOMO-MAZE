import http.server
import socketserver
import threading
import urllib.request
import time
import os

PORT = 8092
DIR = r"D:\Projects\MOMO MAZE\WebGame"

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIR, **kwargs)

httpd = socketserver.TCPServer(("127.0.0.1", PORT), Handler)
t = threading.Thread(target=httpd.serve_forever, daemon=True)
t.start()
time.sleep(0.5)

endpoints = ["index.html", "js/game.js", "js/three.module.js", "js/game_data.js", "css/style.css"]
success = True

for ep in endpoints:
    url = f"http://127.0.0.1:{PORT}/{ep}"
    try:
        with urllib.request.urlopen(url, timeout=3) as res:
            data = res.read()
            print(f"✓ {ep}: HTTP {res.status}, {len(data)} bytes")
    except Exception as e:
        print(f"✗ {ep}: {e}")
        success = False

httpd.shutdown()
if success:
    print("\nALL ASSETS SERVED FLAWLESSLY!")
else:
    print("\nFAILED TO SERVE SOME ASSETS")
