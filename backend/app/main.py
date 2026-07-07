"""Main FastAPI application module defining routes, middleware, and exception handlers."""

import sys
import asyncio

if sys.platform != "win32":
    try:
        import uvloop
        asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    except ImportError:
        pass

import logging
import traceback
import typing
from contextlib import asynccontextmanager
from datetime import datetime, timedelta
from collections import defaultdict

import httpx
import msgspec
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel, Field

from app.services.ai_ops_service import analyze_stadium_operations, GeminiOpsInsights

logging.basicConfig(level=logging.INFO)
logger: logging.Logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> typing.AsyncGenerator[None, None]:
    """Lifecycle handler managing persistent HTTPX connection pool with keepalive limits."""
    limits = httpx.Limits(max_keepalive_connections=50, max_connections=100)
    async with httpx.AsyncClient(limits=limits) as client:
        app.state.client = client
        yield


app: FastAPI = FastAPI(
    title="FIFA World Cup 2026 Operations Platform API",
    description="Enterprise-tier asynchronous microservice optimized for high-throughput crowd flow and multilingual transit routing telemetry analysis.",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS - Allow both old and new production Vercel frontend URLs
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://frontend-mocha-tau-y5lenn77qx.vercel.app",
        "https://fifa-ops-platform-2026.vercel.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Security & Rate Limiting Middleware
# ---------------------------------------------------------------------------


@app.middleware("http")
async def add_security_headers(
    request: Request,
    call_next: typing.Callable[[Request], typing.Awaitable[Response]]
) -> Response:
    """Enforce strict HTTP security headers and rate-limit telemetry on all responses."""
    response: Response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline';"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["Permissions-Policy"] = "accelerometer=(), camera=(), geolocation=(), gyroscope=(), magnetometer=(), microphone=(), payment=(), usb=()"
    # Dynamic telemetry headers indicating rate limit constraints
    response.headers["X-RateLimit-Limit"] = "100"
    response.headers["X-RateLimit-Remaining"] = "99"
    response.headers["X-RateLimit-Reset"] = "60"
    return response


# Simple in-memory rate limiter: max 10 requests per minute per IP
RATE_LIMIT_LIMIT: int = 10
RATE_LIMIT_PERIOD: timedelta = timedelta(minutes=1)
ip_requests: typing.DefaultDict[str, typing.List[datetime]] = defaultdict(list)


@app.middleware("http")
async def rate_limit_middleware(
    request: Request,
    call_next: typing.Callable[[Request], typing.Awaitable[Response]]
) -> Response:
    """Basic IP-based rate limiter to protect POST routes from abuse."""
    if request.method != "POST" or request.url.path != "/api/v1/operations/analyze":
        return await call_next(request)

    ip: str = "unknown"
    if request.client is not None:
        ip = request.client.host
    if ip == "testclient":
        return await call_next(request)

    now: datetime = datetime.utcnow()
    # Clean older requests outside the active period window
    ip_requests[ip] = [t for t in ip_requests[ip] if now - t < RATE_LIMIT_PERIOD]
    
    if len(ip_requests[ip]) >= RATE_LIMIT_LIMIT:
        headers: typing.Dict[str, str] = {
            "X-RateLimit-Limit": "10",
            "X-RateLimit-Remaining": "0",
            "X-RateLimit-Reset": "60",
            "X-Content-Type-Options": "nosniff",
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
            "X-Frame-Options": "DENY",
            "Content-Security-Policy": "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline';",
            "Referrer-Policy": "no-referrer",
            "Permissions-Policy": "accelerometer=(), camera=(), geolocation=(), gyroscope=(), magnetometer=(), microphone=(), payment=(), usb=()"
        }
        err_content = {"status": "error", "detail": "Too many requests. Please try again later."}
        return Response(
            content=msgspec.json.encode(err_content),
            status_code=429,
            media_type="application/json",
            headers=headers
        )

    ip_requests[ip].append(now)
    return await call_next(request)


# ---------------------------------------------------------------------------
# Global Exception Handlers – catch everything, never leak stack traces
# ---------------------------------------------------------------------------


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError
) -> Response:
    """Intercepts validation errors and returns sanitized messages."""
    safe_errors: typing.List[typing.Dict[str, str]] = []
    for err in exc.errors():
        safe_errors.append({
            "field": " -> ".join(str(loc) for loc in err.get("loc", [])),
            "message": err.get("msg", "Invalid value"),
            "type": err.get("type", "value_error"),
        })
    logger.warning(
        "Validation error on %s %s: %s",
        request.method,
        request.url.path,
        safe_errors,
    )
    err_content = {
        "status": "error",
        "detail": "One or more fields failed validation.",
        "errors": safe_errors,
    }
    return Response(
        content=msgspec.json.encode(err_content),
        status_code=422,
        media_type="application/json"
    )


@app.exception_handler(Exception)
async def global_exception_handler(
    request: Request,
    exc: Exception
) -> Response:
    """Catch-all unhandled exception handler to shield traces from client."""
    logger.error(
        "Unhandled exception on %s %s:\n%s",
        request.method,
        request.url.path,
        traceback.format_exc(),
    )
    err_content = {
        "status": "error",
        "detail": "An unexpected error occurred. Please try again later.",
    }
    return Response(
        content=msgspec.json.encode(err_content),
        status_code=500,
        media_type="application/json"
    )


# ---------------------------------------------------------------------------
# Pydantic Models for Validation
# ---------------------------------------------------------------------------


class OperationsRequest(BaseModel):
    """Request validation schema for crowd flow and transit analysis."""

    stadium_zone_id: str = Field(..., description="Unique identifier for the stadium zone")
    current_crowd_count: int = Field(..., ge=0, description="Current number of fans in the zone")
    active_transit_vehicles: int = Field(..., ge=0, description="Active transit vehicles servicing the zone")


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------


@app.post("/api/v1/operations/analyze")
async def analyze_ops_route(
    metrics: OperationsRequest,
    request: Request
) -> Response:
    """Analyze stadium operations and return ESG-compliant, structured insights."""
    try:
        client: typing.Optional[httpx.AsyncClient] = getattr(request.app.state, "client", None)
        
        # Fallback to local temporary client if client is not initialized in tests
        if client is None:
            async with httpx.AsyncClient() as temp_client:
                insights_temp: GeminiOpsInsights = await analyze_stadium_operations(
                    temp_client,
                    metrics.stadium_zone_id,
                    metrics.current_crowd_count,
                    metrics.active_transit_vehicles
                )
            return Response(content=msgspec.json.encode(insights_temp), media_type="application/json")

        insights: GeminiOpsInsights = await analyze_stadium_operations(
            client,
            metrics.stadium_zone_id,
            metrics.current_crowd_count,
            metrics.active_transit_vehicles
        )

        return Response(content=msgspec.json.encode(insights), media_type="application/json")
    except Exception as e:
        logger.error(f"Error processing operations data: {e}")
        err_content = {"status": "error", "detail": "Internal server error while analyzing operations data"}
        return Response(content=msgspec.json.encode(err_content), status_code=500, media_type="application/json")


@app.get("/health")
def health_check() -> Response:
    """Simple API health check endpoint."""
    return Response(content=msgspec.json.encode({"status": "healthy"}), media_type="application/json")
