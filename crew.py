from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task
from dotenv import load_dotenv
import os
import yaml

# Load environment variables
load_dotenv()

# Import tools
from tools.tech_analysis import TechAnalystTool
from tools.fundamental_analysis import FundamentalAnalysisTool
from tools.competitor_analysis import CompetitorAnalysisTool
from tools.risk_assessment import RiskAssessmentTool
from tools.sentiment_analysis import SentimentAnalysisTool

from crewai import Agent, Crew, Process, Task, LLM, CrewOutput

def run_analysis(stock_symbol: str, period: str = "1y") -> CrewOutput:
    """
    Runs the financial analysis crew for a given stock symbol.
    """
    inputs = {'ticker': stock_symbol, 'period': period}
    quant_crew = QuantCrew()
    result = quant_crew.crew().kickoff(inputs=inputs)
    return result

@CrewBase
class QuantCrew:
    """QuantCrew defines a crew for comprehensive financial analysis."""
    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    def __init__(self, llm: LLM = None):
        """
        Initializes the QuantCrew.
        """
        if llm:
            self.llm = llm
        else:
            self.llm = LLM(model=os.environ.get("OPENAI_MODEL_NAME"))

        script_dir = os.path.dirname(__file__)
        agents_config_path = os.path.join(script_dir, self.agents_config)
        tasks_config_path = os.path.join(script_dir, self.tasks_config)

        with open(agents_config_path, 'r') as file:
            self._agents_def = yaml.safe_load(file)
        with open(tasks_config_path, 'r') as file:
            self._tasks_def = yaml.safe_load(file)

        # Instantiate agents once
        self.technical_analyst_agent = self.technical_analyst()
        self.financial_analyst_agent = self.financial_analyst()
        self.sentiment_analyst_agent = self.sentiment_analyst()
        self.investment_strategist_agent = self.investment_strategist()

    @agent
    def technical_analyst(self) -> Agent:
        return Agent(
            role=self._agents_def['technical_analyst']['role'],
            goal=self._agents_def['technical_analyst']['goal'],
            backstory=self._agents_def['technical_analyst']['backstory'],
            verbose=True,
            tools=[TechAnalystTool()],
            llm=self.llm
        )

    @agent
    def financial_analyst(self) -> Agent:
        return Agent(
            role=self._agents_def['financial_analyst']['role'],
            goal=self._agents_def['financial_analyst']['goal'],
            backstory=self._agents_def['financial_analyst']['backstory'],
            verbose=True,
            tools=[FundamentalAnalysisTool(), CompetitorAnalysisTool(), RiskAssessmentTool()],
            llm=self.llm
        )

    @agent
    def sentiment_analyst(self) -> Agent:
        return Agent(
            role=self._agents_def['sentiment_analyst']['role'],
            goal=self._agents_def['sentiment_analyst']['goal'],
            backstory=self._agents_def['sentiment_analyst']['backstory'],
            verbose=True,
            tools=[SentimentAnalysisTool()],
            llm=self.llm
        )

    @agent
    def investment_strategist(self) -> Agent:
        return Agent(
            role=self._agents_def['investment_strategist']['role'],
            goal=self._agents_def['investment_strategist']['goal'],
            backstory=self._agents_def['investment_strategist']['backstory'],
            verbose=True,
            llm=self.llm
        )

    @task
    def apply_technical_analysis(self) -> Task:
        return Task(
            description=self._tasks_def['apply_technical_analysis']['description'],
            expected_output=self._tasks_def['apply_technical_analysis']['expected_output'],
            agent=self.technical_analyst_agent,
            async_execution=True
        )

    @task
    def analyze_fundamentals(self) -> Task:
        return Task(
            description=self._tasks_def['analyze_fundamentals']['description'],
            expected_output=self._tasks_def['analyze_fundamentals']['expected_output'],
            agent=self.financial_analyst_agent,
            async_execution=True
        )

    @task
    def analyze_competitors(self) -> Task:
        return Task(
            description=self._tasks_def['analyze_competitors']['description'],
            expected_output=self._tasks_def['analyze_competitors']['expected_output'],
            agent=self.financial_analyst_agent,
            async_execution=True
        )
    
    @task
    def assess_risk(self) -> Task:
        return Task(
            description=self._tasks_def['assess_risk']['description'],
            expected_output=self._tasks_def['assess_risk']['expected_output'],
            agent=self.financial_analyst_agent,
            async_execution=True
        )

    @task
    def analyze_sentiment(self) -> Task:
        return Task(
            description=self._tasks_def['analyze_sentiment']['description'],
            expected_output=self._tasks_def['analyze_sentiment']['expected_output'],
            agent=self.sentiment_analyst_agent,
            async_execution=True
        )

    @task
    def develop_investment_strategy(self) -> Task:
        return Task(
            description=self._tasks_def['develop_investment_strategy']['description'],
            expected_output=self._tasks_def['develop_investment_strategy']['expected_output'],
            agent=self.investment_strategist_agent,
            context=[
                self.apply_technical_analysis(),
                self.analyze_fundamentals(),
                self.analyze_competitors(),
                self.assess_risk(),
                self.analyze_sentiment()
            ]
        )

    @crew
    def crew(self) -> Crew:
        """Creates and configures the financial analysis crew."""
        return Crew(
            agents=[
                self.technical_analyst_agent,
                self.financial_analyst_agent,
                self.sentiment_analyst_agent,
                self.investment_strategist_agent
            ],
            tasks=[
                # These tasks will run in parallel
                self.analyze_fundamentals(),
                self.apply_technical_analysis(),
                self.analyze_competitors(),
                self.assess_risk(),
                self.analyze_sentiment(),
                # This task will run sequentially after the above tasks are complete
                self.develop_investment_strategy()
            ],
            process=Process.sequential,
            verbose=True
        )