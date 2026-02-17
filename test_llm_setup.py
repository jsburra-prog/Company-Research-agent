import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Test OpenRouter API configuration
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

if not OPENROUTER_API_KEY:
    print("❌ OPENROUTER_API_KEY not found in environment variables")
    print("\nPlease:")
    print("1. Create a .env file in the project root")
    print("2. Add: OPENROUTER_API_KEY=your_api_key_here")
    print("3. Get your API key from https://openrouter.ai/")
else:
    print("✅ OPENROUTER_API_KEY is configured")
    print(f"   Key starts with: {OPENROUTER_API_KEY[:15]}...")
    
    # Test a simple LLM call
    from llm_utils import call_llm
    
    print("\n🤖 Testing OpenRouter API with stepfun/step-3.5-flash:free...")
    try:
        response = call_llm(
            "Say 'Hello! LLM is working.' in one short sentence.",
            "You are a helpful assistant.",
            max_tokens=50
        )
        
        if response:
            print(f"✅ LLM API is working!")
            print(f"   Response: {response}")
        else:
            print("❌ LLM API returned no response. Check your API key and quota.")
            
    except Exception as e:
        print(f"❌ Error: {e}")
