import asyncio
import html
import json
import shlex
import sys
from collections.abc import AsyncIterator
from pathlib import Path

from app.domains.generation import llm, repository
from app.domains.instructions.service import fill_placeholders, get_instruction_content
from app.domains.projects.service import get_project_details


class GenerationError(Exception):
    pass


def safe_project_path(workspace_dir: str, filename: str) -> Path:
    root = Path(workspace_dir).expanduser().resolve()
    target = (root / filename).resolve()
    if root not in target.parents and target != root:
        raise GenerationError(f"Niebezpieczna ścieżka pliku: {filename}")
    return target


def extract_json_array(raw: str) -> str:
    text = strip_code_fence(raw)
    start = text.find("[")
    end = text.rfind("]")
    if start == -1 or end == -1 or end < start:
        return text
    return text[start : end + 1]


def parse_tasks(raw: str) -> list[dict]:
    text = extract_json_array(raw)
    payload = json.loads(text, strict=False)
    if not isinstance(payload, list) or not payload:
        raise ValueError("Odpowiedź musi być niepustą tablicą JSON.")
    tasks = []
    for item in payload:
        if not isinstance(item, dict):
            raise ValueError("Każdy task musi być obiektem.")
        name = str(item.get("name", "")).strip()
        description = str(item.get("task_description", "")).strip()
        filename = str(item.get("filename", "")).strip()
        if not name or not description or not filename:
            raise ValueError("Task wymaga pól name, task_description, filename.")
        tasks.append({"name": name, "task_description": description, "filename": filename})
    return tasks


def wants_separate_files(program_prompt: str) -> bool:
    text = program_prompt.lower()
    markers = ["osobn", "oddziel", "separate", "wiele plik", "kilka plik", "style.css", "script.js"]
    return any(marker in text for marker in markers)


def normalize_tasks(program_prompt: str, recipe: str, tasks: list[dict]) -> list[dict]:
    recipe_text = recipe.lower()
    html_filenames = {task["filename"].lower() for task in tasks}
    recipe_prefers_single_html = "jednym pliku index.html" in recipe_text or "jeden index.html" in recipe_text
    has_html_app = "index.html" in html_filenames or "html" in program_prompt.lower()

    if recipe_prefers_single_html and has_html_app and not wants_separate_files(program_prompt):
        return [
            {
                "name": "index.html",
                "task_description": (
                    "Stwórz kompletną stronę w jednym pliku index.html. "
                    "Umieść HTML, CSS w tagu <style> i JavaScript w tagu <script>. "
                    "Zaimplementuj cały opis programu bez osobnych plików. "
                    f"Opis programu: {program_prompt}"
                ),
                "filename": "index.html",
            }
        ]

    return tasks


def strip_code_fence(raw: str) -> str:
    text = raw.strip()
    if not text.startswith("```"):
        return text
    lines = text.splitlines()
    if not lines:
        return text
    if lines[0].startswith("```"):
        lines = lines[1:]
    if lines and lines[-1].strip() == "```":
        lines = lines[:-1]
    return "\n".join(lines).strip()


def sse(event: str, data: dict) -> str:
    return f"event: {event}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"


def launch_url(project_id: int) -> str:
    project = get_project_details(project_id)
    if not project:
        raise GenerationError("Nie znaleziono projektu.")
    command = (project.get("recipe_run_command") or "").strip()
    workspace = Path(project["workspace_dir"]).expanduser()

    if not command:
        if (workspace / "index.html").exists():
            command = "index.html"
        elif (workspace / "main.py").exists():
            command = "python main.py"
        else:
            raise GenerationError("Recepta nie ma pola uruchamiania.")

    parts = shlex.split(command)
    first = parts[0] if parts else command
    if first.endswith(".html"):
        target = safe_project_path(project["workspace_dir"], first)
        if not target.exists():
            raise GenerationError(f"Nie znaleziono pliku startowego: {first}")
        return f"/generation/projects/{project_id}/workspace/{first}"

    return f"/generation/projects/{project_id}/run"


