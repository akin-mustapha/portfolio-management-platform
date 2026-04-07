"""
FastAPI application — Portfolio Management Platform REST API.

Runs on port 8001.  The Dash dashboard continues to run on port 8050 unchanged.

Start dev server:
    cd <project-root>
    uvicorn src.api.main:app --reload --port 8001

In production, the React build is served as static files from /frontend/dist.
"""

import sys
from pathlib import Path

# Ensure project root (the directory containing src/) is importable
ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
for p in (str(ROOT), str(SRC)):
    if p not in sys.path:
        sys.path.insert(0, p)

from fastapi import FastAPI  # noqa: E402
from fastapi.middleware.cors import CORSMiddleware  # noqa: E402
from fastapi.staticfiles import StaticFiles  # noqa: E402

from api.routers import portfolio, assets, tags, rebalance, credentials  # noqa: E402

app = FastAPI(
    title="Portfolio Management API",
    version="1.0.0",
    description="REST API for the React frontend. Dash dashboard still runs on port 8050.",
)

# Allow Vite dev server and local React build origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(portfolio.router, prefix="/api")
app.include_router(assets.router, prefix="/api")
app.include_router(tags.router, prefix="/api")
app.include_router(rebalance.router, prefix="/api")
app.include_router(credentials.router, prefix="/api")

# Serve the React production build as static files.
# Only mounted when the build exists so `uvicorn` can still start without it.
_frontend_dist = ROOT / "frontend" / "dist"
if _frontend_dist.exists():
    app.mount(
        "/",
        StaticFiles(directory=str(_frontend_dist), html=True),
        name="static",
    )
