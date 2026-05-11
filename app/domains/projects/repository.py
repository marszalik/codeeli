from app.domains.core.database import db


def list_projects() -> list[dict]:
    with db() as conn:
        return conn.execute(
            """
            SELECT p.*, r.name AS recipe_name, a.name AS ai_config_name
            FROM projects p
            LEFT JOIN recipes r ON r.id = p.recipe_id
            LEFT JOIN ai_configs a ON a.id = p.ai_config_id
            ORDER BY p.id DESC
            """
        ).fetchall()


def get_project(project_id: int) -> dict | None:
    with db() as conn:
        return conn.execute("SELECT * FROM projects WHERE id = ?", (project_id,)).fetchone()


def get_project_details(project_id: int) -> dict | None:
    with db() as conn:
        return conn.execute(
            """
            SELECT p.*, r.content AS recipe_content, r.run_command AS recipe_run_command, r.name AS recipe_name,
                   a.provider, a.base_url, a.api_key, a.model, a.temperature,
                   a.name AS ai_config_name
            FROM projects p
            LEFT JOIN recipes r ON r.id = p.recipe_id
            LEFT JOIN ai_configs a ON a.id = p.ai_config_id
            WHERE p.id = ?
            """,
            (project_id,),
        ).fetchone()


def create_project(name: str, recipe_id: int, ai_config_id: int, workspace_dir: str, prompt: str) -> None:
    with db() as conn:
        conn.execute(
            """
            INSERT INTO projects (name, recipe_id, ai_config_id, workspace_dir, prompt)
            VALUES (?, ?, ?, ?, ?)
            """,
            (name, recipe_id, ai_config_id, workspace_dir, prompt),
        )


def update_project(project_id: int, name: str, recipe_id: int, ai_config_id: int, workspace_dir: str, prompt: str) -> None:
    with db() as conn:
        conn.execute(
            """
            UPDATE projects
            SET name = ?, recipe_id = ?, ai_config_id = ?, workspace_dir = ?, prompt = ?
            WHERE id = ?
            """,
            (name, recipe_id, ai_config_id, workspace_dir, prompt, project_id),
        )


def delete_project(project_id: int) -> None:
    with db() as conn:
        conn.execute("DELETE FROM projects WHERE id = ?", (project_id,))
