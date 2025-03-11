from fastapi import APIRouter, HTTPException, File, UploadFile
import os
import tempfile
from typing import Dict, Any
import pdfplumber
import logging

from utils.redis_stream import RedisStreamClient

# Setup logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configure router
router = APIRouter(tags=["PDF Management"])

# Define storage directory
PDF_STORAGE_DIR = os.getenv("PDF_STORAGE_DIR", "./pdf_storage")

# Ensure storage directory exists
os.makedirs(PDF_STORAGE_DIR, exist_ok=True)

# Initialize Redis client
redis_client = RedisStreamClient()

@router.post("/upload_pdf")
async def upload_pdf(file: UploadFile = File(...)) -> Dict[str, Any]:
    """
    Upload and process a PDF file (via direct multipart/form-data).

    Args:
        file (UploadFile): The uploaded PDF file.

    Returns:
        Dict[str, Any]: Processed PDF content, including markdown text.
    """
    try:
        file_name = file.filename  
        if not file_name:
            raise HTTPException(status_code=400, detail="Missing file_name")

        # Read PDF bytes
        pdf_bytes = await file.read()

        # Write to a temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
            temp_file.write(pdf_bytes)
            temp_file_path = temp_file.name

        try:
            # Extract text
            extracted_text = extract_text_from_pdf(temp_file_path)

            # Convert to markdown
            markdown_content = convert_to_markdown(extracted_text, file_name)

            # Save the markdown
            safe_file_name = os.path.splitext(file_name)[0]
            markdown_path = os.path.join(PDF_STORAGE_DIR, f"{safe_file_name}.md")
            with open(markdown_path, "w", encoding="utf-8") as md_file:
                md_file.write(markdown_content)

            # Log to Redis
            await redis_client.publish("pdf_events", {
                "action": "upload_pdf",
                "pdf_name": safe_file_name
            })

            return {
                "name": safe_file_name,
                "content": markdown_content,
                "pages": len(extracted_text),
            }
        finally:
            # Clean up temp file
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing PDF: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing PDF: {str(e)}")

def extract_text_from_pdf(file_path: str) -> list:
    """
    Extract text from each page of the PDF using pdfplumber.

    Args:
        file_path (str): Path to the PDF file

    Returns:
        List[str]: A list of strings, one for each page
    """
    try:
        pages_content = []
  
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text() or ""
                pages_content.append(text)
        return pages_content
    except Exception as e:
        logger.error(f"Error extracting text from PDF: {str(e)}")
        raise Exception(f"Error extracting text from PDF: {str(e)}")

def convert_to_markdown(pages: list, file_name: str) -> str:
    """
    Convert extracted text to markdown format.

    Args:
        pages: List of strings, one for each page
        file_name: Name of the PDF file

    Returns:
        Markdown-formatted string
    """
    try:
        markdown_content = f"# {os.path.splitext(file_name)[0]}\n\n"
        for i, page_text in enumerate(pages, start=1):
            markdown_content += f"## Page {i}\n\n"
            markdown_content += page_text.strip() + "\n\n"

        return markdown_content
    except Exception as e:
        logger.error(f"Error converting to markdown: {str(e)}")
        raise Exception(f"Error converting to markdown: {str(e)}")
