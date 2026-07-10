"""
test_backend.py — 后端 API 集成测试

需要先启动后端服务：
    uvicorn backend.main:app --port 8000

然后运行：
    pytest tests/test_backend.py -v
"""

import pytest
import httpx

BASE_URL = "http://localhost:8000"


@pytest.fixture
def client():
    return httpx.Client(base_url=BASE_URL, timeout=30.0)


def test_health(client):
    """测试健康检查"""
    resp = client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert "version" in data
    print(f"✅ 健康检查通过: {data}")


def test_api_info(client):
    """测试 API 元信息"""
    resp = client.get("/api/info")
    assert resp.status_code == 200
    data = resp.json()
    assert "endpoints" in data
    assert data["name"] == "MornDigest"


def test_list_ai_models(client):
    """测试列出 AI 模型"""
    resp = client.get("/api/ai/models")
    assert resp.status_code == 200
    data = resp.json()
    assert "models" in data
    print(f"📋 可用模型: {[m['name'] for m in data['models']]}")


def test_get_prefs(client):
    """测试获取偏好"""
    resp = client.get("/api/prefs")
    assert resp.status_code == 200
    data = resp.json()
    assert "city" in data
    assert "ai_model" in data


def test_save_and_load_prefs(client):
    """测试保存和读取偏好"""
    new_prefs = {
        "city": "上海",
        "ai_model": "claude",
        "news_categories": ["科技", "体育"],
        "briefing_time": "09:00"
    }
    # 保存
    resp = client.post("/api/prefs", json=new_prefs)
    assert resp.status_code == 200

    # 读取
    resp = client.get("/api/prefs")
    assert resp.status_code == 200
    data = resp.json()
    assert data["city"] == "上海"
    assert "科技" in data["news_categories"]


def test_reset_prefs(client):
    """测试重置偏好"""
    resp = client.post("/api/prefs/reset")
    assert resp.status_code == 200
    data = resp.json()
    assert data["city"] == "北京"


def test_history(client):
    """测试历史简报列表"""
    resp = client.get("/api/brief/history?limit=5")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    print(f"📚 历史简报数量: {len(data)}")


@pytest.mark.skipif(
    True, reason="需要有效的 QWEATHER_KEY 和 NEWS_KEY 才能运行"
)
def test_generate_brief(client):
    """测试生成简报（需要 API Key）"""
    resp = client.post("/api/brief/generate", json={
        "city": "北京",
        "model": "claude",
        "categories": ["科技"],
        "news_limit": 3,
        "use_stored_prefs": False
    })
    assert resp.status_code == 200
    data = resp.json()
    assert "digest" in data
    assert data["city"] == "北京"
