from http.server import BaseHTTPRequestHandler
import json
import urllib.parse
import os
import openai
import pinecone
import uuid
from datetime import datetime

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
    
    def init_pinecone(self):
        try:
            # For serverless indexes, don't specify environment
            pinecone.init(api_key=os.environ.get('PINECONE_API_KEY'))
            index_name = os.environ.get('PINECONE_INDEX_NAME', 'coach-prod')
            return pinecone.Index(index_name)
        except Exception as e:
            return None

    def get_embedding(self, text):
        try:
            client = openai.OpenAI(api_
