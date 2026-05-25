from contextlib import asynccontextmanager

from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import get_settings
from .loader import KnowledgeStore
from .resolver import KnowledgeResolver
from .deps import init_knowledge
from .routers import (
  health,
  conditions,
  frameworks,
  specialties,
  learners,
  disease_arcs,
  immunizations,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
  import sys
  settings = get_settings()
  knowledge_path = settings.get_knowledge_path()
  print(f"Athena starting on {settings.athena_host}:{settings.athena_port}")
  print(f"Loading knowledge from: {knowledge_path}")
  try:
    store = KnowledgeStore(knowledge_path)
    resolver = KnowledgeResolver(store)
    init_knowledge(store, resolver)
    conds = store.get_all_conditions()
    fws = store.get_all_frameworks()
    specs = store.get_all_specialties()
    print(f"Loaded: {len(conds)} conditions, {len(fws)} frameworks, {len(specs)} specialties")
    if not conds and not fws:
      print("WARNING: Athena loaded 0 conditions and 0 frameworks. Check knowledge_path.", file=sys.stderr)
  except Exception as e:
    print(f"FATAL: Athena failed to initialize knowledge store: {e}", file=sys.stderr)
    raise
  yield
  print("Athena shutting down")


app = FastAPI(
  title="Athena",
  description="MedEd Curriculum & Knowledge Service",
  version="0.1.0",
  lifespan=lifespan,
)

settings = get_settings()
app.add_middleware(
  CORSMiddleware,
  allow_origins=settings.cors_origins,
  allow_credentials=True,
  allow_methods=["*"],
  allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(conditions.router)
app.include_router(frameworks.router)
app.include_router(specialties.router)
app.include_router(learners.router)
app.include_router(disease_arcs.router)
app.include_router(immunizations.router)


@app.get("/")
async def root():
  return {"name": "Athena", "version": "0.1.0", "status": "running"}


if __name__ == "__main__":
  import uvicorn
  uvicorn.run(app, host=settings.athena_host, port=settings.athena_port)
