const state = {
  files: [],
  currentFile: null,
  rows: [],
  filteredIndices: [],
  currentRowIndex: -1,
  baseHash: null,
  dirty: false,
  validationErrors: [],
};

const elements = {
  fileList: document.querySelector("#file-list"),
  rowList: document.querySelector("#row-list"),
  searchInput: document.querySelector("#search-input"),
  statusFilter: document.querySelector("#status-filter"),
  editorTitle: document.querySelector("#editor-title"),
  fileMeta: document.querySelector("#file-meta"),
  statusBanner: document.querySelector("#status-banner"),
  recordSummary: document.querySelector("#record-summary"),
  structuredForm: document.querySelector("#structured-form"),
  rawJsonEditor: document.querySelector("#raw-json-editor"),
  sourcePreview: document.querySelector("#source-preview"),
  validationResults: document.querySelector("#validation-results"),
  reviewerInput: document.querySelector("#reviewer-input"),
  showReadonlyToggle: document.querySelector("#show-readonly-toggle"),
};

document.querySelector("#reload-file-button").addEventListener("click", () => {
  if (state.currentFile) {
    loadFile(state.currentFile.path);
  }
});
document.querySelector("#validate-button").addEventListener("click", () => validateCurrentFile());
document.querySelector("#save-button").addEventListener("click", () => saveCurrentFile());
document.querySelector("#search-input").addEventListener("input", () => renderRows());
document.querySelector("#status-filter").addEventListener("change", () => renderRows());
document.querySelector("#show-readonly-toggle").addEventListener("change", () => loadFiles());
document.querySelector("#prev-row-button").addEventListener("click", () => moveRow(-1));
document.querySelector("#next-row-button").addEventListener("click", () => moveRow(1));
document.querySelector("#apply-json-button").addEventListener("click", applyRawJson);
document
  .querySelector("#mark-human-reviewed-button")
  .addEventListener("click", () => setReviewStatus("human_reviewed"));
document.querySelector("#mark-rejected-button").addEventListener("click", () => setReviewStatus("rejected"));
document.querySelector("#mark-promoted-button").addEventListener("click", () => setReviewStatus("promoted"));

loadFiles();

async function loadFiles() {
  const showReadOnly = elements.showReadonlyToggle.checked ? "1" : "0";
  const response = await fetch(`/api/files?all=${showReadOnly}`);
  const payload = await response.json();
  state.files = payload.files;
  renderFileList();
}

function renderFileList() {
  elements.fileList.innerHTML = "";
  if (!state.files.length) {
    elements.fileList.textContent = "Keine Dateien gefunden.";
    return;
  }

  let currentGroup = null;
  for (const file of state.files) {
    if (file.label !== currentGroup) {
      currentGroup = file.label;
      const group = document.createElement("div");
      group.className = "list-group-label";
      group.textContent = currentGroup;
      elements.fileList.appendChild(group);
    }

    const item = document.createElement("button");
    item.type = "button";
    item.className = `list-item ${state.currentFile?.path === file.path ? "active" : ""}`;
    item.innerHTML = `
      <strong>${escapeHtml(lastPathSegment(file.path))}</strong>
      <div class="meta-line">${escapeHtml(file.path)}</div>
      <div class="meta-line">${file.rows} rows · ${file.editable ? "editierbar" : "read-only"}</div>
    `;
    item.addEventListener("click", () => loadFile(file.path));
    elements.fileList.appendChild(item);
  }
}

async function loadFile(path) {
  const response = await fetch(`/api/file?path=${encodeURIComponent(path)}`);
  const payload = await response.json();
  state.currentFile = {
    path: payload.path,
    category: payload.category,
    editable: payload.editable,
    schema: payload.schema,
  };
  state.rows = payload.rows;
  state.baseHash = payload.hash;
  state.validationErrors = payload.validation_errors || [];
  state.dirty = false;
  state.currentRowIndex = payload.rows.length ? 0 : -1;
  renderFileList();
  renderRows();
  renderEditor();
  renderValidationResults(state.validationErrors);
}

