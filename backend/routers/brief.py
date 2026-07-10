"""
brief.py — 简报生成 & 历史 API 路由
"""

import logging
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query

from backend.schemas import BriefGenerateRequest, BriefResponse, NewsItemResponse
from backend.services.ai_service import generate_brief_with_model
from api.weather_api import fetch_weather, WeatherAPIError
from api.news_api import fetch_news, NewsAPIError
from models.prefs import UserPrefs
from storage import create_storage

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/brief", tags=["brief"])


@router.post("/generate", response_model=BriefResponse)
def generate_brief(req: BriefGenerateRequest):
    """生成晨间简报

    完整流程：
        1. 加载偏好（若 use_stored_prefs=True 且未提供显式参数）
        2. 获取天气
        3. 获取新闻
        4. 调用 AI 生成简报
        5. 保存到存储
        6. 返回简报
    """
    try:
        # 解析参数优先级：显式参数 > 存储偏好 > 默认值
        if req.use_stored_prefs:
            storage = create_storage()
            prefs = storage.load_prefs()
        else:
            prefs = UserPrefs.default()

        city = req.city or prefs.city
        model = req.model or prefs.ai_model
        categories = req.categories or prefs.news_categories

        logger.info("生成简报: city=%s, model=%s, categories=%s",
                    city, model, categories)

        # 1. 获取天气
        weather = fetch_weather(city)
        # 2. 获取新闻
        news_items = fetch_news(categories, limit=req.news_limit)
        # 3. AI 生成
        brief = generate_brief_with_model(model, weather, news_items)
        # 4. 保存（降级处理：失败不影响返回）
        try:
            storage = create_storage()
            storage.save_brief(brief)
        except Exception as e:
            logger.warning("保存简报失败（不影响展示）: %s", str(e))

        return BriefResponse(
            date=brief.date,
            city=brief.city,
            weather_summary=brief.weather_summary,
            digest=brief.digest,
            model_used=brief.model_used,
            created_at=brief.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            news_items=[
                NewsItemResponse(
                    title=n.title, summary=n.summary, source=n.source,
                    category=n.category, url=n.url, publish_time=n.publish_time,
                )
                for n in brief.news_items
            ],
        )

    except WeatherAPIError as e:
        raise HTTPException(status_code=502, detail=f"天气服务异常: {e}")
    except NewsAPIError as e:
        raise HTTPException(status_code=502, detail=f"新闻服务异常: {e}")
    except Exception as e:
        logger.error("生成简报失败: %s", str(e), exc_info=True)
        raise HTTPException(status_code=500, detail=f"生成简报失败: {e}")


@router.get("/history", response_model=List[BriefResponse])
def list_briefs(limit: int = Query(default=10, ge=1, le=100)):
    """获取历史简报列表（按时间倒序）"""
    try:
        storage = create_storage()
        briefs = storage.list_briefs(limit)
        return [
            BriefResponse(
                date=b.date,
                city=b.city,
                weather_summary=b.weather_summary,
                digest=b.digest,
                model_used=b.model_used,
                created_at=b.created_at.strftime("%Y-%m-%d %H:%M:%S") if b.created_at else "",
                news_items=[
                    NewsItemResponse(
                        title=n.title, summary=n.summary, source=n.source,
                        category=n.category, url=n.url, publish_time=n.publish_time,
                    )
                    for n in b.news_items
                ],
            )
            for b in briefs
        ]
    except Exception as e:
        logger.error("获取历史失败: %s", str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history/{date}", response_model=BriefResponse)
def get_brief_by_date(date: str):
    """按日期获取简报（YYYY-MM-DD）"""
    try:
        storage = create_storage()
        brief = storage.get_brief(date)
        if not brief:
            raise HTTPException(status_code=404, detail=f"未找到 {date} 的简报")
        return BriefResponse(
            date=brief.date,
            city=brief.city,
            weather_summary=brief.weather_summary,
            digest=brief.digest,
            model_used=brief.model_used,
            created_at=brief.created_at.strftime("%Y-%m-%d %H:%M:%S") if brief.created_at else "",
            news_items=[
                NewsItemResponse(
                    title=n.title, summary=n.summary, source=n.source,
                    category=n.category, url=n.url, publish_time=n.publish_time,
                )
                for n in brief.news_items
            ],
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error("查询简报失败: %s", str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/export/{date}")
def export_brief(date: str):
    """导出指定日期简报为 Markdown 文本"""
    try:
        storage = create_storage()
        brief = storage.get_brief(date)
        if not brief:
            raise HTTPException(status_code=404, detail=f"未找到 {date} 的简报")

        md = f"""# MornDigest 简报 — {brief.date}

## 🌤 天气摘要
{brief.weather_summary}

## ✨ 智能简报
{brief.digest}

## 📰 新闻列表

"""
        for i, n in enumerate(brief.news_items, 1):
            md += f"### {i}. {n.title}\n"
            md += f"**来源**: {n.source} | **时间**: {n.publish_time} | **分类**: {n.category}\n\n"
            if n.summary:
                md += f"{n.summary}\n\n"
            if n.url:
                md += f"[阅读原文]({n.url})\n\n"

        md += f"\n---\n*生成模型: {brief.model_used}*\n"
        md += f"*生成时间: {brief.created_at.strftime('%Y-%m-%d %H:%M:%S') if brief.created_at else ''}*\n"

        from fastapi.responses import PlainTextResponse
        return PlainTextResponse(
            content=md,
            media_type="text/markdown",
            headers={"Content-Disposition": f'attachment; filename="brief-{date}.md"'},
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error("导出简报失败: %s", str(e))
        raise HTTPException(status_code=500, detail=str(e))
