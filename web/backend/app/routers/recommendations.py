"""
Smart Recommendations router - suggests learning based on error patterns and weak areas.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from datetime import datetime, timedelta

from app.database import get_sync_session
from app.models.db_models import (
    ErrorPattern, QuizError, UserVocabulary, Vocabulary,
    TranslationPractice, ConversationPractice, Quiz
)

router = APIRouter(prefix="/api/recommendations", tags=["recommendations"])


@router.get("")
def get_recommendations(db: Session = Depends(get_sync_session)):
    """Get personalized learning recommendations."""
    recommendations = []

    # 1. Check error patterns - what errors do users make most?
    error_patterns = db.query(ErrorPattern)\
        .order_by(desc(ErrorPattern.count))\
        .limit(5)\
        .all()

    if error_patterns:
        for pattern in error_patterns[:3]:
            recommendations.append({
                "type": "error_focus",
                "priority": "high",
                "title": f"Focus on {pattern.error_category}",
                "description": f"You've made {pattern.count} mistakes with {pattern.error_type} ({pattern.error_category}). Practice more!",
                "action": "quiz",
                "icon": "fas fa-exclamation-triangle",
                "color": "red"
            })

    # 2. Check weak vocabulary (low mastery, many incorrect answers)
    weak_words = db.query(UserVocabulary, Vocabulary)\
        .join(Vocabulary, UserVocabulary.vocabulary_id == Vocabulary.id)\
        .filter(UserVocabulary.mastery_level <= 2)\
        .filter(UserVocabulary.times_incorrect > UserVocabulary.times_correct)\
        .order_by(UserVocabulary.times_incorrect.desc())\
        .limit(10)\
        .all()

    if weak_words:
        weak_topics = {}
        for uv, vocab in weak_words:
            topic = vocab.topic or "General"
            if topic not in weak_topics:
                weak_topics[topic] = 0
            weak_topics[topic] += 1

        for topic, count in list(weak_topics.items())[:2]:
            recommendations.append({
                "type": "weak_vocabulary",
                "priority": "high",
                "title": f"Review {topic} vocabulary",
                "description": f"You have {count} words with low mastery in this topic. Consider using flashcards.",
                "action": "flashcards",
                "topic": topic,
                "icon": "fas fa-book",
                "color": "orange"
            })

    # 3. Check due SRS reviews
    due_count = db.query(UserVocabulary)\
        .filter(UserVocabulary.next_review <= datetime.now())\
        .count()

    if due_count > 0:
        recommendations.append({
            "type": "srs_due",
            "priority": "high" if due_count > 10 else "medium",
            "title": f"{due_count} words due for review",
            "description": "Don't break your streak! Review these words now to maintain memory.",
            "action": "srs",
            "count": due_count,
            "icon": "fas fa-redo",
            "color": "blue"
        })

    # 4. Check practice score trends
    week_ago = datetime.now() - timedelta(days=7)

    trans_practices = db.query(TranslationPractice)\
        .filter(TranslationPractice.practiced_at >= week_ago)\
        .all()

    if trans_practices:
        avg_score = sum(p.score for p in trans_practices) / len(trans_practices)
        if avg_score < 7:
            recommendations.append({
                "type": "practice_improvement",
                "priority": "medium",
                "title": "Improve Translation Skills",
                "description": f"Your average translation score is {avg_score:.1f}/10. Try practicing at a lower difficulty level.",
                "action": "translation",
                "icon": "fas fa-language",
                "color": "purple"
            })

    conv_practices = db.query(ConversationPractice)\
        .filter(ConversationPractice.practiced_at >= week_ago)\
        .all()

    if conv_practices:
        avg_score = sum(p.score for p in conv_practices) / len(conv_practices)
        if avg_score < 7:
            recommendations.append({
                "type": "practice_improvement",
                "priority": "medium",
                "title": "Improve Conversation Skills",
                "description": f"Your average conversation score is {avg_score:.1f}/10. Practice more casual conversations.",
                "action": "conversation",
                "icon": "fas fa-comments",
                "color": "indigo"
            })

    # 5. Suggest new learning if user is doing well
    recent_quizzes = db.query(Quiz)\
        .filter(Quiz.completed_at >= week_ago)\
        .all()

    if recent_quizzes:
        avg_quiz_score = sum(q.score for q in recent_quizzes) / len(recent_quizzes)
        if avg_quiz_score >= 80:
            # User is doing well, suggest advancing
            recommendations.append({
                "type": "level_up",
                "priority": "low",
                "title": "Ready to advance!",
                "description": f"Great job! Your quiz average is {avg_quiz_score:.0f}%. Consider learning harder vocabulary.",
                "action": "vocabulary",
                "icon": "fas fa-arrow-up",
                "color": "green"
            })

    # 6. Check if user hasn't practiced recently
    if not trans_practices and not conv_practices:
        recommendations.append({
            "type": "practice_reminder",
            "priority": "medium",
            "title": "Start practicing!",
            "description": "You haven't practiced translation or conversation this week. Try a session now!",
            "action": "translation",
            "icon": "fas fa-play",
            "color": "teal"
        })

    # 7. Suggest specific topics based on quiz errors
    quiz_errors = db.query(QuizError.vocabulary_id, func.count(QuizError.id).label('error_count'))\
        .filter(QuizError.vocabulary_id.isnot(None))\
        .group_by(QuizError.vocabulary_id)\
        .order_by(desc('error_count'))\
        .limit(5)\
        .all()

    if quiz_errors:
        vocab_ids = [e[0] for e in quiz_errors]
        problem_vocab = db.query(Vocabulary)\
            .filter(Vocabulary.id.in_(vocab_ids))\
            .all()

        if problem_vocab:
            problem_topics = list(set(v.topic for v in problem_vocab if v.topic))[:2]
            for topic in problem_topics:
                if not any(r.get("topic") == topic for r in recommendations):
                    recommendations.append({
                        "type": "quiz_errors",
                        "priority": "medium",
                        "title": f"Review {topic}",
                        "description": "You've made multiple quiz errors with words from this topic.",
                        "action": "flashcards",
                        "topic": topic,
                        "icon": "fas fa-clipboard-check",
                        "color": "yellow"
                    })

    # Sort by priority
    priority_order = {"high": 0, "medium": 1, "low": 2}
    recommendations.sort(key=lambda x: priority_order.get(x.get("priority", "low"), 3))

    return {
        "success": True,
        "recommendations": recommendations[:6],  # Return top 6
        "total": len(recommendations)
    }


@router.get("/weak-words")
def get_weak_words(limit: int = 10, db: Session = Depends(get_sync_session)):
    """Get words that need more practice."""
    weak_words = db.query(UserVocabulary, Vocabulary)\
        .join(Vocabulary, UserVocabulary.vocabulary_id == Vocabulary.id)\
        .filter(UserVocabulary.mastery_level <= 2)\
        .order_by(
            UserVocabulary.mastery_level.asc(),
            (UserVocabulary.times_incorrect - UserVocabulary.times_correct).desc()
        )\
        .limit(limit)\
        .all()

    words = []
    for uv, vocab in weak_words:
        word_dict = vocab.to_dict()
        word_dict["mastery_level"] = uv.mastery_level
        word_dict["times_correct"] = uv.times_correct
        word_dict["times_incorrect"] = uv.times_incorrect
        word_dict["accuracy"] = round(uv.times_correct / max(1, uv.times_correct + uv.times_incorrect) * 100)
        words.append(word_dict)

    return {
        "success": True,
        "words": words,
        "count": len(words)
    }


@router.get("/study-suggestions")
def get_study_suggestions(db: Session = Depends(get_sync_session)):
    """Get suggestions for today's study session."""
    suggestions = []

    # Check what's due
    due_count = db.query(UserVocabulary)\
        .filter(UserVocabulary.next_review <= datetime.now())\
        .count()

    if due_count > 0:
        suggestions.append({
            "activity": "SRS Review",
            "duration": f"{min(due_count * 2, 30)} minutes",
            "description": f"Review {due_count} words due today",
            "priority": 1,
            "icon": "fas fa-redo"
        })

    # Check weak words for flashcards
    weak_count = db.query(UserVocabulary)\
        .filter(UserVocabulary.mastery_level <= 2)\
        .count()

    if weak_count > 5:
        suggestions.append({
            "activity": "Flashcard Practice",
            "duration": "15 minutes",
            "description": f"Practice {min(weak_count, 20)} weak words",
            "priority": 2,
            "icon": "fas fa-clone"
        })

    # Suggest quiz
    total_learned = db.query(UserVocabulary).count()
    if total_learned >= 10:
        suggestions.append({
            "activity": "Vocabulary Quiz",
            "duration": "10 minutes",
            "description": "Test your knowledge with a quiz",
            "priority": 3,
            "icon": "fas fa-question-circle"
        })

    # Suggest practice
    suggestions.append({
        "activity": "Translation Practice",
        "duration": "20 minutes",
        "description": "Practice translating passages",
        "priority": 4,
        "icon": "fas fa-language"
    })

    suggestions.append({
        "activity": "Conversation Practice",
        "duration": "15 minutes",
        "description": "Practice English conversation",
        "priority": 5,
        "icon": "fas fa-comments"
    })

    return {
        "success": True,
        "suggestions": suggestions[:5]
    }
