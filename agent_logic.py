import time
import random
import requests
from bs4 import BeautifulSoup
import pandas as pd
from urllib.parse import urlparse, urljoin
import os
from llm_utils import analyze_company_content, generate_linkedin_searches

# --- Constants ---
HIGH_INTENT_QUERIES = [
    '"strategy consulting" "implementation partner"',
    '"product consulting" "build partner"',
    '"consulting firm" "engineering partners"',
    '("strategy consulting" OR "implementation partner" OR "product consulting" OR "build partner" OR "consulting firm" OR "engineering partners") "United States" filetype:pdf "directory" OR "list" OR "partners"',
    '"digital consulting" "delivery partner"',
    '"digital transformation" "implementation partner"',
    '"transformation consulting" "execution partner"',
    '"consulting firm" "we partner with"',
    '"consulting services" "delivered by partners"',
    '"product studio" "development partner"',
    '"UX strategy" "implementation partner"',
    '"product discovery" "build partner"',
    '"innovation studio" "delivery partner"',
    '"design led consulting" "engineering partner"',
    '"white label" "software development"',
    '"extended delivery team" consulting',
    '"execution capacity" consulting firm',
    '"delivery augmentation" consulting',
    '"SaaS implementation partner" consulting',
    '"cloud transformation" "delivery partner"',
    '"AWS partner" "consulting firm"',
    '"scaling delivery" "consulting firm"',
    '"hiring engineers is hard" consulting',
    '"digital consulting firm" "United States"'
]

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

# --- Core Functions ---

def search_companies(query, max_results=10):
    """
    Searches for companies using Serper API.
    """
    print(f"Searching for: {query}".encode('utf-8', errors='replace').decode('utf-8'))
    
    SERP_API_KEY = os.getenv("SERP_API_KEY")
    if not SERP_API_KEY:
        print("Warning: SERP_API_KEY environment variable not set. Please set it to use Serper API.")
        return []
    
    results = []
    try:
        url = "https://serper.dev/search"
        headers = {
            "X-API-KEY": SERP_API_KEY,
            "Content-Type": "application/json"
        }
        payload = {
            "q": query,
            "num": max_results
        }
        
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        organic_results = data.get("organic", [])
        
        # Convert Serper format to match the expected format
        for item in organic_results:
            results.append({
                "title": item.get("title", "Unknown"),
                "href": item.get("link", ""),
                "body": item.get("snippet", "")
            })
            
    except Exception as e:
        print(f"Search error: {e}")
    
    # Add a small random delay to avoid hitting rate limits
    time.sleep(random.uniform(1, 2))
    return results

def get_page_content(url):
    """
    Fetches the content of a URL.
    """
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        return response.text
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None

def find_careers_page(soup, base_url):
    """
    Attempts to find the Careers page URL from the homepage soup.
    """
    for a in soup.find_all('a', href=True):
        text = a.get_text(strip=True).lower()
        if 'career' in text or 'job' in text or 'join us' in text or 'work with us' in text or 'hiring' in text:
             return urljoin(base_url, a['href'])
    return None

def analyze_text_for_keywords(text, positive_keywords, negative_keywords):
    """
    Checks for presence of positive and negative keywords in text.
    """
    text_lower = text.lower()
    positive_matches = [kw for kw in positive_keywords if kw.lower() in text_lower]
    negative_matches = [kw for kw in negative_keywords if kw.lower() in text_lower]
    return positive_matches, negative_matches

