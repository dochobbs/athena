from fastapi import APIRouter, Query

from ..deps import get_resolver

router = APIRouter(prefix="/api/learner-tracks", tags=["learners"])


@router.get("")
async def list_learner_tracks(
  specialty: str | None = Query(None),
  level: str | None = Query(None),
):
  resolver = get_resolver()
  tracks = resolver.resolve_learner_tracks(specialty=specialty, level=level)
  return [t.model_dump(exclude_none=True) for t in tracks]
