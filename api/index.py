from flask import Flask, request, jsonify
import requests
import json
import os

def get_wikidata_facts(company_name):
    try:
        # Search for the company on Wikidata
        search_url = f"https://www.wikidata.org/w/api.php"
        search_params = {
            "action": "wbsearchentities",
            "search": company_name,
            "language": "en",
            "format": "json"
        }
        
        response = requests.get(search_url, params=search_params)
        if response.status_code == 200:
            search_results = response.json()
            
            if search_results.get("search"):
                entity_id = search_results["search"][0]["id"]
                
                # Get detailed information about the entity
                entity_url = f"https://www.wikidata.org/w/api.php"
                entity_params = {
                    "action": "wbgetentities",
                    "ids": entity_id,
                    "format": "json",
                    "props": "claims"
                }
                
                entity_response = requests.get(entity_url, params=entity_params)
                if entity_response.status_code == 200:
                    entity_data = entity_response.json()
                    
                    return {
                        "message": f"Wikidata endpoint for {company_name} is ready.",
                        "entity_id": entity_id,
                        "status": "success"
                    }
        
        return {"error": f"No data found for {company_name}", "company": company_name}
        
    except Exception as e:
        return {"error": str(e), "company": company_name}


def get_sec_financials(ticker):
    try:
        # Alpha Vantage API
        api_key = os.environ.get('ALPHA_VANTAGE_KEY')
        if not api_key:
            return {"error": "Alpha Vantage API key not configured", "ticker": ticker}
        
        # Get company overview
        url = f"https://www.alphavantage.co/query?function=OVERVIEW&symbol={ticker}&apikey={api_key}"
        
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            
            # Check if we got valid data (Alpha Vantage returns empty dict for invalid symbols)
            if data and 'Symbol' in data:
                return {
                    "ticker": ticker,
                    "company_name": data.get('Name', ticker),
                    "sector": data.get('Sector', 'N/A'),
                    "industry": data.get('Industry', 'N/A'),
                    "market_cap": data.get('MarketCapitalization', 'N/A'),
                    "revenue_ttm": data.get('RevenueTTM', 'N/A'),
                    "profit_margin": data.get('ProfitMargin', 'N/A'),
                    "pe_ratio": data.get('PERatio', 'N/A'),
                    "dividend_yield": data.get('DividendYield', 'N/A'),
                    "status": "success",
                    "message": f"Financial data retrieved for {data.get('Name', ticker)}"
                }
            else:
                return {"error": f"No financial data found for ticker {ticker}", "ticker": ticker}
        
        return {"error": f"API request failed with status {response.status_code}", "ticker": ticker}
        
    except Exception as e:
        return {"error": f"API error: {str(e)}", "ticker": ticker}


def get_news(company_name):
    try:
        # Get news API key from environment
        news_api_key = os.environ.get('NEWS_API_KEY')
        if not news_api_key:
            return {"error": "News API key not configured", "company": company_name}
        
        # Use News API to get recent articles
        url = f"https://newsapi.org/v2/everything"
        params = {
            "q": company_name,
            "sortBy": "publishedAt",
            "apiKey": news_api_key,
            "pageSize": 10
        }
        
        response = requests.get(url, params=params)
        if response.status_code == 200:
            news_data = response.json()
            return {
                "company": company_name,
                "articles": news_data.get("articles", []),
                "status": "ok",
                "totalResults": news_data.get("totalResults", 0)
            }
        
        return {"error": f"News API request failed with status {response.status_code}", "company": company_name}
        
    except Exception as e:
        return {"error": str(e), "company": company_name}


def handler(request):
    try:
        # Get the path from the request
        path = request.path
        
        if path == '/get-wikidata-facts':
            company_name = request.args.get('company_name')
            if not company_name:
                return jsonify({"error": "company_name parameter is required"}), 400
            result = get_wikidata_facts(company_name)
            return jsonify(result)
            
        elif path == '/get-sec-financials':
            ticker = request.args.get('ticker')
            if not ticker:
                return jsonify({"error": "ticker parameter is required"}), 400
            result = get_sec_financials(ticker)
            return jsonify(result)
            
        elif path == '/get-news':
            company_name = request.args.get('company_name')
            if not company_name:
                return jsonify({"error": "company_name parameter is required"}), 400
            result = get_news(company_name)
            return jsonify(result)
        
        else:
            return jsonify({"error": "Endpoint not found"}), 404
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500
