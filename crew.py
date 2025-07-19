from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task
from crewai.tools import BaseTool
from tools.tech_analysis import TechAnalystTool
from typing import Any
import yaml
import os

@CrewBase
class QuantCrew:
    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    def __init__(self, provider="openai"):
        if provider == "openai":
            self.llm = LLM(model="gpt-4o-mini")
        else:
            raise ValueError(f"Unsupported provider: {provider}")

        script_dir = os.path.dirname(__file__)
        agents_config_path = os.path.join(script_dir, self.agents_config)
        tasks_config_path = os.path.join(script_dir, self.tasks_config)

        with open(agents_config_path, 'r') as file:
            self.agents = yaml.safe_load(file)
        with open(tasks_config_path, 'r') as file:
            self.tasks = yaml.safe_load(file)

        self.technical_analyst_agent = self.technical_analyst()
        self.investment_strategist_agent = self.investment_strategist()

    @agent
    def technical_analyst(self) -> Agent:
        return Agent(
            role=self.agents['technical_analyst']['role'],
            goal=self.agents['technical_analyst']['goal'],
            backstory=self.agents['technical_analyst']['backstory'],
            verbose=True,
            tools=[TechAnalystTool()],
            llm=self.llm
        )

    @agent
    def investment_strategist(self) -> Agent:
        return Agent(
            role=self.agents['investment_strategist']['role'],
            goal=self.agents['investment_strategist']['goal'],
            backstory=self.agents['investment_strategist']['backstory'],
            verbose=True,
            llm=self.llm
        )

    @task
    def apply_technical_analysis(self) -> Task:
        return Task(
            description=self.tasks['apply_technical_analysis']['description'],
            expected_output=self.tasks['apply_technical_analysis']['expected_output'],
            agent=self.technical_analyst_agent
        )

    @task
    def develop_investment_strategy(self) -> Task:
        return Task(
            description=self.tasks['develop_investment_strategy']['description'],
            expected_output=self.tasks['develop_investment_strategy']['expected_output'],
            agent=self.investment_strategist_agent
        )

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=[
                self.technical_analyst(),
                self.investment_strategist()
            ],
            tasks=[
                self.apply_technical_analysis(),
                self.develop_investment_strategy()
            ],
            process=Process.sequential,
            verbose=True
        )