# Standalone Python Web Server for MOMO MAZE Desktop Browser Edition
import http.server
import socketserver
import webbrowser
import threading
import os
import sys

PORT = 8080
DIRECTORY = os.path.dirname(os.path.abspath(__file__))

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

    def end_headers(self):
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate')
        self.send_header('Access-Control-Allow-Origin', '*')
        super().end_headers()

def open_browser_async(url):
    try:
        webbrowser.open(url)
    except:
        pass

def main():
    global PORT
    for attempt in range(10):
        try:
            with socketserver.TCPServer(("0.0.0.0", PORT), Handler) as httpd:
                url = f"http://localhost:{PORT}"
                print(f"[MomoServer] Server listening on http://localhost:{PORT}")
                sys.stdout.flush()

                # Open browser asynchronously
                if "--no-browser" not in sys.argv:
                    threading.Thread(target=open_browser_async, args=(url,), daemon=True).start()

                httpd.serve_forever()
                break
        except OSError as e:
            if "address already in use" in str(e).lower() or e.errno == 98 or e.errno == 10048:
                PORT += 1
            else:
                raise e

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\nMOMO MAZE server stopped.")
        sys.exit(0)
