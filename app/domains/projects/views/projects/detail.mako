<%inherit file="/base.mako"/>
<%!
import json
%>

% if not project:
  <div class="empty-state">Nie znaleziono projektu.</div>
% else:
<div class="project-layout">
  <section class="panel">
    <h1>${project['name']}</h1>
    <form method="post" action="/projects/${project['id']}" class="vstack gap-3">
      <label class="form-label">Nazwa
        <input class="form-control" name="name" value="${project['name']}" required>
      </label>
      <label class="form-label">Recepta
        <select class="form-select" name="recipe_id" required>
          % for recipe in recipes:
            <option value="${recipe['id']}" ${'selected' if recipe['id'] == project['recipe_id'] else ''}>${recipe['name']}</option>
          % endfor
        </select>
      </label>
      <label class="form-label">Konfiguracja modelu
        <select class="form-select" name="ai_config_id" required>
          % for config in configs:
            <option value="${config['id']}" ${'selected' if config['id'] == project['ai_config_id'] else ''}>${config['name']} (${config['provider']}/${config['model']})</option>
          % endfor
        </select>
      </label>
      <label class="form-label">Katalog roboczy
        <input class="form-control" name="workspace_dir" value="${project['workspace_dir']}" required>
      </label>
      <label class="form-label">Opis programu
        <textarea id="programPrompt" class="form-control" name="prompt" rows="10">${project['prompt']}</textarea>
      </label>
      <div class="d-flex gap-2">
        <button class="btn btn-outline-light" type="submit">Zapisz</button>
        <button class="btn btn-primary" type="button" data-generate-project="${project['id']}">Generuj program</button>
        <button class="btn btn-success ${'' if generation_state.get('run') and generation_state['run']['status'] == 'success' and generation_state.get('files') else 'd-none'}" type="button" data-launch-project="${project['id']}">Uruchom aplikację</button>
      </div>
    </form>
  </section>

  <section class="generation-board">
    <div class="section-head compact">
      <h2>Generowanie</h2>
      <div class="d-flex gap-2 align-items-center">
        <button id="timelineExpandAll" type="button" class="btn btn-sm btn-outline-light">Rozwiń wszystko</button>
        <button id="timelineCollapseAll" type="button" class="btn btn-sm btn-outline-light">Zwiń wszystko</button>
      </div>
    </div>
    <p class="text-muted small mb-2">Pełny strumień: logi, prompty wysłane do modelu, surowe odpowiedzi i zapisane pliki — w jednym oknie. Długie bloki są zwijane (kliknij nagłówek).</p>
    <div class="panel">
      <div id="timeline" class="timeline"></div>
    </div>
  </section>
</div>
<script id="initialGenerationState" type="application/json">${json.dumps(generation_state, ensure_ascii=False).replace("</", "<\\/") | n}</script>
% endif
