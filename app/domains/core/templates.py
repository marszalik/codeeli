from mako.lookup import TemplateLookup

from app.domains.core.config import APP_DIR


lookup = TemplateLookup(
    directories=[
        str(APP_DIR / "domains" / "core" / "views"),
        str(APP_DIR / "domains" / "ai_settings" / "views"),
        str(APP_DIR / "domains" / "projects" / "views"),
        str(APP_DIR / "domains" / "recipes" / "views"),
        str(APP_DIR / "domains" / "instructions" / "views"),
    ],
    input_encoding="utf-8",
    output_encoding="utf-8",
    default_filters=["h"],
)


def render(template_name: str, **context) -> bytes:
    template = lookup.get_template(template_name)
    return template.render(**context)
