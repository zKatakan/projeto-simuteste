from app.repositories.tag_repo import TagRepo

class TagService:
    def __init__(self, repo: TagRepo):
        self.repo = repo
