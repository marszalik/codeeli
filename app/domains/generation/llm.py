import json
import os
from collections.abc import AsyncIterator

import httpx


def _messages(prompt: str) -> list[dict]:
    return [
        {
            "role": "system",
            "content": "Jesteś precyzyjnym generatorem kodu. Odpowiadasz dokładnie w wymaganym formacie.",
        },
        {"role": "user", "content": prompt},
    ]


async def complete(config: dict, prompt: str) -> str:
    provider = config["provider"]
    base_url = config["base_url"].rstrip("/")
    model = config["model"]
    temperature = float(config.get("temperature") or 0)

    if provider == "ollama":
        return await _ollama_complete(base_url, model, prompt, temperature)
    return await _openai_compatible_complete(config, base_url, model, prompt, temperature)


async def stream_complete(config: dict, prompt: str) -> AsyncIterator[str]:
    provider = config["provider"]
    base_url = config["base_url"].rstrip("/")
    model = config["model"]
    temperature = float(config.get("temperature") or 0)

    if provider == "ollama":
        async for chunk in _ollama_stream(base_url, model, prompt, temperature):
            yield chunk
        return

    async for chunk in _openai_compatible_stream(config, base_url, model, prompt, temperature):
        yield chunk


async def _ollama_complete(base_url: str, model: str, prompt: str, temperature: float) -> str:
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": temperature, "num_predict": 12000},
    }
    async with httpx.AsyncClient(timeout=180) as client:
        response = await client.post(f"{base_url}/api/generate", json=payload)
        response.raise_for_status()
        return response.json().get("response", "").strip()


async def _openai_compatible_complete(config: dict, base_url: str, model: str, prompt: str, temperature: float) -> str:
    api_key = config.get("api_key") or os.getenv("OPENAI_API_KEY", "")
    headers = {}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    payload = {
        "model": model,
        "messages": _messages(prompt),
        "temperature": temperature,
        "stream": False,
    }
    async with httpx.AsyncClient(timeout=180) as client:
        response = await client.post(f"{base_url}/chat/completions", json=payload, headers=headers)
        response.raise_for_status()
        payload = response.json()
        return payload["choices"][0]["message"]["content"].strip()


async def _ollama_stream(base_url: str, model: str, prompt: str, temperature: float) -> AsyncIterator[str]:
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": True,
        "options": {"temperature": temperature, "num_predict": 12000},
    }
    async with httpx.AsyncClient(timeout=180) as client:
        async with client.stream("POST", f"{base_url}/api/generate", json=payload) as response:
            response.raise_for_status()
            async for line in response.aiter_lines():
                if not line:
                    continue
                data = json.loads(line)
                chunk = data.get("response", "")
                if chunk:
                    yield chunk


async def _openai_compatible_stream(
    config: dict,
    base_url: str,
    model: str,
    prompt: str,
    temperature: float,
) -> AsyncIterator[str]:
    api_key = config.get("api_key") or os.getenv("OPENAI_API_KEY", "")
    headers = {}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    payload = {
        "model": model,
        "messages": _messages(prompt),
        "temperature": temperature,
        "stream": True,
    }
    async with httpx.AsyncClient(timeout=180) as client:
        async with client.stream("POST", f"{base_url}/chat/completions", json=payload, headers=headers) as response:
            response.raise_for_status()
            async for line in response.aiter_lines():
                if not line or not line.startswith("data: "):
                    continue
                data = line[6:]
                if data == "[DONE]":
                    break
                payload = json.loads(data)
                choices = payload.get("choices", [])
                if not choices:
                    continue
                chunk = choices[0].get("delta", {}).get("content", "")
                if chunk:
                    yield chunk
