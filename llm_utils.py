"""
LLM utilities for enhanced company analysis using stepfun/step-3.5-flash:free via OpenRouter.
"""

import os
import json
from openai import OpenAI

# OpenRouter configuration
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
MODEL_NAME = "stepfun/step-3.5-flash:free"

def get_llm_client():
    """Get OpenAI-compatible client configured for OpenRouter."""
    if not OPENROUTER_API_KEY:
        return None
    
    return OpenAI(
        api_key=OPENROUTER_API_KEY,
        base_url=OPENROUTER_BASE_URL
    )

def call_llm(prompt, system_prompt="You are a helpful assistant.", max_tokens=1000):
    """
    Generic LLM call wrapper.
    
    Args:
        prompt: User prompt
        system_prompt: System instructions
        max_tokens: Maximum response length
        
    Returns:
        LLM response text or None if API unavailable
    """
    client = get_llm_client()
    if not client:
        print("Warning: OPENROUTER_API_KEY not set. Skipping LLM analysis.")
        return None
    
    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            max_tokens=max_tokens,
            temperature=0.3  # Lower temperature for more consistent analysis
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"LLM API error: {e}")
        return None

def analyze_company_content(company_name, url, text_content, careers_text=None):
    """
    Analyze company website content for partner readiness signals.
    
    Args:
        company_name: Company name
        url: Company website URL
        text_content: Scraped homepage text
        careers_text: Optional careers page text
        
    Returns:
        Dict with analysis results or None
    """
    system_prompt = """You are an expert at analyzing consulting firms and technology partners.
Your job is to assess whether a company is partner-ready for SaaS, Cloud, AI/ML, and digital transformation work.

Focus on:
1. Partner/ecosystem language and programs
2. Outcome-based vs staff augmentation positioning
3. Consulting/strategy capabilities vs pure engineering shops
4. Quality signals (case studies, thought leadership, client focus)
"""

    prompt = f"""Analyze this company for partner readiness:

Company: {company_name}
URL: {url}

Homepage Content:
{text_content[:3000]}  # Limit to avoid token limits

{"Careers Page Content:" if careers_text else ""}
{careers_text[:1500] if careers_text else ""}

Provide analysis in JSON format:
{{
    "is_partner_ready": true/false,
    "confidence": "high/medium/low",
    "key_signals": ["signal1", "signal2", ...],
    "red_flags": ["flag1", "flag2", ...],
    "positioning": "consulting-first/engineering-first/balanced/unclear",
    "partner_evidence": "brief description of partner/ecosystem mentions",
    "outcome_focus": "brief description of outcome vs staffing language",
    "reasoning": "1-2 sentence explanation of decision"
}}
"""

    response = call_llm(prompt, system_prompt, max_tokens=800)
    if not response:
        return None
    
    try:
        # Try to parse JSON response
        # Handle markdown code blocks if present
        if "```json" in response:
            response = response.split("```json")[1].split("```")[0].strip()
        elif "```" in response:
            response = response.split("```")[1].split("```")[0].strip()
        
        return json.loads(response)
    except json.JSONDecodeError:
        print(f"Failed to parse LLM response as JSON: {response[:200]}")
        return None

def generate_linkedin_searches(company_name, company_description, llm_analysis=None):
    """
    Generate targeted LinkedIn search strings for key decision-maker roles.
    
    Args:
        company_name: Company name
        company_description: Brief company description
        llm_analysis: Optional LLM analysis results
        
    Returns:
        List of LinkedIn search strings
    """
    system_prompt = """You are an expert at crafting LinkedIn search queries to find decision-makers at consulting and technology firms.
Generate precise search strings that will find Client Partners, Managing Directors, Practice Leads, and Delivery Leads."""

    context = f"Company: {company_name}\nDescription: {company_description}"
    if llm_analysis:
        context += f"\nPositioning: {llm_analysis.get('positioning', 'unknown')}"
    
    prompt = f"""{context}

Generate 3 LinkedIn search strings to find key decision-makers at this company.
Focus on roles like: Client Partner, Managing Director, Practice Lead, Delivery Lead, VP of Partnerships, Head of Alliances.

Return as JSON array:
["search string 1", "search string 2", "search string 3"]
"""

    response = call_llm(prompt, system_prompt, max_tokens=300)
    if not response:
        # Fallback to basic search
        return [
            f'site:linkedin.com/in/ "{company_name}" ("Client Partner" OR "Managing Director" OR "Practice Lead")',
            f'site:linkedin.com/in/ "{company_name}" ("VP Partnerships" OR "Head of Alliances" OR "Delivery Lead")',
            f'site:linkedin.com/in/ "{company_name}" ("Partner" OR "Director")'
        ]
    
    try:
        if "```json" in response:
            response = response.split("```json")[1].split("```")[0].strip()
        elif "```" in response:
            response = response.split("```")[1].split("```")[0].strip()
        
        searches = json.loads(response)
        return searches if isinstance(searches, list) else [response]
    except json.JSONDecodeError:
        # Return response as single search if not valid JSON
        return [response.strip()]

def summarize_companies(companies_data):
    """
    Generate strategic summary of validated companies with patterns and insights.
    
    Args:
        companies_data: List of validated company dicts
        
    Returns:
        Markdown-formatted summary
    """
    if not companies_data:
        return "No companies to summarize."
    
    system_prompt = """You are a strategic advisor analyzing potential technology partners.
Provide concise, actionable insights about the companies and identify patterns."""

    # Prepare company summaries for LLM
    company_summaries = []
    for c in companies_data[:10]:  # Limit to top 10 to avoid token limits
        summary = f"- {c['Company']}: {c.get('Why It Fits', 'N/A')}"
        if c.get('llm_analysis'):
            summary += f" | Positioning: {c['llm_analysis'].get('positioning', 'unknown')}"
        company_summaries.append(summary)
    
    prompt = f"""Analyze these {len(companies_data)} validated partner candidates:

{chr(10).join(company_summaries)}

Provide a brief strategic summary (3-4 sentences) covering:
1. Overall quality and fit of the cohort
2. Common patterns (positioning, capabilities, focus areas)
3. Top 2-3 strongest candidates and why
4. Any gaps or considerations

Keep it concise and actionable.
"""

    response = call_llm(prompt, system_prompt, max_tokens=500)
    if not response:
        # Fallback to basic summary
        return f"Found {len(companies_data)} validated companies. Review the table for details."
    
    return response
