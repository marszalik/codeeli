const providerDefaults = {
  openai: "https://api.openai.com/v1",
  litellm: "http://localhost:4000",
  ollama: "http://localhost:11434",
};

const providerModelHints = {
  openai: ["gpt-5.4-nano", "5.4-nano"],
  litellm: [],
  ollama: [],
};

function setupAiSettings() {
  const provider = document.querySelector("#providerSelect");
  const baseUrl = document.querySelector("#baseUrlInput");
  const apiKey = document.querySelector("#apiKeyInput");
  const modelInput = document.querySelector("#modelInput");
  const modelSelect = document.querySelector("#modelSelect");
  const loadButton = document.querySelector("#loadModelsButton");
  const help = document.querySelector("#modelHelp");
  if (!provider || !loadButton) return;

  function syncProviderDefaults() {
    baseUrl.placeholder = providerDefaults[provider.value] || "";
    modelInput.placeholder = providerModelHints[provider.value]?.[0] || "";
    // auto-fill base_url with provider default if user hasn't typed anything
    if (!baseUrl.value && providerDefaults[provider.value]) {
      baseUrl.value = providerDefaults[provider.value];
    }
  }
  syncProviderDefaults();
  provider.addEventListener("change", syncProviderDefaults);

  modelSelect.addEventListener("change", () => {
    modelInput.value = modelSelect.value;
  });

  function setHelp(text, kind) {
    help.textContent = text;
    help.classList.remove("text-danger", "text-success", "text-info");
    if (kind === "error") help.classList.add("text-danger");
    else if (kind === "ok") help.classList.add("text-success");
    else if (kind === "info") help.classList.add("text-info");
  }

  loadButton.addEventListener("click", async () => {
    // pre-flight: warn early if api_key missing for providers that need it
    const prov = provider.value;
    if ((prov === "litellm" || prov === "openai") && !apiKey.value.trim()) {
      setHelp(`${prov} requires an API key — enter it in the field above and click Fetch again.`, "error");
      return;
    }
    setHelp("Fetching models...", "info");
    modelSelect.classList.add("d-none");
    const params = new URLSearchParams({
      provider: prov,
      base_url: baseUrl.value,
      api_key: apiKey.value,
    });
    let payload;
    try {
      const response = await fetch(`/ai-settings/models?${params.toString()}`);
      payload = await response.json();
    } catch (err) {
      setHelp(`Network error: ${err.message}`, "error");
      return;
    }
    modelSelect.innerHTML = "";
    if (payload.models && payload.models.length) {
      for (const model of payload.models) {
        const option = document.createElement("option");
        option.value = model;
        option.textContent = model;
        modelSelect.appendChild(option);
      }
      modelInput.value = payload.models[0];
      modelSelect.classList.remove("d-none");
      setHelp(`Found models: ${payload.models.length}. First one selected — you can pick another in the list below.`, "ok");
    } else {
      setHelp(payload.error || "No models found. Enter the name manually.", "error");
    }
  });
}

