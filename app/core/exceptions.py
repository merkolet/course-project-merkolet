"""Enhanced exception handling with RFC 7807 support (ADR-001)"""

import uuid
from datetime import datetime, timezone
from typing import Optional

from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel


class ProblemDetail(BaseModel):
    """RFC 7807 Problem Details model"""

    type: str
    title: str
    status: int
    detail: str
    correlation_id: str
    timestamp: str  # ISO string instead of datetime
    instance: Optional[str] = None


class ApiError(Exception):
    """Custom API exception with RFC 7807 support"""

    def __init__(self, code: str, message: str, status: int = 400):
        self.code = code
        self.message = message
        self.status = status
        super().__init__(message)


def create_problem_detail(
    error_type: str,
    title: str,
    status: int,
    detail: str,
    request: Request,
    instance: Optional[str] = None,
) -> ProblemDetail:
    """Create RFC 7807 Problem Detail"""
    correlation_id = getattr(request.state, "correlation_id", str(uuid.uuid4()))

    return ProblemDetail(
        type=f"https://api.wishlist.com/problems/{error_type}",
        title=title,
        status=status,
        detail=detail,
        instance=instance or str(request.url),
        correlation_id=correlation_id,
        timestamp=datetime.now(timezone.utc).isoformat(),
    )


async def api_error_handler(request: Request, exc: ApiError):
    """Handle ApiError with RFC 7807 format"""
    problem_detail = create_problem_detail(
        error_type=exc.code,
        title="API Error",
        status=exc.status,
        detail=exc.message,
        request=request,
    )

    response = JSONResponse(
        status_code=exc.status,
        content=problem_detail.model_dump(),
        headers={"Content-Type": "application/problem+json"},
    )

    # Add correlation ID to response headers
    response.headers["X-Correlation-ID"] = problem_detail.correlation_id
    return response


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle RequestValidationError with RFC 7807 format"""
    problem_detail = create_problem_detail(
        error_type="validation-error",
        title="Validation Failed",
        status=422,
        detail=f"Request validation failed: {exc.errors()}",
        request=request,
    )

    response = JSONResponse(
        status_code=422,
        content=problem_detail.model_dump(),
        headers={"Content-Type": "application/problem+json"},
    )

    # Add correlation ID to response headers
    response.headers["X-Correlation-ID"] = problem_detail.correlation_id
    return response


async def http_exception_handler(request: Request, exc):
    """Handle HTTPException with RFC 7807 format"""
    problem_detail = create_problem_detail(
        error_type="http-error",
        title="HTTP Error",
        status=exc.status_code,
        detail=str(exc.detail),
        request=request,
    )

    response = JSONResponse(
        status_code=exc.status_code,
        content=problem_detail.model_dump(),
        headers={"Content-Type": "application/problem+json"},
    )

    # Add correlation ID to response headers
    response.headers["X-Correlation-ID"] = problem_detail.correlation_id
    return response
