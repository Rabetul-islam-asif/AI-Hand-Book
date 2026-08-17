import http.server
import socketserver
import webbrowser
import os
import sys
import threading
import time

PORT = 8085

class CustomHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        # Prevent caching for live updates and allow CORS
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Expires', '0')
        self.send_header('Access-Control-Allow-Origin', '*')
        super().end_headers()

    def translate_path(self, path):
        if path == "/" or path == "/index.html":
            return "index.html"
        return super().translate_path(path)

def start_server():
    sys.stdout.reconfigure(encoding='utf-8')
    
    if not os.path.exists("index.html"):
        print("Error: index.html not found in the current directory!")
        return

    handler = CustomHTTPRequestHandler
    socketserver.TCPServer.allow_reuse_address = True
    
    current_port = PORT
    httpd = None
    for p in range(current_port, current_port + 20):
        try:
            httpd = socketserver.TCPServer(("", p), handler)
            current_port = p
            break
        except OSError:
            continue
            
    if not httpd:
        print("Error: Could not bind to any port in range 8085-8105!")
        return

    with httpd:
        print(f"============================================================")
        print(f"🚀 AI Engineering Handbook Local Server is RUNNING!")
        print(f"🔗 Access the interactive documentation at: http://localhost:{current_port}")
        print(f"============================================================")
        print("To stop the server, cancel the process in terminal.")
        
        def open_browser():
            time.sleep(1.2)
            print("Opening browser...")
            webbrowser.open(f"http://localhost:{current_port}")
            
        threading.Thread(target=open_browser, daemon=True).start()
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down local server...")
            httpd.shutdown()

if __name__ == "__main__":
    start_server()
