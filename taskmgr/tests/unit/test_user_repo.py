from sqlmodel import Session
from app.models.db import create_db_and_tables, engine
from app.models.entities import User
from app.repositories.user_repo import UserRepo

def test_user_crud_basic():
    create_db_and_tables()
    with Session(engine) as s:
        repo = UserRepo(s)
        u = repo.create(User(name="Ana", email="ana@x.com"))
        assert u.id is not None
        assert repo.get(u.id).email == "ana@x.com"
