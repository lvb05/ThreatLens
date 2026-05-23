from pydantic_settings import BaseSettings
from pathlib import Path

ENV_PATH = Path(__file__).parent.parent.parent.parent / ".env"

class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str = "threatlens-jwt-secret"
    CLAUDE_API_KEY: str = ""
    ABUSEIPDB_KEY: str = ""
    SLACK_WEBHOOK_URL: str = ""
    WAZUH_API_URL: str = ""
    WAZUH_USER: str = "admin"
    WAZUH_PASSWORD: str = ""
    GROQ_API_KEY: str = ""
    ENV: str = "development"

    class Config:
        env_file = str(ENV_PATH)
        env_file_encoding = "utf-8"
        extra = "ignore"

settings = Settings()
print(f"Looking for .env at: {ENV_PATH}")
