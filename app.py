import streamlit as st
import yfinance as yf
import plotly.graph_objs as go
from crew import run_analysis
import json
import pandas as pd
from crewai import CrewOutput
from ui.agent_display import (
    display_technical_analysis,
    display_fundamental_analysis,
    display_risk_assessment,
    display_investment_strategy
)
import pandas_market_calendars as mcal
from datetime import date

def display_report(analysis):
    """Displays the analysis report using Streamlit tabs."""
    st.header("AI Analysis Report")

    tab_titles = [
        "📊 Technical Analysis",
        "📑 Fundamental Analysis",
        "⚖️ Risk Assessment",
        "📈 Investment Strategy"
    ]
    tabs = st.tabs(tab_titles)

    with tabs[0]:
        st.subheader("Technical Analysis")
        display_technical_analysis(analysis.get('technical_analysis', {}))

    with tabs[1]:
        st.subheader("Fundamental Analysis")
        display_fundamental_analysis(analysis.get('fundamental_analysis', {}))

    with tabs[2]:
        st.subheader("Risk Assessment")
        display_risk_assessment(analysis.get('risk_assessment', {}))

    with tabs[3]:
        st.subheader("Investment Strategy & Recommendation")
        display_investment_strategy(analysis.get('investment_strategy', {}))



def display_stock_data(stock_symbol):
    """Fetches and displays stock data and chart."""
    st.header(f"Live Stock Data for {stock_symbol}")
    stock = yf.Ticker(stock_symbol)
    
    st.subheader("Key Statistics")
    info = stock.info
    
    # Ensure info is not empty
    if not info or info.get('regularMarketPrice') is None:
        st.warning(f"Could not retrieve key statistics for {stock_symbol}. The symbol may be invalid or delisted.")
        return

    stats_data = {
        "Metric": ["Market Cap", "P/E Ratio", "52 Week High", "52 Week Low", "Dividend Yield", "Beta"],
        "Value": [
            f"${info.get('marketCap', 0):,}" if info.get('marketCap') else "N/A",
            str(round(info.get('trailingPE', 0), 2)) if info.get('trailingPE') else "N/A",
            f"${info.get('fiftyTwoWeekHigh', 0):,.2f}" if info.get('fiftyTwoWeekHigh') else "N/A",
            f"${info.get('fiftyTwoWeekLow', 0):,.2f}" if info.get('fiftyTwoWeekLow') else "N/A",
            f"{info.get('dividendYield', 0):.2%}" if info.get('dividendYield') else "N/A",
            str(round(info.get('beta', 0), 2)) if info.get('beta') else "N/A"
        ]
    }
    stats_df = pd.DataFrame(stats_data)
    st.table(stats_df.set_index('Metric'))

    st.subheader("Interactive Stock Chart")
    hist = stock.history(period="1y")
    if hist.empty:
        st.warning(f"Could not retrieve historical data for {stock_symbol}.")
        return

    # Get the start and end dates from the historical data
    start_date = hist.index.min().date()
    end_date = hist.index.max().date()

    # Get all official US market holidays and early closes using pandas_market_calendars
    nyse = mcal.get_calendar('NYSE')
    schedule = nyse.schedule(start_date=start_date, end_date=end_date)
    all_trading_days = set(schedule.index.date)
    all_days = set(pd.date_range(start=start_date, end=end_date, freq='B').date)
    # Non-trading days are business days not in trading days
    non_trading_days = sorted(list(all_days - all_trading_days))

    # Create range breaks for weekends and market holidays/non-trading days
    rangebreaks = [
        dict(bounds=["sat", "mon"]),
        dict(values=[d.strftime('%Y-%m-%d') for d in non_trading_days])
    ]

    fig = go.Figure()
    fig.add_trace(go.Candlestick(x=hist.index,
                                 open=hist['Open'],
                                 high=hist['High'],
                                 low=hist['Low'],
                                 close=hist['Close'],
                                 name='Price'))

    fig.add_trace(go.Bar(x=hist.index, y=hist['Volume'], name='Volume', yaxis='y2', marker_color='rgba(0,100,180,0.4)'))
    fig.add_trace(go.Scatter(x=hist.index, y=hist['Close'].rolling(window=20).mean(), name='20-day MA', line=dict(color='green')))
    fig.add_trace(go.Scatter(x=hist.index, y=hist['Close'].rolling(window=50).mean(), name='50-day MA', line=dict(color='orange')))
    fig.add_trace(go.Scatter(x=hist.index, y=hist['Close'].rolling(window=200).mean(), name='200-day MA', line=dict(color='purple')))

    fig.update_layout(
        title=f"{stock_symbol} Price, Volume, and Moving Averages (1 Year)",
        yaxis_title='Price (USD)',
        yaxis2=dict(title='Volume', overlaying='y', side='right', showgrid=False),
        xaxis_rangeslider_visible=False,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    fig.update_xaxes(rangebreaks=rangebreaks)
    st.plotly_chart(fig, use_container_width=True)


def main():
    st.set_page_config(page_title="AI Stock Analyst", layout="wide")

    # --- Sidebar ---
    with st.sidebar:
        st.title("🤖 AI Stock Analyst")
        st.markdown("Your personal AI-powered financial analysis assistant.")
        
        stock_symbol = st.text_input("Enter a stock symbol:", "NVDA").upper()
        
        analyze_button = st.button(f"Analyze {stock_symbol}", use_container_width=True)

    # --- Main Page ---
    st.title("AI-Powered Stock Analysis Crew")

    if analyze_button:
        st.header(f"Analysis for {stock_symbol}")
        with st.spinner(f"🚀 Launching AI crew to analyze {stock_symbol}... This may take a few minutes."):
            result = None
            try:
                result = run_analysis(stock_symbol)
                
                analysis = {
                    "technical_analysis": "",
                    "fundamental_analysis": "",
                    "risk_assessment": "",
                    "investment_strategy": ""
                }

                # Extract outputs from each task
                if hasattr(result, 'tasks_output'):
                    for task_output in result.tasks_output:
                        task_desc = task_output.description.lower()
                        if "technical analysis" in task_desc:
                            analysis["technical_analysis"] = task_output.raw
                        elif "fundamental analysis" in task_desc:
                            analysis["fundamental_analysis"] = task_output.raw
                        elif "risk assessment" in task_desc:
                            analysis["risk_assessment"] = task_output.raw
                        elif "investment strategy" in task_desc:
                            analysis["investment_strategy"] = task_output.raw
                else:
                    st.error("Failed to retrieve task outputs from crew result")

                display_stock_data(stock_symbol)
                display_report(analysis)

            except json.JSONDecodeError:
                st.error("Failed to decode the analysis report. The crew's output was not valid JSON.")
                st.subheader("Raw Output from AI Crew:")
                st.text_area("Raw Output", result.raw if result else "No output.", height=300)
            except Exception as e:
                st.error(f"An unexpected error occurred: {e}")
                if result:
                    st.subheader("Raw Output from AI Crew:")
                    st.text_area("Raw Output", result.raw if result else "No output.", height=300)
    else:
        st.markdown("Enter a stock symbol in the sidebar to get a comprehensive analysis from a team of AI agents.")
        st.info("Select a stock from the sidebar and click 'Analyze' to begin.")


if __name__ == "__main__":
    main()
