#!/usr/bin/env python3
"""
Simple HTTP server for FermTrack Frontend

This script provides a simple HTTP server to serve the frontend files
during development. For production, use a proper web server like nginx.
"""

import http.server
import socketserver
import os
import sys
import webbrowser
from pathlib import Path

# Configuration
DEFAULT_PORT = 8080
FRONTEND_DIR = Path(__file__).parent

def find_available_port(start_port=DEFAULT_PORT, max_attempts=10):
    """Find an available port starting from the default port"""
    import socket
    
    for port in range(start_port, start_port + max_attempts):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('localhost', port))
                return port
        except OSError:
            continue
    
    raise RuntimeError(f"Could not find available port in range {start_port}-{start_port + max_attempts}")

def start_server(port=None, auto_open=True):
    """Start the HTTP server"""
    
    # Change to frontend directory
    os.chdir(FRONTEND_DIR)
    
    # Find available port
    if port is None:
        try:
            port = find_available_port()
        except RuntimeError as e:
            print(f"❌ {e}")
            return 1
    
    # Check if index.html exists
    if not os.path.exists('index.html'):
        print("❌ index.html not found in current directory")
        print("Please run this script from the frontend directory")
        return 1
    
    try:
        # Create server
        handler = http.server.SimpleHTTPRequestHandler
        
        # Add CORS headers for local development
        class CORSRequestHandler(handler):
            def end_headers(self):
                self.send_header('Access-Control-Allow-Origin', '*')
                self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
                self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
                super().end_headers()
        
        with socketserver.TCPServer(("", port), CORSRequestHandler) as httpd:
            server_url = f"http://localhost:{port}"
            
            print("🚀 FermTrack Frontend Server")
            print("=" * 40)
            print(f"📂 Serving: {FRONTEND_DIR}")
            print(f"🌐 URL: {server_url}")
            print(f"📱 Access from mobile: http://YOUR_IP_ADDRESS:{port}")
            print()
            print("💡 Make sure the backend is running at http://localhost:5000")
            print("📋 Default admin login: admin / admin123")
            print()
            print("Press Ctrl+C to stop the server")
            print("=" * 40)
            
            # Open browser automatically
            if auto_open:
                try:
                    webbrowser.open(server_url)
                    print(f"🎯 Opening {server_url} in your browser...")
                except:
                    print(f"🎯 Open {server_url} in your browser manually")
            
            # Start server
            print(f"\n🟢 Server started on port {port}")
            httpd.serve_forever()
            
    except KeyboardInterrupt:
        print("\n\n🛑 Server stopped by user")
        return 0
    except OSError as e:
        if e.errno == 98:  # Address already in use
            print(f"❌ Port {port} is already in use")
            print("Try a different port or stop the process using that port")
        else:
            print(f"❌ Server error: {e}")
        return 1
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return 1

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='FermTrack Frontend Development Server')
    parser.add_argument('-p', '--port', type=int, default=None, 
                       help=f'Port to serve on (default: auto-detect starting from {DEFAULT_PORT})')
    parser.add_argument('--no-browser', action='store_true', 
                       help='Don\'t automatically open browser')
    
    args = parser.parse_args()
    
    return start_server(port=args.port, auto_open=not args.no_browser)

if __name__ == '__main__':
    sys.exit(main())