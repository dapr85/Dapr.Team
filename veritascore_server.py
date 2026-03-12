#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════
VeritasCore™ Local AI Server
Copyright © 2026 DAPR (Dale Associate Public Relations). All Rights Reserved.

This server runs entirely on YOUR computer with YOUR AI models.
No external dependencies. Complete privacy and ownership.

Contact: dapr.team@gmail.com
═══════════════════════════════════════════════════════════════════════════
"""

import http.server
import socketserver
import json
import urllib.request
import urllib.parse
from datetime import datetime

PORT = 8000
OLLAMA_URL = "http://localhost:11434"

class VeritasCoreHandler(http.server.SimpleHTTPRequestHandler):
    """Handle requests for VeritasCore website and API"""
    
    def do_GET(self):
        """Serve the website"""
        if self.path == '/' or self.path == '/index.html':
            self.path = '/veritascore_website.html'
        return super().do_GET()
    
    def do_POST(self):
        """Handle API requests"""
        if self.path == '/api/chat':
            self.handle_chat()
        else:
            self.send_error(404)
    
    def handle_chat(self):
        """Process chat messages with local AI"""
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        
        try:
            data = json.loads(post_data.decode('utf-8'))
            message = data.get('message', '')
            model = data.get('model', 'llama3')
            
            # Try to use Ollama
            response_text = self.get_ollama_response(message, model)
            
            response = {
                'response': response_text,
                'model': model,
                'timestamp': datetime.now().isoformat()
            }
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode())
            
        except Exception as e:
            error_response = {
                'error': str(e),
                'message': 'Failed to process request'
            }
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(error_response).encode())
    
    def get_ollama_response(self, message, model):
        """Get response from Ollama running locally"""
        try:
            url = f"{OLLAMA_URL}/api/generate"
            data = {
                'model': model,
                'prompt': message,
                'stream': False
            }
            
            req = urllib.request.Request(
                url,
                data=json.dumps(data).encode('utf-8'),
                headers={'Content-Type': 'application/json'}
            )
            
            with urllib.request.urlopen(req, timeout=30) as response:
                result = json.loads(response.read().decode('utf-8'))
                return result.get('response', 'No response from model')
                
        except Exception as e:
            return f"⚠️ Ollama not available: {str(e)}\n\nTo use local AI:\n1. Install Ollama from https://ollama.ai\n2. Run: ollama pull {model}\n3. Start: ollama serve\n4. Refresh this page"

    def do_OPTIONS(self):
        """Handle CORS preflight"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

def run_server():
    """Start the VeritasCore local server"""
    with socketserver.TCPServer(("", PORT), VeritasCoreHandler) as httpd:
        print("═" * 80)
        print("VeritasCore™ Local Server")
        print("Copyright © 2026 DAPR. All Rights Reserved.")
        print("═" * 80)
        print(f"\n✓ Server running on: http://localhost:{PORT}")
        print(f"✓ Open in browser:   http://localhost:{PORT}/veritascore_website.html")
        print("\n📡 AI Backend Status:")
        
        # Check Ollama
        try:
            req = urllib.request.Request(f"{OLLAMA_URL}/api/tags")
            with urllib.request.urlopen(req, timeout=2) as response:
                data = json.loads(response.read().decode('utf-8'))
                models = data.get('models', [])
                print(f"  ✓ Ollama connected: {len(models)} models available")
                for model in models:
                    print(f"    • {model.get('name', 'unknown')}")
        except:
            print(f"  ⚠ Ollama not running (install from https://ollama.ai)")
        
        print("\n" + "═" * 80)
        print("Press Ctrl+C to stop the server")
        print("═" * 80 + "\n")
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n\n✓ Server stopped")

if __name__ == "__main__":
    run_server()
