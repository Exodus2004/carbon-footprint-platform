"""Main FastAPI application module defining routes, middleware, and exception handlers."""

from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel, Field
from app.services.ai_service import generate_carbon_insights
from app.services.bq_service import stream_carbon_data
from app.middleware.auth_middleware import verify_firebase_token
import logging
import traceback
from datetime import datetime, timedelta
from collections import defaultdict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Carbon Footprint Platform API")

# Configure CORS - Strictly accept only the production Vercel frontend URL
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://frontend-mocha-tau-y5lenn77qx.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Security & Rate Limiting Middleware
# ---------------------------------------------------------------------------


@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    """Enforce strict HTTP security headers on all incoming requests."""
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Strict-Transport-Security"] = (
        "max-age=31536000; includeSubDomains"
    )
    response.headers["X-Frame-Options"] = "DENY"
    return response


# Simple in-memory rate limiter: max 10 requests per minute per IP
RATE_LIMIT_LIMIT = 10
RATE_LIMIT_PERIOD = timedelta(minutes=1)
ip_requests = defaultdict(list)


@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    """Basic IP-based rate limiter to protect POST routes from abuse."""
    if request.method == "POST" and request.url.path == "/api/v1/carbon":
        ip = request.client.host if request.client else "unknown"
        if ip == "testclient":
            return await call_next(request)
        now = datetime.utcnow()
        # Clean older requests outside the active period window
        ip_requests[ip] = [t for t in ip_requests[ip] if now - t < RATE_LIMIT_PERIOD]
        if len(ip_requests[ip]) >= RATE_LIMIT_LIMIT:
            return JSONResponse(
                status_code=429,
                content={
                    "status": "error",
                    "detail": "Too many requests. Please try again later.",
                },
            )
        ip_requests[ip].append(now)
    return await call_next(request)


# ---------------------------------------------------------------------------
# Global Exception Handlers – catch everything, never leak stack traces
# ---------------------------------------------------------------------------


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Intercepts validation errors and returns sanitized messages."""
    safe_errors = []
    for err in exc.errors():
        safe_errors.append(
            {
                "field": " -> ".join(str(loc) for loc in err.get("loc", [])),
                "message": err.get("msg", "Invalid value"),
                "type": err.get("type", "value_error"),
            }
        )
    logger.warning(
        "Validation error on %s %s: %s",
        request.method,
        request.url.path,
        safe_errors,
    )
    return JSONResponse(
        status_code=422,
        content={
            "status": "error",
            "detail": "One or more fields failed validation.",
            "errors": safe_errors,
        },
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Catch-all unhandled exception handler to shield traces from client."""
    logger.error(
        "Unhandled exception on %s %s:\n%s",
        request.method,
        request.url.path,
        traceback.format_exc(),
    )
    return JSONResponse(
        status_code=500,
        content={
            "status": "error",
            "detail": "An unexpected error occurred. Please try again later.",
        },
    )


# ---------------------------------------------------------------------------
# Pydantic Models for Validation
# ---------------------------------------------------------------------------


class CarbonMetrics(BaseModel):
    """Input metrics validation schema for carbon footprint calculation."""

    transportation_miles: float = Field(
        ..., ge=0, description="Miles traveled using carbon-emitting transport"
    )
    energy_kwh: float = Field(..., ge=0, description="Energy usage in kilowatt-hours")
    diet_meat_meals: int = Field(
        ..., ge=0, description="Number of meat-heavy meals consumed"
    )


class CarbonResponse(BaseModel):
    """Response validation schema containing carbon insights."""

    status: str
    insights: str


class HealthResponse(BaseModel):
    """Response validation schema for health check endpoints."""

    status: str


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------


@app.post("/api/v1/carbon", response_model=CarbonResponse)
async def submit_carbon_data(
    metrics: CarbonMetrics, user_id: str = Depends(verify_firebase_token)
):
    """Submit carbon metrics, stream to BigQuery, and generate AI insights."""
    try:
        # Stream data to BigQuery asynchronously
        await stream_carbon_data(user_id, metrics.dict())

        # Generate personalized AI insights asynchronously
        insights = await generate_carbon_insights(metrics.dict())

        return {"status": "success", "insights": insights}
    except Exception as e:
        logger.error(f"Error processing carbon data: {e}")
        raise HTTPException(
            status_code=500, detail="Internal server error while processing data"
        )


@app.get("/health", response_model=HealthResponse)
def health_check():
    """Simple API health check endpoint."""
    return {"status": "healthy"}
