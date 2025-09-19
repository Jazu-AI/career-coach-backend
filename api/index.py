from http.server import BaseHTTPRequestHandler
import json
import urllib.parse

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
        user_id = body.get('userId')
        text = body.get('text')
        tags = body.get('tags', [])
        metadata = body.get('metadata', {})
        namespace = body.get('namespace', 'default')
        
        if not user_id or not text:
            return {"error": "userId and text are required"}
        
        # TODO: Implement Pinecone storage
        return {
            "ok": True,
            "namespace": namespace,
            "upsertedCount": 1
        }
    
    def search_memory(self, body):
        user_id = body.get('userId')
        query = body.get('query')
        namespace = body.get('namespace', 'default')
        top_k = body.get('topK', 5)
        
        if not user_id or not query:
            return {"error": "userId and query are required"}
        
        # TODO: Implement Pinecone search
        return {
            "ok": True,
            "matches": []
        }
    
    def update_memory(self, body):
        user_id = body.get('userId')
        memory_id = body.get('id')
        
        if not user_id or not memory_id:
            return {"error": "userId and id are required"}
        
        # TODO: Implement Pinecone update
        return {
            "ok": True,
            "namespace": body.get('namespace', 'default'),
            "updated": True
        }
