import streamlit as st
import google.generativeai as genai
import json
import os

# =========================================================
# 🚨 API 키 설정 (따옴표 안에 키를 붙여넣으세요)
# =========================================================
FIXED_API_KEY = "AIzaSyCqYWVqV_JPC6hVJNTx7N68B2MEtXbDa4g"

# =========================================================
# 1. 화면 설정 (모바일 최적화)
# =========================================================
st.set_page_config(page_title="Life-Link Mobile", page_icon="📘", layout="centered")

st.markdown("""
    <style>
    .stButton > button {
        width: 100%;
        padding-top: 15px;
        padding-bottom: 15px;
        font-weight: bold;
        font-size: 18px;
    }
    .card { 
        background-color: white; 
        padding: 20px; 
        border-radius: 15px; 
        box-shadow: 0 2px 5px rgba(0,0,0,0.1); 
        margin-bottom: 15px; 
        border: 1px solid #eee;
    }
    </style>
""", unsafe_allow_html=True)

# =========================================================
# 2. 로직 및 UI
# =========================================================
st.title("📘 Life-Link")
st.caption("당신의 경험을 도서관의 책으로 만들어드립니다.")

# API 키 처리
if FIXED_API_KEY and FIXED_API_KEY != "여기에_API_키를_붙여넣으세요":
    api_key = FIXED_API_KEY
else:
    # Streamlit Cloud Secret이나 입력창에서 키 찾기
    if "GEMINI_API_KEY" in st.secrets:
        api_key = st.secrets["GEMINI_API_KEY"]
    else:
        api_key = st.text_input("API Key 입력", type="password")

def analyze_story(api_key, text):
    try:
        # 표준 라이브러리 설정
        genai.configure(api_key=api_key)
        
        # 가장 안정적인 모델 선택 (1.5 Flash)
        model = genai.GenerativeModel(
            model_name="gemini-3-flash-preview", 
            generation_config={"response_mime_type": "application/json"}
        )
        
        prompt = f"""
        당신은 도서관 사서입니다. 사용자의 경험: "{text}"
        이 경험을 바탕으로 멘토링 역할과 추천 도서를 JSON으로 기획해주세요.
        형식: {{ "summary": "한줄요약", "keywords": ["#키워드"], "role": "역할명", "books": [{{"title": "제목", "author": "저자", "reason": "이유"}}] }}
        """
        
        response = model.generate_content(prompt)
        
        if not response.text:
             return {"error": "AI 응답이 없습니다."}
             
        return json.loads(response.text)
        
    except Exception as e:
        return {"error": str(e)}

story_input = st.text_area("나의 경험을 적어주세요", height=120)

if st.button("✨ 내 역할 찾기"):
    if not api_key:
        st.error("API 키가 필요합니다.")
    elif not story_input:
        st.warning("내용을 입력해주세요.")
    else:
        with st.spinner("분석 중..."):
            result = analyze_story(api_key, story_input)
            
        if "error" in result:
            st.error("오류가 발생했습니다.")
            st.info("API 키를 확인하거나 잠시 후 다시 시도해주세요.")
            st.code(result['error'])
        else:
            st.divider()
            st.markdown(f"""
            <div class="card">
                <h3>🏷️ {result.get('role', '멘토')}</h3>
                <p>{result.get('summary', '')}</p>
                <p style="color:#2E86C1; font-weight:bold;">{' '.join(result.get('keywords', []))}</p>
            </div>
            """, unsafe_allow_html=True)
            
            for book in result.get('books', []):
                st.markdown(f"""
                <div class="card" style="background-color:#f8f9fa">
                    <b>📖 {book.get('title')}</b> <small>({book.get('author')})</small><br>
                    <span style="color:#555">{book.get('reason')}</span>
                </div>
                """, unsafe_allow_html=True)
