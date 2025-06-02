import requests
import urllib.parse
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from supabase import create_client, Client
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from keybert import KeyBERT
import time
import os
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# ✅ Supabase 설정
SUPABASE_URL = "https://ypyujiaoeaqykbqetjef.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InlweXVqaWFvZWFxeWticWV0amVmIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDY1NDUyNTQsImV4cCI6MjA2MjEyMTI1NH0.RuR9l89gxCcMkSzO053EHluQ0ers-piN4SUjZ-LtWjU"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


## -----------------언론사 크롤러 코드 시작!!!! 여기부터 안 건드려도 돼요--------------------
def crawl_yonhap_news(url):
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        return None
    soup = BeautifulSoup(response.text, 'html.parser')
    title_tag = soup.find('h1', class_='tit01')
    title = title_tag.get_text(strip=True) if title_tag else "제목 없음"

    body_tag = soup.find('div', class_='story-news article')
    if body_tag:
        paragraphs = body_tag.find_all('p')
        body_lines = []
        for p in paragraphs:
            if 'txt-copyright' in p.get('class', []): continue
            text = p.get_text(strip=True)
            if text:
                body_lines.append(text)
        body = '\n'.join(body_lines)
    else:
        body = "본문 없음"

    return {"title": title, "url": url, "body": body, "media": "연합뉴스"}


def crawl_newsis_news(url):
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        return None
    soup = BeautifulSoup(response.text, 'html.parser')

    title_tag = soup.select_one('h1.tit.title_area')
    title = title_tag.get_text(strip=True) if title_tag else "제목 없음"

    body_tag = soup.find('div', class_='viewer')
    if body_tag:
        raw_text = body_tag.get_text(separator="\n").strip()
        body_lines = [line.strip() for line in raw_text.split("\n") if line.strip()]
        body = '\n'.join(body_lines)
    else:
        body = "본문 없음"

    return {"title": title, "url": url, "body": body, "media": "뉴시스"}


def crawl_mt_news(url):
    headers = {
        'User-Agent': 'Mozilla/5.0'
    }

    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print("❌ 기사 요청 실패:", response.status_code)
        return None

    soup = BeautifulSoup(response.text, 'html.parser')

    title_tag = soup.find('h1', class_=['subject'])
    title = title_tag.get_text(strip=True) if title_tag else "제목 없음"

    body_tag = soup.find('div', class_='view_text')

    if body_tag:
        raw_text = body_tag.get_text(separator="\n").strip()
        body_lines = [line.strip() for line in raw_text.split("\n") if line.strip()]
        body = '\n'.join(body_lines)
    else:
        body = "본문 없음"

    return {
        "title": title,
        "url": url,
        "body": body,
        "media": "머니투데이"
    }


def crawl_heraldcorp_news(url):
    headers = {
        'User-Agent': 'Mozilla/5.0'
    }

    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print("❌ 기사 요청 실패:", response.status_code)
        return None

    soup = BeautifulSoup(response.text, 'html.parser')

    title = soup.select_one('div.news_title > h1')
    title = title.get_text(strip=True) if title else "제목 없음"

    body_tag = soup.find('article', id='articleText')

    if body_tag:
        raw_text = "\n".join([p.get_text(strip=True) for p in body_tag.find_all('p')]).strip()
        body_lines = [line.strip() for line in raw_text.split("\n") if line.strip()]
        body = '\n'.join(body_lines)
    else:
        body = "본문 없음"

    return {
        "title": title,
        "url": url,
        "body": body,
        "media": "헤럴드경제"
    }


def crawl_sedaily_news(url):
    headers = {
        'User-Agent': 'Mozilla/5.0'
    }

    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print("❌ 기사 요청 실패:", response.status_code)
        return None

    soup = BeautifulSoup(response.text, 'html.parser')

    title_tag = soup.find('h1', class_=['art_tit'])
    title = title_tag.get_text(strip=True) if title_tag else "제목 없음"

    body_tag = soup.find('div', class_='article_view')

    if body_tag:
        for fig in body_tag.find_all('figure', class_='art_photo'):
            fig.decompose()

        for br in body_tag.find_all('br'):
            br.replace_with('\n')

        raw_text = body_tag.get_text(separator="\n").strip()
        body_lines = [line.strip() for line in raw_text.split("\n") if line.strip()]
        body = '\n'.join(body_lines)
    else:
        body = "본문 없음"

    return {
        "title": title,
        "url": url,
        "body": body,
        "media": "서울경제"
    }


