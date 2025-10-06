import google.generativeai as genai
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Configure the API
api_key = os.getenv('GOOGLE_API_KEY')
print(f"API Key found: {'Yes' if api_key else 'No'}")

try:
    # Configure the library
    genai.configure(api_key=api_key)
    
    # List available models
    print("\nListing available models:")
    for m in genai.list_models():
        print(f"- {m.name}: {m.supported_generation_methods}")
    
    # Test a simple generation
    print("\nTesting simple generation:")
    model = genai.GenerativeModel('models/gemini-2.0-pro-exp')
    response = model.generate_content('Write a simple "Hello, World!" in SQL')
    print("\nModel Response:")
    print(response.text)
    
except Exception as e:
    print(f"\nError occurred: {str(e)}")