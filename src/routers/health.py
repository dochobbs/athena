from fastapi import APIRouter

from ..deps import get_store

router = APIRouter(tags=["health"])


@router.get("/api/health")
async def health():
  store = get_store()
  return {
    "status": "healthy",
    "service": "athena",
    "version": "0.1.0",
    "knowledge": {
      "conditions": len(store.get_all_conditions()),
      "frameworks": len(store.get_all_frameworks()),
      "specialties": len(store.get_all_specialties()),
      "learner_tracks": len(store.get_all_learner_tracks()),
      "disease_arcs": len(store.get_all_disease_arcs()),
    },
  }
