import requests
import os
import re
from dotenv import load_dotenv
from transformers import PreTrainedTokenizerFast

# 환경변수 로드
load_dotenv()

# API 설정
HF_API_URL = "https://api-inference.huggingface.co/models/eenzeenee/t5-base-korean-summarization"
HF_HEADERS = {
    "Authorization": f"Bearer {os.getenv('HF_API_TOKEN')}"
}

# Tokenizer 로드 (T5 기반 모델용)
tokenizer = PreTrainedTokenizerFast.from_pretrained("eenzeenee/t5-base-korean-summarization")
print("🔐 Loaded HF Token:", os.getenv("HF_API_TOKEN"))


# 🔹 텍스트 정리
def clean_text(text):
    text = re.sub(r"Copyright.*?무단 전재.*", "", text)
    text = re.sub(r"이 기사는 .*?GAM.*?프리미엄 기사입니다\.", "", text)
    text = re.sub(r'[“”"\'\']+', '"', text)
    text = re.sub(r'\.{3,}', '...', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


# 🔹 요약 대상 유효성 확인
def is_valid_for_summary(text):
    if not text or len(text.strip()) < 100:
        return False
    if text.count('.') + text.count('?') + text.count('!') < 2:
        return False
    return True


# 🔹 문장 수 기반 잘림
def trim_text_safe(text, max_chars=900, max_sentences=10):
    sentences = re.split(r'(?<=[.!?])\s+', text)
    trimmed = ''
    count = 0
    for sentence in sentences:
        if count >= max_sentences or len(trimmed) + len(sentence) > max_chars:
            break
        trimmed += sentence + ' '
        count += 1
    if not trimmed and sentences:
        trimmed = sentences[0]
    return trimmed.strip()


# 🔹 Tokenizer 기반 잘림
def trim_by_token_count(text, max_tokens=950):
    tokens = tokenizer.encode(text, truncation=True, max_length=max_tokens, return_tensors=None)
    decoded = tokenizer.decode(tokens, skip_special_tokens=True)
    return decoded.strip()


# 🔹 요약 함수
def summarize(text):
    if isinstance(text, dict):
        return {"error": "❌ 요약 대상이 문자열이 아닌 dict입니다. text 필드를 확인하세요."}

    text = clean_text(text)

    if not is_valid_for_summary(text):
        return {"error": "⚠️ 기사 내용이 짧거나 요약이 불가능합니다."}

    print(f"[🔍 요약 요청 전] 최종 요청 길이: {len(text)}자 / 문장 수: {text.count('.') + text.count('?') + text.count('!')}")

    if len(text) > 900 or text.count('.') + text.count('?') + text.count('!') > 15:
        print("✂️ 요약 전에 자르기 적용")
        text = trim_text_safe(text, max_chars=900, max_sentences=10)
        print(f"[✂️ 잘림 후] 길이: {len(text)}자 / 문장 수: {text.count('.') + text.count('?') + text.count('!')}")

    text = trim_by_token_count(text, max_tokens=950)
    print(f"[🧠 Token 기반 자르기 적용 후 길이] {len(text)}자")
    print("[🧾 요약 본문 미리보기]:", text[:150], "...")

    try:
        response = requests.post(
            HF_API_URL,
            headers=HF_HEADERS,
            json={
                "inputs": text,
                "parameters": {
                    "max_length": 130,
                    "min_length": 30,
                    "do_sample": False
                }
            }
        )
    except Exception as e:
        return {"error": f"요약 요청 중 오류 발생: {str(e)}"}

    if response.status_code == 200:
        try:
            result = response.json()
            if isinstance(result, list) and len(result) > 0:
                summary_text = result[0].get("summary_text", "").strip()

                if len(summary_text) < 30 or not re.search(r'[가-힣]', summary_text):
                    return {"error": "요약 실패: 의미 없는 응답을 받았습니다. 모델 상태가 불안정할 수 있습니다."}

                if "CNN.com" in summary_text or "iReporter" in summary_text:
                    return {"error": "요약 실패: 모델이 잘못된 응답을 반환했습니다. 다시 시도해 주세요."}

                return {"summary": summary_text}
            elif isinstance(result, dict) and "summary_text" in result:
                return {"summary": result["summary_text"].strip()}
            else:
                return {"error": f"예상치 못한 요약 응답 형식입니다: {result}"}
        except Exception as e:
            return {"error": f"요약 응답 파싱 오류: {str(e)}"}

    else:
        return {
            "error": f"요약 실패: {response.status_code} / {response.text}",
            "hint": "❗ 입력이 너무 길거나, API Token 문제일 수 있습니다."
        }
