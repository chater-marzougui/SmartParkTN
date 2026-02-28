import contextlib
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import socketio
import os

from app.config import settings
from app.db import engine, Base

# Import all models so Alembic can detect them
from app.models import vehicle, event, session, decision, tariff, rule, user, alert  # noqa: F401

# Import routers
from app.routers import auth, vision, vehicles, sessions, events, rules, tariffs, analytics, assistant, alerts, admin


# ── Socket.IO server ────────────────────────────────────────────────────────
sio = socketio.AsyncServer(
    async_mode="asgi",
    cors_allowed_origins=settings.CORS_ORIGINS,
)


@contextlib.asynccontextmanager
async def lifespan(app: FastAPI):
    # Create tables on startup (use Alembic for production migrations)
    Base.metadata.create_all(bind=engine)
    os.makedirs(settings.SNAPSHOT_DIR, exist_ok=True)
    yield


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve snapshots
if os.path.exists(settings.SNAPSHOT_DIR):
    app.mount("/snapshots", StaticFiles(directory=settings.SNAPSHOT_DIR), name="snapshots")

# API routers
app.include_router(auth.router,       prefix="/api/auth",      tags=["Auth"])
app.include_router(vision.router,     prefix="/api/vision",    tags=["Vision"])
app.include_router(vehicles.router,   prefix="/api/vehicles",  tags=["Vehicles"])
app.include_router(sessions.router,   prefix="/api/sessions",  tags=["Sessions"])
app.include_router(events.router,     prefix="/api/events",    tags=["Events"])
app.include_router(rules.router,      prefix="/api/rules",     tags=["Rules"])
app.include_router(tariffs.router,    prefix="/api/tariffs",   tags=["Tariffs"])
app.include_router(analytics.router,  prefix="/api/analytics", tags=["Analytics"])
app.include_router(assistant.router,  prefix="/api/assistant", tags=["Assistant"])
app.include_router(alerts.router,     prefix="/api/alerts",    tags=["Alerts"])
app.include_router(admin.router,      prefix="/api/admin",     tags=["Admin"])


@app.get("/api/health")
def health():
    return {"status": "ok", "version": settings.APP_VERSION}


# Wrap with Socket.IO ASGI middleware
socket_app = socketio.ASGIApp(sio, other_asgi_app=app)
