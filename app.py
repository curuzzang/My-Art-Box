import streamlit as st
import openai
from datetime import datetime, time
import pytz
import requests

client = openai.OpenAI(api_key=st.secrets["api_key"])

# ✅ 번역기 초기화
translator = Translator()

def translate_to_english(text):
    try:
        return translator.translate(text, src='ko', dest='en').text
    except:
        return text

# ✅ 감정/스타일/색감/시점 영어 변환
def translate(term):
    translations = {
        # 감정
        "고요한": "calm", "혼돈의": "chaotic", "따뜻한": "warm", "차가운": "cold",
        "신비로운": "mysterious", "어두운": "dark", "명랑한": "cheerful",
        "감성적인": "emotional", "몽환적인": "dreamy", "강렬한": "intense",
        "단단한": "solid", "불안한": "anxious", "균형 잡힌": "balanced",
        # 스타일
        "수채화": "watercolor", "유화": "oil painting", "드로잉": "sketch",
        "두들 아트": "doodle art", "팝아트": "pop art", "인상주의": "impressionism",
        "입체주의": "cubism", "디지털 아트": "digital art", "애니메이션": "animation",
        "사진풍": "photorealistic", "고흐 스타일": "Van Gogh style",
        "모네 스타일": "Monet style", "피카소 스타일": "Picasso style",
        # 색감
        "파스텔": "pastel", "비비드": "vivid", "모노톤": "monotone",
        "대비 강한": "high contrast", "차분한": "subdued", "무지개": "rainbow",
        "회색조": "grayscale", "세피아": "sepia",
        # 시점
        "정면": "frontal", "측면": "side view", "하이앵글": "high angle",
        "로우앵글": "low angle", "탑뷰": "top view", "오버더숄더": "over-the-shoulder",
        "클로즈업": "close-up", "심도있는": "deep focus", "부드러운 초점": "soft focus",
        "원근법 강조": "with strong perspective"
    }
    return translations.get(term, term)

# ✅ OpenAI 클라이언트 설정
client = OpenAI(api_key=st.secrets["api_key"])

# ✅ 날짜 & 시간 제한
korea = pytz.timezone("Asia/Seoul")
now = datetime.now(korea)
today = now.date()
allowed_dates = [datetime(2025, 7, 1).date(), datetime(2025, 7, 2).date(), datetime(2025, 7, 4).date()]
allowed_time = (time(9, 0), time(13, 0))

# ✅ 타이틀
st.markdown("""
<h1 style='text-align: center; font-size: 20px; color: black; margin-top: 10px;
           background: linear-gradient(to right, #f8cdda, #e6eeff); padding: 10px; border-radius: 10px;'>
    🎨 나의 그림상자 (My Art Box)
</h1>
""", unsafe_allow_html=True)

# ✅ 인증 상태 체크
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

# ✅ 시간 제한 체크
if today not in allowed_dates or not (allowed_time[0] <= now.time() <= allowed_time[1]):
    if today != datetime(2025, 7, 1).date():
        st.error("⛔ 이 웹앱은 다음 시간에만 사용 가능합니다:\n\n📅 7월 1일(테스트), 7월 2일(화), 7월 4일(목) ⏰ 오전 9시 ~ 오후 1시 (KST)")
        st.stop()

# ✅ 좌우 레이아웃
left_col, right_col = st.columns([1, 2])

# ✅ 왼쪽: 사용자 입력
with left_col:
    st.subheader("🖍️ 표현하고 싶은 키워드를 골라보세요")
    custom_prompt = st.text_input("주제를 직접 입력하세요 (예: 내 안의 고요함과 혼돈)", "")
    style = st.selectbox("🎨 스타일", [...])  # 그대로 유지
    color = st.selectbox("🌈 색상 톤", [...])  # 그대로 유지
    mood = st.multiselect("💫 감정·분위기", [...])  # 그대로 유지
    viewpoint = st.selectbox("📷 시점·구도", [...])  # 그대로 유지
    element = st.text_area("🔍 주요 요소 직접 입력 (예: 뿌리, 나무, 나선형, 별, 나침반)", "")

# ✅ 오른쪽: 프롬프트 생성
with right_col:
    st.subheader("✨ 프롬프트 및 이미지 결과")

    if st.button("🎯 프롬프트 생성하기"):
        theme_en = translate_to_english(custom_prompt)
        element_en = translate_to_english(element)
        mood_eng = [translate(m) for m in mood]
        style_eng = translate(style)
        color_eng = translate(color)
        viewpoint_eng = translate(viewpoint)

        prompt = f"A conceptual representation of '{theme_en}'"
        if element_en:
            prompt += f", including {element_en}"
        if mood_eng:
            prompt += f", evoking a sense of {', '.join(mood_eng)}"
        if style_eng:
            prompt += f", in {style_eng} style"
        if color_eng:
            prompt += f", using {color_eng} color tones"
        if viewpoint_eng:
            prompt += f", from a {viewpoint_eng} perspective"

        st.session_state.prompt = prompt
        st.markdown("📝 **프롬프트 (영문)**")
        st.code(prompt)

    # ✅ 이미지 생성
    if "prompt" in st.session_state and st.button("🖼️ 이미지 생성하기"):
        try:
            response = client.images.generate(
                model="dall-e-3",
                prompt=st.session_state.prompt,
                size="1024x1024",
                quality="standard",
                n=1,
            )
            image_url = response.data[0].url
            st.markdown("📝 **프롬프트 (영문)**")
            st.code(st.session_state.prompt)

            st.image(image_url, caption="🎨 생성된 이미지", use_container_width=True)

            img_response = requests.get(image_url)
            if img_response.status_code == 200:
                st.download_button(
                    label="📥 이미지 저장하기",
                    data=img_response.content,
                    file_name="my_art_box_image.png",
                    mime="image/png"
                )
            else:
                st.warning("이미지를 불러오지 못했습니다.")
        except Exception as e:
            st.error(f"❌ 이미지 생성 또는 다운로드 중 오류 발생: {str(e)}")
