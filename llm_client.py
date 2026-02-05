import os
from pathlib import Path
from groq import Groq
from dotenv import load_dotenv


def get_client():
    env_path = Path(__file__).parent / ".env"
    load_dotenv(dotenv_path=env_path, override=True)
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError(
            "Missing GROQ_API_KEY. Set it in your .env file or environment."
        )
    return Groq(api_key=api_key)


def generate_text(prompt, system_message=None, temperature=0.7, max_tokens=1500):
    client = get_client()
    
    messages = []
    if system_message:
        messages.append({"role": "system", "content": system_message})
    messages.append({"role": "user", "content": prompt})
    
    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant", 
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens
        )
        return response.choices[0].message.content
    
    except Exception as e:
        print(f"Groq API Error: {e}")
        raise


def generate_with_retry(prompt, system_message=None, temperature=0.7, max_tokens=1500, retries=2):
    last_error = None
    
    for attempt in range(retries + 1):
        try:
            return generate_text(prompt, system_message, temperature, max_tokens)
        except Exception as e:
            last_error = e
            if attempt < retries:
                print(f"Attempt {attempt + 1} failed, retrying...")
    
    raise last_error


def generate_creative(prompt, system_message=None):
    return generate_text(prompt, system_message, temperature=0.85, max_tokens=2000)


def generate_structured(prompt, system_message=None):
    return generate_text(prompt, system_message, temperature=0.4, max_tokens=1000)
