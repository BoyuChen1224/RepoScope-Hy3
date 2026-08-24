const form = document.querySelector("#analysisForm");
const runButton = document.querySelector("#runButton");
const demoButton = document.querySelector("#demoButton");
const emptyState = document.querySelector("#emptyState");
const results = document.querySelector("#results");
const toast = document.querySelector("#toast");

function notify(message) {
  toast.textContent = message;
  toast.classList.add("show");
  window.setTimeout(() => toast.classList.remove("show"), 4200);
}

function shortRepo(url) {
  try { return new URL(url).pathname.replace(/^\//, "").replace(/\.git$/, ""); }
  catch { return url; }
}

function signal(label, value, present = true) {
  return `<div class="signal ${present ? "" : "missing"}"><strong>${value}</strong><span>${label}</span></div>`;
}

function renderManifest(manifest, score = null) {
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
    `<div class="evidence-item"><code>${doc.path}</code><span>${doc.line_count} lines</span></div>`
  ).join("");
  const warning = manifest.warnings.length
    ? manifest.warnings.join(" ")
    : "快照基础检查未发现缺失的核心项目元数据；语义结论仍需生成报告后评估。";
  document.querySelector("#resultCallout").textContent = warning;
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
  renderManifest({
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
  }, 88);
  notify("已载入固定演示样本，不消耗 Hy3 API 配额。");
});

checkHealth();

