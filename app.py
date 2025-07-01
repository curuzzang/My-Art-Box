import streamlit as st
from datetime import datetime
import pytz
import openai
import os

from openai import OpenAI

# 1. 최신 OpenAI API 사용 설정
client = OpenAI(api_key=st.secrets["api_key"])

# 2. 페이지 설정
st.set_page_config(page_title="🖼️나의 그림상자", layout="wide")

# 3. 시간 제어 설정
kst = pytz.timezone("Asia/Seoul")
now_kst = datetime.now(kst)
today = now_kst.date()
hour = now_kst.hour

allow_dates = [datetime(2025, 7, 1).date(), datetime(2025, 7, 2).date(), datetime(2025, 7, 4).date()]
allow_hours = range(8, 14)  # 오전 9시~오후 1시 (KST 기준)

# 4. 비밀번호 인증
if today in allow_dates and (today == datetime(2025, 7, 1).date() or hour in allow_hours):
    if "authenticated" not in st.session_state:
        password = st.text_input("🔐 수업 비밀번호를 입력하세요:", type="password")
        if st.button("입장하기"):
            if password == st.secrets["class_password"]:
                st.session_state.authenticated = True
                st.success("✅ 인증 성공! 수업에 입장합니다.")
            else:
                st.error("❌ 비밀번호가 틀렸습니다.")
        st.stop()
else:
    st.error("⛔ 이 웹앱은 다음 시간에만 사용 가능합니다:\n\n📅 7월 1일(자유 테스트), 7월 2일(화), 7월 4일(목) ⏰ 오전 9시 ~ 오후 1시 (KST)")
    st.stop()

# 5. 한글 → 영어 변환 테이블
translation_dict = {
    '고요한': 'calm', '혼돈의': 'chaotic', '따뜻한': 'warm', '차가운': 'cold', '신비로운': 'mysterious',
    '어두운': 'dark', '명랑한': 'cheerful', '감성적인': 'emotional', '몽환적인': 'dreamy', '강렬한': 'intense',
    '단단한': 'solid', '불안한': 'anxious', '균형 잡힌': 'balanced', '파스텔': 'pastel', '비비드': 'vivid',
    '모노톤': 'monotone', '대비 강한': 'high contrast', '차분한': 'subdued', '무지개': 'rainbow',
    '회색조': 'grayscale', '세피아': 'sepia',
    '수채화': 'watercolor', '유화': 'oil painting', '드로잉': 'sketch', '두들 아트': 'doodle art',
    '팝아트': 'pop art', '인상주의': 'impressionism', '입체주의': 'cubism', '디지털 아트': 'digital art',
    '애니메이션': 'animation style', '사진풍': 'photorealistic', '고흐 스타일': 'Van Gogh style',
    '모네 스타일': 'Monet style', '피카소 스타일': 'Picasso style',
    '정면': 'frontal', '측면': 'profile', '하이앵글': 'high angle', '로우앵글': 'low angle',
    '탑뷰': 'top view', '오버더숄더': 'over-the-shoulder', '클로즈업': 'close-up', '심도있는': 'deep focus',
    '부드러운 초점': 'soft focus', '원근법 강조': 'perspective emphasized'
}

# 6. UI 구성 (좌: 입력, 우: 결과)
st.markdown(
    "<h1 style='text-align: center; font-size:20px; background: linear-gradient(to right, #e0c3fc, #8ec5fc); color: black;'>🖼️ 나의 그림상자 (My Art Box)</h1>",
    unsafe_allow_html=True
)

col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("✍️ 나를 표현하는 이미지 만들기")
    with st.form("prompt_form"):
        theme = st.text_input("주제 (예: 내 안의 고요함과 혼돈)")
        elements = st.text_input("주요 요소 (쉼표로 구분)", placeholder="예: 나무, 고양이, 달")
        style = st.selectbox("스타일", [k for k in translation_dict if '스타일' in k or '아트' in k or '풍' in k])
        color = st.selectbox("색상 톤", [k for k in translation_dict if k in ['파스텔', '비비드', '모노톤', '무지개', '세피아', '회색조', '차분한', '대비 강한']])
        mood = st.multiselect("감정/분위기", [k for k in translation_dict if k in ['고요한', '혼돈의', '신비로운', '감성적인', '몽환적인', '불안한', '명랑한', '강렬한', '균형 잡힌', '단단한']])
        view = st.selectbox("시점/촬영 구도", [k for k in translation_dict if k in ['정면', '측면', '하이앵글', '로우앵글', '탑뷰', '오버더숄더', '클로즈업', '심도있는', '부드러운 초점', '원근법 강조']])
        submit_btn = st.form_submit_button("✅ 프롬프트 생성")

with col2:
    if submit_btn:
        # 변환
        style_en = translation_dict.get(style, style)
        color_en = translation_dict.get(color, color)
        mood_en = ', '.join([translation_dict.get(m, m) for m in mood])
        view_en = translation_dict.get(view, view)
        elements_en = ', '.join([e.strip() for e in elements.split(",")])

        # 프롬프트 생성
        final_prompt = f"A conceptual representation of '{theme}', including {elements_en}, evoking a sense of {mood_en}, in {style_en} style, using {color_en} tones, from a {view_en} perspective."

        st.success("🎯 생성된 프롬프트:")
        st.code(final_prompt)

        # 프롬프트 저장
        if "generated" not in st.session_state:
            st.session_state["generated"] = []
        st.session_state["generated"].append(final_prompt)

        # 이미지 생성
        if st.button("🎨 이미지 생성하기"):
            with st.spinner("이미지를 생성 중입니다..."):
                try:
                    response = client.images.generate(
                        model="dall-e-3",
                        prompt=final_prompt,
                        size="1024x1024",
                        n=1,
                        response_format="url"
                    )
                    image_url = response.data[0].url
                    st.image(image_url, caption="✨ 생성된 이미지", use_container_width=True)
                    st.markdown(f"[이미지 다운로드]({image_url})", unsafe_allow_html=True)

                    st.session_state["generated"].append({"prompt": final_prompt, "image_url": image_url})
                except Exception as e:
                    st.error(f"이미지 생성 오류: {e}")

    # 생성된 프롬프트 및 이미지 기록
    if "generated" in st.session_state and len(st.session_state["generated"]) > 0:
        st.subheader("🧾 지금까지 생성된 결과")
        for item in reversed(st.session_state["generated"]):
            if isinstance(item, dict):
                with st.container():
                    st.image(item["image_url"], caption=item["prompt"], use_container_width=True)
                    st.markdown("---")
