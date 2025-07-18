import os
from crew import QuantCrew
from dotenv import load_dotenv

load_dotenv()

def run():
    inputs = {
        'ticker': "AAPL",
        'period': "1y"
    }
    myCrew = QuantCrew(provider="openai")
    result = myCrew.crew().kickoff(inputs)

if __name__ == "__main__":
    run()

