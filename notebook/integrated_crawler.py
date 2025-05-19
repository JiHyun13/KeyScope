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

# ✅ 연합뉴스 크롤링 함수
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

# ✅ 조선일보 크롤링 함수
def crawl_chosun_news(url):
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.get(url)
    time.sleep(3)

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    driver.quit()

    title_tag = soup.find('h1')
    title = title_tag.get_text(strip=True) if title_tag else "제목 없음"

    body_paragraphs = soup.select('p.article-body__content.article-body__content-text')
    body_lines = []
    for p in body_paragraphs:
        text = p.get_text(strip=True)
        if not text:
            continue
        if any(keyword in text for keyword in ['기자', '무단 전재', '구독', 'Copyright']):
            continue
        body_lines.append(text)
    body = '\n'.join(body_lines) if body_lines else "본문 없음"

    return {"title": title, "url": url, "body": body, "media": "조선일보"}

# ✅ 뉴시스 크롤링 함수
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


def crawl_news1_news(url):
    # ✅ 셀레니움 옵션 설정
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')  # 창 없이 실행
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')

    # ✅ 드라이버 실행
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.get(url)

    # ✅ 명시적 대기: 본문이 로딩될 때까지 최대 10초 대기
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "articleBodyContent"))
        )
    except:
        print("⏰ 로딩 실패 또는 타임아웃 발생")
        driver.quit()
        return None

    # ✅ 페이지 파싱
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    driver.quit()

    # ✅ 제목 추출
    title_tag = soup.select_one('h1.article-h2-header-title.mb-40')
    title = title_tag.get_text(strip=True) if title_tag else "제목 없음"

    # ✅ 본문 추출
    body_tag = soup.find('div', id='articleBodyContent')
    if body_tag:
        paragraphs = body_tag.find_all('p')
        body_lines = [p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True)]
        body = '\n'.join(body_lines)
    else:
        body = "본문 없음"

    return {
        "title": title,
        "url": url,
        "body": body,
        "media": "뉴스1"
    }
    
# ✅ 머니투데이 뉴스 크롤링 함수
def crawl_mt_news(url):
    headers = {
        'User-Agent': 'Mozilla/5.0'
    }

    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print("❌ 기사 요청 실패:", response.status_code)
        return None

    soup = BeautifulSoup(response.text, 'html.parser')

    # 제목 추출
    title_tag = soup.find('h1', class_=['subject'])
    title = title_tag.get_text(strip=True) if title_tag else "제목 없음"

    # 본문 추출 (p 태그 중에서 저작권 정보 제외)
    # 'view_text' 클래스를 가진 div를 찾음 (본문 전체 영역)
    body_tag = soup.find('div', class_='view_text')

    if body_tag:
    # 본문 텍스트만 추출 (줄바꿈 기준 분리)
        raw_text = body_tag.get_text(separator="\n").strip()

    # 각 줄의 공백 제거 및 빈 줄 제거
        body_lines = [line.strip() for line in raw_text.split("\n") if line.strip()]

    # 다시 줄바꿈 문자로 합침
        body = '\n'.join(body_lines)
    else:
        body = "본문 없음"

    return {
        "title": title,
        "url": url,
        "body": body,
        "media": "머니투데이"
    }

# ✅ 헤럴드경제 크롤링 함수
def crawl_heraldcorp_news(url):
    headers = {
        'User-Agent': 'Mozilla/5.0'
    }

    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print("❌ 기사 요청 실패:", response.status_code)
        return None

    soup = BeautifulSoup(response.text, 'html.parser')

    # 제목 추출
    title = soup.select_one('div.news_title > h1')
    title = title.get_text(strip=True) if title else "제목 없음"

    # 본문 추출 (p 태그 중에서 저작권 정보 제외)
    # 'view_text' 클래스를 가진 div를 찾음 (본문 전체 영역)
    body_tag = soup.find('article', id='articleText')

    if body_tag:
        # article 안의 모든 p 태그 텍스트를 줄바꿈 기준으로 합침
        raw_text = "\n".join([p.get_text(strip=True) for p in body_tag.find_all('p')]).strip()

        # 각 줄의 공백 제거 및 빈 줄 제거
        body_lines = [line.strip() for line in raw_text.split("\n") if line.strip()]

        # 다시 줄바꿈 문자로 합침
        body = '\n'.join(body_lines)
    else:
        body = "본문 없음"

    return {
        "title": title,
        "url": url,
        "body": body,
        "media": "헤럴드경제"
    }


# ✅ 서울경제 크롤링 함수
def crawl_sedaily_news(url):
    headers = {
        'User-Agent': 'Mozilla/5.0'
    }

    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print("❌ 기사 요청 실패:", response.status_code)
        return None

    soup = BeautifulSoup(response.text, 'html.parser')

    # 제목 추출
    title_tag = soup.find('h1', class_=['art_tit'])
    title = title_tag.get_text(strip=True) if title_tag else "제목 없음"

    # 본문 추출 (p 태그 중에서 저작권 정보 제외)
    # 'view_text' 클래스를 가진 div를 찾음 (본문 전체 영역)
    body_tag = soup.find('div', class_='article_view')

    if body_tag:
    # figure 태그 제거 (caption 포함)
        for fig in body_tag.find_all('figure', class_='art_photo'):
            fig.decompose()  # 해당 태그 및 하위 내용 완전 삭제

    # <br> 태그를 '\n'으로 변환
        for br in body_tag.find_all('br'):
            br.replace_with('\n')

    # 텍스트 추출 후 strip
        raw_text = body_tag.get_text(separator="\n").strip()

    # 공백 줄 제거
        body_lines = [line.strip() for line in raw_text.split("\n") if line.strip()]

    # 다시 줄바꿈으로 합침
        body = '\n'.join(body_lines)
    else:
        body = "본문 없음"

    return {
        "title": title,
        "url": url,
        "body": body,
        "media": "서울경제"
    }

