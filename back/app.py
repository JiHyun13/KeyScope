from flask import Flask, request, jsonify, Response, stream_with_context
from flask_cors import CORS
import sys
import os
import re
from collections import OrderedDict
import asyncio

# 경로 설정
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from news_fetcher import get_articles, get_article_content
from summary import summarize
from crawler.integrated_crawler import save_articles_from_naver_parallel
from crawler.keyword_expansion import expand_keywords, get_top_keywords_by_title

# Flask 앱 초기화
app = Flask(__name__)
CORS(app)

# ==================== 🔧 유틸 함수 ====================

def deduplicate_articles(articles):
    seen = set()
    unique = []
    for article in articles:
        key = article.get("title")  # 중복 제거 기준: 'title' 또는 'url'도 가능
        if key and key not in seen:
            seen.add(key)
            unique.append(article)
    return unique

# ==================== 📰 뉴스 수집 ====================

@app.route("/crawl", methods=["POST"])
async def crawl_news():
    data = request.get_json()
    keyword = data.get("text", "").strip()
    print(f"🔍 검색어 수신: {keyword}")

    if not keyword:
        return jsonify({"error": "검색어가 없습니다"}), 400

    try:
        await save_articles_from_naver_parallel(keyword)
        children = get_top_keywords_by_title(keyword, top_n=3)
        child_names = [c["name"] for c in children]

        return jsonify({
            "message": f"'{keyword}' 쿼리 관련 기사 수집 완료",
            "children": child_names
        })
    except Exception as e:
        print("❌ 수집 중 에러:", e)
        return jsonify({"error": str(e)}), 500

# ==================== 🌐 키워드 확장 ====================

@app.route("/expand", methods=["POST"])
async def expand_keywords_api():
    data = request.get_json()
    keyword = data.get("text", "").strip()

    if not keyword:
        return jsonify({"error": "검색어가 없습니다"}), 400

    try:
        expanded_result = await expand_keywords(keyword)
        return jsonify({"expanded_keywords": expanded_result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ==================== 🧠 요약 ====================

@app.route("/summarize", methods=["POST"])
def summarize_api():
    data = request.get_json()
    text = data.get("text", "")

    if not isinstance(text, str):
        return jsonify({"error": "text 필드는 문자열이어야 합니다."}), 400

    if not text:
        return jsonify({"error": "text 필드가 필요합니다."}), 400

    try:
        summary_result = summarize(text)
        return jsonify(summary_result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ==================== 📦 기사 데이터 API ====================

@app.route("/api/articles")
def articles_api():
    keyword = request.args.get("keyword", "")
    try:
        articles = get_articles(keyword)
        articles = deduplicate_articles(articles)
        return jsonify({"articles": articles})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/article_content")
def article_content_api():
    article_id = request.args.get("article_id")
    if not article_id:
        return jsonify({"error": "article_id가 필요합니다."}), 400

    try:
        content = get_article_content(article_id)
        return jsonify({"content": content})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ==================== 🚀 앱 실행 ====================

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
