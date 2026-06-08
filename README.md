# Carbon Footprint Awareness Platform

A full-stack application to track, analyze, and gain insights into individual carbon footprints using AI.

## Architecture

- **Backend:** FastAPI (Python), Google Gemini API, BigQuery Streaming, Firebase Auth Middleware
- **Frontend:** React, Vite, TailwindCSS (via standard CSS utilities), Accessible UI Components

## Local Development

1. Set up your `.env` file with necessary keys (e.g., `GEMINI_API_KEY`).
2. Run `docker-compose up --build`.
3. The backend API is available at `http://localhost:8000`.
4. The frontend app is available at `http://localhost:5173`.

## Security & Accessibility

- The backend implements Firebase token verification and strict Pydantic model validation.
- The frontend enforces semantic HTML5 and ARIA labels for accessibility.
