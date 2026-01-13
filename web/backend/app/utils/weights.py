"""
Weighted scoring system for practice sessions.
Higher weights indicate more difficult options.
"""

# ============ Translation Practice Weights ============

TRANSLATION_LEVEL_WEIGHTS = {
    "A1": 0.70,   # Very basic vocabulary and grammar
    "A2": 0.85,   # Elementary level
    "B1": 1.00,   # Intermediate (baseline)
    "B2": 1.15,   # Upper-intermediate, complex structures
    "C1": 1.30,   # Advanced vocabulary, idioms, nuanced expressions
}

TRANSLATION_DIRECTION_WEIGHTS = {
    "en_to_vi": 0.90,   # Easier - translating to native language
    "vi_to_en": 1.10,   # Harder - producing English from Vietnamese
}

TRANSLATION_LENGTH_WEIGHTS = {
    "short": 0.90,    # 5-8 sentences, less pressure
    "medium": 1.00,   # 13-15 sentences (baseline)
    "long": 1.10,     # 17-25 sentences, requires sustained focus
}

TRANSLATION_COMPLEXITY_WEIGHTS = {
    "simple_short": 0.70,   # Simple sentences, 5-10 words
    "simple_medium": 0.80,  # Simple sentences, 10-15 words
    "simple_long": 0.85,    # Simple sentences, 15-25 words
    "compound": 1.00,       # Compound sentences with conjunctions (baseline)
    "complex": 1.15,        # Complex sentences with subordinate clauses
    "mixed": 1.10,          # Natural mix of all types
}


# ============ Conversation Practice Weights ============

CONVERSATION_LEVEL_WEIGHTS = {
    "A1": 0.70,
    "A2": 0.85,
    "B1": 1.00,
    "B2": 1.15,
    "C1": 1.30,
}

CONVERSATION_STYLE_WEIGHTS = {
    "casual": 0.85,     # Friendly, natural conversation - easiest
    "Casual": 0.85,
    "formal": 1.00,     # Professional, business setting (baseline)
    "Formal": 1.00,
    "roleplay": 1.05,   # Role-play scenarios, requires creativity
    "Role-play": 1.05,
    "interview": 1.15,  # Interview format, need precise answers
    "Interview": 1.15,
    "debate": 1.20,     # Debate/discussion, requires logical argumentation
    "Debate": 1.20,
}

CONVERSATION_LENGTH_WEIGHTS = {
    "short": 0.90,    # 5-8 exchanges
    "Short": 0.90,
    "medium": 1.00,   # 10-15 exchanges (baseline)
    "Medium": 1.00,
    "long": 1.10,     # 18-25 exchanges
    "Long": 1.10,
}


def calculate_translation_difficulty(level: str, direction: str, length: str, complexity: str) -> float:
    """
    Calculate difficulty factor for translation practice.
    Returns a multiplier where 1.0 is baseline (B1, vi_to_en, medium, compound).
    """
    level_w = TRANSLATION_LEVEL_WEIGHTS.get(level, 1.0)
    direction_w = TRANSLATION_DIRECTION_WEIGHTS.get(direction, 1.0)
    length_w = TRANSLATION_LENGTH_WEIGHTS.get(length, 1.0)
    complexity_w = TRANSLATION_COMPLEXITY_WEIGHTS.get(complexity, 1.0)

    return level_w * direction_w * length_w * complexity_w


def calculate_conversation_difficulty(level: str, style: str, length: str) -> float:
    """
    Calculate difficulty factor for conversation practice.
    Returns a multiplier where 1.0 is baseline (B1, formal, medium).
    """
    level_w = CONVERSATION_LEVEL_WEIGHTS.get(level, 1.0)
    style_w = CONVERSATION_STYLE_WEIGHTS.get(style, 1.0)
    length_w = CONVERSATION_LENGTH_WEIGHTS.get(length, 1.0)

    return level_w * style_w * length_w


def calculate_weighted_score(raw_score: float, difficulty_factor: float) -> float:
    """
    Calculate weighted score based on difficulty.

    Formula: weighted_score = raw_score * (1 + (difficulty_factor - 1) * 0.5)

    This formula:
    - At difficulty 1.0 (baseline): weighted = raw
    - At difficulty 1.5: weighted = raw * 1.25 (25% bonus)
    - At difficulty 0.5: weighted = raw * 0.75 (25% penalty)

    The 0.5 coefficient prevents extreme swings while still rewarding difficulty.
    """
    adjustment = 1 + (difficulty_factor - 1) * 0.5
    weighted = raw_score * adjustment

    # Cap at 10 to maintain scoring range
    return min(10.0, round(weighted, 2))


def get_difficulty_label(difficulty_factor: float) -> str:
    """Get human-readable difficulty label."""
    if difficulty_factor < 0.75:
        return "Rất dễ"
    elif difficulty_factor < 0.95:
        return "Dễ"
    elif difficulty_factor <= 1.05:
        return "Trung bình"
    elif difficulty_factor <= 1.25:
        return "Khó"
    else:
        return "Rất khó"
