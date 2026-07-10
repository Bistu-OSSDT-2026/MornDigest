"""
backend — MornDigest FastAPI 后端

提供 RESTful API：
    - /api/weather/query
    - /api/news/query
    - /api/prefs (GET/POST/reset)
    - /api/brief/generate
    - /api/brief/history
    - /api/brief/export/{date}
    - /api/ai/models
    - /api/ai/chat
    - /health
    - /docs (Swagger UI)

启动：
    uvicorn backend.main:app --reload --port 8000
"""
