"""
weather.py — 天气数据模型

定义 WeatherData 标准数据类，所有天气模块返回此类型。
"""

from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Optional


@dataclass
class WeatherData:
    """天气数据标准结构

    所有天气 API 调用模块（api/weather_api.py）必须返回此类型。

    Attributes:
        city: 城市名，如 "北京"
        date: 日期，格式 YYYY-MM-DD
        temp_now: 当前温度 (°C)
        temp_min: 当日最低温度 (°C)
        temp_max: 当日最高温度 (°C)
        condition: 天气状况（晴/多云/阴/雨/雪等）
        humidity: 相对湿度 (%)
        wind_level: 风力等级，如 "3级"
        forecast: 未来 N 日简况列表
        source: 数据来源标识，固定 "qweather"
        timestamp: 数据获取时间
    """

    city: str = ""
    date: str = ""
    temp_now: float = 0.0
    temp_min: float = 0.0
    temp_max: float = 0.0
    condition: str = ""
    humidity: int = 0
    wind_level: str = ""
    forecast: list = field(default_factory=list)
    source: str = "qweather"
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> dict:
        """转为字典格式"""
        d = asdict(self)
        if isinstance(d.get("timestamp"), datetime):
            d["timestamp"] = d["timestamp"].strftime("%Y-%m-%dT%H:%M:%S")
        return d

    @classmethod
    def from_dict(cls, data: dict) -> "WeatherData":
        """从字典创建实例"""
        ts = data.get("timestamp")
        if isinstance(ts, str):
            try:
                ts = datetime.fromisoformat(ts)
            except ValueError:
                ts = datetime.now()
        return cls(
            city=data.get("city", ""),
            date=data.get("date", ""),
            temp_now=data.get("temp_now", 0.0),
            temp_min=data.get("temp_min", 0.0),
            temp_max=data.get("temp_max", 0.0),
            condition=data.get("condition", ""),
            humidity=data.get("humidity", 0),
            wind_level=data.get("wind_level", ""),
            forecast=data.get("forecast", []),
            source=data.get("source", "qweather"),
            timestamp=ts,
        )

    def summary_text(self) -> str:
        """生成简短天气摘要文本"""
        parts = [f"今天{self.date} {self.city}{self.condition}"]
        if self.temp_now:
            parts.append(f"当前温度 {self.temp_now}°C")
        if self.temp_min and self.temp_max:
            parts.append(f"气温 {self.temp_min}-{self.temp_max}°C")
        if self.humidity:
            parts.append(f"湿度 {self.humidity}%")
        if self.wind_level:
            parts.append(f"风力 {self.wind_level}")
        return "，".join(parts)

    def is_valid(self) -> bool:
        """校验数据完整性"""
        return bool(self.city and self.condition and self.temp_now)
