<%inherit file="/base.mako"/>

<div class="page-grid">
  <section>
    <div class="section-head">
      <h1>Projekty</h1>
      <p>Programy docelowe generowane przez Codeeli.</p>
    </div>
    <div class="list-group list-group-flush codeeli-list">
      % if projects:
        % for project in projects:
          <a class="list-group-item list-group-item-action" href="/projects/${project['id']}">
            <div class="d-flex justify-content-between gap-3">
              <strong>${project['name']}</strong>
              <span class="text-secondary small">${project['ai_config_name'] or 'brak AI'}</span>
            </div>
            <div class="small text-secondary mt-1">${project['workspace_dir']}</div>
            <div class="small mt-2">Recepta: ${project['recipe_name'] or 'brak'}</div>
          </a>
        % endfor
      % else:
        <div class="empty-state">Brak projektów. Utwórz pierwszy projekt po prawej.</div>
      % endif
    </div>
  </section>

  <aside class="panel">
    <h2>Nowy projekt</h2>
    <form method="post" action="/projects" class="vstack gap-3">
      <label class="form-label">Nazwa
        <input class="form-control" name="name" required>
      </label>
      <label class="form-label">Recepta
        <select class="form-select" name="recipe_id" required>
          % for recipe in recipes:
            <option value="${recipe['id']}">${recipe['name']}</option>
          % endfor
        </select>
      </label>
      <label class="form-label">Konfiguracja modelu
        <select class="form-select" name="ai_config_id" required>
          % for config in configs:
            <option value="${config['id']}">${config['name']} (${config['provider']}/${config['model']})</option>
          % endfor
        </select>
      </label>
      <label class="form-label">Katalog roboczy
        <input class="form-control" name="workspace_dir" placeholder="domyślnie: workspaces/nazwa-projektu">
      </label>
      <label class="form-label">Opis programu
        <textarea class="form-control" name="prompt" rows="7"></textarea>
      </label>
      <button class="btn btn-primary" type="submit" ${'disabled' if not configs or not recipes else ''}>Utwórz projekt</button>
    </form>
  </aside>
</div>
