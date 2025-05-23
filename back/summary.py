from flask import Flask, request, jsonify
import requests
import os
from dotenv import load_dotenv
from flask_cors import CORS
from crawler.integrated_crawler import save_articles_from_naver

load_dotenv()  # env 파일 로드 (토큰 보안 목적)

app = Flask(__name__)
CORS(app) #Flask에 cors 허용 추가...

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


#크롤러 API
@app.route("/crawl", methods=["POST"])
def crawl():
    data = request.get_json()
    keyword = data.get("text", "").strip()

    if not keyword:
        return jsonify({"error": "검색어가 비어 있습니다."}), 400

    try:
        save_articles_from_naver(keyword)
        return jsonify({"message": f"'{keyword}'에 대한 기사 수집 완료"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

