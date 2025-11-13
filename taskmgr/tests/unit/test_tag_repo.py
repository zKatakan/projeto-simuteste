from sqlmodel import Session
from app.models.db import create_db_and_tables, engine
from app.models.entities import Tag
from app.repositories.tag_repo import TagRepo

def test_tag_crud_basic():
    create_db_and_tables()
    with Session(engine) as s:
        repo = TagRepo(s)
        t = repo.create(Tag(name="urgent"))
        assert t.id is not None
        assert repo.get(t.id).name == "urgent"
