import os
import sys

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")

if not api_key and os.path.exists(".env"):
    with open(".env", "r") as f:
        for line in f:
            if line.strip().startswith("GEMINI_API_KEY="):
                api_key = line.split("=", 1)[1].strip().strip('"').strip("'")
                break

try:
    from google import genai
    client = genai.Client(api_key=api_key)
    print("Available Models:")
    for model in client.models.list():
        print(f" - {model.name} (Supported: {model.supported_actions})")
except Exception as e:
    print("FAILED:", str(e))
