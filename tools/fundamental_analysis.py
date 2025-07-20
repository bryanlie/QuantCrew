from crewai.tools import BaseTool
import yfinance as yf
import pandas as pd

class FundamentalAnalysisTool(BaseTool):
    name: str = "Fundamental Analysis Tool"
    description: str = "Performs comprehensive fundamental analysis on a given stock ticker, returning key financial metrics and ratios."

    def _run(self, ticker: str) -> dict:
        """
        Perform comprehensive fundamental analysis on a given stock ticker.

        Args:
            ticker (str): The stock ticker symbol.

        Returns:
            dict: Comprehensive fundamental analysis results.
        """
        stock = yf.Ticker(ticker)
        try:
            info = stock.info
            # Add a more specific check for a valid info object
            if not info or info.get('trailingPE') is None:
                return {"error": f"Could not retrieve valid financial info for {ticker}. It may be an invalid ticker."}
            
            financials = stock.financials
            balance_sheet = stock.balance_sheet
            cash_flow = stock.cashflow

            if financials.empty or balance_sheet.empty or cash_flow.empty:
                return {"error": f"Could not retrieve complete financial statements for {ticker}."}

        except Exception as e:
            return {"error": f"Failed to retrieve data for {ticker} from yfinance: {e}"}


        # Helper to safely get the most recent value
        def get_latest(df, key):
            if key in df.index and not df.loc[key].empty:
                return df.loc[key].iloc[0]
            return None

        # Calculate additional financial ratios safely
        try:
            total_current_assets = get_latest(balance_sheet, 'Total Current Assets')
            total_current_liabilities = get_latest(balance_sheet, 'Total Current Liabilities')
            total_liabilities = get_latest(balance_sheet, 'Total Liabilities Net Minority Interest')
            total_equity = get_latest(balance_sheet, 'Total Equity Gross Minority Interest')
            net_income = get_latest(financials, 'Net Income')
            total_assets = get_latest(balance_sheet, 'Total Assets')
            total_revenue = get_latest(financials, 'Total Revenue')
            operating_cash_flow = get_latest(cash_flow, 'Operating Cash Flow')
            capital_expenditures = get_latest(cash_flow, 'Capital Expenditure')

            # Previous year's revenue and net income for growth calculation
            prev_total_revenue = financials.loc['Total Revenue'].iloc[1] if len(financials.loc['Total Revenue']) > 1 else None
            prev_net_income = financials.loc['Net Income'].iloc[1] if len(financials.loc['Net Income']) > 1 else None


            current_ratio = total_current_assets / total_current_liabilities if total_current_liabilities else None
            debt_to_equity = total_liabilities / total_equity if total_equity else None
            roe = net_income / total_equity if total_equity else None
            roa = net_income / total_assets if total_assets else None
            revenue_growth = (total_revenue - prev_total_revenue) / prev_total_revenue if total_revenue and prev_total_revenue else None
            net_income_growth = (net_income - prev_net_income) / prev_net_income if net_income and prev_net_income else None
            fcf = (operating_cash_flow + capital_expenditures) if operating_cash_flow and capital_expenditures else None # CapEx is usually negative

        except (KeyError, IndexError) as e:
            current_ratio = debt_to_equity = roe = roa = revenue_growth = net_income_growth = fcf = f"Calculation error: {e}"


        return {
            "ticker": ticker,
            "company_name": info.get('longName'),
            "sector": info.get('sector'),
            "industry": info.get('industry'),
            "market_cap": info.get('marketCap'),
            "pe_ratio": info.get('trailingPE'),
            "forward_pe": info.get('forwardPE'),
            "peg_ratio": info.get('pegRatio'),
            "price_to_book": info.get('priceToBook'),
            "dividend_yield": info.get('dividendYield'),
            "52_week_high": info.get('fiftyTwoWeekHigh'),
            "52_week_low": info.get('fiftyTwoWeekLow'),
            "current_ratio": current_ratio,
            "debt_to_equity": debt_to_equity,
            "return_on_equity": roe,
            "return_on_assets": roa,
            "revenue_growth": revenue_growth,
            "net_income_growth": net_income_growth,
            "free_cash_flow": fcf,
            "analyst_recommendation": info.get('recommendationKey'),
            "target_price": info.get('targetMeanPrice')
        }