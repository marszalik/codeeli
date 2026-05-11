# Codeeli

A small FastAPI + Mako + SQLite app for deterministic code generation with small local LLMs.

## What it solves

Small local models (Ollama, LiteLLM, modest OpenAI-compatible endpoints) are unreliable when asked to generate a whole project in one shot. Codeeli breaks that into a deterministic two-step workflow:

1. ask the model for a strict JSON file plan,
2. then for each planned file, stream its full contents.

Recipes nudge the model toward small, predictable outputs (single-file HTML pages, tiny Python CLIs, etc.), and instructions are editable prompt templates that drive both steps.

## Quick start

```bash
git clone <repo-url> app.codeeli
cd app.codeeli
python -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python scripts/dev.py
```

The dev server picks the first free port starting at 8000 and reloads on file changes.

## Production

Run `scripts/prod.py` behind your own reverse proxy. The entrypoint reads:

* `HOST` (default `127.0.0.1`)
* `PORT` (default `3004`)

## Architecture

The project is organized by domain, not by layer. Each domain owns its router, service, repository, schemas, views, and static assets. See [architecture.md](./architecture.md) for the full conventions.

### Domains

* `core` — shared framework code (config, Mako templates, base layout, navbar, shared static assets).
* `ai_settings` — CRUD for model configurations (OpenAI, LiteLLM, Ollama) and the model-list fetcher.
* `recipes` — short prompt fragments that nudge the model toward a particular output style and a default run command.
* `instructions` — editable prompt templates (`tasks`, `file`) used to drive the planning and per-file generation steps.
* `projects` — target programs: name, recipe, model configuration, workspace directory, and program description.
* `generation` — the streaming generator: plans files, streams each file's contents via SSE, persists runs, and exposes a launcher for the generated workspace.

## Environment variables

| Variable | Default | Used in |
| -------- | ------- | ------- |
| `HOST` | `127.0.0.1` | `scripts/prod.py` |
| `PORT` | `3004` | `scripts/prod.py` |
| `OPENAI_API_KEY` | unset | fallback for OpenAI-compatible providers |
