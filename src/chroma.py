import chromadb
from chromadb.utils import embedding_functions
from chromadb.config import Settings
import os
from typing import Dict, Any, List
import uuid
import logging
import re
from dotenv import load_dotenv


load_dotenv()

logger = logging.getLogger(__name__)


chroma_client = chromadb.PersistentClient(
    path="./chroma_db",
    settings=Settings(allow_reset=True)
)

# 2. Use Google's embedding function (Keeps your stack FREE)
embedding_fn = embedding_functions.GoogleGenerativeAiEmbeddingFunction(
    api_key=os.getenv("GOOGLE_API_KEY")
)

collection = chroma_client.get_or_create_collection(
    name="contract_clauses",
    embedding_function=embedding_fn
)

def get_collection():
    """Get the main clauses collection."""
    return collection

def _smart_clause_split(text: str) -> List[str]:
    """
    Intelligent clause splitting: sections + paragraphs + sentences.
    """
    # Split by section headers (e.g., 1.2, ARTICLE X, Section 3.4)
    # Using single backslashes in raw strings for cleaner regex
    sections = re.split(r'(?i)(?:section|article|clause)\s*[A-Z\d]+[\.\s]', text, flags=re.M)
    
    # Fallback: paragraphs
    paragraphs = [p.strip() for p in re.split(r'\n{2,}', text) if len(p.strip()) > 50]
    
    # Sentences as last resort if text is very dense
    if len(paragraphs) < 3:
        sentences = re.split(r'(?<!mr|mrs|dr)\.(?=\s[A-Z])', text)
        paragraphs = [s.strip() for s in sentences if len(s.strip()) > 100]
    
    clauses = paragraphs[:200]  # Cap to avoid token/cost explosion
    logger.info(f"Split into {len(clauses)} clauses")
    return clauses

def add_contract_to_vector_db(
    contract_text: str, 
    contract_name: str, 
    metadata: Dict[str, Any]
) -> int:
    """
    Add contract clauses to vector DB with smart splitting and batching.
    """
    clauses = _smart_clause_split(contract_text)
    added_count = 0
    
    batch_docs = []
    batch_ids = []
    batch_metas = []
    
    for i, clause in enumerate(clauses):
        doc_id = f"{contract_name}_{uuid.uuid4().hex[:8]}_{i}"
        
        batch_docs.append(clause)
        batch_ids.append(doc_id)
        
        # Pydantic models should be converted to dicts; 
        # ChromaDB metadata supports strings, ints, floats, and bools.
        batch_metas.append({
            "contract": contract_name,
            "clause_id": i,
            "clause_order": i,
            **metadata
        })
        
        # Batching optimizes the upload to the database
        if len(batch_docs) >= 100 or i == len(clauses) - 1:
            try:
                collection.add(
                    documents=batch_docs,
                    ids=batch_ids,
                    metadatas=batch_metas
                )
                added_count += len(batch_docs)
                logger.info(f"Added batch of {len(batch_docs)} clauses")
                
                batch_docs, batch_ids, batch_metas = [], [], []
            except Exception as e:
                logger.error(f"Batch add failed: {e}")
    
    return added_count