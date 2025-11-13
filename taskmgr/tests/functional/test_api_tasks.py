import pytest
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_create_and_list_tasks():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        rp = await ac.post("/api/v1/projects", json={"name":"P"})
        assert rp.status_code == 200
        rt = await ac.post("/api/v1/tags", json={"name":"urgent"})
        tag_id = rt.json()["id"]
        res = await ac.post("/api/v1/tasks", json={"title":"X","project_id":rp.json()["id"],"tag_ids":[tag_id]})
        assert res.status_code == 200
        lst = await ac.get("/api/v1/tasks", params={"q":"X"})
        assert any(t["title"]=="X" for t in lst.json())
