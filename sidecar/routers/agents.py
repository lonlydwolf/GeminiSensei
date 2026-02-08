from fastapi import APIRouter

from agents.manager import agent_manager
from core.types import AgentConfig

router = APIRouter(prefix="/api/agents", tags=["agents"])


@router.get("", response_model=list[AgentConfig])
async def list_agents() -> list[AgentConfig]:
    """List all available agents and their metadata."""
    return agent_manager.get_agents_metadata()
