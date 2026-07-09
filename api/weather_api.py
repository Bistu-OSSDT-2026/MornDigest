"""
weather_api.py — 天气数据获取模块

调用和风天气 (QWeather) API 获取实时天气和预报数据，
解析后返回标准化的 WeatherData 对象。

实现方：芦泓天
"""

import logging
import requests
from datetime import datetime
from typing import Optional

from config.settings import settings
from config.constants import API_TIMEOUT
from models.weather import WeatherData

logger = logging.getLogger(__name__)


class WeatherAPIError(Exception):
    """天气 API 请求异常"""
    pass


def fetch_weather(city: str) -> WeatherData:
    """从和风天气 API 获取指定城市天气数据

    步骤：
        1. 调用地理编码接口获取 location_id
        2. 调用实时天气接口获取当前天气
        3. 调用预报接口获取未来 N 日数据
        4. 解析并组装为标准 WeatherData 对象返回

    Args:
        city: 城市名，如 "北京"

    Returns:
        WeatherData: 标准化天气数据对象

    Raises:
        WeatherAPIError: 当 API Key 未配置或请求失败时抛出
    """
    api_key = settings.get("QWEATHER_KEY")
    if not api_key:
        raise WeatherAPIError("和风天气 API Key (QWEATHER_KEY) 未配置，请在 .env 文件中设置")

    # 步骤 1: 获取 location_id
    location_id = _get_location_id(city, api_key)

    # 步骤 2: 获取实时天气
    now_data = _get_realtime_weather(location_id, api_key)

    # 步骤 3: 获取预报
    forecast_data = _get_forecast(location_id, api_key)

    # 步骤 4: 组装返回
    weather = _build_weather_data(city, now_data, forecast_data)

    if not weather.is_valid():
        logger.warning("天气数据不完整，返回部分数据: city=%s", city)

    logger.info("成功获取天气数据: city=%s, condition=%s", city, weather.condition)
    return weather


def _get_location_id(city: str, api_key: str) -> str:
    """城市名转换location_id"""

    url = "https://geoapi.qweather.com/v2/city/lookup"

    params = {
        "location": city,
        "key": api_key
    }

    try:
        response = requests.get(
            url,
            params=params,
            timeout=API_TIMEOUT
        )

        data = response.json()

        if data.get("code") != "200":
            raise WeatherAPIError(
                f"城市查询失败: {data}"
            )

        return data["location"][0]["id"]


    except Exception as e:
        raise WeatherAPIError(
            f"城市查询异常: {e}"
        )


def _get_realtime_weather(location_id: str, api_key: str) -> dict:

    url = "https://devapi.qweather.com/v7/weather/now"

    params = {
        "location": location_id,
        "key": api_key
    }
    try:

        response = requests.get(
            url,
            params=params,
            timeout=API_TIMEOUT
        )

        data = response.json()


        if data.get("code") != "200":
            raise WeatherAPIError(
                f"实时天气获取失败:{data}"
            )

        return data

    except Exception as e:

        raise WeatherAPIError(
            f"实时天气请求异常:{e}"
        )

def _get_forecast(location_id: str, api_key: str) -> list:

    url = "https://devapi.qweather.com/v7/weather/7d"

    params = {
        "location": location_id,
        "key": api_key
    }

    try:

        response = requests.get(
            url,
            params=params,
            timeout=API_TIMEOUT
        )

        data = response.json()

        if data.get("code") != "200":
            raise WeatherAPIError(
                f"天气预报获取失败:{data}"
            )

        return data.get("daily", [])
    except Exception as e:

        raise WeatherAPIError(
            f"天气预报请求异常:{e}"
        )

def _build_weather_data(city: str, now_data: dict, forecast_data: list) -> WeatherData:
    """组装标准 WeatherData 对象

    Args:
        city: 城市名
        now_data: 实时天气 JSON
        forecast_data: 预报数据列表

    Returns:
        WeatherData 对象
    """
    # 解析 now_data 和 forecast_data 字段
    # 组装 forecast 文本，如 ["明天: 晴 15-20°", "后天: 多云 13-18°"]

    weather = WeatherData()
    weather.city = city
    weather.date = datetime.now().strftime("%Y-%m-%d")
    weather.timestamp = datetime.now()
    weather.source = "qweather"

    now = now_data["now"]

    weather.temp_now = float(now.get("temp", 0))

    if forecast_data:
        weather.temp_min = float(
            forecast_data[0].get("tempMin", 0)
        )

        weather.temp_max = float(
            forecast_data[0].get("tempMax", 0)
        )

    weather.condition = now.get(
        "text",
        "未知"
    )

    weather.humidity = int(
        now.get("humidity", 0)
    )

    weather.wind_level = (
        now.get("windScale", "")
        + "级"
    )

    for day in forecast_data[1:4]:
        weather.forecast.append(
            f"{day['fxDate']}: "
            f"{day['textDay']} "
            f"{day['tempMin']}-"
            f"{day['tempMax']}°"
        )

    return weather
