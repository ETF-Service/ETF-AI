from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from model.model import create_response
import uvicorn
import json
from typing import List

app = FastAPI()

class ChatRequest(BaseModel):
    messages: List[dict]  # 전체 대화 히스토리
    api_key: str
    model_type: str

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
        media_type="text/plain",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Content-Type": "text/event-stream"
        }
    )

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True) 