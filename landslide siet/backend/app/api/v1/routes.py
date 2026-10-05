from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from backend.app.core.security import verify_api_key, verify_token

router = APIRouter(prefix="/api/v1", tags=["api-v1"])


class LoginRequest(BaseModel):
    username: str = Field(..., min_length=1)
    password: str = Field(..., min_length=1)


@router.get("/health")
def health():
    return {
        "status": "ok",
        "service": "landsense",
        "environment": "development",
        "demo_mode": True,
    }


@router.post("/auth/login")
def login(payload: LoginRequest):
    if payload.username == "demo" and payload.password == "demo":
        return {
            "token": "demo-token",
            "user": {
                "name": "Demo User",
                "role": "citizen",
            },
        }
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")


@router.get("/auth/profile")
def profile(token: str = Depends(verify_token)):
    return {
        "name": "Demo User",
        "role": "citizen",
        "authorised": True,
        "token": token,
    }


@router.get("/secure-status")
def secure_status(api_key: str = Depends(verify_api_key)):
    return {"status": "secure", "key": api_key}
