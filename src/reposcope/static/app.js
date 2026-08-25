const form = document.querySelector("#analysisForm");
const runButton = document.querySelector("#runButton");
const demoButton = document.querySelector("#demoButton");
const generateButton = document.querySelector("#generateButton");
const judgeButton = document.querySelector("#judgeButton");
const emptyState = document.querySelector("#emptyState");
const results = document.querySelector("#results");
const toast = document.querySelector("#toast");
const goalInput = document.querySelector("#goal");
const themeButton = document.querySelector("#themeToggle");

const defaultGoals = {
  zh: "评估该项目是否适合在企业研发团队中用于开源项目采用前的技术尽调。",
  en: "Assess whether this project is suitable for enterprise adoption and technical due diligence.",
};

const messages = {
  zh: {
    title: "RepoScope Hy3 · 开源项目采用评估",
    description: "RepoScope Hy3 - 基于证据的开源仓库采用评估工作台",
    productName: "开源项目采用评估", primaryNav: "主导航", workspaceNav: "工作台", methodNav: "评估方法", apiDocsNav: "API 文档",
    languageSwitch: "语言切换", themeDark: "夜间", themeLight: "日间", themeDarkAria: "切换到夜间模式", themeLightAria: "切换到日间模式", apiConnecting: "正在连接", apiOnline: "评估器在线", apiOffline: "评估器离线",
    workflowLabel: "评估流程", stage1Title: "输入仓库", stage1Desc: "填写仓库与采用目标", stage2Title: "锁定快照", stage2Desc: "分析并固定代码快照",
    stage3Title: "生成报告", stage3Desc: "执行自动化证据审查", stage4Title: "评估结论", stage4Desc: "查看评分与采用建议",
    pageKicker: "EVIDENCE-GROUNDED REVIEW", pageTitle: "开源项目采用评估", pageSubtitle: "固定真实代码快照，让每个采用结论都有证据可查。",
    trustNote: "仅分析公开仓库，API 密钥不会进入浏览器", workspaceLabel: "仓库分析工作台", inputTitle: "输入仓库", inputSubtitle: "定义这次采用决策的边界。",
    repoLabel: "公开 GitHub 仓库", repoPlaceholder: "https://github.com/owner/repository", goalLabel: "你的采用目标", goalPlaceholder: "描述使用场景、目标用户、部署方式与合规关注点…",
    guidanceTitle: "填写建议", guidance1: "说明使用场景，例如嵌入产品、内部工具或二次开发。", guidance2: "写明目标用户、部署方式与合规关注点。", guidance3: "系统会固定当前 commit，避免证据随时间漂移。",
    runButton: "开始证据审查", runWorking: "正在固定仓库快照…", demoButton: "载入演示结果", privacyNote: "仓库内容仅在本次分析进程中使用，临时克隆会在检查后删除。",
    emptyLabel: "READY FOR SNAPSHOT", emptyTitle: "等待仓库快照", emptyDesc: "完成左侧信息后，我们会采集证据、固定 commit，并在这里展示可审计的评估结果。",
    emptyCheck1: "验证文件与行号", emptyCheck2: "区分事实与未知项", emptyCheck3: "给出可执行建议", snapshotLocked: "快照已锁定", overallScore: "总体评分", snapshotScore: "快照完整度",
    evidenceTitle: "证据清单", evidenceSubtitle: "来自固定快照的重点文件", generateButton: "调用 Hy3 生成尽调报告", generateWorking: "Hy3 正在构建证据链…", regenerateButton: "重新调用 Hy3 生成报告",
    adoptionDecision: "采用结论", claimsTitle: "关键结论", risksTitle: "风险与未知项", dimensionsTitle: "六大评估维度", dimensionsSubtitle: "规则层验证真实路径、引文和格式",
    judgeButton: "运行 Hy3 语义复核", judgeWorking: "Hy3 正在进行语义复核…", rejudgeButton: "重新运行 Hy3 语义复核", semanticNote: "语义分数是辅助证据，不能覆盖规则层硬门槛。",
    semanticTitle: "Hy3 语义复核", semanticSubtitle: "检查事实准确、证据蕴含与风险完整性", methodKicker: "HOW THE SCORE IS BUILT", methodTitle: "一个总分不够，我们展示分数从哪里来。",
    methodSubtitle: "规则检查负责客观事实，Hy3 负责语义判断，人工标注用于校准边界。", method1Title: "证据覆盖", method1Desc: "关键结论是否给出来源", method2Title: "引用有效", method2Desc: "文件与行号是否真实存在",
    method3Title: "原文落地", method3Desc: "引用文本是否能在快照中找到", method4Title: "不确定性", method4Desc: "未知信息是否被诚实标记", method5Title: "建议可执行", method5Desc: "是否包含动作与验证方法",
    method6Title: "格式合规", method6Desc: "输出是否通过版本化 Schema", footerDisclaimer: "个人 / 犀牛鸟活动作品 · 非腾讯官方发布",
    found: "已发现", missing: "缺失", files: "文件数", documentsCollected: "{count} 份已采集文档", lines: "{count} 行", defaultCallout: "快照基础检查未发现缺失的核心项目元数据；语义结论仍需生成报告后评估。",
    noEvidence: "暂无证据", unknownTitle: "待确认", items: "{count} 项", claimsCount: "{count} 条", grade: "等级 {grade}", hardFailure: "硬门槛触发：{detail}", snapshotFixed: "仓库快照已固定。下一步可调用 Hy3 生成尽调报告。",
    demoLoaded: "已载入固定演示样本，不消耗 Hy3 API 配额。", reportComplete: "报告已生成，并完成确定性证据评估。", semanticComplete: "语义复核完成；规则层硬门槛仍保持优先。",
    inspectFailed: "仓库检查失败", reportFailed: "Hy3 报告生成失败", evaluationFailed: "报告评估失败", semanticFailed: "Hy3 语义复核失败",
    decisionRecommend: "建议采用", decisionConditional: "条件采用", decisionDoNotRecommend: "不建议采用",
    dimEvidenceTraceability: "证据可追溯", dimReferenceValidity: "引用有效性", dimQuoteGrounding: "引文落地", dimUncertaintyDisclosure: "不确定性披露", dimRecommendationActionability: "建议可执行性", dimFormatCompliance: "格式合规性",
    dimFactualAccuracy: "事实准确性", dimEvidenceEntailment: "证据蕴含", dimRiskCompleteness: "风险完整性", dimProfessionalClarity: "专业清晰度",
    verdictSupported: "支持", verdictPartiallySupported: "部分支持", verdictUnsupported: "不支持", verdictContradicted: "矛盾",
  },
  en: {
    title: "RepoScope Hy3 · Open-source Adoption Review",
    description: "RepoScope Hy3 - an evidence-grounded open-source adoption review workspace",
    productName: "Open-source Adoption Review", primaryNav: "Primary navigation", workspaceNav: "Workspace", methodNav: "Method", apiDocsNav: "API Docs",
    languageSwitch: "Language switch", themeDark: "Dark", themeLight: "Light", themeDarkAria: "Switch to dark mode", themeLightAria: "Switch to light mode", apiConnecting: "Connecting", apiOnline: "Evaluator online", apiOffline: "Evaluator offline",
    workflowLabel: "Review workflow", stage1Title: "Input repository", stage1Desc: "Set the repository and goal", stage2Title: "Lock snapshot", stage2Desc: "Inspect and freeze the commit",
    stage3Title: "Generate report", stage3Desc: "Run the evidence review", stage4Title: "Review decision", stage4Desc: "Read scores and guidance",
    pageKicker: "EVIDENCE-GROUNDED REVIEW", pageTitle: "Open-source adoption review", pageSubtitle: "Freeze the real code snapshot so every adoption claim remains auditable.",
    trustNote: "Public repositories only; API keys never enter the browser", workspaceLabel: "Repository analysis workspace", inputTitle: "Input repository", inputSubtitle: "Define the boundary of this adoption decision.",
    repoLabel: "Public GitHub repository", repoPlaceholder: "https://github.com/owner/repository", goalLabel: "Your adoption goal", goalPlaceholder: "Describe the use case, users, deployment model, and compliance concerns…",
    guidanceTitle: "Tips for a stronger review", guidance1: "Describe whether this is embedded, internal tooling, or secondary development.", guidance2: "Name the target users, deployment model, and compliance focus.", guidance3: "RepoScope freezes the current commit to prevent evidence drift.",
    runButton: "Start evidence review", runWorking: "Locking repository snapshot…", demoButton: "Load demo result", privacyNote: "Repository content is used only for this analysis and temporary clones are removed afterward.",
    emptyLabel: "READY FOR SNAPSHOT", emptyTitle: "Waiting for a repository snapshot", emptyDesc: "Complete the inputs to collect evidence, freeze the commit, and reveal an auditable adoption review here.",
    emptyCheck1: "Validate files and lines", emptyCheck2: "Separate facts from unknowns", emptyCheck3: "Produce actionable guidance", snapshotLocked: "Snapshot locked", overallScore: "Overall score", snapshotScore: "Snapshot readiness",
    evidenceTitle: "Evidence inventory", evidenceSubtitle: "Priority files from the frozen snapshot", generateButton: "Generate Hy3 due-diligence report", generateWorking: "Hy3 is building the evidence chain…", regenerateButton: "Regenerate with Hy3",
    adoptionDecision: "Adoption decision", claimsTitle: "Key claims", risksTitle: "Risks and unknowns", dimensionsTitle: "Six evaluation dimensions", dimensionsSubtitle: "The rules layer validates paths, quotes, and format",
    judgeButton: "Run Hy3 semantic review", judgeWorking: "Hy3 is running semantic review…", rejudgeButton: "Run semantic review again", semanticNote: "Semantic scores are advisory and cannot override rules-layer hard gates.",
    semanticTitle: "Hy3 semantic review", semanticSubtitle: "Checks factual accuracy, entailment, and risk completeness", methodKicker: "HOW THE SCORE IS BUILT", methodTitle: "One total score is not enough. We show where it comes from.",
    methodSubtitle: "Rules verify objective facts, Hy3 judges semantics, and human labels calibrate the boundary.", method1Title: "Evidence coverage", method1Desc: "Do material claims cite sources?", method2Title: "Reference validity", method2Desc: "Do files and line ranges exist?",
    method3Title: "Quote grounding", method3Desc: "Can the quote be found in the snapshot?", method4Title: "Uncertainty", method4Desc: "Are unknowns disclosed honestly?", method5Title: "Actionability", method5Desc: "Do recommendations include verification?",
    method6Title: "Format compliance", method6Desc: "Does output pass the versioned schema?", footerDisclaimer: "Personal Rhino-Bird competition entry · Not an official Tencent release",
    found: "FOUND", missing: "MISSING", files: "FILES", documentsCollected: "{count} documents collected", lines: "{count} lines", defaultCallout: "The snapshot contains the core project metadata. Generate the report before drawing semantic conclusions.",
    noEvidence: "NO EVIDENCE", unknownTitle: "Needs confirmation", items: "{count} items", claimsCount: "{count} claims", grade: "Grade {grade}", hardFailure: "Hard gate triggered: {detail}", snapshotFixed: "Repository snapshot locked. You can now generate the Hy3 report.",
    demoLoaded: "Loaded the fixed demo sample without using Hy3 API quota.", reportComplete: "Report generated and deterministic evidence evaluation completed.", semanticComplete: "Semantic review completed; rules-layer hard gates remain authoritative.",
    inspectFailed: "Repository inspection failed", reportFailed: "Hy3 report generation failed", evaluationFailed: "Report evaluation failed", semanticFailed: "Hy3 semantic review failed",
    decisionRecommend: "Recommend", decisionConditional: "Conditional adoption", decisionDoNotRecommend: "Do not recommend",
    dimEvidenceTraceability: "Evidence traceability", dimReferenceValidity: "Reference validity", dimQuoteGrounding: "Quote grounding", dimUncertaintyDisclosure: "Uncertainty disclosure", dimRecommendationActionability: "Recommendation actionability", dimFormatCompliance: "Format compliance",
    dimFactualAccuracy: "Factual accuracy", dimEvidenceEntailment: "Evidence entailment", dimRiskCompleteness: "Risk completeness", dimProfessionalClarity: "Professional clarity",
    verdictSupported: "Supported", verdictPartiallySupported: "Partially supported", verdictUnsupported: "Unsupported", verdictContradicted: "Contradicted",
  },
};

