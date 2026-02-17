import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Test Serper API configuration
SERP_API_KEY = os.getenv("SERP_API_KEY")

if not SERP_API_KEY:
    print("❌ SERP_API_KEY not found in environment variables")
    print("\nPlease:")
    print("1. Create a .env file in the project root")
    print("2. Add: SERP_API_KEY=your_api_key_here")
    print("3. Get your API key from https://serper.dev/")
else:
    print("✅ SERP_API_KEY is configured")
    print(f"   Key starts with: {SERP_API_KEY[:10]}...")
    
    # Test a simple search
    import requests
    
    print("\n🔍 Testing Serper API with a simple search...")
    try:
        url = "https://serper.dev/search"
        headers = {
            "X-API-KEY": SERP_API_KEY,
            "Content-Type": "application/json"
        }
        payload = {
            "q": "consulting firm",
            "num": 3
        }
        
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        organic_results = data.get("organic", [])
        
        print(f"✅ API is working! Found {len(organic_results)} results:")
        for i, result in enumerate(organic_results, 1):
            print(f"   {i}. {result.get('title', 'N/A')}")
            
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 401:
            print("❌ API key is invalid. Please check your key.")
        elif e.response.status_code == 429:
            print("❌ Rate limit exceeded. Check your Serper dashboard.")
        else:
            print(f"❌ HTTP Error: {e}")
    except Exception as e:
        print(f"❌ Error: {e}")
