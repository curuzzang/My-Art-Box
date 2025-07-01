import streamlit as st
import openai

# 페이지 설정
st.set_page_config(page_title="🖼️ 나의 그림상자", layout="wide")
st.markdown(
    "<h1 style='text-align: center; font-size: 20px; color: black; margin-top: 10px;'>🎨 나의 그림상자 (My Art Box)</h1>",
    unsafe_allow_html=True
)

# OpenAI 키
openai.api_key = st.secrets["api_key"]

# 번역 딕셔너리
translation_dict = {
    # 감정 / 분위기
    '고요한': 'calm', '혼돈의': 'chaotic', '따뜻한': 'warm', '차가운': 'cold', '신비로운': 'mysterious',
    '어두운': 'dark', '명랑한': 'cheerful', '감성적인': 'emotional', '몽환적인': 'dreamy', '강렬한': 'intense',
    '단단한': 'solid', '불안한': 'anxious', '균형 잡힌': 'balanced',

    # 색상 톤
    '파스텔': 'pastel', '비비드': 'vivid', '모노톤': 'monotone', '대비 강한': 'high contrast',
    '차분한': 'subdued', '무지개': 'rainbow', '회색조': 'grayscale', '세피아': 'sepia',

    # 스타일
    '수채화': 'watercolor', '유화': 'oil painting', '드로잉': 'sketch', '두들 아트': 'doodle art',
    '팝아트': 'pop art', '인상주의': 'impressionism', '입체주의': 'cubism', '디지털 아트': 'digital art',
    '애니메이션': 'animation style', '사진풍': 'photorealistic', '고흐 스타일': 'Van Gogh style',
    '모네 스타일': 'Monet style', '피카소 스타일': 'Picasso style',

    # 시점 / 구도
    '정면': 'frontal', '측면': 'profile', '하이앵글': 'high angle', '로우앵글': 'low angle',
    '탑뷰': 'top view', '오버더숄더': 'over-the-shoulder', '클로즈업': 'close-up', '심도있는': 'deep focus',
    '부드러운 초점': 'soft focus', '원근법 강조': 'perspective emphasized'
}

# UI 컬럼
col1, col2 = st.columns([1, 2])

# 프롬프트 입력 폼
with col1:
    st.subheader("🧾 나를 표현하는 이미지 만들기")
    with st.form("prompt_form"):
        theme = st.text_input("주제 (예: 내면의 평화)")
        genre = st.selectbox("스타일", [k for k in translation_dict if '스타일' in k or '아트' in k or '풍' in k])
        elements = st.text_input("주요 요소 (쉼표로 구분)", placeholder="예: 나무, 고양이, 달")
        color_tone = st.selectbox("색상 톤", [k for k in translation_dict if k in ['파스텔', '비비드', '모노톤', '무지개', '세피아', '회색조', '차분한', '대비 강한']])
        moods = st.multiselect("감정/분위기", [k for k in translation_dict if k in ['고요한', '혼돈의', '신비로운', '감성적인', '몽환적인', '불안한', '명랑한', '강렬한', '균형 잡힌', '단단한']])
        viewpoint = st.selectbox("시점/구도", [k for k in translation_dict if k in ['정면', '측면', '하이앵글', '로우앵글', '탑뷰', '오버더숄더', '클로즈업', '심도있는', '부드러운 초점', '원근법 강조']])
        generate_prompt_btn = st.form_submit_button("✅ 프롬프트 생성")

# 세션 초기화
if "generated_prompts" not in st.session_state:
    st.session_state["generated_prompts"] = []
if "current_prompt" not in st.session_state:
    st.session_state["current_prompt"] = ""

# 우측 영역: 프롬프트 생성 + 이미지 생성
with col2:
    if generate_prompt_btn:
        genre_en = translation_dict.get(genre, genre)
        elements_en = ', '.join([e.strip() for e in elements.split(",")])
        color_en = translation_dict.get(color_tone, color_tone)
        mood_en = ', '.join([translation_dict.get(m, m) for m in moods])
        viewpoint_en = translation_dict.get(viewpoint, viewpoint)

        final_prompt = f"Create an image that expresses '{theme}' in {genre_en} style. Include {elements_en}, use {color_en} color tones to convey a feeling of {mood_en}, captured from a {viewpoint_en} perspective."
        st.session_state["current_prompt"] = final_prompt

    if st.session_state["current_prompt"]:
        st.success("🖋️ 생성된 프롬프트:")
        st.code(st.session_state["current_prompt"], language="text")

        if st.button("🎨 이미지 생성하기"):
            with st.spinner("이미지 생성 중..."):
                try:
                    response = openai.Image.create(
                        model="dall-e-3",
                        prompt=st.session_state["current_prompt"],
                        size="1024x1024",
                        n=1,
                        response_format="url"
                    )
                    image_url = response["data"][0]["url"]
                    st.session_state["generated_prompts"].append({
                        "prompt": st.session_state["current_prompt"],
                        "image_url": image_url
                    })
                except Exception as e:
                    st.error(f"이미지 생성 오류: {e}")

    if st.session_state["generated_prompts"]:
        st.subheader("📌 생성된 이미지 모음")
        for item in reversed(st.session_state["generated_prompts"]):
            st.image(item["image_url"], caption=item["prompt"], use_container_width=True)
            st.markdown(f"[이미지 다운로드]({item['image_url']})", unsafe_allow_html=True)
            st.markdown("---")
