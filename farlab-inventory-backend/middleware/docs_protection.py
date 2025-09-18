# /middleware/docs_protection.py
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from utils.security import decode_access_token # Existing JWT decoding function
from database import SessionLocal # Database session
from models.user import User # User model
from utils.logging_config import get_logger

logger = get_logger(__name__)

def is_protected_path(path: str) -> bool:
    """Check if the requested path requires admin authentication."""
    protected_paths = ["/docs", "/redoc", "/openapi.json"]
    return any(path.startswith(p) for p in protected_paths)

def extract_token_from_header(auth_header: str) -> str:
    """Extract JWT tokenfrom Authorization header."""
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header format",
            headers={"WWW-Authenticate": "Bearer"}
        )
    return auth_header.split(" ")[1]

def verify_admin_user(token: str) -> dict:
    """Verify JWT token and ensure user is an active admin."""
    try:
        # Decode JWT token
        payload = decode_access_token(token)
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: missing user identification"
            )
        
        # Query database for user
        db = SessionLocal()
        try:
            user = db.query(User).filter(User.id == int(user_id)).first()

            if not user:
                logger.warning(f"User with ID {user_id} not found.")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token: user not found"
                )
            if not user.is_active:
                logger.warning(f"Inactive user {user.username} attempted docs access.")
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="User account is inactive"
                )
            if not user.is_admin:
                logger.warning(f"Non-admin user {user.username} attempted docs access.")
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="User does not have admin privileges"
                )
            logger.info(f"Admin user {user.username} authenticated for docs access.")
            return user # Return user object or relevant info
        finally:
            db.close() # Ensure DB session is closed    

    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except ValueError as e:
        logger.warning(f"Invalid user ID format in token: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token format"
        )
    except Exception as e:
        logger.error(f"Token verification failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token verification failed"
        )
    
async def admin_docs_middleware(request: Request, call_next):
    """Main middleware function to protect documentation endpoints."""
    
    # Check if this path requires admin authentication
    if not is_protected_path(request.url.path):
        return await call_next(request)
    
    logger.debug(f"Protecting admin-only endpoint: {request.url.path}")
    
    # Allow Swagger UI static assets (CSS, JS, images)
    if request.url.path.endswith(('.css', '.js', '.png', '.ico', '.map', '.woff', '.woff2')):
        return await call_next(request)
    
    # Allow Swagger UI and ReDoc pages to load (they need to show the login form)
    if request.url.path in ["/docs", "/redoc"]:
        logger.info(f"Allowing Swagger UI to load: {request.url.path}")
        return await call_next(request)
    
    # CRITICAL: Allow openapi.json for unauthenticated requests
    # This is needed for Swagger UI to load and show the authentication form
    if request.url.path == "/openapi.json":
        # Check if there's an Authorization header
        auth_header = request.headers.get("Authorization")
        
        if not auth_header:
            # No auth header - allow access so Swagger UI can load
            logger.info("Allowing unauthenticated access to /openapi.json for Swagger UI")
            return await call_next(request)
        
        # If auth header exists, verify it
        try:
            token = extract_token_from_header(auth_header)
            user = verify_admin_user(token)
            logger.info(f"Authenticated access to /openapi.json by admin: {user.username}")
            response = await call_next(request)
            response.headers["X-Admin-Access"] = "true"
            return response
        except HTTPException as http_exc:
            # Auth failed, but still allow access for Swagger UI to work
            logger.warning(f"Failed auth for /openapi.json, allowing for Swagger UI: {http_exc.detail}")
            return await call_next(request)
    
    # For any other protected endpoints, require authentication
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={
                "detail": "Authentication required",
                "type": "authentication_required"
            },
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    try:
        token = extract_token_from_header(auth_header)
        user = verify_admin_user(token)
        
        response = await call_next(request)
        response.headers["X-Admin-Access"] = "true"
        response.headers["X-User-ID"] = str(user.id)
        return response
        
    except HTTPException as http_exc:
        return JSONResponse(
            status_code=http_exc.status_code,
            content={
                "detail": http_exc.detail,
                "type": "admin_access_denied" if http_exc.status_code == 403 else "authentication_failed"
            },
            headers=http_exc.headers or {}
        )
    
# Check Swagger UI authentication
def check_swagger_auth(request: Request) -> bool:
    """
    Check if request comes from an authenticated Swagger UI session.
    Swagger UI stores auth in session/cookies after using the Authorize button.
    """
    # Check for authorization header (API calls)
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        return True
    
    # Check for Swagger UI cookie-based auth (if implemented)
    # Swagger UI typically uses cookies or session storage
    auth_cookie = request.cookies.get("swagger_auth")
    if auth_cookie:
        return True

    return False

