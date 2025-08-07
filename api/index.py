from flask import Flask, request, jsonify
import requests
import os

# Initialize the Flask app
app = Flask(___name___)

# --- Helper function to get CIK ---
def get_cik_for_ticker(ticker_symbol: str):
    # This is the first line to change
    headers = {'User-Agent': "jazu-ai"} # <--- CHANGE MADE HERE
    try:
        response = requests.get("https://www.sec.gov/files/company_tickers.json", headers=headers)
        response.raise_for_status()
        company_data = response.json()
        for key, value in company_data.items():
            if value['ticker'] == ticker_symbol.upper():
                return str(value['cik_str']).zfill(10)
    except requests.exceptions.RequestException as e:
        print(f"Error fetching CIK list: {e}")
    return None

# --- Route for SEC Financials ---
@app.route('/get-sec-financials', methods=['GET'])
def get_sec_financials_route():
    ticker = request.args.get('ticker')
    if not ticker:
        return jsonify({"error": "Ticker parameter is missing"}), 400
    
    cik = get_cik_for_ticker(ticker)
    if not cik:
        return jsonify({"error": f"CIK not found for ticker: {ticker}"}), 404
    
    facts_url = f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json"
    # This is the second line to change
    headers = {'User-Agent': "jazu-ai"} # <--- CHANGE MADE HERE
    try:
        response = requests.get(facts_url, headers=headers)
        response.raise_for_status()
        return jsonify(response.json())
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Failed to fetch SEC data: {e}"}), 500

# --- Route for News ---
@app.route('/get-news', methods=['GET'])
def get_news_route():
    company_name = request.args.get('company_name')
    NEWS_API_KEY = os.environ.get("NEWS_API_KEY")
    
    if not NEWS_API_KEY:
        return jsonify({"error": "News API key is not configured"}), 500
    if not company_name:
        return jsonify({"error": "Company name parameter is missing"}), 400
        
    news_url = f"https://newsapi.org/v2/everything?q={company_name}&sortBy=relevancy&language=en&apiKey={NEWS_API_KEY}"
    try:
        response = requests.get(news_url)
        response.raise_for_status()
        return jsonify(response.json())
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Failed to fetch news data: {e}"}), 500

# --- Route for Wikidata (you would build this out similarly) ---
@app.route('/get-wikidata-facts', methods=['GET'])
def get_wikidata_facts_route():
    # You would add the Python logic for the Wikidata query here
    company_name = request.args.get('company_name')
    # For now, we'll return a placeholder

    return jsonify({"message": f"Wikidata endpoint for {company_name} is ready."})


