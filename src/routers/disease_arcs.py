from fastapi import APIRouter, HTTPException, Query

from ..deps import get_resolver, get_store

router = APIRouter(prefix="/api/disease-arcs", tags=["disease-arcs"])


@router.get("")
async def list_disease_arcs(
  specialty: str | None = Query(None),
):
  if specialty:
    resolver = get_resolver()
    arcs = resolver.resolve_disease_arcs(specialty=specialty)
  else:
    store = get_store()
    arcs = store.get_all_disease_arcs()
  return [a.model_dump(exclude_none=True) for a in arcs]


@router.get("/{arc_id}")
async def get_disease_arc(arc_id: str):
  store = get_store()
  arc = store.get_disease_arc(arc_id)
  if arc is None:
    raise HTTPException(status_code=404, detail=f"Disease arc '{arc_id}' not found")
  return arc.model_dump(exclude_none=True)
