from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .config import get_settings
from .database import Base, SessionLocal, engine
from .routes import clients, dashboard, invoices
from .routes import settings as settings_router
from .utils import mark_overdue_invoices

cfg = get_settings()


# Lifespan
# asynccontextmanager lets us run code at startup and shutdown in one block.
# Everything before 'yield' runs when the server starts.
# Everything after 'yield' runs when the server shuts down.
# This replaced the older @app.on_event("startup") pattern in FastAPI 0.93+.


@asynccontextmanager
async def lifespan(app: FastAPI):
    # STARTUP
    # Create all tables defined in models.py if they don't exist yet.
    # Safe to call repeatedly — does nothing if tables already exist.
    Base.metadata.create_all(bind=engine)

    # Scan for any invoices that passed their due_date since last run
    # and flip their status to OVERDUE.
    db = SessionLocal()
    try:
        updated = mark_overdue_invoices(db)
        if updated:
            print(f"[startup] Marked {updated} invoice(s) as overdue")
    finally:
        db.close()

    yield  # server is now running and accepting requests

    # SHUTDOWN — nothing needed for SQLite v1, but the hook is here for
    # future cleanup: closing connection pools, flushing caches, etc.
    print("[shutdown] Invoice API stopped cleanly")


# App instance

app = FastAPI(
    title=cfg.app_name,
    version=cfg.app_version,
    description="""
## Invoice App API

Full-featured invoice management backend.

### Features
- **Clients** — create, search, soft-delete
- **Invoices** — full lifecycle: draft → sent → viewed → paid
- **Payments** — partial payments, auto status advancement
- **Activity log** — every change recorded with before/after values
- **Dashboard** — aggregated stats in one request
- **Settings** — business profile, reusable tax rates
    """,
    # Disable the /docs and /redoc pages in production by setting these to None
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)


# CORS middleware
# Browsers block requests from a different origin (port counts as different).
# This middleware adds the response headers that tell the browser it's allowed.

origins = [o.strip() for o in cfg.allowed_origins.split(",")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


#  Global exception handler
# Catches any unhandled exception and returns a clean JSON error instead of
# an HTML stack trace. Never expose raw tracebacks to API consumers.


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    # In debug mode, include the error message; in production return generic text
    detail = str(exc) if cfg.debug else "An internal error occurred"
    return JSONResponse(status_code=500, content={"detail": detail})


#  Routers
# Each router is a separate file in routes/. Mounting them here keeps
# main.py short regardless of how many features we add.

app.include_router(dashboard.router)
app.include_router(clients.router)
app.include_router(invoices.router)
app.include_router(settings_router.router)


#  Health check


@app.get("/", tags=["Health"], summary="Server health check")
def root():
    """
    Confirms the server is running. Used by deployment platforms and
    developers to verify the API is reachable before making real calls.
    """
    return {
        "status": "ok",
        "app": cfg.app_name,
        "version": cfg.app_version,
    }


#  API summary


@app.get("/routes", tags=["Health"], summary="List all registered routes")
def list_routes():
    """Returns every URL the server responds to. Dev-only convenience."""
    return [
        {"path": route.path, "methods": list(route.methods), "name": route.name}
        for route in app.routes
        if hasattr(route, "methods")
    ]
