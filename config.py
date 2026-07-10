DEFAULT_CONFIG = {
    "target_language": "English",
    "native_language": "Indonesian",
    "tone": "casual",
    "difficulty": "beginner",
    "focus_mode": "conversation",
    "memory_enabled": True,
    "max_history": 10,
}

LANGUAGES = ["English", "Japanese", "Korean", "Mandarin", "French", "Spanish"]
TONES = ["formal", "casual", "friendly"]
DIFFICULTIES = ["beginner", "intermediate", "advanced"]
MODES = ["conversation", "grammar", "vocab", "quiz", "helpbox"]

MODE_LABELS = {
    "conversation": "💬 Conversation",
    "grammar": "📝 Grammar Check",
    "vocab": "📚 Vocabulary",
    "quiz": "🎯 Quiz",
    "helpbox": "💬 HelpBox",
}

MODE_DESCRIPTIONS = {
    "conversation": "Chat naturally in your target language with an AI native speaker.",
    "grammar": "Write a sentence and get grammar corrections with explanations.",
    "vocab": "Ask about any word — get definition, examples, synonyms.",
    "quiz": "Test your knowledge with AI-generated quiz questions.",
    "helpbox": "Embeddable popup chat widget — assist users on any platform.",
}
