import google.generativeai as genai
import os
import logging

logger = logging.getLogger(__name__)

# Configure Gemini API
api_key = os.getenv("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)

def generate_carbon_insights(metrics: dict) -> str:
    """
    Uses Google Gemini API to generate personalized actionable insights
    based on the user's carbon metrics.
    """
    transportation = metrics.get('transportation_miles', 0)
    energy = metrics.get('energy_kwh', 0)
    diet = metrics.get('diet_meat_meals', 0)

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
            return (
                "Consider carpooling or biking for your transportation needs this week. "
                "Reducing your meat consumption by even one meal can significantly lower your footprint. "
                "Small changes in daily habits lead to major environmental impact."
            )

        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        logger.error(f"Failed to generate Gemini insights: {e}")
        return "We encountered an issue generating your personalized insights. Please try again later."
