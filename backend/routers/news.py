"""
news.py — 新闻 API 路由
"""

import logging
from fastapi import APIRouter, HTTPException

from backend.schemas import NewsQueryRequest, NewsItemResponse, NewsListResponse
from api.news_api import fetch_news, NewsAPIError

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/news", tags=["news"])


@router.post("/query", response_model=NewsListResponse)
def query_news(req: NewsQueryRequest):
    """按分类查询新闻列表"""
    try:
        items = fetch_news(req.categories, limit=req.limit)
        return NewsListResponse(
            items=[
                NewsItemResponse(
                    title=i.title,
                    summary=i.summary,
                    source=i.source,
                    category=i.category,
                    url=i.url,
                    publish_time=i.publish_time,
                )
                for i in items
            ],
            total=len(items),
        )
    except NewsAPIError as e:
        logger.error("新闻 API 错误: %s", str(e))
        raise HTTPException(status_code=502, detail=f"新闻服务异常: {str(e)}")
    except Exception as e:
        logger.error("新闻查询失败: %s", str(e))
        raise HTTPException(status_code=500, detail=f"服务器内部错误: {str(e)}")
