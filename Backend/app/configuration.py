from functools import lru_cache

from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict
)


class Settings(BaseSettings):

    groq_api_key: str
    tavily_api_key: str

    model_name: str = (
        "llama-3.3-70b-versatile"
    )

    app_name: str = (
        "Advanced AI Agent Capstone"
    )

    database_path: str = (
        "agent_state.db"
    )

    reports_dir: str = (
        "../data/reports"
    )

    documents_dir: str = (
        "../data/documents"
    )

    cors_origins: str = (
        "http://localhost:5173"
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )

    @property
    def cors_origin_list(self):

        return [
            origin.strip()
            for origin in self.cors_origins.split(",")
            if origin.strip()
        ]


@lru_cache
def get_settings():

    return Settings()


settings = get_settings()