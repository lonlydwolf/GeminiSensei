"""Roadmap API endpoint"""

import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from agents.roadmap_creator import roadmap_creator
from core.types import RoadmapCreateRequest, RoadmapCreateResult, RoadmapResponse
from database.models import Phase, Roadmap
from database.session import get_db
from schemas.models import RoadmapReadDetailed

db_dep = Annotated[AsyncSession, Depends(get_db)]

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/roadmap", tags=["roadmap"])


@router.post("/create", response_model=RoadmapResponse)
async def create_roadmap(request: RoadmapCreateRequest, db: db_dep):
    """Create a new learning roadmap.

    Args:
        request: Roadmap Creation request
        db: Database session

    Returns:
        Roadmap ID and success message
    """
    try:
        result: RoadmapCreateResult = await roadmap_creator.create_roadmap(
            goal=request.goal, background=request.background, preferences=request.preferences, db=db
        )

        return RoadmapResponse(roadmap_id=result.roadmap_id, message="Roadmap created successfully")

    except Exception as e:
        logger.error(f"Failed to create roadmap: {e}")
        raise HTTPException(
            status_code=500, detail="Internal server error occurred while creating roadmap"
        )


@router.get("/{roadmap_id}", response_model=RoadmapReadDetailed)
async def get_roadmap(roadmap_id: str, db: db_dep):
    """Get roadmap details with all phases and lessons.

    Args:
        roadmap_id: Roadmap ID
        db: Database session

    Returns:
        Complete roadmap data
    """
    try:
        result = await db.execute(
            select(Roadmap)
            .options(selectinload(Roadmap.phases).selectinload(Phase.lessons))
            .where(Roadmap.id == roadmap_id)
        )
        roadmap = result.scalar_one_or_none()

        if not roadmap:
            raise HTTPException(status_code=404, detail="Roadmap not found")
        return roadmap

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching roadmap: {e}")
        raise HTTPException(
            status_code=500, detail="Internal server error occurred while fetching roadmap"
        )
