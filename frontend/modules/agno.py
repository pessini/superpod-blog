from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import AsyncGenerator, Dict, List, Literal, Optional

from agno.client import AgentOSClient
from agno.db.base import SessionType

from .config import AGNO_BASE_URL
from .logging import logger

EntityType = Literal["agent", "workflow", "team"]


@dataclass
class Entity:
    """Represents an AgentOS entity (agent, workflow, or team)."""

    id: str
    name: str
    type: EntityType
    description: str = ""

    @property
    def profile_key(self) -> str:
        """Generate unique key for chat profile."""
        return f"{self.type}:{self.id}"

    def __str__(self) -> str:
        return f"{self.type.title()}: {self.name} ({self.id})"

    @classmethod
    def from_agno_object(cls, obj, entity_type: EntityType) -> "Entity":
        """Create Entity from AgentOS API object."""
        return cls(
            id=getattr(obj, "id", obj.name),
            name=obj.name,
            type=entity_type,
            description=getattr(obj, "description", f"{entity_type.title()}: {obj.name}"),
        )


class AgnoClientError(Exception):
    """Base exception for AgnoService errors."""

    pass


class AgnoClient:
    """Service for interacting with AgentOS API."""

    _entities_cache: Optional[Dict[str, Entity]] = None
    _cache_timestamp: Optional[datetime] = None
    _cache_ttl: timedelta = timedelta(minutes=5)

    def __init__(self, base_url: Optional[str] = None, timeout: float = 60.0):
        """
        Initialize AgnoService.

        Args:
            base_url: AgnoOS instance URL (defaults to AGNO_BASE_URL from config)
            timeout: Request timeout in seconds (default: 60.0)
        """
        self.base_url = base_url or AGNO_BASE_URL
        self.timeout = timeout
        self.client = AgentOSClient(base_url=self.base_url, timeout=self.timeout)
        logger.info(f"AgnoService initialized with base_url: {self.base_url}, timeout: {self.timeout}")

    async def health_check(self) -> bool:
        """Check if AgnoOS instance is reachable."""
        try:
            await self.client.aget_config()
            logger.info("AgnoOS health check passed")
            return True
        except Exception as e:
            logger.error(f"AgnoOS health check failed: {e}")
            return False

    async def get_available_entities(self, force_refresh: bool = False) -> Dict[str, Entity]:
        """
        Fetch available entities from AgnoOS with caching.

        Args:
            force_refresh: If True, bypass cache and fetch fresh data

        Returns:
            Dictionary of entities keyed by profile_key

        Raises:
            AgnoClientError: If unable to fetch entities
        """
        if not force_refresh and self._is_cache_valid():
            logger.debug("Returning cached entities")
            return self._entities_cache

        try:
            config = await self.client.aget_config()
            entities = {}

            for entity_list, entity_type in [
                (config.agents, "agent"),
                (config.workflows, "workflow"),
                (config.teams, "team"),
            ]:
                if entity_list:
                    for obj in entity_list:
                        entity = Entity.from_agno_object(obj, entity_type)
                        entities[entity.profile_key] = entity

            self._entities_cache = entities
            self._cache_timestamp = datetime.now()

            logger.info(f"Fetched {len(entities)} entities from AgnoOS")
            return entities

        except Exception as e:
            logger.error(f"Error fetching Agno entities: {e}")
            raise AgnoClientError(f"Failed to fetch entities: {str(e)}")

    def _is_cache_valid(self) -> bool:
        """Check if the entities cache is still valid."""
        if self._entities_cache is None or self._cache_timestamp is None:
            return False
        return datetime.now() - self._cache_timestamp < self._cache_ttl

    async def create_session(self, user_id: str, entity_id: str, entity_type: EntityType) -> str:
        """
        Create a new session for the given entity.

        Args:
            user_id: Unique identifier for the user
            entity_id: ID of the agent/workflow/team
            entity_type: Type of entity

        Returns:
            Session ID string

        Raises:
            AgnoClientError: If session creation fails
        """
        try:
            create_args = {"user_id": user_id}

            match entity_type:
                case "agent":
                    create_args["agent_id"] = entity_id
                case "team":
                    create_args["team_id"] = entity_id
                    create_args["session_type"] = SessionType.TEAM
                case "workflow":
                    create_args["workflow_id"] = entity_id
                    create_args["session_type"] = SessionType.WORKFLOW

            session = await self.client.create_session(**create_args)
            session_id = session.session_id

            logger.info(f"Created session {session_id} for user {user_id} with {entity_type}: {entity_id}")
            return session_id

        except Exception as e:
            logger.error(f"Error creating Agno session: {e}")
            raise AgnoClientError(f"Failed to create session: {str(e)}")

    async def send_message(
        self, session_id: str, message: str, entity_id: str, entity_type: EntityType, user_data: Optional[Dict] = None
    ) -> AsyncGenerator[str, None]:
        """
        Send a message to the Agno session and stream the response.

        Args:
            session_id: Session identifier
            message: Message to send
            entity_id: ID of the agent/workflow/team
            entity_type: Type of entity
            user_data: Optional user context data

        Yields:
            Response chunks as strings

        Raises:
            AgnoClientError: If message sending fails
        """
        try:
            logger.debug(f"Sending message to {entity_type}:{entity_id} in session {session_id}")

            params = {
                "session_id": session_id,
                "message": message,
            }

            match entity_type:
                case "agent":
                    stream = self.client.run_agent_stream(agent_id=entity_id, **params)
                case "workflow":
                    stream = self.client.run_workflow_stream(workflow_id=entity_id, **params)
                case "team":
                    stream = self.client.run_team_stream(team_id=entity_id, **params)

            async for event in stream:
                if hasattr(event, "content") and event.content:
                    yield event.content

        except Exception as e:
            logger.error(f"Error sending message to Agno: {e}")
            raise AgnoClientError(f"Failed to send message: {str(e)}")

    async def get_session_history(self, session_id: str) -> List[Dict]:
        """Retrieve the message history for a session."""
        try:
            session_data = await self.client.get_session(session_id=session_id)

            if hasattr(session_data, "memory") and hasattr(session_data.memory, "messages"):
                return session_data.memory.messages
            elif hasattr(session_data, "messages"):
                return session_data.messages

            return []

        except Exception as e:
            logger.error(f"Error retrieving session history: {e}")
            return []

    async def delete_session(self, session_id: str) -> bool:
        """Delete a session."""
        try:
            await self.client.delete_session(session_id=session_id)
            logger.info(f"Deleted session {session_id}")
            return True

        except Exception as e:
            logger.error(f"Error deleting session: {e}")
            raise AgnoClientError(f"Failed to delete session: {str(e)}")

    def clear_cache(self) -> None:
        """Clear the entities cache to force refresh on next request."""
        self._entities_cache = None
        self._cache_timestamp = None
        logger.info("Entities cache cleared")

    @classmethod
    def set_cache_ttl(cls, minutes: int) -> None:
        """Set the cache time-to-live for all instances."""
        cls._cache_ttl = timedelta(minutes=minutes)
        logger.info(f"Cache TTL set to {minutes} minutes")


if __name__ == "__main__":
    """Debug helper to inspect AgentOSClient attributes"""
    print("Attributes of AgentOSClient:")
    for attr in dir(AgentOSClient):
        if not attr.startswith("_"):
            print(f"- {attr}")
