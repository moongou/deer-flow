import json
import logging
from pathlib import Path

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from deerflow.config import get_app_config

logger = logging.getLogger(__name__)

_USER_CONFIG_FILE = Path("user_models_config.json")

# Minimal provider display info keyed by provider id
_PROVIDER_NAMES: dict[str, str] = {
    "openai": "OpenAI",
    "anthropic": "Anthropic",
    "google": "Google Gemini",
    "groq": "Groq",
    "openrouter": "OpenRouter",
    "together": "Together AI",
    "deepseek": "DeepSeek",
    "qwen": "通义千问",
    "doubao": "豆包",
    "kimi": "Kimi/Moonshot",
    "zhipu": "智谱 GLM",
    "yi": "零一万物",
    "minimax": "MiniMax",
    "stepfun": "阶跃星辰",
    "baichuan": "百川 AI",
    "hunyuan": "混元",
    "302ai": "302.AI",
    "ollama": "Ollama",
    "ollama-remote": "Ollama Remote",
    "lmstudio": "LM Studio",
}


def _get_user_active_model_responses() -> list["ModelResponse"]:
    """Return all user-activated models that should appear in the frontend selector."""
    if not _USER_CONFIG_FILE.exists():
        return []
    try:
        cfg = json.loads(_USER_CONFIG_FILE.read_text())
        seen: set[str] = set()
        responses: list[ModelResponse] = []

        def append_model(provider_id: str | None, model_id: str | None) -> None:
            if not provider_id or not model_id:
                return
            name = f"user:{provider_id}/{model_id}"
            if name in seen:
                return
            seen.add(name)
            provider_name = _PROVIDER_NAMES.get(provider_id, provider_id)
            responses.append(
                ModelResponse(
                    name=name,
                    model=model_id,
                    display_name=f"{provider_name}: {model_id}",
                    description="已激活到前端，可在模型选择器中使用",
                )
            )

        active_provider = cfg.get("active_provider")
        active_model = cfg.get("active_model")

        append_model(active_provider, active_model)

        for provider_id, override in cfg.get("provider_overrides", {}).items():
            append_model(provider_id, override.get("active_model"))

        return responses
    except Exception as exc:
        logger.debug("Could not load user active models: %s", exc)
        return []


router = APIRouter(prefix="/api", tags=["models"])


class ModelResponse(BaseModel):
    """Response model for model information."""

    name: str = Field(..., description="Unique identifier for the model")
    model: str = Field(..., description="Actual provider model identifier")
    display_name: str | None = Field(None, description="Human-readable name")
    description: str | None = Field(None, description="Model description")
    supports_thinking: bool = Field(default=False, description="Whether model supports thinking mode")
    supports_reasoning_effort: bool = Field(default=False, description="Whether model supports reasoning effort")


class TokenUsageResponse(BaseModel):
    """Token usage display configuration."""

    enabled: bool = Field(default=False, description="Whether token usage display is enabled")


class ModelsListResponse(BaseModel):
    """Response model for listing all models."""

    models: list[ModelResponse]
    token_usage: TokenUsageResponse


@router.get(
    "/models",
    response_model=ModelsListResponse,
    summary="List All Models",
    description="Retrieve a list of all available AI models configured in the system.",
)
async def list_models() -> ModelsListResponse:
    """List all available models from configuration.

    Returns model information suitable for frontend display,
    excluding sensitive fields like API keys and internal configuration.

    Returns:
        A list of all configured models with their metadata and token usage display settings.

    Example Response:
        ```json
        {
            "models": [
                {
                    "name": "gpt-4",
                    "model": "gpt-4",
                    "display_name": "GPT-4",
                    "description": "OpenAI GPT-4 model",
                    "supports_thinking": false,
                    "supports_reasoning_effort": false
                },
                {
                    "name": "claude-3-opus",
                    "model": "claude-3-opus",
                    "display_name": "Claude 3 Opus",
                    "description": "Anthropic Claude 3 Opus model",
                    "supports_thinking": true,
                    "supports_reasoning_effort": false
                }
            ],
            "token_usage": {
                "enabled": true
            }
        }
        ```
    """
    config = get_app_config()
    models = [
        ModelResponse(
            name=model.name,
            model=model.model,
            display_name=model.display_name,
            description=model.description,
            supports_thinking=model.supports_thinking,
            supports_reasoning_effort=model.supports_reasoning_effort,
        )
        for model in config.models
    ]

    # Prepend user-activated models so they are immediately selectable in the frontend.
    for user_model in reversed(_get_user_active_model_responses()):
        if not any(m.name == user_model.name for m in models):
            models.insert(0, user_model)

    return ModelsListResponse(
        models=models,
        token_usage=TokenUsageResponse(enabled=config.token_usage.enabled),
    )


@router.get(
    "/models/{model_name}",
    response_model=ModelResponse,
    summary="Get Model Details",
    description="Retrieve detailed information about a specific AI model by its name.",
)
async def get_model(model_name: str) -> ModelResponse:
    """Get a specific model by name.

    Args:
        model_name: The unique name of the model to retrieve.

    Returns:
        Model information if found.

    Raises:
        HTTPException: 404 if model not found.

    Example Response:
        ```json
        {
            "name": "gpt-4",
            "display_name": "GPT-4",
            "description": "OpenAI GPT-4 model",
            "supports_thinking": false
        }
        ```
    """
    config = get_app_config()
    model = config.get_model_config(model_name)
    if model is None:
        raise HTTPException(status_code=404, detail=f"Model '{model_name}' not found")

    return ModelResponse(
        name=model.name,
        model=model.model,
        display_name=model.display_name,
        description=model.description,
        supports_thinking=model.supports_thinking,
        supports_reasoning_effort=model.supports_reasoning_effort,
    )
