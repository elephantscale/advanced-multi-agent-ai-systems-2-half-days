import os
from typing import Union
from dotenv import load_dotenv

from .mock_llm import MockLLM
from .openai_llm import OpenAILLM


def get_llm(force_mock: bool = False, deterministic: bool = True, verbose: bool = True) -> Union[MockLLM, OpenAILLM]:
    load_dotenv()
    
    api_key = os.getenv('OPENAI_API_KEY')
    
    if force_mock or not api_key:
        if verbose:
            if force_mock:
                print("🤖 Running with MockLLM (forced)")
            else:
                print("🤖 Running with MockLLM (no API key found)")
            print(f"   Mode: {'Deterministic' if deterministic else 'Probabilistic'}")
        return MockLLM(deterministic=deterministic)
    
    else:
        try:
            model = os.getenv('OPENAI_MODEL', 'gpt-4o-mini')
            base_url = os.getenv('OPENAI_BASE_URL')
            
            if verbose:
                print(f"🚀 Running with OpenAI LLM")
                print(f"   Model: {model}")
                if base_url:
                    print(f"   Base URL: {base_url}")
            
            return OpenAILLM(api_key=api_key, model=model, base_url=base_url)
        
        except Exception as e:
            if verbose:
                print(f"⚠️  Failed to initialize OpenAI LLM: {e}")
                print("🤖 Falling back to MockLLM")
            return MockLLM(deterministic=deterministic)


def print_llm_stats(llm: Union[MockLLM, OpenAILLM]) -> None:
    stats = llm.get_stats()
    
    print("\n" + "="*50)
    print("📊 LLM Usage Statistics")
    print("="*50)
    print(f"Model: {stats['model']}")
    print(f"Total Calls: {stats['total_calls']}")
    print(f"Total Tokens: {stats['total_tokens']}")
    print(f"Total Cost: ${stats['total_cost']:.4f}")
    
    if 'avg_tokens_per_call' in stats:
        print(f"Avg Tokens/Call: {stats['avg_tokens_per_call']}")
        print(f"Avg Cost/Call: ${stats['avg_cost_per_call']:.4f}")
    
    if 'mode' in stats:
        print(f"Mode: {stats['mode']}")
    
    print("="*50 + "\n")