def crawl_newspim_news(url):
    headers = {
        'User-Agent': 'Mozilla/5.0'
    }

    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print("❌ 기사 요청 실패:", response.status_code)
        return None

    soup = BeautifulSoup(response.text, 'html.parser')

    title_tag = soup.find('h2')
    title = title_tag.get_text(strip=True) if title_tag else "제목 없음"

    body_tag = soup.find('div', class_='contents', itemprop='articleBody')

    if body_tag:
        raw_text = "\n".join([p.get_text(strip=True) for p in body_tag.find_all('p')]).strip()
        body_lines = [line.strip() for line in raw_text.split("\n") if line.strip()]
        body = ''.join(body_lines)
    else:
        body = "본문 없음"

    return {
        "title": title,
        "url": url,
        "body": body,
        "media": "뉴스핌"
    }


def crawl_dailian_news(url):
    headers = {
        'User-Agent': 'Mozilla/5.0'
    }

    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print("❌ 기사 요청 실패:", response.status_code)
        return None

    soup = BeautifulSoup(response.text, 'html.parser')

    title_tag = soup.find('h1', class_=['title'])
    title = title_tag.get_text(strip=True) if title_tag else "제목 없음"

    body_tag = soup.find('div', class_='article')

    if body_tag:
        raw_text = "\n".join([p.get_text(strip=True) for p in body_tag.find_all('p')]).strip()
        body_lines = [line.strip() for line in raw_text.split("\n") if line.strip()]
        body = ''.join(body_lines)
    else:
        body = "본문 없음"

    return {
        "title": title,
        "url": url,
        "body": body,
        "media": "데일리안"
    }


def crawl_mk_news(url):
    headers = {
        'User-Agent': 'Mozilla/5.0'
    }

    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print("❌ 기사 요청 실패:", response.status_code)
        return None

    soup = BeautifulSoup(response.text, 'html.parser')

    title_tag = soup.find('h2', class_=['news_ttl'])
    title = title_tag.get_text(strip=True) if title_tag else "제목 없음"
    
    body_tag = soup.find('div', class_='news_cnt_detail_wrap', itemprop='articleBody')

    if body_tag:
        p_texts = [p.get_text(strip=True) for p in body_tag.find_all('p')]
        p_texts = [text for text in p_texts if text]

        if p_texts:
            body = ''.join(p_texts)
        else:
            br_texts = [str(t).strip() for t in body_tag.children if t and str(t).strip() and not getattr(t, 'name', None)]
            br_texts = [text for text in br_texts if text]
            if br_texts:
                body = ''.join(br_texts)
            else:
                body = "본문 없음"
    else:
        body = "본문 없음"
        
    return {
        "title": title,
        "url": url,
        "body": body,
        "media": "매일경제"
    }


def crawl_asiae_news(url):
    headers = {
        'User-Agent': 'Mozilla/5.0'
    }

    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print("❌ 기사 요청 실패:", response.status_code)
        return None

    soup = BeautifulSoup(response.text, 'html.parser')

    title_tag = soup.find('h1')
    title = title_tag.get_text(strip=True) if title_tag else "제목 없음"
    
    body_tag = soup.find('div', class_='article')

    if body_tag:
        p_tags = [p for p in body_tag.find_all('p') if 'txt_prohibition' not in p.get('class', [])]

        raw_text = "\n".join([p.get_text(strip=True) for p in p_tags]).strip()

        body_lines = [line.strip() for line in raw_text.split("\n") if line.strip()]

        body = ''.join(body_lines)
    else:
        body = "본문 없음"

    return {
        "title": title,
        "url": url,
        "body": body,
        "media": "아시아경제"
    }
    
