# AI Escape Room — The Locked Library

The Locked Library is a text-based escape room built with Python, Streamlit, and Google Gemini. You wake up in a locked library and use chat messages to examine objects, collect items, solve puzzles, and unlock the exit.

## Problem

An AI Game Master can make a text adventure feel natural, but it can also forget what the player has collected, invent objects, or open the exit before the player completes the puzzles. The game needs a consistent way to track progress and enforce its rules.

## Solution

The project implements the same escape room in two versions.

| Feature | Version 1 — Interactive | Version 2 — Reliable |
|---|---|---|
| Entry point | `app.py` | `app_v2.py` |
| Game rules | Included in Gemini's prompt | Defined and checked by Python |
| Game progress | Tracked through the conversation | Stored as structured state, including inventory, solved puzzles, and lock status |
| Narration | Gemini generates the Game Master's reply | Gemini selects from descriptions approved by the game engine |
| Invalid actions | Gemini decides how to respond | Python rejects the action and preserves progress |

Version 1 shows how an LLM can run a conversational game. Version 2 gives Python control over the outcome of each action. If Gemini is unavailable in Version 2, the app displays the approved local description so the player can continue.

## Technologies

- **Python** for the application, game rules, and tests
- **Streamlit** for the browser-based chat interface and session state
- **Google Gemini API** via `google-genai` for the Game Master and narration
- **python-dotenv** for loading the local `.env` configuration
- **unittest** for checking the Version 2 game rules

## Installation on Windows

You need Python installed, a copy of this repository, and a Gemini API key.

1. Open the repository folder in VS Code.
2. Select **Terminal → New Terminal** and use PowerShell.
3. From the repository root, create a virtual environment and install the dependencies:

   ```powershell
   py -m venv .venv
   .\.venv\Scripts\python.exe -m pip install -r requirements.txt
   ```

4. If you do not already have a `.env` file, create one from the template:

   ```powershell
   Copy-Item .env.example .env
   ```

5. Open `.env` and replace the placeholders with your API key and a model ID available to your account:

   ```dotenv
   GEMINI_API_KEY=your_api_key_here
   GEMINI_MODEL=your_model_id_here
   ```

   You can obtain a key from [Google AI Studio](https://aistudio.google.com/apikey). Once your key is configured, you can list available models with:

   ```powershell
   .\.venv\Scripts\python.exe check_models.py
   ```

   For this assignment, choose a model with free-tier access and available quota. Keep `.env` private. Commit `.env.example` with placeholders.

## Run the application

Start either version from the repository root.

**Version 1**

```powershell
.\.venv\Scripts\python.exe -m streamlit run app.py
```

**Version 2**

```powershell
.\.venv\Scripts\python.exe -m streamlit run app_v2.py
```

Open the local URL printed in the terminal, usually `http://localhost:8501`. Press **Ctrl+C** in the terminal to stop the running version before starting the other one.

## How to play

Start by typing `examine desk`. Explore the desk, bookshelf, drawer, painting, and exit door. Use the clues to open the drawer, collect the key, and work out the final door code.

In Version 2, enter one action per message. Try `examine bookshelf`, `inventory`, `hint`, or `take key`. If an action is rejected, try a shorter command with the object name. Use **Restart game** to reset the room and start over.

## Testing

Run the Version 2 engine tests:

```powershell
.\.venv\Scripts\python.exe -m unittest -v test_game_engine
```

The tests cover invalid codes, using a key before collecting it, unsupported objects, attempts to skip prerequisites, and a complete escape sequence. To check the interface and Gemini connection, launch both versions and try the cases in the [manual comparison guide](docs/TEST_CASES.md). In Version 2, the **Gemini selected the narration** message confirms a successful narration call.

## Project files

| File | Purpose |
|---|---|
| `app.py` | Version 1 Streamlit interface and Gemini calls |
| `game_prompt.py` | Version 1 room description and Game Master instructions |
| `app_v2.py` | Version 2 Streamlit interface and narration |
| `game_engine.py` | Version 2 state, action validation, and puzzle rules |
| `test_game_engine.py` | Automated tests for the Version 2 engine |
| `check_models.py` | Lists models available to the configured Gemini account |
| `requirements.txt` | Python dependencies |
| `.env.example` | Environment variable template |