function renderRows() {
  elements.rowList.innerHTML = "";
  if (!state.currentFile) {
    elements.rowList.textContent = "Datei wählen.";
    return;
  }

  const query = elements.searchInput.value.trim().toLowerCase();
  const status = elements.statusFilter.value;
  state.filteredIndices = [];

  state.rows.forEach((row, index) => {
    const haystack = JSON.stringify(buildSearchIndex(row)).toLowerCase();
    const matchesQuery = !query || haystack.includes(query);
    const rowStatus = row.review_status || row.meta?.review_status || "";
    const matchesStatus = !status || rowStatus === status;
    if (matchesQuery && matchesStatus) {
      state.filteredIndices.push(index);
    }
  });

  if (!state.filteredIndices.length) {
    elements.rowList.textContent = "Keine Rows für den aktuellen Filter.";
    state.currentRowIndex = -1;
    renderEditor();
    return;
  }

  if (!state.filteredIndices.includes(state.currentRowIndex)) {
    state.currentRowIndex = state.filteredIndices[0];
  }

  for (const index of state.filteredIndices) {
    const row = state.rows[index];
    const item = document.createElement("button");
    item.type = "button";
    item.className = `list-item ${index === state.currentRowIndex ? "active" : ""}`;
    item.innerHTML = `
      <strong>${escapeHtml(describeRow(row))}</strong>
      <div class="meta-line">${escapeHtml(row.review_status || row.meta?.review_status || "<none>")}</div>
      <div class="meta-line">${escapeHtml(describeSecondary(row))}</div>
    `;
    item.addEventListener("click", () => {
      state.currentRowIndex = index;
      renderRows();
      renderEditor();
    });
    elements.rowList.appendChild(item);
  }
}

function renderEditor() {
  const row = currentRow();
  if (!row) {
    elements.editorTitle.textContent = "Kein Datensatz gewählt";
    elements.fileMeta.textContent = state.currentFile ? state.currentFile.path : "";
    elements.recordSummary.innerHTML = "";
    elements.structuredForm.innerHTML = "";
    elements.rawJsonEditor.value = "";
    elements.sourcePreview.textContent = "Keine Provenance verfügbar.";
    updateStatusBanner();
    return;
  }

  elements.editorTitle.textContent = describeRow(row);
  elements.fileMeta.textContent = `${state.currentFile.path} · Row ${state.currentRowIndex + 1} von ${state.rows.length}`;
  elements.rawJsonEditor.value = JSON.stringify(row, null, 2);

  renderSummary(row);
  renderStructuredForm(row);
  updateStatusBanner();
  loadSourcePreview(row);
}

function renderSummary(row) {
  const cards = [];
  cards.push(summaryCard("Status", row.review_status || row.meta?.review_status || "<none>"));
  cards.push(summaryCard("ID", describeRow(row)));
  if (row.record_type) {
    cards.push(summaryCard("Record Type", row.record_type));
  }
  if (row.target_split || row.split) {
    cards.push(summaryCard("Split", row.target_split || row.split));
  }
  if (row.task_type || row.case_type) {
    cards.push(summaryCard("Task", row.task_type || row.case_type));
  }
  if (row.teacher_model) {
    cards.push(summaryCard("Teacher", row.teacher_model));
  }
  if (row.approved_by || row.meta?.approved_by) {
    cards.push(summaryCard("Approved By", row.approved_by || row.meta?.approved_by));
  }
  elements.recordSummary.innerHTML = cards.join("");
}

function renderStructuredForm(row) {
  elements.structuredForm.innerHTML = "";
  const descriptor = buildFormDescriptor(row);
  if (!descriptor.length) {
    elements.structuredForm.innerHTML = `<div class="field-group">Für diesen Typ gibt es noch keinen strukturierten Editor. Nutze Roh-JSON.</div>`;
    return;
  }

  for (const field of descriptor) {
    const group = document.createElement("div");
    group.className = "field-group";

    const label = document.createElement("label");
    label.textContent = field.label;
    group.appendChild(label);

    const control = field.multiline ? document.createElement("textarea") : document.createElement("input");
    if (!field.multiline) {
      control.type = "text";
    }
    control.value = getByPath(row, field.path) ?? "";
    control.placeholder = field.placeholder || "";
    control.addEventListener("input", (event) => {
      setByPath(row, field.path, event.target.value, field.asList === true);
      refreshRawJson();
      markDirty();
    });
    group.appendChild(control);

    elements.structuredForm.appendChild(group);
  }
}

