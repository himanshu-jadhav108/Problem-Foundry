import httpx
import logging
from typing import Optional
from app.providers.base import LLMProvider

logger = logging.getLogger(__name__)

class OllamaProvider(LLMProvider):
    """
    Local Ollama API integration provider.
    Communicates via Ollama's HTTP REST API (default http://localhost:11434).
    """

    def __init__(self, model_name: str = "qwen2.5-coder:7b", api_base: str = "http://localhost:11434"):
        self.model_name = model_name
        self.api_base = api_base.rstrip("/")

    async def generate(self, prompt: str, system: Optional[str] = None) -> str:
        url = f"{self.api_base}/api/generate"
        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.2,
                "num_ctx": 8192
            }
        }
        if system:
            payload["system"] = system

        async with httpx.AsyncClient(timeout=120.0) as client:
            try:
                response = await client.post(url, json=payload)
                response.raise_for_status()
                data = response.json()
                return data.get("response", "").strip()
            except Exception as e:
                logger.error(f"OllamaProvider generation failed: {e}")
                raise RuntimeError(f"Ollama provider error ({self.model_name} at {self.api_base}): {str(e)}")

    async def test_connection(self) -> bool:
        url = f"{self.api_base}/api/tags"
        async with httpx.AsyncClient(timeout=5.0) as client:
            try:
                res = await client.get(url)
                return res.status_code == 200
            except Exception:
                return False
