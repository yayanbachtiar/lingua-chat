import os
from dotenv import load_dotenv

load_dotenv()

_client = None
_types = None


def _get_client():
    global _client, _types
    if _client is None:
        from google import genai as _genai
        from google.genai import types as _genai_types
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError(
                "GEMINI_API_KEY not found! "
                "Get a free key at https://aistudio.google.com/apikey "
                "and add it to your .env file."
            )
        _client = _genai.Client(api_key=api_key)
        _types = _genai_types
    return _client, _types


def build_system_prompt(config: dict) -> str:
    mode = config["focus_mode"]
    target = config["target_language"]
    native = config["native_language"]
    tone = config["tone"]
    difficulty = config["difficulty"]

    mode_instructions = {
        "conversation": (
            f"Respond naturally in {target}. "
            f"If the user makes a mistake in {target}, gently correct them "
            f"by restating the correct version naturally in your response."
        ),
        "grammar": (
            "Analyze the user's sentence for grammar errors. "
            "For each error found:\n"
            "1. Point out what was wrong\n"
            "2. Explain the grammar rule\n"
            "3. Show the corrected sentence\n"
            "If there are no errors, praise the user and suggest a small improvement."
        ),
        "vocab": (
            "When the user asks about a word or phrase, provide:\n"
            "1. Definition in {native}\n"
            "2. Example sentence in {target}\n"
            "3. Synonyms or related words\n"
            "4. Common usage notes"
        ),
        "quiz": (
            f"Generate a quiz question appropriate for {difficulty} level.\n"
            "Types: translate this sentence, fill-in-the-blank, multiple choice.\n"
            "After the user answers, tell them if they're correct and explain why.\n"
            "Then generate a new question."
        ),
        "helpbox": (
            f"You are a helpful assistant embedded on a website as a live chat widget.\n"
            "Respond conversationally and concisely (1-2 paragraphs max).\n"
            "Help users with their questions in a friendly, professional tone.\n"
            f"Primary language: {target}."
        ),
    }

    instruction = mode_instructions.get(mode, mode_instructions["conversation"])

    return (
        f"You are a {target} teacher. Your student's native language is {native}.\n\n"
        f"Tone: {tone} — keep your responses {tone} and encouraging.\n"
        f"Difficulty: {difficulty} — use {difficulty}-level vocabulary and grammar.\n"
        f"Mode: {mode}\n\n"
        f"{instruction}\n\n"
        f"Keep responses concise (max 3 paragraphs). Focus on teaching, not just answering."
    )


def get_ai_response(config: dict, messages: list, user_input: str) -> str:
    client, types = _get_client()
    system_prompt = build_system_prompt(config)

    # Build conversation contents with history
    contents = []
    max_history = config.get("max_history", 10)
    if config.get("memory_enabled", True) and messages:
        for msg in messages[-max_history:]:
            role = "user" if msg["role"] == "user" else "model"
            contents.append(types.Content(
                role=role,
                parts=[types.Part(text=msg["content"])]
            ))

    # Add current user message
    contents.append(types.Content(
        role="user",
        parts=[types.Part(text=user_input)]
    ))

    response = client.models.generate_content(
        model="gemini-3.5-flash",
        contents=contents,
        config=types.GenerateContentConfig(
            system_instruction=system_prompt,
            temperature=0.7,
            max_output_tokens=1024,
        ),
    )

    return response.text or "I'm sorry, I couldn't generate a response. Please try again."
