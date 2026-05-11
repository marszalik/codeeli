from app.domains.core.database import db


def list_recipes() -> list[dict]:
    with db() as conn:
        return conn.execute("SELECT * FROM recipes ORDER BY id DESC").fetchall()


def get_recipe(recipe_id: int) -> dict | None:
    with db() as conn:
        return conn.execute("SELECT * FROM recipes WHERE id = ?", (recipe_id,)).fetchone()


def create_recipe(name: str, content: str, run_command: str) -> None:
    with db() as conn:
        conn.execute(
            "INSERT INTO recipes (name, content, run_command) VALUES (?, ?, ?)",
            (name, content, run_command),
        )


def update_recipe(recipe_id: int, name: str, content: str, run_command: str) -> None:
    with db() as conn:
        conn.execute(
            "UPDATE recipes SET name = ?, content = ?, run_command = ? WHERE id = ?",
            (name, content, run_command, recipe_id),
        )


def delete_recipe(recipe_id: int) -> None:
    with db() as conn:
        conn.execute("DELETE FROM recipes WHERE id = ?", (recipe_id,))
