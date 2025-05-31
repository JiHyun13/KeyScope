import os, sys, re, json,time
from dotenv import load_dotenv
from supabase import create_client
from keybert import KeyBERT
from collections import Counter
from flask import jsonify
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
    return [{"name": kw, "score": round(freq / top_keywords[0][1], 3)} for kw, freq in top_keywords]


def expand_keywords(query_keyword):
    print(f"✅ 시작: {query_keyword}")

    children_list = get_top_keywords_by_title(query_keyword)
    print(f"확장 키워드 리스트: {children_list}")

    if not children_list:
        print(f"🔄 기사 없음, 크롤링 수행: {query_keyword}")
        save_articles_from_naver_parallel(query_keyword)
        print(f"크롤링 완료, 재조회 시작: {query_keyword}")
        children_list = get_top_keywords_by_title(query_keyword)
        print(f"크롤링 후 확장 키워드 리스트: {children_list}")

    return children_list

# def expand_crawl_with_tree(child_keyword):
#     save_articles_from_naver_parallel(child_keyword['name'])

#         # grand_keywords = get_top_keywords_by_title(child['name'], top_n=2)
#         # for g in grand_keywords:
#         #     try:
#         #         print(f"🌐 손자 크롤링 시작: {g['name']}")
#         #         save_articles_from_naver_parallel(g['name'])
#         #         print(f"🌐 손자 크롤링 완료: {g['name']}")
#         #     except Exception as e:
#         #         print(f"❌ 손자 크롤링 실패: {e}")
#         # child["children"] = grand_keywords

#     print("크롤링+확장 결과 트리:", )
#     return tree