def crawl_nocut_news(url):
    headers = {
        'User-Agent': 'Mozilla/5.0'
    }

    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print("❌ 기사 요청 실패:", response.status_code)
        return None

    soup = BeautifulSoup(response.text, 'html.parser')
    
    # 제목 추출
    title_tag = soup.find('h2')
    title = title_tag.get_text(strip=True) if title_tag else "제목 없음"
    
    body_tag = soup.find('div', id='pnlContent')  # id 속성으로 본문 div를 찾음

    if body_tag:
        for br in body_tag.find_all("br"):
            br.replace_with("")  # br 태그 삭제, 줄바꿈 없이 이어붙임

        raw_text = body_tag.get_text(strip=True)
        # 불필요한 빈 줄 제거 및 공백 정리
        body_lines = [line.strip() for line in raw_text.split("\n") if line.strip()]
        body = "\n".join(body_lines)
    else:
        body = "본문 없음"

    return {
        "title": title,
        "url": url,
        "body": body,
        "media": "노컷뉴스"
    }
    
def crawl_edaily_news(url):
    headers = {
        'User-Agent': 'Mozilla/5.0'
    }

    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print("❌ 기사 요청 실패:", response.status_code)
        return None

    soup = BeautifulSoup(response.text, 'html.parser')
    
    # 제목 추출
    title_tag = soup.find('h1')
    title = title_tag.get_text(strip=True) if title_tag else "제목 없음"
    
    body_tag = soup.find('div', class_='news_body', itemprop='articleBody')

    if body_tag:
    # 부수 요소 제거
        for tag_to_remove in body_tag.find_all(['table', 'div'], class_=['gg_textshow']):
            tag_to_remove.decompose()  # 태그 자체 삭제

    # <br> 태그는 줄바꿈 문자로 변환
        for br in body_tag.find_all("br"):
            br.replace_with("\n")

        raw_text = body_tag.get_text(separator="\n", strip=True)

    # 빈 줄 제거 및 공백 정리
        body_lines = [line.strip() for line in raw_text.split("\n") if line.strip()]
        body = "\n".join(body_lines)
        
        body = body.replace('\n', '').replace('\r', '')
    else:
        body = "본문 없음"

    return {
        "title": title,
        "url": url,
        "body": body,
        "media": "이데일리"
    }
    
#경인일보 크롤링 함수
def crawl_kyeongin_news(url):
    headers = {
        'User-Agent': 'Mozilla/5.0'
    }

    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print("❌ 기사 요청 실패:", response.status_code)
        return None

    soup = BeautifulSoup(response.text, 'html.parser')
    
    # 제목 추출
    title_tag = soup.find('h1')
    title = title_tag.get_text(strip=True) if title_tag else "제목 없음"
    
    body_tag = soup.find('div', class_='article-body')  # 혹은 id='article-body'

    if body_tag:
        # 광고용 div 등 불필요한 요소 제거: id가 'svcad_'로 시작하는 div 제거
        for ad_div in body_tag.find_all('div'):
            if ad_div.get('id') and ad_div['id'].startswith('svcad_'):
                ad_div.decompose()

        # table, 특정 클래스 div 제거 (필요시 추가)
        for tag_to_remove in body_tag.find_all(['table', 'div'], class_=['gg_textshow']):
            tag_to_remove.decompose()

        # <br> 태그를 줄바꿈으로 변환
        for br in body_tag.find_all('br'):
            br.replace_with('\n')

        raw_text = body_tag.get_text(separator='\n', strip=True)

        # 빈 줄 제거 및 공백 정리
        body_lines = [line.strip() for line in raw_text.split("\n") if line.strip()]
        body = "\n".join(body_lines)
        
        body = body.replace('\n', '').replace('\r', '')

    else:
        body = "본문 없음"
   
    return {
        "title": title,
        "url": url,
        "body": body,
        "media": "경인일보"
    }

