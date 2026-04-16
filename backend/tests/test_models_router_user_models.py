import asyncio
import json
from types import SimpleNamespace
from unittest.mock import patch

from app.gateway.routers import models as models_router


def test_list_models_includes_all_frontend_activated_user_models(
    tmp_path,
    monkeypatch,
):
    config_file = tmp_path / "user_models_config.json"
    config_file.write_text(
        json.dumps(
            {
                "active_provider": "ollama-remote",
                "active_model": "deepseek-v3.2",
                "provider_overrides": {
                    "ollama-remote": {
                        "active_model": "deepseek-v3.2",
                        "extra_models": ["deepseek-v3.2"],
                    },
                    "openai": {
                        "active_model": "gpt-4.1-mini",
                        "extra_models": ["gpt-4.1-mini"],
                    },
                },
            }
        )
    )

    monkeypatch.setattr(models_router, "_USER_CONFIG_FILE", config_file)

    builtin_model = SimpleNamespace(
        name="builtin-model",
        model="builtin-model",
        display_name="Built-in Model",
        description="Built-in description",
        supports_thinking=False,
        supports_reasoning_effort=False,
    )
    app_config = SimpleNamespace(
        models=[builtin_model],
        token_usage=SimpleNamespace(enabled=False),
    )

    with patch("app.gateway.routers.models.get_app_config", return_value=app_config):
        result = asyncio.run(models_router.list_models())

    assert [model.name for model in result.models] == [
        "user:ollama-remote/deepseek-v3.2",
        "user:openai/gpt-4.1-mini",
        "builtin-model",
    ]
    assert result.models[0].description == "已激活到前端，可在模型选择器中使用"