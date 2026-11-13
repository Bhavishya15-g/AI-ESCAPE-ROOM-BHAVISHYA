import copy
import re


# Solutions remain in Python, outside the narrator.
DRAWER_CODE = "314"
PAINTING_NUMBER = "6285"
EXIT_CODE = "5826"

HELP = (
    "Try: examine desk, examine bookshelf, examine painting, "
    "open drawer with 314, take key, use key on painting, "
    "enter a four-digit code into the door, inventory, or hint."
)

# This help message intentionally does not reveal solutions.
HELP = (
    "Try: examine desk, examine bookshelf, examine painting, "
    "open drawer with CODE, take key, use key on painting, "
    "enter CODE into the door, inventory, or hint."
)


def new_game():
    return {
        "room": "library",
        "objects": ["desk", "bookshelf", "drawer", "painting", "door"],
        "inventory": [],
        "clues_seen": [],
        "drawer_open": False,
        "painting_open": False,
        "door_open": False,
        "solved_puzzles": [],
        "escaped": False,
    }


def normalize(text):
    text = text.lower().strip()
    text = re.sub(r"[.!?]+$", "", text)
    return re.sub(r"\s+", " ", text)


def remember(state, field, value):
    if value not in state[field]:
        state[field].append(value)


def apply_action(current_state, player_text):
    """Return a new state and an approved player-facing outcome."""
    state = copy.deepcopy(current_state)
    action = normalize(player_text)

    if state["escaped"]:
        return state, "You have already escaped. Restart to play again."

    if action in {"help", "instructions", "what can i do"}:
        return state, HELP

    if action in {
        "inventory",
        "check inventory",
        "check my inventory",
        "show inventory",
    }:
        items = ", ".join(state["inventory"]) or "nothing"
        return state, f"You are carrying: {items}."

    if action in {"hint", "give me a hint", "help me"}:
        if not state["drawer_open"]:
            message = "Read the desk note and compare the book dates."
        elif "brass key" not in state["inventory"]:
            message = "Look inside the open drawer and collect its item."
        elif not state["painting_open"]:
            message = "Examine the painting and consider where the key fits."
        else:
            message = "The desk note explains how to read the final number."
        return state, message

    # Only complete, recognized commands are accepted.
    # Extra instructions attached to a command are not executed.
    examination = re.fullmatch(
        r"(?:examine|inspect|look at|investigate)"
        r" (?:the )?(desk|bookshelf|drawer|painting|door)",
        action,
    )

    if examination:
        target = examination.group(1)

        if target == "desk":
            remember(state, "clues_seen", "desk")
            return state, (
                "Two notes lie on the desk: "
                "'Arrange the books oldest first' and "
                "'Read the final number backwards.'"
            )

        if target == "bookshelf":
            remember(state, "clues_seen", "bookshelf")
            return state, (
                "Three books show dates and digits: "
                "Astronomy — 2005 — digit 4; "
                "History — 1980 — digit 3; "
                "Poetry — 1995 — digit 1."
            )

        if target == "drawer":
            if not state["drawer_open"]:
                return state, "The drawer is locked with a three-digit keypad."
            if "brass key" in state["inventory"]:
                return state, "The drawer is open and empty."
            return state, "The open drawer contains a brass key."

        if target == "painting":
            if state["painting_open"]:
                return state, (
                    f"The painting compartment is open. "
                    f"The number inside is {PAINTING_NUMBER}."
                )
            return state, (
                "The painting frame has a small keyhole. "
                "Its compartment is locked."
            )

        return state, "The exit door is locked with a four-digit keypad."

    drawer_attempt = re.fullmatch(
        r"(?:open|unlock) (?:the )?drawer"
        r" (?:with|using)(?: (?:the )?code)? (\d+)",
        action,
    )

    if drawer_attempt:
        if state["drawer_open"]:
            return state, "The drawer is already open."

        if drawer_attempt.group(1) != DRAWER_CODE:
            return state, "Incorrect drawer code. The drawer stays locked."

        state["drawer_open"] = True
        remember(state, "solved_puzzles", "book_order")
        return state, (
            "The drawer unlocks. Inside is a brass key. "
            "You can now take it."
        )

    if action in {"open drawer", "open the drawer"}:
        if state["drawer_open"]:
            return state, "The drawer is already open."
        return state, "The drawer needs a three-digit code."

    if re.fullmatch(
        r"(?:take|collect|pick up) (?:the )?(?:brass )?key",
        action,
    ):
        if not state["drawer_open"]:
            return state, "You cannot collect the key from a locked drawer."

        if "brass key" in state["inventory"]:
            return state, "You already have the brass key."

        state["inventory"].append("brass key")
        return state, "You collect the brass key and put it in your inventory."

    if re.fullmatch(
        r"use (?:the )?(?:brass )?key on (?:the )?painting",
        action,
    ):
        if "brass key" not in state["inventory"]:
            return state, "You must collect the brass key before using it."

        if state["painting_open"]:
            return state, "The painting compartment is already open."

        state["painting_open"] = True
        remember(state, "solved_puzzles", "painting_lock")
        return state, (
            "The key opens the painting compartment. "
            f"Inside is the number {PAINTING_NUMBER}."
        )

    door_attempt = re.fullmatch(
        r"(?:"
        r"(?:open|unlock) (?:the )?door"
        r" (?:with|using)(?: (?:the )?code)? (\d+)"
        r"|enter (\d+) (?:into|in|on) (?:the )?door"
        r")",
        action,
    )

    if door_attempt:
        code = door_attempt.group(1) or door_attempt.group(2)

        if code != EXIT_CODE:
            return state, "Incorrect exit code. The door stays locked."

        prerequisites_met = (
            state["drawer_open"]
            and "brass key" in state["inventory"]
            and state["painting_open"]
            and "book_order" in state["solved_puzzles"]
            and "painting_lock" in state["solved_puzzles"]
        )

        if not prerequisites_met:
            return state, (
                "The exit remains locked. Complete the drawer "
                "and painting puzzles first."
            )

        state["door_open"] = True
        state["escaped"] = True
        remember(state, "solved_puzzles", "reverse_number")
        return state, "The exit door unlocks. You step outside. You escaped!"

    # Unknown objects, false claims, and bypass instructions reach here.
    return state, (
        "That action is not supported. No game progress was changed. "
        + HELP
    )