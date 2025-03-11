from fastapi import APIRouter, HTTPException, Body
from typing import Dict, Any, Optional
from utils.redis_stream import RedisStreamClient
from utils.cost_logger import CostLogger
from llm_integration.lite_llm_client import LiteLLMClient
import logging

# Setup logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configure router
router = APIRouter(tags=["LLM Integration"])

# Initialize clients
redis_client = RedisStreamClient()
cost_logger = CostLogger()
llm_client = LiteLLMClient()

@router.post("/summarize")
async def summarize(
    payload: Dict[str, Any] = Body(
        ...,
        example={
            "model": "GPT-4o",
            "pdf_content": "# Example PDF\n\n## Page 1\n\nThis is sample content.",
            "pdf_name": "example.pdf",
            "selected_text": None
        }
    )
) -> Dict[str, Any]:
    """
    Generate a summary of PDF content using an LLM.
    
    Args:
        payload: Dict containing model, pdf_content, pdf_name, and selected_text
        
    Returns:
        Dict containing the summary and token usage information
    """
    try:
        # Extract parameters
        model = payload.get("model", "GPT-4o")
        pdf_content = payload.get("pdf_content")
        pdf_name = payload.get("pdf_name")
        selected_text = payload.get("selected_text")
        
        if not pdf_content and not pdf_name:
            raise HTTPException(status_code=400, detail="Missing PDF content or name")
        
        # Determine what content to summarize
        content_to_summarize = selected_text if selected_text else pdf_content
        
        # Create the prompt
        prompt = create_summary_prompt(content_to_summarize, pdf_name)
        
        # Call LLM to generate summary
        response = await llm_client.generate_response(
            model=model,
            prompt=prompt,
            max_tokens=1000
        )
        
        # Extract summary and token usage
        summary = response.get("content", "Failed to generate summary.")
        token_usage = response.get("token_usage", {})
        
        # Log usage to Redis
        await redis_client.publish("llm_usage", {
            "action": "summarize",
            "model": model,
            "pdf_name": pdf_name,
            "token_usage": token_usage
        })
        
        # Log cost
        cost_logger.log_cost(model, token_usage)
        
        return {
            "summary": summary,
            "token_usage": token_usage
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating summary: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error generating summary: {str(e)}")

def create_summary_prompt(content: str, document_name: Optional[str] = None) -> str:
    """
    Create a prompt for summarizing document content.
    
    Args:
        content: The content to summarize
        document_name: Optional name of the document
        
    Returns:
        Formatted prompt string
    """
    doc_context = f"document '{document_name}'" if document_name else "the provided document"
    
    prompt = f"""
    Please provide a comprehensive summary of {doc_context}. Focus on the key points, main ideas, 
    and important details. The summary should be well-structured and capture the essence of the content.
    
    Here is the content to summarize:
    
    {content}
    """
    
    return prompt.strip()