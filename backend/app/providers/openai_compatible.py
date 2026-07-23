import httpx
import logging
from typing import Optional
from app.providers.base import LLMProvider

logger = logging.getLogger(__name__)

class OpenAICompatibleProvider(LLMProvider):
    """
    OpenAI-compatible local API provider (LM Studio, vLLM, LocalAI, Ollama OpenAI endpoint).
    Standard POST /v1/chat/completions interaction.
    """

    def __init__(self, model_name: str = "local-model", api_base: str = "http://localhost:1234/v1", api_key: str = "lm-studio"):
        self.model_name = model_name
        self.api_base = api_base.rstrip("/")
        self.api_key = api_key

    async def generate(self, prompt: str, system: Optional[str] = None) -> str:
        # Standardize /v1/chat/completions endpoint
        if not self.api_base.endswith("/chat/completions"):
            url = f"{self.api_base}/chat/completions"
        else:
            url = self.api_base

        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": self.model_name,
            "messages": messages,
            "temperature": 0.2,
            "max_tokens": 4096
        }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        async with httpx.AsyncClient(timeout=120.0) as client:
            try:
                response = await client.post(url, json=payload, headers=headers)
                response.raise_for_status()
                data = response.json()
                choices = data.get("choices", [])
                if choices:
                    return choices[0].get("message", {}).get("content", "").strip()
                return ""
            except Exception as e:
                logger.error(f"OpenAICompatibleProvider failed: {e}")
                raise RuntimeError(f"OpenAI-compatible provider error ({self.model_name} at {self.api_base}): {str(e)}")

    async def test_connection(self) -> bool:
        if "/chat/completions" in self.api_base:
            base = self.api_base.replace("/chat/completions", "")
        else:
            base = self.api_base
        url = f"{base}/models"
        headers = {"Authorization": f"Bearer {self.api_key}"}
        async with httpx.AsyncClient(timeout=5.0) as client:
            try:
                res = await client.get(url, headers=headers)
                return res.status_code == 200
            except Exception:
                return False
