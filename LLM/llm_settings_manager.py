from llama_index.llms.gemini import Gemini
from llama_index.llms.deepseek import DeepSeek
from llama_index.llms.anthropic import Anthropic
import os
from dotenv import load_dotenv

load_dotenv()

class LLMSettingsManager:
    """Manages settings and initialization of different LLM models."""
    
    def __init__(self):
        self.api_keys = {
            "deepseek": os.getenv("DEEPSEEK_API_KEY"),
            "anthropic": os.getenv("ANTHROPIC_API_KEY"),
        }
        
        self.available_models = {
            "gemini": [
                "models/gemini-2.0-flash",
                "models/gemini-1.5-pro",
                "models/gemini-1.0-pro",
                "models/gemini-1.5-flash"
            ],
            "deepseek": [
                "deepseek-chat",
                "deepseek-coder",
                "deepseek-67b-chat"
            ],
            "anthropic": [
                "claude-3-5-sonnet-20241022",
                "claude-3-5-haiku-20241022",
                "claude-3-sonnet-20240229",
                "claude-3-haiku-20240307"
            ]
        }
        
    def get_available_models(self, provider: str = None):
        """
        Get the list of available models.
        
        Args:
            provider (str, optional): Specific provider name. If None, returns all.
            
        Returns:
            dict or list of available models
        """
        if provider:
            provider = provider.lower()
            if provider in self.available_models:
                return self.available_models[provider]
            raise ValueError(f"Invalid provider: {provider}")
        return self.available_models
    
    def get_llm(self, provider: str, **kwargs):
        """
        Initialize and return an LLM instance based on the chosen provider.
        
        Args:
            provider (str): LLM provider name ("gemini", "deepseek", "anthropic")
            **kwargs: Additional parameters for LLM initialization
            
        Returns:
            Corresponding LLM instance
        """
        provider = provider.lower()
        if provider not in self.available_models:
            raise ValueError(f"Invalid provider: {provider}")
            
        # Get default model (first one in the list)
        default_model = self.available_models[provider][0]
        model = kwargs.get("model", default_model)
        
        # Check if model is valid
        if model not in self.available_models[provider]:
            raise ValueError(f"Invalid model for {provider}: {model}")
            
        temperature = kwargs.get("temperature", 0.1)
            
        if provider == "gemini":
            return Gemini(model=model, temperature=temperature)
            
        elif provider == "deepseek":
            return DeepSeek(
                model=model,
                api_key=self.api_keys["deepseek"],
                temperature=temperature,
            )
            
        elif provider == "anthropic":
            return Anthropic(
                model=model,
                api_key=self.api_keys["anthropic"],
                temperature=temperature,
            )
    
    def get_default_llm(self):
        """Returns the default LLM instance (Anthropic Claude)"""
        return self.get_llm("anthropic")
