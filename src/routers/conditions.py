from fastapi import APIRouter, HTTPException, Query

from ..deps import get_resolver, get_store

router = APIRouter(prefix="/api/conditions", tags=["conditions"])


@router.get("")
async def list_conditions(
  specialty: str | None = Query(None, description="Filter by specialty: pediatrics, internal_medicine, family_practice"),
  age_months: int | None = Query(None, description="Filter by patient age in months"),
  level: str | None = Query(None, description="Filter by learner level: student, resident, attending"),
  system: str | None = Query(None, description="Filter by organ system: pulmonary, gi, cardiology, etc."),
):
  if specialty:
    resolver = get_resolver()
    conditions = resolver.resolve_conditions(
      specialty=specialty,
      age_months=age_months,
      level=level,
      system=system,
    )
  else:
    store = get_store()
    conditions = store.get_all_conditions()
    if system:
      conditions = [c for c in conditions if c.system == system]
  return [c.model_dump(exclude_none=True) for c in conditions]


@router.get("/{condition_id}")
async def get_condition(condition_id: str):
  store = get_store()
  condition = store.get_condition(condition_id)
  if condition is None:
    raise HTTPException(status_code=404, detail=f"Condition '{condition_id}' not found")
  return condition.model_dump(exclude_none=True)
