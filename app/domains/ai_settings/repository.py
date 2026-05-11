from app.domains.core.database import db


def list_configs() -> list[dict]:
    with db() as conn:
        return conn.execute("SELECT * FROM ai_configs ORDER BY id DESC").fetchall()


def get_config(config_id: int) -> dict | None:
    with db() as conn:
        return conn.execute("SELECT * FROM ai_configs WHERE id = ?", (config_id,)).fetchone()


def create_config(data: dict) -> None:
    with db() as conn:
        conn.execute(
            """
            INSERT INTO ai_configs (name, provider, base_url, api_key, model, temperature)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                data["name"],
                data["provider"],
                data["base_url"],
                data.get("api_key", ""),
                data["model"],
                float(data.get("temperature") or 0),
            ),
        )


def delete_config(config_id: int) -> None:
    with db() as conn:
        conn.execute("DELETE FROM ai_configs WHERE id = ?", (config_id,))
