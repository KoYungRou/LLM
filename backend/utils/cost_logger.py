import logging
import json
import os
from datetime import datetime
from typing import Dict, Any, Optional

# Setup logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CostLogger:
    """
    Utility to log and track LLM API usage costs.
    """
    
    def __init__(self):
        """Initialize the cost logger."""
        self.log_dir = os.getenv("COST_LOG_DIR", "./cost_logs")
        os.makedirs(self.log_dir, exist_ok=True)
        
        # Model pricing per 1K tokens (in USD)
        self.model_pricing = {
            "GPT-4o": {"input": 0.01, "output": 0.03},
            "Gemini-Flash": {"input": 0.0035, "output": 0.0035},
            "DeepSeek": {"input": 0.0009, "output": 0.0009},
            "Claude": {"input": 0.008, "output": 0.024},
            "Grok": {"input": 0.005, "output": 0.015}
        }
    
    def log_cost(self, model: str, token_usage: Dict[str, Any]) -> None:
        """
        Log the cost of an LLM API call.
        
        Args:
            model: The name of the LLM model
            token_usage: Dictionary containing input_tokens and output_tokens
        """
        try:
            # Extract token counts
            input_tokens = token_usage.get("input_tokens", 0)
            output_tokens = token_usage.get("output_tokens", 0)
            
            # Calculate costs
            pricing = self.model_pricing.get(model, {"input": 0.01, "output": 0.03})
            input_cost = (input_tokens / 1000) * pricing["input"]
            output_cost = (output_tokens / 1000) * pricing["output"]
            total_cost = input_cost + output_cost
            
            # Update token usage with cost information
            token_usage["input_cost"] = input_cost
            token_usage["output_cost"] = output_cost
            token_usage["cost"] = total_cost
            
            # Log to console
            logger.info(
                f"Model: {model}, Input tokens: {input_tokens}, "
                f"Output tokens: {output_tokens}, Cost: ${total_cost:.6f}"
            )
            
            # Log to file
            self._write_to_log(model, input_tokens, output_tokens, input_cost, output_cost, total_cost)
            
        except Exception as e:
            logger.error(f"Error logging cost: {str(e)}")
    
    def _write_to_log(
        self, 
        model: str, 
        input_tokens: int, 
        output_tokens: int, 
        input_cost: float, 
        output_cost: float, 
        total_cost: float
    ) -> None:
        """
        Write usage data to log file.
        
        Args:
            model: The name of the LLM model
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens
            input_cost: Cost of input tokens
            output_cost: Cost of output tokens
            total_cost: Total cost
        """
        try:
            # Get current date for log file name
            today = datetime.now().strftime("%Y-%m-%d")
            log_file = os.path.join(self.log_dir, f"cost_log_{today}.jsonl")
            
            # Create log entry
            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "model": model,
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "input_cost": input_cost,
                "output_cost": output_cost,
                "total_cost": total_cost
            }
            
            # Write to log file
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(log_entry) + "\n")
                
        except Exception as e:
            logger.error(f"Error writing to cost log: {str(e)}")
    
    def get_daily_summary(self, date: Optional[str] = None) -> Dict[str, Any]:
        """
        Get a summary of usage for a specific date.
        
        Args:
            date: Date string in format YYYY-MM-DD (defaults to today)
            
        Returns:
            Dictionary with usage summary
        """
        try:
            # Use provided date or default to today
            target_date = date or datetime.now().strftime("%Y-%m-%d")
            log_file = os.path.join(self.log_dir, f"cost_log_{target_date}.jsonl")
            
            # Check if log file exists
            if not os.path.exists(log_file):
                return {
                    "date": target_date,
                    "total_cost": 0,
                    "total_input_tokens": 0,
                    "total_output_tokens": 0,
                    "models": {}
                }
            
            # Initialize summary
            summary = {
                "date": target_date,
                "total_cost": 0,
                "total_input_tokens": 0,
                "total_output_tokens": 0,
                "models": {}
            }
            
            # Read log file
            with open(log_file, "r", encoding="utf-8") as f:
                for line in f:
                    if not line.strip():
                        continue
                    
                    # Parse log entry
                    entry = json.loads(line)
                    
                    # Update summary
                    summary["total_cost"] += entry["total_cost"]
                    summary["total_input_tokens"] += entry["input_tokens"]
                    summary["total_output_tokens"] += entry["output_tokens"]
                    
                    # Update model-specific data
                    model = entry["model"]
                    if model not in summary["models"]:
                        summary["models"][model] = {
                            "cost": 0,
                            "input_tokens": 0,
                            "output_tokens": 0,
                            "call_count": 0
                        }
                    
                    summary["models"][model]["cost"] += entry["total_cost"]
                    summary["models"][model]["input_tokens"] += entry["input_tokens"]
                    summary["models"][model]["output_tokens"] += entry["output_tokens"]
                    summary["models"][model]["call_count"] += 1
            
            return summary
            
        except Exception as e:
            logger.error(f"Error getting daily summary: {str(e)}")
            return {
                "date": target_date if 'target_date' in locals() else datetime.now().strftime("%Y-%m-%d"),
                "error": str(e)
            }