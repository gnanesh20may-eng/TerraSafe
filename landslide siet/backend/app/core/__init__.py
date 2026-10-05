from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer, APIKeyHeader

bearer_scheme = HTTPBearer(auto_error=False)
api_key_scheme = APIKeyHeader(name="x-api-key", auto_error=False)


def verify_token(credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme)) -> str:
    if credentials is None or credentials.credentials != "demo-token":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing or invalid token")
    return credentials.credentials


def verify_api_key(api_key: str | None = Depends(api_key_scheme)) -> str:
    if api_key is None or api_key != "demo-api-key":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing or invalid API key")
    return api_key
