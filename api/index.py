from http.server import BaseHTTPRequestHandler
import json
import urllib.parse
import os

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Parse the URL and query parameters
        url_parts = urllib.parse.urlparse(self.path)
        path = url_parts.path
        query = urllib.parse.parse_qs(url_parts.query)
        
        # Set response headers
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        # Route to different functions based on path
        if path == '/get-wikidata-facts':
            company_name = query.get('company_name', [''])[0]
            result = self.get_wikidata_facts(company_name)
        elif path == '/get-sec-financials':
            ticker = query.get('ticker', [''])[0]
            result = self.get_sec_financials(ticker)
        elif path == '/get-news':
            company_name = query.get('company_name', [''])[0]
            result = self.get_news(company_name)
        else:
            result = {"error": "Endpoint not found", "path": path}
        
        # Send JSON response
        self.wfile.write(json.dumps(result).encode())
    
    def do_POST(self):
        # Parse the URL
        url_parts = urllib.parse.urlparse(self.path)
        path = url_parts.path
        
        # Read POST body
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        
        try:
            body = json.loads(post_data.decode('utf-8'))
        except:
            self.send_error(400, "Invalid JSON")
            return
        
        # Set response headers
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        # Route to memory functions
        if path == '/api/store-memory':
            result = self.store_memory(body)
        elif path == '/api/search-memory':
            result = self.search_memory(body)
        elif path == '/api/update-memory':
            result = self.update_memory(body)
        else:
            result = {"error": "Endpoint not found", "path": path}
        
        # Send JSON response
        self.wfile.write(json.dumps(result).encode())
    
    def get_wikidata_facts(self, company_name):
        if not company_name:
            return {"error": "company_name parameter required"}
        
        return {
            "message": f"Wikidata endpoint for {company_name} is ready.",
            "company": company_name,
            "status": "success"
        }
    
    def get_sec_financials(self, ticker):
        if not ticker:
            return {"error": "ticker parameter required"}
        
        return {
            "message": f"Financial data endpoint ready for {ticker}",
            "ticker": ticker,
            "status": "success"
        }
    
    def get_news(self, company_name):
        if not company_name:
            return {"error": "company_name parameter required"}
        
        return {
            "message": f"News endpoint ready for {company_name}",
            "company": company_name,
            "status": "success"
        }
    
    def store_memory(self, body):
        try:
            # Check environment variables first
            pinecone_key = os.environ.get('PINECONE_API_KEY')
            openai_key = os.environ.get('OPENAI_API_KEY')
            
            if not pinecone_key:
                return {"error": "PINECONE_API_KEY not configured"}
            if not openai_key:
                return {"error": "OPENAI_API_KEY not configured"}
            
            # Try importing dependencies
            try:
                import openai
                import uuid
                from datetime import datetime
                from pinecone import Pinecone
            except ImportError as e:
                return {"error": f"Import failed: {str(e)}"}
            
            return {
                "ok": True,
                "namespace": body.get('namespace', 'default'),
                "upsertedCount": 1,
                "debug": "All checks passed, dependencies loaded"
            }
            
        except Exception as e:
            return {"error": f"Unexpected error: {str(e)}"}
    
    def search_memory(self, body):
        return {"ok": True, "matches": [], "debug": "placeholder"}
    
    def update_memory(self, body):
        return {"ok": True, "namespace": "default", "updated": True, "debug": "placeholder"}
