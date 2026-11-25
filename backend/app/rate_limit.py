"""Per-client request limits, shared across legacy and versioned routes."""

import logging
import math
import time

from limits import RateLimitItemPerHour, RateLimitItemPerMinute
from limits.aio.storage import MemoryStorage, RedisStorage
from limits.aio.strategies import MovingWindowRateLimiter
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from app.config import settings
from app.security import client_ip

logger = logging.getLogger(__name__)


def create_storage():
    url = settings.rate_limit_storage_url
    if url == "memory://":
        return MemoryStorage()
    if url.startswith(("redis://", "rediss://")):
        return RedisStorage(url, implementation="redispy", socket_connect_timeout=2, socket_timeout=2)
    raise ValueError("RATE_LIMIT_STORAGE_URL must be memory://, redis:// or rediss://")


storage = create_storage()
limiter = MovingWindowRateLimiter(storage)


def limits_for(path: str, method: str):
    path = path.rstrip("/") or "/"
    if path.startswith("/v1/api/"):
        path = path[3:]
    if path != "/" and path != "/api" and not path.startswith("/api/"):
        return []
    limits = [("api", RateLimitItemPerMinute(settings.rate_limit_per_minute))]
    if method == "POST" and path == "/api/auth/login":
        limits.append(("login", RateLimitItemPerMinute(settings.rate_limit_login_per_minute)))
    elif method == "POST" and path == "/api/auth/register":
        limits.append(("register", RateLimitItemPerHour(settings.rate_limit_register_per_hour)))
    return limits


class RateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        if request.method == "OPTIONS":
            return await call_next(request)
        # Only forwarded headers from configured proxies are trusted; see
        # app.security.client_ip.
        client = client_ip(request)
        try:
            for group, limit in limits_for(request.url.path, request.method):
                if not await limiter.hit(limit, group, client):
                    stats = await limiter.get_window_stats(limit, group, client)
                    retry_after = max(1, math.ceil(stats.reset_time - time.time()))
                    return JSONResponse(
                        status_code=429,
                        content={"detail": "Too many requests. Please try again later."},
                        headers={"Retry-After": str(retry_after), "Cache-Control": "no-store"},
                    )
        except Exception:
            logger.exception("Rate limit storage unavailable")
            return JSONResponse(status_code=503, content={"detail": "Service temporarily unavailable."}, headers={"Cache-Control": "no-store"})
        return await call_next(request)
