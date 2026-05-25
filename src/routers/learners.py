from fastapi import APIRouter, Query

from ..deps import get_resolver, validate_specialty

router = APIRouter(prefix="/api/learner-tracks", tags=["learners"])


@router.get("")
async def list_learner_tracks(
  specialty: str | None = Query(None),
  level: str | None = Query(None),
):
  validate_specialty(specialty)
  resolver = get_resolver()
  tracks = resolver.resolve_learner_tracks(specialty=specialty, level=level)
  return [t.model_dump(exclude_none=True) for t in tracks]
