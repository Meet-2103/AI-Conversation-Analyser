from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    GOOGLE_API_KEY: str = "sk-placeholder"
    MODEL_NAME: str = "gemini-3.6-flash"
    
    class Config:
        env_file = ".env"

settings = Settings()
