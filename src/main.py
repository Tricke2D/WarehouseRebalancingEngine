from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.v1.routes_allocation import router as allocation_router
from src.api.v1.routes_transfer import router as transfer_router
from src.api.v1.routes_dashboard import router as dashboard_router
from src.api.v1.routes_testing import router as testing_router
from src.scheduler import setup_scheduled_jobs, start_scheduler, shutdown_scheduler
from src.core.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    setup_scheduled_jobs()
    start_scheduler()
    yield
    # Shutdown
    shutdown_scheduler()


app = FastAPI(
    title="Warehouse Rebalancing Engine",
    description="Multi-Warehouse Inventory Management with Smart Rebalancing",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(allocation_router)
app.include_router(transfer_router)
app.include_router(dashboard_router)

# Hanya di non-production
if settings.app_env != "production":
    app.include_router(testing_router)


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "warehouse-engine"}


@app.get("/")
async def root():
    return {"message": "Warehouse Rebalancing Engine API"}