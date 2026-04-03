from pathlib import Path

import pytest
from fastapi.testclient import TestClient

FIXTURES_DIR = Path(__file__).parent / "fixtures"


@pytest.fixture
def client(monkeypatch):
  monkeypatch.setenv("KNOWLEDGE_DIR", str(FIXTURES_DIR))
  from athena.src.config import get_settings
  get_settings.cache_clear()
  from athena.src.loader import KnowledgeStore
  from athena.src.resolver import KnowledgeResolver
  from athena.src.deps import init_knowledge
  from athena.src.main import app
  init_knowledge(KnowledgeStore(FIXTURES_DIR), KnowledgeResolver(KnowledgeStore(FIXTURES_DIR)))
  with TestClient(app) as c:
    yield c
  get_settings.cache_clear()
