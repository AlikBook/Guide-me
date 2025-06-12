from pydantic import BaseSettings

class Settings(BaseSettings):
    app_name: str = "FastAPI Metro Assistant"
    api_version: str = "1.0.0"
    debug: bool = True

    class Config:
        env_file = ".env"

settings = Settings()