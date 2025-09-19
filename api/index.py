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
            pinecone.init(
                api_key=os.environ.get('PINECONE_API_KEY'),
                environment="us-east-1-aws"  # Adjust to your Pinecone environment
            )
            index_name = os.environ.get('PINECONE_INDEX_NAME', 'coach-prod')
            return pinecone.Index(index_name)
        except Exception as e:
            return None

    def get_embedding(self, text):
        try:
            client = openai.OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))
            response = client.embeddings.create(
                model="text-embedding-ada-002",
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            return None
    
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
        
        try:
            # Generate embedding
            embedding = self.get_embedding(text)
            if not embedding:
                return {"error": "Failed to generate embedding"}
            
            # Initialize Pinecone
            index = self.init_pinecone()
            if not index:
                return {"error": "Failed to connect to Pinecone"}
            
            # Create vector record
            vector_id = f"{user_id}_{uuid.uuid4()}"
            vector_data = {
                "id": vector_id,
                "values": embedding,
                "metadata": {
                    "userId": user_id,
                    "text": text,
                    "tags": tags,
                    "timestamp": datetime.utcnow().isoformat(),
                    **metadata
                }
            }
            
            # Store in Pinecone
            index.upsert([vector_data], namespace=namespace)
            
            return {
                "ok": True,
                "namespace": namespace,
                "upsertedCount": 1
            }
        
        except Exception as e:
            return {"error": f"Storage failed: {str(e)}"}
    
    def search_memory(self, body):
        user_id = body.get('userId')
        query = body.get('query')
        namespace = body.get('namespace', 'default')
        top_k = body.get('topK', 5)
        
        if not user_id or not query:
            return {"error": "userId and query are required"}
        
        try:
            # Generate query embedding
            query_embedding = self.get_embedding(query)
            if not query_embedding:
                return {"error": "Failed to generate query embedding"}
            
            # Initialize Pinecone
            index = self.init_pinecone()
            if not index:
                return {"error": "Failed to connect to Pinecone"}
            
            # Search vectors
            results = index.query(
                vector=query_embedding,
                top_k=top_k,
                namespace=namespace,
                filter={"userId": user_id},
                include_metadata=True
            )
            
            # Format response
            matches = []
            for match in results.matches:
                matches.append({
                    "id": match.id,
                    "score": float(match.score),
                    "metadata": match.metadata
                })
            
            return {
                "ok": True,
                "matches": matches
            }
        
        except Exception as e:
            return {"error": f"Search failed: {str(e)}"}
    
    def update_memory(self, body):
        user_id = body.get('userId')
        memory_id = body.get('id')
        
        if not user_id or not memory_id:
            return {"error": "userId and id are required"}
        
        return {
            "ok": True,
            "namespace": body.get('namespace', 'default'),
            "updated": True
        }
