from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    redis_url: str = "redis://localhost:6379/0"
    chroma_dir: str = "./chroma_db"
    tts_voice: str = "alloy"
    asr_model: str = "small"
    groq_api_key: str = ""
    allowed_origins: str = "http://localhost:3000"
    upload_dir: str = "./uploads"

    class Config:
        env_file = ".env"


settings = Settings()