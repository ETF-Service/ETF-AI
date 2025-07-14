import streamlit as st
import datetime
import time
from model.model import create_response, analyze_sentiment, cosine_sim
from tunning.instructions import instructions, analyze_instructions
import data

# 고객이 선택할 ETF 상품.(현재 모델이 제공하는 ETF 상품들)
ETF = data.ETF

if "sidebar_collapsed" not in st.session_state:
    st.session_state.sidebar_collapsed = False

# 메세지 조건문
cond1 = "api_key" in st.session_state
cond2 = "model_type" in st.session_state
cond3 = "user_name" in st.session_state
cond4 = "invest_type" in st.session_state
cond5 = "interest" in st.session_state
cond6 = "invest_price" in st.session_state
cond7 = "invest_infos" in st.session_state

if "messages" not in st.session_state and cond1 and cond2 and cond3 and cond4 and cond5 and cond6 and cond7 and len(st.session_state.interest) == len(st.session_state.invest_price) and not st.session_state.sidebar_collapsed:
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
        options=ETF
    )

    if st.session_state.interest:
        for interest in st.session_state.interest:
            st.write(f"**{interest}**")

            frequency = st.radio("투자 주기를 선택하세요:", ["매일", "매주", "매월"], horizontal=True, key=f"frequency {interest}")
            if frequency == "매일":
                cycle = "매일"
                duration = st.number_input("투자 기간 (연)", min_value=1, step=1, key = f"duration {interest}")
                invest_price = st.text_input("**일 적립 금액**", key=f"interest {interest}")
            elif frequency == "매주":
                cycle = st.selectbox("투자 요일", ["월요일", "화요일", "수요일", "목요일", "금요일", "토요일", "일요일"], key = f"cycle {interest}")
                duration = st.number_input("투자 기간 (연)", min_value=1, step=1, key = f"duration {interest}")
                invest_price = st.text_input("**주 적립 금액**", key=f"interest {interest}")
            else:
                cycle = st.number_input("투자 일자", min_value=1, max_value=31, step=1, key = f"cycle {interest}")
                duration = st.number_input("투자 기간 (연)", min_value=1, step=1, key = f"duration {interest}")
                invest_price = st.text_input("**월 적립 금액**", key=f"interest {interest}")
            
            invest_info = {
                "frequency": frequency,
                "cycle": cycle,
                "duration": duration,
                "invest_price": invest_price
            }
            
            if "invest_infos" not in st.session_state:
                st.session_state.invest_infos = {}

            st.session_state.invest_infos[interest] = invest_info

            if "invest_price" not in st.session_state:
                st.session_state.invest_price = []

            st.session_state.invest_price.append(invest_price)

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
        week_days = {0: '월요일', 1: '화요일', 2: '수요일', 3: '목요일', 4: '금요일', 5: '토요일', 6: '일요일'}
        now = datetime.datetime.now()
        now_weekday = week_days[datetime.date.today().weekday()]

        today_ETF = []
        today_ETF_invest_price = []

        for invest_name in st.session_state.invest_infos:
            invest_info = st.session_state.invest_infos[invest_name]
            if invest_info["frequency"] == "매일":
                today_ETF.append(invest_name)
                today_ETF_invest_price.append(invest_info["invest_price"])
            elif invest_info["frequency"] == "매주" and invest_info["cycle"] == now_weekday:
                today_ETF.append(invest_name)
                today_ETF_invest_price.append(invest_info["invest_price"])
            elif invest_info["frequency"] == "매월" and invest_info["cycle"] == now.day:
                today_ETF.append(invest_name)
                today_ETF_invest_price.append(invest_info["invest_price"])

        analyze_messages = [
            {
                "role": "developer",
                "content": analyze_instructions(st.session_state.user_name, st.session_state.invest_type, st.session_state.interest, st.session_state.invest_price, st.session_state.invest_infos)
            },
            {
                "role": "user",
                "content": f"네이버 글로벌 경제 뉴스, 네이버 한국 경제 뉴스, 한국은행에서 제공하는 정보 3가지를 모두 분석해줘.\
                            지금 나는 {today_ETF} ETF에 각각 {today_ETF_invest_price}원씩 투자하고 있어. 투자 비율을 조정해야 하는 것이 있어?\
                            요약만 간결하게 해서 상품에 투자 비중을 정해서 최종 금액을 도출해줘."
            }
        ]

        response = analyze_sentiment(analyze_messages, st.session_state.api_key, st.session_state.model_type)

        if len(prev_response) != 0:
            # 코사인 유사도 측정
            similarity = cosine_sim(prev_response[-1], response[0])
            # 코사인 유사도가 일정 수준보다 낮게 나온다면 알림 보내기.
            if similarity < 0.5:
                prev_response.append(response)
                with st.chat_message("assistant"):
                    st.write(response[0])
        else:
            prev_response.append(response)
            with st.chat_message("assistant"):
                st.write(response[0])

        # 1분마다 실시간 처리
        time.sleep(60)