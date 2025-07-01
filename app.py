import streamlit as st
from openai import OpenAI
from datetime import datetime, time
import pytz

# ✅ 비밀키 설정 (Streamlit secrets에 저장 필요)
client = OpenAI(api_key=st.secrets["api_key"])

# ✅ 사용 가능한 날짜 및 시간 설정
korea = pytz.timezone("Asia/Seoul")
now = datetime.now(korea)
today = now.date()
allowed_dates = [datetime(2025, 7, 1).date(), datetime(2025, 7, 2).date(), datetime(2025, 7, 4).date()]
allowed_time = (time(9, 0), time(13, 0))  # 오전 9시~오후 1시

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

# ✅ 타이틀
st.markdown("""
<h1 style='text-align: center; font-size: 20px; color: black; margin-top: 10px;
           background: linear-gradient(to right, #f8cdda, #e6eeff); padding: 10px; border-radius: 10px;'>
    🎨 나의 그림상자 (My Art Box)
</h1>
""", unsafe_allow_html=True)

# ✅ 시간 제한
if today not in allowed_dates or not (allowed_time[0] <= now.time() <= allowed_time[1]):
    if today != datetime(2025, 7, 1).date():
        st.error("⛔ 이 웹앱은 다음 시간에만 사용 가능합니다:\n\n📅 7월 1일(테스트), 7월 2일(화), 7월 4일(목) ⏰ 오전 9시 ~ 오후 1시 (KST)")
        st.stop()

# ✅ 비밀번호 인증
if not st.session_state.authenticated:
    pw = st.text_input("🔐 수업 비밀번호를 입력하세요:", type="password")
    if st.button("입장하기"):
        if pw == st.secrets["password"]:
            st.session_state.authenticated = True
            st.success("✅ 인증 성공! 수업에 입장합니다.")
        else:
            st.error("❌ 비밀번호가 틀렸습니다.")
    st.stop()

# ✅ 좌우 레이아웃
left_col, right_col = st.columns([1, 2])

# ✅ 왼쪽 입력창
with left_col:
    st.subheader("🖍️ 나를 표현하는 키워드를 골라보세요")
    custom_prompt = st.text_input("주제를 직접 입력하세요 (예: 내 안의 고요함과 혼돈)", "")

    style = st.selectbox("🎨 스타일", [
        "수채화", "유화", "드로잉", "두들 아트", "팝아트",
        "인상주의", "입체주의", "디지털 아트", "애니메이션",
        "사진풍", "고흐 스타일", "모네 스타일", "피카소 스타일"
    ])

    color = st.selectbox("🌈 색상 톤", [
        "파스텔", "비비드", "모노톤", "대비 강한",
        "차분한", "무지개", "회색조", "세피아"
    ])

    mood = st.multiselect("💫 감정·분위기", [
        "고요한", "혼돈의", "따뜻한", "차가운",
        "신비로운", "어두운", "명랑한", "감성적인",
        "몽환적인", "강렬한", "단단한", "불안한", "균형 잡힌"
    ])

    viewpoint = st.selectbox("📷 시점·구도", [
        "정면", "측면", "하이앵글", "로우앵글",
        "탑뷰", "오버더숄더", "클로즈업",
        "심도있는", "부드러운 초점", "원근법 강조"
    ])

    element = st.text_area("🔍 주요 요소 직접 입력 (예: 뿌리, 나무, 나선형, 별, 나침반)", "")

# ✅ 오른쪽: 프롬프트 생성 및 이미지 생성
with right_col:
    st.subheader("✨ 프롬프트 및 이미지 결과")

    if st.button("🎯 프롬프트 생성하기"):
        def translate(term):
            translations = {
                "고요한": "calm", "혼돈의": "chaotic", "따뜻한": "warm", "차가운": "cold",
                "신비로운": "mysterious", "어두운": "dark", "명랑한": "cheerful",
                "감성적인": "emotional", "몽환적인": "dreamy", "강렬한": "intense",
                "단단한": "solid", "불안한": "anxious", "균형 잡힌": "balanced"
            }
            return translations.get(term, term)

        mood_eng = [translate(m) for m in mood]
        prompt = f"A conceptual representation of '{custom_prompt}'"
        if element:
            prompt += f", including {element}"
        if mood_eng:
            prompt += f", evoking a sense of {', '.join(mood_eng)}"
        if style:
            prompt += f", in {style} style"
        if color:
            prompt += f", using {color} color tones"
        if viewpoint:
            prompt += f", from a {viewpoint} perspective"

        st.session_state.prompt = prompt
        st.markdown("📝 **프롬프트 (영문)**")
        st.code(prompt)

    if "prompt" in st.session_state:
        if st.button("🖼️ 이미지 생성하기"):
            try:
                response = client.images.generate(
                    model="dall-e-3",
                    prompt=st.session_state.prompt,
                    size="1024x1024",
                    quality="standard",
                    n=1,
                )
                image_url = response.data[0].url
                st.image(image_url, caption="🎨 생성된 이미지", use_column_width=True)
                st.markdown(f'<a href="{image_url}" download="my_art_box_image.png" target="_blank">📥 이미지 다운로드</a>', unsafe_allow_html=True)
            except Exception as e:
                st.error(f"❌ 이미지 생성 중 오류 발생: {str(e)}")
