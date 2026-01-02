"""AgentOS"""

from pathlib import Path

from agno.os import AgentOS

from agents.agno_assist import agno_assist
from agents.simple_agent import agno_simple
from agents.web_agent import web_agent
from modules.langfuse import init_tracing
from teams.multilingual_team import multilingual_team
from teams.reasoning_finance_team import reasoning_research_team
from workflows.investment_workflow import investment_workflow
from workflows.research_workflow import research_workflow

# Ensure tracing is initialized before any agent calls happen
init_tracing()

os_config_path = str(Path(__file__).parent.joinpath("config.yaml"))

# Create the AgentOS
agent_os = AgentOS(
    id="agentos-docker",
    agents=[agno_simple, web_agent, agno_assist],
    teams=[multilingual_team, reasoning_research_team],
    workflows=[investment_workflow, research_workflow],
    # Configuration for the AgentOS
    config=os_config_path,
)

app = agent_os.get_app()

if __name__ == "__main__":
    # Serve the application
    agent_os.serve(app="main:app", reload=True)
