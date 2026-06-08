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

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Carbon Footprint Platform API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Global Exception Handlers – catch everything, never leak stack traces
# ---------------------------------------------------------------------------

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Intercepts Pydantic / FastAPI 422 validation errors and returns a
    sanitised response that lists field-level issues without exposing
    internal model structure or stack traces.
    """
    safe_errors = []
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
    """
    Catch-all for any unhandled exception.  The full traceback is written
    to the server log but the client only receives a generic message.
    """
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
    transportation_miles: float = Field(..., ge=0, description="Miles traveled using carbon-emitting transport")
    energy_kwh: float = Field(..., ge=0, description="Energy usage in kilowatt-hours")
    diet_meat_meals: int = Field(..., ge=0, description="Number of meat-heavy meals consumed")

class CarbonResponse(BaseModel):
    status: str
    insights: str


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.post("/api/v1/carbon", response_model=CarbonResponse)
async def submit_carbon_data(
    metrics: CarbonMetrics,
    user_id: str = Depends(verify_firebase_token)
):
    """
    Submit carbon metrics for a user, stream to BigQuery, and get AI insights.
    """
    try:
        # Stream data to BigQuery
        stream_carbon_data(user_id, metrics.dict())

        # Generate personalized AI insights
        insights = generate_carbon_insights(metrics.dict())

        return {"status": "success", "insights": insights}
    except Exception as e:
        logger.error(f"Error processing carbon data: {e}")
        raise HTTPException(status_code=500, detail="Internal server error while processing data")


@app.get("/health")
def health_check():
    return {"status": "healthy"}
