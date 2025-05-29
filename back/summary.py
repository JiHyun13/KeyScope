# back/summary.py
import requests
import os
from dotenv import load_dotenv

load_dotenv()

HF_API_URL = "https://api-inference.huggingface.co/models/facebook/bart-large-cnn"
HF_HEADERS = {
    "Authorization": f"Bearer {os.getenv('HF_API_TOKEN')}"
}

def summarize(text):
    response = requests.post(
        HF_API_URL,
        headers=HF_HEADERS,
        json={"inputs": text}
    )

    if response.status_code == 200:
        return response.json()[0].get("summary_text", "요약 결과가 없습니다.")
    else:
        raise Exception(f"요약 실패: {response.text}")
