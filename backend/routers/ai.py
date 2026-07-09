"""
ai.py — AI 模型管理 API 路由
"""

import logging
from fastapi import APIRouter, HTTPException

from backend.schemas import (
    AIModelsResponse, AIModelInfo,
    ChatRequest, ChatResponse,
)
from backend.services.anthropic_adapter import get_claude_service
from backend.services.ai_service import get_available_models

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/ai", tags=["ai"])


@router.get("/models", response_model=AIModelsResponse)
def list_models():
    """列出所有可用的 AI 模型"""
    try:
        models = get_available_models()
        return AIModelsResponse(
            models=[AIModelInfo(**m) for m in models]
        )
    except Exception as e:
        logger.error("列出 AI 模型失败: %s", str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    """直接调用 AI 模型对话（高级接口）

    用于让前端可以自定义提示词直接与 AI 对话，
    不依赖简报生成流程。
    """
    try:
        if req.model == "claude":
            service = get_claude_service()
            if not service.is_available:
                raise HTTPException(
                    status_code=503,
                    detail="Claude 服务不可用：请检查 ANTHROPIC_API_KEY 配置"
                )
            messages = [{"role": m.role, "content": m.content} for m in req.messages]
            content = service.chat(
                messages=messages,
                max_tokens=req.max_tokens,
                temperature=req.temperature,
            )
            return ChatResponse(content=content, model=req.model)
        else:
            raise HTTPException(
                status_code=400,
                detail=f"模型 {req.model} 的直接对话接口暂未实现，请使用 /api/brief/generate"
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error("AI chat 失败: %s", str(e))
        raise HTTPException(status_code=500, detail=str(e))
