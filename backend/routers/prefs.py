"""
prefs.py — 用户偏好 API 路由
"""

import logging
from fastapi import APIRouter, HTTPException

from backend.schemas import UserPrefsRequest, UserPrefsResponse
from models.prefs import UserPrefs
from storage import create_storage

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/prefs", tags=["prefs"])


@router.get("", response_model=UserPrefsResponse)
def get_prefs():
    """获取当前用户偏好"""
    try:
        storage = create_storage()
        prefs = storage.load_prefs()
        return UserPrefsResponse(
            city=prefs.city,
            news_categories=prefs.news_categories,
            ai_model=prefs.ai_model,
            briefing_time=prefs.briefing_time,
        )
    except Exception as e:
        logger.error("读取偏好失败: %s", str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("", response_model=UserPrefsResponse)
def save_prefs(req: UserPrefsRequest):
    """保存用户偏好"""
    try:
        storage = create_storage()
        prefs = UserPrefs(
            city=req.city,
            news_categories=req.news_categories,
            ai_model=req.ai_model,
            briefing_time=req.briefing_time,
        )
        storage.save_prefs(prefs)
        logger.info("偏好已保存: city=%s, model=%s", prefs.city, prefs.ai_model)
        return UserPrefsResponse(
            city=prefs.city,
            news_categories=prefs.news_categories,
            ai_model=prefs.ai_model,
            briefing_time=prefs.briefing_time,
        )
    except Exception as e:
        logger.error("保存偏好失败: %s", str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/reset", response_model=UserPrefsResponse)
def reset_prefs():
    """重置为默认偏好"""
    try:
        storage = create_storage()
        prefs = UserPrefs.default()
        storage.save_prefs(prefs)
        logger.info("偏好已重置为默认")
        return UserPrefsResponse(
            city=prefs.city,
            news_categories=prefs.news_categories,
            ai_model=prefs.ai_model,
            briefing_time=prefs.briefing_time,
        )
    except Exception as e:
        logger.error("重置偏好失败: %s", str(e))
        raise HTTPException(status_code=500, detail=str(e))
