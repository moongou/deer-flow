"""Comprehensive User Model Configuration API

Supports 18 predefined providers (Chinese + International + Local),
Ollama local model discovery, localhost:9999 service integration,
API key testing, and active model management.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import httpx
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

router = APIRouter(prefix="/api/user-models", tags=["User Model Configuration"])
USER_CONFIG_FILE = Path("user_models_config.json")
LOCAL_SERVICES_URL = "http://localhost:9999/api/projects"
OLLAMA_URL = "http://localhost:11434"

# ---------------------------------------------------------------------------
# Predefined provider catalogue
# ---------------------------------------------------------------------------
PREDEFINED_PROVIDERS: list[dict[str, Any]] = [
    # International
    {
        "id": "openai",
        "name": "OpenAI",
        "base_url": "https://api.openai.com/v1",
        "protocol": "openai",
        "group": "international",
        "icon": "\U0001f916",
        "description": "GPT-4o, o1, o3 \u65d7\u8230\u6a21\u578b",
        "default_models": ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "o1", "o3-mini"],
        "docs_url": "https://platform.openai.com/docs",
    },
    {
        "id": "anthropic",
        "name": "Anthropic",
        "base_url": "https://api.anthropic.com",
        "protocol": "anthropic",
        "group": "international",
        "icon": "\U0001f9e0",
        "description": "Claude 3.5 / 3.7 Sonnet, Opus \u7cfb\u5217",
        "default_models": ["claude-opus-4-5", "claude-3-7-sonnet-20250219", "claude-3-5-sonnet-20241022", "claude-3-5-haiku-20241022"],
        "docs_url": "https://docs.anthropic.com",
    },
    {
        "id": "google",
        "name": "Google Gemini",
        "base_url": "https://generativelanguage.googleapis.com/v1beta",
        "protocol": "gemini",
        "group": "international",
        "icon": "\U0001f52e",
        "description": "Gemini 2.5 Pro/Flash",
        "default_models": ["gemini-2.5-pro-preview-05-06", "gemini-2.0-flash", "gemini-2.0-flash-thinking-exp"],
        "docs_url": "https://ai.google.dev/docs",
    },
    {
        "id": "groq",
        "name": "Groq",
        "base_url": "https://api.groq.com/openai/v1",
        "protocol": "openai",
        "group": "international",
        "icon": "\u26a1",
        "description": "\u8d85\u5feb\u63a8\u7406\u52a0\u901f",
        "default_models": ["llama-3.3-70b-versatile", "llama-3.1-8b-instant", "mixtral-8x7b-32768"],
        "docs_url": "https://console.groq.com/docs",
    },
    {
        "id": "openrouter",
        "name": "OpenRouter",
        "base_url": "https://openrouter.ai/api/v1",
        "protocol": "openai",
        "group": "international",
        "icon": "\U0001f310",
        "description": "\u591a\u6a21\u578b\u805a\u5408\u8def\u7531 (200+ \u6a21\u578b)",
        "default_models": [],
        "docs_url": "https://openrouter.ai/docs",
    },
    {
        "id": "together",
        "name": "Together AI",
        "base_url": "https://api.together.xyz/v1",
        "protocol": "openai",
        "group": "international",
        "icon": "\U0001f91d",
        "description": "\u5f00\u6e90\u6a21\u578b\u9ad8\u6027\u80fd\u63a8\u7406",
        "default_models": ["meta-llama/Llama-3.3-70B-Instruct-Turbo", "deepseek-ai/DeepSeek-R1"],
        "docs_url": "https://docs.together.ai",
    },
    # Chinese
    {
        "id": "deepseek",
        "name": "DeepSeek \u6df1\u5ea6\u6c42\u7d22",
        "base_url": "https://api.deepseek.com/v1",
        "protocol": "openai",
        "group": "china",
        "icon": "\U0001f40b",
        "description": "DeepSeek-R1 / V3 \u63a8\u7406\u65d7\u8230",
        "default_models": ["deepseek-chat", "deepseek-reasoner"],
        "docs_url": "https://platform.deepseek.com/docs",
    },
    {
        "id": "qwen",
        "name": "\u901a\u4e49\u5343\u95ee (Alibaba)",
        "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
        "protocol": "openai",
        "group": "china",
        "icon": "\u2601\ufe0f",
        "description": "Qwen2.5-Max / QwQ-Plus \u63a8\u7406",
        "default_models": ["qwen-max", "qwen-plus", "qwq-plus", "qwen2.5-72b-instruct"],
        "docs_url": "https://help.aliyun.com/zh/dashscope",
    },
    {
        "id": "doubao",
        "name": "\u8c46\u5305 (ByteDance/\u706b\u5c71\u5f15\u64ce)",
        "base_url": "https://ark.cn-beijing.volces.com/api/v3",
        "protocol": "openai",
        "group": "china",
        "icon": "\U0001fad8",
        "description": "\u8c46\u5305 Pro / Lite \u7cfb\u5217",
        "default_models": [],
        "docs_url": "https://www.volcengine.com/docs/82379",
    },
    {
        "id": "kimi",
        "name": "Kimi / Moonshot AI",
        "base_url": "https://api.moonshot.cn/v1",
        "protocol": "openai",
        "group": "china",
        "icon": "\U0001f319",
        "description": "Moonshot \u8d85\u957f\u4e0a\u4e0b\u6587\u7cfb\u5217",
        "default_models": ["moonshot-v1-8k", "moonshot-v1-32k", "moonshot-v1-128k"],
        "docs_url": "https://platform.moonshot.cn/docs",
    },
    {
        "id": "zhipu",
        "name": "\u667a\u8c31 GLM",
        "base_url": "https://open.bigmodel.cn/api/paas/v4",
        "protocol": "openai",
        "group": "china",
        "icon": "\U0001f9ec",
        "description": "GLM-4-Plus / Flash, CogVideo \u7cfb\u5217",
        "default_models": ["glm-4-plus", "glm-4-flash", "glm-z1-plus"],
        "docs_url": "https://bigmodel.cn/dev/howuse/introduction",
    },
    {
        "id": "yi",
        "name": "\u96f6\u4e00\u4e07\u7269 (Yi)",
        "base_url": "https://api.lingyiwanwu.com/v1",
        "protocol": "openai",
        "group": "china",
        "icon": "\u2728",
        "description": "Yi-Lightning / Large \u7cfb\u5217",
        "default_models": ["yi-lightning", "yi-large", "yi-vision-plus"],
        "docs_url": "https://platform.lingyiwanwu.com/docs",
    },
    {
        "id": "minimax",
        "name": "MiniMax",
        "base_url": "https://api.minimax.chat/v1",
        "protocol": "openai",
        "group": "china",
        "icon": "\U0001f3af",
        "description": "abab \u7cfb\u5217\u591a\u6a21\u6001\u5927\u6a21\u578b",
        "default_models": ["abab6.5s-chat", "abab7-chat-preview"],
        "docs_url": "https://platform.minimaxi.com/document",
    },
    {
        "id": "stepfun",
        "name": "\u9636\u8dc3\u661f\u8fb0 (Stepfun)",
        "base_url": "https://api.stepfun.com/v1",
        "protocol": "openai",
        "group": "china",
        "icon": "\U0001fa90",
        "description": "Step-2 / Step-1 \u8d85\u957f\u4e0a\u4e0b\u6587",
        "default_models": ["step-2-16k", "step-1-200k"],
        "docs_url": "https://platform.stepfun.com/docs",
    },
    {
        "id": "baichuan",
        "name": "\u767e\u5ddd AI",
        "base_url": "https://api.baichuan-ai.com/v1",
        "protocol": "openai",
        "group": "china",
        "icon": "\U0001f30a",
        "description": "Baichuan4-Air / Turbo \u7cfb\u5217",
        "default_models": ["Baichuan4-Air", "Baichuan4-Turbo"],
        "docs_url": "https://platform.baichuan-ai.com/docs",
    },
    {
        "id": "hunyuan",
        "name": "\u6df7\u5143 (Tencent)",
        "base_url": "https://api.hunyuan.cloud.tencent.com/v1",
        "protocol": "openai",
        "group": "china",
        "icon": "\U0001f409",
        "description": "\u6df7\u5143 Turbo / Pro \u7cfb\u5217",
        "default_models": ["hunyuan-turbo", "hunyuan-pro", "hunyuan-standard"],
        "docs_url": "https://cloud.tencent.com/document/product/1729",
    },
    {
        "id": "302ai",
        "name": "302.AI \u805a\u5408\u5e73\u53f0",
        "base_url": "https://api.302.ai/v1",
        "protocol": "openai",
        "group": "china",
        "icon": "\U0001f517",
        "description": "\u56fd\u5185\u76f4\u8fde\u56fd\u9645\u6a21\u578b (GPT/Claude/Gemini \u5747\u53ef)",
        "default_models": [],
        "docs_url": "https://302.ai/docs",
    },
    # Local
    {
        "id": "ollama",
        "name": "Ollama (\u672c\u5730)",
        "base_url": "http://localhost:11434/v1",
        "protocol": "openai",
        "group": "local",
        "icon": "\U0001f999",
        "description": "\u672c\u5730\u8fd0\u884c Llama / Qwen / Mistral \u7b49\u5f00\u6e90\u6a21\u578b",
        "default_models": [],
        "docs_url": "https://ollama.com",
    },
    {
        "id": "ollama-remote",
        "name": "Ollama (\u8fdc\u7a0b)",
        "base_url": "",
        "protocol": "openai",
        "group": "ollama",
        "icon": "\u2601\ufe0f",
        "description": "\u8fde\u63a5\u8fdc\u7a0b Ollama \u670d\u52a1\uff0c\u9700\u8981 API Key \u6216\u81ea\u5b9a\u4e49\u5730\u5740",
        "default_models": [],
        "docs_url": "https://ollama.com",
    },
    {
        "id": "lmstudio",
        "name": "LM Studio / llama.cpp",
        "base_url": "http://localhost:1234/v1",
        "protocol": "openai",
        "group": "local",
        "icon": "\U0001f5a5\ufe0f",
        "description": "\u4efb\u4f55\u672c\u5730 OpenAI \u517c\u5bb9\u670d\u52a1",
        "default_models": [],
        "docs_url": "https://lmstudio.ai",
    },
]
PREDEFINED_MAP: dict[str, dict] = {p["id"]: p for p in PREDEFINED_PROVIDERS}


# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------


class ProviderOverride(BaseModel):
    api_key: str = ""
    base_url: str | None = None
    enabled: bool = False
    extra_models: list[str] = Field(default_factory=list)
    active_model: str | None = None


class CustomProvider(BaseModel):
    id: str
    name: str
    base_url: str
    protocol: str = "openai"
    group: str = "custom"
    icon: str = "\u2699\ufe0f"
    description: str = ""
    api_key: str = ""
    enabled: bool = False
    extra_models: list[str] = Field(default_factory=list)
    active_model: str | None = None


class UserConfig(BaseModel):
    provider_overrides: dict[str, ProviderOverride] = Field(default_factory=dict)
    custom_providers: dict[str, CustomProvider] = Field(default_factory=dict)
    active_provider: str | None = None
    active_model: str | None = None
    enabled_local_services: list[str] = Field(default_factory=list)


class SetAPIKeyRequest(BaseModel):
    provider_id: str
    api_key: str
    base_url: str | None = None


class TestConnectionRequest(BaseModel):
    provider_id: str
    api_key: str | None = None
    base_url: str | None = None


class SetActiveModelRequest(BaseModel):
    provider_id: str
    model_id: str


class AddCustomProviderRequest(BaseModel):
    id: str
    name: str
    base_url: str
    protocol: str = "openai"
    icon: str = "\u2699\ufe0f"
    description: str = ""


class ToggleLocalServiceRequest(BaseModel):
    service_id: str
    enabled: bool


# ---------------------------------------------------------------------------
# Config helpers
# ---------------------------------------------------------------------------


def _load() -> UserConfig:
    if USER_CONFIG_FILE.exists():
        try:
            return UserConfig.model_validate_json(USER_CONFIG_FILE.read_text())
        except Exception:
            pass
    return UserConfig()


def _save(cfg: UserConfig) -> None:
    USER_CONFIG_FILE.write_text(cfg.model_dump_json(indent=2))


def _merged_provider(provider_id: str, cfg: UserConfig) -> dict | None:
    if provider_id in PREDEFINED_MAP:
        base = dict(PREDEFINED_MAP[provider_id])
        override = cfg.provider_overrides.get(provider_id, ProviderOverride())
        base["has_key"] = bool(override.api_key)
        base["api_key"] = "***" if override.api_key else ""
        base["enabled"] = override.enabled
        base["base_url"] = override.base_url or base["base_url"]
        base["extra_models"] = override.extra_models
        base["active_model"] = override.active_model
        return base
    if provider_id in cfg.custom_providers:
        p = cfg.custom_providers[provider_id].model_dump()
        p["has_key"] = bool(p.get("api_key"))
        p["api_key"] = "***" if p["has_key"] else ""
        return p
    return None


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------


@router.get("/providers")
async def get_providers() -> list[dict]:
    """Return all providers with user overrides merged in."""
    cfg = _load()
    result = [_merged_provider(p["id"], cfg) for p in PREDEFINED_PROVIDERS]
    for custom in cfg.custom_providers.values():
        merged = _merged_provider(custom.id, cfg)
        if merged:
            result.append(merged)
    return result


@router.put("/providers/{provider_id}/apikey")
async def set_api_key(provider_id: str, req: SetAPIKeyRequest) -> dict:
    cfg = _load()
    override = cfg.provider_overrides.get(provider_id, ProviderOverride())
    override.api_key = req.api_key
    if req.base_url:
        override.base_url = req.base_url
    override.enabled = True
    cfg.provider_overrides[provider_id] = override
    _save(cfg)
    return {"status": "ok", "provider_id": provider_id}


@router.delete("/providers/{provider_id}/apikey")
async def remove_api_key(provider_id: str) -> dict:
    cfg = _load()
    if provider_id in cfg.provider_overrides:
        cfg.provider_overrides[provider_id].api_key = ""
        cfg.provider_overrides[provider_id].enabled = False
        _save(cfg)
    return {"status": "ok"}


@router.post("/providers/{provider_id}/test")
async def test_connection(provider_id: str, req: TestConnectionRequest) -> dict:
    """Test API key connectivity and return live model list if possible."""
    cfg = _load()
    api_key = req.api_key or cfg.provider_overrides.get(provider_id, ProviderOverride()).api_key
    if not api_key and provider_id not in ("ollama", "lmstudio"):
        return {"ok": False, "error": "No API key configured"}

    base = dict(PREDEFINED_MAP.get(provider_id, {}))
    override = cfg.provider_overrides.get(provider_id, ProviderOverride())
    base_url = req.base_url or override.base_url or base.get("base_url", "")
    protocol = base.get("protocol", "openai")

    try:
        async with httpx.AsyncClient(timeout=httpx.Timeout(12.0)) as client:
            if protocol == "anthropic":
                resp = await client.get(
                    "https://api.anthropic.com/v1/models",
                    headers={"x-api-key": api_key, "anthropic-version": "2023-06-01"},
                )
                if resp.status_code == 200:
                    return {"ok": True, "models": [m["id"] for m in resp.json().get("data", [])][:20]}
                return {"ok": False, "error": f"HTTP {resp.status_code}: {resp.text[:200]}"}

            elif protocol == "gemini":
                resp = await client.get(f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}")
                if resp.status_code == 200:
                    models = [m["name"].replace("models/", "") for m in resp.json().get("models", []) if "generateContent" in m.get("supportedGenerationMethods", [])]
                    return {"ok": True, "models": models[:20]}
                return {"ok": False, "error": f"HTTP {resp.status_code}: {resp.text[:200]}"}

            else:  # openai-compatible
                headers = {"Authorization": f"Bearer {api_key}"} if api_key else {}
                resp = await client.get(base_url.rstrip("/") + "/models", headers=headers)
                if resp.status_code == 200:
                    data = resp.json()
                    if "data" in data:
                        models = [m["id"] for m in data["data"]]
                    elif "models" in data:
                        models = [m if isinstance(m, str) else m.get("name", "") for m in data["models"]]
                    else:
                        models = []
                    return {"ok": True, "models": sorted(models)[:50]}
                return {"ok": False, "error": f"HTTP {resp.status_code}: {resp.text[:200]}"}
    except Exception as exc:
        return {"ok": False, "error": str(exc)}


@router.post("/providers/custom")
async def add_custom_provider(req: AddCustomProviderRequest) -> dict:
    cfg = _load()
    if req.id in PREDEFINED_MAP:
        raise HTTPException(400, "ID conflicts with a predefined provider")
    cfg.custom_providers[req.id] = CustomProvider(**req.model_dump())
    _save(cfg)
    return {"status": "ok", "provider_id": req.id}


@router.delete("/providers/{provider_id}")
async def delete_provider(provider_id: str) -> dict:
    cfg = _load()
    if provider_id in PREDEFINED_MAP:
        raise HTTPException(400, "Cannot delete predefined providers")
    cfg.custom_providers.pop(provider_id, None)
    _save(cfg)
    return {"status": "ok"}


# Ollama
@router.get("/ollama/models")
async def list_ollama_models() -> dict:
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(f"{OLLAMA_URL}/api/tags")
            if resp.status_code == 200:
                raw = resp.json().get("models", [])
                models = [
                    {
                        "name": m["name"],
                        "size_gb": round(m.get("size", 0) / 1e9, 1),
                        "modified_at": m.get("modified_at", ""),
                        "quantization": m.get("details", {}).get("quantization_level", ""),
                        "parameter_size": m.get("details", {}).get("parameter_size", ""),
                        "family": m.get("details", {}).get("family", ""),
                    }
                    for m in raw
                ]
                return {"ok": True, "running": True, "models": models}
            return {"ok": False, "running": False, "models": [], "error": f"HTTP {resp.status_code}"}
    except Exception as exc:
        return {"ok": False, "running": False, "models": [], "error": str(exc)}


# Active model
@router.get("/active")
async def get_active_model() -> dict:
    cfg = _load()
    return {"active_provider": cfg.active_provider, "active_model": cfg.active_model}


@router.post("/active")
async def set_active_model(req: SetActiveModelRequest) -> dict:
    cfg = _load()
    cfg.active_provider = req.provider_id
    cfg.active_model = req.model_id
    override = cfg.provider_overrides.get(req.provider_id, ProviderOverride())
    override.active_model = req.model_id
    if req.provider_id != "ollama" and req.model_id not in override.extra_models:
        override.extra_models.append(req.model_id)
    cfg.provider_overrides[req.provider_id] = override
    _save(cfg)
    return {"status": "ok", "active_provider": req.provider_id, "active_model": req.model_id}


# Local services
@router.get("/local-services")
async def get_local_services() -> dict:
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(LOCAL_SERVICES_URL)
            if resp.status_code != 200:
                return {"ok": False, "services": [], "error": f"HTTP {resp.status_code}"}
            services = resp.json()
            cfg = _load()
            return {"ok": True, "services": [{**svc, "user_enabled": svc["id"] in cfg.enabled_local_services} for svc in services]}
    except Exception as exc:
        return {"ok": False, "services": [], "error": str(exc)}


@router.post("/local-services/toggle")
async def toggle_local_service(req: ToggleLocalServiceRequest) -> dict:
    cfg = _load()
    if req.enabled:
        if req.service_id not in cfg.enabled_local_services:
            cfg.enabled_local_services.append(req.service_id)
    else:
        cfg.enabled_local_services = [s for s in cfg.enabled_local_services if s != req.service_id]
    _save(cfg)
    return {"status": "ok", "service_id": req.service_id, "enabled": req.enabled}


# ---------------------------------------------------------------------------
# Legacy compatibility
# ---------------------------------------------------------------------------


@router.get("/api-keys")
async def get_api_keys_legacy() -> dict:
    cfg = _load()
    return {pid: o.enabled for pid, o in cfg.provider_overrides.items() if o.api_key}


@router.post("/api-keys")
async def set_api_key_legacy(request: dict) -> dict:
    provider = request.get("provider", "")
    api_key = request.get("api_key", "")
    if not provider or not api_key:
        raise HTTPException(400, "provider and api_key required")
    cfg = _load()
    override = cfg.provider_overrides.get(provider, ProviderOverride())
    override.api_key = api_key
    override.enabled = True
    cfg.provider_overrides[provider] = override
    _save(cfg)
    return {"status": "success", "provider": provider}


@router.get("/models")
async def get_models_legacy() -> dict:
    cfg = _load()
    return {
        o.active_model: {
            "name": o.active_model,
            "display_name": o.active_model,
            "provider": pid,
            "model_id": o.active_model,
            "supports_thinking": False,
            "supports_vision": False,
            "enabled": True,
        }
        for pid, o in cfg.provider_overrides.items()
        if o.active_model
    }


@router.get("/status")
async def get_status() -> dict:
    cfg = _load()
    configured = [pid for pid, o in cfg.provider_overrides.items() if o.api_key and o.enabled]
    return {
        "api_keys_configured": configured,
        "models_count": sum(1 for o in cfg.provider_overrides.values() if o.active_model),
        "models": [o.active_model for o in cfg.provider_overrides.values() if o.active_model],
        "active_provider": cfg.active_provider,
        "active_model": cfg.active_model,
    }