async def run_project_command(project_id: int) -> str:
    project = get_project_details(project_id)
    if not project:
        raise GenerationError("Nie znaleziono projektu.")
    command = (project.get("recipe_run_command") or "").strip()
    if not command:
        command = "python main.py"
    parts = shlex.split(command)
    if not parts:
        raise GenerationError("Pusta komenda uruchamiania.")
    if parts[0] == "python":
        parts[0] = sys.executable

    workspace = Path(project["workspace_dir"]).expanduser().resolve()
    if not workspace.exists():
        raise GenerationError("Katalog roboczy projektu nie istnieje.")

    process = await asyncio.create_subprocess_exec(
        *parts,
        cwd=workspace,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    try:
        stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=20)
    except asyncio.TimeoutError:
        process.kill()
        await process.wait()
        stdout, stderr = b"", b"Proces przekroczyl limit 20 sekund."

    output = stdout.decode("utf-8", errors="replace")
    errors = stderr.decode("utf-8", errors="replace")
    title = html.escape(project["name"])
    command_text = html.escape(command)
    output_text = html.escape(output or "(brak stdout)")
    error_text = html.escape(errors or "(brak stderr)")
    code = process.returncode

    return f"""<!doctype html>
<html lang="pl">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Codeeli run: {title}</title>
  <style>
    body {{ background: #111418; color: #eef2f6; font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; margin: 24px; }}
    h1 {{ font-family: system-ui, sans-serif; font-size: 22px; }}
    pre {{ background: #0c0f12; border: 1px solid #343c47; border-radius: 6px; padding: 14px; white-space: pre-wrap; }}
    .meta {{ color: #9aa7b5; margin-bottom: 18px; }}
  </style>
</head>
<body>
  <h1>{title}</h1>
  <div class="meta">Komenda: {command_text} · exit code: {code}</div>
  <h2>stdout</h2>
  <pre>{output_text}</pre>
  <h2>stderr</h2>
  <pre>{error_text}</pre>
</body>
</html>"""


async def generate_project(project_id: int, user_prompt: str) -> AsyncIterator[str]:
    project = get_project_details(project_id)
    if not project:
        yield sse("error", {"message": "Nie znaleziono projektu."})
        return
    if not project.get("model"):
        yield sse("error", {"message": "Projekt nie ma konfiguracji modelu."})
        return

    run_id = repository.create_run(project_id, user_prompt)
    logs: list[str] = []

    try:
        recipe = project.get("recipe_content") or ""
        task_template = get_instruction_content("tasks")
        file_template = get_instruction_content("file")

        yield sse("log", {"message": "Krok 1: proszę model o plan plików."})
        tasks = None
        last_error = ""
        for attempt in range(1, 4):
            prompt = fill_placeholders(
                task_template,
                {"program_prompt": user_prompt, "recipe": recipe},
            )
            yield sse("prompt", {"kind": "plan", "attempt": attempt, "template": task_template, "content": prompt})
            try:
                raw = await llm.complete(project, prompt)
            except Exception as exc:
                last_error = str(exc)
                yield sse("log", {"message": f"Model zwrócił błąd. Próba {attempt}/3: {last_error}"})
                await asyncio.sleep(0.5)
                continue
            yield sse("tasks_raw", {"attempt": attempt, "content": raw})
            try:
                tasks = parse_tasks(raw)
                break
            except Exception as exc:
                last_error = str(exc)
                yield sse("log", {"message": f"Plan nie jest poprawnym JSON-em. Próba {attempt}/3: {last_error}"})
                await asyncio.sleep(0.2)
        if tasks is None:
            raise GenerationError(f"Nie udało się uzyskać poprawnego planu: {last_error}")
        normalized_tasks = normalize_tasks(user_prompt, recipe, tasks)
        if normalized_tasks != tasks:
            yield sse(
                "log",
                {"message": "Codeeli uprościło plan do jednego pliku zgodnie z receptą."},
            )
            tasks = normalized_tasks

        repository.save_tasks(project_id, run_id, tasks)
        yield sse("tasks", {"tasks": tasks})

        root = Path(project["workspace_dir"]).expanduser()
        root.mkdir(parents=True, exist_ok=True)
        context_parts: list[str] = []
        plan_text = "\n".join(
            f"- {task['filename']}: {task['task_description']}" for task in tasks
        )

        for index, task in enumerate(tasks, start=1):
            filename = task["filename"]
            yield sse("log", {"message": f"Krok 2.{index}: generuję {filename}."})
            file_prompt = fill_placeholders(
                file_template,
                {
                    "program_prompt": user_prompt,
                    "recipe": recipe,
                    "context": "\n\n".join(context_parts) or "Brak.",
                    "plan": plan_text,
                    "task_description": task["task_description"],
                    "filename": filename,
                },
            )
            yield sse("prompt", {"kind": "file", "filename": filename, "template": file_template, "content": file_prompt})
            content_parts: list[str] = []
            yield sse("file_start", {"filename": filename})
            async for chunk in llm.stream_complete(project, file_prompt):
                content_parts.append(chunk)
                yield sse("file_delta", {"filename": filename, "content": chunk})
            content = strip_code_fence("".join(content_parts))
            target = safe_project_path(project["workspace_dir"], filename)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(content, encoding="utf-8")
            repository.save_generated_file(project_id, run_id, filename, content)
            context_parts.append(f"FILE: {filename}\n{content}")
            yield sse("file", {"filename": filename, "content": content})

        logs.append("Generowanie zakończone.")
        repository.finish_run(run_id, "success", "\n".join(logs))
        yield sse("done", {"message": "Generowanie zakończone.", "workspace_dir": project["workspace_dir"]})
    except Exception as exc:
        repository.finish_run(run_id, "error", str(exc))
        yield sse("error", {"message": str(exc)})
