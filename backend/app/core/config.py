from pydantic_settings import BaseSettings
from pathlib import Path

ENV_PATH = Path(__file__).parent.parent.parent.parent / ".env"
print(f"Looking for .env at: {ENV_PATH}")  # debug line

class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str = "threatlens-secret"
    CLAUDE_API_KEY: str = ""
    ABUSEIPDB_KEY: str = ""
    SLACK_WEBHOOK_URL: str = ""
    WAZUH_API_URL: str = ""
    WAZUH_USER: str = "admin"
    WAZUH_PASSWORD: str = ""

    class Config:
        env_file = str(ENV_PATH)

settings = Settings()