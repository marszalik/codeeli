import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager

from app.domains.core.config import DB_PATH, ensure_runtime_dirs


SCHEMA = """
CREATE TABLE IF NOT EXISTS ai_configs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    provider TEXT NOT NULL,
    base_url TEXT NOT NULL,
    api_key TEXT NOT NULL DEFAULT '',
    model TEXT NOT NULL,
    temperature REAL NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS recipes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    content TEXT NOT NULL,
    run_command TEXT NOT NULL DEFAULT '',
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS instructions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    key TEXT NOT NULL UNIQUE,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS projects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    recipe_id INTEGER,
    ai_config_id INTEGER,
    workspace_dir TEXT NOT NULL,
    prompt TEXT NOT NULL DEFAULT '',
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (recipe_id) REFERENCES recipes(id),
    FOREIGN KEY (ai_config_id) REFERENCES ai_configs(id)
);

CREATE TABLE IF NOT EXISTS generation_runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    user_prompt TEXT NOT NULL,
    status TEXT NOT NULL,
    log TEXT NOT NULL DEFAULT '',
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    finished_at TEXT,
    FOREIGN KEY (project_id) REFERENCES projects(id)
);

CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    run_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    task_description TEXT NOT NULL,
    filename TEXT NOT NULL,
    position INTEGER NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(id),
    FOREIGN KEY (run_id) REFERENCES generation_runs(id)
);

CREATE TABLE IF NOT EXISTS generated_files (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    run_id INTEGER NOT NULL,
    filename TEXT NOT NULL,
    content TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(id),
    FOREIGN KEY (run_id) REFERENCES generation_runs(id)
);
"""


DEFAULT_RECIPES = [
    (
        "Simple Python",
        "Use plain Python. Prefer the standard library. Produce small, readable files. Return exactly the requested content.",
        "python main.py",
    ),
    (
        "Simple HTML and JavaScript",
        "Use plain HTML and JavaScript. If the user does not ask for separate files, produce a single index.html.",
        "index.html",
    ),
    (
        "Small Python CLI",
        "Build a program in plain Python 3. Use only the standard library. Prefer a single file. No markdown.",
        "python main.py",
    ),
    (
        "Small HTML JS",
        "Build a simple page in a single index.html file. Put CSS inside <style> and JavaScript inside <script>. Only create separate files if the user explicitly asks. No frameworks. No markdown.",
        "index.html",
    ),
    (
        "Small HTML Game",
        "Build a game in a single index.html file. CSS in <style>, JavaScript in <script>. Keep simple game state. On win or draw, stop moves and do not overwrite the result message. Add a restart button. No markdown.",
        "index.html",
    ),
    (
        "Small CRUD HTML",
        "Build a CRUD application in a single index.html file. CSS in <style>, JavaScript in <script>. Store data in localStorage. Handle forms with submit + event.preventDefault(). Add list, search, and delete if it fits the task. No markdown.",
        "index.html",
    ),
]

DEFAULT_INSTRUCTIONS = [
    (
        "tasks",
        "Task planning",
        """Program description:
{{program_prompt}}

Recipe:
{{recipe}}

Plan a very small number of files.
If it can be done with one file, use one file.
If it is a simple HTML page and the user does not ask for separate files, plan only index.html.
Return only a JSON array.
Format:
[{"name":"short name","task_description":"full description of the file contents","filename":"file_name"}]
If you plan index.html together with separate CSS/JS files, state in the index.html task that it must link exactly those files.
Do not use markdown. Do not add any text outside the JSON.
filename must be a relative path, without .. and without an absolute path.""",
    ),
    (
        "file",
        "File generation",
        """Program description:
{{program_prompt}}

Recipe:
{{recipe}}

Previously generated files:
{{context}}

Full file plan:
{{plan}}

Task:
{{task_description}}

Target file path:
{{filename}}

Write the full contents of this single file.
If this file references other files from the plan, use the exact names from the plan.
Do not copy code from other files when the plan calls for a separate file.
If you write JavaScript, use the exact ids, classes, and function names from the HTML.
If the HTML has onclick="name()", the function name must be available as window.name.
If you use a form, handle submit with event.preventDefault() or set action buttons to type="button".
Return only the file code.
The first character of the response must be the first character of the file.
Do not use markdown. Do not add explanations.""",
    ),
]


def dict_factory(cursor: sqlite3.Cursor, row: sqlite3.Row) -> dict:
    return {column[0]: row[index] for index, column in enumerate(cursor.description)}


@contextmanager
def db() -> Iterator[sqlite3.Connection]:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = dict_factory
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db() -> None:
    ensure_runtime_dirs()
    with db() as conn:
        conn.executescript(SCHEMA)
        columns = {
            row["name"]
            for row in conn.execute("PRAGMA table_info(recipes)").fetchall()
        }
        if "run_command" not in columns:
            conn.execute("ALTER TABLE recipes ADD COLUMN run_command TEXT NOT NULL DEFAULT ''")

        for name, content, run_command in DEFAULT_RECIPES:
            exists = conn.execute("SELECT id FROM recipes WHERE name = ?", (name,)).fetchone()
            if not exists:
                conn.execute(
                    "INSERT INTO recipes (name, content, run_command) VALUES (?, ?, ?)",
                    (name, content, run_command),
                )
            elif not exists.get("run_command"):
                conn.execute(
                    "UPDATE recipes SET run_command = ? WHERE id = ?",
                    (run_command, exists["id"]),
                )
        for key, title, content in DEFAULT_INSTRUCTIONS:
            exists = conn.execute("SELECT id FROM instructions WHERE key = ?", (key,)).fetchone()
            if not exists:
                conn.execute(
                    "INSERT INTO instructions (key, title, content) VALUES (?, ?, ?)",
                    (key, title, content),
                )
