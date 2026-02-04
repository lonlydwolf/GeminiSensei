from fastapi import APIRouter

from agents.manager import agent_manager
from core.types import AgentMetadata

router = APIRouter(prefix="/api/agents", tags=["agents"])

@router.get("", response_model=list[AgentMetadata])
async def list_agents() -> list[AgentMetadata]:
    """List all available agents and their metadata."""
    return agent_manager.get_agents_metadata()
