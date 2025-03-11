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

@router.post("/ask_question")
async def ask_question(
    payload: Dict[str, Any] = Body(
        ...,
        example={
            "model": "GPT-4o",
            "question": "What is the main topic of this document?",
            "pdf_content": "# Example PDF\n\n## Page 1\n\nThis is sample content.",
            "pdf_name": "example.pdf",
            "selected_text": None
        }
    )
) -> Dict[str, Any]:
    """
    Answer a question about PDF content using an LLM.
    
    Args:
        payload: Dict containing model, question, pdf_content, pdf_name, and selected_text
        
    Returns:
        Dict containing the answer and token usage information
    """
    try:
        # Extract parameters
        model = payload.get("model", "GPT-4o")
        question = payload.get("question")
        pdf_content = payload.get("pdf_content")
        pdf_name = payload.get("pdf_name")
        selected_text = payload.get("selected_text")
        
        if not question:
            raise HTTPException(status_code=400, detail="Missing question")
        if not pdf_content and not pdf_name:
            raise HTTPException(status_code=400, detail="Missing PDF content or name")
        
        # Determine what content to search
        context = selected_text if selected_text else pdf_content
        
        # Create the prompt
        prompt = create_qa_prompt(question, context, pdf_name)
        
        # Call LLM to generate answer
        response = await llm_client.generate_response(
            model=model,
            prompt=prompt,
            max_tokens=1000
        )
        
        # Extract answer and token usage
        answer = response.get("content", "Failed to generate an answer.")
        token_usage = response.get("token_usage", {})
        
        # Log usage to Redis
        await redis_client.publish("llm_usage", {
            "action": "ask_question",
            "model": model,
            "pdf_name": pdf_name,
            "question": question,
            "token_usage": token_usage
        })
        
        # Log cost
        cost_logger.log_cost(model, token_usage)
        
        return {
            "answer": answer,
            "token_usage": token_usage
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error answering question: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error answering question: {str(e)}")

def create_qa_prompt(question: str, context: str, document_name: Optional[str] = None) -> str:
    """
    Create a prompt for answering a question about document content.
    
    Args:
        question: The question to answer
        context: The context to search for answers
        document_name: Optional name of the document
        
    Returns:
        Formatted prompt string
    """
    doc_context = f"document '{document_name}'" if document_name else "the provided document"
    
    prompt = f"""
    Please answer the following question about {doc_context}. Base your answer only on the 
    information provided in the context. If the answer cannot be found in the context, please 
    state that clearly.
    
    Context:
    {context}
    
    Question:
    {question}
    """
    
    return prompt.strip()