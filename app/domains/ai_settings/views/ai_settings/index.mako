<%inherit file="/base.mako"/>

<div class="page-grid">
  <section>
    <div class="section-head">
      <h1>AI Settings</h1>
      <p>Model configurations for OpenAI, LiteLLM, and Ollama.</p>
    </div>
    <div class="list-group list-group-flush codeeli-list">
      % if configs:
        % for config in configs:
          <div class="list-group-item">
            <div class="d-flex justify-content-between gap-3">
              <strong>${config['name']}</strong>
              <form method="post" action="/ai-settings/${config['id']}/delete">
                <button class="btn btn-outline-danger btn-sm" type="submit">Delete</button>
              </form>
            </div>
            <div class="small text-secondary">${config['provider']} · ${config['base_url']}</div>
            <div class="mt-2">${config['model']} · temperature ${config['temperature']}</div>
          </div>
        % endfor
      % else:
        <div class="empty-state">No configurations. Add a model on the right.</div>
      % endif
    </div>
  </section>

  <aside class="panel">
    <h2>New configuration</h2>
    <form method="post" action="/ai-settings" class="vstack gap-3" id="aiConfigForm">
      <label class="form-label">Name
        <input class="form-control" name="name" required>
      </label>
      <label class="form-label">Provider
        <select class="form-select" name="provider" id="providerSelect">
          <option value="openai">OpenAI</option>
          <option value="litellm">LiteLLM</option>
          <option value="ollama">Ollama</option>
        </select>
      </label>
      <label class="form-label">Base URL
        <input class="form-control" name="base_url" id="baseUrlInput" placeholder="provider default">
      </label>
      <label class="form-label">API key
        <input class="form-control" name="api_key" id="apiKeyInput" type="password">
      </label>
      <label class="form-label">Model
        <div class="input-group">
          <input class="form-control" name="model" id="modelInput" required>
          <button class="btn btn-outline-light" type="button" id="loadModelsButton">Fetch</button>
        </div>
        <select class="form-select mt-2 d-none" id="modelSelect"></select>
        <div class="form-text" id="modelHelp">OpenAI, LiteLLM, and Ollama can fetch a model list. For OpenAI you can also type e.g. gpt-5.4-nano.</div>
      </label>
      <label class="form-label">Temperature
        <input class="form-control" name="temperature" type="number" min="0" max="2" step="0.1" value="0">
      </label>
      <button class="btn btn-primary" type="submit">Add configuration</button>
    </form>
  </aside>
</div>
