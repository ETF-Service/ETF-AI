from openai import OpenAI
from function_calling.function import *
from function_calling.tools import *
import warnings
import json
warnings.filterwarnings('ignore')

def create_response(messages, api_key, model_type):
    if model_type == "Clova X":
        model_type = "HCX-005"
        client = OpenAI(
            api_key=api_key,
            base_url="https://clovastudio.stream.ntruss.com/v1/openai"
            )
    else:
        client = OpenAI(api_key=api_key)

    # 모델 유형(gpt-o4-mini, gpt-o4, Clova X ...)
    Model = model_type

    response = client.chat.completions.create(
        messages=messages,
        model=Model,
        temperature=0.9,
        tools=tools
    )

    cnt = 0

    while response.choices[0].finish_reason=="tool_calls" and cnt <= 5:
        cnt += 1
        print()
        for tool in response.choices[0].message.tool_calls or []:
            args = json.loads(tool.function.arguments)

            if tool.function.name == "get_finance_info":
                output = get_finance_info(args["symbols"], args["start"], args["end"])
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
                            "content": str(output) if output else "해당 요청에 대한 정보를 찾을 수 없습니다."
                        }
                    )

            elif tool.function.name == "get_finance_analized":
                output = get_finance_analized(args["symbols"])
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
                            "content": str(output) if output else "해당 요청에 대한 정보를 찾을 수 없습니다."
                        }
                    )
            elif tool.function.name == "get_financial":
                output = get_financial(args["symbols"])
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
                            "content": str(output) if output else "해당 요청에 대한 정보를 찾을 수 없습니다."
                        }
                    )
            elif tool.function.name == "bring_recent_news_naver":
                output = bring_recent_news_naver(args["top_n"])
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
                            "content": str(output) if output else "해당 요청에 대한 정보를 찾을 수 없습니다."
                        }
                    )
            elif tool.function.name == "Korea_Bank_News_Text":
                output = Korea_Bank_News_Text()
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
                            "content": str(output) if output else "해당 요청에 대한 정보를 찾을 수 없습니다."
                        }
                    )

        response = client.chat.completions.create(
            messages=messages,
            model=Model,
            temperature=0.9,
            tools=tools,
        )

    response = client.chat.completions.create(
            messages=messages,
            model=Model,
            temperature=0.9,
            tools=tools,
            stream=True
        )
    
    return response, messages