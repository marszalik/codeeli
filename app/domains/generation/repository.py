from app.domains.core.database import db

def create_run(project_id: int, user_prompt: str) -> int:
    with db() as conn:
        cursor = conn.execute(
            "INSERT INTO generation_runs (project_id, user_prompt, status) VALUES (?, ?, ?)",
            (project_id, user_prompt, "running"),
        )
        return int(cursor.lastrowid)

def finish_run(run_id: int, status: str, log: str) -> None:
    with db() as conn:
        conn.execute(
            "UPDATE generation_runs SET status = ?, log = ?, finished_at = CURRENT_TIMESTAMP WHERE id = ?",
            (status, log, run_id),
        )

def save_tasks(project_id: int, run_id: int, tasks: list[dict]) -> None:
    with db() as conn:
        conn.execute("DELETE FROM tasks WHERE project_id = ?", (project_id,))
        for index, task in enumerate(tasks):
            conn.execute(
                """
                INSERT INTO tasks (project_id, run_id, name, task_description, filename, position)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    project_id,
                    run_id,
                    task["name"],
                    task["task_description"],
                    task["filename"],
                    index,
                ),
            )

def save_generated_file(project_id: int, run_id: int, filename: str, content: str) -> None:
    with db() as conn:
        conn.execute(
            """
            INSERT INTO generated_files (project_id, run_id, filename, content)
            VALUES (?, ?, ?, ?)
            """,
            (project_id, run_id, filename, content),
        )

def list_generated_files(project_id: int) -> list[dict]:
    with db() as conn:
        return conn.execute(
            """
            SELECT gf.*
            FROM generated_files gf
            JOIN (
                SELECT filename, MAX(id) AS id
                FROM generated_files
                WHERE project_id = ?
                GROUP BY filename
            ) latest ON latest.id = gf.id
            ORDER BY gf.filename
            """,
            (project_id,),
        ).fetchall()

def latest_run(project_id: int) -> dict | None:
    with db() as conn:
        return conn.execute(
            """
            SELECT *
            FROM generation_runs
            WHERE project_id = ?
            ORDER BY id DESC
            LIMIT 1
            """,
            (project_id,),
        ).fetchone()

def latest_tasks(project_id: int) -> list[dict]:
    with db() as conn:
        run = conn.execute(
            "SELECT id FROM generation_runs WHERE project_id = ? ORDER BY id DESC LIMIT 1",
            (project_id,),
        ).fetchone()
        if not run:
            return []
        return conn.execute(
            "SELECT * FROM tasks WHERE run_id = ? ORDER BY position",
            (run["id"],),
        ).fetchall()

def latest_state(project_id: int) -> dict:
    run = latest_run(project_id)
    return {
        "run": run,
        "tasks": latest_tasks(project_id),
        "files": list_generated_files(project_id),
    }
