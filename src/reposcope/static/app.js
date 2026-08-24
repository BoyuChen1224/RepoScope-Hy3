const form = document.querySelector("#analysisForm");
const runButton = document.querySelector("#runButton");
const demoButton = document.querySelector("#demoButton");
const emptyState = document.querySelector("#emptyState");
const results = document.querySelector("#results");
const toast = document.querySelector("#toast");
const generateButton = document.querySelector("#generateButton");
let activeManifest = null;
let activeReport = null;

function notify(message) {
  toast.textContent = message;
  toast.classList.add("show");
  window.setTimeout(() => toast.classList.remove("show"), 4200);
}

function escapeHtml(value) {
  return String(value).replace(/[&<>'"]/g, character => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", "'": "&#39;", '"': "&quot;",
  })[character]);
}

function shortRepo(url) {
  try { return new URL(url).pathname.replace(/^\//, "").replace(/\.git$/, ""); }
  catch { return url; }
}

function signal(label, value, present = true) {
  return `<div class="signal ${present ? "" : "missing"}"><strong>${value}</strong><span>${label}</span></div>`;
}

function renderManifest(manifest, score = null) {
  activeManifest = manifest;
  activeReport = null;
  emptyState.classList.add("hidden");
  results.classList.remove("hidden");
  document.querySelector("#resultRepo").textContent = shortRepo(manifest.source_url);
  document.querySelector("#resultSha").textContent = manifest.commit_sha.slice(0, 12);
  const calculated = score ?? Math.min(96, 48 + Object.values(manifest.signals).filter(v => v === true).length * 8);
  document.querySelector("#resultScore").textContent = calculated;
  document.querySelector(".score-ring").style.setProperty("--score", calculated);

  const s = manifest.signals;
  document.querySelector("#signalGrid").innerHTML = [
    signal("README", s.has_readme ? "FOUND" : "MISS", s.has_readme),
    signal("LICENSE", s.has_license ? "FOUND" : "MISS", s.has_license),
    signal("TESTS", s.has_tests ? "FOUND" : "MISS", s.has_tests),
    signal("CI", s.has_ci ? "FOUND" : "MISS", s.has_ci),
    signal("FILES", String(manifest.file_count), true),
  ].join("");

  const docs = manifest.documents.slice(0, 12);
  document.querySelector("#evidenceCount").textContent = `${manifest.documents.length} 份已采集文档`;
  document.querySelector("#evidenceList").innerHTML = docs.map(doc =>
    `<div class="evidence-item"><code>${escapeHtml(doc.path)}</code><span>${Number(doc.line_count)} lines</span></div>`
  ).join("");
  const warning = manifest.warnings.length
    ? manifest.warnings.join(" ")
    : "快照基础检查未发现缺失的核心项目元数据；语义结论仍需生成报告后评估。";
  document.querySelector("#resultCallout").textContent = warning;
  document.querySelector("#reportView").classList.add("hidden");
  document.querySelector("#scoreBreakdown").classList.add("hidden");
  generateButton.classList.remove("hidden");
}

function evidenceLabel(item) {
  const ref = item.evidence?.[0];
  return ref ? `${ref.path}:${Number(ref.line_start)}-${Number(ref.line_end)}` : "NO EVIDENCE";
}

function renderReport(report) {
  activeReport = report;
  const view = document.querySelector("#reportView");
  view.classList.remove("hidden");
  document.querySelector("#reportDecision").textContent = report.decision.replaceAll("_", " ");
  document.querySelector("#reportSummary").textContent = report.executive_summary;
  document.querySelector("#claimCount").textContent = `${report.claims.length} 条`;
  document.querySelector("#claimList").innerHTML = report.claims.slice(0, 5).map(claim =>
    `<article class="report-card"><strong>${escapeHtml(claim.id)} · ${escapeHtml(claim.category)}</strong><p>${escapeHtml(claim.text)}</p><code>${escapeHtml(evidenceLabel(claim))}</code></article>`
  ).join("");
  const risks = [...report.risks, ...(report.unknowns || []).map((text, index) => ({
    id: `U${String(index + 1).padStart(3, "0")}`, severity: "unknown", title: "待确认", description: text, evidence: [],
  }))];
  document.querySelector("#riskCount").textContent = `${risks.length} 项`;
  document.querySelector("#riskList").innerHTML = risks.slice(0, 6).map(risk =>
    `<article class="report-card risk-${escapeHtml(risk.severity)}"><strong>${escapeHtml(risk.id)} · ${escapeHtml(risk.title)}</strong><p>${escapeHtml(risk.description)}</p><code>${escapeHtml(evidenceLabel(risk))}</code></article>`
  ).join("");
  view.scrollIntoView({behavior: "smooth", block: "nearest"});
}

function renderEvaluation(evaluation) {
  document.querySelector("#scoreBreakdown").classList.remove("hidden");
  document.querySelector("#gradeLabel").textContent = `Grade ${evaluation.grade}`;
  document.querySelector("#dimensionList").innerHTML = evaluation.dimensions.map(item =>
    `<div class="dimension-row"><span>${escapeHtml(item.label)}</span><div class="dimension-bar"><i style="width:${Math.max(0, Math.min(100, Number(item.score) / 4 * 100))}%"></i></div><strong>${Number(item.score).toFixed(1)}</strong></div>`
  ).join("");
  document.querySelector("#resultScore").textContent = Math.round(evaluation.total_score);
  document.querySelector(".score-ring").style.setProperty("--score", evaluation.total_score);
  if (evaluation.hard_failures.length) {
    document.querySelector("#resultCallout").textContent = `硬门槛触发：${evaluation.hard_failures.join(" ")}`;
  }
}

async function checkHealth() {
  try {
    const response = await fetch("/api/health");
    if (!response.ok) throw new Error();
    document.querySelector("#apiStatus").textContent = "评估器在线";
    document.querySelector(".status-dot").classList.add("ok");
  } catch {
    document.querySelector("#apiStatus").textContent = "评估器离线";
  }
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  runButton.disabled = true;
  runButton.querySelector("span").textContent = "正在固定仓库快照…";
  try {
    const response = await fetch("/api/repositories/inspect", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        repository_url: document.querySelector("#repoUrl").value,
        goal: document.querySelector("#goal").value,
      }),
    });
    const payload = await response.json();
    if (!response.ok) throw new Error(payload.detail || "仓库检查失败");
    renderManifest(payload);
    notify("仓库快照已固定。下一步可调用 Hy3 生成尽调报告。");
  } catch (error) {
    notify(error.message);
  } finally {
    runButton.disabled = false;
    runButton.querySelector("span").textContent = "开始证据审查";
  }
});

