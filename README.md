# Financial Analyst Crew

## Project Status

**In Development:** This project is currently under active development. The core framework is in place, but features are subject to change and expansion.

## Overview

This project implements a "Quant Crew," a team of AI agents powered by the `crewai` framework, designed to perform comprehensive financial analysis on a given stock. The crew consists of specialized agents that collaborate to analyze a stock from multiple angles: technical, fundamental, competitive, risk, and market sentiment.

The primary goal is to create an automated system that can provide a detailed, multi-faceted analysis of a stock, similar to what a team of human financial analysts would produce. This is all presented in a user-friendly web interface built with Streamlit.

## Features

-   **Interactive Web Interface**: A Streamlit application provides a clean and easy-to-use front-end.
-   **Multi-Agent Analysis**: Utilizes a team of AI agents for a 360-degree view of a stock.
-   **Comprehensive Reporting**: Generates a final report with sections for technical, fundamental, competitor, risk, and sentiment analysis, plus an overall investment strategy.
-   **Live Financial Data**: Displays up-to-date stock charts and key financial statistics.
-   **Transparent Process**: Includes an "Agent-by-Agent Breakdown" to show the detailed output from each AI agent, offering insight into the analysis process.

## Project Structure

The project is organized as follows:

```
FinancialAnalyst/
│
├─── app.py                 # The Streamlit web interface
├─── crew.py                # Defines the agents, tasks, and the crew itself
├─── requirements.txt       # Python dependencies
│
├─── config/
│    ├─── agents.yaml       # Configuration for the different agents (roles, goals)
│    └─── tasks.yaml        # Configuration for the tasks (descriptions, expected outputs)
│
└─── tools/
     ├─── tech_analysis.py         # Custom tool for performing technical analysis
     ├─── fundamental_analysis.py  # Custom tool for fundamental analysis
     ├─── competitor_analysis.py   # Custom tool for competitor analysis
     ├─── risk_assessment.py       # Custom tool for risk assessment
     └─── sentiment_analysis.py    # Custom tool for sentiment analysis
```

- **`app.py`**: The main entry point to launch the Streamlit web application.
- **`crew.py`**: The heart of the project, where the `QuantCrew` class assembles the AI team.
- **`config/`**: Contains YAML files that define the properties of agents and tasks.
- **`tools/`**: Holds custom tools that agents use to perform specific actions.

## Setup

1.  **Install Dependencies:**
    Navigate to the `FinancialAnalyst` directory and install the required Python packages.
    ```bash
    pip install -r requirements.txt
    ```

2.  **Configure Environment Variables:**
    Create a `.env` file in the root of the `stockAgent` directory. You will need API keys for your chosen language model and for financial data.

    ```
    # For OpenAI models
    OPENAI_API_KEY="your-openai-api-key"
    OPENAI_MODEL_NAME="gpt-4o-mini"

    # For Competitor Analysis Tool (get a free key from https://site.financialmodelingprep.com/developer/docs)
    FMP_API_KEY="your-fmp-api-key"
    ```

## Usage

To run the financial analysis application, execute the `app.py` script from the project root directory:

```bash
streamlit run FinancialAnalyst/app.py
```

This will launch the web interface in your browser. Enter a stock ticker and click "Analyze" to start the process.

## How It Works

The `QuantCrew` is composed of several specialized agents that work together to perform a comprehensive stock analysis. The workflow is designed for efficiency, with several analyses running in parallel.

1.  **Parallel Analysis Phase**:
    *   **Technical Analyst**: Uses the `TechAnalystTool` to analyze stock price trends, chart patterns, and technical indicators.
    *   **Financial Analyst**: Uses a suite of tools (`FundamentalAnalysisTool`, `CompetitorAnalysisTool`, `RiskAssessmentTool`) to examine the company's financial health, competitive landscape, and potential risks.
    *   **Sentiment Analyst**: Employs the `SentimentAnalysisTool` to gauge market sentiment by analyzing news headlines and social media.

    These initial tasks are executed concurrently to gather diverse insights quickly.

2.  **Synthesis and Strategy Phase**:
    *   **Investment Strategist**: This agent receives the reports from all the other analysts. It synthesizes the technical, fundamental, competitive, risk, and sentiment analyses to develop a holistic investment strategy and provide a final recommendation, formatted as a single JSON object.

The process is orchestrated by `crewai`, which manages the flow of information between agents and ensures that the final strategy is based on a well-rounded view of the stock. The Streamlit app then parses this final output and displays it in a structured report.
