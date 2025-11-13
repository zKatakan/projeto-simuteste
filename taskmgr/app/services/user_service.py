from app.repositories.user_repo import UserRepo

class UserService:
    def __init__(self, repo: UserRepo):
        self.repo = repo
