from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./data/taskmgr.db"
    MAX_OPEN_TASKS_PER_USER: int = 1
    LOG_LEVEL: str = "INFO"
    FILE_STORAGE_DIR: str = "./data/files"
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

settings = Settings()
