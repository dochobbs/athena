from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings
from pydantic import ConfigDict


class Settings(BaseSettings):
  model_config = ConfigDict(
    env_file=".env",
    env_file_encoding="utf-8",
  )

  athena_host: str = "0.0.0.0"
  athena_port: int = 9105
  debug: bool = False
  cors_origins: list[str] = [
    "http://localhost:9100",
    "http://localhost:5173",
  ]
  knowledge_dir: str = ""

  def get_knowledge_path(self) -> Path:
    if self.knowledge_dir:
      return Path(self.knowledge_dir)
    return Path(__file__).parent.parent / "knowledge"


@lru_cache
def get_settings() -> Settings:
  return Settings()
