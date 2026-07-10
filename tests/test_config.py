"""Unit tests for config.py — all constants and defaults."""

import sys
from pathlib import Path

# Ensure project root is on sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import config


class TestDefaultConfig:
    def test_has_default_config(self):
        assert isinstance(config.DEFAULT_CONFIG, dict)
        assert "target_language" in config.DEFAULT_CONFIG
        assert "native_language" in config.DEFAULT_CONFIG
        assert "tone" in config.DEFAULT_CONFIG
        assert "difficulty" in config.DEFAULT_CONFIG
        assert "focus_mode" in config.DEFAULT_CONFIG
        assert "memory_enabled" in config.DEFAULT_CONFIG
        assert "max_history" in config.DEFAULT_CONFIG

    def test_default_values(self):
        cfg = config.DEFAULT_CONFIG
        assert cfg["target_language"] == "English"
        assert cfg["native_language"] == "Indonesian"
        assert cfg["tone"] == "casual"
        assert cfg["difficulty"] == "beginner"
        assert cfg["focus_mode"] == "conversation"
        assert cfg["memory_enabled"] is True
        assert cfg["max_history"] == 10


class TestLanguages:
    def test_languages_list(self):
        assert isinstance(config.LANGUAGES, list)
        assert len(config.LANGUAGES) > 0
        assert "English" in config.LANGUAGES
        assert "Japanese" in config.LANGUAGES
        assert "Indonesian" not in config.LANGUAGES  # it's a target language list


class TestTones:
    def test_tones_list(self):
        assert "formal" in config.TONES
        assert "casual" in config.TONES
        assert "friendly" in config.TONES


class TestDifficulties:
    def test_difficulties_list(self):
        assert "beginner" in config.DIFFICULTIES
        assert "intermediate" in config.DIFFICULTIES
        assert "advanced" in config.DIFFICULTIES


class TestModes:
    def test_modes_include_helpbox(self):
        assert "conversation" in config.MODES
        assert "grammar" in config.MODES
        assert "vocab" in config.MODES
        assert "quiz" in config.MODES
        assert "helpbox" in config.MODES

    def test_modes_count(self):
        assert len(config.MODES) == 5

    def test_all_modes_have_labels(self):
        for mode in config.MODES:
            assert mode in config.MODE_LABELS, f"Missing label for mode: {mode}"
            assert isinstance(config.MODE_LABELS[mode], str)
            assert len(config.MODE_LABELS[mode]) > 0

    def test_all_modes_have_descriptions(self):
        for mode in config.MODES:
            assert mode in config.MODE_DESCRIPTIONS, f"Missing description for mode: {mode}"
            assert isinstance(config.MODE_DESCRIPTIONS[mode], str)
            assert len(config.MODE_DESCRIPTIONS[mode]) > 0
