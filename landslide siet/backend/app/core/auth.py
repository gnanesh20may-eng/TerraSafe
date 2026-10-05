from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from backend.app.config import JWT_ACCESS_TOKEN_EXPIRE_MINUTES, JWT_ALGORITHM, JWT_SECRET

bearer = HTTPBearer(auto_error=False)
ALLOWED_ROLES = {"admin", "district_officer", "field_responder", "public"}


def issue_token(subject: str, role: str, secret: str | None = None) -> str:
    signing_secret = secret or JWT_SECRET
    if not signing_secret or role not in ALLOWED_ROLES:
        raise ValueError("JWT secret and a valid role are required")
    now = datetime.now(timezone.utc)
    return jwt.encode(
        {"sub": subject, "role": role, "iat": now, "exp": now + timedelta(minutes=JWT_ACCESS_TOKEN_EXPIRE_MINUTES)},
        signing_secret,
        algorithm=JWT_ALGORITHM,
    )


def current_principal(credentials: HTTPAuthorizationCredentials | None = Depends(bearer)) -> dict[str, Any]:
    if credentials is None:
        raise HTTPException(status_code=401, detail="Bearer token required", headers={"WWW-Authenticate": "Bearer"})
    if not JWT_SECRET:
        raise HTTPException(status_code=503, detail="Authentication is not configured")
    try:
        claims = jwt.decode(credentials.credentials, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        role = claims.get("role")
        subject = claims.get("sub")
        if role not in ALLOWED_ROLES or not isinstance(subject, str):
            raise ValueError("invalid principal claims")
        return {"sub": subject, "role": role}
    except (jwt.PyJWTError, ValueError) as error:
        raise HTTPException(status_code=401, detail="Invalid or expired bearer token") from error


def require_roles(*roles: str):
    def dependency(principal: dict[str, Any] = Depends(current_principal)) -> dict[str, Any]:
        if principal["role"] not in roles:
            raise HTTPException(status_code=403, detail="Role is not authorized for this action")
        return principal

    return dependency
