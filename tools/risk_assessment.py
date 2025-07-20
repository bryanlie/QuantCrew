from crewai.tools import BaseTool
import yfinance as yf
import numpy as np
import pandas as pd

class RiskAssessmentTool(BaseTool):
    name: str = "Risk Assessment Tool"
    description: str = (
        "Performs a comprehensive risk assessment for a stock. "
        "The benchmark ticker must be a valid symbol from Yahoo Finance (e.g., '^GSPC' for S&P 500)."
    )

    def _run(self, ticker: str, benchmark: str = "^GSPC", period: str = "5y") -> dict:
        """
        Perform risk assessment for a given stock.
        """
        try:
            # Download data for both tickers at once for automatic alignment
            data = yf.download([ticker, benchmark], period=period, progress=False)['Close']

            if data.empty or ticker not in data or benchmark not in data or data[ticker].isnull().all() or data[benchmark].isnull().all():
                 return {"error": f"Could not retrieve valid data for {ticker} or {benchmark}."}

            # Calculate daily returns
            returns = data.pct_change().dropna()

            if returns.empty:
                return {"error": "Not enough data to calculate returns."}

            # Calculate beta
            covariance = returns[ticker].cov(returns[benchmark])
            benchmark_variance = returns[benchmark].var()
            beta = covariance / benchmark_variance if benchmark_variance != 0 else 0

            # Calculate Sharpe ratio
            risk_free_rate = 0.02  # Assume 2% risk-free rate
            excess_returns = returns[ticker] - (risk_free_rate / 252)
            sharpe_ratio = np.sqrt(252) * excess_returns.mean() / excess_returns.std() if excess_returns.std() != 0 else 0

            # Calculate Value at Risk (VaR)
            var_95 = np.percentile(returns[ticker], 5)

            # Calculate Maximum Drawdown
            cumulative_returns = (1 + returns[ticker]).cumprod()
            peak = cumulative_returns.cummax()
            drawdown = (cumulative_returns - peak) / peak
            max_drawdown = drawdown.min()

            return {
                "ticker": ticker,
                "beta": round(beta, 2),
                "sharpe_ratio": round(sharpe_ratio, 2),
                "value_at_risk_95": round(var_95, 4),
                "max_drawdown": round(max_drawdown, 4),
                "volatility": round(returns[ticker].std() * np.sqrt(252), 4)
            }
        except Exception as e:
            return {"error": f"An error occurred during risk assessment: {e}"}