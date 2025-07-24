from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from model.model import create_response, analyze_sentiment
import uvicorn
import json
from typing import List
from tunning.instructions import instructions

app = FastAPI()

class ChatRequest(BaseModel):
    messages: List[dict]  # 전체 대화 히스토리
    api_key: str
    model_type: str

class PersonaRequest(BaseModel):
    name: str
    invest_type: int
    interest: List[str]

@app.post("/chat")
async def chat_endpoint(req: ChatRequest):
    
    # 백엔드에서 전송한 전체 대화 히스토리 사용
    stream, updated_messages = create_response(req.messages, req.api_key, req.model_type)
    answer = ""
    for chunk in stream:
        delta = getattr(chunk.choices[0], "delta", None)
        if delta and hasattr(delta, "content") and delta.content:
            answer += delta.content
    return {"answer": answer}

@app.post("/chat/stream")
async def chat_stream_endpoint(req: ChatRequest):
    """스트리밍 응답을 위한 엔드포인트"""
    
    async def generate_stream():
        try:
            # 백엔드에서 전송한 전체 대화 히스토리 사용
            stream, updated_messages = create_response(req.messages, req.api_key, req.model_type)
            
            for chunk in stream:
                delta = getattr(chunk.choices[0], "delta", None)
                if delta and hasattr(delta, "content") and delta.content:
                    yield f"data: {json.dumps({'content': delta.content})}\n\n"
            
            yield "data: [DONE]\n\n"
            
        except Exception as e:
            error_message = f"AI 서비스 오류: {str(e)}"
            yield f"data: {json.dumps({'content': error_message})}\n\n"
            yield "data: [DONE]\n\n"
    
    return StreamingResponse(
        generate_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True) 

@app.post("/persona")
async def get_persona(req: PersonaRequest):
    persona = instructions(req.name, req.invest_type, req.interest)
    return {"persona": persona}

@app.post("/analyze")
async def analyze_endpoint(req: ChatRequest):
    """투자 분석을 위한 엔드포인트 - analyze_sentiment 함수 사용"""
    try:
        # analyze_sentiment 함수 호출
        analysis_result, updated_messages = analyze_sentiment(req.messages, req.api_key, req.model_type)
        
        return {
            "answer": analysis_result,
            "success": True
        }
    except Exception as e:
        return {
            "answer": f"분석 중 오류가 발생했습니다: {str(e)}",
            "success": False,
            "error": str(e)
        }