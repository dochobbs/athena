from fastapi import APIRouter, HTTPException, Query

from ..deps import get_resolver, get_store

router = APIRouter(prefix="/api/frameworks", tags=["frameworks"])


@router.get("")
async def list_frameworks(
  specialty: str | None = Query(None),
  category: str | None = Query(None),
):
  if specialty:
    resolver = get_resolver()
    frameworks = resolver.resolve_frameworks(specialty=specialty, category=category)
  else:
    store = get_store()
    frameworks = store.get_all_frameworks()
    if category:
      frameworks = [f for f in frameworks if f.category == category]
  return [f.model_dump(exclude_none=True) for f in frameworks]


@router.get("/for-condition/{condition_id}")
async def get_framework_for_condition(
  condition_id: str,
  specialty: str = Query(..., description="Required: which specialty context"),
  level: str | None = Query(None),
):
  resolver = get_resolver()
  fw = resolver.resolve_framework_for_condition(
    condition=condition_id, specialty=specialty, level=level,
  )
  if fw is None:
    raise HTTPException(
      status_code=404,
      detail=f"No framework for '{condition_id}' in specialty '{specialty}'",
    )
  return fw.model_dump(exclude_none=True)


@router.get("/{framework_id}")
async def get_framework(framework_id: str):
  store = get_store()
  fw = store.get_framework(framework_id)
  if fw is None:
    raise HTTPException(status_code=404, detail=f"Framework '{framework_id}' not found")
  return fw.model_dump(exclude_none=True)
