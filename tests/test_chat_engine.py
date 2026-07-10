"""Unit tests for chat_engine.py — prompt builder with mocked API."""

import sys
from pathlib import Path
from unittest.mock import patch, MagicMock
import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Must patch dotenv before importing chat_engine
with patch("chat_engine.load_dotenv"):
    import chat_engine


SAMPLE_CONFIG = {
    "target_language": "Japanese",
    "native_language": "Indonesian",
    "tone": "casual",
    "difficulty": "beginner",
    "focus_mode": "conversation",
    "memory_enabled": True,
    "max_history": 10,
}


class TestBuildSystemPrompt:
    def test_conversation_mode(self):
        prompt = chat_engine.build_system_prompt({**SAMPLE_CONFIG, "focus_mode": "conversation"})
        assert "Japanese" in prompt
        assert "Indonesian" in prompt
        assert "casual" in prompt
        assert "beginner" in prompt
        assert "teacher" in prompt

    def test_grammar_mode(self):
        prompt = chat_engine.build_system_prompt({**SAMPLE_CONFIG, "focus_mode": "grammar"})
        assert "grammar errors" in prompt.lower() or "grammar" in prompt.lower()

    def test_vocab_mode(self):
        prompt = chat_engine.build_system_prompt({**SAMPLE_CONFIG, "focus_mode": "vocab"})
        assert "Definition" in prompt
        assert "Example" in prompt
        assert "Synonyms" in prompt

    def test_quiz_mode(self):
        prompt = chat_engine.build_system_prompt({**SAMPLE_CONFIG, "focus_mode": "quiz"})
        assert "quiz" in prompt.lower()
        assert "multiple choice" in prompt.lower()

    def test_helpbox_mode(self):
        prompt = chat_engine.build_system_prompt({**SAMPLE_CONFIG, "focus_mode": "helpbox"})
        assert "chat widget" in prompt.lower()
        assert "concisely" in prompt.lower()

    def test_all_modes_produce_string(self):
        for mode in ["conversation", "grammar", "vocab", "quiz", "helpbox"]:
            prompt = chat_engine.build_system_prompt({**SAMPLE_CONFIG, "focus_mode": mode})
            assert isinstance(prompt, str)
            assert len(prompt) > 50

    def test_tone_affects_output(self):
        formal = chat_engine.build_system_prompt({**SAMPLE_CONFIG, "tone": "formal"})
        casual = chat_engine.build_system_prompt({**SAMPLE_CONFIG, "tone": "casual"})
        assert "formal" in formal
        assert "casual" in casual

    def test_difficulty_affects_output(self):
        beginner = chat_engine.build_system_prompt({**SAMPLE_CONFIG, "difficulty": "beginner"})
        advanced = chat_engine.build_system_prompt({**SAMPLE_CONFIG, "difficulty": "advanced"})
        assert "beginner" in beginner
        assert "advanced" in advanced


class TestGetAiResponse:
    def test_successful_response(self):
        """get_ai_response returns text when Gemini responds."""

        mock_response = MagicMock()
        mock_response.text = "Konnichiwa! How can I help you today?"

        mock_client = MagicMock()
        mock_client.models.generate_content.return_value = mock_response

        mock_types = MagicMock()
        mock_types.Content = MagicMock()
        mock_types.Part = MagicMock()
        mock_types.GenerateContentConfig = MagicMock()

        with (
            patch.object(chat_engine, "_client", mock_client),
            patch.object(chat_engine, "_types", mock_types),
        ):
            result = chat_engine.get_ai_response(
                SAMPLE_CONFIG,
                [{"role": "user", "content": "Hello"}],
                "How are you?",
            )

        assert result == "Konnichiwa! How can I help you today?"

    def test_response_none_fallback(self):
        """When Gemini returns None text, fallback message is used."""

        mock_response = MagicMock()
        mock_response.text = None

        mock_client = MagicMock()
        mock_client.models.generate_content.return_value = mock_response

        mock_types = MagicMock()
        mock_types.Content = MagicMock()
        mock_types.Part = MagicMock()
        mock_types.GenerateContentConfig = MagicMock()

        with (
            patch.object(chat_engine, "_client", mock_client),
            patch.object(chat_engine, "_types", mock_types),
        ):
            result = chat_engine.get_ai_response(
                SAMPLE_CONFIG,
                [],
                "Hello",
            )

        assert "couldn't generate" in result.lower() or "sorry" in result.lower()

    @patch("chat_engine.os.getenv", return_value=None)
    def test_missing_api_key_raises(self, mock_getenv):
        """Calling _get_client without API key raises ValueError."""
        with pytest.raises(ValueError, match="GEMINI_API_KEY"):
            chat_engine._get_client()
