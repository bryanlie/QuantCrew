from crewai.tools import BaseTool
import yfinance as yf
import requests
import os

class CompetitorAnalysisTool(BaseTool):
    name: str = "Competitor Analysis Tool"
    description: str = "Performs competitor analysis for a given stock ticker, providing a list of top competitors and their key financial metrics."

    def _get_competitors(self, ticker: str) -> list:
        """
        Fetches a list of competitor stock tickers from the Financial Modeling Prep (FMP) API.
        """
        api_key = os.environ.get("FMP_API_KEY")
        if not api_key:
            return None
        
        url = f"https://financialmodelingprep.com/api/v3/stock_peers?symbol={ticker}&apikey={api_key}"
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            return data[0].get('peersList', []) if data else []
        except requests.exceptions.RequestException as e:
            print(f"Error fetching competitors from FMP: {e}")
            return None

    def _run(self, ticker: str, num_competitors: int = 5) -> dict:
        """
        Perform competitor analysis for a given stock.

        Args:
            ticker (str): The stock ticker symbol.
            num_competitors (int): Number of top competitors to analyze.

        Returns:
            dict: Competitor analysis results.
        """
        stock = yf.Ticker(ticker)
        try:
            info = stock.info
            industry = info.get('industry', 'N/A')
        except Exception as e:
            return {"error": f"Could not fetch stock info for {ticker} from yfinance: {e}"}

        competitors = self._get_competitors(ticker)

        if competitors is None:
            return {"error": "FMP_API_KEY not found in environment variables. Please add it to your .env file."}
        
        if not competitors:
            return {"error": f"Could not find competitors for {ticker} using the FMP API."}

        competitor_data = []
        for comp_ticker in competitors[:num_competitors]:
            if comp_ticker != ticker:
                try:
                    comp_stock = yf.Ticker(comp_ticker)
                    comp_info = comp_stock.info
                    competitor_data.append({
                        "ticker": comp_ticker,
                        "name": comp_info.get('longName'),
                        "market_cap": f"${comp_info.get('marketCap', 0):,}",
                        "pe_ratio": round(comp_info.get('trailingPE', 0), 2),
                    })
                except Exception as e:
                    print(f"Could not fetch data for competitor {comp_ticker} from yfinance: {e}")

        return {
            "main_stock": ticker,
            "industry": industry,
            "competitors": competitor_data if competitor_data else "No competitor data could be fetched."
        }
