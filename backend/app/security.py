"""JWT role authentication; signing secret must come from the environment."""

from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone
from typing import Any

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

ROLES = {"admin", "district_officer", "field_responder", "public"}
bearer = HTTPBearer(auto_error=False)


def create_access_token(subject: str, role: str, *, secret: str | None = None) -> str:
    if role not in ROLES:
        raise ValueError(f"unsupported role: {role}")
    signing_secret = secret or os.getenv("JWT_SECRET", "")
    if len(signing_secret) < 32:
        raise RuntimeError("JWT_SECRET must contain at least 32 characters")
    ttl_minutes = int(os.getenv("ACCESS_TOKEN_TTL_MINUTES", "60"))
    if ttl_minutes < 1:
        raise ValueError("ACCESS_TOKEN_TTL_MINUTES must be positive")
    now = datetime.now(timezone.utc)
    return jwt.encode(
        {
            "sub": subject,
            "role": role,
            "iat": now,
            "exp": now + timedelta(minutes=ttl_minutes),
        },
        signing_secret,
        algorithm="HS256",
    )


def current_actor(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer),
) -> dict[str, Any]:
    if credentials is None:
        raise HTTPException(status_code=401, detail="Bearer token required")
    secret = os.getenv("JWT_SECRET", "")
    if len(secret) < 32:
        raise HTTPException(status_code=503, detail="JWT authentication is not configured")
    try:
        claims = jwt.decode(credentials.credentials, secret, algorithms=["HS256"])
    except jwt.ExpiredSignatureError as exc:
        raise HTTPException(status_code=401, detail="Bearer token expired") from exc
    except jwt.InvalidTokenError as exc:
        raise HTTPException(status_code=401, detail="Invalid bearer token") from exc
    if claims.get("role") not in ROLES or not claims.get("sub"):
        raise HTTPException(status_code=401, detail="Bearer token has invalid claims")
    return {"subject": claims["sub"], "role": claims["role"]}


def require_roles(*roles: str):
    if not roles or any(role not in ROLES for role in roles):
        raise ValueError("at least one supported role is required")

    def dependency(actor: dict[str, Any] = Depends(current_actor)) -> dict[str, Any]:
        if actor["role"] not in roles:
            raise HTTPException(status_code=403, detail="Insufficient role")
        return actor

    return dependency
