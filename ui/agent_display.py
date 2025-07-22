import streamlit as st
import json
import re
import pandas as pd

def display_agent_outputs(agent_outputs):
    """
    Display CrewAI agent outputs in Streamlit tabs.
    agent_outputs: dict with keys as agent types and values as output content.
    """
    tab_names = [
        "Technical Analysis",
        "Fundamental Analysis",
        "Risk Assessment",
        "Investment Strategy"
    ]
    display_funcs = [
        display_technical_analysis,
        display_fundamental_analysis,
        display_risk_assessment,
        display_investment_strategy
    ]
    tabs = st.tabs(tab_names)
    for i, tab in enumerate(tabs):
        with tab:
            agent_type = tab_names[i].replace(" ", "_").lower()
            content = agent_outputs.get(agent_type, None)
            display_funcs[i](content)

def display_generic_agent(content, agent_name="Agent Output"):
    """Display output for unknown agent types."""
    st.subheader(agent_name)
    if not content:
        st.warning(f"No output available for {agent_name}")
        return
    analysis = _recursive_extract_json(content)
    if isinstance(analysis, dict):
        df = pd.DataFrame(list(analysis.items()), columns=['Key', 'Value'])
        st.table(df.set_index('Key'))
    else:
        st.markdown(analysis)

def _recursive_extract_json(content):
    """
    Recursively extracts and parses JSON from a string, handling nested JSON.
    """
    if isinstance(content, (dict, list)):
        return content
    
    try:
        # First, try to load the content directly
        data = json.loads(content)
        if isinstance(data, str):
            # If the loaded data is still a string, recurse
            return _recursive_extract_json(data)
        return data
    except (json.JSONDecodeError, TypeError):
        # If direct loading fails, try to find a JSON blob
        match = re.search(r'```json\s*([\s\S]*?)\s*```', content)
        if match:
            try:
                data = json.loads(match.group(1))
                if isinstance(data, str):
                    return _recursive_extract_json(data)
                return data
            except (json.JSONDecodeError, TypeError):
                return content # Return the raw content if all parsing fails
        return content

def display_technical_analysis(content):
    """Display technical analysis results from the agent"""
    if not content:
        st.warning("No technical analysis available")
        return
        
    analysis = _recursive_extract_json(content)
    if isinstance(analysis, dict):
        reasoning = analysis.get("reasoning", None)
        if reasoning:
            st.markdown(f"**Reasoning:**\n{reasoning}")
        st.metric("Trend", analysis.get("trend", "N/A"))
        st.metric("Signal", analysis.get("signal", "N/A"))
        indicators = analysis.get("indicators", {})
        if isinstance(indicators, dict) and indicators:
            df = pd.DataFrame(list(indicators.items()), columns=['Indicator', 'Value'])
            st.table(df.set_index('Indicator'))
        elif indicators:
            st.write(indicators)
    elif isinstance(analysis, str):
        st.markdown(analysis)
    # Do not display raw output or error for other types

def display_fundamental_analysis(content):
    """Display fundamental analysis results from the agent"""
    if not content:
        st.warning("No fundamental analysis available")
        return
        
    analysis = _recursive_extract_json(content)
    if isinstance(analysis, dict) and analysis:
        reasoning = analysis.get("reasoning", None)
        if reasoning:
            st.markdown(f"**Reasoning:**\n{reasoning}")
        # Remove reasoning from table if present
        table_data = {k: v for k, v in analysis.items() if k != "reasoning"}
        df = pd.DataFrame(list(table_data.items()), columns=['Metric', 'Value'])
        st.table(df.set_index('Metric'))
    elif isinstance(analysis, str):
        st.markdown(analysis)
    # Do not display raw output or error for other types


def display_risk_assessment(content):
    """Display risk assessment results from the agent"""
    if not content:
        st.warning("No risk assessment available")
        return
        
    analysis = _recursive_extract_json(content)
    if isinstance(analysis, dict) and analysis:
        reasoning = analysis.get("reasoning", None)
        if reasoning:
            st.markdown(f"**Reasoning:**\n{reasoning}")
        # Remove reasoning from table if present
        table_data = {k: v for k, v in analysis.items() if k != "reasoning"}
        df = pd.DataFrame(list(table_data.items()), columns=['Metric', 'Value'])
        st.table(df.set_index('Metric'))
    elif isinstance(analysis, str):
        st.markdown(analysis)
    # Do not display raw output or error for other types

def display_investment_strategy(content):
    """Display investment strategy in a formatted way"""
    if not content:
        st.warning("No investment strategy available")
        return
        
    strategy = _recursive_extract_json(content)
    if isinstance(strategy, dict):
        recommendation = strategy.get("recommendation", None)
        confidence = strategy.get("confidence_score", "N/A")
        rationale = strategy.get("rationale", "N/A")

        st.metric(label="Confidence Score", value=str(confidence))
        st.subheader("Rationale")
        # Only clean rationale if it's a string
        if isinstance(rationale, str):
            rationale_clean = re.sub(r'<[^>]+>', '', rationale)
            rationale_clean = rationale_clean.replace('&dollar;', '$').replace('&#36;', '$')
            rationale_clean = rationale_clean.replace('$', '\$')
            st.markdown(rationale_clean)
        elif isinstance(rationale, dict):
            # Display dict rationale as a table
            df = pd.DataFrame(list(rationale.items()), columns=["Key", "Value"])
            st.table(df.set_index("Key"))
        else:
            st.write(rationale)

        if isinstance(recommendation, dict):
            st.subheader("Recommendations by Strategy Type")
            for strat_type, details in recommendation.items():
                st.markdown(f"### {strat_type.capitalize()} Strategy")
                if isinstance(details, dict):
                    display_dict = {}
                    for k, v in details.items():
                        key = k.replace('_', ' ').capitalize()
                        val = str(v)
                        if isinstance(v, str):
                            val_clean = re.sub(r'<[^>]+>', '', val)
                            val_clean = val_clean.replace('&dollar;', '$').replace('&#36;', '$')
                            val_clean = val_clean.replace('$', '\$')
                        else:
                            val_clean = val
                        display_dict[key] = val_clean
                    df = pd.DataFrame(list(display_dict.items()), columns=["Parameter", "Value"])
                    for idx, row in df.iterrows():
                        st.markdown(f"**{row['Parameter']}:** {row['Value']}")
                else:
                    st.write(details)
        elif recommendation:
            st.subheader("Recommendation")
            if isinstance(recommendation, str):
                rec_clean = re.sub(r'<[^>]+>', '', recommendation)
                rec_clean = rec_clean.replace('&dollar;', '$').replace('&#36;', '$')
                rec_clean = rec_clean.replace('$', '\$')
                st.markdown(rec_clean)
            elif isinstance(recommendation, dict):
                df = pd.DataFrame(list(recommendation.items()), columns=["Key", "Value"])
                st.table(df.set_index("Key"))
            else:
                st.write(recommendation)
    # Do not display raw output or error for other types




