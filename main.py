from fastapi import FastAPI, Request, BackgroundTasks
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from model.model import create_response, analyze_sentiment
import uvicorn
import json
import asyncio
import time
from typing import List, Dict, Any
from tunning.instructions import instructions
from concurrent.futures import ThreadPoolExecutor
import logging
import os

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="ETF AI Analysis Service", version="1.0.0")

# 병렬 처리를 위한 스레드 풀
executor = ThreadPoolExecutor(max_workers=10)

class ChatRequest(BaseModel):
    messages: List[dict]  # 전체 대화 히스토리
    api_key: str
    model_type: str

class PersonaRequest(BaseModel):
    name: str
    invest_type: int
    interest: List[str]

class BatchAnalyzeRequest(BaseModel):
    requests: List[ChatRequest]  # 여러 분석 요청을 한 번에 처리

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

@app.post("/persona")
async def get_persona(req: PersonaRequest):
    persona = instructions(req.name, req.invest_type, req.interest)
    return {"persona": persona}

@app.post("/analyze")
async def analyze_endpoint(req: ChatRequest):
    """투자 분석을 위한 엔드포인트 - analyze_sentiment 함수 사용 (병렬 처리 지원)"""
    start_time = time.time()
    
    try:
        # 스레드 풀에서 동기 함수를 비동기로 실행
        loop = asyncio.get_event_loop()
        analysis_result, updated_messages = await loop.run_in_executor(
            executor, 
            analyze_sentiment, 
            req.messages, 
            req.api_key, 
            req.model_type
        )
        
        processing_time = time.time() - start_time
        logger.info(f"✅ AI 분석 완료 ({processing_time:.2f}초)")
        logger.info(f"✅ AI 분석 결과: {analysis_result}")
        
        return {
            "answer": analysis_result,
            "success": True,
            "processing_time": processing_time
        }
    except Exception as e:
        processing_time = time.time() - start_time
        logger.error(f"❌ AI 분석 실패 ({processing_time:.2f}초): {e}")
        
        return {
            "answer": f"분석 중 오류가 발생했습니다: {str(e)}",
            "success": False,
            "error": str(e),
            "processing_time": processing_time
        }

@app.post("/analyze/batch")
async def batch_analyze_endpoint(req: BatchAnalyzeRequest):
    """여러 투자 분석을 병렬로 처리하는 엔드포인트"""
    start_time = time.time()
    logger.info(f"🔄 배치 분석 시작: {len(req.requests)}개 요청")
    
    try:
        # 모든 분석 작업을 병렬로 실행
        async def analyze_single(request: ChatRequest) -> Dict[str, Any]:
            single_start_time = time.time()
            
            try:
                loop = asyncio.get_event_loop()
                analysis_result, updated_messages = await loop.run_in_executor(
                    executor,
                    analyze_sentiment,
                    request.messages,
                    request.api_key,
                    request.model_type
                )
                
                single_processing_time = time.time() - single_start_time
                logger.info(f"✅ 단일 분석 완료 ({single_processing_time:.2f}초)")
                logger.info(f"✅ AI 분석 결과: {analysis_result}")
                
                return {
                    "success": True,
                    "answer": analysis_result,
                    "processing_time": single_processing_time,
                    "request_id": id(request)  # 요청 식별용
                }
                
            except Exception as e:
                single_processing_time = time.time() - single_start_time
                logger.error(f"❌ 단일 분석 실패 ({single_processing_time:.2f}초): {e}")
                
                return {
                    "success": False,
                    "error": str(e),
                    "processing_time": single_processing_time,
                    "request_id": id(request)
                }
        
        # 모든 요청을 병렬로 처리
        tasks = [analyze_single(request) for request in req.requests]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 결과 처리
        successful_results = []
        failed_results = []
        
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                failed_results.append({
                    "index": i,
                    "error": str(result),
                    "request_id": id(req.requests[i])
                })
            elif result.get("success"):
                successful_results.append(result)
            else:
                failed_results.append(result)
        
        total_processing_time = time.time() - start_time
        
        logger.info(f"✅ 배치 분석 완료: 성공 {len(successful_results)}개, 실패 {len(failed_results)}개 ({total_processing_time:.2f}초)")
        
        return {
            "success": True,
            "results": {
                "successful": successful_results,
                "failed": failed_results
            },
            "summary": {
                "total_requests": len(req.requests),
                "successful_count": len(successful_results),
                "failed_count": len(failed_results),
                "success_rate": len(successful_results) / len(req.requests) if req.requests else 0,
                "total_processing_time": total_processing_time,
                "avg_processing_time": total_processing_time / len(req.requests) if req.requests else 0
            }
        }
        
    except Exception as e:
        total_processing_time = time.time() - start_time
        logger.error(f"❌ 배치 분석 실패 ({total_processing_time:.2f}초): {e}")
        
        return {
            "success": False,
            "error": str(e),
            "processing_time": total_processing_time
        }

@app.get("/")
async def root():
    """Railway 헬스체크용 루트 엔드포인트"""
    return {
        "message": "ETF AI Analysis Service is running",
        "status": "healthy",
        "service": "ETF AI Analysis Service",
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check():
    """AI 서버 상태 확인"""
    return {
        "status": "healthy",
        "service": "ETF AI Analysis Service",
        "timestamp": time.time(),
        "thread_pool_size": executor._max_workers
    }

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8001))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False) 