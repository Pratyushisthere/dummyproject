from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import RedirectResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt
import requests
import os
from typing import Optional

# Initialize router and security
router = APIRouter(prefix="/auth", tags=["Auth"])
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
    print(f"Configuration error: {e}")
    raise

# Cache for JWKS
_jwks_cache = None

def get_jwks():
    """Retrieve JWKS from the endpoint with caching."""
    global _jwks_cache
    if _jwks_cache:
        return _jwks_cache
    try:
        res = requests.get(JWKS_URL, timeout=5)
        res.raise_for_status()
        _jwks_cache = res.json()
        return _jwks_cache
    except requests.RequestException as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Failed to fetch JWKS: {str(e)}"
        )

def verify_token(token: str):
    """Verify JWT token and return its payload."""
    try:
        header = jwt.get_unverified_header(token)
        kid = header.get("kid")
        
        if not kid:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token header missing key ID"
            )

        jwks = get_jwks()
        key = next((k for k in jwks.get("keys", []) if k.get("kid") == kid), None)
        
        if not key:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token key"
            )

        return jwt.decode(
            token,
            key,
            algorithms=["RS256"],
            issuer=ISSUER,
            options={"verify_aud": False},
        )
    except jwt.JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}"
        )

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Dependency to get current user from JWT token."""
    try:
        payload = verify_token(credentials.credentials)
        return {
            "w3_id": payload.get("uid") or payload.get("sub"),
            "name": payload.get("displayName") or payload.get("name"),
            "email": payload.get("emailAddress") or payload.get("email"),
        }
    except HTTPException as e:
        raise e
    except Exception as e:
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
            f"?response_type=code"
            f"&client_id={CLIENT_ID}"
            f"&redirect_uri={redirect_uri}"
            f"&scope=openid%20profile%20email"
        )
        return RedirectResponse(url=url)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error initiating login: {str(e)}"
        )

@router.get("/callback")
async def callback(code: str, request: Request):
    """Handle OAuth2 callback and exchange code for tokens."""
    try:
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

        if not token_res.ok:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token exchange failed"
            )

        tokens = token_res.json()
        access_token = tokens.get("access_token")
        
        if not access_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="No access token in response"
            )

        response = RedirectResponse(url=f"{FRONTEND_URL}/")
        response.set_cookie(
            key="access_token",
            value=f"Bearer {access_token}",
            httponly=True,
            secure=False,  # Set to True in production with HTTPS
            samesite="lax",
            path="/",
            max_age=tokens.get("expires_in", 3600)
        )
        return response

    except requests.RequestException as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Authentication service unavailable: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing callback: {str(e)}"
        )