"""
FastAPI application — Portfolio Management Platform REST API.

Runs on port 8001.  The Dash dashboard continues to run on port 8050 unchanged.

Start dev server:
    cd v2/
    uvicorn backend.api.main:app --reload --port 8001

In production, the React build is served as static files from /frontend/dist.
"""

from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend.api.routers import portfolio, assets, tags, rebalance, credentials

ROOT = Path(__file__).resolve().parents[2]

app = FastAPI(
    title="Portfolio Management API",
    version="1.0.0",
    description="REST API for the React frontend. Dash dashboard still runs on port 8050.",
)

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

_frontend_dist = ROOT / "frontend" / "dist"
if _frontend_dist.exists():
    app.mount(
        "/",
        StaticFiles(directory=str(_frontend_dist), html=True),
        name="static",
    )
