# Democracyverse (Election Process Education)

This is an interactive web application designed for the Google Prompt Wars hackathon. It guides users through the voter journey and features an AI Townhall simulator powered by the Google Gemini API.

## Features
- **Voter Journey Timeline:** Step-by-step educational guide.
- **AI Townhall:** Input a political topic and watch Gemini simulate a debate between two personas.
- **Civics Quiz:** Test your knowledge.
- **Bilingual Support:** Instantly toggle between English and Telugu.
- **WCAG AA Compliant:** High-contrast dark theme with glassmorphism.

## Setup
1. Clone this repository.
2. Run `npm install`.
3. Create a `.env` file with `VITE_GEMINI_API_KEY="your_api_key_here"`.
4. Run `npm run dev`.

## Security (Google Cloud Key Restrictions)
Since Vite exposes variables prefixed with `VITE_` to the client-side code, it is highly recommended to lock down your Gemini API key:
1. Go to the **Google Cloud Console** -> **APIs & Services** -> **Credentials**.
2. Click your **Gemini API Key**.
3. Under **Application restrictions**, select **Websites**.
4. Add your exact Cloud Run URL (e.g., `https://democracyverse-xyz123.a.run.app/*`).

This ensures that even if someone inspects the source code and finds the key, Google will block any requests that don't originate from your live app.
