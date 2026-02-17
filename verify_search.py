from duckduckgo_search import DDGS

def test_search():
    print("Testing DuckDuckGo Search...")
    try:
        results = []
        with DDGS() as ddgs:
            # simple query
            gen = ddgs.text("test", max_results=3)
            for r in gen:
                results.append(r)
        
        if results:
            print("Successfully fetched search results.")
            for r in results:
                print(f"- {r.get('title')}")
        else:
            print("No results found, but no error raised.")
            
    except Exception as e:
        print(f"Search failed: {e}")

if __name__ == "__main__":
    test_search()
