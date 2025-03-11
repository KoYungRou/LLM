from fastapi import APIRouter, HTTPException, Query
import os
import json
from typing import Dict, Any
from utils.redis_stream import RedisStreamClient
import logging

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

# --- 移除或注释以下函数即可 ---
# @router.get("/list_pdfs")
# async def list_pdfs() -> Dict[str, List[str]]:
#     """
#     List all previously processed PDFs.
#     """
#     try:
#         # Check if the storage directory exists
#         if not os.path.exists(PDF_STORAGE_DIR):
#             return {"pdfs": []}
#         
#         # List all markdown files in the storage directory
#         pdf_files = [f for f in os.listdir(PDF_STORAGE_DIR) if f.endswith('.md')]
#         
#         # Remove the .md extension
#         pdf_names = [os.path.splitext(f)[0] for f in pdf_files]
#         
#         return {"pdfs": pdf_names}
#     except Exception as e:
#         logger.error(f"Error listing PDFs: {str(e)}")
#         raise HTTPException(status_code=500, detail=f"Error listing PDFs: {str(e)}")

@router.get("/select_pdfcontent")
async def select_pdfcontent(pdf_name: str = Query(..., description="Name of the PDF to select")) -> Dict[str, Any]:
    """
    Retrieve content of a previously processed PDF.
    
    Args:
        pdf_name: Name of the PDF to select
        
    Returns:
        Dict containing the PDF content
    """
    try:
        # Create the file path (adding .md extension)
        file_path = os.path.join(PDF_STORAGE_DIR, f"{pdf_name}.md")
        
        # Check if the file exists
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail=f"PDF '{pdf_name}' not found")
        
        # Read the file content
        with open(file_path, "r", encoding="utf-8") as file:
            content = file.read()
        
        # Log the action to Redis
        await redis_client.publish("pdf_events", {
            "action": "select_pdf",
            "pdf_name": pdf_name
        })
        
        return {"name": pdf_name, "content": content}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error selecting PDF: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error selecting PDF content: {str(e)}")
