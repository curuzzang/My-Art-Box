import streamlit as st
import openai
from datetime import datetime
import pytz

# ----------------- 기본 설정 ------------------
st.set_page_config(page_title="🖼️나의 그림상자 (My Art Box)", layout="wide")

# ----------------- 스타일 지정 -----------------
st.markdown("""
    <style>
    .main { overflow-y: hidden; }
    .block-container { padding-top: 0rem; padding-bottom: 0rem; }
    h1 {
        text-align: center;
        font-size: 20px !important;
        color: black;
    }
    </style>
    """, unsafe_allow_html=True)

# ----------------- 타이틀 -----------------
st.title("🎨 나의 그림상자 (My Art Box)")

# ----------------- API Key -----------------
openai.api_key = st.secrets["api_key"]

# ----------------- 번역 테이블 -----------------
translation_dict = {
    '고요한': 'calm', '혼돈의': 'chaotic', '따뜻한': 'warm', '차가운': 'cold',
    '신비로운': 'mysterious', '어두운': 'dark', '명랑한': 'cheerful', '감성적인': 'emotional',
    '몽환적인': 'dreamy', '강렬한': 'intense', '단단한': 'solid', '불안한': 'anxious',
    '균형 잡힌': 'balanced', '기쁨의': 'joyful', '슬픔의': 'sorrowful', '두려운': 'fearful',
    '희망찬': 'hopeful', '그리운': 'nostalgic', '쓸쓸한': 'lonely', '편안한': 'relaxed', '기발한': 'whimsical',

    '파스텔': 'pastel', '비비드': 'vivid', '모노톤': 'monotone', '대비 강한': 'high contrast',
    '차분한': 'subdued', '무지개': 'rainbow', '회색조': 'grayscale', '세피아': 'sepia',
    '중간톤': 'midtone', '자연색': 'natural color', '흑백': 'black and white',
    '선명한': 'clear', '따뜻한 색조': 'warm tones', '차가운 색조': 'cool tones',

    '수채화': 'watercolor', '유화': 'oil painting', '드로잉': 'sketch', '두들 아트': 'doodle art',
    '팝아트': 'pop art', '인상주의': 'impressionism', '입체주의': 'cubism', '디지털 아트': 'digital art',
    '애니메이션': 'animation style', '사진풍': 'photorealistic', '고흐 스타일': 'Van Gogh style',
    '모네 스타일': 'Monet style', '피카소 스타일': 'Picasso style', '일러스트': 'illustration',
    '데생': 'drawing', '미니멀리즘': 'minimalism',

    '정면': 'frontal', '측면': 'profile', '하이앵글': 'high angle', '로우앵글': 'low angle',
    '탑뷰': 'top view', '오버더숄더': 'over-the-shoulder', '클로즈업': 'close-up',
    '심도있는': 'deep focus', '부드러운 초점': 'soft focus', '원근법 강조': 'perspective emphasized'
}

# ----------------- 컬럼 분할 -----------------
col1, col2 = st.columns([1, 2], gap="large")

# ----------------- 왼쪽: 입력창 -----------------
with col1:
    st.subheader("🧾 AI로 생각 그리기")
    with st.form("prompt_form"):
        theme = st.text_input("주제 (예: 내면의 평화)")
        genre = st.selectbox("스타일", [k for k in translation_dict if translation_dict[k] in ['watercolor', 'sketch', 'oil painting', 'doodle art', 'impressionism', 'cubism', 'digital art', 'animation style', 'photorealistic', 'Van Gogh style', 'Monet style', 'Picasso style', 'illustration', 'drawing', 'minimalism']])
        elements = st.text_input("주요 요소 (쉼표로 구분)", placeholder="예: 나무, 고양이, 달")
        color_tone = st.selectbox("색상 톤", [k for k in translation_dict if translation_dict[k] in ['pastel', 'vivid', 'monotone', 'high contrast', 'subdued', 'rainbow', 'grayscale', 'sepia', 'midtone', 'natural color', 'black and white', 'clear', 'warm tones', 'cool tones']])
        moods = st.multiselect("감정/분위기", [k for k in translation_dict if translation_dict[k] in ['calm', 'chaotic', 'warm', 'cold', 'mysterious', 'dark', 'cheerful', 'emotional', 'dreamy', 'intense', 'solid', 'anxious', 'balanced', 'joyful', 'sorrowful', 'fearful', 'hopeful', 'nostalgic', 'lonely', 'relaxed', 'whimsical']])
        viewpoint = st.selectbox("카메라 시점/효과", [k for k in translation_dict if 'angle' in translation_dict[k] or 'focus' in translation_dict[k] or 'view' in translation_dict[k]])
        generate_prompt_btn = st.form_submit_button("✅ 프롬프트 생성")

# ----------------- 오른쪽: 결과 -----------------
with col2:
    if generate_prompt_btn:
        # 영어 변환
        genre_en = translation_dict.get(genre, genre)
        elements_en = ', '.join([e.strip() for e in elements.split(",")])
        color_en = translation_dict.get(color_tone, color_tone)
        mood_en = ', '.join([translation_dict.get(m, m) for m in moods])
        viewpoint_en = translation_dict.get(viewpoint, viewpoint)

        # 프롬프트 구성
        final_prompt = f"Create an image that expresses '{theme}' in {genre_en} style. Include {elements_en}, use {color_en} color tones to convey a feeling of {mood_en}, captured from a {viewpoint_en} perspective."

        st.success("🖋️ 생성된 프롬프트:")
        st.code(final_prompt)

        # 이미지 생성
        if st.button("🎨 이미지 생성하기"):
            with st.spinner("이미지 생성 중..."):
                try:
                    response = openai.Image.create(
                        model="dall-e-3",
                        prompt=final_prompt,
                        size="1024x1024",
                        n=1,
                        response_format="url"
                    )
                    image_url = response["data"][0]["url"]
                    st.image(image_url, caption="🖼️ 생성된 이미지", use_container_width=True)
                    st.markdown(f"[이미지 다운로드]({image_url})", unsafe_allow_html=True)

                    # 세션에 저장
                    if "generated_prompts" not in st.session_state:
                        st.session_state["generated_prompts"] = []
                    st.session_state["generated_prompts"].append({
                        "prompt": final_prompt,
                        "image_url": image_url
                    })
                except Exception as e:
                    st.error(f"이미지 생성 오류: {e}")

        # 누적된 프롬프트 & 이미지
        if "generated_prompts" in st.session_state:
            st.subheader("📜 이전에 생성한 결과")
            for item in reversed(st.session_state["generated_prompts"]):
                with st.container():
                    st.image(item["image_url"], caption=item["prompt"], use_container_width=True)
                    st.markdown("---")
