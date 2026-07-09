"""
schemas.py — API 数据模型（Pydantic）

定义所有 HTTP 接口的请求/响应数据结构。
与 models/*.py 中的领域模型解耦，但相互转换。
"""

from typing import List, Optional
from pydantic import BaseModel, Field


# ========== 通用响应 ==========

class ApiResponse(BaseModel):
    """通用响应包装"""
    success: bool = True
    message: str = "ok"
    data: Optional[dict] = None


class ErrorResponse(BaseModel):
    """错误响应"""
    success: bool = False
    error: str
    detail: Optional[str] = None


# ========== 天气 ==========

class WeatherResponse(BaseModel):
    """天气数据响应"""
    city: str
    date: str
    temp_now: float
    temp_min: float
    temp_max: float
    condition: str
    humidity: int
    wind_level: str
    forecast: List[str] = []
    source: str = "qweather"


class WeatherQueryRequest(BaseModel):
    """天气查询请求"""
    city: str = Field(..., min_length=1, description="城市名")


# ========== 新闻 ==========

class NewsItemResponse(BaseModel):
    """单条新闻"""
    title: str
    summary: str = ""
    source: str = ""
    category: str = "综合"
    url: str = ""
    publish_time: str = ""


class NewsQueryRequest(BaseModel):
    """新闻查询请求"""
    categories: List[str] = Field(default_factory=lambda: ["科技", "综合"])
    limit: int = Field(default=5, ge=1, le=50)


class NewsListResponse(BaseModel):
    """新闻列表响应"""
    items: List[NewsItemResponse]
    total: int


# ========== 偏好 ==========

class UserPrefsRequest(BaseModel):
    """用户偏好请求"""
    city: str = "北京"
    news_categories: List[str] = Field(default_factory=lambda: ["科技", "综合"])
    ai_model: str = "claude"
    briefing_time: str = "08:00"


class UserPrefsResponse(BaseModel):
    """用户偏好响应"""
    city: str
    news_categories: List[str]
    ai_model: str
    briefing_time: str


# ========== 简报 ==========

class BriefGenerateRequest(BaseModel):
    """简报生成请求"""
    city: Optional[str] = None
    model: Optional[str] = "claude"
    categories: Optional[List[str]] = None
    news_limit: int = Field(default=5, ge=1, le=20)
    use_stored_prefs: bool = True


class BriefResponse(BaseModel):
    """简报响应"""
    date: str
    city: str
    weather_summary: str
    digest: str
    model_used: str
    created_at: str
    news_items: List[NewsItemResponse] = []


# ========== AI 模型 ==========

class AIModelInfo(BaseModel):
    """AI 模型信息"""
    name: str
    display: str
    available: bool


class AIModelsResponse(BaseModel):
    """AI 模型列表响应"""
    models: List[AIModelInfo]


class ChatMessage(BaseModel):
    """聊天消息"""
    role: str  # user / assistant
    content: str


class ChatRequest(BaseModel):
    """直接调用 AI 聊天请求"""
    model: str = "claude"
    messages: List[ChatMessage]
    max_tokens: int = Field(default=2000, ge=1, le=8000)
    temperature: float = Field(default=0.7, ge=0, le=2)


class ChatResponse(BaseModel):
    """聊天响应"""
    content: str
    model: str
    usage: Optional[dict] = None


# ========== 健康检查 ==========

class HealthResponse(BaseModel):
    """健康检查响应"""
    status: str
    version: str
    storage_backend: str
    ai_models_available: List[str]
