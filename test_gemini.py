import os
import google.generativeai as genai

# Configure API
api_key = os.getenv('GOOGLE_API_KEY')
genai.configure(api_key=api_key)

# List available models
print("Available models:")
for m in genai.list_models():
    print(f"- {m.name}")

# Try to use the model
try:
    model = genai.GenerativeModel('gemini-flash')
    response = model.generate_content("Hello, what models are you?")
    print("\nResponse:", response.text)
except Exception as e:
    print("\nError:", str(e)) 