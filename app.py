import streamlit as st
from config import DEFAULT_CONFIG, LANGUAGES, TONES, DIFFICULTIES, MODES, MODE_LABELS, MODE_DESCRIPTIONS
from chat_engine import get_ai_response

st.set_page_config(
    page_title="LinguaChat",
    page_icon="🌍",
    layout="wide",
)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "config" not in st.session_state:
    st.session_state.config = DEFAULT_CONFIG.copy()

# --- Sidebar ---
with st.sidebar:
    st.title("🌍 LinguaChat")
    st.markdown("Your AI Language Learning Buddy")
    st.divider()

    st.subheader("⚙️ Settings")

    target_lang = st.selectbox(
        "Target Language",
        LANGUAGES,
        index=LANGUAGES.index(st.session_state.config["target_language"]),
    )

    native_lang = st.selectbox(
        "Your Language",
        ["Indonesian", "English", "Japanese", "Korean"],
        index=0,
    )

    tone = st.select_slider(
        "Tone",
        options=TONES,
        value=st.session_state.config["tone"],
    )

    difficulty = st.select_slider(
        "Difficulty",
        options=DIFFICULTIES,
        value=st.session_state.config["difficulty"],
    )

    st.divider()
    st.subheader("🎯 Mode")

    selected_mode = st.radio(
        "Learning Mode",
        options=MODES,
        format_func=lambda x: MODE_LABELS[x],
        index=MODES.index(st.session_state.config["focus_mode"]),
    )

    st.caption(MODE_DESCRIPTIONS[selected_mode])

    # Update config
    st.session_state.config["target_language"] = target_lang
    st.session_state.config["native_language"] = native_lang
    st.session_state.config["tone"] = tone
    st.session_state.config["difficulty"] = difficulty
    st.session_state.config["focus_mode"] = selected_mode

    st.divider()

    if st.button("🗑️ Clear Chat History", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# --- Main Chat Area ---
st.title(f"{MODE_LABELS[selected_mode]} — {target_lang}")

# Display chat messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Chat input
if prompt := st.chat_input("Type your message here..."):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Get AI response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                response = get_ai_response(
                    st.session_state.config,
                    st.session_state.messages[:-1],  # history without current prompt
                    prompt,
                )
                st.markdown(response)
                st.session_state.messages.append({"role": "assistant", "content": response})
            except Exception as e:
                error_str = str(e)
                if "429" in error_str or "RESOURCE_EXHAUSTED" in error_str:
                    import re
                    retry_match = re.search(r"retry in ([\d.]+)s", error_str)
                    retry_msg = f" ⏳ Coba lagi dalam **{float(retry_match.group(1)):.0f} detik**." if retry_match else ""
                    error_msg = (
                        "⚠️ **Rate limit exceeded** — Gemini free tier quota habis."
                        f"{retry_msg}\n\n"
                        "Solusi:\n"
                        "1. Tunggu beberapa menit, lalu coba lagi\n"
                        "2. Atau upgrade ke paid tier di https://aistudio.google.com\n"
                        "3. Atau ganti ke model lain di `chat_engine.py` (kuota terpisah per model)"
                    )
                elif "API key" in error_str.lower() or "permission_denied" in error_str.lower():
                    error_msg = (
                        "⚠️ **Gemini API key not found!**\n\n"
                        "1. Copy `.env.example` to `.env`\n"
                        "2. Get free API key at https://aistudio.google.com/apikey\n"
                        "3. Add to .env: `GEMINI_API_KEY=your-api-key`\n"
                        "4. Restart the app"
                    )
                else:
                    error_msg = f"⚠️ Error: {error_str}"
                st.error(error_msg)
