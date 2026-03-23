import os
import google.generativeai as genai

# 환경변수에서 API 키를 읽어옵니다. 
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

# 요약 모델 
summary_model = genai.GenerativeModel("gemini-1.5-flash")

def summarize_filing(ticker: str, form_type: str, content: str) -> str:
    """
    공시 원문을 바탕으로 3줄 요약을 생성합니다.
    """
    if not content or len(content.strip()) == 0:
        return "본문 내용을 가져올 수 없어 요약할 수 없습니다."
        
    prompt = f"""
    당신은 투자자에게 SEC 공시를 실시간으로 브리핑하는 전문 분석가입니다. 
    다음 {ticker}의 {form_type} 공시를 분석하여 아래 JSON 형식으로만 응답하세요.

    [지침]
    1. 정확성: 공시의 핵심 숫자와 주체를 정확히 명시.
    2. 가독성: 억지로 줄이지 말고, 자연스럽고 깔끔한 문장으로 작성.
    3. 태그: "급등신호", "호재", "중립", "악재", "위험" 중 하나를 선택.
    4. 내용 구성: 공시 발생 원인, 결정 사항, 재무적 파급 효과, 향후 전망, 투자자 주의사항 및 리스크를 종합하여 작성하세요. ('핵심 요약:', '영향 분석:' 같은 인위적인 소제목 양식은 제외하고 자연스러운 글이나 불릿 포인트로 작성할 것)
    5. 출력은 반드시 순수 JSON 문자열만 출력해야 하며, 마크다운(```)이나 추가 설명은 제외하세요.

    [JSON 출력 양식]
    {{
    "thread_title": "{ticker}: [자연스러운 한 줄 요약] [태그]",
    "summary": "[공시에 대한 상세 분석 내용을 여기에 작성. 줄바꿈은 \\n 사용]"
    }}

    [공시 원문 시작]
    {content[:100000]}
    [공시 원문 끝]
    """
    try:
        response = summary_model.generate_content(prompt)
        text = response.text.strip()
        if text.startswith("```json"):
            text = text[7:]
        elif text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        return text.strip()
    except Exception as e:
        print(f"[Gemini] Error summarizing filing: {e}")
        return '{{"thread_title": "요약 생성 오류", "summary": "요약 생성 중 오류가 발생했습니다."}}'

def answer_question(ticker: str, form_type: str, content: str, history: list, question: str) -> str:
    """
    쓰레드의 대화 기록(history)과 공시 원문(content)을 바탕으로 질문에 답변합니다.
    history 포맷: [{"role": "user"|"model", "parts": "message"}]
    """
    if not content or len(content.strip()) == 0:
        return '{"is_related": true, "answer": "본문 내용이 없어 질문에 답변할 수 없습니다."}'

    chat = summary_model.start_chat(history=history)
    
    prompt = f"""
당신은 미국 주식 SEC 공시 분석 전문가입니다.
종목명: {ticker}
공시 종류: {form_type}

[지침]
1. 사용자의 질문이 현재 종목({ticker}) 및 제공된 공시 내용과 관련이 있는지 평가하여, 관련이 있다면 true, 무관한 질문(예: 다른 주식, 일상 대화 등)이라면 false로 설정하세요.
2. 관련이 있다면 사용자 질문에 한국어로 친절하고 정확하게 답변을 작성하세요.
3. 관련이 없다면 짧게 "해당 주식 및 공시와 무관한 질문입니다."라고 작성하세요.
4. 반드시 아래 JSON 형식으로만 응답하세요. 마크다운(```)은 제외하세요.

[JSON 출력 양식]
{{
  "is_related": true,
  "answer": "답변 내용..."
}}

[공시 내용 일부]
{content[:50000]} 

[사용자 질문]
{question}
"""
    try:
        response = chat.send_message(prompt)
        text = response.text.strip()
        if text.startswith("```json"):
            text = text[7:]
        elif text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        return text.strip()
    except Exception as e:
        print(f"[Gemini] Error answering question: {e}")
        return '{{"is_related": true, "answer": "답변 생성 중 오류가 발생했습니다."}}'
