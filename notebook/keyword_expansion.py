import os, sys, re, json,time
from dotenv import load_dotenv
from supabase import create_client
from keybert import KeyBERT
from collections import Counter
from flask import jsonify



# 환경 변수 및 Supabase 설정
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from integrated_crawler import save_articles_from_naver_parallel

load_dotenv()
supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))

# 키워드 추출 모델
kw_model = KeyBERT(model='snunlp/KR-SBERT-V40K-klueNLI-augSTS')


def is_valid_keyword(word):
    if not word: return False
    word = word.strip()
    if word in ["제목", "없음"]: return False  # 의미 없는 키워드
    if len(word) < 2 or len(word) > 10: return False
    if re.match(r"^\d", word): return False
    if any(x in word for x in ["보도", "기자", "부고", "운세", "뉴스", "afpbbnews"]): return False
    if re.search(r"[가-힣]+(의|를|은|는|이|가|에|로|과|와|도)$", word): return False
    if any(x in word for x in ["억", "천만", "위안", "달러"]): return False
    if word.endswith(("을", "를", "은", "는", "이", "가", "에", "의", "로")): return False
    return True

def get_top_keywords_by_title(query_keyword, top_n=3):
    print(f"\n🧩 '{query_keyword}' 관련 기사 제목에서 키워드 추출")

    # Supabase에서 query_keyword에 해당하는 기사들 불러오기
    response = supabase.table("test").select("title").eq("query_keyword", query_keyword).execute()
    print(f"📄 제목 수: {len(response.data)}")

    word_counter = Counter()
    for row in response.data:
        title = row.get("title", "")
        words = re.findall(r"[가-힣]{2,}", title)  # 한글 2글자 이상만 추출
        filtered = [w for w in words if is_valid_keyword(w) and w != query_keyword]
        word_counter.update(filtered)

    # 상위 top_n 반환
    top_keywords = word_counter.most_common(top_n)
    
    print(f"🎯 최빈도 키워드: {top_keywords}")
    if not top_keywords:
        return []
    
    return [{"name": kw, "score": round(freq / top_keywords[0][1], 3)} for kw, freq in top_keywords]

def store_keyword_graph(parent, children):
    for child in children:
        name = child.get("name", "").strip()
        if not name:  # 빈 이름 필터
            continue

        try:
            supabase.table("keyword_graph").insert({
                "query_keyword": name,
                "article_keywords": parent
            }).execute()
            print(f"✅ 저장 성공: {name}")
        except Exception as e:
            print(f"❌ 저장 실패: {name} →", e)



# keyword_expansion.py

def expand_keywords(query_keyword):
    print(f"✅ 시작: {query_keyword}")
    
    graph = {
        query_keyword: {
            "primary": [],
            "secondary": []
        }
    }

    # 🔹 1차 확장
    primary_keywords = get_top_keywords_by_title(query_keyword)
    print(f"🔹 primary: {primary_keywords}")
    graph[query_keyword]["primary"] = [kw["name"] for kw in primary_keywords]

    for primary in primary_keywords:
        p_name = primary["name"]
        graph[p_name] = {"primary": [], "secondary": []}

        try:
            # 🔹 2차 확장 (secondary)
            secondary_keywords = get_top_keywords_by_title(p_name)
            print(f"🔸 secondary ({p_name}): {secondary_keywords}")
            graph[p_name]["secondary"] = [kw["name"] for kw in secondary_keywords]
        except Exception as e:
            print(f"❌ secondary 확장 실패 ({p_name}):", e)
            graph[p_name]["secondary"] = []

    print(f"✅ 그래프 완성: {graph}")
    return graph
