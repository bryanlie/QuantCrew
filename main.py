import os
from crew import QuantCrew
from dotenv import load_dotenv

load_dotenv()

def run():
    """
    Run the QuantCrew with specified inputs.
    """
    inputs = {
        'ticker': "AAPL",
        'period': "1y"
    }
    # Instantiate the crew. The LLM is now configured within the QuantCrew class.
    quant_crew = QuantCrew()
    result = quant_crew.crew().kickoff(inputs)
    print("\n\n########################")
    print("## Here is the result")
    print("########################\n")
    print(result)

if __name__ == "__main__":
    run()