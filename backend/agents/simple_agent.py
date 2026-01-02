from agno.agent import Agent
from agno.models.ollama import Ollama

from app.models import OLLAMA_BASE_URL, OLLAMA_MODEL_ID

agno_simple = Agent(
    id="agno-simple",
    name="Agno Simple Agent",
    model=Ollama(id=OLLAMA_MODEL_ID, host=OLLAMA_BASE_URL),
    # Description of the agent
    # Defines agent identity/persona. Start of system message
    description="You are a helpful assistant. All your responses must be brief and concise.",
    # Instructions for the agent
    # Defines specific behaviors/rules. Inside <instructions> XML tags
    instructions="Always write max of 2 sentences.",
    # -*- Other settings -*-
    # Format responses using markdown
    markdown=True,
    # Add the current date and time to the instructions
    add_datetime_to_context=True,
)