# ✅ 뉴스핌 크롤링 함수
def crawl_newspim_news(url):
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

    body_tag = soup.find('div', class_='contents', itemprop='articleBody')

    if body_tag:
        # articleBody 내 모든 p 태그 텍스트를 줄바꿈 기준으로 합침
        raw_text = "\n".join([p.get_text(strip=True) for p in body_tag.find_all('p')]).strip()

        # 각 줄 공백 제거 및 빈 줄 제거
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


# ✅ 데일리안 크롤링 함수
def crawl_dailian_news(url):
    headers = {
        'User-Agent': 'Mozilla/5.0'
    }

    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print("❌ 기사 요청 실패:", response.status_code)
        return None

    soup = BeautifulSoup(response.text, 'html.parser')

    # 제목 추출
    title_tag = soup.find('h1', class_=['title'])
    title = title_tag.get_text(strip=True) if title_tag else "제목 없음"

    body_tag = soup.find('div', class_='article')

    if body_tag:
        # articleBody 내 모든 p 태그 텍스트를 줄바꿈 기준으로 합침
        raw_text = "\n".join([p.get_text(strip=True) for p in body_tag.find_all('p')]).strip()

        # 각 줄 공백 제거 및 빈 줄 제거
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

# ✅ 매일경제 크롤링 함수
def crawl_mk_news(url):
    headers = {
        'User-Agent': 'Mozilla/5.0'
    }

    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print("❌ 기사 요청 실패:", response.status_code)
        return None

    soup = BeautifulSoup(response.text, 'html.parser')

    # 제목 추출
    title_tag = soup.find('h2', class_=['news_ttl'])
    title = title_tag.get_text(strip=True) if title_tag else "제목 없음"
    
    body_tag = soup.find('div', class_='news_cnt_detail_wrap', itemprop='articleBody')

    if body_tag:
        p_texts = [p.get_text(strip=True) for p in body_tag.find_all('p')]
        p_texts = [text for text in p_texts if text]

        if p_texts:
            body = ''.join(p_texts)
        else:
            # p 태그 없거나 빈 경우 br 기준 텍스트 노드 추출
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

# ✅ 아시아경제 크롤링 함수
def crawl_asiae_news(url):
    headers = {
        'User-Agent': 'Mozilla/5.0'
    }

    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print("❌ 기사 요청 실패:", response.status_code)
        return None

    soup = BeautifulSoup(response.text, 'html.parser')

    # 제목 추출
    title_tag = soup.find('h1')  # 그냥 첫 번째 h1 태그 찾기
    title = title_tag.get_text(strip=True) if title_tag else "제목 없음"
    
    body_tag = soup.find('div', class_='article')

    if body_tag:
        # class가 txt_prohibition인 p 태그는 제외하고 텍스트 추출
        p_tags = [p for p in body_tag.find_all('p') if 'txt_prohibition' not in p.get('class', [])]

        raw_text = "\n".join([p.get_text(strip=True) for p in p_tags]).strip()

        # 각 줄 공백 제거 및 빈 줄 제거
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


# ✅ Supabase 저장 함수
def save_to_supabase(data):
    try:
        existing = supabase.table("articles").select("id").eq("url", data["url"]).execute()
        if existing.data:
            print("⚠️ 이미 저장된 기사:", data["url"])
            return False
        supabase.table("articles").insert([data]).execute()
        print("✅ 저장 완료:", data['title'])
        return True
    except Exception as e:
        print("❌ 저장 실패:", e)
        return False

# ✅ 언론사 도메인 → 크롤링 함수 매핑
CRAWLER_FUNCTION_MAP = {
    "www.yna.co.kr": crawl_yonhap_news,
    "www.chosun.com": crawl_chosun_news,
    "www.newsis.com": crawl_newsis_news,
    "www.news1.kr" : crawl_news1_news,
    "news.mt.co.kr" : crawl_mt_news,
    "biz.heraldcorp.com" : crawl_heraldcorp_news,
    "www.sedaily.com" : crawl_sedaily_news,
    "www.newspim.com" : crawl_newspim_news,
    "www.dailian.co.kr" : crawl_dailian_news,
    "www.mk.co.kr" : crawl_mk_news,
    "view.asiae.co.kr" : crawl_asiae_news,
    "www.khan.co.kr" : crawl_khan_news,
    
    
}

# ✅ 언론사 도메인 → 언론사 이름 매핑
MEDIA_NAME_MAP = {
    "www.yna.co.kr": "연합뉴스",
    "www.chosun.com": "조선일보",
    "www.newsis.com": "뉴시스",
    "www.news1.kr" : "뉴스1",
    "news.mt.co.kr" : "머니투데이",
    "biz.heraldcorp.com" : "헤럴드경제",
    "www.sedaily.com" : "서울경제",
    "www.newspim.com" : "뉴스핌",
    "www.dailian.co.kr" : "데일리안",
    "www.mk.co.kr" : "매일경제",
    "view.asiae.co.kr" : "아시아경제",
    "www.khan.co.kr" : "경향신문",
    
    
}

# ✅ 네이버 뉴스 수집 및 저장
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
                    success = save_to_supabase(article)
                    if success:
                        saved_count_by_domain[domain] += 1

        if len(items) < display:
            break

    # ✅ 최종 결과 출력
    print("\n✅ 저장 요약")
    for domain, count in saved_count_by_domain.items():
        media = MEDIA_NAME_MAP.get(domain, domain)
        print(f"📰 {media} 기사 총 {count}건 Supabase에 저장 완료")

# ✅ 실행
save_articles_from_naver("딥페이크")
