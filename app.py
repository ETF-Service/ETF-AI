import streamlit as st
import time
from model.model import create_response, analyze_sentiment, cosine_sim
from tunning.instructions import instructions, analyze_instructions

# ETF
data = [
    "미국s&p500(SPY)",
    "미국_나스닥(QQQ)",
    "한국(EWY)",
    "일본(EWJ)",
    "중국(MCHI)",
    "유럽(VGK)"
]

if "sidebar_collapsed" not in st.session_state:
    st.session_state.sidebar_collapsed = False

# 메세지 조건문
cond1 = "api_key" in st.session_state
cond2 = "model_type" in st.session_state
cond3 = "user_name" in st.session_state
cond4 = "invest_type" in st.session_state
cond5 = "interest" in st.session_state

if "messages" not in st.session_state and cond1 and cond2 and cond3 and cond4 and cond5 and st.session_state.sidebar_collapsed:
    print(st.session_state.invest_type)
    print(st.session_state.user_name)
    print(st.session_state.interest)

    st.session_state.messages = [
        {
            "role": "developer",
            "content": instructions(st.session_state.user_name, st.session_state.invest_type, st.session_state.interest),
        }
    ]

if "alarm" not in st.session_state:
    st.session_state.alarm = False

if st.session_state.sidebar_collapsed:
    st.set_page_config(initial_sidebar_state="collapsed")
else:
    st.set_page_config(initial_sidebar_state="expanded")

st.set_page_config(
    layout="wide",
    page_icon="💸",
    page_title="금융 Agent"
)

with st.sidebar:
    st.write("### 모델 선택 및 API 키 입력")
    st.session_state.api_key = st.text_input("**API_KEY**")
    st.session_state.model_type = st.selectbox("**사용할 모델 종류**", ["gpt-4o", "gpt-4o-mini", "Clova X"])

    st.write("----")
    # 사용자의 정보를 가져오는 부분
    st.write("### 사용자 정보")
    st.session_state.user_name = st.text_input("**이름**")

    st.session_state.invest_type = st.select_slider(
        label="**투자 성향(0(보수적) ~ 10(공격적))**",
        options=[
            0,
            1,
            2,
            3,
            4,
            5,
            6,
            7,
            8,
            9,
            10
        ]
    )

    st.session_state.interest = st.multiselect(
        "**현재 투자하고 있는 ETF**",
        key="visibility",
        options=data
    )

    if st.button("저장"):
        st.session_state.sidebar_collapsed = True
        st.rerun()

st.title("ETF 알림 챗봇")
file = st.file_uploader("참고하고 싶은 금융 관련 파일을 업로드 하세요.")
if "messages" in st.session_state:
    for message in st.session_state.messages:
        if message["role"] != "assistant" and message["role"] != "user":
            continue
        if message["content"] == None:
            continue
        with st.chat_message(message["role"]):
            st.write(message["content"])

if prompt := st.chat_input("금융 정보에 대해 질문하세요!"):
    
    st.session_state.messages.append(
        {
            "role": "user", 
            "content": prompt
        }
    )

    with st.chat_message("user"):
        st.write(prompt)

    with st.chat_message("assistant"):
        stream, st.session_state.messages = create_response(st.session_state.messages, st.session_state.api_key, st.session_state.model_type)
        response = st.write_stream(stream)

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": response
        }
    )

if st.button("알림 설정"):
    st.session_state.alarm = not st.session_state.alarm
    if st.session_state.alarm:
        st.write("알람 켜짐. 앞으로 실시간 정보를 받아올 수 있어요!")
    else:
        st.write("알람 꺼짐.")

if st.session_state.alarm:

    st.subheader("알림 서비스 활성화중...")
    prev_response = []

    while True:
        analyze_messages = [
            {
                "role": "developer",
                "content": analyze_instructions(st.session_state.user_name, st.session_state.invest_type, st.session_state.interest)
            },
            {
                "role": "user",
                "content": "네이버 최근 뉴스랑 한국은행에서 제공하는 정보를 통해서\
                    지금 내가 투자하고 있는 상품중에 적립식 투자를 더 올리거나 말아야 할 상품 있어? 아니면 더 추가될 만한 상품 있니? 최대 2줄로 근거는 말하지 말고, 확실하게 답해줘."
            }
        ]
        response = analyze_sentiment(analyze_messages, st.session_state.api_key, st.session_state.model_type)
        if len(prev_response) != 0:
            # 코사인 유사도 측정
            similarity = cosine_sim(prev_response[-1], response[0])
            if similarity < 0.55:
                prev_response.append(response)
                with st.chat_message("assistant"):
                    st.write(response[0])
        else:
            prev_response.append(response)
            with st.chat_message("assistant"):
                st.write(response[0])

        # 1분마다 실시간 처리
        time.sleep(60)