# infrastructure/llm/provider_factory.py
"""
LLM Provider Factory - Creates LLM providers based on configuration.
"""
from typing import Optional, Dict, Any
import os

from core.interfaces.llm_provider import ILLMProvider
from infrastructure.llm.claude_provider import ClaudeProvider
from infrastructure.llm.openai_provider import OpenAIProvider
from infrastructure.llm.gemini_provider import GeminiProvider


class LLMProviderFactory:
    """Factory for creating LLM providers."""
    
    # Registry of available providers
    PROVIDERS = {
        "claude": ClaudeProvider,
        "openai": OpenAIProvider,
        "gemini": GeminiProvider,
    }
    
    # Default models for each provider
    DEFAULT_MODELS = {
        "claude": "claude-3-7-sonnet-20250219",
        "openai": "gpt-4o",
        "gemini": "gemini-2.0-flash-exp",
    }
    
    # Environment variable names for API keys
    API_KEY_ENV_VARS = {
        "claude": "ANTHROPIC_API_KEY",
        "openai": "OPENAI_API_KEY",
        "gemini": "GEMINI_API_KEY",
    }
    
    @classmethod
    def create_provider(
        cls,
        provider_name: str,
        model_id: Optional[str] = None,
        api_key: Optional[str] = None
    ) -> ILLMProvider:
        """
        Create LLM provider by name.
        
        Args:
            provider_name: Provider name ("claude", "openai", "gemini")
            model_id: Optional model ID (uses default if not provided)
            api_key: Optional API key (reads from env if not provided)
            
        Returns:
            Concrete LLM provider instance
            
        Raises:
            ValueError: If provider is unknown or API key is missing
        """
        provider_name = provider_name.lower()
        
        if provider_name not in cls.PROVIDERS:
            raise ValueError(
                f"Unknown provider: {provider_name}. "
                f"Available providers: {list(cls.PROVIDERS.keys())}"
            )
        
        # Get API key from parameter or environment
        if api_key is None:
            env_var = cls.API_KEY_ENV_VARS[provider_name]
            api_key = os.getenv(env_var)
            
            if not api_key:
                raise ValueError(
                    f"API key for {provider_name} not found. "
                    f"Please set {env_var} environment variable or pass api_key parameter."
                )
        
        # Get model ID (use default if not provided)
        if model_id is None:
            model_id = cls.DEFAULT_MODELS[provider_name]
        
        # Create provider instance
        provider_class = cls.PROVIDERS[provider_name]
        return provider_class(api_key=api_key, model_id=model_id)
    
    @classmethod
    def create_from_config(cls, config: Dict[str, Any]) -> ILLMProvider:
        """
        Create provider from configuration dictionary.
        
        Args:
            config: Configuration dict with keys:
                - provider: Provider name
                - model: Optional model ID
                - api_key: Optional API key
                
        Returns:
            Concrete LLM provider instance
        """
        return cls.create_provider(
            provider_name=config["provider"],
            model_id=config.get("model"),
            api_key=config.get("api_key")
        )
    
    @classmethod
    def list_providers(cls) -> Dict[str, str]:
        """List all available providers."""
        return {
            name: provider.__name__
            for name, provider in cls.PROVIDERS.items()
        }
    
    @classmethod
    def list_models(cls, provider_name: str) -> Dict[str, str]:
        """
        List available models for a provider.
        
        Args:
            provider_name: Provider name
            
        Returns:
            Dict of model_id -> model_name
        """
        provider_name = provider_name.lower()
        
        if provider_name not in cls.PROVIDERS:
            raise ValueError(f"Unknown provider: {provider_name}")
        
        provider_class = cls.PROVIDERS[provider_name]
        return provider_class.list_available_models()