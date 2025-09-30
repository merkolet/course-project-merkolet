"""Custom exceptions for the application"""

from fastapi import Request
from fastapi.responses import JSONResponse


class ApiError(Exception):
    """Custom API exception with error code and message"""

    def __init__(self, code: str, message: str, status: int = 400):
        self.code = code
        self.message = message
        self.status = status


async def api_error_handler(request: Request, exc: ApiError):
    """Handle ApiError exceptions"""
    return JSONResponse(
        status_code=exc.status,
        content={"error": {"code": exc.code, "message": exc.message}},
    )


async def http_exception_handler(request: Request, exc):
    """Handle FastAPI HTTPException"""
    from fastapi import HTTPException

    if isinstance(exc, HTTPException):
        detail = exc.detail if isinstance(exc.detail, str) else "http_error"
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": {"code": "http_error", "message": detail}},
        )
