import streamlit as st
from google import genai
from google.genai import types  # 공식 문서 권장: 타입 설정을 위한 모듈
import json

# =========================================================
# 🚨 [설정] API 키 입력 (이곳에 키를 붙여넣으세요)
# =========================================================
FIXED_API_KEY = "AIzaSyCqYWVqV_JPC6hVJNTx7N68B2MEtXbDa4g"

# =========================================================
# 1. 화면 기본 설정
# =========================================================
st.set_page_config(page_title="Life-Link | AI 휴먼북", page_icon="📘", layout="wide")

st.markdown("""
    <style>
    .card { 
        background-color: white; 
        padding: 25px; 
        border-radius: 15px; 
        box-shadow: 0 4px 6px rgba(0,0,0,0.1); 
        margin-bottom: 20px; 
        border: 1px solid #f0f2f6;
    }
    .highlight { color: #4A90E2; font-weight: bold; }
    .role-title { color: #2E86C1; font-size: 1.5em; font-weight: bold; margin-bottom: 10px; }
    .book-card { background-color: #f8f9fa; padding: 15px; border-radius: 10px; margin-bottom: 10px; }
    </style>
""", unsafe_allow_html=True)

# =========================================================
# 2. 사이드바 설정
# =========================================================
with st.sidebar:
    st.title("📘 Life-Link")
    st.markdown("### 사람과 삶을 잇는\n### 도서관 휴먼북 플랫폼")
    st.divider()
    
    # API 키 처리 로직
    if FIXED_API_KEY and FIXED_API_KEY != "여기에_API_키를_붙여넣으세요":
        api_key = FIXED_API_KEY
        st.success("✅ API 키가 로드되었습니다.")
    else:
        api_key = st.text_input("Gemini API Key", type="password")
    
    st.info("**💡 사용 모델:** gemini-1.5-flash (안정적인 정식 버전)")

# =========================================================
# 3. AI 분석 함수 (Google Gen AI SDK 공식 표준)
# =========================================================
def analyze_life_link(api_key, text):
    try:
        # [Migration Guide] 1. 클라이언트 생성 (Client 방식)
        client = genai.Client(api_key=api_key)
        
        sys_prompt = """
        당신은 도서관의 '휴먼북(사람책)'을 기획하는 따뜻하고 통찰력 있는 사서입니다.
        사용자의 경험을 분석하여, 이웃에게 지혜를 나눠줄 수 있는 멋진 멘토링 역할을 부여해주세요.
        
        [필수 요구사항]
        1. 말투: 존중하고 격려하는 따뜻한 '해요'체 사용.
        2. 역할(Role)명: 창의적이고 직관적인 이름 (예: '동네 골목대장' -> '골목 놀이 큐레이터')
        3. 출력: 반드시 JSON 형식만 출력.
        """

        user_prompt = f"""
        사용자 경험: "{text}"
        
        위 내용을 분석하여 아래 JSON 스키마에 맞춰 답해주세요.
        {{
            "summary": "경험을 칭찬하는 따뜻한 한 줄 요약",
            "keywords": ["#키워드1", "#키워드2", "#키워드3"],
            "role": "도서관에서 진행할 멘토링 프로그램 명",
            "books": [
                {{"title": "책제목", "author": "저자", "reason": "추천 이유"}}
            ]
        }}
        """

        # [Migration Guide] 2. 콘텐츠 생성 호출
        # - model: 'gemini-1.5-flash' (429 오류 해결을 위해 안정적인 모델 사용)
        # - config: types.GenerateContentConfig 사용 (공식 권장 설정 방식)
        response = client.models.generate_content(
            model="gemini-3-flash-preview", 
            contents=sys_prompt + "\n" + user_prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",  # JSON 응답 강제
                temperature=0.7
            )
        )
        
        # [Migration Guide] 3. 응답 처리
        if not response.text:
            return {"error": "AI 응답이 비어있습니다."}
            
        return json.loads(response.text)

    except Exception as e:
        # 에러 메시지 반환
        return {"error": str(e)}

# =========================================================
# 4. 메인 화면 로직
# =========================================================
st.title("당신의 경험이 누군가에게는 길이 됩니다 🛤️")
st.markdown("##### 사소한 경험이라도 좋습니다. 당신의 이야기를 들려주세요.")

story_input = st.text_area("나의 경험 입력", height=150, 
    placeholder="예) 30년간 초등학교 선생님으로 일하며 아이들과 텃밭을 가꾸는 것을 좋아했습니다. 은퇴 후에는..."
)

if st.button("✨ 나의 '휴먼북' 역할 찾기", type="primary"):
    if not api_key:
        st.error("API 키가 없습니다. 코드 상단에 키를 입력해주세요.")
    elif not story_input:
        st.warning("경험을 입력해주세요!")
    else:
        with st.spinner("🔍 AI 사서가 당신의 경험을 분석 중입니다..."):
            result = analyze_life_link(api_key, story_input)

        if "error" in result:
            st.error(f"오류가 발생했습니다: {result['error']}")
            if "429" in str(result['error']):
                st.warning("⚠️ 사용량이 많아 일시적으로 제한되었습니다. 잠시 후 다시 시도해주세요.")
        else:
            # 결과 화면 출력
            st.divider()
            col1, col2 = st.columns([1, 1.2])
            
            with col1:
                st.subheader("👤 당신을 위한 휴먼북 프로필")
                st.markdown(f"""
                <div class="card">
                    <p style="font-size:1.1em; color:#555;">{result.get('summary', '')}</p>
                    <div class="role-title">🏷️ {result.get('role', '멋진 멘토')}</div>
                    <p class="highlight">{'   '.join(result.get('keywords', []))}</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.subheader("📚 함께 읽으면 좋은 추천 도서")
                for book in result.get('books', []):
                    st.markdown(f"""
                    <div class="book-card">
                        <b>📖 {book.get('title')}</b> <span style='font-size:0.8em'>({book.get('author')})</span>
                        <br><span style="font-size:0.9em; color:#666;">💡 {book.get('reason')}</span>
                    </div>
                    """, unsafe_allow_html=True)
