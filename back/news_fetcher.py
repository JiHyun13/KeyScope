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

    # 1차: query_keyword에서 검색
    response = (
        supabase
        .from_("test")
        .select("id,title,body,url")
        .ilike("query_keyword", f"%{keyword}%")
        .limit(10)
        .execute()
    )

    if response.data:
        return response.data

    # 2차: title에서 검색
    response = (
        supabase
        .from_("test")
        .select("id,title,body,url")
        .ilike("title", f"%{keyword}%")
        .limit(10)
        .execute()
    )

    if response.data:
        return response.data

    # 3차: body에서 검색
    response = (
        supabase
        .from_("test")
        .select("id,title,body,url")
        .ilike("body", f"%{keyword}%")
        .limit(10)
        .execute()
    )

    return response.data or []


def get_article_content(article_id):
    response = (
        supabase
        .from_("test")
        .select("body")
        .eq("id", article_id)
        .single()
        .execute()
    )

    if not response.data or "body" not in response.data or not response.data["body"]:
        raise Exception(f"기사 본문이 비어 있거나 존재하지 않습니다. (ID: {article_id})")

    print(f"✅ Supabase 응답 데이터: {response.data}")  # 로그 추가

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