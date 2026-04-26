# utils.py
from typing import List
from pydantic import BaseModel, Field
from . import client, ml_model, ml_vectorizer
import json

def remove_json_titles(schema):
    if isinstance(schema, dict):
        return {k: remove_json_titles(v) for k, v in schema.items() if k != 'title'}
    elif isinstance(schema, list):
        return [remove_json_titles(i) for i in schema]
    return schema

CUAD_CATEGORIES = [
    "Document Name", "Parties", "Agreement Date", "Effective Date", "Expiration Date",
    "Renewal Term", "Notice to Terminate Renewal", "Governing Law", "Most Favored Nation",
    "Non-Compete", "Exclusivity", "No-Solicit of Customers", "Competitive Restriction Exception",
    "No-Solicit of Employees", "Non-Disparagement", "Termination for Convenience",
    "Right of First Refusal, Offer or Negotiation (ROFR/ROFO/ROFN)", "Change of Control",
    "Anti-Assignment", "Revenue/Profit Sharing", "Price Restriction", "Minimum Commitment",
    "Volume Restriction", "IP Ownership Assignment", "Joint IP Ownership", "License Grant",
    "Non-Transferable License", "Affiliate IP License-Licensor", "Affiliate IP License-Licensee",
    "Unlimited/All-You-Can-Eat License", "Irrevocable or Perpetual License", "Source Code Escrow",
    "Post-Termination Services", "Audit Rights", "Uncapped Liability", "Cap on Liability",
    "Liquidated Damages", "Warranty Duration", "Insurance", "Covenant Not to Sue",
    "Third Party Beneficiary"
]

class ClauseAnalysis(BaseModel):
    category: str = Field(..., description="CUAD category")
    clause_text: str = Field(..., description="Exact clause text")
    party_obligations: str = Field(..., description="Party1: ...; Party2: ...")
    risk_level: str = Field(..., description="low|medium|high|critical")
    risk_explanation: str = Field(..., description="Risk analysis")

# ====================== IMPROVED ML + GEMINI HYBRID (Now detects High/Critical Risk) ======================
def classify_clauses_ml(contract_text: str) -> List[ClauseAnalysis]:
    """Fast ML detection + Smart Gemini risk scoring"""
    if ml_model is None or ml_vectorizer is None:
        return classify_clauses(contract_text)

    # Step 1: ML quickly finds relevant clauses
    clauses = [c.strip() for c in contract_text.split('\n\n') if len(c.strip()) > 40]
    candidate_clauses = []

    for clause in clauses[:150]:
        if not clause:
            continue
        vec = ml_vectorizer.transform([clause])
        if ml_model.predict(vec)[0] == 1:
            candidate_clauses.append(clause)

    if not candidate_clauses:
        return []

    # Step 2: Send only candidates to Gemini for accurate category + REAL risk level
    prompt = f"""You are a senior corporate lawyer.
Analyze these extracted clauses from a contract.
Classify each into the correct CUAD category and assign risk_level:
- high or critical if the clause creates significant legal/financial exposure
- medium or low otherwise

Clauses:
{"\n\n---\n\n".join(candidate_clauses[:10])}

Return ONLY a JSON array of objects with this exact schema:
{{
  "category": "string",
  "clause_text": "string",
  "party_obligations": "Party1: ...; Party2: ...",
  "risk_level": "low|medium|high|critical",
  "risk_explanation": "string"
}}"""

    try:
        raw_schema = ClauseAnalysis.model_json_schema()
        schema = remove_json_titles(raw_schema)
        array_schema = {"type": "array", "items": schema}

        response = client.generate_content(
            prompt,
            generation_config={
                "response_mime_type": "application/json",
                "response_schema": array_schema
            }
        )
        data = json.loads(response.text)
        return [ClauseAnalysis(**item) for item in data]
    except Exception as e:
        print(f"Hybrid ML error: {e}")
        return []

# ====================== GEMINI FALLBACK (unchanged) ======================
def classify_clauses(contract_text: str) -> List[ClauseAnalysis]:
    prompt = f"""You are a senior corporate lawyer.
Extract all clauses that match these CUAD categories:

{', '.join(CUAD_CATEGORIES)}

Return a JSON array of objects. Each object must exactly follow this schema:
{{
  "category": "string",
  "clause_text": "string",
  "party_obligations": "Party1: ...; Party2: ...",
  "risk_level": "low|medium|high|critical",
  "risk_explanation": "string"
}}

Contract:
    {contract_text[:16000]}"""

    try:
        raw_schema = ClauseAnalysis.model_json_schema()
        schema = remove_json_titles(raw_schema)
        array_schema = {"type": "array", "items": schema}

        response = client.generate_content(
            prompt,
            generation_config={
                "response_mime_type": "application/json",
                "response_schema": array_schema
            }
        )
        data = json.loads(response.text)
        return [ClauseAnalysis(**item) for item in data]
    except Exception as e:
        print(f"Classification error: {e}")
        return []