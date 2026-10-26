# Food Verse AI — Multimodal Food Intelligence Agent

Skill Wallet Capstone Project 3. Streamlit app for food image analysis, visible freshness cues, kitchen hygiene screening, pantry recipes, and meal planning. It runs without an API key in demo mode and uses no external database.

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

The app starts with **Google Gemini** selected. Enter your API key in the sidebar to run live vision analysis, recipe generation, personalized meal planning, and video kitchen review. Alternatively select **Groq** for image analysis and text generation. The key is entered as a password and held in Streamlit session memory; it is not written to config. Uploaded media and prompts are sent to the selected provider. **Demo mode** is an explicit sample-only option and needs no key.

## Streamlit Community Cloud deployment

1. Push the project to GitHub.
2. Create an app from that repository and set the main file to `app.py`.
3. Deploy; dependencies are listed in `requirements.txt`.
4. Users can enter their own API key in the sidebar.

No database, model download, or account system is required.

## Modules

- Nutrition audit: dish, ingredients, portion, macros, likely allergens, and health score estimates.
- Freshness check: visible cues, freshness stage, cautious action, and storage guidance.
- Kitchen safety: visible indicator score, checklist, and corrective actions. Gemini video mode analyzes uploaded clips; Groq mode supports images.
- Recipe assistant: pantry recipes with dietary preferences, time, steps, and substitutions; demo mode provides a template.
- Meal planner: Mifflin–St Jeor BMR/TDEE, seven-day outline, and downloadable starter grocery list.

## Limitations

AI outputs are estimates, not diagnoses, allergen guarantees, food-safety determinations, or regulatory inspections. Images cannot reveal temperature history, internal contamination, exact ingredients, or exact portion weight. The meal schedule is a general template, not medical nutrition therapy. The BMR formula uses binary sex constants; individual energy needs vary. Seek qualified guidance where health or safety is at stake.