def crawl_seoul_news(url):
    headers = {
        'User-Agent': 'Mozilla/5.0'
    }

    response = requests.get(url, headers=headers)

    # 인코딩 강제 지정 (utf-8 또는 euc-kr 둘 중 하나 시도)
    response.encoding = 'utf-8'  # 또는 'euc-kr'

    if response.status_code != 200:
        print("❌ 기사 요청 실패:", response.status_code)
        return None

    soup = BeautifulSoup(response.text, 'html.parser')
    
    # 제목 추출
    title_tag = soup.find('h1')
    title = title_tag.get_text(strip=True) if title_tag else "제목 없음"
    
    body_tag = soup.find('div', class_='viewContent body18 color700')

    if body_tag:
        # 광고 div 제거 (예: id가 svcad_로 시작하는 div)
        for ad_div in body_tag.find_all('div'):
            if ad_div.get('id') and ad_div['id'].startswith('svcad_'):
                ad_div.decompose()

        # 불필요한 태그 제거 (필요 시 추가)
        for tag_to_remove in body_tag.find_all(['table', 'div'], class_=['gg_textshow']):
            tag_to_remove.decompose()

        # <br> 태그를 줄바꿈 문자로 대체
        for br in body_tag.find_all('br'):
            br.replace_with('\n')

        # 텍스트 추출 및 빈 줄 제거
        raw_text = body_tag.get_text(separator='\n', strip=True)
        body_lines = [line.strip() for line in raw_text.split('\n') if line.strip()]
        body = '\n'.join(body_lines)
        body = body.replace('\n', '').replace('\r', '')

    else:
        body = "본문 없음"

    return {
        "title": title,
        "url": url,
        "body": body,
        "media": "서울신문"
    }
    
def crawl_fn_news(url):
    headers = {
        'User-Agent': 'Mozilla/5.0'
    }

    response = requests.get(url, headers=headers)

# 인코딩 강제 지정 (utf-8 또는 euc-kr 둘 중 하나 시도)
    response.encoding = 'utf-8'  # 또는 'euc-kr'

    if response.status_code != 200:
        print("❌ 기사 요청 실패:", response.status_code)
        return None

    soup = BeautifulSoup(response.text, 'html.parser')
    
    # 제목 추출
    title_tag = soup.find('h1')
    title = title_tag.get_text(strip=True) if title_tag else "제목 없음"
    
    body_tag = soup.find('div', class_='cont_view', id='article_content')

    if body_tag:
        # 광고 div 제거 (필요 시 조건 추가)
        for ad_div in body_tag.find_all('div'):
            if ad_div.get('id') and ad_div['id'].startswith('svcad_'):
                ad_div.decompose()

        # 부수 요소 제거 (필요하면 더 추가 가능)
        for tag_to_remove in body_tag.find_all(['table', 'div'], class_=['gg_textshow']):
            tag_to_remove.decompose()

        # <br> 태그를 줄바꿈 문자로 대체
        for br in body_tag.find_all('br'):
            br.replace_with('\n')

        # 텍스트 추출 및 빈 줄 제거
        raw_text = body_tag.get_text(separator='\n', strip=True)
        body_lines = [line.strip() for line in raw_text.split('\n') if line.strip()]
        body = '\n'.join(body_lines)
        body = body.replace('\n', '').replace('\r', '')

    else:
        body = "본문 없음"

    return {
        "title": title,
        "url": url,
        "body": body,
        "media": "파이낸셜뉴스"
    }

## -----------------언론사 크롤러 코드 끝!!!! 여기까지 안 건드려도 돼요--------------------

kw_model = KeyBERT(model='distiluse-base-multilingual-cased')
# ✅ Supabase 저장 함수 (수정: 'test' 테이블, keyword 컬럼 추가)
def extract_keywords_with_scores(body, top_n=5):
    raw = kw_model.extract_keywords(body, top_n=top_n)
    return [{"keyword": kw, "score": round(score, 4)} for kw, score in raw]

# ✅ Supabase 저장 함수 수정: 'keywords' 포함
def save_to_supabase(data, query_keyword, log_path="save_log.txt"):
    try:
        existing = supabase.table("test").select("id").eq("url", data["url"]).eq("query_keyword", query_keyword).execute()
        if existing.data:
            print(f"⚠️ 이미 저장된 기사: {data['url']}")
            return False
        article_keywords = extract_keywords_with_scores(data["body"], top_n=5)
        record = data.copy()
        record["query_keyword"] = query_keyword
        record["article_keywords"] = article_keywords  # ✅ jsonb로 저장될 구조

        supabase.table("test").insert([record]).execute()
        print(f"✅ 저장 완료: {data['title']}")
        return True

    except Exception as e:
        print(f"❌ 저장 실패: {e}")
        return False


    except Exception as e:
        msg = f"❌ 저장 실패: {e}"
        print(msg)
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(msg + "\n")
        return False
