import hmac
import hashlib
import base64
import json
import time
from fastapi import Request, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
from app.config import settings

security = HTTPBearer(auto_error=False)
ALLOWED_IPS = set()


def _sign(payload: str) -> str:
    sig = hmac.new(settings.jwt_secret.encode(), payload.encode(), hashlib.sha256).digest()
    return base64.urlsafe_b64encode(sig).decode()


def create_jwt_token(user_id: str = 'admin') -> str:
    header = base64.urlsafe_b64encode(json.dumps({'alg': 'HS256', 'typ': 'JWT'}).encode()).decode().rstrip('=')
    payload = base64.urlsafe_b64encode(json.dumps({
        'user_id': user_id,
        'exp': int(time.time()) + 86400,
        'iat': int(time.time()),
    }).encode()).decode().rstrip('=')
    signature = _sign(f'{header}.{payload}')
    return f'{header}.{payload}.{signature}'


def verify_jwt_token(token: str) -> dict:
    parts = token.split('.')
    if len(parts) != 3:
        raise HTTPException(401, 'Invalid token format')
    expected_sig = _sign(f'{parts[0]}.{parts[1]}')
    if not hmac.compare_digest(parts[2], expected_sig):
        raise HTTPException(401, 'Invalid token signature')
    try:
        padding = -len(parts[1]) % 4
        payload = json.loads(base64.urlsafe_b64decode(parts[1] + '=' * padding))
        if payload.get('exp', 0) < time.time():
            raise HTTPException(401, 'Token expired')
        return payload
    except Exception:
        raise HTTPException(401, 'Invalid token')


async def require_auth(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)):
    if settings.env == 'development':
        return {'user_id': 'admin'}
    if credentials is None:
        raise HTTPException(401, 'Authentication required')
    return verify_jwt_token(credentials.credentials)


async def check_ip_whitelist(request: Request, call_next):
    if settings.env == 'production' and ALLOWED_IPS:
        client_ip = request.client.host if request.client else ''
        if client_ip not in ALLOWED_IPS:
            raise HTTPException(403, 'IP not whitelisted')
    return await call_next(request)


def set_allowed_ips(ips: list):
    ALLOWED_IPS.clear()
    ALLOWED_IPS.update(ips)
