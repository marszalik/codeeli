from app.domains.core.database import db


def list_instructions() -> list[dict]:
    with db() as conn:
        return conn.execute("SELECT * FROM instructions ORDER BY key").fetchall()


def get_instruction(key: str) -> dict | None:
    with db() as conn:
        return conn.execute("SELECT * FROM instructions WHERE key = ?", (key,)).fetchone()


def update_instruction(item_id: int, title: str, content: str) -> None:
    with db() as conn:
        conn.execute(
            "UPDATE instructions SET title = ?, content = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
            (title, content, item_id),
        )
