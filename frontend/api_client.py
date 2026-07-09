"""
api_client.py — 前端 HTTP 客户端

Streamlit 前端通过此客户端调用 FastAPI 后端的所有接口。
所有方法返回统一格式：{"success": bool, "data": ..., "error": ...}
"""

import os
import logging
import httpx
from typing import Optional, List

logger = logging.getLogger(__name__)

# 后端地址（可通过环境变量覆盖）
API_BASE_URL = os.environ.get("MORNDIGEST_API_URL", "http://127.0.0.1:8000")
API_TIMEOUT = float(os.environ.get("MORNDIGEST_API_TIMEOUT", "60"))


class APIClient:
    """FastAPI 后端 HTTP 客户端"""

    def __init__(self, base_url: str = API_BASE_URL, timeout: float = API_TIMEOUT):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self._client = httpx.Client(base_url=self.base_url, timeout=self.timeout)

    def _request(self, method: str, path: str, **kwargs) -> dict:
        """统一请求方法"""
        try:
            resp = self._client.request(method, path, **kwargs)
            resp.raise_for_status()
            return {"success": True, "data": resp.json(), "status": resp.status_code}
        except httpx.HTTPStatusError as e:
            error_detail = "未知错误"
            try:
                error_detail = e.response.json().get("detail", str(e))
            except Exception:
                error_detail = e.response.text or str(e)
            logger.error("API 错误 [%s %s]: %s", method, path, error_detail)
            return {
                "success": False,
                "error": str(error_detail),
                "status": e.response.status_code,
            }
        except httpx.RequestError as e:
            logger.error("API 连接错误 [%s %s]: %s", method, path, str(e))
            return {
                "success": False,
                "error": f"无法连接到后端服务 ({self.base_url}): {str(e)}",
                "status": 0,
            }
        except Exception as e:
            logger.error("API 未知错误 [%s %s]: %s", method, path, str(e))
            return {"success": False, "error": f"未知错误: {str(e)}", "status": 500}

    # ===== 健康检查 =====
    def health(self) -> dict:
        return self._request("GET", "/health")

    # ===== AI 模型 =====
    def list_ai_models(self) -> dict:
        return self._request("GET", "/api/ai/models")

    # ===== 偏好 =====
    def get_prefs(self) -> dict:
        return self._request("GET", "/api/prefs")

    def save_prefs(self, city: str, ai_model: str,
                   news_categories: List[str], briefing_time: str = "08:00") -> dict:
        return self._request("POST", "/api/prefs", json={
            "city": city,
            "ai_model": ai_model,
            "news_categories": news_categories,
            "briefing_time": briefing_time,
        })

    def reset_prefs(self) -> dict:
        return self._request("POST", "/api/prefs/reset")

    # ===== 简报 =====
    def generate_brief(self, city: Optional[str] = None,
                       model: Optional[str] = None,
                       categories: Optional[List[str]] = None,
                       news_limit: int = 5,
                       use_stored_prefs: bool = False) -> dict:
        return self._request("POST", "/api/brief/generate", json={
            "city": city,
            "model": model,
            "categories": categories,
            "news_limit": news_limit,
            "use_stored_prefs": use_stored_prefs,
        })

    def list_history(self, limit: int = 10) -> dict:
        return self._request("GET", f"/api/brief/history?limit={limit}")

    def get_brief(self, date: str) -> dict:
        return self._request("GET", f"/api/brief/history/{date}")

    # ===== 天气 & 新闻 =====
    def query_weather(self, city: str) -> dict:
        return self._request("POST", "/api/weather/query", json={"city": city})

    def query_news(self, categories: List[str], limit: int = 5) -> dict:
        return self._request("POST", "/api/news/query",
                             json={"categories": categories, "limit": limit})


# 全局单例
_client: Optional[APIClient] = None


def get_client() -> APIClient:
    """获取 API 客户端单例"""
    global _client
    if _client is None:
        _client = APIClient()
    return _client
