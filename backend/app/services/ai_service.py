"""AI service module containing helper methods for interacting with Gemini APIs."""

import google.generativeai as genai
import os
import logging

logger = logging.getLogger(__name__)

# Configure Gemini API
api_key = os.getenv("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)

# Simple in-memory cache to prevent redundant API calls for identical metric inputs
_insights_cache = {}


async def generate_carbon_insights(metrics: dict) -> str:
    """Generates personalized actionable insights based on carbon metrics.

    Args:
        metrics: A dictionary containing the user's transportation, energy, and diet stats.

    Returns:
        A string containing encouraging, specific, and actionable insights.
    """
    transportation = metrics.get("transportation_miles", 0)
    energy = metrics.get("energy_kwh", 0)
    diet = metrics.get("diet_meat_meals", 0)

    # Use rounded tuple as the cache key to handle minor float differences
    cache_key = (round(float(transportation), 2), round(float(energy), 2), int(diet))

    if cache_key in _insights_cache:
        logger.info(f"Returning cached insights for metrics: {cache_key}")
        return _insights_cache[cache_key]

    prompt = (
        f"I am building a Carbon Footprint Awareness Platform. "
        f"A user has submitted the following weekly metrics:\n"
        f"- Transportation: {transportation} miles driven.\n"
        f"- Energy usage: {energy} kWh.\n"
        f"- Diet: {diet} meat-heavy meals.\n\n"
        f"Provide a brief, encouraging, and highly specific 3-sentence recommendation "
        f"on how they can reduce their carbon footprint this week. Focus on the highest impact area."
    )

    try:
        if not api_key:
            logger.warning("GEMINI_API_KEY not set. Returning mock insights.")
            mock_insight = (
                "Consider carpooling or biking for your transportation needs this week. "
                "Reducing your meat consumption by even one meal can significantly lower your footprint. "
                "Small changes in daily habits lead to major environmental impact."
            )
            _insights_cache[cache_key] = mock_insight
            return mock_insight

        model = genai.GenerativeModel("gemini-3.5-flash")
        response = await model.generate_content_async(prompt)
        insight_text = response.text.strip()

        # Cache the successful insight response
        _insights_cache[cache_key] = insight_text
        return insight_text
    except Exception as e:
        logger.error(f"Failed to generate Gemini insights: {e}")
        err_msg = str(e).lower()
        if "429" in err_msg or "quota" in err_msg or "resource_exhausted" in err_msg:
            return "The AI service is currently rate-limited on the free tier. Please wait about 30 seconds and try again."
        return "We encountered an issue generating your personalized insights. Please try again later."
