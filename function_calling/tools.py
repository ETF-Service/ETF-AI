tools = [
    {
        "type": "function",
        "function": {
            "name": "get_finance_info",
            "description": "입력된 일정 동안 해당 투자 종목(야후 finance 심볼들(예시로 AAPL))의 종가, 최고가, 최저가, 시가, 거래량을 가져오는 함수",
            "parameters": {
                "type": "object",
                "properties": {
                    "symbols": {
                        "type": "array",
                        "items": {
                            "type": "string"
                        },
                        "description": "야후 finance 심볼 리스트"
                    },
                    "start": {
                        "type": "string",
                        "description": "원하는 시작 일자. 예를 들어, '2025-06-20'이런 식으로 입력이 되어야 함. 주말은 안 나오니까 주의"
                    },
                    "end": {
                        "type": "string",
                        "description": "원하는 종료 일자 + 1일. 예를 들어, 25년 6월 28일의 정보까지 보고싶으면 '2025-06-29'이런 식으로 입력이 되어야 함. 또한, 25년 6월 30까지의 정보를 보고싶으면 '2025-07-01'로 입력해야함. 주말은 안 나오니까 주의"
                    },
                },
                "required": ["symbols", "start", "end"],
                "additionalProperties": False,
            },
            "strict": True
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_finance_analized",
            "description": "입력된 야후 finance 심볼들(예시로 AAPL)에 대해 투자 분석가들이 내놓은 간략한 의견이야.",
            "parameters": {
                "type": "object",
                "properties": {
                    "symbols": {
                        "type": "array",
                        "items": {
                            "type": "string"
                        },
                        "description": "야후 finance 심볼 리스트"
                    },
                },
                "required": ["symbols"],
                "additionalProperties": False,
            },
            "strict": True
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_financial",
            "description": "입력된 야후 finance 심볼들에 대한 재무제표야.",
            "parameters": {
                "type": "object",
                "properties": {
                    "symbols": {
                        "type": "array",
                        "items": {
                            "type": "string"
                        },
                        "description": "야후 finance 심볼 리스트"
                    },
                },
                "required": ["symbols"],
                "additionalProperties": False,
            },
            "strict": True
        }
    },
    {
        "type": "function",
        "function": {
            "name": "bring_recent_news_naver_global",
            "description": "네이버 글로벌 경제 뉴스에서 최근 뉴스를 가지고 오는 함수야. 이 함수는 실시간으로 적용되어야 하기 때문에 필요시 지속적으로 함수를 불러야 해.",
            "parameters": {
                "type": "object",
                "properties": {
                    "top_n": {
                        "type": "number",
                        "description": "몇개의 최신 뉴스를 검색할 지 입력받는 변수."
                    },
                },
                "required": ["top_n"],
                "additionalProperties": False,
            },
            "strict": True
        }
    },
    {
        "type": "function",
        "function": {
            "name": "bring_recent_news_naver_korea",
            "description": "네이버 한국 경제 뉴스에서 최근 뉴스를 가지고 오는 함수야. 이 함수는 실시간으로 적용되어야 하기 때문에 필요시 지속적으로 함수를 불러야 해.",
            "parameters": {
                "type": "object",
                "properties": {
                    "top_n": {
                        "type": "number",
                        "description": "몇개의 최신 뉴스를 검색할 지 입력받는 변수."
                    },
                },
                "required": ["top_n"],
                "additionalProperties": False,
            },
            "strict": True
        }
    },
    {
        "type": "function",
        "function": {
            "name": "Korea_Bank_News_Text",
            "description": "최근 ETF 관련 정보를 분석하기 위해 한국은행에서 제공하는 현지정보, 동향분석 텍스트를 받아오는 함수야.",
            "parameters": {
                "type": "object",
                "properties": {
                    "page": {
                        "type": "number",
                        "description": "몇 페이지까지 크롤링할지 정하는 변수."
                    },
                },
                "required": ["page"],
                "additionalProperties": False,
            },
            "strict": True
        }
    }
]