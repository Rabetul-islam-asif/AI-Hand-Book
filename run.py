import http.server
import socketserver
import webbrowser
import os
import sys
import threading
import time

PORT = 8000

class CustomHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        # Prevent caching for live updates
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Expires', '0')
        super().end_headers()

    def translate_path(self, path):
        # Ensure that requested paths map correctly even if running from different directories
        # We serve index.html as the primary page
        if path == "/" or path == "/index.html":
            return "index.html"
        return super().translate_path(path)

def start_server():
    # Direct terminal stdout to avoid cp1252 issue in standard print
    sys.stdout.reconfigure(encoding='utf-8')
    
    # Check if index.html exists
    if not os.path.exists("index.html"):
        print("Error: index.html not found in the current directory!")
        return

    handler = CustomHTTPRequestHandler
    
    # Allow port reuse to avoid 'Address already in use' error
    socketserver.TCPServer.allow_reuse_address = True
    
    with socketserver.TCPServer(("", PORT), handler) as httpd:
        print(f"============================================================")
        print(f"🚀 AI Engineering Handbook Local Server is RUNNING!")
        print(f"🔗 Access the interactive documentation at: http://localhost:{PORT}")
        print(f"============================================================")
        print("To stop the server, cancel the process in terminal.")
        
        # Open browser in a separate thread after 1.5 seconds to ensure server has started
        def open_browser():
            time.sleep(1.5)
            print("Opening browser...")
            webbrowser.open(f"http://localhost:{PORT}")
            
        threading.Thread(target=open_browser, daemon=True).start()
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down local server...")
            httpd.shutdown()

if __name__ == "__main__":
    start_server()
