## Development Process

### Version 1 — Interactive AI Escape Room

I first built `app.py` to test whether a player could explore the locked library through a chat interface. I defined the room, objects, clues, and puzzle rules in `game_prompt.py`. Streamlit kept the conversation history, and Gemini acted as the Game Master. It interpreted the player's actions, described the outcomes, and reported when the player escaped.

During setup, I encountered a model-unavailable error. Streamlit opened the game, but Gemini could not answer the first player action with the configured model. This exposed a dependency on the Gemini API for gameplay.

I also identified a limitation in how Version 1 tracked progress. The app checked the format of Gemini's response, but it relied on Gemini to remember which items the player had collected and which puzzles were complete. That left the game vulnerable to inconsistent decisions, such as accepting a claimed key or reporting an escape before the required puzzles were solved.

### Version 2 — Reliable AI Escape Room

I added `app_v2.py` and moved the game rules into `game_engine.py`. The engine stores the player's inventory, solved puzzles, and lock status in a structured Python dictionary. It checks each action against that state before updating the game.

| Version 1 limitation | Version 2 change | Why it was necessary |
|---|---|---|
| Gemini inferred progress from the conversation. | Python stores inventory, puzzle progress, and lock status explicitly. | The game can check whether the player actually collected the key or solved a puzzle. |
| Gemini decided whether an action succeeded. | Python validates actions and checks prerequisites before updating state. | An incorrect code keeps the drawer locked, and the correct exit code alone cannot skip the required puzzles. |
| Gemini generated the outcome and its description together. | Gemini selects from descriptions approved by the game engine. | The description shown to the player matches the outcome decided by Python. |
| A failed Gemini request interrupted gameplay. | The app displays an approved local description if Gemini is unavailable. | The player can continue solving puzzles during an API error. |

Both versions have separate entry points so they can be run and compared. See [test cases and comparison results](docs/TEST_CASES.md) for the inputs used to evaluate valid actions, invalid actions, and attempts to skip puzzle requirements.