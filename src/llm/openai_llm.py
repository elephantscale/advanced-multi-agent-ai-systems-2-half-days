import os
from typing import Dict, Any, Optional
from datetime import datetime

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


class OpenAILLM:
    
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None, base_url: Optional[str] = None):
        if not OPENAI_AVAILABLE:
            raise ImportError("OpenAI package not installed. Run: pip install openai")
        
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        self.model = model or os.getenv('OPENAI_MODEL', 'gpt-4o-mini')
        self.base_url = base_url or os.getenv('OPENAI_BASE_URL')
        
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")
        
        client_kwargs = {'api_key': self.api_key}
        if self.base_url:
            client_kwargs['base_url'] = self.base_url
        
        self.client = OpenAI(**client_kwargs)
        self.call_count = 0
        self.total_tokens = 0
        self.total_cost = 0.0
        
        self.pricing = {
            'gpt-4o-mini': {'input': 0.00015 / 1000, 'output': 0.0006 / 1000},
            'gpt-4o': {'input': 0.0025 / 1000, 'output': 0.01 / 1000},
            'gpt-4-turbo': {'input': 0.01 / 1000, 'output': 0.03 / 1000},
            'gpt-3.5-turbo': {'input': 0.0005 / 1000, 'output': 0.0015 / 1000},
        }
    
    def generate(self, prompt: str, temperature: float = 0.7, max_tokens: int = 500) -> Dict[str, Any]:
        self.call_count += 1
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert AI assistant helping with incident management and log analysis."},
                    {"role": "user", "content": prompt}
                ],
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            response_text = response.choices[0].message.content
            
            prompt_tokens = response.usage.prompt_tokens if hasattr(response, 'usage') else len(prompt.split())
            completion_tokens = response.usage.completion_tokens if hasattr(response, 'usage') else len(response_text.split())
            total_tokens = prompt_tokens + completion_tokens
            
            cost = self._calculate_cost(prompt_tokens, completion_tokens)
            
            self.total_tokens += total_tokens
            self.total_cost += cost
            
            return {
                'response': response_text,
                'model': self.model,
                'tokens': total_tokens,
                'prompt_tokens': prompt_tokens,
                'completion_tokens': completion_tokens,
                'cost': cost,
                'timestamp': datetime.now().isoformat(),
                'call_number': self.call_count
            }
        
        except Exception as e:
            return {
                'response': f"Error calling OpenAI API: {str(e)}",
                'model': self.model,
                'tokens': 0,
                'cost': 0.0,
                'error': str(e),
                'timestamp': datetime.now().isoformat(),
                'call_number': self.call_count
            }
    
    def _calculate_cost(self, prompt_tokens: int, completion_tokens: int) -> float:
        model_key = self.model
        if model_key not in self.pricing:
            for key in self.pricing.keys():
                if key in model_key:
                    model_key = key
                    break
            else:
                model_key = 'gpt-4o-mini'
        
        pricing = self.pricing[model_key]
        cost = (prompt_tokens * pricing['input']) + (completion_tokens * pricing['output'])
        return cost
    
    def get_stats(self) -> Dict[str, Any]:
        return {
            'total_calls': self.call_count,
            'total_tokens': self.total_tokens,
            'total_cost': round(self.total_cost, 4),
            'model': self.model,
            'avg_tokens_per_call': round(self.total_tokens / self.call_count, 2) if self.call_count > 0 else 0,
            'avg_cost_per_call': round(self.total_cost / self.call_count, 4) if self.call_count > 0 else 0
        }
