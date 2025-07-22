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
        Perform risk assessment for a given stock. Returns metrics and reasoning.
        """
        try:
            data = yf.download([ticker, benchmark], period=period, progress=False)['Close']
            if data.empty or ticker not in data or benchmark not in data or data[ticker].isnull().all() or data[benchmark].isnull().all():
                 return {"error": f"Could not retrieve valid data for {ticker} or {benchmark}."}
            returns = data.pct_change().dropna()
            if returns.empty:
                return {"error": "Not enough data to calculate returns."}
            covariance = returns[ticker].cov(returns[benchmark])
            benchmark_variance = returns[benchmark].var()
            beta = covariance / benchmark_variance if benchmark_variance != 0 else 0
            risk_free_rate = 0.02
            excess_returns = returns[ticker] - (risk_free_rate / 252)
            sharpe_ratio = np.sqrt(252) * excess_returns.mean() / excess_returns.std() if excess_returns.std() != 0 else 0
            var_95 = np.percentile(returns[ticker], 5)
            cumulative_returns = (1 + returns[ticker]).cumprod()
            peak = cumulative_returns.cummax()
            drawdown = (cumulative_returns - peak) / peak
            max_drawdown = drawdown.min()
            volatility = round(returns[ticker].std() * np.sqrt(252), 4)

            # Generate reasoning string
            reasoning = (
                f"Risk assessment for {ticker} (vs benchmark {benchmark}, period {period}):\n"
                f"Beta: {round(beta, 2)} (measures sensitivity to market movements). "
                f"Sharpe Ratio: {round(sharpe_ratio, 2)} (risk-adjusted return). "
                f"Value at Risk (95%): {round(var_95, 4)} (potential loss in worst 5% of days). "
                f"Max Drawdown: {round(max_drawdown, 4)} (largest peak-to-trough decline). "
                f"Annualized Volatility: {volatility}. "
                f"A higher beta means more market risk, a higher Sharpe ratio means better risk-adjusted returns, and a larger drawdown/volatility means more risk."
            )

            return {
                "ticker": ticker,
                "beta": round(beta, 2),
                "sharpe_ratio": round(sharpe_ratio, 2),
                "value_at_risk_95": round(var_95, 4),
                "max_drawdown": round(max_drawdown, 4),
                "volatility": volatility,
                "reasoning": reasoning
            }
        except Exception as e:
            return {"error": f"An error occurred during risk assessment: {e}"}