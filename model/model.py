from openai import OpenAI
from function_calling.function import *
from function_calling.tools import *
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import warnings
import json
warnings.filterwarnings('ignore')

# 고객의 금융 관련 질문에 대한 응답을 제공하는 함수.
def create_response(messages, api_key, model_type):
    # 클라이언트 설정 (기존 코드와 동일)
    if model_type == "Clova X":
        model_type = "HCX-005"
        client = OpenAI(
            api_key=api_key,
            base_url="https://clovastudio.stream.ntruss.com/v1/openai"
        )
    else:
        client = OpenAI(api_key=api_key)

    Model = model_type

    response = client.chat.completions.create(
        messages=messages,
        model=Model,
        temperature=0.9,
        tools=tools
    )

    # tool_calls가 있는 경우 이를 처리
    if response.choices[0].finish_reason == "tool_calls":
        for tool in response.choices[0].message.tool_calls or []:
            args = json.loads(tool.function.arguments)

            # 각 tool에 대한 처리 (함수 호출 후 메시지 업데이트)
            output = None
            try:
                if tool.function.name == "get_finance_info":
                    output = get_finance_info(args["symbols"], args["start"], args["end"])
                elif tool.function.name == "get_finance_analized":
                    output = get_finance_analized(args["symbols"])
                elif tool.function.name == "get_financial":
                    output = get_financial(args["symbols"])
                elif tool.function.name == "bring_recent_news_naver":
                    output = bring_recent_news_naver(args["top_n"])
                elif tool.function.name == "Korea_Bank_News_Text":
                    output = Korea_Bank_News_Text()

            except Exception as e:
                output = f"⚠️ 함수 실행 중 오류 발생: {str(e)}"

            # 함수 결과가 있을 경우 messages에 추가
            if output:
                messages.append(
                    {
                        "role": "assistant",
                        "content": None,
                        "tool_calls": [
                            {
                                "id": tool.id,
                                "type": "function",
                                "function": {
                                    "name": tool.function.name,
                                    "arguments": str(args)
                                }
                            }
                        ]
                    }
                )
                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool.id, 
                        "content": str(output) if output else "정보를 가져올 수 없음."
                    }
                )

    # 스트리밍을 활성화한 호출
    response = client.chat.completions.create(
        messages=messages,
        model=Model,
        temperature=0.9,
        stream=True
    )
    
    # value == tool_calls => 응답 안됨. value != tool_calls => 응답 됨.
    print(messages)
    
    return response, messages

# 실시간으로 고객이 투자하는 ETF 상품 및 추가로 투자할 만한 가치가 있는 ETF 추천하는 모델 생성.
def analyze_sentiment(messages, api_key, model_type):
    # 클라이언트 설정 (기존 코드와 동일)
    if model_type == "Clova X":
        model_type = "HCX-005"
        client = OpenAI(
            api_key=api_key,
            base_url="https://clovastudio.stream.ntruss.com/v1/openai"
        )
    else:
        client = OpenAI(api_key=api_key)

    Model = model_type

    response = client.chat.completions.create(
        messages=messages,
        model=Model,
        temperature=0.9,
        tools=tools
    )

    # tool_calls가 있는 경우 이를 처리
    if response.choices[0].finish_reason == "tool_calls":
        for tool in response.choices[0].message.tool_calls or []:
            args = json.loads(tool.function.arguments)

            # 각 tool에 대한 처리 (함수 호출 후 메시지 업데이트)
            output = None
            try:
                if tool.function.name == "get_finance_info":
                    output = get_finance_info(args["symbols"], args["start"], args["end"])
                elif tool.function.name == "get_finance_analized":
                    output = get_finance_analized(args["symbols"])
                elif tool.function.name == "get_financial":
                    output = get_financial(args["symbols"])
                elif tool.function.name == "bring_recent_news_naver":
                    output = bring_recent_news_naver(args["top_n"])
                elif tool.function.name == "Korea_Bank_News_Text":
                    output = Korea_Bank_News_Text()

            except Exception as e:
                output = f"⚠️ 함수 실행 중 오류 발생: {str(e)}"

            # 함수 결과가 있을 경우 messages에 추가
            if output:
                messages.append(
                    {
                        "role": "assistant",
                        "content": None,
                        "tool_calls": [
                            {
                                "id": tool.id,
                                "type": "function",
                                "function": {
                                    "name": tool.function.name,
                                    "arguments": str(args)
                                }
                            }
                        ]
                    }
                )
                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool.id, 
                        "content": str(output) if output else "정보를 가져올 수 없음."
                    }
                )

    # 스트리밍을 활성화한 호출
    response = client.chat.completions.create(
        messages=messages,
        model=Model,
        temperature=0.9,
    )

    response = response.choices[0].message.content

    return response, messages

# 두 문장의 코사인 유사도 확인하는 함수
# 모델은 허깅페이스를 이용함.
def cosine_sim(sent1, sent2):
    print(sent2)
    model = SentenceTransformer('paraphrase-MiniLM-L6-v2')

    sent1_encode = model.encode([sent1])
    sent2_encode = model.encode([sent2])
    similarity = cosine_similarity(sent1_encode, sent2_encode)
    print(similarity)

    return similarity[0][0]