let currentLanguage = "zh";
let currentTheme = "light";
let apiHealthState = "connecting";
let currentStage = 1;
let activeManifest = null;
let activeReport = null;
let activeEvaluation = null;
let activeSemanticEvaluation = null;
let activeManifestScore = null;
let isDemoData = false;
let activeNoticeKey = null;

try {
  if (window.localStorage.getItem("reposcope-language") === "en") currentLanguage = "en";
  if (window.localStorage.getItem("reposcope-theme") === "dark") currentTheme = "dark";
} catch { /* local storage can be unavailable in hardened browsers */ }

function t(key, values = {}) {
  let output = messages[currentLanguage][key] ?? messages.zh[key] ?? key;
  Object.entries(values).forEach(([name, value]) => { output = output.replaceAll(`{${name}}`, String(value)); });
  return output;
}

function escapeHtml(value) {
  return String(value).replace(/[&<>'"]/g, character => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", "'": "&#39;", '"': "&quot;",
  })[character]);
}

function notify(message, messageKey = null) {
  activeNoticeKey = messageKey;
  toast.textContent = message;
  toast.classList.add("show");
  window.setTimeout(() => toast.classList.remove("show"), 4200);
}

function shortRepo(url) {
  try { return new URL(url).pathname.replace(/^\//, "").replace(/\.git$/, ""); }
  catch { return url; }
}

function updateGoalCount() {
  document.querySelector("#goalCount").textContent = String(goalInput.value.length);
}

function setStage(stage) {
  currentStage = stage;
  document.querySelectorAll("[data-stage]").forEach(item => {
    const itemStage = Number(item.dataset.stage);
    item.classList.toggle("active", itemStage === stage);
    item.classList.toggle("complete", itemStage < stage);
    if (itemStage === stage) item.setAttribute("aria-current", "step");
    else item.removeAttribute("aria-current");
  });
}

function updateApiStatus() {
  const status = document.querySelector("#apiStatus");
  status.textContent = t(apiHealthState === "online" ? "apiOnline" : apiHealthState === "offline" ? "apiOffline" : "apiConnecting");
}

function updateThemeControl() {
  const dark = currentTheme === "dark";
  themeButton.setAttribute("aria-pressed", String(dark));
  themeButton.setAttribute("aria-label", t(dark ? "themeLightAria" : "themeDarkAria"));
  themeButton.setAttribute("title", t(dark ? "themeLightAria" : "themeDarkAria"));
  themeButton.querySelector("i").className = `ph ${dark ? "ph-sun" : "ph-moon"}`;
  document.querySelector("#themeLabel").textContent = t(dark ? "themeLight" : "themeDark");
}

function applyTheme(theme, persist = true) {
  currentTheme = theme === "dark" ? "dark" : "light";
  document.documentElement.dataset.theme = currentTheme;
  updateThemeControl();
  if (persist) {
    try { window.localStorage.setItem("reposcope-theme", currentTheme); } catch { /* no-op */ }
  }
}

function updateActionLabels() {
  const runState = runButton.dataset.state || "idle";
  runButton.querySelector("span").textContent = t(runState === "working" ? "runWorking" : "runButton");
  const generateState = generateButton.dataset.state || "idle";
  generateButton.querySelector("span").textContent = t(generateState === "working" ? "generateWorking" : generateState === "done" ? "regenerateButton" : "generateButton");
  const judgeState = judgeButton.dataset.state || "idle";
  judgeButton.querySelector("span").textContent = t(judgeState === "working" ? "judgeWorking" : judgeState === "done" ? "rejudgeButton" : "judgeButton");
}

function setButtonState(button, state) {
  button.dataset.state = state;
  updateActionLabels();
}

function decisionLabel(decision) {
  return t({recommend: "decisionRecommend", conditional: "decisionConditional", do_not_recommend: "decisionDoNotRecommend"}[decision] || decision);
}

const dimensionKeys = {
  evidence_traceability: "dimEvidenceTraceability", reference_validity: "dimReferenceValidity", quote_grounding: "dimQuoteGrounding",
  uncertainty_disclosure: "dimUncertaintyDisclosure", recommendation_actionability: "dimRecommendationActionability", format_compliance: "dimFormatCompliance",
  factual_accuracy: "dimFactualAccuracy", evidence_entailment: "dimEvidenceEntailment", risk_completeness: "dimRiskCompleteness", professional_clarity: "dimProfessionalClarity",
};

function dimensionLabel(item) {
  const normalized = String(item.key || item.label || "").toLowerCase().replaceAll(" ", "_");
  return dimensionKeys[normalized] ? t(dimensionKeys[normalized]) : item.label;
}

function applyLanguage(language, rerender = true) {
  const previousGoal = goalInput.value;
  currentLanguage = language === "en" ? "en" : "zh";
  document.documentElement.lang = currentLanguage === "zh" ? "zh-CN" : "en";
  document.title = t("title");
  document.querySelector("#metaDescription").setAttribute("content", t("description"));
  document.querySelectorAll("[data-i18n]").forEach(element => { element.textContent = t(element.dataset.i18n); });
  document.querySelectorAll("[data-i18n-placeholder]").forEach(element => { element.setAttribute("placeholder", t(element.dataset.i18nPlaceholder)); });
  document.querySelectorAll("[data-i18n-aria]").forEach(element => { element.setAttribute("aria-label", t(element.dataset.i18nAria)); });
  document.querySelectorAll("[data-lang]").forEach(button => {
    const active = button.dataset.lang === currentLanguage;
    button.classList.toggle("active", active);
    button.setAttribute("aria-pressed", String(active));
  });
  if (Object.values(defaultGoals).includes(previousGoal)) goalInput.value = defaultGoals[currentLanguage];
  try { window.localStorage.setItem("reposcope-language", currentLanguage); } catch { /* no-op */ }
  updateApiStatus();
  updateThemeControl();
  updateActionLabels();
  updateGoalCount();
  setStage(currentStage);
  if (!rerender || !activeManifest) return;
  if (isDemoData) {
    activeManifest = makeDemoManifest();
    activeReport = makeDemoReport();
    activeEvaluation = makeDemoEvaluation();
    activeSemanticEvaluation = makeDemoSemanticEvaluation();
  }
  renderManifest(activeManifest, activeManifestScore, false);
  if (activeReport) renderReport(activeReport, false);
  if (activeEvaluation) renderEvaluation(activeEvaluation);
  if (activeSemanticEvaluation) renderSemanticEvaluation(activeSemanticEvaluation, false);
  if (toast.classList.contains("show") && activeNoticeKey) toast.textContent = t(activeNoticeKey);
}

function signal(label, value, present, icon) {
  return `<div class="signal ${present ? "" : "missing"}"><span class="signal-icon"><i class="ph ${icon}" aria-hidden="true"></i></span><strong>${escapeHtml(value)}</strong><span>${escapeHtml(label)}</span></div>`;
}

function renderManifest(manifest, score = null, reset = true) {
  activeManifest = manifest;
  activeManifestScore = score;
  if (reset) {
    activeReport = null; activeEvaluation = null; activeSemanticEvaluation = null; isDemoData = false;
    document.querySelector("#reportView").classList.add("hidden");
    document.querySelector("#scoreBreakdown").classList.add("hidden");
    document.querySelector("#semanticActions").classList.add("hidden");
    document.querySelector("#semanticView").classList.add("hidden");
    setButtonState(generateButton, "idle"); setButtonState(judgeButton, "idle");
  }
  emptyState.classList.add("hidden");
  results.classList.remove("hidden");
  document.querySelector("#resultRepo").textContent = shortRepo(manifest.source_url);
  document.querySelector("#resultSha").textContent = manifest.commit_sha.slice(0, 12);
  document.querySelector("#resultBranch").textContent = manifest.default_branch || "main";
  const calculated = score ?? Math.min(96, 48 + Object.values(manifest.signals || {}).filter(value => value === true).length * 8);
  document.querySelector("#resultScore").textContent = String(Math.round(calculated));
  document.querySelector("#scoreGrade").textContent = "—";
  document.querySelector("#scoreCaption").textContent = t("snapshotScore");

  const signals = manifest.signals || {};
  document.querySelector("#signalGrid").innerHTML = [
    signal("README", signals.has_readme ? t("found") : t("missing"), Boolean(signals.has_readme), "ph-file-text"),
    signal("LICENSE", signals.has_license ? t("found") : t("missing"), Boolean(signals.has_license), "ph-scales"),
    signal("TESTS", signals.has_tests ? t("found") : t("missing"), Boolean(signals.has_tests), "ph-test-tube"),
    signal("CI", signals.has_ci ? t("found") : t("missing"), Boolean(signals.has_ci), "ph-checks"),
    signal(t("files"), String(manifest.file_count), true, "ph-files"),
  ].join("");

  const documents = (manifest.documents || []).slice(0, 12);
  document.querySelector("#evidenceCount").textContent = t("documentsCollected", {count: manifest.documents?.length || 0});
  document.querySelector("#evidenceList").innerHTML = documents.map(document =>
    `<div class="evidence-item"><i class="ph ph-file-text" aria-hidden="true"></i><code>${escapeHtml(document.path)}</code><span>${escapeHtml(t("lines", {count: Number(document.line_count)}))}</span></div>`
  ).join("");
  document.querySelector("#resultCallout").textContent = manifest.warnings?.length ? manifest.warnings.join(" ") : t("defaultCallout");
  generateButton.classList.remove("hidden");
  if (reset) setStage(2);
}

function evidenceLabel(item) {
  const reference = item.evidence?.[0];
  return reference ? `${reference.path}:${Number(reference.line_start)}-${Number(reference.line_end)}` : t("noEvidence");
}

function renderReport(report, scroll = true) {
  activeReport = report;
  const view = document.querySelector("#reportView");
  view.classList.remove("hidden");
  document.querySelector("#reportDecision").textContent = decisionLabel(report.decision);
  document.querySelector("#reportSummary").textContent = report.executive_summary;
  document.querySelector("#claimCount").textContent = t("claimsCount", {count: report.claims.length});
  document.querySelector("#claimList").innerHTML = report.claims.slice(0, 5).map(claim =>
    `<article class="report-card"><strong>${escapeHtml(claim.id)} · ${escapeHtml(claim.category)}</strong><p>${escapeHtml(claim.text)}</p><code>${escapeHtml(evidenceLabel(claim))}</code></article>`
  ).join("");
  const risks = [...report.risks, ...(report.unknowns || []).map((text, index) => ({
    id: `U${String(index + 1).padStart(3, "0")}`, severity: "unknown", title: t("unknownTitle"), description: text, evidence: [],
  }))];
  document.querySelector("#riskCount").textContent = t("items", {count: risks.length});
  document.querySelector("#riskList").innerHTML = risks.slice(0, 6).map(risk =>
    `<article class="report-card risk-${escapeHtml(risk.severity)}"><strong>${escapeHtml(risk.id)} · ${escapeHtml(risk.title)}</strong><p>${escapeHtml(risk.description)}</p><code>${escapeHtml(evidenceLabel(risk))}</code></article>`
  ).join("");
  if (scroll) view.scrollIntoView({behavior: "smooth", block: "nearest"});
}

function renderEvaluation(evaluation) {
  activeEvaluation = evaluation;
  document.querySelector("#scoreBreakdown").classList.remove("hidden");
  document.querySelector("#gradeLabel").textContent = t("grade", {grade: evaluation.grade});
  document.querySelector("#dimensionList").innerHTML = evaluation.dimensions.map(item =>
    `<div class="dimension-row"><span>${escapeHtml(dimensionLabel(item))}</span><div class="dimension-bar"><i style="width:${Math.max(0, Math.min(100, Number(item.score) / 4 * 100))}%"></i></div><strong>${Number(item.score).toFixed(1)}</strong></div>`
  ).join("");
  document.querySelector("#resultScore").textContent = String(Math.round(evaluation.total_score));
  document.querySelector("#scoreGrade").textContent = evaluation.grade;
  document.querySelector("#scoreCaption").textContent = t("overallScore");
  if (evaluation.hard_failures.length) document.querySelector("#resultCallout").textContent = t("hardFailure", {detail: evaluation.hard_failures.join(" ")});
  document.querySelector("#semanticActions").classList.remove("hidden");
  setButtonState(generateButton, "done");
  setStage(4);
}

function verdictLabel(verdict) {
  return t({supported: "verdictSupported", partially_supported: "verdictPartiallySupported", unsupported: "verdictUnsupported", contradicted: "verdictContradicted"}[verdict] || verdict);
}

function renderSemanticEvaluation(evaluation, scroll = true) {
  activeSemanticEvaluation = evaluation;
  document.querySelector("#semanticView").classList.remove("hidden");
  document.querySelector("#semanticDimensionList").innerHTML = evaluation.dimensions.map(item =>
    `<div class="dimension-row"><span>${escapeHtml(dimensionLabel(item))}</span><div class="dimension-bar"><i style="width:${Math.max(0, Math.min(100, Number(item.score) / 4 * 100))}%"></i></div><strong>${Number(item.score).toFixed(1)}</strong></div>`
  ).join("");
  document.querySelector("#judgementList").innerHTML = evaluation.claim_judgements.map(item =>
    `<article class="judgement"><strong>${escapeHtml(item.claim_id)}</strong><em>${escapeHtml(verdictLabel(item.verdict))}</em><p>${escapeHtml(item.explanation)}</p></article>`
  ).join("");
  setButtonState(judgeButton, "done");
  if (scroll) document.querySelector("#semanticView").scrollIntoView({behavior: "smooth", block: "nearest"});
}

function makeDemoManifest() {
  return {
    source_url: "https://github.com/pypa/sampleproject", commit_sha: "621e4974ca25e8804d62557db919510b1c5a9b18", default_branch: "main", file_count: 12, total_size_bytes: 928441,
    signals: {has_readme: true, has_license: true, has_tests: true, has_ci: true, has_security_policy: false},
    warnings: [currentLanguage === "zh" ? "没有发现 SECURITY.md；采用前需确认漏洞披露渠道。" : "No SECURITY.md was found; confirm the vulnerability disclosure channel before adoption."],
    documents: [{path: "README.md", line_count: 184}, {path: "LICENSE.txt", line_count: 202}, {path: "pyproject.toml", line_count: 67}, {path: ".github/workflows/ci.yml", line_count: 49}, {path: "tests/test_evidence.py", line_count: 138}, {path: "src/sample/simple.py", line_count: 53}],
  };
}

function makeDemoReport() {
  const zh = currentLanguage === "zh";
  return {
    repository: activeManifest?.source_url, commit_sha: activeManifest?.commit_sha, analysis_goal: zh ? "企业采用评估" : "Enterprise adoption review",
    executive_summary: zh ? "项目具备清晰的安装说明、自动化测试与 CI，但缺少漏洞披露政策；建议完成安全响应流程后有条件采用。" : "The project has clear setup guidance, automated tests, and CI, but lacks a vulnerability disclosure policy. Adopt conditionally after establishing a security response process.",
    decision: "conditional", decision_confidence: 0.88,
    claims: [
      {id: "C001", category: "testing", text: zh ? "仓库包含自动化测试与 CI 工作流。" : "The repository includes automated tests and a CI workflow.", confidence: 0.95, evidence: [{path: ".github/workflows/ci.yml", line_start: 1, line_end: 20, quote: "pytest"}]},
      {id: "C002", category: "license", text: zh ? "仓库包含顶层许可证文件。" : "The repository contains a top-level license file.", confidence: 0.98, evidence: [{path: "LICENSE.txt", line_start: 1, line_end: 3, quote: "MIT License"}]},
    ],
    risks: [{id: "R001", severity: "high", title: zh ? "漏洞披露渠道缺失" : "Missing vulnerability disclosure channel", description: zh ? "快照中未找到 SECURITY.md。" : "No SECURITY.md was found in the snapshot.", evidence: []}],
    recommendations: [], unknowns: [zh ? "当前维护者对安全问题的响应时间无法从仓库快照确认。" : "Maintainer response time for security issues cannot be established from the snapshot."],
  };
}

function makeDemoEvaluation() {
  return {total_score: 90, grade: "A", hard_failures: [], dimensions: [
    {key: "evidence_traceability", label: "Evidence traceability", score: 4}, {key: "reference_validity", label: "Reference validity", score: 4},
    {key: "quote_grounding", label: "Quote grounding", score: 3}, {key: "uncertainty_disclosure", label: "Uncertainty disclosure", score: 4},
    {key: "recommendation_actionability", label: "Recommendation actionability", score: 4}, {key: "format_compliance", label: "Format compliance", score: 4},
  ]};
}

function makeDemoSemanticEvaluation() {
  const zh = currentLanguage === "zh";
  return {dimensions: [
    {key: "factual_accuracy", label: "Factual accuracy", score: 4}, {key: "evidence_entailment", label: "Evidence entailment", score: 4},
    {key: "risk_completeness", label: "Risk completeness", score: 3}, {key: "professional_clarity", label: "Professional clarity", score: 4},
  ], claim_judgements: [
    {claim_id: "C001", verdict: "supported", explanation: zh ? "CI 文件与测试目录共同支持该结论。" : "The CI file and tests directory support this claim."},
    {claim_id: "C002", verdict: "supported", explanation: zh ? "顶层许可证文件直接支持该结论。" : "The top-level license file directly supports this claim."},
  ]};
}

async function checkHealth() {
  try {
    const response = await fetch("/api/health");
    if (!response.ok) throw new Error();
    apiHealthState = "online";
    document.querySelector(".status-dot").classList.add("ok");
  } catch {
    apiHealthState = "offline";
  }
  updateApiStatus();
}

form.addEventListener("submit", async event => {
  event.preventDefault();
  runButton.disabled = true; setButtonState(runButton, "working"); setStage(1);
  try {
    const response = await fetch("/api/repositories/inspect", {method: "POST", headers: {"Content-Type": "application/json"}, body: JSON.stringify({repository_url: document.querySelector("#repoUrl").value, goal: goalInput.value})});
    const payload = await response.json();
    if (!response.ok) throw new Error(payload.detail || t("inspectFailed"));
    renderManifest(payload);
    notify(t("snapshotFixed"), "snapshotFixed");
  } catch (error) { notify(error.message); }
  finally { runButton.disabled = false; setButtonState(runButton, "idle"); }
});

demoButton.addEventListener("click", () => {
  const manifest = makeDemoManifest();
  renderManifest(manifest, 90);
  isDemoData = true;
  activeReport = makeDemoReport(); activeEvaluation = makeDemoEvaluation(); activeSemanticEvaluation = makeDemoSemanticEvaluation();
  renderReport(activeReport, false); renderEvaluation(activeEvaluation); renderSemanticEvaluation(activeSemanticEvaluation, false);
  notify(t("demoLoaded"), "demoLoaded");
});

generateButton.addEventListener("click", async () => {
  if (!activeManifest) return;
  generateButton.disabled = true; setButtonState(generateButton, "working"); setStage(3);
  try {
    const reportResponse = await fetch("/api/reports/generate", {method: "POST", headers: {"Content-Type": "application/json"}, body: JSON.stringify({manifest: activeManifest})});
    const report = await reportResponse.json();
    if (!reportResponse.ok) throw new Error(report.detail || t("reportFailed"));
    renderReport(report);
    const evaluationResponse = await fetch("/api/evaluations/evaluate", {method: "POST", headers: {"Content-Type": "application/json"}, body: JSON.stringify({manifest: activeManifest, report})});
    const evaluation = await evaluationResponse.json();
    if (!evaluationResponse.ok) throw new Error(evaluation.detail || t("evaluationFailed"));
    renderEvaluation(evaluation); notify(t("reportComplete"), "reportComplete");
  } catch (error) { notify(error.message); setStage(2); }
  finally { generateButton.disabled = false; if (!activeEvaluation) setButtonState(generateButton, "idle"); }
});

judgeButton.addEventListener("click", async () => {
  if (!activeManifest || !activeReport) return;
  judgeButton.disabled = true; setButtonState(judgeButton, "working");
  try {
    const response = await fetch("/api/evaluations/judge", {method: "POST", headers: {"Content-Type": "application/json"}, body: JSON.stringify({manifest: activeManifest, report: activeReport})});
    const evaluation = await response.json();
    if (!response.ok) throw new Error(evaluation.detail || t("semanticFailed"));
    renderSemanticEvaluation(evaluation); notify(t("semanticComplete"), "semanticComplete");
  } catch (error) { notify(error.message); }
  finally { judgeButton.disabled = false; if (!activeSemanticEvaluation) setButtonState(judgeButton, "idle"); }
});

document.querySelectorAll("[data-lang]").forEach(button => button.addEventListener("click", () => applyLanguage(button.dataset.lang)));
themeButton.addEventListener("click", () => applyTheme(currentTheme === "dark" ? "light" : "dark"));
goalInput.addEventListener("input", updateGoalCount);
applyTheme(currentTheme, false);
applyLanguage(currentLanguage, false);
setStage(1);
checkHealth();
