from flask import Flask, request, jsonify
from news_fetcher import get_articles, get_article_content
from summary import summarize
from flask_cors import CORS
from crawler.integrated_crawler import save_articles_from_naver_parallel

app = Flask(__name__)
CORS(app)


@app.route("/api/articles")
def articles_api():
    keyword = request.args.get("keyword", "")
    try:
        articles = get_articles(keyword)
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

@app.route("/summarize", methods=["POST"])
def summarize_api():
    data = request.get_json()
    text = data.get("text", "")
    if not text:
        return jsonify({"error": "text 필드가 필요합니다."}), 400
    try:
        summary = summarize(text)
        return jsonify({"summary": summary})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/keywords")
def keyword_graph_api():
    from news_fetcher import get_keyword_graph
    try:
        data = get_keyword_graph()
        return jsonify({"graph": data})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route("/crawl", methods=["POST"])
def crawl_news():
    data = request.get_json()
    keyword = data.get("text", "").strip()
    print(f"🔍 검색어 수신: {keyword}")

    if not keyword:
        return jsonify({"error": "검색어가 없습니다"}), 400

    try:
        save_articles_from_naver_parallel(keyword)  # ✅ 핵심 동작 연결
        return jsonify({"message": f"'{keyword}' 관련 기사 수집 완료"})
    except Exception as e:
        print("❌ 수집 중 에러:", e)
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)