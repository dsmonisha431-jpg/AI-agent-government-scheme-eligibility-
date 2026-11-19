
import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

if not api_key:
    print("Gemini API key missing!")
else:
    try:
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model=model,
            contents="Say Hello in Tamil"
        )
        print("GEMINI API CONNECTED!")
        print(response.text)
    except Exception as e:
        print("API Error:", e)
