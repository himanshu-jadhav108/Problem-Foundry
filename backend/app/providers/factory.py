import logging
from typing import Optional
from app.providers.base import LLMProvider
from app.providers.ollama_provider import OllamaProvider
from app.providers.openai_compatible import OpenAICompatibleProvider

logger = logging.getLogger(__name__)

class ProviderFactory:
    """
    Singleton and Dynamic Factory for instantiating and switching local LLM providers.
    """
    _instance: Optional[LLMProvider] = None
    _provider_type: str = "ollama"
    _model_name: str = "qwen2.5-coder:7b"
    _api_base: str = "http://localhost:11434"
    _api_key: str = ""

    @classmethod
    def get_provider(cls) -> LLMProvider:
        if cls._instance is None:
            cls._instance = cls.create_provider(
                provider_type=cls._provider_type,
                model_name=cls._model_name,
                api_base=cls._api_base,
                api_key=cls._api_key
            )
        return cls._instance

    @classmethod
    def create_provider(cls, provider_type: str, model_name: str, api_base: str, api_key: str = "") -> LLMProvider:
        provider_type = provider_type.lower()
        if provider_type in ["ollama"]:
            return OllamaProvider(model_name=model_name, api_base=api_base)
        elif provider_type in ["openai_compatible", "lmstudio", "vllm", "openai"]:
            return OpenAICompatibleProvider(model_name=model_name, api_base=api_base, api_key=api_key)
        else:
            raise ValueError(f"Unsupported provider type: {provider_type}")

    @classmethod
    def switch_provider(cls, provider_type: str, model_name: str, api_base: str, api_key: str = "") -> LLMProvider:
        logger.info(f"Switching LLM provider to {provider_type} using model {model_name} at {api_base}")
        new_provider = cls.create_provider(provider_type, model_name, api_base, api_key)
        cls._provider_type = provider_type
        cls._model_name = model_name
        cls._api_base = api_base
        cls._api_key = api_key
        cls._instance = new_provider
        return new_provider

    @classmethod
    def get_active_config(cls) -> dict:
        return {
            "provider_type": cls._provider_type,
            "model_name": cls._model_name,
            "api_base": cls._api_base,
            "is_connected": cls._instance is not None
        }
