import google.generativeai as genai
from dotenv import load_dotenv
import os

# Load .env file to get your GEMINI_API_KEY
load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    print("Error: GEMINI_API_KEY environment variable not set in your .env file.")
else:
    genai.configure(api_key=GEMINI_API_KEY)
    print("Configured Gemini API. Attempting to list models...")
    try:
        found_models = False
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                print(f"  Model name: {m.name}, Display name: {m.display_name}")
                found_models = True
        if not found_models:
            print("No models found that support 'generateContent' with your API key.")
    except Exception as e:
        print(f"An error occurred while listing models: {e}")