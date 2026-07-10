"""
weather_api.py — 天气数据获取模块

调用和风天气 (QWeather) API 获取实时天气和预报数据。

支持专属子账号（sub-host）的路径差异：
    公共账号路径: /v2/city/lookup
    专属子账号:   /geo/v2/city/lookup  (前缀多了 /geo/)

通过 QWEATHER_USE_GEO_PREFIX=true 自动启用专属子账号模式。

实现方：芦泓天
"""

import logging
import requests
import os
from datetime import datetime
from typing import Optional

from config.settings import settings
from config.constants import API_TIMEOUT
from models.weather import WeatherData

logger = logging.getLogger(__name__)


class WeatherAPIError(Exception):
    """天气 API 请求异常"""
    pass


# 公共域名
PUBLIC_GEO_HOST = "https://geoapi.qweather.com"
PUBLIC_DEV_HOST = "https://devapi.qweather.com"


def _is_sub_account() -> bool:
    """是否使用专属子账号模式
    
    当设置了 QWEATHER_API_HOST 或 QWEATHER_USE_GEO_PREFIX 时启用
    """
    return bool(
        os.environ.get("QWEATHER_API_HOST") or
        os.environ.get("QWEATHER_USE_GEO_PREFIX", "").lower() in ("true", "1", "yes")
    )


def _get_geo_host() -> str:
    """地理编码 Host"""
    custom = os.environ.get("QWEATHER_GEO_HOST") or os.environ.get("QWEATHER_API_HOST")
    if custom:
        return custom.rstrip("/")
    return PUBLIC_GEO_HOST


def _get_dev_host() -> str:
    """数据接口 Host"""
    custom = os.environ.get("QWEATHER_DEV_HOST") or os.environ.get("QWEATHER_API_HOST")
    if custom:
        return custom.rstrip("/")
    return PUBLIC_DEV_HOST


def _geo_path() -> str:
    """地理编码接口路径
    
    专属子账号需要 /geo 前缀
    """
    if _is_sub_account():
        return "/geo/v2/city/lookup"
    return "/v2/city/lookup"


def fetch_weather(city: str) -> WeatherData:
    """从和风天气 API 获取指定城市天气数据

    Args:
        city: 城市名

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

    url = f"{_get_geo_host()}{_geo_path()}"
    logger.debug("地理编码 URL: %s", url)

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

        if response.status_code != 200:
            raise WeatherAPIError(
                f"城市查询失败: HTTP {response.status_code}, body={response.text[:200]}"
            )

        data = response.json()

        if data.get("code") != "200":
            raise WeatherAPIError(
                f"城市查询失败: {data}"
            )

        return data["location"][0]["id"]


    except WeatherAPIError:
        raise
    except Exception as e:
        raise WeatherAPIError(
            f"城市查询异常: {e}"
        )


def _get_realtime_weather(location_id: str, api_key: str) -> dict:

    url = f"{_get_dev_host()}/v7/weather/now"

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

        if response.status_code != 200:
            raise WeatherAPIError(
                f"实时天气获取失败: HTTP {response.status_code}, body={response.text[:200]}"
            )

        data = response.json()


        if data.get("code") != "200":
            raise WeatherAPIError(
                f"实时天气获取失败:{data}"
            )

        return data

    except WeatherAPIError:
        raise
    except Exception as e:

        raise WeatherAPIError(
            f"实时天气请求异常:{e}"
        )

def _get_forecast(location_id: str, api_key: str) -> list:

    url = f"{_get_dev_host()}/v7/weather/7d"

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

        if response.status_code != 200:
            raise WeatherAPIError(
                f"天气预报获取失败: HTTP {response.status_code}, body={response.text[:200]}"
            )

        data = response.json()

        if data.get("code") != "200":
            raise WeatherAPIError(
                f"天气预报获取失败:{data}"
            )

        return data.get("daily", [])
    except WeatherAPIError:
        raise
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
