def get_sec_financials(ticker):
    try:
        import requests
        import os
        
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
