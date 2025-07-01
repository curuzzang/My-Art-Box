import streamlit as st
from datetime import datetime
from openai import OpenAI
import pytz

# --- 4. OpenAI API Key 설정 ---
openai.api_key = st.secrets["api_key"]

# 타이틀 스타일 설정
st.markdown("""
    <h1 style='text-align: center; font-size:20px; margin-top:10px; color:black;'>🎨 나의 그림상자 (My Art Box)</h1>
""", unsafe_allow_html=True)

# 시간 제한 설정
today = datetime.now(pytz.timezone("Asia/Seoul"))
date = today.date()
hour = today.hour

allowed = (
    date == datetime(2025, 7, 1).date() or  # 자유 사용일
    (date in [datetime(2025, 7, 2).date(), datetime(2025, 7, 4).date()] and 9 <= hour <= 13)
)

if not allowed:
    st.error("⛔ 현재는 사용 가능한 시간이 아닙니다.\n\n👉 사용 가능 시간: 7월 1일 (제한 없음), 7월 2일·4일 (오전 9시~오후 1시)")
    st.stop()

# 비밀번호 입력
password = st.text_input("🔑 비밀번호를 입력하세요", type="password")
if password != "1234":  # 수업 당일 수동으로 바꾸세요
    st.warning("비밀번호를 입력해야 사용 가능합니다.")
    st.stop()

# 한영 변환 사전
translation_dict = {
    # 스타일
    "수채화": "watercolor", "유화": "oil painting", "두들풍": "doodle style", "디지털 페인팅": "digital painting",
    "일본 애니메이션풍": "Japanese anime style", "큐비즘": "cubism", "사이버펑크": "cyberpunk",
    "팝아트": "pop art", "미니멀리즘": "minimalism", "몽환적인": "dreamlike",

    # 색상 톤
    "파스텔": "pastel", "원색": "primary color", "모노톤": "monotone", "선명한": "vivid",
    "따뜻한": "warm", "차가운": "cool", "대비색": "complementary colors", "무채색": "achromatic",

    # 감정 및 분위기
    "고요한": "calm", "혼돈의": "chaotic", "따뜻한": "warm", "차가운": "cold", "신비로운": "mysterious",
    "우울한": "melancholic", "경쾌한": "cheerful", "불안한": "anxious", "자유로운": "free", "감성적인": "emotional",

    # 시점 및 구도
    "정면": "frontal", "측면": "side view", "탑뷰": "top-down", "하늘을 올려다보는": "upward view",
    "클로즈업": "close-up", "광각": "wide angle", "역광": "backlight", "소프트 포커스": "soft focus",
    "로우 앵글": "low angle", "하이 앵글": "high angle"
}

# UI: 왼쪽 입력, 오른쪽 출력
col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("🎯 프롬프트 구성하기")

    theme = st.text_input("주제 (예: 내면의 평화)")
    genre = st.selectbox("스타일", list({k for k in translation_dict if translation_dict[k] in [
        "watercolor", "oil painting", "doodle style", "digital painting", "Japanese anime style",
        "cubism", "cyberpunk", "pop art", "minimalism", "dreamlike"
    ]}))

    elements = st.text_area("주요 요소 (쉼표로 구분)", placeholder="예: 나무, 달, 나")
    color = st.selectbox("색상 톤", [k for k, v in translation_dict.items() if v in [
        "pastel", "primary color", "monotone", "vivid", "warm", "cool", "complementary colors", "achromatic"
    ]])
    moods = st.multiselect("감정/분위기 (다중 선택 가능)", [k for k, v in translation_dict.items() if v in [
        "calm", "chaotic", "warm", "cold", "mysterious", "melancholic", "cheerful", "anxious", "free", "emotional"
    ]])
    viewpoint = st.selectbox("카메라 시점/효과", [k for k, v in translation_dict.items() if v in [
        "frontal", "side view", "top-down", "upward view", "close-up", "wide angle",
        "backlight", "soft focus", "low angle", "high angle"
    ]])

    generate = st.button("✨ 프롬프트 생성하기")

with col2:
    st.subheader("🧾 생성된 프롬프트")

    if generate:
        genre_en = translation_dict.get(genre, genre)
        elements_en = elements  # 사용자가 직접 입력
        color_en = translation_dict.get(color, color)
        moods_en = ", ".join([translation_dict.get(m, m) for m in moods])
        viewpoint_en = translation_dict.get(viewpoint, viewpoint)

        prompt = (
            f"Create an image that expresses '{theme}' in a {genre_en} style. "
            f"Be sure to include {elements_en}, and use {color_en} color tones to convey a feeling of {moods_en}, "
            f"captured from a {viewpoint_en} perspective. "
            f"Include subtle details that emphasize the emotional nuance of '{theme}'."
        )

        st.text_area("🔍 영어 프롬프트", value=prompt, height=200)

        # 이미지 생성
if st.button("🎨 이미지 생성하기"):
    with st.spinner("🖼️ 이미지 생성 중입니다. 잠시만 기다려주세요..."):
        try:
            client = OpenAI()  # 최신 API 방식
            response = client.images.generate(
                model="dall-e-3",
                prompt=prompt,
                size="1024x1024",
                n=1
            )
            image_url = response.data[0].url

            st.image(image_url, caption="🖼️ 생성된 이미지", use_container_width=True)
            st.markdown(f"[🖼️ 이미지 다운로드]({image_url})", unsafe_allow_html=True)

            # 세션에 저장
            if "generated_prompts" not in st.session_state:
                st.session_state["generated_prompts"] = []
            st.session_state["generated_prompts"].append({
                "prompt": prompt,
                "image_url": image_url
            })

        except Exception as e:
            st.error(f"❌ 이미지 생성 오류: {e}")
