from abc import ABC, abstractmethod
import time
from typing import Dict, Any, List
from openai import OpenAI
from config import Config
from models import AgentResponse, TravelRequest

class BaseAgent(ABC):
    def __init__(self, name: str):
        self.name = name
        # Handle missing API key gracefully for demo purposes
        if Config.OPENAI_API_KEY and Config.OPENAI_API_KEY != "test_key_for_demo":
            self.client = OpenAI(api_key=Config.OPENAI_API_KEY)
        else:
            self.client = None
            print(f"Warning: {name} initialized without OpenAI API key - using mock responses")
    
    @abstractmethod
    async def process(self, request: TravelRequest, context: Dict[str, Any] = None) -> AgentResponse:
        """Process the travel request and return agent response"""
        pass
    
    def _create_agent_response(self, success: bool, data: Dict[str, Any], 
                             error_message: str = None, start_time: float = None) -> AgentResponse:
        """Create a standardized agent response"""
        processing_time = time.time() - start_time if start_time else 0.0
        
        return AgentResponse(
            agent_name=self.name,
            success=success,
            data=data,
            error_message=error_message,
            processing_time=processing_time
        )
    
    async def _call_openai(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Make a call to OpenAI API"""
        if not self.client:
            # Return mock response for demo purposes
            return self._get_mock_response()
        
        try:
            response = self.client.chat.completions.create(
                model=kwargs.get('model', Config.OPENAI_MODEL),
                messages=messages,
                max_tokens=kwargs.get('max_tokens', Config.MAX_TOKENS),
                temperature=kwargs.get('temperature', Config.TEMPERATURE)
            )
            return response.choices[0].message.content
        except Exception as e:
            raise Exception(f"OpenAI API error: {str(e)}")
    
    def _get_mock_response(self) -> str:
        """Return mock response for demo purposes"""
        return '{"message": "Mock response - OpenAI API key not configured"}'
    
    def _extract_json_from_response(self, response: str) -> Dict[str, Any]:
        """Extract JSON from OpenAI response"""
        import json
        import re
        
        # Try to find JSON in the response
        json_match = re.search(r'\{.*\}', response, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group())
            except json.JSONDecodeError:
                pass
        
        # If no JSON found, return the response as text
        return {"response": response}
