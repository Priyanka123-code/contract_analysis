📄 AI Contract Intelligence Dashboard
  1. Project OverviewContract review is traditionally a time-consuming task in legal and business operations.
  2.  This project leverages Large Language Models (LLMs) and Machine Learning to automatically analyze contracts,
  3. extract key terms, identify party obligations, flag risky clauses, and generate plain-English summaries.
2. Key FeaturesAutomated Metadata Extraction: Captures principal parties, effective/expiration dates, contract values, and governing law.
   Intelligent Clause Classification: Categorizes provisions against 41 professional CUAD categories using a hybrid Gemini and ML approach.
   Risk Assessment: Automatically flags unusual or risky clauses (e.g., unlimited liability, unilateral termination) and provides a weighted risk score (0-100).
   RAG-Powered Intelligence: Uses ChromaDB for Retrieval-Augmented Generation to allow for precise clause segmenting and identification.
   Hybrid Model Architecture: Combines a Trained ML Model (93% accuracy) with Gemini 3 Flash for high-precision extraction.
   Executive Dashboard: Provides a visual interface with risk gauges, metadata cards, and interactive data visualizations.
   
4. Tech Stack
    Language: Python 3.10+.
    LLM Engine: Google Gemini 3 Flash (2026 Edition).
    Vector Database: ChromaDB for clause indexing and RAG.
    Frontend: Streamlit with custom CSS and Plotly for visual intelligence.
    Extraction Libraries: pdfplumber and PyMuPDF (fitz) for robust PDF parsing.
    Environment Management: python-dotenv for secure API key handling.
   
5. System ArchitectureThe system follows a 7-phase implementation roadmap:
   Contract Upload: PDF ingestion via the Streamlit Control Center.
   Text Extraction: Multi-engine parsing to handle various PDF layouts.
   Metadata Extraction: AI-driven identification of core contract details.
   Segmentation & Classification: Dividing text into clauses and mapping them to CUAD standards.
   Risk Flagging: Pattern detection for high-impact liabilities.
   Executive Summary: Generating Grade-10 reading level plain-English summaries.
   Dashboard Visualization: Rendering results through an interactive risk gauge and provision inventory.

6. Expected Output
Users receive a comprehensive intelligence report including:

Extracted metadata table.

Interactive risk gauge score.

Detailed clause inventory categorized by CUAD standards.

Downloadable intelligence report in JSON format.
