from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError

from app.api.wishes import router as wishes_router
from app.core.exceptions import (
    ApiError,
    api_error_handler,
    http_exception_handler,
    validation_exception_handler,
)
from app.middleware.correlation import CorrelationMiddleware
from app.middleware.security_headers import SecurityHeadersMiddleware
from app.middleware.xss_sanitizer import XSSSanitizerMiddleware

app = FastAPI(
    title="Wishlist API",
    version="0.1.0",
    description="API для управления списком желаемых вещей",
)

# Add security middlewares (order matters!)
# 1. Correlation ID (first, so it's available for all requests)
app.add_middleware(CorrelationMiddleware)
# 2. XSS Sanitizer (before security headers, sanitizes response content)
app.add_middleware(XSSSanitizerMiddleware)
# 3. Security Headers (last, adds headers to all responses)
app.add_middleware(SecurityHeadersMiddleware)

# Register exception handlers
app.add_exception_handler(ApiError, api_error_handler)
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)

# Include routers
app.include_router(wishes_router)


@app.get("/health")
def health():
    """Health check endpoint"""
    return {"status": "ok"}
