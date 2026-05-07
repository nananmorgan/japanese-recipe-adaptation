# Japanese Recipe Adaptation with Generative AI

## Live Demo
Try the app here: [Recipe Drift Checker](https://nanas-recipe-drift-checker.streamlit.app)

## Overview
A web application that takes a recipe URL and a zip code, then adapts the recipe to use ingredients and techniques available in that location, with a focus on Japanese-style adaptations. The system combines GPT-based recipe generation, a fine-tuned GPT-4.1 model for ingredient role classification, and a custom "recipe drift" scoring algorithm that measures how far an adapted recipe has deviated from the original.

## Key Features
- **Recipe Fetching**: Accepts any recipe URL and extracts ingredients and instructions using GPT with structured output (Pydantic models)
- **Location-Aware Adaptation**: Adapts the recipe based on the user's zip code, tailoring ingredient substitutions to what's locally available
- **Ingredient Role Classification**: A fine-tuned GPT-4.1 model (`ft:gpt-4.1-2025-04-14`) classifies each ingredient as *core*, *supporting*, or *optional*
- **Model-Based Change Detection**: A second GPT model compares original and adapted ingredient lists and maps each original ingredient to one of: *unchanged*, *swapped*, or *removed* — more robust than simple string matching
- **Drift Scoring**: A custom algorithm computes a drift level (LOW / MEDIUM / HIGH) based on how many core and supporting ingredients were changed
- **Interactive Web App**: Clean, styled Streamlit interface deployed to Streamlit Community Cloud

## How the Drift Score Works
- **LOW**: No core ingredients changed AND 2 or fewer supporting ingredients changed
- **MEDIUM**: 1–2 core ingredients changed OR 3+ supporting ingredients changed
- **HIGH**: 3 or more core ingredients changed

## Tools & Models
- **GPT-5** for recipe extraction and adaptation
- **Fine-tuned GPT-4.1** for ingredient role classification (trained on a custom dataset)
- **Pydantic** for structured model outputs
- **Streamlit** for web application deployment
- **Python** (openai, re, json)

## Repository Contents
```
japanese-recipe-adaptation/
├── recipe_adaptation.ipynb   # Development notebook — pipeline logic and testing
├── recipe_adaptation_app.py  # Streamlit web application
├── presentation.pptx         # Project presentation slides
├── requirements.txt          # Python dependencies
└── README.md
```

## Note on API Key
This app requires a valid OpenAI API key to run locally. When running via Streamlit Community Cloud, the key is stored as a secret. To run locally, set your key as an environment variable: `export OPENAI_API_KEY=your_key_here`
