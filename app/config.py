from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    openweather_api_key: str
    database_url: str = "sqlite:///./events.db"

    class Config:
        env_file = ".env"

settings = Settings()