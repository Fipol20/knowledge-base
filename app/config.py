from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = "sqlite:///./kb.db"
    duplicate_threshold: float = 0.6
    default_search_top_k: int = 10

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
