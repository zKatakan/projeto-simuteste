import pytest
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_project_progress_and_archive_rule():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        p = (await ac.post("/api/v1/projects", json={"name":"P"})).json()
        await ac.post("/api/v1/tasks", json={"title":"T1","project_id":p["id"],"status":"DONE","priority":5})
        await ac.post("/api/v1/tasks", json={"title":"T2","project_id":p["id"],"priority":1})
        prog = (await ac.get(f"/api/v1/projects/{p['id']}/progress")).json()
        assert prog["progress"] == 50.0
        can = (await ac.get(f"/api/v1/projects/{p['id']}/can-archive")).json()
        assert can["can_archive"] is False