function buildFormDescriptor(row) {
  if (row.output_id && row.candidate) {
    return buildFormDescriptor(row.candidate);
  }
  if (row.messages && row.meta) {
    return [
      { path: "messages.0.content", label: "System", multiline: true },
      { path: "messages.1.content", label: "User", multiline: true },
      { path: "messages.2.content", label: "Assistant", multiline: true },
    ];
  }
  if (row.prompt && row.expected_behavior) {
    return [
      { path: "prompt", label: "Prompt", multiline: true },
      { path: "expected_behavior", label: "Expected Behavior", multiline: true },
      { path: "reference_answer", label: "Reference Answer", multiline: true },
      { path: "case_description", label: "Case Description", multiline: true },
      { path: "rubric.style", label: "Rubric Style", multiline: true },
      { path: "rubric.must_include", label: "Must Include", multiline: true, asList: true, placeholder: "Ein Eintrag pro Zeile" },
      { path: "rubric.must_not_include", label: "Must Not Include", multiline: true, asList: true, placeholder: "Ein Eintrag pro Zeile" },
    ];
  }
  return [];
}

async function loadSourcePreview(row) {
  const source = firstSourceSpan(row);
  if (!source) {
    elements.sourcePreview.textContent = "Keine Provenance verfügbar.";
    return;
  }

  const response = await fetch(
    `/api/source?path=${encodeURIComponent(source.path)}&start=${source.start}&end=${source.end}&context=2`
  );
  const payload = await response.json();
  elements.sourcePreview.innerHTML = `
    <div class="meta-line">${escapeHtml(payload.path)} · Zeilen ${payload.start}-${payload.end}</div>
    ${payload.lines
      .map(
        (line) => `
          <div class="source-line ${line.number >= payload.start && line.number <= payload.end ? "highlight" : ""}">
            ${String(line.number).padStart(4, " ")}  ${escapeHtml(line.text)}
          </div>
        `
      )
      .join("")}
  `;
}

async function validateCurrentFile() {
  if (!state.currentFile) {
    return;
  }
  const response = await fetch("/api/validate", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ path: state.currentFile.path, rows: state.rows }),
  });
  const payload = await response.json();
  state.validationErrors = payload.errors || [];
  renderValidationResults(state.validationErrors);
  updateStatusBanner(payload.ok ? "Validierung erfolgreich." : "Validierung fehlgeschlagen.", payload.ok ? "" : "warning");
}

async function saveCurrentFile() {
  if (!state.currentFile) {
    return;
  }
  const isGold = state.currentFile.category.startsWith("gold");
  let allowGoldWrite = false;
  if (isGold) {
    allowGoldWrite = window.confirm(
      "Du speicherst in data/gold/. Das ist Source of Truth. Wirklich fortfahren?"
    );
    if (!allowGoldWrite) {
      return;
    }
  }

  const response = await fetch("/api/save", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      path: state.currentFile.path,
      rows: state.rows,
      base_hash: state.baseHash,
      allow_gold_write: allowGoldWrite,
    }),
  });
  const payload = await response.json();
  if (!response.ok || !payload.ok) {
    renderValidationResults(payload.errors || ["Speichern fehlgeschlagen."]);
    updateStatusBanner("Speichern fehlgeschlagen.", "warning");
    return;
  }
  state.baseHash = payload.hash;
  state.dirty = false;
  updateStatusBanner("Datei gespeichert.");
}

function setReviewStatus(status) {
  const row = currentRow();
  if (!row) {
    return;
  }
  const reviewer = requireReviewer();
  if (!reviewer) {
    return;
  }

  row.review_status = status;
  row.approved_by = reviewer;

  if (row.candidate && typeof row.candidate === "object") {
    row.candidate.review_status = status;
    row.candidate.approved_by = reviewer;
    if (row.candidate.meta) {
      row.candidate.meta.review_status = status;
      row.candidate.meta.approved_by = reviewer;
    }
  }

  if (row.meta) {
    row.meta.review_status = status;
    row.meta.approved_by = reviewer;
  }

  refreshRawJson();
  markDirty();
  renderRows();
  renderSummary(row);
}

function applyRawJson() {
  const index = state.currentRowIndex;
  if (index < 0) {
    return;
  }
  try {
    const parsed = JSON.parse(elements.rawJsonEditor.value);
    state.rows[index] = parsed;
    markDirty();
    renderRows();
    renderEditor();
  } catch (error) {
    updateStatusBanner(`JSON ungültig: ${error.message}`, "warning");
  }
}

function moveRow(offset) {
  if (!state.filteredIndices.length) {
    return;
  }
  const currentPos = state.filteredIndices.indexOf(state.currentRowIndex);
  const nextPos = Math.max(0, Math.min(state.filteredIndices.length - 1, currentPos + offset));
  state.currentRowIndex = state.filteredIndices[nextPos];
  renderRows();
  renderEditor();
}

