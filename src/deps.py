"""Shared dependencies — store and resolver singletons.

Separating these from main.py avoids circular imports
(main imports routers, routers need store/resolver).
"""
from __future__ import annotations

from .loader import KnowledgeStore
from .resolver import KnowledgeResolver

_store: KnowledgeStore | None = None
_resolver: KnowledgeResolver | None = None


def init_knowledge(store: KnowledgeStore, resolver: KnowledgeResolver):
  global _store, _resolver
  _store = store
  _resolver = resolver


def get_store() -> KnowledgeStore:
  assert _store is not None, "KnowledgeStore not initialized — call init_knowledge first"
  return _store


def get_resolver() -> KnowledgeResolver:
  assert _resolver is not None, "KnowledgeResolver not initialized — call init_knowledge first"
  return _resolver
