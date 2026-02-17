from duckduckgo_search import DDGS
import time

# Test basic search functionality
queries = [
    "consulting firm",
    "digital transformation consulting"
]

for query in queries:
    print(f"\nTesting query: '{query}'")
    print("-" * 60)
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, region='wt-wt', safesearch='off', max_results=3))
            print(f"Found {len(results)} results")
            for i, r in enumerate(results, 1):
                print(f"{i}. {r.get('title', 'N/A')}")
                print(f"   {r.get('href', 'N/A')}")
    except Exception as e:
        print(f"Error: {e}")
    
    time.sleep(2)