function renderValidationResults(errors) {
  if (!errors.length) {
    elements.validationResults.innerHTML = `<div>Keine Fehler.</div>`;
    return;
  }
  elements.validationResults.innerHTML = `<ul>${errors
    .map((error) => `<li>${escapeHtml(error)}</li>`)
    .join("")}</ul>`;
}

function updateStatusBanner(message = null, kind = "") {
  const parts = [];
  if (message) {
    parts.push(message);
  }
  if (state.currentFile) {
    parts.push(`${state.currentFile.path} · ${state.rows.length} rows`);
  }
  if (state.dirty) {
    parts.push("Ungespeicherte Änderungen");
  }
  elements.statusBanner.textContent = parts.join(" · ") || "Keine Datei geladen.";
  elements.statusBanner.className = `status-banner ${kind || (state.dirty ? "dirty" : "")}`.trim();
}

function currentRow() {
  if (state.currentRowIndex < 0) {
    return null;
  }
  return state.rows[state.currentRowIndex];
}

function refreshRawJson() {
  const row = currentRow();
  if (row) {
    elements.rawJsonEditor.value = JSON.stringify(row, null, 2);
  }
}

function markDirty() {
  state.dirty = true;
  updateStatusBanner();
}

function requireReviewer() {
  const value = elements.reviewerInput.value.trim();
  if (!value) {
    updateStatusBanner("Reviewer ist erforderlich, um einen Status zu setzen.", "warning");
    return "";
  }
  return value;
}

function describeRow(row) {
  return row.output_id || row.id || row.eval_id || row.chunk_id || row.task_card_id || "<unknown>";
}

function describeSecondary(row) {
  return row.task_type || row.case_type || row.record_type || row.section_title || "";
}

function buildSearchIndex(row) {
  return {
    id: describeRow(row),
    status: row.review_status || row.meta?.review_status || "",
    secondary: describeSecondary(row),
    chunks: row.source_chunk_ids || row.meta?.source_chunk_ids || [],
    docs: row.source_doc_ids || row.meta?.source_doc_ids || [],
    prompt: row.prompt || row.candidate?.prompt || "",
    assistant:
      row.messages?.[2]?.content ||
      row.candidate?.messages?.[2]?.content ||
      row.reference_answer ||
      row.candidate?.reference_answer ||
      "",
  };
}

function firstSourceSpan(row) {
  const provenance = row.provenance || row.candidate?.provenance;
  if (!provenance?.source_records?.length) {
    return null;
  }
  const record = provenance.source_records[0];
  const rawSpan = record.source_spans?.[0];
  if (typeof rawSpan === "string") {
    const match = rawSpan.match(/^(.*)#L(\d+)(?:-L?(\d+))?$/);
    if (match) {
      return {
        path: match[1],
        start: Number(match[2]),
        end: Number(match[3] || match[2]),
      };
    }
  }
  return record.normalized_path ? { path: record.normalized_path, start: 1, end: 20 } : null;
}

function summaryCard(label, value) {
  return `<div class="summary-card"><strong>${escapeHtml(label)}</strong><div class="meta-line">${escapeHtml(String(value || ""))}</div></div>`;
}

function getByPath(root, path) {
  const parts = path.split(".");
  let current = root;
  for (const part of parts) {
    if (current == null) {
      return "";
    }
    if (Array.isArray(current)) {
      current = current[Number(part)];
    } else {
      current = current[part];
    }
  }
  if (Array.isArray(current)) {
    return current.join("\n");
  }
  return current ?? "";
}

function setByPath(root, path, value, asList = false) {
  const parts = path.split(".");
  let current = root;
  for (let i = 0; i < parts.length - 1; i += 1) {
    const part = parts[i];
    if (Array.isArray(current)) {
      current = current[Number(part)];
    } else {
      current = current[part];
    }
  }
  const last = parts[parts.length - 1];
  const normalizedValue = asList ? splitLines(value) : value;
  if (Array.isArray(current)) {
    current[Number(last)] = normalizedValue;
  } else {
    current[last] = normalizedValue;
  }
}

function splitLines(value) {
  return value
    .split(/\r?\n/)
    .map((entry) => entry.trim())
    .filter(Boolean);
}

function lastPathSegment(path) {
  return path.split("/").at(-1);
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}
