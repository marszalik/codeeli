from app.domains.instructions import repository


def list_instructions() -> list[dict]:
    return repository.list_instructions()


def get_instruction_content(key: str) -> str:
    item = repository.get_instruction(key)
    return item["content"] if item else ""


def update_instruction(item_id: int, title: str, content: str) -> None:
    repository.update_instruction(item_id, title, content)


def fill_placeholders(template: str, values: dict[str, str]) -> str:
    result = template
    for key, value in values.items():
        result = result.replace("{{" + key + "}}", value)
    return result
