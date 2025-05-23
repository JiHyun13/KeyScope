import requests
import urllib.parse
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from supabase import create_client, Client
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time

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

## -----------------언론사 크롤러 코드 끝!!!! 여기까지 안 건드려도 돼요--------------------


# ✅ Supabase 저장 함수 (수정: 'test' 테이블, keyword 컬럼 추가)
def save_to_supabase(data, keyword):
    try:
        # url과 keyword가 같은 데이터가 이미 있는지 확인
        existing = supabase.table("test").select("id").eq("url", data["url"]).eq("keyword", keyword).execute()
        if existing.data:
            print("⚠️ 이미 저장된 기사:", data["url"])
            return False

        data_with_keyword = data.copy()
        data_with_keyword["keyword"] = keyword

        supabase.table("test").insert([data_with_keyword]).execute()
        print("✅ 저장 완료:", data["title"])
        return True
    except Exception as e:
        print("❌ 저장 실패:", e)
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
}

# 네이버 뉴스 수집 및 저장 (수정: keyword 인자 사용)
def save_articles_from_naver(query):
    client_id = "_TznE38btYhyzWYsq9XK"
    client_secret = "06UYVlSHF9"

    encoded_query = urllib.parse.quote(query)
    headers = {
        "X-Naver-Client-Id": client_id,
        "X-Naver-Client-Secret": client_secret
    }

    display = 100
    saved_count_by_domain = {domain: 0 for domain in CRAWLER_FUNCTION_MAP.keys()}

    for start in range(1, 1000 + 1, display):
        url = f"https://openapi.naver.com/v1/search/news.json?query={encoded_query}&display={display}&start={start}&sort=date"
        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            print(f"❌ 요청 실패 at start={start}: {response.status_code}")
            continue

        data = response.json()
        items = data.get("items", [])
        if not items:
            break

        for item in items:
            originallink = item.get("originallink", "")
            domain = urlparse(originallink).netloc

            if domain in CRAWLER_FUNCTION_MAP:
                article = CRAWLER_FUNCTION_MAP[domain](originallink)
                if article:
                    success = save_to_supabase(article, query)
                    if success:
                        saved_count_by_domain[domain] += 1

        if len(items) < display:
            break

    print("\n✅ 저장 요약")
    for domain, count in saved_count_by_domain.items():
        media = MEDIA_NAME_MAP.get(domain, domain)
        print(f"📰 {media} 기사 총 {count}건 Supabase test 테이블에 저장 완료")


# main 실행부 (input으로 검색어 받음)
if __name__ == "__main__":
    search_keyword = input("검색어를 입력하세요: ").strip()
    if search_keyword:
        save_articles_from_naver(search_keyword)
    else:
        print("검색어가 입력되지 않았습니다.")
