import os
from crewai import Agent, Task, Crew
from crewai_tools import SerperDevTool
from langchain_openai import ChatOpenAI
import configparser
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG, filename="logs.log", format='%(asctime)s [%(levelname)s]: %(message)s')

# Load configuration settings from env.ini
config = configparser.ConfigParser()
config.read('env.ini')

# Retrieve API keys from the config file
OPENAI_API_KEY = config['OPEN_AI']['OPENAI_API_KEY']
SERPER_API_KEY = config['SERPER']['SERPER_API_KEY']

# Initialize the search tool with the Serper API key
search_tool = SerperDevTool(api_key=SERPER_API_KEY)

# Define your agents with roles and goals
researcher = Agent(
    role="Senior Research Assistant",
    goal="Look up the latest advancements in AI agents.",
    backstory="""You work at a leading tech think tank.
    Your expertise lies in searching Google for AI Agent frameworks.
    You have a knack for dissecting complex data and presenting actionable insights.""",
    verbose=True,
    allow_delegation=False,
    tools=[search_tool],
    llm=ChatOpenAI(
        api_key=OPENAI_API_KEY,  # Provide the OpenAI API key
        model_name="gpt-4-turbo-preview",
        temperature=0.2,
        max_tokens=200,  # Adjust max tokens based on needs
        top_p=0.9,
        frequency_penalty=0.2,
        presence_penalty=0.3
    ),
    max_iterations=200,  # Increase iterations further
    max_time=3600  # Increase time limit further (60 minutes)
)

writer = Agent(
    role="Professional Short-Article Writer",
    goal="Summarize the latest advancements in AI agents in a concise article.",
    backstory="""You are a renowned Content Strategist, known for your insightful and engaging articles.
    You transform complex concepts into compelling narratives.""",
    verbose=True,
    allow_delegation=True,
    llm=ChatOpenAI(
        api_key=OPENAI_API_KEY,  # Provide the OpenAI API key
        model_name="gpt-4-turbo-preview",
        temperature=0.7,
        max_tokens=300,  # Adjust max tokens based on needs
        top_p=0.85,
        frequency_penalty=0.1,
        presence_penalty=0.6
    ),
    max_iterations=200,  # Increase iterations further
    max_time=3600  # Increase time limit further (60 minutes)
)

# Create tasks for your agents
task1 = Task(
    description="""Conduct a comprehensive analysis of the latest advancements in AI Agents in March 2024.
    Identify key trends, breakthrough technologies, and potential industry impacts.""",
    expected_output="Full analysis report in bullet points",
    agent=researcher
)

task2 = Task(
    description="""Using the insights provided, write a short article
    that highlights the most significant AI Agent advancements.
    Your post should be informative yet accessible, catering to a tech-savvy audience.
    Make it sound cool, avoid complex words so it doesn't sound like AI.""",
    expected_output="Full blog post of at least 3 paragraphs",
    agent=writer
)

# Instantiate your crew with a sequential process
crew = Crew(
    agents=[researcher, writer],
    tasks=[task1, task2],
    verbose=True
)

# Kick off the crew process and get results
result = crew.kickoff()

# Display the result
print("##############")
print(result)
