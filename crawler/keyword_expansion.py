import os, sys, re, json,time
from dotenv import load_dotenv
from supabase import create_client
from keybert import KeyBERT
from collections import Counter
from crawler.integrated_crawler import save_articles_from_naver_parallel



# 환경 변수 및 Supabase 설정
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
load_dotenv()
supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))

# 키워드 추출 모델
kw_model = KeyBERT(model='snunlp/KR-SBERT-V40K-klueNLI-augSTS')


def is_valid_keyword(word):
    if not word: return False
    if len(word) < 2 or len(word) > 10: return False
    if re.match(r"^\d", word): return False  # 숫자로 시작
    if any(x in word for x in ["보도", "기자", "부고", "운세", "뉴스", "afpbbnews"]): return False
    if re.search(r"[가-힣]+(의|를|은|는|이|가|에|로|과|와|도)$", word): return False
    if any(x in word for x in ["억", "천만", "위안", "달러"]): return False
    if word.endswith(("을", "를", "은", "는", "이", "가", "에", "의", "로")): return False
    return True

def get_keywords_for_query(query_keyword):
    response = supabase.table("test").select("article_keywords").eq("query_keyword", query_keyword).execute()
    print(f"🧩 '{query_keyword}'에 대한 행 개수:", len(response.data))

    keywords = []
    for row in response.data:
        if row["article_keywords"]:
            try:
                for kw in row["article_keywords"]:
                    if "keyword" in kw:
                        word = kw["keyword"].strip()
                        if 2 <= len(word) <= 15 and word != query_keyword:
                            keywords.append(word)
            except Exception as e:
                print(f"⚠️ 키워드 파싱 실패: {e}")
    print(f"🎯 추출된 키워드 수 (전처리 후): {len(keywords)})")
    return keywords

def get_top_similar_keywords(query_keyword, candidate_keywords, top_n=3, with_score=False):
    print("🔍 유사 키워드 추출 시작")
    if not candidate_keywords:
        return []

    candidate_keywords = list(set([kw for kw in candidate_keywords if kw != query_keyword]))
    filtered_keywords = [kw for kw in candidate_keywords if is_valid_keyword(kw)]
    filtered_keywords = list(set(filtered_keywords))[:30]
    if not filtered_keywords:
        return []

    try:
        print(f"🧠 유사도 계산 중...)")
        result = kw_model.extract_keywords(query_keyword, candidates=filtered_keywords, top_n=top_n)
    except Exception as e:
        print(f"⚠️ 유사도 계산 오류: {e}")
        result = []

    return result if with_score else [kw for kw, _ in result]


def expand_and_crawl_with_tree(query_keyword):
    print(f"✅ 시작: {query_keyword}")
    visited = set([query_keyword])

    # 루트에서 자식 3개 추출
    level1_candidates = get_keywords_for_query(query_keyword)
    level1_results = get_top_similar_keywords(query_keyword, level1_candidates, top_n=2, with_score=True)

    children = []

    for i, (child_kw, child_score) in enumerate(level1_results):
        if child_kw in visited:
            continue
        visited.add(child_kw)
        print(f"🌐 1차 크롤링: {child_kw}")
        try:
            save_articles_from_naver_parallel(child_kw)
        except Exception as e:
            print(f"❌ {child_kw} 크롤링 실패: {e}")

        # 자식 키워드에서 손주 2개 추출
        level2_candidates = get_keywords_for_query(child_kw)
        level2_results = get_top_similar_keywords(child_kw, level2_candidates, top_n=2, with_score=True)

        grandchildren = []
        for j, (g_kw, g_score) in enumerate(level2_results):
            if g_kw in visited:
                continue
            visited.add(g_kw)
            print(f"🌐 2차 크롤링: {g_kw}")
            try:
                save_articles_from_naver_parallel(g_kw)
            except Exception as e:
                print(f"❌ {g_kw} 크롤링 실패: {e}")
            grandchildren.append({
                "name": g_kw,
                "score": round(g_score, 3)
            })

        children.append({
            "name": child_kw,
            "score": round(child_score, 3),
            "children": grandchildren
        })

    return {
        "tree": {
            "name": query_keyword,
            "score": 1.0,
            "children": children
        }
    }




