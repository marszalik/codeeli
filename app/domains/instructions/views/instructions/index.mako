<%inherit file="/base.mako"/>

<div class="section-head">
  <h1>Instructions</h1>
  <p>Prompt templates used by the generator. Placeholders: {{program_prompt}}, {{recipe}}, {{context}}, {{plan}}, {{task_description}}, {{filename}}.</p>
</div>

<div class="vstack gap-3">
  % for item in instructions:
    <form method="post" action="/instructions/${item['id']}" class="panel">
      <div class="d-flex justify-content-between align-items-center gap-3">
        <label class="form-label flex-grow-1">Title
          <input class="form-control" name="title" value="${item['title']}" required>
        </label>
        <span class="badge text-bg-secondary">${item['key']}</span>
      </div>
      <label class="form-label mt-3">Content
        <textarea class="form-control monospace" name="content" rows="12" required>${item['content']}</textarea>
      </label>
      <button class="btn btn-outline-light btn-sm mt-3" type="submit">Save instruction</button>
    </form>
  % endfor
</div>
