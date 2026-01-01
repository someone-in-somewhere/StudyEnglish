"""
Chat Service - AI-powered conversational English practice.
Provides real-time grammar correction and adaptive responses.
"""

import logging
import uuid
from datetime import datetime
from typing import List, Dict, Optional, Any

from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.models.db_models import ChatHistory, UserSettings
from app.services.ai_model_manager import ai_manager

logger = logging.getLogger(__name__)


class ChatService:
    """Service for AI chatbot conversations with grammar correction."""

    def __init__(self, db: Session):
        """Initialize with database session."""
        self.db = db

    def send_message(
        self,
        message: str,
        session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process user message and generate response.

        Args:
            message: User's message
            session_id: Optional chat session ID

        Returns:
            Response with corrections if any
        """
        # Generate session ID if not provided
        if not session_id:
            session_id = str(uuid.uuid4())

        # Get user level for adaptive responses
        user_level = self._get_user_level()

        # Check grammar first
        grammar_result = ai_manager.correct_grammar(message)
        has_errors = grammar_result["has_errors"]
        corrections = grammar_result["corrections"]

        # Save user message
        user_msg = ChatHistory(
            session_id=session_id,
            role="user",
            message=message,
            has_errors=has_errors,
            corrections=corrections
        )
        self.db.add(user_msg)

        # Get conversation context
        context = self._get_conversation_context(session_id)

        # Generate response
        response_text = self._generate_response(
            message=message,
            context=context,
            level=user_level,
            has_errors=has_errors
        )

        # Save assistant response
        assistant_msg = ChatHistory(
            session_id=session_id,
            role="assistant",
            message=response_text,
            has_errors=False,
            corrections=None
        )
        self.db.add(assistant_msg)
        self.db.commit()

        return {
            "success": True,
            "session_id": session_id,
            "response": response_text,
            "has_errors": has_errors,
            "corrections": corrections
        }

    def _get_user_level(self) -> str:
        """Get user's target level from settings."""
        settings = self.db.query(UserSettings).first()
        return settings.target_level if settings else "B1"

    def _get_conversation_context(
        self,
        session_id: str,
        limit: int = 6
    ) -> List[Dict[str, str]]:
        """Get recent messages for context."""
        messages = (
            self.db.query(ChatHistory)
            .filter(ChatHistory.session_id == session_id)
            .order_by(desc(ChatHistory.timestamp))
            .limit(limit)
            .all()
        )

        # Reverse to get chronological order
        messages = list(reversed(messages))

        return [
            {"role": m.role, "content": m.message}
            for m in messages
        ]

    def _generate_response(
        self,
        message: str,
        context: List[Dict[str, str]],
        level: str,
        has_errors: bool
    ) -> str:
        """Generate AI response."""
        level_instructions = {
            "A1": "Use very simple vocabulary and short sentences. Speak slowly and clearly.",
            "A2": "Use simple vocabulary and basic sentence structures.",
            "B1": "Use clear, standard language appropriate for intermediate learners.",
            "B2": "Use more complex vocabulary and varied sentence structures.",
            "C1": "Use sophisticated vocabulary and complex grammar naturally.",
            "C2": "Speak naturally with idiomatic expressions and nuanced language."
        }

        instruction = level_instructions.get(level, level_instructions["B1"])

        # Build conversation history
        history = ""
        for msg in context[-4:]:  # Last 4 messages
            role = "User" if msg["role"] == "user" else "Assistant"
            history += f"{role}: {msg['content']}\n"

        error_note = ""
        if has_errors:
            error_note = "The user made some grammar mistakes. Gently acknowledge this if appropriate, but focus on continuing the conversation naturally."

        prompt = f"""You are a friendly English tutor having a conversation with a student at {level} level.

Instructions:
- {instruction}
- Be encouraging and supportive
- Keep responses concise (2-3 sentences)
- Ask follow-up questions to keep the conversation going
- {error_note}

Recent conversation:
{history}

User's latest message: {message}

Your response:"""

        try:
            response = ai_manager.generate_text(
                prompt,
                max_tokens=200,
                temperature=0.8
            )
            return response.strip()

        except Exception as e:
            logger.error(f"Response generation failed: {e}")
            # Fallback responses
            fallbacks = [
                "That's interesting! Can you tell me more about it?",
                "I see. What else would you like to discuss?",
                "Great! Let's continue practicing. What's on your mind?",
            ]
            import random
            return random.choice(fallbacks)

    def get_history(
        self,
        session_id: str,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Get chat history for a session.

        Args:
            session_id: Chat session ID
            limit: Maximum messages to return

        Returns:
            List of messages
        """
        messages = (
            self.db.query(ChatHistory)
            .filter(ChatHistory.session_id == session_id)
            .order_by(ChatHistory.timestamp.asc())
            .limit(limit)
            .all()
        )

        return [m.to_dict() for m in messages]

    def get_sessions(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get list of chat sessions."""
        # Get distinct session IDs with latest message
        from sqlalchemy import distinct

        sessions = (
            self.db.query(
                ChatHistory.session_id,
                func.max(ChatHistory.timestamp).label("last_message"),
                func.count(ChatHistory.id).label("message_count")
            )
            .group_by(ChatHistory.session_id)
            .order_by(desc("last_message"))
            .limit(limit)
            .all()
        )

        from sqlalchemy import func

        results = []
        for session in sessions:
            # Get first user message as preview
            first_msg = (
                self.db.query(ChatHistory.message)
                .filter(
                    ChatHistory.session_id == session.session_id,
                    ChatHistory.role == "user"
                )
                .first()
            )

            results.append({
                "session_id": session.session_id,
                "last_message": session.last_message.isoformat() if session.last_message else None,
                "message_count": session.message_count,
                "preview": first_msg.message[:50] + "..." if first_msg and len(first_msg.message) > 50 else (first_msg.message if first_msg else "")
            })

        return results

    def delete_session(self, session_id: str) -> bool:
        """Delete a chat session."""
        try:
            deleted = (
                self.db.query(ChatHistory)
                .filter(ChatHistory.session_id == session_id)
                .delete()
            )
            self.db.commit()
            return deleted > 0
        except Exception as e:
            logger.error(f"Failed to delete session: {e}")
            self.db.rollback()
            return False

    def get_error_summary(self, session_id: str) -> Dict[str, Any]:
        """Get summary of grammar errors in a session."""
        messages = (
            self.db.query(ChatHistory)
            .filter(
                ChatHistory.session_id == session_id,
                ChatHistory.has_errors == True
            )
            .all()
        )

        all_corrections = []
        for msg in messages:
            if msg.corrections:
                all_corrections.extend(msg.corrections)

        # Categorize errors
        error_types = {}
        for correction in all_corrections:
            error_type = correction.get("error_type", "grammar")
            if error_type not in error_types:
                error_types[error_type] = []
            error_types[error_type].append(correction)

        return {
            "session_id": session_id,
            "total_errors": len(all_corrections),
            "messages_with_errors": len(messages),
            "error_types": error_types,
            "corrections": all_corrections
        }

    def start_topic_conversation(
        self,
        topic: str,
        session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Start a conversation about a specific topic."""
        if not session_id:
            session_id = str(uuid.uuid4())

        user_level = self._get_user_level()

        prompt = f"""You are a friendly English tutor starting a conversation about "{topic}" with a {user_level} level student.

Start the conversation with:
1. A brief, engaging introduction to the topic
2. An easy question to get the student talking

Keep it simple and encouraging. 2-3 sentences maximum."""

        try:
            response = ai_manager.generate_text(prompt, max_tokens=150, temperature=0.8)
        except:
            response = f"Let's talk about {topic}! What do you know about this topic?"

        # Save as first message
        msg = ChatHistory(
            session_id=session_id,
            role="assistant",
            message=response.strip(),
            has_errors=False
        )
        self.db.add(msg)
        self.db.commit()

        return {
            "success": True,
            "session_id": session_id,
            "topic": topic,
            "response": response.strip()
        }


def get_chat_service(db: Session) -> ChatService:
    """Factory function to create ChatService."""
    return ChatService(db)
