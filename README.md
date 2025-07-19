# Financial Analyst Crew

## Project Status

**In Development:** This project is currently under active development. The core framework is in place, but features are subject to change and expansion.

## Overview

This project implements a "Quant Crew," a team of AI agents powered by the `crewai` framework, designed to perform comprehensive financial analysis on a given stock. The crew consists of specialized agents that collaborate to analyze technical indicators, assess market trends, and formulate investment strategies.

The primary goal is to create an automated system that can provide a detailed, multi-faceted analysis of a stock, similar to what a team of human financial analysts would produce.

## Project Structure

The project is organized as follows:

```
FinancialAnalyst/
│
├─── main.py                # Main entry point to run the crew
├─── crew.py                # Defines the agents, tasks, and the crew itself
├─── requirements.txt       # Python dependencies
│
├─── config/
│    ├─── agents.yaml       # Configuration for the different agents (roles, goals)
│    └─── tasks.yaml        # Configuration for the tasks (descriptions, expected outputs)
│
└─── tools/
     └─── tech_analysis.py  # Custom tool for performing technical analysis
```

- **`main.py`**: The script to initialize and kick off the analysis process.
- **`crew.py`**: The heart of the project, where the `QuantCrew` class uses `@agent` and `@task` decorators to assemble the AI team.
- **`config/`**: Contains YAML files that define the properties of agents and tasks, allowing for easy modification without changing the core logic.
- **`tools/`**: Holds custom tools that agents can use to perform specific actions, such as fetching and analyzing stock data.

## Setup

1.  **Install Dependencies:**
    Navigate to the `FinancialAnalyst` directory and install the required Python packages.
    ```bash
    pip install -r requirements.txt
    ```

2.  **Configure Environment Variables:**
    This project requires API keys for the language models. Create a `.env` file in the root of the `stockAgent` directory and add your OpenAI API key:
    ```
    OPENAI_API_KEY="your-api-key-here"
    ```

## Usage

To run the financial analysis, execute the `main.py` script from within the `FinancialAnalyst` directory:

```bash
python main.py
```

By default, the crew uses the OpenAI `gpt-4o-mini` model. You can switch to a local Ollama model by modifying the `QuantCrew` instantiation in `main.py`:

```python
# In main.py
# myCrew = QuantCrew(provider="openai")  // Default
myCrew = QuantCrew(provider="ollama") // To use Ollama
```

The stock ticker to be analyzed is currently hardcoded in `main.py` but will be parameterized in a future update.

## How It Works

The `QuantCrew` operates sequentially:

1.  **Technical Analysis**: The `technical_analyst` agent uses the `TechAnalystTool` to perform a detailed technical analysis of the stock.
2.  **Investment Strategy**: The `investment_strategist` agent takes the technical analysis report and develops a comprehensive investment strategy based on the findings.

The process is orchestrated by `crewai`, which manages the flow of information between agents and tasks.
