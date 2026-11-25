"""Client-address resolution and HTTP security headers.

Rate limiting must key on a client address that an attacker cannot choose.
The ASGI client address is trustworthy; forwarded headers are only trusted
when the immediate peer is a configured reverse proxy (``TRUSTED_PROXY_IPS``).
"""

import ipaddress
from functools import lru_cache

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from app.config import settings

API_CSP = "default-src 'none'; frame-ancestors 'none'; base-uri 'none'; form-action 'none'"
AUTH_PATHS = frozenset(
    {
        "/api/auth/login",
        "/v1/api/auth/login",
        "/api/auth/register",
        "/v1/api/auth/register",
        "/api/auth/me",
        "/v1/api/auth/me",
    }
)


@lru_cache(maxsize=8)
def _trusted_networks(raw: str) -> tuple[ipaddress.IPv4Network | ipaddress.IPv6Network, ...]:
    networks = []
    for part in raw.split(","):
        part = part.strip()
        if not part:
            continue
        try:
            networks.append(ipaddress.ip_network(part, strict=False))
        except ValueError:
            continue
    return tuple(networks)


def _valid_ip(value: str | None) -> str | None:
    if not value:
        return None
    try:
        return str(ipaddress.ip_address(value.strip()))
    except ValueError:
        return None


def client_ip(request: Request) -> str:
    """Return the best-known client address without trusting client input."""
    peer = request.client.host if request.client else "unknown"
    peer_ip = _valid_ip(peer)
    if peer_ip is None:
        return peer

    networks = _trusted_networks(settings.trusted_proxy_ips)
    if not any(ipaddress.ip_address(peer_ip) in network for network in networks):
        return peer_ip

    # The immediate peer is a trusted proxy. Cloudflare overwrites this header,
    # so it is the most reliable value when present.
    forwarded = _valid_ip(request.headers.get("cf-connecting-ip"))
    if forwarded:
        return forwarded

    # Fall back to the rightmost X-Forwarded-For entry, which is the value the
    # nearest trusted proxy appended. Leftmost entries are client-controlled.
    header = request.headers.get("x-forwarded-for")
    if header:
        for candidate in reversed(header.split(",")):
            forwarded = _valid_ip(candidate)
            if forwarded:
                return forwarded
    return peer_ip


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add browser security headers and stop auth responses being cached."""

    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        headers = response.headers

        if "x-content-type-options" not in headers:
            headers["X-Content-Type-Options"] = "nosniff"
        if "x-frame-options" not in headers:
            headers["X-Frame-Options"] = "DENY"
        if "referrer-policy" not in headers:
            headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        if "permissions-policy" not in headers:
            headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
        if "strict-transport-security" not in headers:
            headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"

        if "content-security-policy" not in headers:
            content_type = headers.get("content-type", "")
            headers["Content-Security-Policy"] = (
                settings.frontend_csp if content_type.startswith("text/html") else API_CSP
            )

        if request.url.path in AUTH_PATHS:
            headers["Cache-Control"] = "no-store"

        return response
