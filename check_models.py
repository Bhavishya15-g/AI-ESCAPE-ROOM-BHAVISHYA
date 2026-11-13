import os
from pathlib import Path

from dotenv import load_dotenv
from google import genai

load_dotenv(Path(__file__).with_name(".env"), override=True)

api_key = os.getenv("GEMINI_API_KEY", "").strip()

if not api_key or api_key == "PASTE_YOUR_REAL_KEY_HERE":
    raise SystemExit("Add your real Gemini API key to .env first.")

with genai.Client(api_key=api_key) as client:
    print("Models supporting text generation:\n")

    for model in client.models.list():
        actions = model.supported_actions or []

        if "generateContent" in actions:
            print(model.name.removeprefix("models/"))