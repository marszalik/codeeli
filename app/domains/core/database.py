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
        "Prosty Python",
        "Używaj prostego Pythona. Preferuj standard library. Twórz małe, czytelne pliki. Zwracaj dokładnie żądaną treść.",
        "python main.py",
    ),
    (
        "Prosty HTML i JavaScript",
        "Użyj prostego HTML-a i JavaScriptu. Jeśli użytkownik nie prosi o osobne pliki, zrób jeden index.html.",
        "index.html",
    ),
    (
        "Mały Python CLI",
        "Zrób program w prostym Pythonie 3. Używaj tylko standard library. Najlepiej jeden plik. Bez markdown.",
        "python main.py",
    ),
    (
        "Mały HTML JS",
        "Zrób prostą stronę w jednym pliku index.html. Umieść CSS w <style>, a JavaScript w <script>. Osobne pliki twórz tylko gdy użytkownik o nie prosi. Bez frameworków. Bez markdown.",
        "index.html",
    ),
    (
        "Mała gra HTML",
        "Zrób grę w jednym pliku index.html. CSS w <style>, JavaScript w <script>. Trzymaj prosty stan gry. Po wygranej lub remisie zatrzymaj ruchy i nie nadpisuj komunikatu wyniku. Dodaj przycisk restart. Bez markdown.",
        "index.html",
    ),
    (
        "Mały CRUD HTML",
        "Zrób aplikację CRUD w jednym pliku index.html. CSS w <style>, JavaScript w <script>. Dane trzymaj w localStorage. Formularze obsługuj przez submit z event.preventDefault(). Dodaj listę, wyszukiwanie i usuwanie jeśli pasuje do zadania. Bez markdown.",
        "index.html",
    ),
]

DEFAULT_INSTRUCTIONS = [
    (
        "tasks",
        "Generowanie tasków",
        """Opis programu:
{{program_prompt}}

Recepta:
{{recipe}}

Zaplanuj bardzo małą liczbę plików.
Jeśli da się zrobić jeden plik, użyj jednego pliku.
Jeśli to prosta strona HTML i użytkownik nie prosi o osobne pliki, zaplanuj tylko index.html.
Zwróć tylko tablicę JSON.
Format:
[{"name":"krótka nazwa","task_description":"pełny opis zawartości pliku","filename":"nazwa_pliku"}]
Jeśli planujesz index.html oraz osobne pliki CSS/JS, opisz w tasku index.html, że ma linkować dokładnie te pliki.
Nie używaj markdown. Nie dodawaj tekstu poza JSON.
filename ma być ścieżką względną, bez .. i bez ścieżki absolutnej.""",
    ),
    (
        "file",
        "Generowanie pliku",
        """Opis programu:
{{program_prompt}}

Recepta:
{{recipe}}

Poprzednio wygenerowane pliki:
{{context}}

Pełny plan plików:
{{plan}}

Task:
{{task_description}}

Docelowa ścieżka pliku:
{{filename}}

Napisz kompletną treść tego jednego pliku.
Jeśli ten plik ma odwoływać się do innych plików z planu, użyj dokładnych nazw z planu.
Nie kopiuj kodu z innych plików, jeśli plan przewiduje osobny plik.
Jeśli piszesz JavaScript, użyj dokładnych id, klas i nazw funkcji z HTML.
Jeśli HTML ma onclick="nazwa()", funkcja nazwa musi być dostępna jako window.nazwa.
Jeśli używasz formularza, obsłuż submit z event.preventDefault() albo ustaw przyciski akcji jako type="button".
Zwróć tylko kod pliku.
Pierwszy znak odpowiedzi ma być pierwszym znakiem pliku.
Nie używaj markdown. Nie dodawaj objaśnień.""",
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
