from fastapi import APIRouter, HTTPException, Query

router = APIRouter(prefix="/api/immunizations", tags=["immunizations"])


@router.get("")
async def list_immunizations(
  age_months: int | None = Query(None),
):
  # YAML schedules exist at knowledge/immunizations/{peds_aap.yaml, adult_acip.yaml}
  # but loader/models aren't wired yet. Return 501 so callers don't mistake [] for "no
  # immunizations needed at this age."
  raise HTTPException(
    status_code=501,
    detail="Immunizations endpoint not yet implemented. YAML schedules present but loader pending.",
  )
