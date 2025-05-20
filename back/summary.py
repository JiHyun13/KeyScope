from flask import Flask, request, jsonify
import requests
import os
from dotenv import load_dotenv

load_dotenv()  # env 파일 로드 (토큰 보안 목적)

app = Flask(__name__)

HF_API_URL = "https://api-inference.huggingface.co/models/facebook/bart-large-cnn"
HF_HEADERS = {
    "Authorization": f"Bearer {os.getenv('HF_API_TOKEN')}"
}

@app.route("/summarize", methods=["POST"])
def summarize():
    data = request.get_json()
    article_text = data.get("text", "")

    # Hugging Face API 요청
    hf_response = requests.post(
        HF_API_URL,
        headers=HF_HEADERS,
        json={"inputs": article_text}
    )

    
    hf_response.encoding = 'utf-8' 

    if hf_response.status_code == 200:
        summary = hf_response.json()[0].get("summary_text", "요약 결과가 없습니다.")
        print(summary)

        response = jsonify({"summary": summary})
        response.headers["Content-Type"] = "application/json; charset=utf-8"
        return response
    else:
        response = jsonify({
            "error": "요약 실패",
            "detail": hf_response.text
        })
        response.headers["Content-Type"] = "application/json; charset=utf-8"
        return response, 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
