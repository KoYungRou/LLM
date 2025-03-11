import os
import json
import aiohttp
import logging
from typing import Dict, Any, Optional, List
import tiktoken

# Setup logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LiteLLMClient:
    """
    Client for interacting with various LLM providers through LiteLLM.
    """
    
    def __init__(self):
        """Initialize the LiteLLM client."""
        self.api_base_url = os.getenv("LITELLM_API_URL", "http://localhost:4000/v1")
        self.api_keys = {
            "openai": os.getenv("OPENAI_API_KEY", ""),
            "google": os.getenv("GOOGLE_API_KEY", ""),
            "anthropic": os.getenv("ANTHROPIC_API_KEY", ""),
            "deepseek": os.getenv("DEEPSEEK_API_KEY", ""),
            "xai": os.getenv("XAI_API_KEY", "")
        }
        
        # Model mapping to provider-specific model names
        self.model_mapping = {
            "GPT-4o": {"provider": "openai", "model": "gpt-4o"},
            "Gemini-Flash": {"provider": "google", "model": "gemini-1.5-flash"},
            "DeepSeek": {"provider": "deepseek", "model": "deepseek-coder"},
            "Claude": {"provider": "anthropic", "model": "claude-3-sonnet-20240229"},
            "Grok": {"provider": "xai", "model": "grok-1"}
        }
        
        # Initialize tokenizers for token counting fallback
        self.tokenizers = {}
        try:
            self.tokenizers["gpt"] = tiktoken.get_encoding("cl100k_base")
        except Exception:
            logger.warning("Could not load tiktoken for token counting")
    
    async def generate_response(
        self, 
        model: str, 
        prompt: str, 
        max_tokens: int = 1000,
        temperature: float = 0.7,
        system_message: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate a response from an LLM through LiteLLM.
        
        Args:
            model: The model name to use
            prompt: The user prompt
            max_tokens: Maximum tokens in the response
            temperature: Temperature setting for generation
            system_message: Optional system message
            
        Returns:
            Dictionary with generation result and token usage
        """
        try:
            # Map the model name to provider-specific model
            model_info = self.model_mapping.get(model)
            if not model_info:
                logger.warning(f"Unknown model: {model}, falling back to GPT-4o")
                model_info = self.model_mapping["GPT-4o"]
            
            provider = model_info["provider"]
            provider_model = model_info["model"]
            
            # Check for API key
            api_key = self.api_keys.get(provider)
            if not api_key:
                logger.warning(f"No API key found for {provider}, using empty key")
            
            # Construct messages
            messages = []
            if system_message:
                messages.append({"role": "system", "content": system_message})
            messages.append({"role": "user", "content": prompt})
            
            # Prepare the payload
            payload = {
                "model": provider_model,
                "messages": messages,
                "max_tokens": max_tokens,
                "temperature": temperature
            }
            
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}"
            }
            
            # Count input tokens for logging (fallback if API doesn't return this)
            input_tokens = self._count_tokens(prompt)
            
            # Make API request
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.api_base_url}/chat/completions", 
                    headers=headers,
                    json=payload,
                    timeout=60  # Longer timeout for LLM responses
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        logger.error(f"API error: {response.status}, {error_text}")
                        raise Exception(f"API error: {response.status}, {error_text}")
                    
                    result = await response.json()
            
            # Extract content and handle token usage
            content = result.get("choices", [{}])[0].get("message", {}).get("content", "")
            
            # Extract token usage from response or use fallback counting
            usage = result.get("usage", {})
            
            token_usage = {
                "input_tokens": usage.get("prompt_tokens", input_tokens),
                "output_tokens": usage.get("completion_tokens", self._count_tokens(content)),
                "total_tokens": usage.get("total_tokens", input_tokens + self._count_tokens(content))
            }
            
            # Log successful response
            logger.info(
                f"Generated response for model {model} "
                f"({token_usage['input_tokens']} input, {token_usage['output_tokens']} output tokens)"
            )
            
            return {
                "content": content,
                "token_usage": token_usage
            }
            
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            
            # Fallback to local token counting for error case
            return {
                "content": f"I apologize, but I encountered an error while processing your request: {str(e)}",
                "token_usage": {
                    "input_tokens": input_tokens if 'input_tokens' in locals() else self._count_tokens(prompt),
                    "output_tokens": 0,
                    "total_tokens": input_tokens if 'input_tokens' in locals() else self._count_tokens(prompt)
                }
            }
    
    def _count_tokens(self, text: str) -> int:
        """
        Count the number of tokens in a text.
        
        Args:
            text: Text to count tokens for
            
        Returns:
            Token count
        """
        try:
            if "gpt" in self.tokenizers:
                tokens = self.tokenizers["gpt"].encode(text)
                return len(tokens)
            else:
                # Very rough estimation if tokenizer not available
                return len(text.split())
        except Exception as e:
            logger.error(f"Error counting tokens: {str(e)}")
            # Fallback to word count
            return len(text.split())