import google.generativeai as genai
from dotenv import load_dotenv
import os

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("❌ ERROR: No se encontró la clave 'GEMINI_API_KEY'.")
    exit(1)

genai.configure(api_key=api_key)

model = genai.GenerativeModel(model_name="models/gemini-2.5-flash")
models = genai.list_models()
for model in models:
    print(model)
