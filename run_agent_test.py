from agent_logic import search_companies, validate_company

# Test the updated validation logic with a real query
query = '"consulting firm" "we partner with"'
print(f"Testing query: {query}")
print("=" * 80)

# First, just get the raw search results
print("\n1. Fetching raw search results...")
raw_results = search_companies(query, max_results=5)

print(f"\nFound {len(raw_results)} raw search results:")
for i, r in enumerate(raw_results, 1):
    name = r.get('title', 'Unknown')
    url = r.get('href', '')
    print(f"{i}. {name}")
    print(f"   URL: {url}")

# Now validate each one
print("\n" + "=" * 80)
print("2. Validating each result...")
print("=" * 80)

validated = []
for r in raw_results:
    name = r.get('title', 'Unknown')
    url = r.get('href', '')
    
    # Skip garbage sites
    if "linkedin.com" in url or "clutch.co" in url or "upwork.com" in url:
        print(f"\nSkipping {name} (filtered domain)")
        continue
    
    print(f"\nValidating: {name}")
    result = validate_company(name, url)
    if result:
        validated.append(result)
        print(f"✓ PASSED - {result['Why It Fits']}")
    else:
        print(f"✗ FAILED validation")

print("\n" + "=" * 80)
print(f"Final result: {len(validated)} companies passed validation")
