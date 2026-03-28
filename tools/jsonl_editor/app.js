const state = {
  files: [],
  currentFile: null,
  rows: [],
  originalRows: [],
  filteredIndices: [],
  currentRowIndex: -1,
  baseHash: null,
  review: null,
  promotion: null,
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
  reviewPanel: document.querySelector("#review-panel"),
  reviewOutputPath: document.querySelector("#review-output-path"),
  reviewSummary: document.querySelector("#review-summary"),
  promotionPanel: document.querySelector("#promotion-panel"),
  promotionTrainOutputPath: document.querySelector("#promotion-train-output-path"),
  promotionEvalOutputPath: document.querySelector("#promotion-eval-output-path"),
  promotionSummary: document.querySelector("#promotion-summary"),
  diffPanel: document.querySelector("#diff-panel"),
  diffView: document.querySelector("#diff-view"),
  recordSummary: document.querySelector("#record-summary"),
  structuredForm: document.querySelector("#structured-form"),
  rawJsonEditor: document.querySelector("#raw-json-editor"),
  sourcePreview: document.querySelector("#source-preview"),
  validationResults: document.querySelector("#validation-results"),
  reviewerInput: document.querySelector("#reviewer-input"),
  showReadonlyToggle: document.querySelector("#show-readonly-toggle"),
  changedOnlyToggle: document.querySelector("#changed-only-toggle"),
};

document.querySelector("#reload-file-button").addEventListener("click", () => {
  if (state.currentFile) {
    loadFile(state.currentFile.path);
  }
});
document.querySelector("#save-reviewed-button").addEventListener("click", () => saveReviewedFile());
document.querySelector("#load-reviewed-button").addEventListener("click", () => loadExistingReviewedOverlay());
document.querySelector("#promote-gold-button").addEventListener("click", () => promoteToGold());
document.querySelector("#validate-button").addEventListener("click", () => validateCurrentFile());
document.querySelector("#save-button").addEventListener("click", () => saveCurrentFile());
document.querySelector("#search-input").addEventListener("input", () => renderRows());
document.querySelector("#status-filter").addEventListener("change", () => renderRows());
document.querySelector("#show-readonly-toggle").addEventListener("change", () => loadFiles());
document.querySelector("#changed-only-toggle").addEventListener("change", () => renderRows());
document.querySelector("#prev-row-button").addEventListener("click", () => moveRow(-1));
document.querySelector("#next-row-button").addEventListener("click", () => moveRow(1));
document.querySelector("#apply-json-button").addEventListener("click", applyRawJson);
document.querySelector("#approve-next-button").addEventListener("click", () => reviewAndAdvance("human_reviewed"));
document.querySelector("#reject-next-button").addEventListener("click", () => reviewAndAdvance("rejected"));
document.querySelector("#pending-filter-button").addEventListener("click", () => {
  elements.statusFilter.value = "teacher_generated";
  renderRows();
});
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
      <div class="meta-line">${file.rows} rows | ${file.editable ? "editierbar" : "read-only"}</div>
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
  state.originalRows = deepCopyRows(payload.rows);
  state.baseHash = payload.hash;
  state.review = payload.review || null;
  state.promotion = payload.promotion || null;
  state.validationErrors = payload.validation_errors || [];
  state.dirty = false;
  state.currentRowIndex = payload.rows.length ? 0 : -1;
  elements.statusFilter.value = state.review?.default_status_filter || "";
  renderFileList();
  renderRows();
  renderEditor();
  renderReviewPanel();
  renderPromotionPanel();
  renderValidationResults(state.validationErrors);
}

