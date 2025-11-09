"""Security headers middleware (S06-06)"""

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add security headers to all HTTP responses"""

    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)

        # X-Frame-Options: Prevent clickjacking
        response.headers["X-Frame-Options"] = "DENY"

        # X-Content-Type-Options: Prevent MIME type sniffing
        response.headers["X-Content-Type-Options"] = "nosniff"

        # X-XSS-Protection: Enable XSS filter (legacy, but still useful)
        response.headers["X-XSS-Protection"] = "1; mode=block"

        # Referrer-Policy: Control referrer information
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        # Content-Security-Policy: Prevent XSS and injection attacks
        # Basic CSP for API (no inline scripts/styles needed)
        csp_policy = (
            "default-src 'self'; script-src 'none'; style-src 'none'; "
            "img-src 'self' data:; font-src 'self'; connect-src 'self';"
        )
        response.headers["Content-Security-Policy"] = csp_policy

        # Strict-Transport-Security: Force HTTPS (if using HTTPS)
        # Note: Only add if request is over HTTPS
        if request.url.scheme == "https":
            response.headers["Strict-Transport-Security"] = (
                "max-age=31536000; includeSubDomains"
            )

        # Permissions-Policy: Control browser features
        response.headers["Permissions-Policy"] = (
            "geolocation=(), microphone=(), camera=(), payment=()"
        )

        return response
