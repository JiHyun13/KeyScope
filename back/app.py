# back/app.py
from flask import Flask, request, jsonify
from news_fetcher import get_articles, get_article_content
from summary import summarize
from flask_cors import CORS
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


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

