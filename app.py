import streamlit as st
import yfinance as yf
import plotly.graph_objs as go
from crew import run_analysis
import json
import pandas as pd
from crewai import CrewOutput

def display_report(analysis):
    """Displays the analysis report using Streamlit tabs."""
    st.header("AI Analysis Report")

    tab_titles = [
        "📈 Investment Strategy",
        "📊 Technical Analysis",
        "📑 Fundamental Analysis",
        "👥 Competitor Analysis",
        "⚖️ Risk Assessment",
        "📰 Sentiment Analysis"
    ]
    tabs = st.tabs(tab_titles)

    with tabs[0]:
        st.subheader("Investment Strategy & Recommendation")
        st.markdown(analysis.get('investment_strategy', 'No investment strategy available.'))

    with tabs[1]:
        st.subheader("Technical Analysis")
        st.markdown(analysis.get('technical_analysis', 'No technical analysis available.'))
        st.subheader("Chart Patterns")
        st.markdown(analysis.get('chart_patterns', 'No chart patterns identified.'))

    with tabs[2]:
        st.subheader("Fundamental Analysis")
        st.markdown(analysis.get('fundamental_analysis', 'No fundamental analysis available.'))

    with tabs[3]:
        st.subheader("Competitor Analysis")
        st.markdown(analysis.get('competitor_analysis', 'No competitor analysis available.'))

    with tabs[4]:
        st.subheader("Risk Assessment")
        st.markdown(analysis.get('risk_assessment', 'No risk assessment available.'))

    with tabs[5]:
        st.subheader("Sentiment Analysis")
        st.markdown(analysis.get('sentiment_analysis', 'No sentiment analysis available.'))

def display_agent_outputs(result: CrewOutput):
    """Displays the outputs from each agent's task in a formatted way."""
    st.header("Agent-by-Agent Breakdown")
    with st.expander("Show Agent Process"):
        if not hasattr(result, 'task_outputs') or not result.task_outputs:
            st.warning("Could not find task outputs in the result object.")
            st.write("Available attributes:", dir(result))
            return

        for task_output in result.task_outputs:
            st.subheader(f"Task for: {task_output.task.agent.role}")
            st.markdown(f"> {task_output.task.description}")

            st.markdown("#### Agent's Raw Output:")
            try:
                # Try to load the raw output as JSON
                output_data = json.loads(task_output.raw)
                
                # Display the JSON in an expandable format
                st.json(output_data)

                # If the data is a list of dictionaries, it's ideal for a table
                if isinstance(output_data, list) and all(isinstance(i, dict) for i in output_data):
                    st.markdown("#### Formatted as Table:")
                    st.table(pd.DataFrame(output_data))
                # If it's a dictionary, we can also create a table
                elif isinstance(output_data, dict):
                    # A special case for the competitor analysis format
                    if 'competitors' in output_data and isinstance(output_data['competitors'], list):
                        st.markdown("#### Formatted Competitors Table:")
                        st.table(pd.DataFrame(output_data['competitors']))
                    else:
                        st.markdown("#### Formatted as Table:")
                        st.table(pd.DataFrame(output_data.items(), columns=['Key', 'Value']))

            except (json.JSONDecodeError, TypeError):
                # If output is not JSON, display as plain text
                st.text(task_output.raw)
            
            st.markdown("---")

def display_stock_data(stock_symbol):
    """Fetches and displays stock data and chart."""
    st.header(f"Live Stock Data for {stock_symbol}")
    stock = yf.Ticker(stock_symbol)
    
    st.subheader("Key Statistics")
    info = stock.info
    
    stats_data = {
        "Metric": ["Market Cap", "P/E Ratio", "52 Week High", "52 Week Low", "Dividend Yield", "Beta"],
        "Value": [
            f"${info.get('marketCap', 'N/A'):,}",
            str(round(info.get('trailingPE', 0), 2)),
            f"${info.get('fiftyTwoWeekHigh', 0):,.2f}",
            f"${info.get('fiftyTwoWeekLow', 0):,.2f}",
            f"{info.get('dividendYield', 0):.2%}",
            str(round(info.get('beta', 0), 2))
        ]
    }
    stats_df = pd.DataFrame(stats_data)
    st.table(stats_df.set_index('Metric'))

    st.subheader("Interactive Stock Chart")
    hist = stock.history(period="1y")

    fig = go.Figure()
    fig.add_trace(go.Candlestick(x=hist.index,
                                 open=hist['Open'],
                                 high=hist['High'],
                                 low=hist['Low'],
                                 close=hist['Close'],
                                 name='Price'))

    fig.add_trace(go.Bar(x=hist.index, y=hist['Volume'], name='Volume', yaxis='y2', marker_color='rgba(0,100,180,0.4)'))
    fig.add_trace(go.Scatter(x=hist.index, y=hist['Close'].rolling(window=50).mean(), name='50-day MA', line=dict(color='orange')))
    fig.add_trace(go.Scatter(x=hist.index, y=hist['Close'].rolling(window=200).mean(), name='200-day MA', line=dict(color='purple')))

    fig.update_layout(
        title=f"{stock_symbol} Price, Volume, and Moving Averages (1 Year)",
        yaxis_title='Price (USD)',
        yaxis2=dict(title='Volume', overlaying='y', side='right', showgrid=False),
        xaxis_rangeslider_visible=False,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    st.plotly_chart(fig, use_container_width=True)


def main():
    st.set_page_config(page_title="AI Stock Analyst", layout="wide")
    st.title("🤖 AI-Powered Stock Analysis Crew")
    st.markdown("Enter a stock symbol to get a comprehensive analysis from a team of AI agents.")

    stock_symbol = st.text_input("Enter stock symbol (e.g., AAPL, TSLA, NVDA):", "NVDA").upper()

    if st.button(f"Analyze {stock_symbol}"):
        with st.spinner(f"🚀 Launching AI crew to analyze {stock_symbol}... This may take a few minutes."):
            result = None
            try:
                result = run_analysis(stock_symbol)
                analysis = json.loads(result.raw)
                
                display_report(analysis)
                display_stock_data(stock_symbol)
                display_agent_outputs(result)

            except json.JSONDecodeError:
                st.error("Failed to decode the analysis report. The crew's output was not valid JSON.")
                st.subheader("Raw Output from AI Crew:")
                st.text_area("Raw Output", result.raw if result else "No output.", height=300)
            except Exception as e:
                st.error(f"An unexpected error occurred: {e}")
                if result:
                    st.subheader("Raw Output from AI Crew:")
                    st.text_area("Raw Output", result.raw if result else "No output.", height=300)

if __name__ == "__main__":
    main()
