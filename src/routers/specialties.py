from fastapi import APIRouter, HTTPException

from ..deps import get_store

router = APIRouter(prefix="/api/specialties", tags=["specialties"])


@router.get("")
async def list_specialties():
  store = get_store()
  specialties = store.get_all_specialties()
  return [s.model_dump(exclude_none=True) for s in specialties]


@router.get("/{specialty_id}")
async def get_specialty(specialty_id: str):
  store = get_store()
  spec = store.get_specialty(specialty_id)
  if spec is None:
    raise HTTPException(status_code=404, detail=f"Specialty '{specialty_id}' not found")
  return spec.model_dump(exclude_none=True)
