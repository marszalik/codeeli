<%!
import os
import time
from app.domains.core.config import APP_DIR

_STATIC_DIR = str(APP_DIR / "domains" / "core" / "static")

def asset_v(name: str) -> int:
    path = os.path.join(_STATIC_DIR, name)
    try:
        return int(os.path.getmtime(path))
    except OSError:
        return int(time.time())
%>
<!doctype html>
<html lang="pl">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Codeeli</title>
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
  <link href="/static/core.css?v=${asset_v('core.css')}" rel="stylesheet">
</head>
<body>
  <nav class="navbar navbar-expand-lg navbar-dark border-bottom border-secondary-subtle sticky-top app-nav">
    <div class="container-fluid px-4">
      <a class="navbar-brand d-flex align-items-center gap-2" href="/projects">
        <span class="brand-mark">C</span>
        <span>Codeeli</span>
      </a>
      <div class="navbar-nav nav-pills gap-1">
        <a class="nav-link ${'active' if active == 'projects' else ''}" href="/projects">Projekty</a>
        <a class="nav-link ${'active' if active == 'recipes' else ''}" href="/recipes">Recepty</a>
        <a class="nav-link ${'active' if active == 'instructions' else ''}" href="/instructions">Instrukcje</a>
        <a class="nav-link ${'active' if active == 'ai' else ''}" href="/ai-settings">AI</a>
      </div>
    </div>
  </nav>
  <main class="container-fluid px-4 py-4">
    ${self.body()}
  </main>
  <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"></script>
  <script src="/static/core.js?v=${asset_v('core.js')}"></script>
</body>
</html>
