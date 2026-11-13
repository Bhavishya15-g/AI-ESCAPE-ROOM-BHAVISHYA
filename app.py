import json
import os
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv
from google import genai
from google.genai import types

from game_prompt import INTRODUCTION, SYSTEM_PROMPT


# Read configuration from the .env beside this file.
load_dotenv(Path(__file__).with_name(".env"), override=True)

st.set_page_config(
    page_title="Library Escape Room",
    page_icon="🔐",
)

st.title("🔐 Library Escape Room")
st.caption("Version 1 — Gemini is your Game Master.")

api_key = os.getenv("GEMINI_API_KEY", "").strip()
model_name = os.getenv("GEMINI_MODEL", "").strip()

if not api_key or api_key == "PASTE_YOUR_REAL_KEY_HERE":
    st.error("Add your Gemini API key to .env, then restart the app.")
    st.stop()

if not model_name:
    st.error("Set GEMINI_MODEL in .env, then restart the app.")
    st.stop()


# Streamlit remembers these values between chat messages.
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": INTRODUCTION}
    ]

if "escaped" not in st.session_state:
    st.session_state.escaped = False


with st.sidebar:
    st.header("How to play")
    st.write(
        "Explore the five objects, collect useful items, "
        "solve the puzzles, and unlock the exit."
    )
    st.markdown(
        "- Examine the desk\n"
        "- Inspect the bookshelf\n"
        "- Collect an item\n"
        "- Use an item\n"
        "- Check my inventory\n"
        "- Give me a hint"
    )

    if st.button("Restart game"):
        st.session_state.messages = [
            {"role": "assistant", "content": INTRODUCTION}
        ]
        st.session_state.escaped = False
        st.rerun()


# Display the conversation already saved.
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if st.session_state.escaped:
    st.success("You escaped! Use Restart game to play again.")


player_action = st.chat_input(
    "What would you like to do?",
    disabled=st.session_state.escaped,
)

if player_action:
    with st.chat_message("user"):
        st.markdown(player_action)

    # Build a candidate conversation. Save it only if the API succeeds.
    candidate_messages = st.session_state.messages + [
        {"role": "user", "content": player_action}
    ]

    contents = [
        types.Content(
            role="user" if message["role"] == "user" else "model",
            parts=[types.Part(text=message["content"])],
        )
        for message in candidate_messages
    ]

    try:
        with st.spinner("The Game Master is thinking..."):
            with genai.Client(api_key=api_key) as client:
                response = client.models.generate_content(
                    model=model_name,
                    contents=contents,
                    config=types.GenerateContentConfig(
                        system_instruction=SYSTEM_PROMPT,
                        response_mime_type="application/json",
                    ),
                )

            result = json.loads(response.text or "")

            if (
                not isinstance(result, dict)
                or not isinstance(result.get("message"), str)
                or not result["message"].strip()
                or not isinstance(result.get("escaped"), bool)
            ):
                raise ValueError("Unexpected game response")

        st.session_state.messages = candidate_messages + [
            {"role": "assistant", "content": result["message"]}
        ]
        st.session_state.escaped = result["escaped"]
        st.rerun()

    except (json.JSONDecodeError, ValueError):
        st.error(
            "The AI returned an unexpected response. "
            "Your progress was kept. Please enter your action again."
        )

    except Exception as error:
        code = str(getattr(error, "code", ""))

        if code in {"401", "403"}:
            st.error("Authentication failed. Check your API key and access.")
        elif code == "404":
            st.error("Model unavailable. Check GEMINI_MODEL in .env.")
        elif code == "429":
            st.error(
                "Rate limit or quota reached. Check AI Studio usage "
                "and retry when quota is available."
            )
        else:
            st.error(
                "Could not contact Gemini. Check your connection "
                "and API configuration, then try again."
            )