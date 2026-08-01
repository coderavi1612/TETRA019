import os
from google import genai

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")

for model in ["gemini-2.0-flash", "gemini-flash-latest"]:
    print(f"\nTesting model: {model}...")
    try:
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model=model,
            contents="Say hello and confirm you are online!"
        )
        print("SUCCESS!")
        print("Gemini Response:", response.text.strip())
        break
    except Exception as e:
        print("FAILED:", str(e))
