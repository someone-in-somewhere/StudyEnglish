"""
Analytics router for progress tracking and statistics.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from datetime import datetime, timedelta, date
from collections import defaultdict

from app.database import get_db
from app.models.db_models import (
    UserVocabulary, Quiz, StudySession,
    TranslationPractice, ConversationPractice
)

router = APIRouter(prefix="/api/analytics", tags=["analytics"])


@router.get("/heatmap")
def get_activity_heatmap(
    days: int = 365,
    db: Session = Depends(get_db)
):
    """Get activity heatmap data (like GitHub contribution graph)."""
    end_date = date.today()
    start_date = end_date - timedelta(days=days)

    # Initialize all days with 0
    heatmap = {}
    current = start_date
    while current <= end_date:
        heatmap[current.isoformat()] = 0
        current += timedelta(days=1)

    # Count vocabulary learned per day
    vocab_counts = db.query(
        func.date(UserVocabulary.learned_at).label('date'),
        func.count(UserVocabulary.id).label('count')
    ).filter(
        UserVocabulary.learned_at >= start_date
    ).group_by(
        func.date(UserVocabulary.learned_at)
    ).all()

    for row in vocab_counts:
        if row.date:
            date_str = row.date.isoformat() if hasattr(row.date, 'isoformat') else str(row.date)
            if date_str in heatmap:
                heatmap[date_str] += row.count

    # Count quizzes per day
    quiz_counts = db.query(
        func.date(Quiz.completed_at).label('date'),
        func.count(Quiz.id).label('count')
    ).filter(
        Quiz.completed_at >= start_date,
        Quiz.completed_at.isnot(None)
    ).group_by(
        func.date(Quiz.completed_at)
    ).all()

    for row in quiz_counts:
        if row.date:
            date_str = row.date.isoformat() if hasattr(row.date, 'isoformat') else str(row.date)
            if date_str in heatmap:
                heatmap[date_str] += row.count * 2  # Weight quizzes more

    # Count practice sessions
    trans_counts = db.query(
        func.date(TranslationPractice.practiced_at).label('date'),
        func.count(TranslationPractice.id).label('count')
    ).filter(
        TranslationPractice.practiced_at >= start_date
    ).group_by(
        func.date(TranslationPractice.practiced_at)
    ).all()

    for row in trans_counts:
        if row.date:
            date_str = row.date.isoformat() if hasattr(row.date, 'isoformat') else str(row.date)
            if date_str in heatmap:
                heatmap[date_str] += row.count * 3

    conv_counts = db.query(
        func.date(ConversationPractice.practiced_at).label('date'),
        func.count(ConversationPractice.id).label('count')
    ).filter(
        ConversationPractice.practiced_at >= start_date
    ).group_by(
        func.date(ConversationPractice.practiced_at)
    ).all()

    for row in conv_counts:
        if row.date:
            date_str = row.date.isoformat() if hasattr(row.date, 'isoformat') else str(row.date)
            if date_str in heatmap:
                heatmap[date_str] += row.count * 3

    # Convert to list format for frontend
    result = [{"date": k, "count": v} for k, v in sorted(heatmap.items())]

    # Calculate max for color intensity
    max_count = max(v for v in heatmap.values()) if heatmap else 1

    return {
        "success": True,
        "heatmap": result,
        "max_count": max_count,
        "total_days": len([v for v in heatmap.values() if v > 0])
    }


@router.get("/weekly")
def get_weekly_stats(db: Session = Depends(get_db)):
    """Get weekly learning statistics."""
    today = date.today()
    weeks = []

    for i in range(12):  # Last 12 weeks
        week_end = today - timedelta(days=i * 7)
        week_start = week_end - timedelta(days=6)

        # Words learned this week
        words = db.query(UserVocabulary).filter(
            func.date(UserVocabulary.learned_at) >= week_start,
            func.date(UserVocabulary.learned_at) <= week_end
        ).count()

        # Quizzes this week
        quizzes = db.query(Quiz).filter(
            func.date(Quiz.completed_at) >= week_start,
            func.date(Quiz.completed_at) <= week_end,
            Quiz.completed_at.isnot(None)
        ).all()

        quiz_count = len(quizzes)
        quiz_avg = sum(q.score for q in quizzes) / len(quizzes) if quizzes else 0

        # Practice sessions
        trans = db.query(TranslationPractice).filter(
            func.date(TranslationPractice.practiced_at) >= week_start,
            func.date(TranslationPractice.practiced_at) <= week_end
        ).count()

        conv = db.query(ConversationPractice).filter(
            func.date(ConversationPractice.practiced_at) >= week_start,
            func.date(ConversationPractice.practiced_at) <= week_end
        ).count()

        weeks.append({
            "week_start": week_start.isoformat(),
            "week_end": week_end.isoformat(),
            "words_learned": words,
            "quizzes": quiz_count,
            "quiz_avg": round(quiz_avg, 1),
            "translation_practices": trans,
            "conversation_practices": conv,
            "total_activities": words + quiz_count + trans + conv
        })

    weeks.reverse()  # Oldest first

    return {
        "success": True,
        "weeks": weeks
    }


@router.get("/monthly")
def get_monthly_stats(db: Session = Depends(get_db)):
    """Get monthly learning statistics."""
    today = date.today()
    months = []

    for i in range(6):  # Last 6 months
        # Calculate month start and end
        month_date = today - timedelta(days=i * 30)
        month_start = date(month_date.year, month_date.month, 1)

        if month_date.month == 12:
            month_end = date(month_date.year + 1, 1, 1) - timedelta(days=1)
        else:
            month_end = date(month_date.year, month_date.month + 1, 1) - timedelta(days=1)

        # Words learned this month
        words = db.query(UserVocabulary).filter(
            func.date(UserVocabulary.learned_at) >= month_start,
            func.date(UserVocabulary.learned_at) <= month_end
        ).count()

        # Quizzes
        quizzes = db.query(Quiz).filter(
            func.date(Quiz.completed_at) >= month_start,
            func.date(Quiz.completed_at) <= month_end,
            Quiz.completed_at.isnot(None)
        ).all()

        months.append({
            "month": month_start.strftime("%Y-%m"),
            "month_name": month_start.strftime("%B %Y"),
            "words_learned": words,
            "quizzes": len(quizzes),
            "quiz_avg": round(sum(q.score for q in quizzes) / len(quizzes), 1) if quizzes else 0
        })

    months.reverse()

    return {
        "success": True,
        "months": months
    }


@router.get("/streak")
def get_streak_info(db: Session = Depends(get_db)):
    """Get streak information."""
    today = date.today()

    # Get all activity dates
    activity_dates = set()

    # Vocabulary learned dates
    vocab_dates = db.query(func.date(UserVocabulary.learned_at)).distinct().all()
    for d in vocab_dates:
        if d[0]:
            activity_dates.add(d[0] if isinstance(d[0], date) else date.fromisoformat(str(d[0])))

    # Quiz dates
    quiz_dates = db.query(func.date(Quiz.completed_at)).filter(
        Quiz.completed_at.isnot(None)
    ).distinct().all()
    for d in quiz_dates:
        if d[0]:
            activity_dates.add(d[0] if isinstance(d[0], date) else date.fromisoformat(str(d[0])))

    # Practice dates
    trans_dates = db.query(func.date(TranslationPractice.practiced_at)).distinct().all()
    for d in trans_dates:
        if d[0]:
            activity_dates.add(d[0] if isinstance(d[0], date) else date.fromisoformat(str(d[0])))

    conv_dates = db.query(func.date(ConversationPractice.practiced_at)).distinct().all()
    for d in conv_dates:
        if d[0]:
            activity_dates.add(d[0] if isinstance(d[0], date) else date.fromisoformat(str(d[0])))

    # Calculate current streak
    current_streak = 0
    check_date = today

    while check_date in activity_dates:
        current_streak += 1
        check_date -= timedelta(days=1)

    # If today has no activity, check if yesterday had (streak still active)
    if current_streak == 0 and (today - timedelta(days=1)) in activity_dates:
        check_date = today - timedelta(days=1)
        while check_date in activity_dates:
            current_streak += 1
            check_date -= timedelta(days=1)

    # Calculate longest streak
    if not activity_dates:
        longest_streak = 0
    else:
        sorted_dates = sorted(activity_dates)
        longest_streak = 1
        current = 1

        for i in range(1, len(sorted_dates)):
            if (sorted_dates[i] - sorted_dates[i-1]).days == 1:
                current += 1
                longest_streak = max(longest_streak, current)
            else:
                current = 1

    return {
        "success": True,
        "current_streak": current_streak,
        "longest_streak": longest_streak,
        "total_active_days": len(activity_dates),
        "is_active_today": today in activity_dates
    }


@router.get("/summary")
def get_analytics_summary(db: Session = Depends(get_db)):
    """Get overall analytics summary."""
    # Total stats
    total_words = db.query(UserVocabulary).count()
    total_quizzes = db.query(Quiz).filter(Quiz.completed_at.isnot(None)).count()
    total_trans = db.query(TranslationPractice).count()
    total_conv = db.query(ConversationPractice).count()

    # This week stats
    week_ago = date.today() - timedelta(days=7)

    week_words = db.query(UserVocabulary).filter(
        func.date(UserVocabulary.learned_at) >= week_ago
    ).count()

    week_quizzes = db.query(Quiz).filter(
        func.date(Quiz.completed_at) >= week_ago,
        Quiz.completed_at.isnot(None)
    ).count()

    # Average quiz score
    all_quizzes = db.query(Quiz).filter(Quiz.completed_at.isnot(None)).all()
    avg_quiz = sum(q.score for q in all_quizzes) / len(all_quizzes) if all_quizzes else 0

    # Practice averages
    trans_all = db.query(TranslationPractice).all()
    trans_avg = sum(t.score for t in trans_all) / len(trans_all) if trans_all else 0

    conv_all = db.query(ConversationPractice).all()
    conv_avg = sum(c.score for c in conv_all) / len(conv_all) if conv_all else 0

    return {
        "success": True,
        "summary": {
            "total_words_learned": total_words,
            "total_quizzes": total_quizzes,
            "total_translation_practices": total_trans,
            "total_conversation_practices": total_conv,
            "week_words_learned": week_words,
            "week_quizzes": week_quizzes,
            "average_quiz_score": round(avg_quiz, 1),
            "average_translation_score": round(trans_avg, 1),
            "average_conversation_score": round(conv_avg, 1)
        }
    }
