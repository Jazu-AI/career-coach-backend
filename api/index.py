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
