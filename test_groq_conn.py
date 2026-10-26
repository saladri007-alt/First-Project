"""Quick diagnostic script to verify Groq API connectivity."""

import os
from src.config import settings
from groq import Groq

print("Checking Groq Configuration:")
print(f"  has_groq_key: {settings.has_groq_key}")
print(f"  active_provider: {settings.active_llm_provider}")
print(f"  groq_model: {settings.GROQ_MODEL}")

if not settings.has_groq_key:
    print("\n[ERROR] GROQ_API_KEY is not set or empty in .env!")
    exit(1)

masked_key = (
    settings.GROQ_API_KEY[:6] + "..." + settings.GROQ_API_KEY[-4:]
    if len(settings.GROQ_API_KEY) > 10
    else "***"
)
print(f"  API Key detected: {masked_key}")
print(f"\nSending test ping to Groq API (Model: {settings.GROQ_MODEL})...")

try:
    client = Groq(api_key=settings.GROQ_API_KEY)
    response = client.chat.completions.create(
        model=settings.GROQ_MODEL,
        messages=[
            {
                "role": "system",
                "content": "You are a helpful assistant. Output valid JSON only.",
            },
            {
                "role": "user",
                "content": 'Return a JSON object with: {"status": "success", "message": "Groq connection operational"}',
            }
        ],
        response_format={"type": "json_object"},
        max_tokens=500,
        timeout=20.0,
    )
    print("\n[SUCCESS] Connected to Groq API successfully!")
    print("Response payload:")
    print(response.choices[0].message.content)

except Exception as e:
    print(f"\n[ERROR] Groq API call failed: {type(e).__name__}: {e}")
    # Also list available models from Groq to help debug if model name differs
    try:
        models = client.models.list()
        print("\nAvailable Groq models on your account:")
        for m in models.data[:10]:
            print(f" - {m.id}")
    except Exception as m_err:
        pass
