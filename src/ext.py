# src/ext.py
import streamlit
import pdfplumber
import fitz  # PyMuPDF
from typing import Union, BinaryIO
import io
import logging

logger = logging.getLogger(__name__)

def extract_text_from_pdf(pdf_input: Union[str, bytes, BinaryIO, "streamlit.runtime.uploaded_file_manager.UploadedFile"]) -> str:
    """
    Robust PDF text extraction for both file paths AND Streamlit UploadedFile.
    """
    text = ""
    pdf_bytes = None

    # === Convert everything to bytes first (fixes Streamlit issue) ===
    if hasattr(pdf_input, "read"):          # Streamlit UploadedFile or file-like
        try:
            pdf_bytes = pdf_input.read()
            if hasattr(pdf_input, "seek"):
                pdf_input.seek(0)  # reset pointer for future reads
        except Exception as e:
            raise ValueError(f"Failed to read uploaded file: {e}")
    elif isinstance(pdf_input, str):        # file path
        with open(pdf_input, "rb") as f:
            pdf_bytes = f.read()
    elif isinstance(pdf_input, bytes):
        pdf_bytes = pdf_input
    else:
        raise ValueError(f"Unsupported input type: {type(pdf_input)}")

    if not pdf_bytes or len(pdf_bytes) < 100:
        raise ValueError("PDF appears empty or too small to be valid")

    # === Primary: pdfplumber (best layout/tables) ===
    try:
        with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
            for page in pdf.pages:
                extracted = page.extract_text(layout=True)
                if extracted:
                    text += extracted + "\n\n"
        logger.info(f"✅ pdfplumber extracted {len(text)} chars")
        if len(text.strip()) > 200:
            return text.strip()
    except Exception as e:
        logger.warning(f"pdfplumber failed: {e} — trying PyMuPDF fallback")

    # === Fallback: PyMuPDF ===
    try:
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        for page_num in range(len(doc)):
            text += doc[page_num].get_text("text") + "\n\n"
        doc.close()
        logger.info(f"✅ PyMuPDF fallback extracted {len(text)} chars")
    except Exception as e2:
        raise ValueError(f"Both PDF extractors failed. File is not a valid PDF. Error: {e2}")

    result = text.strip()
    if len(result) < 100:
        raise ValueError("Extracted text too short — probably not a valid contract PDF")

    return result