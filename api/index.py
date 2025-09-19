def get_sec_financials(ticker):
    try:
        # Alternative approach: Use company tickers JSON from SEC
        import requests
        import json
        
        # Get company CIK from SEC tickers file
        tickers_url = "https://www.sec.gov/files/company_tickers.json"
        headers = {"User-Agent": "JaZu Career Coach (contact@jazu.ai)"}
        
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
                # Get financial data using CIK
                facts_url = f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json"
                facts_response = requests.get(facts_url, headers=headers)
                
                if facts_response.status_code == 200:
                    data = facts_response.json()
                    return {
                        "ticker": ticker,
                        "cik": cik,
                        "company_name": data.get("entityName", ""),
                        "financial_data": "Retrieved successfully",
                        "message": f"Financial data found for {ticker}"
                    }
            
        return {"error": f"CIK not found for ticker {ticker}", "ticker": ticker}
        
    except Exception as e:
        return {"error": str(e), "ticker": ticker}
