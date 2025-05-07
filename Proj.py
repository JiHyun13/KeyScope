import requests

def summarize_article(article_text, api_key):
    url = "https://api.smmry.com"
    
    payload = {
        'SM_API_KEY': api_key,
        'sm_length': 5,  # 요약문 길이 (문장 수)
        'sm_with_break': True  # 문단 구분 포함
    }
    
    files = {
        'sm_api_input': (None, article_text)
    }
    
    try:
        response = requests.post(url, data=payload, files=files)
        result = response.json()
        return result.get("sm_api_content", "요약 실패")
    
    except Exception as e:
        return f"에러 발생: {e}"
