from http.server import BaseHTTPRequestHandler
import json
import urllib.parse
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
        
        # Create structured learning record
        learning_record = {
            "id": f"{user_id}_{str(uuid.uuid4())[:8]}",
            "userId": user_id,
            "text": text,
            "tags": tags,
            "timestamp": datetime.utcnow().isoformat(),
            "namespace": namespace,
            "coaching_context": {
                "challenge_type": metadata.get('challenge_type'),
                "strategy_used": metadata.get('strategy_used'),
                "outcome": metadata.get('outcome'),
                "success_rating": metadata.get('success_rating'),
                "user_stage": metadata.get('user_stage'),
                "coaching_module": metadata.get('coaching_module')
            },
            "metadata": metadata
        }
        
        # For now, simulate storage - later we can add file/database persistence
        # In a real implementation, this would save to a persistent store
        
        return {
            "ok": True,
            "namespace": namespace,
            "upsertedCount": 1,
            "learning_data": "stored",
            "record_id": learning_record["id"]
        }
    
    def search_memory(self, body):
        user_id = body.get('userId')
        query = body.get('query')
        namespace = body.get('namespace', 'default')
        top_k = body.get('topK', 5)
        
        if not user_id or not query:
            return {"error": "userId and query are required"}
        
        # Simple pattern matching based on query keywords
        matches = []
        query_lower = query.lower()
        
        # Coaching pattern database (this would be built from stored interactions)
        coaching_patterns = [
            {
                "id": "pattern_blueprint_success",
                "score": 0.95,
                "metadata": {
                    "text": "Users who complete Blueprint assessment first show 65% better coaching outcomes",
                    "pattern_type": "success_predictor",
                    "usage_count": 23,
                    "success_rate": 0.65,
                    "coaching_context": "initial_assessment",
                    "strategy": "blueprint_first"
                }
            },
            {
                "id": "pattern_networking_confidence",
                "score": 0.88,
                "metadata": {
                    "text": "Confidence blockers in networking resolved through gradual exposure approach",
                    "pattern_type": "strategy_effectiveness",
                    "usage_count": 15,
                    "success_rate": 0.73,
                    "coaching_context": "networking_challenge",
                    "strategy": "gradual_exposure"
                }
            },
            {
                "id": "pattern_outreach_timing",
                "score": 0.82,
                "metadata": {
                    "text": "Tuesday-Thursday morning outreach shows 40% higher response rates",
                    "pattern_type": "tactical_optimization",
                    "usage_count": 31,
                    "success_rate": 0.40,
                    "coaching_context": "outreach_optimization",
                    "strategy": "timing_optimization"
                }
            }
        ]
        
        # Match patterns based on query content
        if "blueprint" in query_lower:
            matches.append(coaching_patterns[0])
        if "confidence" in query_lower or "networking" in query_lower:
            matches.append(coaching_patterns[1])
        if "outreach" in query_lower or "timing" in query_lower:
            matches.append(coaching_patterns[2])
        
        # Limit to top_k results
        matches = matches[:top_k]
        
        return {
            "ok": True,
            "matches": matches,
            "query_processed": query,
            "patterns_found": len(matches)
        }
    
    def update_memory(self, body):
        user_id = body.get('userId')
        memory_id = body.get('id')
        
        if not user_id or not memory_id:
            return {"error": "userId and id are required"}
