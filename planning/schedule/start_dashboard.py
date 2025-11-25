#!/usr/bin/env python3
"""
Simple local server for the dashboard.
Run this, then open http://localhost:8000/dashboard.html in your browser.
"""

import http.server
import socketserver
import webbrowser
from pathlib import Path
import time
import threading

PORT = 8000

class QuietHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    """HTTP handler that only logs errors."""
    def log_message(self, format, *args):
        # Only log errors, not every request
        if args[1] != '200':
            super().log_message(format, *args)

def open_browser():
    """Open browser after short delay."""
    time.sleep(1.5)
    webbrowser.open(f'http://localhost:{PORT}/dashboard.html')

if __name__ == "__main__":
    # Change to script directory
    script_dir = Path(__file__).parent
    import os
    os.chdir(script_dir)

    # Start browser opener in background
    threading.Thread(target=open_browser, daemon=True).start()

    # Start server
    with socketserver.TCPServer(("", PORT), QuietHTTPRequestHandler) as httpd:
        print("=" * 60)
        print("🏗️  Santa Ray Task Dashboard Server")
        print("=" * 60)
        print()
        print(f"✅ Server running at: http://localhost:{PORT}")
        print(f"📊 Dashboard opening in your browser...")
        print()
        print("💡 Tip: Bookmark http://localhost:{PORT}/dashboard.html")
        print()
        print("⌨️  Press Ctrl+C to stop the server")
        print()

        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n\n👋 Dashboard server stopped.")
