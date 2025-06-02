<<<<<<< Updated upstream
import os
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def get_articles(keyword):
    if not keyword:
        return []

    # 1차: keyword 열에서 검색
    response = (
        supabase
        .from_("articles")
        .select("id,title,body")
        .ilike("keyword", f"%{keyword}%")
        .limit(10)
        .execute()
    )

    # 2차: 제목(title)에서 검색
    if not response.data:
        response = (
            supabase
            .from_("articles")
            .select("id,title,body")
            .ilike("title", f"%{keyword}%")
            .limit(10)
            .execute()
        )

    # 3차: 본문(body)에서 검색
    if not response.data:
        response = (
            supabase
            .from_("articles")
            .select("id,title,body")
            .ilike("body", f"%{keyword}%")
            .limit(10)
            .execute()
        )

    if response.error:
        raise Exception(response.error.message)
    
    return response.data or []


def get_article_content(article_id):
    response = (
        supabase
        .from_("articles")
        .select("body")
        .eq("id", article_id)
        .single()
        .execute()
    )

    if response.error:
        raise Exception(response.error.message)

    return response.data["body"]

def get_keyword_graph():
    response = (
        supabase
        .from_("keyword_graph")
        .select("keyword, parent")
        .execute()
    )
    if response.error:
        raise Exception(response.error.message)

    # 계층 구조로 재구성
    graph = {}
    for row in response.data:
        keyword = row["keyword"]
        parent = row["parent"]
        if parent is None:
            if keyword not in graph:
                graph[keyword] = {"primary": []}
        else:
            if parent not in graph:
                graph[parent] = {"primary": []}
            graph[parent]["primary"].append(keyword)
    return graph
=======
# back/news_fetcher.py
import os
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# 🔍 검색 키워드로 기사 리스트 가져오기 (query_keyword → title → body 순으로 검색)
def get_articles(keyword):
    if not keyword:
        return []

    for column in ["query_keyword", "title", "body"]:
        response = (
            supabase
            .from_("test")
            .select("id,title,body")
            .ilike(column, f"%{keyword}%")
            .limit(10)
            .execute()
        )
        if response.data:
            break

    if response.error:
        raise Exception(response.error.message)

    return response.data or []

# 📰 특정 기사 ID로 기사 본문(body) 가져오기
def get_article_content(article_id):
    response = (
        supabase
        .from_("test")
        .select("body")
        .eq("id", article_id)
        .single()
        .execute()
    )

    if response.error:
        raise Exception(response.error.message)

    return response.data["body"]

# 🧠 전체 키워드 그래프 가져오기 (query_keyword → article_keywords 기반 계층형 구조)
def get_keyword_graph():
    response = (
        supabase
        .from_("keyword_graph")
        .select("article_keywords,query_keyword")
        .execute()
    )

    if response.error:
        raise Exception(response.error.message)

    graph = {}
    for row in response.data:
        child = row["query_keyword"]
        parent = row["article_keywords"]

        if parent is None:
            if child not in graph:
                graph[child] = {"primary": []}
        else:
            if parent not in graph:
                graph[parent] = {"primary": []}
            if child not in graph[parent]["primary"]:
                graph[parent]["primary"].append(child)

    return graph
>>>>>>> Stashed changes
