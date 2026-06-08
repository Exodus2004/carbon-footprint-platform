"""AI service module utilizing the Gemini REST API with connection pooling and cryptographic caching."""

import os
import logging
import hashlib
import httpx
import msgspec
from typing import Dict, Union

from app.core.constants import (
    IPCC_CO2E_TRANSPORT_FACTOR,
    EPA_CO2E_GRID_FACTOR,
    DIET_CO2E_FACTOR,
)

logger: logging.Logger = logging.getLogger(__name__)

# Cryptographic zero-latency cache layer (deterministic cache keys via SHA256)
_insights_crypto_cache: Dict[str, Dict[str, Union[str, float]]] = {}


class TextPart(msgspec.Struct):
    """Msgspec representation of a Gemini response text part."""
    text: str


class Content(msgspec.Struct):
    """Msgspec representation of a Gemini response content object."""
    parts: list[TextPart]


class Candidate(msgspec.Struct):
    """Msgspec representation of a Gemini response candidate object."""
    content: Content


class GeminiResponse(msgspec.Struct):
    """Msgspec representation of a Gemini REST API response envelope."""
    candidates: list[Candidate]


class GeminiInsights(msgspec.Struct):
    """Msgspec representation of the structured JSON schema returned by Gemini."""
    iso_14064_scope_1_kg: float
    iso_14064_scope_2_kg: float
    esg_compliance_rating: str
    actionable_epa_strategy: str


class TextPartInput(msgspec.Struct):
    """Msgspec representation of a Gemini payload text part."""
    text: str


class ContentInput(msgspec.Struct):
    """Msgspec representation of a Gemini payload content object."""
    parts: list[TextPartInput]


class GenerationConfigInput(msgspec.Struct):
    """Msgspec representation of a Gemini payload generation config."""
    responseMimeType: str
    responseSchema: dict[str, Union[str, dict[str, dict[str, str]], list[str]]]


class GeminiPayload(msgspec.Struct):
    """Msgspec representation of the Gemini generateContent payload."""
    contents: list[ContentInput]
    generationConfig: GenerationConfigInput


async def generate_carbon_insights(
    client: httpx.AsyncClient,
    metrics: Dict[str, Union[int, float]]
) -> Dict[str, Union[str, float]]:
    """Generates ESG and ISO 14064-1 compliant carbon insights using Gemini.

    Args:
        client: A persistent httpx.AsyncClient session context.
        metrics: Dictionary containing user metrics.

    Returns:
        A dictionary with keys: status, insights, and calculated_co2e.
    """
    transportation: float = float(metrics.get("transportation_miles", 0.0))
    energy: float = float(metrics.get("energy_kwh", 0.0))
    diet: int = int(metrics.get("diet_meat_meals", 0))

    # ISO 14064-1 / GHG Protocol calculations based on regulation constants
    scope1: float = transportation * IPCC_CO2E_TRANSPORT_FACTOR
    scope2: float = energy * EPA_CO2E_GRID_FACTOR
    scope3: float = diet * DIET_CO2E_FACTOR
    total_co2e: float = round(scope1 + scope2 + scope3, 2)

    # Cryptographic hash key generation to prevent redundant outbound requests
    normalized_metrics = {
        "diet_meat_meals": diet,
        "energy_kwh": round(energy, 2),
        "transportation_miles": round(transportation, 2)
    }
    serialized_payload: bytes = msgspec.json.encode(normalized_metrics)
    cache_key: str = hashlib.sha256(serialized_payload).hexdigest()

    if cache_key in _insights_crypto_cache:
        logger.info(f"Zero-latency cache hit for hash key: {cache_key}")
        return _insights_crypto_cache[cache_key]

    api_key: str = os.getenv("GEMINI_API_KEY", "")
    if not api_key:
        logger.warning("GEMINI_API_KEY not configured. Returning mock data.")
        mock_insights = (
            f"ISO 14064 Scope 1: {scope1:.2f} kg CO2e. "
            f"Scope 2: {scope2:.2f} kg CO2e. "
            f"ESG Compliance Rating: B+. "
            f"Strategy: Implement home energy efficiency checks and reduce weekly transport miles."
        )
        mock_data: Dict[str, Union[str, float]] = {
            "status": "success",
            "insights": mock_insights,
            "calculated_co2e": total_co2e
        }
        _insights_crypto_cache[cache_key] = mock_data
        return mock_data

    # Rigid JSON Schema constraint for Gemini response
    schema: dict[str, Union[str, dict[str, dict[str, str]], list[str]]] = {
        "type": "OBJECT",
        "properties": {
            "iso_14064_scope_1_kg": {"type": "NUMBER"},
            "iso_14064_scope_2_kg": {"type": "NUMBER"},
            "esg_compliance_rating": {"type": "STRING"},
            "actionable_epa_strategy": {"type": "STRING"}
        },
        "required": ["iso_14064_scope_1_kg", "iso_14064_scope_2_kg", "esg_compliance_rating", "actionable_epa_strategy"]
    }

    prompt: str = (
        f"I am building a Carbon Footprint ESG Compliance Platform. "
        f"A user has submitted the following weekly metrics conforming to ISO 14064-1 & GHG Protocol Corporate Standard:\n"
        f"- Transportation: {transportation} miles driven (Scope 1 Direct: {scope1:.2f} kg CO2e).\n"
        f"- Energy usage: {energy} kWh (Scope 2 Indirect: {scope2:.2f} kg CO2e).\n"
        f"- Diet: {diet} meat-heavy meals (Scope 3: {scope3:.2f} kg CO2e).\n"
        f"- Total Calculated Weekly Footprint: {total_co2e:.2f} kg CO2e.\n\n"
        f"Analyze these inputs and return the exact ISO Scope 1 and Scope 2 metrics, a letter rating for ESG compliance (e.g. A, B-, C) "
        f"based on target reductions, and a specific, actionable EPA-aligned strategy to reduce their impact."
    )

    payload = GeminiPayload(
        contents=[
            ContentInput(parts=[TextPartInput(text=prompt)])
        ],
        generationConfig=GenerationConfigInput(
            responseMimeType="application/json",
            responseSchema=schema
        )
    )

    url: str = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.5-flash:generateContent?key={api_key}"

    try:
        response: httpx.Response = await client.post(
            url,
            content=msgspec.json.encode(payload),
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
        
        # Parse output utilizing typed msgspec Structs
        response_envelope = msgspec.json.decode(response.content, type=GeminiResponse)
        raw_text: str = response_envelope.candidates[0].content.parts[0].text
        result = msgspec.json.decode(raw_text, type=GeminiInsights)
        
        insights_text = (
            f"ISO 14064 Scope 1: {result.iso_14064_scope_1_kg:.2f} kg CO2e. "
            f"Scope 2: {result.iso_14064_scope_2_kg:.2f} kg CO2e. "
            f"ESG Compliance Rating: {result.esg_compliance_rating}. "
            f"Strategy: {result.actionable_epa_strategy}"
        )

        final_result: Dict[str, Union[str, float]] = {
            "status": "success",
            "insights": insights_text,
            "calculated_co2e": total_co2e
        }
        
        _insights_crypto_cache[cache_key] = final_result
        return final_result

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
            "insights": "We encountered an issue generating your ESG compliance insights. Please try again later.",
            "calculated_co2e": total_co2e
        }