function setupGeneration() {
  const button = document.querySelector("[data-generate-project]");
  if (!button) return;
  const launchButton = document.querySelector("[data-launch-project]");
  const prompt = document.querySelector("#programPrompt");
  const timeline = document.querySelector("#timeline");
  const expandAllBtn = document.querySelector("#timelineExpandAll");
  const collapseAllBtn = document.querySelector("#timelineCollapseAll");
  if (!timeline) return;

  // streaming file aggregation: filename -> { node, contentEl }
  const streamingFiles = new Map();

  function nowStamp() {
    return new Date().toLocaleTimeString();
  }

  function clearTimeline() {
    timeline.innerHTML = "";
    streamingFiles.clear();
  }

  function autoscroll() {
    timeline.scrollTop = timeline.scrollHeight;
  }

  function tagClass(kind) {
    return `tl-tag tl-tag-${kind}`;
  }

  // simple log entry (one line, no body)
  function addLog(message, kind = "log") {
    const row = document.createElement("div");
    row.className = `tl-entry tl-${kind}`;
    const head = document.createElement("div");
    head.className = "tl-head";
    head.innerHTML = `<span class="tl-time"></span><span class="${tagClass(kind)}"></span><span class="tl-title"></span>`;
    head.querySelector(".tl-time").textContent = nowStamp();
    head.querySelector(".tl-tag").textContent = kind.toUpperCase();
    head.querySelector(".tl-title").textContent = message;
    row.appendChild(head);
    timeline.appendChild(row);
    autoscroll();
    return row;
  }

  // collapsible body entry. opts: {kind, title, body, openByDefault, language}
  function addBlock(opts) {
    const details = document.createElement("details");
    details.className = `tl-entry tl-${opts.kind}`;
    if (opts.openByDefault) details.open = true;
    const summary = document.createElement("summary");
    summary.className = "tl-head";
    summary.innerHTML = `<span class="tl-time"></span><span class="${tagClass(opts.kind)}"></span><span class="tl-title"></span><span class="tl-meta"></span>`;
    summary.querySelector(".tl-time").textContent = nowStamp();
    summary.querySelector(".tl-tag").textContent = (opts.tagText || opts.kind).toUpperCase();
    summary.querySelector(".tl-title").textContent = opts.title || "";
    if (opts.meta) summary.querySelector(".tl-meta").textContent = opts.meta;
    details.appendChild(summary);
    const pre = document.createElement("pre");
    pre.className = "tl-body";
    if (opts.language) pre.dataset.language = opts.language;
    pre.textContent = opts.body || "";
    details.appendChild(pre);
    timeline.appendChild(details);
    autoscroll();
    return { details, pre };
  }

  function startStreamingFile(filename) {
    const block = addBlock({
      kind: "file-stream",
      tagText: "file",
      title: `Writing file: ${filename}`,
      body: "",
      openByDefault: true,
    });
    streamingFiles.set(filename, block);
    return block;
  }

  function appendToStreamingFile(filename, chunk) {
    let block = streamingFiles.get(filename);
    if (!block) block = startStreamingFile(filename);
    block.pre.textContent += chunk;
    autoscroll();
  }

  function finalizeFile(filename, content) {
    const block = streamingFiles.get(filename);
    if (block) {
      block.pre.textContent = content;
      const meta = block.details.querySelector(".tl-meta");
      if (meta) meta.textContent = `${content.length} chars · saved`;
      const titleEl = block.details.querySelector(".tl-title");
      if (titleEl) titleEl.textContent = `Saved file: ${filename}`;
      streamingFiles.delete(filename);
    } else {
      addBlock({
        kind: "file-saved",
        tagText: "file",
        title: `Saved file: ${filename}`,
        meta: `${content.length} chars`,
        body: content,
      });
    }
  }

  function renderTasks(tasks) {
    const lines = tasks.map((t, i) => `${i + 1}. [${t.filename}] ${t.name}\n    ${t.task_description}`).join("\n\n");
    addBlock({
      kind: "tasks",
      title: `File plan (${tasks.length})`,
      body: lines,
      openByDefault: true,
    });
  }

  function renderPrompt(data) {
    const titleBits = [`Prompt → model`, `kind=${data.kind}`];
    if (data.filename) titleBits.push(`file=${data.filename}`);
    if (data.attempt) titleBits.push(`attempt=${data.attempt}`);
    addBlock({
      kind: "prompt",
      title: titleBits.join(" · "),
      meta: `${(data.content || "").length} chars`,
      body: data.content || "",
    });
  }

  function renderTasksRaw(data) {
    addBlock({
      kind: "response",
      title: `Raw model response (plan, attempt ${data.attempt})`,
      meta: `${(data.content || "").length} chars`,
      body: data.content || "",
    });
  }

  if (expandAllBtn) {
    expandAllBtn.addEventListener("click", () => {
      timeline.querySelectorAll("details").forEach((d) => (d.open = true));
    });
  }
  if (collapseAllBtn) {
    collapseAllBtn.addEventListener("click", () => {
      timeline.querySelectorAll("details").forEach((d) => (d.open = false));
    });
  }

  function loadInitialState() {
    const stateNode = document.querySelector("#initialGenerationState");
    if (!stateNode || !stateNode.textContent.trim()) return;
    const state = JSON.parse(stateNode.textContent);
    if (!state.run) return;
    addLog(`Last run: ${state.run.status}`, "log");
    if (state.run.created_at) addLog(`Start: ${state.run.created_at}`, "log");
    if (state.run.finished_at) addLog(`End: ${state.run.finished_at}`, "log");
    if (state.run.log) {
      for (const line of state.run.log.split("\n").filter(Boolean)) addLog(line, "log");
    }
    if (state.tasks && state.tasks.length) renderTasks(state.tasks);
    if (state.files && state.files.length) {
      for (const f of state.files) {
        addBlock({
          kind: "file-saved",
          tagText: "file",
          title: `File: ${f.filename}`,
          meta: `${(f.content || "").length} chars`,
          body: f.content || "",
        });
      }
    }
    if (launchButton && state.run.status === "success" && state.files && state.files.length) {
      launchButton.classList.remove("d-none");
    }
  }

  async function handleSse(response) {
    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = "";
    while (true) {
      const { value, done } = await reader.read();
      if (done) break;
      buffer += decoder.decode(value, { stream: true });
      const chunks = buffer.split("\n\n");
      buffer = chunks.pop() || "";
      for (const chunk of chunks) {
        const eventLine = chunk.split("\n").find((line) => line.startsWith("event: "));
        const dataLine = chunk.split("\n").find((line) => line.startsWith("data: "));
        if (!eventLine || !dataLine) continue;
        const event = eventLine.slice(7);
        let data;
        try {
          data = JSON.parse(dataLine.slice(6));
        } catch {
          continue;
        }
        if (event === "log") addLog(data.message, "log");
        else if (event === "prompt") renderPrompt(data);
        else if (event === "tasks_raw") renderTasksRaw(data);
        else if (event === "tasks") renderTasks(data.tasks);
        else if (event === "file_start") startStreamingFile(data.filename);
        else if (event === "file_delta") appendToStreamingFile(data.filename, data.content);
        else if (event === "file") finalizeFile(data.filename, data.content);
        else if (event === "done") {
          addLog(`${data.message} Directory: ${data.workspace_dir}`, "done");
          if (launchButton) launchButton.classList.remove("d-none");
        } else if (event === "error") addLog(`Error: ${data.message}`, "error");
      }
    }
  }

  if (launchButton) {
    launchButton.addEventListener("click", async () => {
      const response = await fetch(`/generation/projects/${launchButton.dataset.launchProject}/launch`, {
        method: "POST",
      });
      const payload = await response.json();
      if (payload.url) {
        window.open(payload.url, "_blank", "noopener");
      } else {
        addLog(`Launch error: ${payload.error || "no URL"}`, "error");
      }
    });
  }

  button.addEventListener("click", async () => {
    if (!prompt.value.trim()) {
      addLog("Enter a program description before generating.", "error");
      return;
    }
    clearTimeline();
    if (launchButton) launchButton.classList.add("d-none");
    button.disabled = true;
    addLog("Generation started.", "log");
    const body = new URLSearchParams({ prompt: prompt.value });
    try {
      const response = await fetch(`/generation/projects/${button.dataset.generateProject}`, {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body,
      });
      await handleSse(response);
    } catch (error) {
      addLog(`Connection error: ${error.message}`, "error");
    } finally {
      button.disabled = false;
    }
  });

  loadInitialState();
}

setupAiSettings();
setupGeneration();