function renderRows() {
  elements.rowList.innerHTML = "";
  if (!state.currentFile) {
    elements.rowList.textContent = "Datei waehlen.";
    return;
  }

  const query = elements.searchInput.value.trim().toLowerCase();
  const status = elements.statusFilter.value;
  const changedOnly = elements.changedOnlyToggle.checked;
  state.filteredIndices = [];

  state.rows.forEach((row, index) => {
    const haystack = JSON.stringify(buildSearchIndex(row)).toLowerCase();
    const matchesQuery = !query || haystack.includes(query);
    const rowStatus = row.review_status || row.meta?.review_status || "";
    const matchesStatus = !status || rowStatus === status;
    const matchesChangedOnly = !changedOnly || hasRowChanged(index);
    if (matchesQuery && matchesStatus && matchesChangedOnly) {
      state.filteredIndices.push(index);
    }
  });

  if (!state.filteredIndices.length) {
    elements.rowList.textContent = "Keine Rows fuer den aktuellen Filter.";
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
      <div class="meta-line">${escapeHtml(describeSecondary(row))}${hasRowChanged(index) ? " | geaendert" : ""}</div>
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
    elements.editorTitle.textContent = "Kein Datensatz gewaehlt";
    elements.fileMeta.textContent = state.currentFile ? state.currentFile.path : "";
    elements.recordSummary.innerHTML = "";
    elements.structuredForm.innerHTML = "";
    elements.diffView.textContent = "Keine Unterschiede.";
    elements.diffPanel.classList.add("hidden");
    elements.rawJsonEditor.value = "";
    elements.sourcePreview.textContent = "Keine Provenance verfuegbar.";
    renderReviewPanel();
    renderPromotionPanel();
    updateStatusBanner();
    return;
  }

  elements.editorTitle.textContent = describeRow(row);
  elements.fileMeta.textContent = `${state.currentFile.path} | Row ${state.currentRowIndex + 1} von ${state.rows.length}`;
  elements.rawJsonEditor.value = JSON.stringify(row, null, 2);

  renderSummary(row);
  renderStructuredForm(row);
  renderDiffPanel();
  renderReviewPanel();
  renderPromotionPanel();
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
    elements.structuredForm.innerHTML =
      '<div class="field-group">Fuer diesen Typ gibt es noch keinen strukturierten Editor. Nutze Roh-JSON.</div>';
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
      {
        path: "rubric.must_include",
        label: "Must Include",
        multiline: true,
        asList: true,
        placeholder: "Ein Eintrag pro Zeile",
      },
      {
        path: "rubric.must_not_include",
        label: "Must Not Include",
        multiline: true,
        asList: true,
        placeholder: "Ein Eintrag pro Zeile",
      },
    ];
  }
  return [];
}

