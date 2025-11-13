import pytest
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_rule_no_assignee_done():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        p = (await ac.post("/api/v1/projects", json={"name":"P"})).json()
        t = (await ac.post("/api/v1/tasks", json={"title":"T","project_id":p["id"]})).json()
        res = await ac.patch(f"/api/v1/tasks/{t['id']}/status", params={"new_status":"DONE"})
        assert res.status_code == 422