def validate_company(name, url):
    """
    Validates a company based on the strict checklist.
    """
    print(f"Validating: {name} ({url})".encode('utf-8', errors='replace').decode('utf-8'))
    
    if not url:
        return None

    homepage_content = get_page_content(url)
    if not homepage_content:
        return None

    soup = BeautifulSoup(homepage_content, 'html.parser')
    text_content = soup.get_text(separator=' ', strip=True)

    # 1. Partner/Ecosystem/Implementation check
    partner_keywords = ["partner", "ecosystem", "implementation", "alliance", "joint venture"]
    p_matches, _ = analyze_text_for_keywords(text_content, partner_keywords, [])
    
    # 2. Outcome vs Hiring language
    outcome_keywords = ["business outcome", "value", "transformation", "roi", "strategic", "roadmap", "advisory"]
    hiring_keywords = ["staff augmentation", "hiring engineers", "100+ engineers", "dedicated team", "outstaffing"]
    
    o_matches, h_matches = analyze_text_for_keywords(text_content, outcome_keywords, hiring_keywords)
    
    # Evidence snippet
    evidence = []
    if o_matches:
        evidence.append(f"Focus on: {', '.join(list(set(o_matches))[:3])}")
    if p_matches:
        evidence.append(f"Partnership keywords: {', '.join(list(set(p_matches))[:3])}")
    
    # 3. Careers Page Check
    careers_url = find_careers_page(soup, url)
    careers_status = "N/A"
    
    c_matches = []
    e_matches = []

    if careers_url:
        careers_content = get_page_content(careers_url)
        if careers_content:
            c_soup = BeautifulSoup(careers_content, 'html.parser')
            c_text = c_soup.get_text(separator=' ', strip=True).lower()
            
            consulting_roles = ["consultant", "strategist", "engagement manager", "client partner", "solution architect", "delivery lead"]
            engineering_roles = ["software engineer", "full stack developer", "backend developer", "frontend developer", "qa engineer"]
            
            c_matches, e_matches = analyze_text_for_keywords(c_text, consulting_roles, engineering_roles)
            
            # Heuristic: If engineering roles massively outnumber consulting roles AND they handle "hiring", it's likely a body shop.
            # However, many consulting firms DO hire engineers.
            # The prompt says: "❌ If they are hiring many engineers / developers → SKIP unless they clearly position themselves as consulting‑first."
            
            if len(e_matches) > len(c_matches) * 2 and "consulting" not in text_content.lower():
                 return None # Skip body shops
            
            if c_matches:
                 careers_status = f"Hiring: {', '.join(list(set(c_matches))[:3])}"
                 evidence.append(careers_status)
            else:
                 careers_status = "No explicit consulting roles found"

    # 4. LLM Analysis (if available)
    llm_analysis = None
    careers_text = None
    if careers_url and careers_content:
        careers_text = BeautifulSoup(careers_content, 'html.parser').get_text(separator=' ', strip=True)
    
    llm_analysis = analyze_company_content(name, url, text_content, careers_text)
    
    # Final Decision Logic - combine keyword-based and LLM analysis
    is_fit = False
    reasons = []
    confidence = "medium"

    # Keyword-based validation (baseline)
    if o_matches:
        is_fit = True
        reasons.append("Outcome-based language detected")
    
    if p_matches:
        is_fit = True
        reasons.append("Partner/Ecosystem language detected")

    if c_matches:
        is_fit = True
        reasons.append("Hiring consulting roles")
    
    if "consulting" in text_content.lower() or "strategy" in text_content.lower():
        is_fit = True
        reasons.append("Positions as consulting/strategy firm")
    
    # LLM-enhanced validation
    if llm_analysis:
        if llm_analysis.get("is_partner_ready"):
            is_fit = True
            confidence = llm_analysis.get("confidence", "medium")
            
            # Add LLM insights to reasons
            positioning = llm_analysis.get("positioning", "")
            if positioning and positioning not in ["unclear"]:
                reasons.append(f"LLM: {positioning} positioning")
            
            # Add key signals to evidence
            key_signals = llm_analysis.get("key_signals", [])
            if key_signals:
                evidence.append(f"Signals: {', '.join(key_signals[:3])}")
            
            # Note any red flags
            red_flags = llm_analysis.get("red_flags", [])
            if red_flags:
                evidence.append(f"⚠️ Risks: {', '.join(red_flags[:2])}")
        else:
            # LLM says not partner-ready, but if we have strong keyword signals, keep it with lower confidence
            if not is_fit:
                return None
            confidence = "low"
            llm_reasoning = llm_analysis.get("reasoning", "")
            if llm_reasoning:
                evidence.append(f"Note: {llm_reasoning}")

    if not is_fit:
        return None

    # Generate better LinkedIn search strings using LLM
    company_description = " | ".join(reasons[:2])  # Brief description for LLM
    linkedin_searches = generate_linkedin_searches(name, company_description, llm_analysis)
    
    # Format LinkedIn searches for display
    if isinstance(linkedin_searches, list) and len(linkedin_searches) > 0:
        linkedin_search = " | ".join(linkedin_searches[:3])
    else:
        linkedin_search = f'site:linkedin.com/in/ "{name}" ("Client Partner" OR "Managing Director" OR "Practice Lead")'
    
    return {
        "Company": name,
        "Website": url,
        "Why It Fits": "; ".join(reasons),
        "Evidence": " | ".join(evidence) if evidence else "Outcomes mentioned",
        "LinkedIn Search Strings": linkedin_search,
        "Confidence": confidence,
        "llm_analysis": llm_analysis  # Store for later use in summary
    }

def process_query(query, num_results=5):
    """
    Runs the full process for a single query.
    """
    raw_results = search_companies(query, max_results=num_results)
    validated_companies = []
    
    for r in raw_results:
        # DDG returns 'title', 'href', 'body'
        name = r.get('title', 'Unknown')
        url = r.get('href', '')
        
        # Basic filter to avoid garbage sites
        if "linkedin.com" in url or "clutch.co" in url or "upwork.com" in url:
            continue
            
        company_data = validate_company(name, url)
        if company_data:
            validated_companies.append(company_data)
            
    return validated_companies

def generate_summary(df):
    """
    Generates a summary of the top fits using LLM analysis.
    """
    if df.empty:
        return "No suitable companies found."
    
    # Import here to avoid circular dependency
    from llm_utils import summarize_companies
    
    # Convert DataFrame to list of dicts for LLM
    companies_data = df.to_dict('records')
    
    # Get LLM-powered summary
    llm_summary = summarize_companies(companies_data)
    
    if llm_summary and llm_summary != "No companies to summarize.":
        summary_lines = ["\n### Strategic Analysis\n", llm_summary, "\n"]
    else:
        summary_lines = ["\n### Top Strongest Fits\n"]
    
    # Add top 3 companies with details
    summary_lines.append("\n### Top 3 Companies\n")
    top_3 = df.head(3)
    
    for index, row in top_3.iterrows():
        summary_lines.append(f"**{row['Company']}** ({row.get('Confidence', 'medium')} confidence)")
        summary_lines.append(f"- *Why*: {row['Why It Fits']}")
        summary_lines.append(f"- *Evidence*: {row.get('Evidence', 'N/A')}")
        summary_lines.append("")
        
    return "\n".join(summary_lines)
