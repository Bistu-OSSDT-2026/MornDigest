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
    """地理编码：城市名 → location_id

    Args:
        city: 城市名
        api_key: API Key

    Returns:
        location_id 字符串

    Raises:
        WeatherAPIError: 请求失败或无结果
    """
    # TODO: 芦泓天 — 实现地理编码请求
    # 参考文档: https://dev.qweather.com/docs/api/reference/geo-api/
    # URL: https://geoapi.qweather.com/v2/city/lookup?location={city}&key={api_key}
    # 返回示例: {"code":"200","location":[{"id":"101010100","name":"北京","adm2":"北京",...}]}
    # 取 location[0]["id"] 即可
    raise WeatherAPIError("天气地理编码接口待实现")


def _get_realtime_weather(location_id: str, api_key: str) -> dict:
    """获取实时天气

    Args:
        location_id: 城市 location_id
        api_key: API Key

    Returns:
        解析后的 JSON dict

    Raises:
        WeatherAPIError: 请求失败
    """
    # TODO: 芦泓天 — 实现实时天气请求
    # 参考文档: https://dev.qweather.com/docs/api/weather/weather-now/
    # URL: https://devapi.qweather.com/v7/weather/now?location={id}&key={api_key}
    # 返回示例: {"code":"200","now":{"temp":"25","icon":"100","text":"晴","feelsLike":"26","humidity":"45","windDir":"东南","windScale":"3",...}}
    raise WeatherAPIError("实时天气接口待实现")


def _get_forecast(location_id: str, api_key: str) -> list:
    """获取天气预报

    Args:
        location_id: 城市 location_id
        api_key: API Key

    Returns:
        未来 N 日预报数据列表

    Raises:
        WeatherAPIError: 请求失败
    """
    # TODO: 芦泓天 — 实现预报请求
    # 参考文档: https://dev.qweather.com/docs/api/weather/weather-forecast/
    # URL: https://devapi.qweather.com/v7/weather/7d?location={id}&key={api_key}
    # 返回示例: {"code":"200","daily":[{"fxDate":"2026-07-09","tempMax":"28","tempMin":"18","iconDay":"100","textDay":"晴","iconNight":"101","textNight":"多云",...}, ...]}
    raise WeatherAPIError("天气预报接口待实现")


def _build_weather_data(city: str, now_data: dict, forecast_data: list) -> WeatherData:
    """组装标准 WeatherData 对象

    Args:
        city: 城市名
        now_data: 实时天气 JSON
        forecast_data: 预报数据列表

    Returns:
        WeatherData 对象
    """
    # TODO: 芦泓天 — 解析 now_data 和 forecast_data 字段
    # 组装 forecast 文本，如 ["明天: 晴 15-20°", "后天: 多云 13-18°"]

    weather = WeatherData()
    weather.city = city
    weather.date = datetime.now().strftime("%Y-%m-%d")
    weather.timestamp = datetime.now()
    weather.source = "qweather"

    # TODO: 填充以下字段 (芦泓天)
    # weather.temp_now = float(now_data["now"]["temp"])
    # weather.temp_min = float(forecast_data[0]["tempMin"])
    # weather.temp_max = float(forecast_data[0]["tempMax"])
    # weather.condition = now_data["now"]["text"]
    # weather.humidity = int(now_data["now"]["humidity"])
    # weather.wind_level = now_data["now"]["windScale"] + "级"
    # for day in forecast_data[1:4]:
    #     weather.forecast.append(f"{day['fxDate']}: {day['textDay']} {day['tempMin']}-{day['tempMax']}°")

    return weather
