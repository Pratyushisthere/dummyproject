from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import RedirectResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt
import requests
import os
import logging
from typing import Optional

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Initialize router and security
router = APIRouter(prefix="/auth/ibm", tags=["Auth"])
security = HTTPBearer()

def get_required_env_var(name: str) -> str:
    """Helper function to get required environment variables."""
    value = os.getenv(name)
    if not value:
        raise ValueError(f"Missing required environment variable: {name}")
    return value

# Load environment variables
try:
    # IBM W3ID Configuration
    CLIENT_ID = get_required_env_var("W3ID_CLIENT_ID")
    CLIENT_SECRET = get_required_env_var("W3ID_CLIENT_SECRET")
    TOKEN_ENDPOINT = get_required_env_var("TOKEN_ENDPOINT")
    AUTH_ENDPOINT = get_required_env_var("AUTH_ENDPOINT")
    REDIRECT_URI = get_required_env_var("W3ID_REDIRECT_URI")
    JWKS_URL = get_required_env_var("JWKS_URL")
    ISSUER = get_required_env_var("JWT_ISSUER")
    FRONTEND_URL = get_required_env_var("FRONTEND_URL")
except ValueError as e:
    logger.error(f"Configuration error: {e}")
    raise

# Cache for JWKS
_jwks_cache = None

def get_jwks():
    """Retrieve JWKS from the endpoint with caching."""
    global _jwks_cache
    if _jwks_cache:
        return _jwks_cache
    try:
        logger.debug(f"Fetching JWKS from {JWKS_URL}")
        res = requests.get(JWKS_URL, timeout=5)
        res.raise_for_status()
        _jwks_cache = res.json()
        return _jwks_cache
    except requests.RequestException as e:
        logger.error(f"Failed to fetch JWKS: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Failed to fetch JWKS: {str(e)}"
        )

def verify_token(token: str):
    """Verify JWT token and return its payload."""
    try:
        logger.debug("Verifying token...")
        header = jwt.get_unverified_header(token)
        kid = header.get("kid")
        
        if not kid:
            logger.error("Token header missing key ID")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token header missing key ID"
            )

        jwks = get_jwks()
        key = next((k for k in jwks.get("keys", []) if k.get("kid") == kid), None)
        
        if not key:
            logger.error("Invalid token key")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token key"
            )

        payload = jwt.decode(
            token,
            key,
            algorithms=["RS256"],
            issuer=ISSUER,
            options={"verify_aud": False},
        )
        logger.debug("Token verified successfully")
        return payload

    except jwt.JWTError as e:
        logger.error(f"JWT Error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}"
        )

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Dependency to get current user from JWT token."""
    try:
        logger.debug("Getting current user...")
        payload = verify_token(credentials.credentials)
        user_data = {
            "w3_id": payload.get("uid") or payload.get("sub"),
            "name": payload.get("displayName") or payload.get("name"),
            "email": payload.get("emailAddress") or payload.get("email"),
        }
        logger.debug(f"User data: {user_data}")
        return user_data
    except HTTPException as e:
        logger.error(f"Authentication error: {str(e.detail)}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error in get_current_user: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing authentication: {str(e)}"
        )

@router.get("/login")
async def login():
    """Initiate the OAuth2 login flow."""
    try:
        from urllib.parse import quote_plus
        redirect_uri = quote_plus(REDIRECT_URI)
        url = (
            f"{AUTH_ENDPOINT}"
            "?response_type=code"
            f"&client_id={CLIENT_ID}"
            f"&redirect_uri={redirect_uri}"
            "&scope=openid%20profile%20email"
        )
        logger.debug(f"Redirecting to login URL: {url}")
        return RedirectResponse(url=url)
    except Exception as e:
        logger.error(f"Login error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error initiating login: {str(e)}"
        )

@router.get("/me")
async def get_current_user_endpoint(user = Depends(get_current_user)):
    """Get current user information."""
    return user

@router.get("/callback")
async def callback(code: str):
    """Handle OAuth2 callback and exchange code for tokens."""
    try:
        logger.debug("Received callback with authorization code")
        
        # Exchange code for tokens
        token_res = requests.post(
            TOKEN_ENDPOINT,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            auth=(CLIENT_ID, CLIENT_SECRET),
            data={
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": REDIRECT_URI,
            },
            timeout=10
        )

        logger.debug(f"Token response status: {token_res.status_code}")
        logger.debug(f"Token response: {token_res.text}")

        if not token_res.ok:
            logger.error(f"Token exchange failed: {token_res.text}")
            return RedirectResponse(f"{FRONTEND_URL}/login?error=token_exchange_failed")

        tokens = token_res.json()
        access_token = tokens.get("access_token")
        
        if not access_token:
            logger.error("No access token in response")
            return RedirectResponse(f"{FRONTEND_URL}/login?error=no_access_token")

        # Create response and set cookie
        response = RedirectResponse(url=FRONTEND_URL)
        response.set_cookie(
            key="access_token",
            value=f"Bearer {access_token}",
            httponly=True,
            secure=False,  # Set to True in production with HTTPS
            samesite="lax",
            path="/",
            max_age=tokens.get("expires_in", 3600)
        )
        
        logger.debug("Successfully processed callback, redirecting to frontend")
        return response

    except requests.RequestException as e:
        logger.error(f"Request error in callback: {str(e)}", exc_info=True)
        return RedirectResponse(f"{FRONTEND_URL}/login?error=service_unavailable")
    except Exception as e:
        logger.error(f"Unexpected error in callback: {str(e)}", exc_info=True)
        return RedirectResponse(f"{FRONTEND_URL}/login?error=auth_failed")