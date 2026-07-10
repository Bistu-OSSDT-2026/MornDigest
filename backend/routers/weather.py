"""
weather.py — 天气 API 路由
"""

import logging
from fastapi import APIRouter, HTTPException

from backend.schemas import WeatherQueryRequest, WeatherResponse
from api.weather_api import fetch_weather, WeatherAPIError

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/weather", tags=["weather"])


@router.post("/query", response_model=WeatherResponse)
def query_weather(req: WeatherQueryRequest):
    """查询指定城市的天气"""
    try:
        weather = fetch_weather(req.city)
        return WeatherResponse(
            city=weather.city,
            date=weather.date,
            temp_now=weather.temp_now,
            temp_min=weather.temp_min,
            temp_max=weather.temp_max,
            condition=weather.condition,
            humidity=weather.humidity,
            wind_level=weather.wind_level,
            forecast=weather.forecast,
            source=weather.source,
        )
    except WeatherAPIError as e:
        logger.error("天气 API 错误: %s", str(e))
        raise HTTPException(status_code=502, detail=f"天气服务异常: {str(e)}")
    except Exception as e:
        logger.error("天气查询失败: %s", str(e))
        raise HTTPException(status_code=500, detail=f"服务器内部错误: {str(e)}")
