def get_sec_financials(ticker):
    try:
        # Alternative approach: Use company tickers JSON from SEC
        import requests
        import json
        
        # Get company CIK from SEC tickers file
       def get_sec_financials(ticker):
    try:
        import requests
        import json
        
        # Use SEC's official company tickers endpoint
        tickers_url = "https://www.sec.gov/files/company_tickers.json"
        headers = {"User-Agent": "JaZu Career Coach API (contact@jazu.ai)"}
        
        response = requests.get(tickers_url, headers=headers)
        if response.status_code == 200:
            companies = response.json()
            
            # Find CIK for the ticker
            cik = None
            for company_data in companies.values():
                if company_data.get('ticker', '').upper() == ticker.upper():
                    cik = str(company_data['cik_str']).zfill(10)
                    break
            
            if cik:
                # Get basic company facts
                facts_url = f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json"
                facts_response = requests.get(facts_url, headers=headers)
                
                if facts_response.status_code == 200:
                    data = facts_response.json()
                    
                    # Extract key financial metrics if available
                    facts = data.get('facts', {})
                    company_name = data.get('entityName', ticker)
                    
                    return {
                        "ticker": ticker,
                        "company_name": company_name,
                        "cik": cik,
                        "status": "success",
                        "message": f"Financial data retrieved for {company_name}",
                        "data_available": len(facts) > 0
                    }
            
        return {"error": f"No SEC data found for ticker {ticker}", "ticker": ticker}
        
    except Exception as e:
        return {"error": f"API error: {str(e)}", "ticker": ticker}
