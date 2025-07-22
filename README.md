# Financial Analyst Crew

## Project Status

**In Development:** This project is currently under active development. The core framework is in place, but features are subject to change and expansion.

## Overview

This project implements a "Quant Crew," a team of AI agents powered by the `crewai` framework, designed to perform comprehensive financial analysis on a given stock. The crew consists of specialized agents that collaborate to analyze a stock from multiple angles: technical, fundamental, risk, and investment strategy.

The primary goal is to create an automated system that can provide a detailed, multi-faceted analysis of a stock, similar to what a team of human financial analysts would produce. This is all presented in a user-friendly web interface built with Streamlit.

## Features

-   **Interactive Web Interface**: A Streamlit application provides a clean and easy-to-use front-end.
-   **Multi-Agent Analysis**: Utilizes a team of AI agents for a multi-angle view of a stock.
-   **Comprehensive Reporting**: Generates a report with sections for technical, fundamental, and risk analysis, plus an overall investment strategy.
-   **Live Financial Data**: Displays up-to-date stock charts and key financial statistics, with accurate market holiday handling.
-   **Agent Reasoning**: Shows the reasoning and explanations from each agent for transparency.

## Project Structure


**Key Files:**
- `app.py`: Streamlit web interface and chart logic
- `crew.py`: Defines agents, tasks, and crew
- `requirements.txt`: Python dependencies
- `config/`: YAML config for agents and tasks
- `tools/`: Custom analysis tools (technical, fundamental, risk)

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
    *   **Technical Analyst**: Analyzes stock price trends and technical indicators.
    *   **Fundamental Analyst**: Examines the company's financial health.
    *   **Risk Analyst**: Assesses risk factors including volatility and sector risks.
    *   **Investment Strategist**: Synthesizes all analyses to provide a final investment strategy and recommendation.

All agent outputs include reasoning for transparency. The Streamlit app displays results in tabs and uses official market calendars to avoid chart gaps.
