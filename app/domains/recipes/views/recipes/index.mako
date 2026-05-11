<%inherit file="/base.mako"/>

<div class="page-grid">
  <section>
    <div class="section-head">
      <h1>Recepty</h1>
      <p>Krótkie instrukcje prowadzące mały model.</p>
    </div>
    <div class="vstack gap-3">
      % for recipe in recipes:
        <form method="post" action="/recipes/${recipe['id']}" class="panel">
          <label class="form-label">Nazwa
            <input class="form-control" name="name" value="${recipe['name']}" required>
          </label>
          <label class="form-label mt-3">Treść
            <textarea class="form-control" name="content" rows="4" required>${recipe['content']}</textarea>
          </label>
          <label class="form-label mt-3">Uruchamianie
            <input class="form-control monospace" name="run_command" value="${recipe.get('run_command') or ''}" placeholder="index.html albo python main.py">
          </label>
          <div class="d-flex gap-2 mt-3">
            <button class="btn btn-outline-light btn-sm" type="submit">Zapisz</button>
            <button class="btn btn-outline-danger btn-sm" form="delete-recipe-${recipe['id']}" type="submit">Usuń</button>
          </div>
        </form>
        <form id="delete-recipe-${recipe['id']}" method="post" action="/recipes/${recipe['id']}/delete"></form>
      % endfor
    </div>
  </section>
  <aside class="panel">
    <h2>Nowa recepta</h2>
    <form method="post" action="/recipes" class="vstack gap-3">
      <label class="form-label">Nazwa
        <input class="form-control" name="name" required>
      </label>
      <label class="form-label">Treść
        <textarea class="form-control" name="content" rows="8" required></textarea>
      </label>
      <label class="form-label">Uruchamianie
        <input class="form-control monospace" name="run_command" placeholder="index.html albo python main.py">
      </label>
      <button class="btn btn-primary" type="submit">Dodaj receptę</button>
    </form>
  </aside>
</div>
