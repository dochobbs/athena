from fastapi import APIRouter, Query

router = APIRouter(prefix="/api/immunizations", tags=["immunizations"])


@router.get("")
async def list_immunizations(
  age_months: int | None = Query(None),
):
  # Content populated in Plan 2 (migration). For now, return empty list.
  return []
