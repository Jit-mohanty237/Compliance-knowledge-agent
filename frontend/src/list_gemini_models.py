import os
import google.generativeai as genai
from dotenv import load_dotenv
load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

print("Listing available models from Google Generative AI SDK:")
try:
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(f"Model Name: {m.name}, Display: {m.display_name}")
except Exception as e:
    print("Error listing models:", e)
