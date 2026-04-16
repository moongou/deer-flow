"""Resolve user-configured models (from user_models_config.json) into ModelConfig objects.

This module is intentionally self-contained and does not import from the gateway
so it can be used directly by the LangGraph harness process.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

_USER_CONFIG_FILE = Path("user_models_config.json")

# Map provider id → (langchain class path, api_key_kwarg, default base_url)
# api_key_kwarg=None means no API key is required (local providers).
_PROVIDER_META: dict[str, tuple[str, str | None, str | None]] = {
    "openai": ("langchain_openai:ChatOpenAI", "openai_api_key", "https://api.openai.com/v1"),
    "anthropic": ("langchain_anthropic:ChatAnthropic", "anthropic_api_key", None),
    "google": ("langchain_google_genai:ChatGoogleGenerativeAI", "google_api_key", None),
    "groq": ("langchain_openai:ChatOpenAI", "openai_api_key", "https://api.groq.com/openai/v1"),
    "openrouter": ("langchain_openai:ChatOpenAI", "openai_api_key", "https://openrouter.ai/api/v1"),
    "together": ("langchain_openai:ChatOpenAI", "openai_api_key", "https://api.together.xyz/v1"),
    "deepseek": ("langchain_openai:ChatOpenAI", "openai_api_key", "https://api.deepseek.com/v1"),
    "qwen": ("langchain_openai:ChatOpenAI", "openai_api_key", "https://dashscope.aliyuncs.com/compatible-mode/v1"),
    "doubao": ("langchain_openai:ChatOpenAI", "openai_api_key", "https://ark.cn-beijing.volces.com/api/v3"),
    "kimi": ("langchain_openai:ChatOpenAI", "openai_api_key", "https://api.moonshot.cn/v1"),
    "zhipu": ("langchain_openai:ChatOpenAI", "openai_api_key", "https://open.bigmodel.cn/api/paas/v4"),
    "yi": ("langchain_openai:ChatOpenAI", "openai_api_key", "https://api.lingyiwanwu.com/v1"),
    "minimax": ("langchain_openai:ChatOpenAI", "openai_api_key", "https://api.minimax.chat/v1"),
    "stepfun": ("langchain_openai:ChatOpenAI", "openai_api_key", "https://api.stepfun.com/v1"),
    "baichuan": ("langchain_openai:ChatOpenAI", "openai_api_key", "https://api.baichuan-ai.com/v1"),
    "hunyuan": ("langchain_openai:ChatOpenAI", "openai_api_key", "https://api.hunyuan.cloud.tencent.com/v1"),
    "302ai": ("langchain_openai:ChatOpenAI", "openai_api_key", "https://api.302.ai/v1"),
    "ollama": ("langchain_openai:ChatOpenAI", None, "http://localhost:11434/v1"),
    "ollama-remote": ("langchain_openai:ChatOpenAI", "openai_api_key", None),
    "lmstudio": ("langchain_openai:ChatOpenAI", None, "http://localhost:1234/v1"),
}


def build_user_model_config(model_name: str) -> ModelConfig | None:  # noqa: F821  (ModelConfig imported below)
    """Return a ModelConfig for the given user-model name (format: ``user:{provider}/{model_id}``).

    Returns None if the model name is not a user model, user config is missing,
    or the active model in the config no longer matches.
    """
    from deerflow.config.model_config import ModelConfig  # avoid circular at module level

    if not model_name.startswith("user:"):
        return None

    rest = model_name[5:]
    slash = rest.find("/")
    if slash == -1:
        return None

    provider_id = rest[:slash]
    model_id = rest[slash + 1 :]

    if not _USER_CONFIG_FILE.exists():
        return None

    try:
        raw = json.loads(_USER_CONFIG_FILE.read_text())
    except Exception as exc:
        logger.debug("user_models_config.json read error: %s", exc)
        return None

    # Validate that this provider/model is still the active one
    if raw.get("active_provider") != provider_id or raw.get("active_model") != model_id:
        # Also allow if it's no longer "active" but was previously configured — just build from overrides
        overrides = raw.get("provider_overrides", {}).get(provider_id, {})
        if not overrides.get("api_key") and provider_id not in ("ollama", "lmstudio"):
            logger.debug("User model %s is not active/configured, skipping injection", model_name)
            return None
        # If there IS an api_key for this provider, allow it even if not the global active
        overrides_for_model = overrides
    else:
        overrides_for_model = raw.get("provider_overrides", {}).get(provider_id, {})

    api_key: str = overrides_for_model.get("api_key", "")
    base_url_override: str | None = overrides_for_model.get("base_url") or None

    # Check custom providers if not in predefined map
    meta = _PROVIDER_META.get(provider_id)
    if meta is None:
        custom = raw.get("custom_providers", {}).get(provider_id)
        if not custom:
            logger.debug("Unknown provider %s for user model injection", provider_id)
            return None
        use_class = "langchain_openai:ChatOpenAI"
        api_key_kwarg: str | None = "openai_api_key"
        default_base_url: str | None = custom.get("base_url")
        display_name = f"{custom.get('name', provider_id)}: {model_id}"
    else:
        use_class, api_key_kwarg, default_base_url = meta
        display_name = f"{provider_id}: {model_id}"

    base_url = base_url_override or default_base_url

    extra: dict = {}
    if base_url and "ChatOpenAI" in use_class:
        extra["base_url"] = base_url
    if api_key and api_key_kwarg:
        extra[api_key_kwarg] = api_key
    elif not api_key and "ChatOpenAI" in use_class and base_url:
        # Local models (Ollama, LM Studio) don't need an API key but ChatOpenAI requires one
        extra["openai_api_key"] = "not-needed"

    try:
        return ModelConfig(
            name=model_name,
            display_name=display_name,
            use=use_class,
            model=model_id,
            **extra,
        )
    except Exception as exc:
        logger.warning("Failed to build ModelConfig for %s: %s", model_name, exc)
        return None
