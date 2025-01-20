#File: LLM/llm_settings_manager.py

import os
from typing import Optional, Dict, Any, Tuple
from dotenv import load_dotenv
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
import logging

# Cấu hình logging và environment
load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants
ENVIRONMENT = os.getenv("ENVIRONMENT", "PRODUCT")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL_DEFAULT = "gemini-1.5-pro"

# Model configurations
MODEL_SETTINGS = {
    "gemini-1.5-pro": {
        "model": "gemini-1.5-pro-002",
        "max_tokens": 8192,
        "temperature": 0.7,
        "candidate_count": 1,
    },
    "gemini-1.5-flash": {
        "model": "gemini-1.5-flash-002",
        "max_tokens": 4096,
        "temperature": 0.7,
        "candidate_count": 1,
    },
    "gemini-1.0-pro": {
        "model": "gemini-1.0-pro-002",
        "max_tokens": 2048,
        "temperature": 0.7,
        "candidate_count": 1,
    }
}

# Safety settings
SAFETY_SETTINGS = {
    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
}

class LLMSettings:
    def __init__(self) -> None:
        self.client: Optional[genai.GenerativeModel] = None
        self.current_model: str = GEMINI_MODEL_DEFAULT
        self._setup_client()

    def _setup_client(self) -> None:
        """Initialize the Gemini client with API key."""
        if not GEMINI_API_KEY:
            raise ValueError("Gemini API key not found in environment variables")
        
        genai.configure(api_key=GEMINI_API_KEY)
        model_name = MODEL_SETTINGS[self.current_model]["model"]
        self.client = genai.GenerativeModel(model_name)

    def _ensure_client(self) -> None:
        """Ensure client is initialized."""
        if self.client is None:
            self._setup_client()

    def _create_generation_config(self, model: str, max_tokens: Optional[int], temperature: Optional[float]) -> genai.types.GenerationConfig:
        """Create generation configuration for the model."""
        settings = MODEL_SETTINGS[model]
        return genai.types.GenerationConfig(
            temperature=temperature if temperature is not None else settings['temperature'],
            candidate_count=settings['candidate_count'],
            max_output_tokens=max_tokens or settings['max_tokens'],
        )

    def _process_response(self, response) -> Tuple[bool, str]:
        """Process and validate the response from Gemini."""
        if not response.candidates:
            return False, "No candidates generated"

        candidate = response.candidates[0]

        # Check for safety or recitation issues
        if hasattr(candidate, 'finish_reason'):
            if candidate.finish_reason == 'SAFETY':
                return False, "Content blocked by safety filter"
            if candidate.finish_reason == 'RECITATION':
                return False, "Content is a recitation"

        # Extract content
        if hasattr(candidate, 'content') and candidate.content and candidate.content.parts:
            return True, candidate.content.parts[0].text

        return False, "No content generated"

    def get_response(self, prompt: str, model: Optional[str] = None, 
                    max_tokens: Optional[int] = None, temperature: Optional[float] = None) -> str:
        """
        Get response from Gemini model.
        
        Args:
            prompt: Input text prompt
            model: Model name (optional)
            max_tokens: Maximum tokens for response (optional)
            temperature: Temperature for response generation (optional)
        
        Returns:
            Generated response text
        """
        try:
            self._ensure_client()
            model_name = model or self.current_model
            
            if model_name not in MODEL_SETTINGS:
                raise ValueError(f"Unsupported model: {model_name}")

            generation_config = self._create_generation_config(model_name, max_tokens, temperature)
            
            response = self.client.generate_content(
                prompt,
                generation_config=generation_config,
                safety_settings=SAFETY_SETTINGS
            )

            # Log any prompt feedback
            if hasattr(response, 'prompt_feedback') and response.prompt_feedback:
                logger.warning(f"Prompt feedback issues: {response.prompt_feedback}")

            success, result = self._process_response(response)
            if not success:
                error_msg = f"Gemini failed to respond. Error: {result}"
                logger.error(error_msg)
                return error_msg

            return result

        except Exception as e:
            error_msg = f"Error generating response: {str(e)}"
            logger.error(error_msg)
            return error_msg