# 언론사 도메인 → 크롤링 함수 매핑
CRAWLER_FUNCTION_MAP = {
    "www.yna.co.kr": crawl_yonhap_news,
    "www.newsis.com": crawl_newsis_news,
    "news.mt.co.kr" : crawl_mt_news,
    "biz.heraldcorp.com" : crawl_heraldcorp_news,
    "www.sedaily.com" : crawl_sedaily_news,
    "www.newspim.com" : crawl_newspim_news,
    "www.dailian.co.kr" : crawl_dailian_news,
    "www.mk.co.kr" : crawl_mk_news,
    "view.asiae.co.kr" : crawl_asiae_news,
    "www.nocutnews.co.kr" : crawl_nocut_news,
    "www.edaily.co.kr" : crawl_edaily_news,
    "www.kyeongin.com" : crawl_kyeongin_news,
    "www.seoul.co.kr" : crawl_seoul_news,
    "www.fnnews.com" : crawl_fn_news,
}

# 언론사 도메인 → 언론사 이름 매핑
MEDIA_NAME_MAP = {
    "www.yna.co.kr": "연합뉴스",
    "www.newsis.com": "뉴시스",
    "news.mt.co.kr" : "머니투데이",
    "biz.heraldcorp.com" : "헤럴드경제",
    "www.sedaily.com" : "서울경제",
    "www.newspim.com" : "뉴스핌",
    "www.dailian.co.kr" : "데일리안",
    "www.mk.co.kr" : "매일경제",
    "view.asiae.co.kr" : "아시아경제",
    "www.nocutnews.co.kr" : "노컷뉴스",
    "www.edaily.co.kr" : "이데일리뉴스",
    "www.kyeongin.com" : "경인일보",
    "www.seoul.co.kr" : "서울신문",
    "www.fnnews.com" : "파이낸셜뉴스",

    
}

from concurrent.futures import ThreadPoolExecutor, as_completed

def save_articles_from_naver_parallel(query, max_workers=10):  # 병렬처리 시도
    client_id = "_TznE38btYhyzWYsq9XK"
    client_secret = "06UYVlSHF9"

    encoded_query = urllib.parse.quote(query)
    headers = {
        "X-Naver-Client-Id": client_id,
        "X-Naver-Client-Secret": client_secret
    }

    display = 10
    saved_count_by_domain = {domain: 0 for domain in CRAWLER_FUNCTION_MAP.keys()}

    for start in range(1, 101, display):
        url = f"https://openapi.naver.com/v1/search/news.json?query={encoded_query}&display={display}&start={start}&sort=date"
        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            print(f"❌ 요청 실패 at start={start}: {response.status_code}")
            continue

        data = response.json()
        items = data.get("items", [])
        if not items:
            break

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = []

            for item in items:
                originallink = item.get("originallink", "")
                domain = urlparse(originallink).netloc

                if domain in CRAWLER_FUNCTION_MAP:
                    futures.append(executor.submit(CRAWLER_FUNCTION_MAP[domain], originallink))
                else:
                    continue

            for future in as_completed(futures):
                try:
                    article = future.result()
                except Exception as e:
                    print(f"❌ 크롤링 중 예외 발생: {e}")
                    continue

                if article:
                    success = save_to_supabase(article, query)
                    if success:
                        domain = urlparse(article["url"]).netloc
                        saved_count_by_domain[domain] += 1

        if len(items) < display:
            break

    # 1) 출력
    print("\n✅ 저장 요약")
    for domain, count in saved_count_by_domain.items():
        media = MEDIA_NAME_MAP.get(domain, domain)
        print(f"📰 {media} 기사 총 {count}건 Supabase test 테이블에 저장 완료")

    # 2) 텍스트 파일로 저장
    os.makedirs("log", exist_ok=True)

    filename = f"log/{query}_news_save_summary.txt"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(f"검색어: {query}\n\n")
        f.write("언론사별 저장 건수 요약:\n")
        for domain, count in saved_count_by_domain.items():
            media = MEDIA_NAME_MAP.get(domain, domain)
            f.write(f"{media}: {count}건\n")

    print(f"\n✅ 저장 요약을 '{filename}' 파일로 저장했습니다.")