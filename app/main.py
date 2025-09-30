from fastapi import FastAPI, HTTPException

from app.api.wishes import router as wishes_router
from app.core.exceptions import ApiError, api_error_handler, http_exception_handler

app = FastAPI(
    title="Wishlist API",
    version="0.1.0",
    description="API для управления списком желаемых вещей",
)

# Register exception handlers
app.add_exception_handler(ApiError, api_error_handler)
app.add_exception_handler(HTTPException, http_exception_handler)

# Include routers
app.include_router(wishes_router)


@app.get("/health")
def health():
    """Health check endpoint"""
    return {"status": "ok"}
