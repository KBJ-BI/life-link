import streamlit as st
import google.generativeai as genai
import json
import time

# =========================================================
# ⚙️ 설정 및 API 키
# =========================================================
# 여기에 본인의 API 키를 입력하세요
FIXED_API_KEY = "여기에_API_키를_붙여넣으세요"

st.set_page_config(
    page_title="Life-Link | 당신의 경험이 책이 됩니다",
    page_icon="📘",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# =========================================================
# 🎨 UI 디자인 (HTML 스타일 적용)
# =========================================================
st.markdown("""
    <style>
    @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');
    
    .stApp {
        background-color: #f4f7f6;
        font-family: 'Pretendard', sans-serif;
    }
    
    /* 카드 스타일 */
    .custom-card {
        background: white;
        border-radius: 16px;
        padding: 20px;
        margin-bottom: 15px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        border: 1px solid #eee;
    }
    
    .card-header {
        border-bottom: 1px solid #f0f0f0;
        padding-bottom: 10px;
        margin-bottom: 15px;
        font-weight: bold;
        color: #333;
        display: flex;
        justify-content: space-between;
    }

    /* 책 리스트 스타일 */
    .book-item {
        display: flex;
        gap: 15px;
        padding: 12px;
        background: #f9f9f9;
        border-radius: 8px;
        margin-bottom: 8px;
        align-items: center;
    }
    
    .badge {
        background: #E0F2F1;
        color: #00695C;
        padding: 4px 8px;
        border-radius: 4px;
        font-size: 0.8rem;
    }
    
    /* 버튼 스타일 */
    .stButton > button {
        width: 100%;
        background-color: #4A90E2;
        color: white;
        border: none;
        padding: 15px;
        border-radius: 12px;
        font-weight: bold;
    }
    .stButton > button:hover {
        background-color: #357ABD;
        color: white;
    }
    </style>
""", unsafe_allow_html=True)

# =========================================================
# 🧠 AI 분석 로직 (오류 방지 강화)
# =========================================================
def analyze_with_ai(api_key, text):
    try:
        genai.configure(api_key=api_key)
        
        # 🚨 [핵심 수정] 안전 설정: AI가 답변을 거부하지 않도록 필터 해제
        safety_settings = [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
        ]

        model = genai.GenerativeModel(
            model_name="gemini-3-flash-preview",
            generation_config={"response_mime_type": "application/json"},
            safety_settings=safety_settings
        )

        prompt = f"""
        당신은 도서관 휴먼북 기획자입니다. 
        사용자의 경험: "{text}"
        
        이 내용을 분석하여 다음 JSON 형식으로 응답해주세요.
        {{
            "summary": "경험을 따뜻하게 칭찬하는 요약",
            "keywords": ["#키워드1", "#키워드2"],
            "role": "창의적인 멘토링 프로그램 명",
            "books": [
                {{"title": "책제목1", "author": "저자1"}},
                {{"title": "책제목2", "author": "저자2"}}
            ]
        }}
        """
        
        response = model.generate_content(prompt)
        
        # 🚨 [핵심 수정] 빈 응답 체크 (NoneType 에러 방지)
        if response.text:
            return json.loads(response.text)
        else:
            return {"error": "AI가 응답을 생성하지 못했습니다. 내용을 조금 더 자세히 적어주세요."}
            
    except Exception as e:
        return {"error": f"분석 중 오류가 발생했습니다: {str(e)}"}

# =========================================================
# 📱 메인 앱 화면
# =========================================================

# 헤더
st.markdown("""
    <div style="display:flex; justify-content:space-between; align-items:center; background:white; padding:15px; border-radius:12px; margin-bottom:20px; box-shadow:0 2px 5px rgba(0,0,0,0.05);">
        <div style="font-size:1.5rem; font-weight:800; color:#4A90E2;">Life-Link</div>
        <div style="background:#FFF8E1; color:#F57F17; padding:5px 12px; border-radius:20px; font-weight:bold;">🪙 0 Lib</div>
    </div>
    <div style="text-align:center; margin-bottom:30px;">
        <h3>당신의 경험을 기록하세요</h3>
        <p style="color:#666;">AI가 당신의 이야기를 듣고<br>세상에 하나뿐인 <b>휴먼북</b>으로 만들어 드립니다.</p>
    </div>
""", unsafe_allow_html=True)

# API 키 및 입력
if FIXED_API_KEY and FIXED_API_KEY != "여기에_API_키를_붙여넣으세요":
    api_key = FIXED_API_KEY
else:
    if "GEMINI_API_KEY" in st.secrets:
        api_key = st.secrets["GEMINI_API_KEY"]
    else:
        api_key = st.text_input("🔑 API Key 입력", type="password")

story_input = st.text_area("나의 이야기", height=150, placeholder="예시: 30년간 선생님으로 일하며 아이들과 소통하는 것을 좋아했습니다.")

if st.button("🎙️ AI 자서전 만들기"):
    if not api_key:
        st.error("API 키가 필요합니다.")
    elif len(story_input) < 5:
        st.warning("내용을 조금 더 적어주세요.")
    else:
        with st.spinner("AI가 분석 중입니다..."):
            result = analyze_with_ai(api_key, story_input)
            time.sleep(1) 

        if result and "error" not in result:
            # 결과 화면 출력
            
            # 1. 프로필 카드
            keywords_html = " ".join([f"<span>{k}</span>" for k in result.get('keywords', [])])
            st.markdown(f"""
            <div class="custom-card">
                <div class="card-header">
                    <span>🤖 AI 분석 리포트</span>
                    <span class="badge">분석완료</span>
                </div>
                <div style="display:flex; align-items:center; gap:15px; margin-bottom:10px;">
                    <div style="font-size:2.5rem;">👴</div>
                    <div>
                        <h4 style="margin:0;">김라이프 님</h4>
                        <p style="margin:5px 0; color:#4A90E2; font-weight:bold;">{keywords_html}</p>
                    </div>
                </div>
                <p style="color:#555; line-height:1.6;">{result.get('summary')}</p>
            </div>
            """, unsafe_allow_html=True)

            # 2. 역할 카드
            st.markdown(f"""
            <div class="custom-card" style="border-left: 5px solid #50E3C2;">
                <div class="card-header"><span>✨ 맞춤형 활동 제안</span></div>
                <p>보유하신 재능을 살려 활동해보세요!</p>
                <div style="background:#E0F2F1; padding:15px; border-radius:8px; margin-top:10px; color:#00695C; font-weight:bold;">
                    추천 역할: {result.get('role')}
                </div>
            </div>
            """, unsafe_allow_html=True)

            # 3. 책 추천 카드 (🚨 HTML 깨짐 수정 완료 부분)
            books_html_list = ""
            for book in result.get('books', []):
                books_html_list += f"""
                <div class="book-item">
                    <div style="font-size:1.5rem;">📖</div>
                    <div>
                        <div style="font-weight:bold;">{book.get('title')}</div>
                        <div style="font-size:0.8rem; color:#888;">{book.get('author')} 저</div>
                    </div>
                </div>
                """
            
            # HTML을 합쳐서 한 번에 렌더링 (unsafe_allow_html=True 필수)
            st.markdown(f"""
            <div class="custom-card">
                <div class="card-header"><span>📚 함께 읽으면 좋은 책</span></div>
                {books_html_list}
            </div>
            """, unsafe_allow_html=True)
            
            st.success("🎉 분석 완료! 코인이 지급되었습니다.")
            st.balloons()

        elif result and "error" in result:
            st.error(result["error"])
