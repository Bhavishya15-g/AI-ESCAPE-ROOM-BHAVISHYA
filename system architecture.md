## System Architecture

### Version 1 — Interactive AI Escape Room

```mermaid
flowchart TD
    P["Player"] -->|"Types an action"| A["Streamlit · app.py"]
    R["Room and rules · game_prompt.py"] --> A
    H["Conversation history"] <-->|"Read and save messages"| A
    A -->|"Sends rules and conversation"| G["Gemini Game Master"]
    G -->|"Returns narration and escape status"| A
    A -->|"Displays the response"| P
```

Gemini interprets the player's action, decides what happens, and narrates the result. Streamlit stores the conversation and displays the response.

### Version 2 — Reliable AI Escape Room

```mermaid
flowchart TD
    P["Player"] -->|"Types an action"| A["Streamlit · app_v2.py"]
    A -->|"Passes the action"| E["Python validator · game_engine.py"]
    E <-->|"Checks progress and applies valid changes"| S["Game state: inventory, puzzles, and locks"]
    E -->|"Returns the approved outcome"| A
    A -->|"Sends approved descriptions"| G["Gemini narrator"]
    G -->|"Returns its description choice"| A
    A -->|"Displays selected or fallback narration"| P
```

Python checks each action and updates the game state. Gemini selects an approved description of the outcome. If Gemini is unavailable, Streamlit displays the approved local description.