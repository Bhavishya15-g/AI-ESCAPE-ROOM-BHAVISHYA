import json
import os
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv
from google import genai
from google.genai import types

from game_engine import apply_action, new_game


load_dotenv(Path(__file__).with_name(".env"), override=True)

st.set_page_config(
    page_title="Reliable Library Escape Room",
    page_icon="🔐",
)

INTRO = (
    "You wake up inside a locked library. "
    "There is a desk, bookshelf, locked drawer, painting, "
    "and exit door. Explore the room and escape. "
    "Start with: examine desk."
)

api_key = os.getenv("GEMINI_API_KEY", "").strip()
model_name = os.getenv("GEMINI_MODEL", "").strip()


def narrate(outcome):
    """
    Gemini chooses an approved description.

    Raw player instructions, secret codes, and the full game state
    are not sent to Gemini. Its output cannot modify game state.
    """
    choices = [
        outcome,
        "You pause and look carefully. " + outcome,
        "In the quiet library, you continue your investigation. " + outcome,
    ]

    if not api_key or not model_name:
        return outcome, "Local narration: API configuration is missing."

    try:
        with genai.Client(api_key=api_key) as client:
            response = client.models.generate_content(
                model=model_name,
                contents=json.dumps(
                    {
                        "task": (
                            "Select the most natural narration for this "
                            "escape-room event. Return only a JSON object "
                            "with choice set to 0, 1, or 2."
                        ),
                        "choices": choices,
                    }
                ),
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                ),
            )

        selection = json.loads(response.text or "")
        index = selection.get("choice")

        if type(index) is not int or index not in range(len(choices)):
            raise ValueError("Invalid narration choice")

        return choices[index], "Gemini selected the narration."

    except Exception:
        return outcome, (
            "Gemini narration was unavailable. "
            "The approved local description was used."
        )


if "v2_state" not in st.session_state:
    st.session_state.v2_state = new_game()

if "v2_messages" not in st.session_state:
    st.session_state.v2_messages = [
        {"role": "assistant", "content": INTRO}
    ]

if "v2_narration_status" not in st.session_state:
    st.session_state.v2_narration_status = ""


st.title("🔐 Reliable Library Escape Room")
st.caption("Version 2 — Python validates every action.")

with st.sidebar:
    st.header("How to play")

    st.markdown(
        "- Examine the desk\n"
        "- Examine the bookshelf\n"
        "- Open drawer with CODE\n"
        "- Take key\n"
        "- Examine painting\n"
        "- Use key on painting\n"
        "- Enter CODE into the door\n"
        "- Inventory\n"
        "- Hint"
    )

    st.subheader("Inventory")
    inventory = st.session_state.v2_state["inventory"]
    st.write(", ".join(inventory) if inventory else "Empty")

    solved = st.session_state.v2_state["solved_puzzles"]
    st.write(f"Puzzles completed: {len(solved)} / 3")

    if st.button("Restart game"):
        st.session_state.v2_state = new_game()
        st.session_state.v2_messages = [
            {"role": "assistant", "content": INTRO}
        ]
        st.session_state.v2_narration_status = ""
        st.rerun()


for message in st.session_state.v2_messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if st.session_state.v2_narration_status:
    st.caption(st.session_state.v2_narration_status)

if st.session_state.v2_state["escaped"]:
    st.success("You escaped! Restart to play again.")


player_text = st.chat_input(
    "Enter one action at a time...",
    disabled=st.session_state.v2_state["escaped"],
)

if player_text:
    # Python decides the outcome before Gemini is contacted.
    next_state, approved_outcome = apply_action(
        st.session_state.v2_state,
        player_text,
    )

    with st.spinner("Preparing the Game Master's response..."):
        narration, status = narrate(approved_outcome)

    st.session_state.v2_state = next_state

    st.session_state.v2_messages.extend(
        [
            {"role": "user", "content": player_text},
            {"role": "assistant", "content": narration},
        ]
    )

    st.session_state.v2_narration_status = status
    st.rerun()