"""
Practice history router for Translation and Conversation practice.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import Optional
from datetime import datetime, timedelta

from app.database import get_sync_session
from app.models.db_models import TranslationPractice, ConversationPractice
from app.utils.weights import (
    calculate_translation_difficulty,
    calculate_conversation_difficulty,
    calculate_weighted_score,
    get_difficulty_label
)

router = APIRouter(prefix="/api/practice", tags=["practice"])


# ============ Translation Practice ============

@router.get("/translation")
def get_translation_history(
    limit: int = 50,
    db: Session = Depends(get_sync_session)
):
    """Get translation practice history."""
    history = db.query(TranslationPractice)\
        .order_by(desc(TranslationPractice.practiced_at))\
        .limit(limit)\
        .all()

    return {
        "success": True,
        "history": [h.to_dict() for h in history],
        "count": len(history)
    }


@router.post("/translation")
def save_translation_practice(
    data: dict,
    db: Session = Depends(get_sync_session)
):
    """Save a translation practice session."""
    practice = TranslationPractice(
        topic=data.get("topic", ""),
        level=data.get("level", ""),
        direction=data.get("direction", ""),
        length=data.get("length", ""),
        complexity=data.get("complexity", ""),
        score=float(data.get("score", 0))
    )

    db.add(practice)
    db.commit()
    db.refresh(practice)

    return {
        "success": True,
        "message": "Translation practice saved",
        "practice": practice.to_dict()
    }


@router.delete("/translation/{practice_id}")
def delete_translation_practice(
    practice_id: int,
    db: Session = Depends(get_sync_session)
):
    """Delete a translation practice record."""
    practice = db.query(TranslationPractice).filter(
        TranslationPractice.id == practice_id
    ).first()

    if not practice:
        raise HTTPException(status_code=404, detail="Practice record not found")

    db.delete(practice)
    db.commit()

    return {"success": True, "message": "Deleted successfully"}


@router.get("/translation/stats")
def get_translation_stats(db: Session = Depends(get_sync_session)):
    """Get translation practice statistics."""
    total = db.query(TranslationPractice).count()

    avg_score = db.query(func.avg(TranslationPractice.score)).scalar() or 0

    # Last 7 days stats
    week_ago = datetime.now() - timedelta(days=7)
    weekly = db.query(TranslationPractice)\
        .filter(TranslationPractice.practiced_at >= week_ago)\
        .all()

    return {
        "success": True,
        "stats": {
            "total_sessions": total,
            "avg_score": round(float(avg_score), 1),
            "weekly_sessions": len(weekly),
            "weekly_avg": round(sum(p.score for p in weekly) / len(weekly), 1) if weekly else 0
        }
    }


@router.get("/translation/topic-stats")
def get_translation_topic_stats(db: Session = Depends(get_sync_session)):
    """Get translation practice statistics grouped by topic with weighted scores."""
    # Get all practices for detailed calculation
    all_practices = db.query(TranslationPractice).all()

    # Group by topic and calculate weighted scores
    topic_data = {}
    for p in all_practices:
        if p.topic not in topic_data:
            topic_data[p.topic] = {
                "practices": [],
                "directions": {"vi_to_en": 0, "en_to_vi": 0}
            }

        # Calculate difficulty and weighted score
        difficulty = calculate_translation_difficulty(
            p.level or "B1",
            p.direction or "vi_to_en",
            p.length or "medium",
            p.complexity or "compound"
        )
        weighted = calculate_weighted_score(p.score, difficulty)

        topic_data[p.topic]["practices"].append({
            "raw_score": p.score,
            "weighted_score": weighted,
            "difficulty": difficulty,
            "practiced_at": p.practiced_at
        })

        if p.direction in topic_data[p.topic]["directions"]:
            topic_data[p.topic]["directions"][p.direction] += 1

    result = []
    for topic, data in topic_data.items():
        practices = data["practices"]
        raw_scores = [p["raw_score"] for p in practices]
        weighted_scores = [p["weighted_score"] for p in practices]
        difficulties = [p["difficulty"] for p in practices]

        avg_difficulty = sum(difficulties) / len(difficulties) if difficulties else 1.0

        result.append({
            "topic": topic,
            "total_sessions": len(practices),
            "avg_score": round(sum(raw_scores) / len(raw_scores), 1) if raw_scores else 0,
            "avg_weighted_score": round(sum(weighted_scores) / len(weighted_scores), 1) if weighted_scores else 0,
            "best_score": round(max(raw_scores), 1) if raw_scores else 0,
            "best_weighted_score": round(max(weighted_scores), 1) if weighted_scores else 0,
            "lowest_score": round(min(raw_scores), 1) if raw_scores else 0,
            "avg_difficulty": round(avg_difficulty, 2),
            "difficulty_label": get_difficulty_label(avg_difficulty),
            "last_practiced": max(p["practiced_at"] for p in practices).isoformat() if practices else None,
            "vi_to_en_count": data["directions"]["vi_to_en"],
            "en_to_vi_count": data["directions"]["en_to_vi"]
        })

    # Sort by total sessions descending
    result.sort(key=lambda x: x['total_sessions'], reverse=True)

    return {
        "success": True,
        "topic_stats": result,
        "total_topics": len(result)
    }


# ============ Conversation Practice ============

@router.get("/conversation")
def get_conversation_history(
    limit: int = 50,
    db: Session = Depends(get_sync_session)
):
    """Get conversation practice history."""
    history = db.query(ConversationPractice)\
        .order_by(desc(ConversationPractice.practiced_at))\
        .limit(limit)\
        .all()

    return {
        "success": True,
        "history": [h.to_dict() for h in history],
        "count": len(history)
    }


@router.post("/conversation")
def save_conversation_practice(
    data: dict,
    db: Session = Depends(get_sync_session)
):
    """Save a conversation practice session."""
    practice = ConversationPractice(
        topic=data.get("topic", ""),
        level=data.get("level", ""),
        style=data.get("style", ""),
        length=data.get("length", ""),
        score=float(data.get("score", 0))
    )

    db.add(practice)
    db.commit()
    db.refresh(practice)

    return {
        "success": True,
        "message": "Conversation practice saved",
        "practice": practice.to_dict()
    }


@router.delete("/conversation/{practice_id}")
def delete_conversation_practice(
    practice_id: int,
    db: Session = Depends(get_sync_session)
):
    """Delete a conversation practice record."""
    practice = db.query(ConversationPractice).filter(
        ConversationPractice.id == practice_id
    ).first()

    if not practice:
        raise HTTPException(status_code=404, detail="Practice record not found")

    db.delete(practice)
    db.commit()

    return {"success": True, "message": "Deleted successfully"}


@router.get("/conversation/stats")
def get_conversation_stats(db: Session = Depends(get_sync_session)):
    """Get conversation practice statistics."""
    total = db.query(ConversationPractice).count()

    avg_score = db.query(func.avg(ConversationPractice.score)).scalar() or 0

    # Last 7 days stats
    week_ago = datetime.now() - timedelta(days=7)
    weekly = db.query(ConversationPractice)\
        .filter(ConversationPractice.practiced_at >= week_ago)\
        .all()

    return {
        "success": True,
        "stats": {
            "total_sessions": total,
            "avg_score": round(float(avg_score), 1),
            "weekly_sessions": len(weekly),
            "weekly_avg": round(sum(p.score for p in weekly) / len(weekly), 1) if weekly else 0
        }
    }


@router.get("/conversation/topic-stats")
def get_conversation_topic_stats(db: Session = Depends(get_sync_session)):
    """Get conversation practice statistics grouped by topic with weighted scores."""
    # Get all practices for detailed calculation
    all_practices = db.query(ConversationPractice).all()

    # Group by topic and calculate weighted scores
    topic_data = {}
    for p in all_practices:
        if p.topic not in topic_data:
            topic_data[p.topic] = {
                "practices": [],
                "styles": {}
            }

        # Calculate difficulty and weighted score
        difficulty = calculate_conversation_difficulty(
            p.level or "B1",
            p.style or "formal",
            p.length or "medium"
        )
        weighted = calculate_weighted_score(p.score, difficulty)

        topic_data[p.topic]["practices"].append({
            "raw_score": p.score,
            "weighted_score": weighted,
            "difficulty": difficulty,
            "practiced_at": p.practiced_at
        })

        # Count styles
        if p.style:
            topic_data[p.topic]["styles"][p.style] = topic_data[p.topic]["styles"].get(p.style, 0) + 1

    result = []
    for topic, data in topic_data.items():
        practices = data["practices"]
        raw_scores = [p["raw_score"] for p in practices]
        weighted_scores = [p["weighted_score"] for p in practices]
        difficulties = [p["difficulty"] for p in practices]

        avg_difficulty = sum(difficulties) / len(difficulties) if difficulties else 1.0

        result.append({
            "topic": topic,
            "total_sessions": len(practices),
            "avg_score": round(sum(raw_scores) / len(raw_scores), 1) if raw_scores else 0,
            "avg_weighted_score": round(sum(weighted_scores) / len(weighted_scores), 1) if weighted_scores else 0,
            "best_score": round(max(raw_scores), 1) if raw_scores else 0,
            "best_weighted_score": round(max(weighted_scores), 1) if weighted_scores else 0,
            "lowest_score": round(min(raw_scores), 1) if raw_scores else 0,
            "avg_difficulty": round(avg_difficulty, 2),
            "difficulty_label": get_difficulty_label(avg_difficulty),
            "last_practiced": max(p["practiced_at"] for p in practices).isoformat() if practices else None,
            "styles": data["styles"]
        })

    # Sort by total sessions descending
    result.sort(key=lambda x: x['total_sessions'], reverse=True)

    return {
        "success": True,
        "topic_stats": result,
        "total_topics": len(result)
    }


# ============ Combined Stats ============

@router.get("/all/stats")
def get_all_practice_stats(db: Session = Depends(get_sync_session)):
    """Get combined practice statistics for dashboard."""
    # Translation stats
    trans_total = db.query(TranslationPractice).count()
    trans_avg = db.query(func.avg(TranslationPractice.score)).scalar() or 0

    # Conversation stats
    conv_total = db.query(ConversationPractice).count()
    conv_avg = db.query(func.avg(ConversationPractice.score)).scalar() or 0

    # Last 7 days for chart
    week_ago = datetime.now() - timedelta(days=7)

    trans_weekly = db.query(TranslationPractice)\
        .filter(TranslationPractice.practiced_at >= week_ago)\
        .all()

    conv_weekly = db.query(ConversationPractice)\
        .filter(ConversationPractice.practiced_at >= week_ago)\
        .all()

    # Build daily scores for chart
    daily_scores = {}
    for i in range(7):
        date = (datetime.now() - timedelta(days=6-i)).date()
        daily_scores[date.isoformat()] = {"translation": [], "conversation": []}

    for p in trans_weekly:
        date_key = p.practiced_at.date().isoformat()
        if date_key in daily_scores:
            daily_scores[date_key]["translation"].append(p.score)

    for p in conv_weekly:
        date_key = p.practiced_at.date().isoformat()
        if date_key in daily_scores:
            daily_scores[date_key]["conversation"].append(p.score)

    # Calculate averages
    chart_data = []
    for date_key, scores in daily_scores.items():
        chart_data.append({
            "date": date_key,
            "translation": round(sum(scores["translation"]) / len(scores["translation"]), 1) if scores["translation"] else None,
            "conversation": round(sum(scores["conversation"]) / len(scores["conversation"]), 1) if scores["conversation"] else None
        })

    return {
        "success": True,
        "stats": {
            "translation": {
                "total": trans_total,
                "avg_score": round(float(trans_avg), 1)
            },
            "conversation": {
                "total": conv_total,
                "avg_score": round(float(conv_avg), 1)
            }
        },
        "chart_data": chart_data
    }


@router.get("/recent")
def get_recent_activity(
    limit: int = 10,
    db: Session = Depends(get_sync_session)
):
    """Get recent practice activity for dashboard."""
    trans = db.query(TranslationPractice)\
        .order_by(desc(TranslationPractice.practiced_at))\
        .limit(limit)\
        .all()

    conv = db.query(ConversationPractice)\
        .order_by(desc(ConversationPractice.practiced_at))\
        .limit(limit)\
        .all()

    # Merge and sort
    activity = []
    for t in trans:
        d = t.to_dict()
        d["type"] = "Translation"
        activity.append(d)

    for c in conv:
        d = c.to_dict()
        d["type"] = "Conversation"
        activity.append(d)

    # Sort by date descending
    activity.sort(key=lambda x: x["date"] or "", reverse=True)

    return {
        "success": True,
        "activity": activity[:limit]
    }
