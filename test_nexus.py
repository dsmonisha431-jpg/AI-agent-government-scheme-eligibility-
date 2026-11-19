
import os
import requests
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).with_name(".env"))

api_key = os.getenv("NEXUS_API_KEY")
base_url = os.getenv("NEXUS_BASE_URL")

if not api_key or not base_url:
    print("ERROR: API key or Base URL missing")
else:
    url = base_url.rstrip("/") + "/v1/models"

    try:
        response = requests.get(
            url,
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=30
        )

        print("HTTP Status:", response.status_code)

        if response.status_code == 200:
            print("NEXUS API CONNECTED!")
            data = response.json()

            for model in data.get("data", []):
                print("Model:", model.get("id"))
        else:
            print("API Error:", response.text[:1000])

    except Exception as e:
        print("Connection Error:", str(e))
