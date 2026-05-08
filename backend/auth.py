import os
import logging
from dotenv import load_dotenv
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt

# Load environment variables immediately when this module is imported
load_dotenv()

logger = logging.getLogger(__name__)

# FastAPI security scheme for bearer tokens
security = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    FastAPI Dependency to verify Supabase JWTs.
    Reads the secret lazily at call time (not module load) to ensure .env is loaded.
    """
    token = credentials.credentials

    # Read at call time — guarantees the value is loaded from .env
    jwt_secret = os.getenv("SUPABASE_JWT_SECRET")

    if not jwt_secret:
        logger.error("SUPABASE_JWT_SECRET is not set in the environment.")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Server authentication is misconfigured. SUPABASE_JWT_SECRET is missing."
        )

    try:
        payload = jwt.decode(
            token,
            jwt_secret,
            algorithms=["HS256"],
            options={
                "verify_aud": False,  # Supabase aud is "authenticated"
                "verify_exp": True,   # Always enforce token expiry
            }
        )

        user_id = payload.get("sub")
        email = payload.get("email")

        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token structure: missing user UUID.",
                headers={"WWW-Authenticate": "Bearer"},
            )

        logger.info(f"Authenticated user: {email} (sub={user_id})")

        return {
            "user_id": user_id,
            "email": email,
            "role": payload.get("role", "authenticated")
        }

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication token has expired. Please log in again.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidSignatureError:
        logger.error("JWT signature verification failed. Check that SUPABASE_JWT_SECRET is correct.")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token signature is invalid. Ensure your JWT secret is correct.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError as e:
        logger.warning(f"Failed JWT validation: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid authentication credentials: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )
