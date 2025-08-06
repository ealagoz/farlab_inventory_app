# FASTAPI app main file
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from sqlalchemy.orm import Session
from sqlalchemy import text
from database import get_db, create_tables
from services.scheduler import start_scheduler
from utils.logging_config import get_logger
from utils.config import settings

# Import routers
from routers import auth, users, instruments, parts, alerts

# Get a logger for this module
logger = get_logger(__name__)

# App lifespan function


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle application startup and shutdown events."""
    # Startup
    logger.info("INFO: Application startup...")
    logger.info("INFO: Creating database tables...")
    create_tables()
    logger.info("INFO: Database tables created successfully!")

    # --- Start the background scheduler ---
    logger.info("INFO: Starting background scheduler...")
    start_scheduler()

    yield  # The application runs while the lifespan context is active

    # Shutdown
    logger.info("INFO: Application shutdown...")
    # Add any cleanup logic here, like closing a database connection pool if any!


# Create FASTAPI app instance
app = FastAPI(
    title="FARLAB Inventory Management System",
    description="Laboratory inventory management system for tracking instruments parts and alerts",
    version="0.0.1",
    lifespan=lifespan  # Pass lifespan manager here
)

# CORS Middleware Configuration
# This allows frontend (running on a different origin) to communicate
# with backend
origins = [
    "http://localhost",
    settings.FRONTEND_URL,  # Default for Vite
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,  # Important for cookies and auth headers
    allow_methods=["*"],  # Allows all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)

# --- API Routers ---
# Include routers from other files, adding /api prefix to all of them
# The "tags" parameter groups the endpoints in the interactive API doc
app.include_router(auth.router)
app.include_router(instruments.router)
app.include_router(parts.router)
app.include_router(users.router)
app.include_router(alerts.router)

# Root endpoint


@app.get("/")
async def root():
    """Root endpoint returning basic API information."""
    return {
        "message": "Welcome to FARLAB Inventory Management System",
        "version": "0.0.1",
        "status": "running"
    }

# Health check endpoint


@app.get("/health")
async def health_check(db: Session = Depends(get_db)):
    """Health check endpoint to verify database connection."""
    try:
        # Simple query to test database connection
        db.execute(text('SELECT 1'))
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        logger.error(f"ERROR: Health check failed: {e}")
        raise HTTPException(
            status_code=500, detail="Database connection failed:")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
