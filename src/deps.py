"""Shared dependencies — store and resolver singletons.

Separating these from main.py avoids circular imports
(main imports routers, routers need store/resolver).
"""
from __future__ import annotations

from fastapi import HTTPException

from .loader import KnowledgeStore
from .resolver import KnowledgeResolver

_store: KnowledgeStore | None = None
_resolver: KnowledgeResolver | None = None


def init_knowledge(store: KnowledgeStore, resolver: KnowledgeResolver):
  global _store, _resolver
  _store = store
  _resolver = resolver


def get_store() -> KnowledgeStore:
  if _store is None:
    raise HTTPException(status_code=503, detail="Athena knowledge store not initialized")
  return _store


def get_resolver() -> KnowledgeResolver:
  if _resolver is None:
    raise HTTPException(status_code=503, detail="Athena resolver not initialized")
  return _resolver


VALID_SPECIALTIES = {"pediatrics", "internal_medicine", "family_practice"}


def validate_specialty(specialty: str | None) -> None:
  """Reject unknown specialty values with 400 instead of silently returning []."""
  if specialty and specialty not in VALID_SPECIALTIES:
    raise HTTPException(
      status_code=400,
      detail=f"Unknown specialty '{specialty}'. Valid: {sorted(VALID_SPECIALTIES)}",
    )
