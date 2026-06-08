"""AI service module utilizing the Gemini REST API with connection pooling and caching."""

import os
import logging
import httpx
import orjson
from typing import Dict, Any, Tuple

logger: logging.Logger = logging.getLogger(__name__)

# Persistent in-memory cache for carbon calculations and insights
_insights_cache: Dict[Tuple[float, float, int], Dict[str, Any]] = {}

async def generate_carbon_insights(
    client: httpx.AsyncClient,
    metrics: Dict[str, Any]
) -> Dict[str, Any]:
    """Generates personalized carbon insights conforming to the GHG Protocol.

    Args:
        client: A persistent httpx.AsyncClient session context.
        metrics: Dictionary containing user metrics (transportation, energy, diet).

    Returns:
        A dictionary with keys: status, insights, and calculated_co2e.
    """
    transportation: float = float(metrics.get("transportation_miles", 0.0))
    energy: float = float(metrics.get("energy_kwh", 0.0))
    diet: int = int(metrics.get("diet_meat_meals", 0))

    # GHG Protocol calculations
    scope1: float = transportation * 0.404  # Scope 1: Direct emissions (miles driven)
    scope2: float = energy * 0.385          # Scope 2: Indirect lifecycle emissions (electricity)
    scope3: float = diet * 2.5              # Scope 3: Diet emissions (meat meals)
    total_co2e: float = round(scope1 + scope2 + scope3, 2)

    cache_key: Tuple[float, float, int] = (
        round(transportation, 2),
        round(energy, 2),
        diet
    )

    if cache_key in _insights_cache:
        logger.info(f"Returning cached insights for metrics: {cache_key}")
        return _insights_cache[cache_key]

    api_key: str = os.getenv("GEMINI_API_KEY", "")
    if not api_key:
        logger.warning("GEMINI_API_KEY not configured. Returning mock data.")
        mock_data: Dict[str, Any] = {
            "status": "success",
            "insights": (
                "Your Scope 1 transportation emissions represent a significant impact. "
                "Reducing vehicle travel and shifting to a plant-based diet will lower Scope 3. "
                "Small, persistent household energy reductions will cut Scope 2 lifecycle emissions."
            ),
            "calculated_co2e": total_co2e
        }
        _insights_cache[cache_key] = mock_data
        return mock_data

    # Rigid JSON Schema constraint for Gemini response
    schema: Dict[str, Any] = {
        "type": "OBJECT",
        "properties": {
            "status": {"type": "STRING"},
            "insights": {"type": "STRING"},
            "calculated_co2e": {"type": "NUMBER"}
        },
        "required": ["status", "insights", "calculated_co2e"]
    }

    prompt: str = (
        f"I am building a Carbon Footprint Awareness Platform. "
        f"A user has submitted the following weekly metrics conforming to the Greenhouse Gas (GHG) Protocol Corporate Standard:\n"
        f"- Transportation: {transportation} miles driven (Scope 1 Direct: {scope1:.2f} kg CO2e).\n"
        f"- Energy usage: {energy} kWh (Scope 2 Indirect Lifecycle: {scope2:.2f} kg CO2e).\n"
        f"- Diet: {diet} meat-heavy meals (Scope 3 Diet: {scope3:.2f} kg CO2e).\n"
        f"- Total Calculated Weekly Footprint: {total_co2e:.2f} kg CO2e.\n\n"
        f"Provide a brief, encouraging, and highly specific 3-sentence recommendation "
        f"on how they can reduce their carbon footprint this week based on these exact math inputs. Focus on the highest impact area."
    )

    payload: Dict[str, Any] = {
        "contents": [
            {
                "parts": [
                    {"text": prompt}
                ]
            }
        ],
        "generationConfig": {
            "responseMimeType": "application/json",
            "responseSchema": schema
        }
    }

    url: str = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.5-flash:generateContent?key={api_key}"

    try:
        # Utilize pooled HTTP client for zero-handshake overhead
        response: httpx.Response = await client.post(
            url,
            content=orjson.dumps(payload),
            headers={"Content-Type": "application/json"},
            timeout=15.0
        )
        
        if response.status_code == 429:
            logger.error("Gemini API returned 429 Rate Limited.")
            return {
                "status": "error",
                "insights": "The AI service is currently rate-limited on the free tier. Please wait about 30 seconds and try again.",
                "calculated_co2e": total_co2e
            }

        response.raise_for_status()
        
        # Parse output utilizing high-performance orjson
        response_data: Dict[str, Any] = orjson.loads(response.content)
        raw_text: str = response_data["candidates"][0]["content"]["parts"][0]["text"]
        result: Dict[str, Any] = orjson.loads(raw_text)
        
        # Ground total calculated CO2e mathematically to our local calculation
        result["calculated_co2e"] = total_co2e
        
        _insights_cache[cache_key] = result
        return result

    except Exception as e:
        logger.error(f"Error communicating with Gemini REST API: {e}")
        err_msg: str = str(e).lower()
        if "429" in err_msg or "quota" in err_msg or "resource_exhausted" in err_msg:
            return {
                "status": "error",
                "insights": "The AI service is currently rate-limited on the free tier. Please wait about 30 seconds and try again.",
                "calculated_co2e": total_co2e
            }
        return {
            "status": "error",
            "insights": "We encountered an issue generating your personalized insights. Please try again later.",
            "calculated_co2e": total_co2e
        }
