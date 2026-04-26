# pre.py
from pydantic import BaseModel, Field
from . import client
import json

def remove_json_titles(schema):
    """Recursively removes 'title' field for Gemini compatibility."""
    if isinstance(schema, dict):
        return {k: remove_json_titles(v) for k, v in schema.items() if k != 'title'}
    elif isinstance(schema, list):
        return [remove_json_titles(i) for i in schema]
    return schema

class ContractMetadata(BaseModel):
    party_1: str = Field(..., description="First main party name")
    party_2: str = Field(..., description="Second main party name")
    effective_date: str = Field(..., description="Effective date in YYYY-MM-DD or 'not specified'")
    expiration_date: str = Field(..., description="Expiration date or 'Perpetual' or 'not specified'")
    contract_value: str = Field(..., description="Total contract value if mentioned")
    governing_law: str = Field(..., description="Governing law jurisdiction")
    notice_period: str = Field(..., description="Notice period for termination")

def extract_contract_metadata(contract_text: str) -> ContractMetadata:
    prompt = f"""You are an expert contract lawyer.
Extract the following metadata from the contract.
Use "not specified" if information is missing.
Return ONLY valid JSON.

Contract text:
{contract_text[:14000]}"""

    try:
        raw_schema = ContractMetadata.model_json_schema()
        schema = remove_json_titles(raw_schema)

        response = client.generate_content(
            prompt,
            generation_config={
                "response_mime_type": "application/json",
                "response_schema": schema
            }
        )
        data = json.loads(response.text)
        return ContractMetadata(**data)
    except Exception as e:
        raise ValueError(f"Metadata extraction failed: {e}")