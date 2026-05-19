import os
import google.generativeai as genai
from dotenv import load_dotenv

def test_vertex_ai():
    load_dotenv(override=True)
    api_key = os.getenv("GOOGLE_API_KEY")
    
    print(f"--- VERTEX AI MANUAL TEST ---")
    print(f"Key detected: {'Yes' if api_key else 'No'}")
    if api_key:
        print(f"Prefix: {api_key[:8]}...")
    
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-pro')
        
        print("Sending test prompt to Gemini Pro...")
        response = model.generate_content("Hello! This is a manual check for an autonomous urban crisis system. Can you give me a 1-sentence tactical update on why AI is critical for crisis management?")
        
        print(f"\nAPI RESPONSE SUCCESS:")
        print(f"Content: {response.text.strip()}")
        print("-" * 30)
        return True
    except Exception as e:
        print(f"\nAPI TEST FAILED:")
        print(f"Error: {str(e)}")
        print("-" * 30)
        return False

if __name__ == "__main__":
    test_vertex_ai()
