"""
OpenAI API client for agent reasoning.
"""
import logging
from typing import List, Dict, Any, Optional
from openai import OpenAI
from app.config import settings

logger = logging.getLogger(__name__)


class OpenAIClient:
    """Client for OpenAI API interactions."""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize OpenAI client.
        
        Args:
            api_key: OpenAI API key (defaults to settings)
        """
        self.api_key = api_key or settings.openai_api_key
        self.client = OpenAI(api_key=self.api_key)
        self.model = "gpt-4o-mini"  # Cost-effective model for reasoning
    
    def analyze_with_reasoning(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 1000
    ) -> str:
        """
        Send a prompt to OpenAI and get reasoning response.
        
        Args:
            system_prompt: System context for the AI
            user_prompt: User query/task
            temperature: Sampling temperature (0-1)
            max_tokens: Maximum response tokens
            
        Returns:
            AI response text
            
        Raises:
            Exception: If API call fails
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            content = response.choices[0].message.content
            logger.info(f"OpenAI reasoning completed: {len(content)} chars")
            return content
            
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            raise
    
    def multi_step_reasoning(
        self,
        steps: List[Dict[str, str]],
        temperature: float = 0.7
    ) -> List[str]:
        """
        Execute multi-step reasoning chain.
        
        Args:
            steps: List of dicts with 'system' and 'user' prompts
            temperature: Sampling temperature
            
        Returns:
            List of responses for each step
        """
        responses = []
        
        for i, step in enumerate(steps):
            logger.info(f"Executing reasoning step {i+1}/{len(steps)}")
            response = self.analyze_with_reasoning(
                system_prompt=step['system'],
                user_prompt=step['user'],
                temperature=temperature
            )
            responses.append(response)
        
        return responses
