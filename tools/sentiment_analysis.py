from crewai.tools import BaseTool
import yfinance as yf
from textblob import TextBlob
import requests
from bs4 import BeautifulSoup
import random

class SentimentAnalysisTool(BaseTool):
    name: str = "Sentiment Analysis Tool"
    description: str = "Analyzes the market sentiment for a stock using news headlines and simulated social media data."

    def _run(self, ticker: str) -> dict:
        """
        Perform sentiment analysis on recent news articles about the given stock.

        Args:
            ticker (str): The stock ticker symbol.

        Returns:
            dict: Sentiment analysis results.
        """
        news_sentiment = self._get_news_sentiment(ticker)
        social_sentiment = self._simulate_social_sentiment(ticker)

        return {
            "ticker": ticker,
            "news_sentiment": news_sentiment,
            "social_sentiment": social_sentiment,
            "overall_sentiment": (news_sentiment + social_sentiment) / 2
        }

    def _get_news_sentiment(self, ticker: str) -> float:
        """
        Get sentiment from news headlines for a given stock ticker from MarketWatch.
        """
        url = f"https://www.marketwatch.com/investing/stock/{ticker}"
        try:
            response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            return 0.0

        soup = BeautifulSoup(response.text, 'html.parser')
        headlines = soup.find_all('h3', class_='article__headline')

        if not headlines:
            # Fallback to yfinance news if MarketWatch fails
            try:
                stock = yf.Ticker(ticker)
                news = stock.news
                headlines = [article['title'] for article in news[:10]]
                if not headlines:
                    return 0.0
                
                sentiment_scores = [TextBlob(h).sentiment.polarity for h in headlines]
                return sum(sentiment_scores) / len(sentiment_scores) if sentiment_scores else 0.0

            except Exception:
                return 0.0


        sentiment_scores = []
        for headline in headlines:
            text = headline.get_text()
            blob = TextBlob(text)
            sentiment_scores.append(blob.sentiment.polarity)

        return sum(sentiment_scores) / len(sentiment_scores) if sentiment_scores else 0.0

    def _simulate_social_sentiment(self, ticker: str) -> float:
        # This is a placeholder for actual social media sentiment analysis.
        # In a real-world scenario, you would use APIs from Twitter, StockTwits, etc.
        return random.uniform(-0.3, 0.3)