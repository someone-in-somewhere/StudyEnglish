"""Topics API endpoints."""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_sync_session
from app.services.topic_service import TopicService
from app.models.schemas import TopicsResponse

router = APIRouter(prefix="/api/topics", tags=["topics"])


@router.get("", response_model=TopicsResponse)
def get_all_topics(db: Session = Depends(get_sync_session)):
    """Get all 23 predefined topics with statistics."""
    service = TopicService(db)

    topics = service.get_topics_with_stats()

    return TopicsResponse(success=True, topics=topics, total=len(topics))


@router.get("/list")
def get_topics_list():
    """Get simple list of all topics (no stats)."""
    topics = TopicService.get_all_topics()

    return {"success": True, "topics": topics}


@router.get("/tier/{tier}")
def get_topics_by_tier(tier: int):
    """Get topics by tier (1-6)."""
    if tier < 1 or tier > 6:
        raise HTTPException(status_code=400, detail="Tier must be between 1 and 6")

    topics = TopicService.get_topics_by_tier(tier)

    return {"success": True, "tier": tier, "topics": topics}


@router.get("/tiers")
def get_tier_names():
    """Get tier names mapping."""
    return {"success": True, "tiers": TopicService.get_tier_names()}


@router.get("/{topic_id}")
def get_topic(topic_id: int):
    """Get a specific topic by ID."""
    topic = TopicService.get_topic_by_id(topic_id)

    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")

    return {"success": True, "topic": topic}


@router.get("/search/{query}")
def search_topics(
    query: str,
    db: Session = Depends(get_sync_session)
):
    """Search topics by name."""
    service = TopicService(db)

    results = service.search_topics(query)

    return {"success": True, "results": results, "count": len(results)}
