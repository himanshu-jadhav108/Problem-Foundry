from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from app.schemas.problem import ModelSwitchRequest
from app.providers.factory import ProviderFactory

router = APIRouter(prefix="/api/models", tags=["Models"])

@router.get("", response_model=Dict[str, Any])
async def get_active_model():
    """
    Returns active LLM provider configuration and connection health status.
    """
    config = ProviderFactory.get_active_config()
    provider = ProviderFactory.get_provider()
    is_alive = await provider.test_connection()
    config["is_connected"] = is_alive
    return config

@router.post("/switch", response_model=Dict[str, Any])
async def switch_model(req: ModelSwitchRequest):
    """
    Dynamically switches the active LLM provider at runtime (Ollama, LM Studio, vLLM, OpenAI-compatible).
    """
    try:
        new_provider = ProviderFactory.switch_provider(
            provider_type=req.provider_type,
            model_name=req.model_name,
            api_base=req.api_base,
            api_key=req.api_key or ""
        )
        is_alive = await new_provider.test_connection()
        return {
            "status": "success",
            "provider_type": req.provider_type,
            "model_name": req.model_name,
            "api_base": req.api_base,
            "is_connected": is_alive
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to switch provider: {str(e)}")