demoButton.addEventListener("click", () => {
  const manifest = {
    source_url: "https://github.com/example/evidence-ledger",
    commit_sha: "f71a9e0128da54b49e45b63572b7b366a0b9f1c3",
    file_count: 147,
    total_size_bytes: 928441,
    signals: {has_readme: true, has_license: true, has_tests: true, has_ci: true, has_security_policy: false},
    warnings: ["没有发现 SECURITY.md；采用前需确认漏洞披露渠道。"],
    documents: [
      {path: "README.md", line_count: 184}, {path: "LICENSE", line_count: 202},
      {path: "pyproject.toml", line_count: 67}, {path: ".github/workflows/ci.yml", line_count: 49},
      {path: "tests/test_evidence.py", line_count: 138}, {path: "src/ledger/store.py", line_count: 241},
    ],
  };
  renderManifest(manifest, 88);
  const report = {
    repository: manifest.source_url, commit_sha: manifest.commit_sha, analysis_goal: "企业采用评估",
    executive_summary: "项目具备清晰的安装说明、自动化测试与 CI，但缺少漏洞披露政策；建议完成安全响应流程后有条件采用。",
    decision: "conditional", decision_confidence: .88,
    claims: [
      {id: "C001", category: "testing", text: "仓库包含自动化测试与 CI 工作流。", confidence: .95, evidence: [{path: ".github/workflows/ci.yml", line_start: 1, line_end: 20, quote: "pytest"}]},
      {id: "C002", category: "license", text: "仓库包含顶层许可证文件。", confidence: .98, evidence: [{path: "LICENSE", line_start: 1, line_end: 3, quote: "Apache License"}]},
    ],
    risks: [{id: "R001", severity: "high", title: "漏洞披露渠道缺失", description: "快照中未找到 SECURITY.md。", evidence: []}],
    recommendations: [{title: "补充安全政策", action: "新增 SECURITY.md。", verification: "确认文档包含私密报告渠道。", related_paths: []}],
    unknowns: ["当前维护者对安全问题的响应时间无法从仓库快照确认。"],
  };
  renderReport(report);
  renderEvaluation({total_score: 88, grade: "A", hard_failures: [], dimensions: [
    {label: "Evidence traceability", score: 4}, {label: "Reference validity", score: 4},
    {label: "Quote grounding", score: 3}, {label: "Uncertainty disclosure", score: 4},
    {label: "Recommendation actionability", score: 4}, {label: "Format compliance", score: 4},
  ]});
  notify("已载入固定演示样本，不消耗 Hy3 API 配额。");
});

generateButton.addEventListener("click", async () => {
  if (!activeManifest) return;
  generateButton.disabled = true;
  generateButton.querySelector("span").textContent = "Hy3 正在构建证据链…";
  try {
    const reportResponse = await fetch("/api/reports/generate", {
      method: "POST", headers: {"Content-Type": "application/json"},
      body: JSON.stringify({manifest: activeManifest}),
    });
    const report = await reportResponse.json();
    if (!reportResponse.ok) throw new Error(report.detail || "Hy3 报告生成失败");
    renderReport(report);
    const evaluationResponse = await fetch("/api/evaluations/evaluate", {
      method: "POST", headers: {"Content-Type": "application/json"},
      body: JSON.stringify({manifest: activeManifest, report}),
    });
    const evaluation = await evaluationResponse.json();
    if (!evaluationResponse.ok) throw new Error(evaluation.detail || "报告评估失败");
    renderEvaluation(evaluation);
    notify("报告已生成，并完成确定性证据评估。");
  } catch (error) {
    notify(error.message);
  } finally {
    generateButton.disabled = false;
    generateButton.querySelector("span").textContent = "重新调用 Hy3 生成报告";
  }
});

checkHealth();
