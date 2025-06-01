import os, sys, re, json, time, asyncio
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

# 키워드 유효성 검사 함수
def is_valid_keyword(word):
    if not word: return False
    if len(word) < 2 or len(word) > 10: return False
    if re.match(r"^\d", word): return False  # 숫자로 시작
    if any(x in word for x in ["보도", "기자", "부고", "운세", "뉴스", "afpbbnews"]): return False
    if re.search(r"[가-힣]+(의|를|은|는|이|가|에|로|과|와|도)$", word): return False
    if any(x in word for x in ["억", "천만", "위안", "달러"]): return False
    if word.endswith(("을", "를", "은", "는", "이", "가", "에", "의", "로")): return False
    return True

# DB에서 쿼리 확인
def check_query_in_db(query_keyword):
    try:
        # query_keyword를 기준으로 데이터 존재 여부 확인
        existing = supabase.table("test").select("id").eq("query_keyword", query_keyword).execute()
        # 데이터가 있으면 True, 없으면 False 반환
        return bool(existing.data)  # 이미 DB에 저장된 데이터가 있으면 True 반환
    except Exception as e:
        print(f"❌ DB 확인 중 오류: {e}")
        return False  # 오류 발생 시 False 반환

# 제목에서 키워드 추출
def get_top_keywords_by_title(query_keyword, top_n=3):
    print(f"🧩 '{query_keyword}' 관련 기사 제목에서 키워드 추출")
    
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

# 자식에 대한 손자 키워드 추출 (자식 3개에 대해 손자 2개)
async def get_grandchild_keywords(child_keyword, top_n=2):
    print(f"🌱 {child_keyword} 관련 손자 키워드 추출")

    try:
        # Supabase에서 자식 키워드에 해당하는 기사들 불러오기
        response = supabase.table("test").select("title").eq("query_keyword", child_keyword).execute()
        print(f"📄 자식 제목 수: {len(response.data)}")

        if len(response.data) == 0:
            print(f"❌ 자식 키워드에 대한 관련 기사 없음: {child_keyword}")
            print(f"🔄 크롤링 시작: {child_keyword}")
            await save_articles_from_naver_parallel(child_keyword)  # 자식 키워드에 대한 기사가 없으면 크롤링 수행
            response = supabase.table("test").select("title").eq("query_keyword", child_keyword).execute()  # 크롤링 후 다시 데이터 조회
            print(f"📄 크롤링 후 자식 제목 수: {len(response.data)}")

        word_counter = Counter()
        for row in response.data:
            title = row.get("title", "")
            words = re.findall(r"[가-힣]{2,}", title)  # 한글 2글자 이상만 추출
            filtered = [w for w in words if is_valid_keyword(w) and w != child_keyword]
            word_counter.update(filtered)

        # 상위 top_n 반환
        top_keywords = word_counter.most_common(top_n)
        print(f"🎯 손자 최빈도 키워드: {top_keywords}")
        return [{"name": kw, "score": round(freq / top_keywords[0][1], 3)} for kw, freq in top_keywords]

    except Exception as e:
        print(f"❌ 손자 키워드 추출 중 오류: {e}")
        return []  # 예외 발생 시 빈 리스트 반환

# 쿼리에 대해 자식과 손자 리스트를 생성하는 최종 함수
async def expand_keywords(query_keyword):
    print(f"✅ 시작: {query_keyword}")
    
    try:
        # 쿼리 자체에 대한 자식 키워드 목록 가져오기
        children_list = get_top_keywords_by_title(query_keyword)
        print(f"자식 키워드 리스트: {children_list}")

        expanded_result = {}

        # 쿼리 키워드도 expanded_result에 추가
        expanded_result[query_keyword] = {
            "name": query_keyword,
            "score": 1.0,  # 기본 점수, 필요 시 수정 가능
            "children": children_list
        }

        if not children_list:
            print(f"🔄 기사 없음, 크롤링 수행: {query_keyword}")
            await save_articles_from_naver_parallel(query_keyword)  # 비동기 크롤링 수행
            print(f"크롤링 완료, 재조회 시작: {query_keyword}")
            children_list = get_top_keywords_by_title(query_keyword)

        # 자식 키워드에 대해 손자 키워드 2개 추출
        for child in children_list:
            child_keyword = child['name']
            print(f"🌱 {child_keyword}의 손자 키워드 생성 시작")

            # 자식 키워드에 대해 손자 키워드 추출
            grandchild_list = await get_grandchild_keywords(child_keyword, top_n=2)  # 비동기 호출
            child["children"] = grandchild_list  # 자식에 손자 추가

            # 자식 키워드를 expanded_result에 추가
            expanded_result[child_keyword] = child

        print(f"✅ 확장된 키워드 결과: {expanded_result}")

        return expanded_result

    except Exception as e:
        print(f"❌ 키워드 확장 중 오류: {e}")
        return []  # 오류 발생 시 빈 리스트 반환
