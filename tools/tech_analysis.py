import yfinance as yf
import numpy as np
from scipy.signal import find_peaks

from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Type

from ta.trend import SMAIndicator, MACD
from ta.momentum import RSIIndicator
from ta.volatility import BollingerBands

class TechAnalysisInput(BaseModel):
    """Input schema for technical analysis queries."""
    ticker: str = Field(..., description="The stock ticker symbol")
    period: str = Field(default="1y", description="The time period for analysis")

class TechAnalystTool(BaseTool):
    name: str = "Technical Analysis Tool"
    description: str = "Perform technical analysis on a given stock symbol"
    args_schema: Type[BaseModel] = TechAnalysisInput

    def _run(self, ticker: str, period: str = "1y") -> dict:
        period_mapping = {
            # "1d": "1d",
            # "5d": "5d",
            "1mo": "1mo",
            "3mo": "3mo",
            "6mo": "6mo",
            "1y": "1y",
            "2y": "2y",
            "5y": "5y",
            "10y": "10y",
            "ytd": "ytd",
            "max": "max",
            "6m": "6mo",
        }
        yf_period = period_mapping.get(period, "1y")

        try:
            analyst = TechAnalyst(ticker, yf_period)
            analyst.fetch_data()
            if analyst.df is None or analyst.df.empty:
                return {"error": f"Could not retrieve or process data for {ticker} for period {yf_period}. The dataframe is empty."}
            indicators = analyst.calculate_indicators()
            trend = analyst.analyze_trend()
            signal = analyst.generate_signal()

            return {
                "indicators": indicators,
                "trend": trend,
                "signal": signal
            }
        except Exception as e:
            return {"error": str(e)}

    async def _arun(self, ticker: str, period: str = "1y") -> dict:
        # Implement async version if needed
        return self._run(ticker, period)


class TechAnalyst:
    def __init__(self, ticker: str, period: str = "1y"):
        self.ticker = ticker
        self.period = period
        self.df = None

    def fetch_data(self):
        """Fetch historical stock data and calculate necessary technical indicators."""
        try:
            stock = yf.Ticker(self.ticker)
            history = stock.history(period=self.period)
            if history.empty:
                raise ValueError(f"No data found for ticker {self.ticker} and period {self.period}")

            df = history.copy()

            # Calculate only necessary indicators
            if len(df) >= 200:
                df['trend_sma_200'] = SMAIndicator(close=df['Close'], window=200).sma_indicator()
            if len(df) >= 50:
                df['trend_sma_50'] = SMAIndicator(close=df['Close'], window=50).sma_indicator()
            if len(df) >= 26: # MACD requirements
                macd = MACD(close=df['Close'], window_slow=26, window_fast=12, window_sign=9)
                df['trend_macd'] = macd.macd()
                df['trend_macd_signal'] = macd.macd_signal()
                df['trend_macd_diff'] = macd.macd_diff()
            if len(df) >= 20: # Bollinger Bands requirements
                bb = BollingerBands(close=df['Close'], window=20, window_dev=2)
                df['volatility_bbhi'] = bb.bollinger_hband_indicator()
                df['volatility_bbh'] = bb.bollinger_hband()
                df['volatility_bbl'] = bb.bollinger_lband()
                df['volatility_bbm'] = bb.bollinger_mavg()
            if len(df) >= 14: # RSI requirements
                df['momentum_rsi'] = RSIIndicator(close=df['Close'], window=14).rsi()

            self.df = df.dropna()

        except Exception as e:
            raise ValueError(f"Error processing data for {self.ticker}: {str(e)}")

    def calculate_indicators(self):
        """Calculate technical indicators."""
        if self.df is None or self.df.empty:
            raise ValueError("Data not fetched or empty. Call fetch_data() first.")

        # These calculations require at least 20 data points after dropna
        if len(self.df) >= 20:
            self.df['volatility'] = self.df['Close'].pct_change().rolling(window=20).std() * np.sqrt(252)
            self.df['momentum'] = self.df['Close'] - self.df['Close'].shift(20)
        else:
            self.df['volatility'] = np.nan
            self.df['momentum'] = np.nan


        close_prices = self.df['Close'].values
        peaks, _ = find_peaks(close_prices, distance=20)
        troughs, _ = find_peaks(-close_prices, distance=20)
        support_levels = close_prices[troughs][-3:]
        resistance_levels = close_prices[peaks][-3:]

        # Prepare indicator values, handling cases where they might not have been calculated
        indicators = {
            "current_price": round(self.df['Close'].iloc[-1], 2),
            "sma_50": round(self.df['trend_sma_50'].iloc[-1], 2) if 'trend_sma_50' in self.df.columns else None,
            "sma_200": round(self.df['trend_sma_200'].iloc[-1], 2) if 'trend_sma_200' in self.df.columns else None,
            "rsi": round(self.df['momentum_rsi'].iloc[-1], 2) if 'momentum_rsi' in self.df.columns else None,
            "macd": round(self.df['trend_macd_diff'].iloc[-1], 4) if 'trend_macd_diff' in self.df.columns else None,
            "bollinger_hband": round(self.df['volatility_bbh'].iloc[-1], 2) if 'volatility_bbh' in self.df.columns else None,
            "support_levels": [round(level, 2) for level in support_levels],
            "resistance_levels": [round(level, 2) for level in resistance_levels],
            "volatility": round(self.df['volatility'].iloc[-1], 4) if self.df['volatility'].notna().any() else None,
            "momentum": round(self.df['momentum'].iloc[-1], 2) if self.df['momentum'].notna().any() else None
        }
        return indicators

    def analyze_trend(self):
        """Analyze the overall trend of the stock."""
        if 'trend_sma_50' not in self.df.columns or 'trend_sma_200' not in self.df.columns:
            return "Not enough data for trend analysis"

        current_price = self.df['Close'].iloc[-1]
        sma_50 = self.df['trend_sma_50'].iloc[-1]
        sma_200 = self.df['trend_sma_200'].iloc[-1]

        if current_price > sma_50 > sma_200:
            return "Strong Uptrend"
        elif current_price > sma_50 and sma_50 < sma_200:
            return "Potential Uptrend"
        elif current_price < sma_50 < sma_200:
            return "Strong Downtrend"
        elif current_price < sma_50 and sma_50 > sma_200:
            return "Potential Downtrend"
        else:
            return "Neutral"

    def generate_signal(self):
        """Generate a trading signal based on technical indicators."""
        if 'momentum_rsi' not in self.df.columns or 'trend_macd_diff' not in self.df.columns or 'volatility_bbl' not in self.df.columns:
             return "Not enough data for signal generation"

        rsi = self.df['momentum_rsi'].iloc[-1]
        macd = self.df['trend_macd_diff'].iloc[-1]
        current_price = self.df['Close'].iloc[-1]
        lower_bb = self.df['volatility_bbl'].iloc[-1]
        upper_bb = self.df['volatility_bbh'].iloc[-1]

        if rsi < 30 and macd > 0 and current_price < lower_bb:
            return "Strong Buy"
        elif rsi < 40 and macd > 0:
            return "Buy"
        elif rsi > 70 and macd < 0 and current_price > upper_bb:
            return "Strong Sell"
        elif rsi > 60 and macd < 0:
            return "Sell"
        else:
            return "Hold"