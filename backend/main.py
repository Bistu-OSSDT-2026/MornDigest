"""
main.py — FastAPI 后端入口

启动方式：
    cd /Users/lhtt/Desktop/MornDigest
    uvicorn backend.main:app --reload --port 8000

    或：
    python -m backend.main

API 文档：
    http://localhost:8000/docs       (Swagger UI)
    http://localhost:8000/redoc      (ReDoc)

健康检查：
    GET  /health
"""

import os
import sys
import logging
from pathlib import Path

# ===== 路径设置 =====
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# 加载 .env
from dotenv import load_dotenv
env_path = project_root / ".env"
if env_path.exists():
    load_dotenv(env_path)

# ===== 日志配置 =====
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("mornigest.api")

# ===== FastAPI =====
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from config.settings import settings
from config.constants import APP_NAME, APP_VERSION, DEFAULT_STORAGE_BACKEND
from backend.schemas import HealthResponse
from backend.routers import brief, prefs, weather, news, ai
from backend.services.anthropic_adapter import get_claude_service

app = FastAPI(
    title=f"{APP_NAME} API",
    description="AI 晨间智能简报工具 - 后端 API",
    version=APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
)

# ===== CORS =====
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ===== 注册路由 =====
app.include_router(weather.router)
app.include_router(news.router)
app.include_router(prefs.router)
app.include_router(brief.router)
app.include_router(ai.router)

# ===== 静态前端（可选）=====
web_dir = project_root / "web"
if web_dir.exists():
    app.mount("/static", StaticFiles(directory=str(web_dir)), name="static")

    @app.get("/", include_in_schema=False)
    def serve_index():
        index_file = web_dir / "index.html"
        if index_file.exists():
            return FileResponse(str(index_file))
        return {"message": f"{APP_NAME} API 运行中", "docs": "/docs"}


# ===== 健康检查 =====
@app.get("/health", response_model=HealthResponse, tags=["meta"])
def health_check():
    """健康检查端点"""
    claude = get_claude_service()
    backend = settings.get("STORAGE_BACKEND", DEFAULT_STORAGE_BACKEND)

    available_models = []
    if claude.is_available:
        available_models.append("claude")

    return HealthResponse(
        status="ok",
        version=APP_VERSION,
        storage_backend=backend,
        ai_models_available=available_models,
    )


@app.get("/api/info", tags=["meta"])
def api_info():
    """API 元信息"""
    return {
        "name": APP_NAME,
        "version": APP_VERSION,
        "endpoints": {
            "weather_query": "POST /api/weather/query",
            "news_query": "POST /api/news/query",
            "prefs_get": "GET /api/prefs",
            "prefs_save": "POST /api/prefs",
            "prefs_reset": "POST /api/prefs/reset",
            "brief_generate": "POST /api/brief/generate",
            "brief_history": "GET /api/brief/history",
            "brief_by_date": "GET /api/brief/history/{date}",
            "brief_export": "GET /api/brief/export/{date}",
            "ai_models": "GET /api/ai/models",
            "ai_chat": "POST /api/ai/chat",
            "health": "GET /health",
        }
    }


# ===== 启动 =====
if __name__ == "__main__":
    import uvicorn
    logger.info("=" * 60)
    logger.info("启动 %s API 服务", APP_NAME)
    logger.info("=" * 60)
    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )
