# FASTAPI app main file
from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from contextlib import asynccontextmanager
from sqlalchemy.orm import Session
from sqlalchemy import text
import threading
from datetime import datetime
import time

from database import get_db, create_tables, SessionLocal, init_app as init_database_app
from services.scheduler import start_scheduler, scheduler_instance, scheduled_alert_job
from utils.logging_config import get_logger
from utils.config import settings
from utils.create_admin import ensure_admin_exists

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

    # Initialize database connections and monitoring
    logger.info("INFO: Initializing database connections...")
    init_database_app()
    logger.info("INFO: Database connections initialized successfully!")

    # Create database tables
    logger.info("INFO: Creating database tables...")
    create_tables()
    logger.info("INFO: Database tables created successfully!")

    # --- Create admin user if not exists ---
    logger.info("INFO: Ensuring admin user exists...")
    # db: Session = SessionLocal()
    # try:
    #     ensure_admin_exists(db)
    # finally:
    #     db.close()
    # Use the dependency function instead of direct SessionLocal
    db_gen = get_db()
    db: Session = next(db_gen)
    try:
        ensure_admin_exists(db)
    finally:
        # Properly close the generator
        try:
            next(db_gen)
        except StopIteration:
            pass

    # --- Start the background scheduler ---
    logger.info("INFO: Starting background scheduler...")
    start_scheduler()

    yield  # The application runs while the lifespan context is active

    # Shutdown
    logger.info("INFO: Application shutdown...")
    
    # Shutdown scheduler
    if scheduler_instance and scheduler_instance.running:
        logger.info("INFO: Shutting down scheduler...")
        scheduler_instance.shutdown(wait=True)
        
    # Close database connections
    logger.info("INFO: Closing database connections...")
    # The connection pools will be automatically closed when the process exits
    
    logger.info("INFO: Application shutdown complete.")


# Create FASTAPI app instance
app = FastAPI(
    title="FARLAB Inventory Management System",
    description="Laboratory inventory management system for tracking instruments parts and alerts",
    version="0.0.1",
    lifespan=lifespan,  # Pass lifespan manager here
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# CORS Middleware Configuration


app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL],
    allow_credentials=True,  # Important for cookies and auth headers
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Accept", "Accept-Language", "Content-Language", "Content-Type", "Authorization"],  # ✅ Specific headers only
    expose_headers=["X-Total-Count"], # Only expose what frontend needs
)

# Add TrustedHost middleware for additional protection
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=[
        "localhost", 
        "127.0.0.1", 
        "backend",
        # "your-production-domain.com"  # Add when deploying
        ]
)

# Add request timing middleware for monitoring
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)

    return response

# --- API Routers ---
# Include routers from other files, adding /api prefix to all of them
# The "tags" parameter groups the endpoints in the interactive API doc
app.include_router(auth.router, prefix=settings.API_PREFIX)
app.include_router(instruments.router,
                   prefix=f"{settings.API_PREFIX}/instruments")
app.include_router(parts.router, prefix=f"{settings.API_PREFIX}/parts")
app.include_router(users.router, prefix=f"{settings.API_PREFIX}/users")
app.include_router(alerts.router, prefix=f"{settings.API_PREFIX}/alerts")

# Root endpoint


@app.get("/")
async def root():
    """Root endpoint returning basic API information."""
    return {
        "message": "Welcome to FARLAB Inventory Management System",
        "version": "0.0.1",
        "status": "running",
        "docs": "/docs"
    }

# Global job status tracking
job_status = {
    "last_run": None,
    "last_success": None,
    "last_failure": None,
    "last_error": None,
    "failure_count": 0,
    "total_runs": 0,
    "average_duration": 0.0
}
job_status_lock = threading.Lock()

def update_job_status(success: bool, duration: float, error: str = None):
    """Thread-safe job status updates."""
    with job_status_lock:
        now = datetime.now()
        job_status["last_run"] = now
        job_status["total_runs"] += 1

        if success:
            job_status["last_success"] = now
            job_status["failure_count"] = 0 # Reset on success
        else: 
            job_status["last_failure"] = now
            job_status["failure_count"] += 1
            job_status["last_error"] = error

        # Update average duration
        current_avg = job_status["average_duration"]
        total_runs = job_status["total_runs"]
        job_status["average_duration"] = ((current_avg * (total_runs - 1)) + duration) / total_runs


# Health check endpoints


@app.get("/health")
async def health_check(db: Session = Depends(get_db)):
    """Health check endpoint to verify database connection."""
    try:
        # Simple query to test database connection
        result = db.execute(text('SELECT COUNT(*) as user_count FROM users')).first()
        return {
            "status": "healthy",
            "database": "connected",
            "user_count": result.user_count if result else 0,
            "timestamp": int(time.time())
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(
            status_code=503, # Service unavailable
            detail="Database connection failed"
        )

@app.get("/health/scheduler")
async def scheduler_health_check():
    """Health check specifically for background scheduler."""
    with job_status_lock:
        status = job_status.copy()

    is_healthy = True 
    issues = []

    # Check if job ran recently
    if status["last_run"]:
        minutes_since_run = (datetime.now() - status["last_run"]).total_seconds() / 60
        expected_interval = settings.SCHEDULER_INTERVAL_MINUTES

        if minutes_since_run > expected_interval * 2: # Allow some buffer
            is_healthy = False
            issues.append(f"Job hasnot run in {minutes_since_run: .1f} minutes")
    else:
        is_healthy = False
        issues.append("Job has never run")

    # Check failure rate
    if status["failure_count"] > 3:
        is_healthy = False
        issues.append(f"Too many consecutive failures: {status['failure_count']}")


    return {
        "scheduler_healthy": is_healthy,
        "issues": issues,
        "job_status": job_status,
        "scheduler_running": scheduler_instance.running if scheduler_instance else False
    }    

# Enhanced job wrapper with monitoring
def safe_scheduled_alert_job():
    """Job wrapper with comprehensive monitoring."""
    start_time = time.time()
    error_msg = None
    
    try:
        # Scheduler job logic
        scheduled_alert_job()
        success = True
        
    except Exception as e:
        success = False
        error_msg = str(e)
        logger.error("Scheduled job failed: %s", e, exc_info=True)
        
        # TODO: Send critical alert if failure count is high
        
    finally:
        duration = time.time() - start_time
        update_job_status(success, duration, error_msg)
        
        logger.info(
            "Job completed: success=%s, duration=%.2fs, total_runs=%d", 
            success, duration, job_status["total_runs"]
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
