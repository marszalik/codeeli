import os

import httpx

from app.domains.ai_settings import repository


PROVIDER_DEFAULTS = {
    "openai": "https://api.openai.com/v1",
    "litellm": "http://localhost:4000",
    "ollama": "http://localhost:11434",
}


def list_configs() -> list[dict]:
    return repository.list_configs()


def create_config(data: dict) -> None:
    provider = data["provider"]
    if not data.get("base_url"):
        data["base_url"] = PROVIDER_DEFAULTS[provider]
    repository.create_config(data)


def delete_config(config_id: int) -> None:
    repository.delete_config(config_id)


async def list_models(provider: str, base_url: str | None = None, api_key: str = "") -> list[str]:
    base = (base_url or PROVIDER_DEFAULTS.get(provider, "")).rstrip("/")
    headers = {}
    if provider == "openai":
        key = api_key or os.getenv("OPENAI_API_KEY", "")
        if key:
            headers["Authorization"] = f"Bearer {key}"
    elif provider == "litellm" and api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    async with httpx.AsyncClient(timeout=5) as client:
        if provider == "ollama":
            response = await client.get(f"{base}/api/tags")
            response.raise_for_status()
            payload = response.json()
            return [item["name"] for item in payload.get("models", []) if item.get("name")]

        response = await client.get(f"{base}/models", headers=headers)
        response.raise_for_status()
        payload = response.json()
        return [item["id"] for item in payload.get("data", []) if item.get("id")]
