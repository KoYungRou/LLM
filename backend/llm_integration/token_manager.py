import logging
from typing import Dict, Any
import os
import json
from datetime import datetime

# Setup logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TokenManager:
    """
    Manages token usage and cost calculations for LLM API calls.
    """
    
    def __init__(self, model_pricing: Dict[str, Dict[str, float]] = None):
        """
        Initialize the token manager.
        
        Args:
            model_pricing: Dictionary mapping model names to pricing info
        """
        # Default pricing per 1K tokens if not provided
        self.model_pricing = model_pricing or {
            "GPT-4o": {"input": 0.01, "output": 0.03},
            "Gemini-Flash": {"input": 0.0035, "output": 0.0035},
            "DeepSeek": {"input": 0.0009, "output": 0.0009},
            "Claude": {"input": 0.008, "output": 0.024},
            "Grok": {"input": 0.005, "output": 0.015}
        }
        
        # Directory for usage logs
        self.log_dir = os.getenv("TOKEN_LOG_DIR", "./token_logs")
        os.makedirs(self.log_dir, exist_ok=True)
    
    def calculate_cost(self, model: str, input_tokens: int, output_tokens: int) -> Dict[str, Any]:
        """
        Calculate the cost of an API call.
        
        Args:
            model: The model name
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens
            
        Returns:
            Dictionary with cost information
        """
        try:
            # Get pricing for the model
            pricing = self.model_pricing.get(model, {"input": 0.01, "output": 0.03})
            
            # Calculate costs
            input_cost = (input_tokens / 1000) * pricing["input"]
            output_cost = (output_tokens / 1000) * pricing["output"]
            total_cost = input_cost + output_cost
            
            return {
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "total_tokens": input_tokens + output_tokens,
                "input_cost": input_cost,
                "output_cost": output_cost,
                "cost": total_cost
            }
        except Exception as e:
            logger.error(f"Error calculating cost: {str(e)}")
            return {
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "total_tokens": input_tokens + output_tokens,
                "input_cost": 0,
                "output_cost": 0,
                "cost": 0,
                "error": str(e)
            }
    
    def log_usage(
        self, 
        model: str, 
        operation: str, 
        input_tokens: int, 
        output_tokens: int, 
        metadata: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Log token usage and cost information.
        
        Args:
            model: The model name
            operation: The operation type (e.g., summarize, ask_question)
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens
            metadata: Additional metadata to log
            
        Returns:
            Dictionary with cost information
        """
        try:
            # Calculate cost
            cost_info = self.calculate_cost(model, input_tokens, output_tokens)
            
            # Create log entry
            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "model": model,
                "operation": operation,
                **cost_info
            }
            
            # Add metadata if provided
            if metadata:
                log_entry["metadata"] = metadata
            
            # Get current date for log file name
            today = datetime.now().strftime("%Y-%m-%d")
            log_file = os.path.join(self.log_dir, f"token_log_{today}.jsonl")
            
            # Write to log file
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(log_entry) + "\n")
            
            # Log to console
            logger.info(
                f"Model: {model}, Operation: {operation}, "
                f"Input tokens: {input_tokens}, Output tokens: {output_tokens}, "
                f"Cost: ${cost_info['cost']:.6f}"
            )
            
            return cost_info
            
        except Exception as e:
            logger.error(f"Error logging usage: {str(e)}")
            return {
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "total_tokens": input_tokens + output_tokens,
                "cost": 0,
                "error": str(e)
            }
    
    def get_usage_summary(self, date: str = None) -> Dict[str, Any]:
        """
        Get a summary of token usage for a specific date.
        
        Args:
            date: Date string in format YYYY-MM-DD (defaults to today)
            
        Returns:
            Dictionary with usage summary
        """
        try:
            # Use provided date or default to today
            target_date = date or datetime.now().strftime("%Y-%m-%d")
            log_file = os.path.join(self.log_dir, f"token_log_{target_date}.jsonl")
            
            # Check if log file exists
            if not os.path.exists(log_file):
                return {
                    "date": target_date,
                    "total_cost": 0,
                    "total_tokens": 0,
                    "models": {}
                }
            
            # Initialize summary
            summary = {
                "date": target_date,
                "total_cost": 0,
                "total_tokens": 0,
                "models": {}
            }
            
            # Read log file
            with open(log_file, "r", encoding="utf-8") as f:
                for line in f:
                    if not line.strip():
                        continue
                    
                    entry = json.loads(line)
                    
                    # Update summary
                    summary["total_cost"] += entry.get("cost", 0)
                    summary["total_tokens"] += entry.get("total_tokens", 0)
                    
                    # Update model-specific data
                    model = entry.get("model", "unknown")
                    if model not in summary["models"]:
                        summary["models"][model] = {
                            "cost": 0,
                            "input_tokens": 0,
                            "output_tokens": 0,
                            "operations": {}
                        }
                    
                    model_summary = summary["models"][model]
                    model_summary["cost"] += entry.get("cost", 0)
                    model_summary["input_tokens"] += entry.get("input_tokens", 0)
                    model_summary["output_tokens"] += entry.get("output_tokens", 0)
                    
                    # Update operation-specific data
                    operation = entry.get("operation", "unknown")
                    if operation not in model_summary["operations"]:
                        model_summary["operations"][operation] = {
                            "count": 0,
                            "cost": 0,
                            "tokens": 0
                        }
                    
                    op_summary = model_summary["operations"][operation]
                    op_summary["count"] += 1
                    op_summary["cost"] += entry.get("cost", 0)
                    op_summary["tokens"] += entry.get("total_tokens", 0)
            
            return summary
        
        except Exception as e:
            logger.error(f"Error getting usage summary: {str(e)}")
            return {
                "date": target_date if 'target_date' in locals() else datetime.now().strftime("%Y-%m-%d"),
                "error": str(e)
            }