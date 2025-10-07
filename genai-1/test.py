import os
from groq import Groq
from dotenv import load_dotenv
import sys

# Load environment variables from .env file
load_dotenv()

# Get the API key
api_key = os.environ.get("GROQ_API_KEY")
print("Loaded API key:", api_key)
if not api_key:
    print("❌ GROQ_API_KEY not found in .env file. Please check your setup.")
    sys.exit(1)

print("✅ Groq API Key found.")

try:
    client = Groq(api_key=api_key)
    print("🚀 Requesting chat completion from Groq...")

    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": "Explain the importance of fast language models in 3 short points.",
            }
        ],
        model="llama-3.1-8b-instant",
    )

    print("\n✅ Success! Model Response:")
    print(chat_completion.choices[0].message.content)

except Exception as e:
    print(f"\n❌ An error occurred: {e}")