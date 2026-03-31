from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
import os

BASE_DIR = Path(__file__).resolve().parent
ENV_PATH = BASE_DIR / ".env"   # app/.env 기준
print("DEBUG os.getenv('OLLAMA_HOST') =", os.getenv("OLLAMA_HOST"))

print("DEBUG settings.py 위치:", __file__)
print("DEBUG 기대하는 env 위치:", ENV_PATH)
print("DEBUG env 존재 여부:", ENV_PATH.exists())

class Settings(BaseSettings):
    neo4j_uri: str
    neo4j_user: str
    neo4j_password: str
    ollama_host: str

    model_config = SettingsConfigDict(
        env_file=ENV_PATH,
        env_file_encoding="utf-8",
    )

settings = Settings()

print("DEBUG 최종 ollama_host:", settings.ollama_host)