from pathlib import Path
import sys

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
ROOT_DIR = Path(__file__).resolve().parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))
if str(ROOT_DIR.parent) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR.parent))

from config import settings
from database import Base, engine
from models import file_permission, file_provenance, share_link, team, user  # noqa: F401
from routers import activity, audit, auth, files, permissions, provenance, share, users

Base.metadata.create_all(bind=engine)
settings.DATA_DIR.mkdir(parents=True, exist_ok=True)

app = FastAPI(title=settings.APP_NAME, debug=settings.DEBUG, docs_url="/docs", redoc_url="/redoc")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(files.router)
app.include_router(permissions.router)
app.include_router(share.router)
app.include_router(provenance.router)
app.include_router(activity.router)
app.include_router(audit.router)
app.include_router(users.router)


@app.get("/")
def root():
    return {"status": "running", "service": settings.APP_NAME}


@app.get("/health")
def health():
    return {"status": "healthy"}