async function loadSourcePreview(row) {
  const source = firstSourceSpan(row);
  if (!source) {
    elements.sourcePreview.textContent = "Keine Provenance verfuegbar.";
    return;
  }

  const response = await fetch(
    `/api/source?path=${encodeURIComponent(source.path)}&start=${source.start}&end=${source.end}&context=2`
  );
  const payload = await response.json();
  elements.sourcePreview.innerHTML = `
    <div class="meta-line">${escapeHtml(payload.path)} | Zeilen ${payload.start}-${payload.end}</div>
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
  const payload = await postJson("/api/validate", { path: state.currentFile.path, rows: state.rows });
  state.validationErrors = payload.body.errors || [];
  renderValidationResults(state.validationErrors);
  updateStatusBanner(
    payload.body.ok ? "Validierung erfolgreich." : "Validierung fehlgeschlagen.",
    payload.body.ok ? "" : "warning"
  );
}

async function saveCurrentFile() {
  if (!state.currentFile) {
    return;
  }
  if (state.currentFile.category === "teacher_outputs") {
    const proceed = window.confirm(
      "Das schreibt direkt in die rohe teacher_outputs-Datei. Normalerweise solltest du stattdessen 'Review-Datei schreiben' verwenden. Trotzdem fortfahren?"
    );
    if (!proceed) {
      return;
    }
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

  const payload = await postJson("/api/save", {
    path: state.currentFile.path,
    rows: state.rows,
    base_hash: state.baseHash,
    allow_gold_write: allowGoldWrite,
  });
  if (!payload.ok || !payload.body.ok) {
    renderValidationResults(payload.body.errors || ["Speichern fehlgeschlagen."]);
    updateStatusBanner("Speichern fehlgeschlagen.", "warning");
    return;
  }
  state.baseHash = payload.body.hash;
  state.dirty = false;
  updateStatusBanner("Datei gespeichert.");
}

async function saveReviewedFile(overwriteOutput = false) {
  if (!state.currentFile || !state.review) {
    return;
  }

  const outputPath = elements.reviewOutputPath.value.trim();
  if (!outputPath) {
    updateStatusBanner("Reviewed output path ist erforderlich.", "warning");
    return;
  }

  const reviewer = requireReviewer();
  if (!reviewer) {
    return;
  }

  const payload = await postJson("/api/save-reviewed", {
    path: state.currentFile.path,
    output_path: outputPath,
    rows: state.rows,
    base_hash: state.baseHash,
    overwrite_output: overwriteOutput,
  });

  if (payload.status === 409 && payload.body.errors?.length && !overwriteOutput) {
    const overwrite = window.confirm(
      `${payload.body.errors[0]}\n\nBestehende Review-Datei ueberschreiben?`
    );
    if (overwrite) {
      await saveReviewedFile(true);
      return;
    }
    updateStatusBanner("Review-Export abgebrochen.", "warning");
    return;
  }

  if (!payload.ok || !payload.body.ok) {
    renderValidationResults(payload.body.errors || ["Review-Export fehlgeschlagen."]);
    updateStatusBanner("Review-Export fehlgeschlagen.", "warning");
    return;
  }

  if (payload.body.output_path === state.currentFile.path) {
    state.baseHash = payload.body.hash;
    state.dirty = false;
  }
  updateStatusBanner(`Review-Datei geschrieben: ${payload.body.output_path}`);
}

async function loadExistingReviewedOverlay() {
  if (!state.currentFile || !state.review?.existing_output_exists || !state.review.existing_output_path) {
    updateStatusBanner("Kein vorhandener reviewed-Stand gefunden.", "warning");
    return;
  }

  const response = await fetch(
    `/api/review-overlay?source_path=${encodeURIComponent(state.currentFile.path)}&reviewed_path=${encodeURIComponent(state.review.existing_output_path)}`
  );
  const payload = await response.json();
  state.rows = payload.rows;
  state.dirty = payload.merge_summary.merged_count > 0;
  state.review.existing_merge_summary = payload.merge_summary;
  const mergeNote =
    payload.merge_summary.conflict_count > 0
      ? ` Konflikte: ${payload.merge_summary.conflict_count}.`
      : payload.merge_summary.missing_count > 0 || payload.merge_summary.extra_count > 0
        ? ` Fehlende/extra IDs: ${payload.merge_summary.missing_count}/${payload.merge_summary.extra_count}.`
        : "";
  updateStatusBanner(
    payload.merge_summary.merged_count > 0
      ? `Vorhandener Review-Stand geladen: ${payload.merge_summary.merged_count} Rows uebernommen.${mergeNote}`
      : "Vorhandener Review-Stand brachte keine abweichenden Rows.",
    payload.merge_summary.merged_count > 0 ? "dirty" : ""
  );
  renderRows();
  renderEditor();
  renderReviewPanel();
  renderPromotionPanel();
}

async function promoteToGold(overwriteOutputs = false) {
  if (!state.currentFile || !state.promotion) {
    return;
  }

  const trainOutputPath = elements.promotionTrainOutputPath.value.trim();
  const evalOutputPath = elements.promotionEvalOutputPath.value.trim();
  if (!trainOutputPath || !evalOutputPath) {
    updateStatusBanner("Train- und Eval-Output-Pfade sind erforderlich.", "warning");
    return;
  }

  const payload = await postJson("/api/promote-gold", {
    path: state.currentFile.path,
    rows: state.rows,
    train_output_path: trainOutputPath,
    eval_output_path: evalOutputPath,
    overwrite_outputs: overwriteOutputs,
  });

  if (payload.status === 409 && payload.body.errors?.length && !overwriteOutputs) {
    const overwrite = window.confirm(
      `${payload.body.errors[0]}\n\nBestehende Gold-Dateien ueberschreiben?`
    );
    if (overwrite) {
      await promoteToGold(true);
      return;
    }
    updateStatusBanner("Promotion abgebrochen.", "warning");
    return;
  }

  if (!payload.ok || !payload.body.ok) {
    renderValidationResults(payload.body.errors || ["Promotion fehlgeschlagen."]);
    updateStatusBanner("Promotion fehlgeschlagen.", "warning");
    return;
  }

  const checkMessages = (payload.body.checks || []).flatMap((check) =>
    check.messages.map((message) => `${check.path}: ${message}`)
  );
  renderValidationResults([], checkMessages);
  updateStatusBanner(
    `Gold-Dateien geschrieben: train=${payload.body.train_count}, eval=${payload.body.eval_count}`
  );
}

function setReviewStatus(status, options = {}) {
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
  if (options.render !== false) {
    renderRows();
    renderSummary(row);
    renderReviewPanel();
    renderPromotionPanel();
  }
}

function reviewAndAdvance(status) {
  if (!state.review || !state.filteredIndices.length) {
    return;
  }
  const currentPos = state.filteredIndices.indexOf(state.currentRowIndex);
  setReviewStatus(status, { render: false });
  renderRows();
  if (state.filteredIndices.length) {
    const nextPos = Math.max(0, Math.min(state.filteredIndices.length - 1, currentPos));
    state.currentRowIndex = state.filteredIndices[nextPos];
  }
  renderRows();
  renderEditor();
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
    updateStatusBanner(`JSON ungueltig: ${error.message}`, "warning");
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

function renderValidationResults(errors, messages = []) {
  if (!errors.length && !messages.length) {
    elements.validationResults.innerHTML = "<div>Keine Fehler.</div>";
    return;
  }
  const entries = [...errors, ...messages];
  elements.validationResults.innerHTML = `<ul>${entries
    .map((entry) => `<li>${escapeHtml(entry)}</li>`)
    .join("")}</ul>`;
}

function renderReviewPanel() {
  if (!state.review || !state.currentFile) {
    elements.reviewPanel.classList.add("hidden");
    elements.reviewSummary.innerHTML = "";
    return;
  }

  elements.reviewPanel.classList.remove("hidden");
  document.querySelector("#load-reviewed-button").disabled = !state.review.existing_output_exists;
  if (
    !elements.reviewOutputPath.dataset.boundPath ||
    elements.reviewOutputPath.dataset.boundPath !== state.currentFile.path
  ) {
    elements.reviewOutputPath.value = state.review.suggested_output_path;
    elements.reviewOutputPath.dataset.boundPath = state.currentFile.path;
  }

  const summary = computeReviewSummary();
  elements.reviewSummary.innerHTML = [
    summaryCard("Pending", summary.pendingCount),
    summaryCard("Decided", summary.decidedCount),
    summaryCard("Reviewed", summary.statusCounts.human_reviewed || 0),
    summaryCard("Rejected", summary.statusCounts.rejected || 0),
    summaryCard("Existing Review", state.review.existing_output_exists ? "ja" : "nein"),
    summaryCard("Mergeable", state.review.existing_merge_summary?.mergeable_count || 0),
    summaryCard("Conflicts", state.review.existing_merge_summary?.conflict_count || 0),
  ].join("");
}

function renderPromotionPanel() {
  if (!state.promotion || !state.currentFile) {
    elements.promotionPanel.classList.add("hidden");
    elements.promotionSummary.innerHTML = "";
    return;
  }

  elements.promotionPanel.classList.remove("hidden");
  if (
    !elements.promotionTrainOutputPath.dataset.boundPath ||
    elements.promotionTrainOutputPath.dataset.boundPath !== state.currentFile.path
  ) {
    elements.promotionTrainOutputPath.value = state.promotion.train_output_path;
    elements.promotionTrainOutputPath.dataset.boundPath = state.currentFile.path;
  }
  if (
    !elements.promotionEvalOutputPath.dataset.boundPath ||
    elements.promotionEvalOutputPath.dataset.boundPath !== state.currentFile.path
  ) {
    elements.promotionEvalOutputPath.value = state.promotion.eval_output_path;
    elements.promotionEvalOutputPath.dataset.boundPath = state.currentFile.path;
  }

  const summary = computePromotionSummary();
  elements.promotionSummary.innerHTML = [
    summaryCard("Eligible", summary.eligibleCount),
    summaryCard("Train", summary.trainCount),
    summaryCard("Eval", summary.evalCount),
  ].join("");
}

function renderDiffPanel() {
  const row = currentRow();
  if (!row || !state.originalRows.length) {
    elements.diffPanel.classList.add("hidden");
    elements.diffView.textContent = "Keine Unterschiede.";
    return;
  }

  const originalRow = state.originalRows[state.currentRowIndex];
  const fields = comparableFields(row, originalRow);
  const changedFields = fields.filter((field) => field.before !== field.after);

  if (!changedFields.length) {
    elements.diffPanel.classList.add("hidden");
    elements.diffView.textContent = "Keine Unterschiede.";
    return;
  }

  elements.diffPanel.classList.remove("hidden");
  elements.diffView.classList.remove("muted");
  elements.diffView.innerHTML = changedFields
    .map(
      (field) => `
        <div class="diff-card changed">
          <strong>${escapeHtml(field.label)}</strong>
          <div class="diff-columns">
            <div>
              <div class="meta-line">Original</div>
              <pre>${escapeHtml(field.before)}</pre>
            </div>
            <div>
              <div class="meta-line">Aktuell</div>
              <pre>${escapeHtml(field.after)}</pre>
            </div>
          </div>
        </div>
      `
    )
    .join("");
}

function updateStatusBanner(message = null, kind = "") {
  const parts = [];
  if (message) {
    parts.push(message);
  }
  if (state.currentFile) {
    parts.push(`${state.currentFile.path} | ${state.rows.length} rows`);
  }
  if (state.dirty) {
    parts.push("Ungespeicherte Aenderungen");
  }
  elements.statusBanner.textContent = parts.join(" | ") || "Keine Datei geladen.";
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
  renderReviewPanel();
  renderPromotionPanel();
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

function computeReviewSummary() {
  const counts = {};
  for (const row of state.rows) {
    const status = row.review_status || "<none>";
    counts[status] = (counts[status] || 0) + 1;
  }
  return {
    statusCounts: counts,
    pendingCount: (counts.draft || 0) + (counts.seed || 0) + (counts.teacher_generated || 0),
    decidedCount: (counts.human_reviewed || 0) + (counts.rejected || 0),
  };
}

function computePromotionSummary() {
  const humanReviewed = state.rows.filter((row) => row.review_status === "human_reviewed");
  return {
    eligibleCount: humanReviewed.length,
    trainCount: humanReviewed.filter((row) => row.record_type === "sft_sample").length,
    evalCount: humanReviewed.filter((row) => row.record_type === "eval_case").length,
  };
}

function hasRowChanged(index) {
  return JSON.stringify(state.rows[index]) !== JSON.stringify(state.originalRows[index]);
}

function comparableFields(currentRowValue, originalRowValue) {
  const currentShape = comparableShape(currentRowValue);
  const originalShape = comparableShape(originalRowValue);
  return currentShape.map((field, index) => ({
    label: field.label,
    before: stringifyComparableValue(originalShape[index]?.value),
    after: stringifyComparableValue(field.value),
  }));
}

function comparableShape(row) {
  if (!row) {
    return [];
  }
  if (row.output_id && row.candidate) {
    return comparableShape(row.candidate);
  }
  if (row.messages && row.meta) {
    return [
      { label: "System", value: row.messages?.[0]?.content || "" },
      { label: "User", value: row.messages?.[1]?.content || "" },
      { label: "Assistant", value: row.messages?.[2]?.content || "" },
    ];
  }
  if (row.prompt && row.expected_behavior) {
    return [
      { label: "Prompt", value: row.prompt || "" },
      { label: "Expected Behavior", value: row.expected_behavior || "" },
      { label: "Reference Answer", value: row.reference_answer || "" },
      { label: "Case Description", value: row.case_description || "" },
      { label: "Must Include", value: row.rubric?.must_include || [] },
      { label: "Must Not Include", value: row.rubric?.must_not_include || [] },
    ];
  }
  return [{ label: "JSON", value: row }];
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

function stringifyComparableValue(value) {
  if (Array.isArray(value)) {
    return value.join("\n");
  }
  if (value && typeof value === "object") {
    return JSON.stringify(value, null, 2);
  }
  return String(value || "");
}

function deepCopyRows(rows) {
  return JSON.parse(JSON.stringify(rows));
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

async function postJson(url, body) {
  const response = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  const payload = await response.json();
  return { ok: response.ok, status: response.status, body: payload };
}
