from __future__ import annotations

import json
import re

from openai import OpenAI

from .config import Settings
from .models import DueDiligenceReport, RepositoryManifest

SYSTEM_PROMPT = """You are RepoScope, an evidence-grounded open-source due diligence analyst.
Return only JSON that conforms to the supplied schema. Every material factual claim must cite one
or more evidence excerpts using the exact repository-relative path and line numbers. Never invent
files,
commands, test outcomes, project activity, vulnerabilities, or license conclusions. Put facts that
cannot be established from the supplied snapshot in unknowns. Distinguish absence of evidence from
evidence of absence. Recommendations must include a concrete action and a verification method.
"""


def _compact_manifest(manifest: RepositoryManifest, max_chars: int) -> dict[str, object]:
    prioritized = sorted(
        manifest.documents,
        key=lambda document: (not bool(document.tags), document.path.casefold()),
    )
    documents: list[dict[str, object]] = []
    used_chars = 0
    for document in prioritized:
        remaining = max_chars - used_chars
        if remaining <= 500:
            break
        payload = document.model_dump()
        payload["excerpt"] = document.excerpt[:remaining]
        documents.append(payload)
        used_chars += len(str(payload["excerpt"]))
    return {
        "source_url": manifest.source_url,
        "commit_sha": manifest.commit_sha,
        "goal": manifest.goal,
        "file_count": manifest.file_count,
        "total_size_bytes": manifest.total_size_bytes,
        "languages": manifest.languages,
        "signals": manifest.signals,
        "warnings": manifest.warnings,
        "documents": documents,
        "context_budget": {
            "available_documents": len(manifest.documents),
            "included_documents": len(documents),
            "included_excerpt_characters": used_chars,
        },
    }


def _extract_json(content: str) -> str:
    stripped = content.strip()
    fenced = re.fullmatch(r"```(?:json)?\s*(.*?)\s*```", stripped, flags=re.DOTALL)
    return fenced.group(1) if fenced else stripped


def _json_object_candidates(content: str, wrappers: tuple[str, ...]) -> list[dict[str, object]]:
    parsed = json.loads(_extract_json(content))
    if not isinstance(parsed, dict):
        raise ValueError("Hy3 JSON response must be an object.")
    candidates = [parsed]
    for wrapper in wrappers:
        nested = parsed.get(wrapper)
        if isinstance(nested, dict):
            candidates.append({**parsed, **nested})
    return candidates


def _parse_report(content: str) -> DueDiligenceReport:
    candidates = _json_object_candidates(
        content, ("report", "result", "due_diligence_report", "assessment")
    )
    errors: list[Exception] = []
    for candidate in candidates:
        try:
            return DueDiligenceReport.model_validate(candidate)
        except ValueError as exc:
            errors.append(exc)
    keys = sorted(candidates[0])
    raise ValueError(
        f"Hy3 report did not match the required schema; top-level keys: {keys}"
    ) from errors[-1]


class Hy3ReportGenerator:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.client = OpenAI(base_url=settings.hy3_base_url, api_key=settings.hy3_api_key)

    def _complete(
        self, messages: list[dict[str, str]], kwargs: dict[str, object]
    ) -> str:
        response = self.client.chat.completions.create(
            model=self.settings.hy3_model,
            messages=messages,
            temperature=0.2,
            top_p=1.0,
            **kwargs,
        )
        content = response.choices[0].message.content
        if not content:
            raise RuntimeError("Hy3 returned an empty report.")
        return content

    def generate(self, manifest: RepositoryManifest) -> DueDiligenceReport:
        user_payload = {
            "task": "Produce a repository adoption due-diligence report for the stated goal.",
            "repository_snapshot": _compact_manifest(
                manifest, self.settings.reposcope_max_context_chars
            ),
            "output_schema": DueDiligenceReport.model_json_schema(),
        }
        kwargs: dict[str, object] = {}
        if self.settings.hy3_enable_reasoning_effort:
            kwargs["extra_body"] = {
                "chat_template_kwargs": {
                    "reasoning_effort": self.settings.hy3_reasoning_effort,
                }
            }
        if self.settings.hy3_enable_json_response_format:
            kwargs["response_format"] = {"type": "json_object"}
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": json.dumps(user_payload, ensure_ascii=False)},
        ]
        content = self._complete(messages, kwargs)
        try:
            return _parse_report(content)
        except ValueError:
            repair_payload = {
                "task": "Repair the previous response so it passes the required schema.",
                "instructions": [
                    "Return one JSON object only.",
                    "Use the exact top-level field names from output_schema.",
                    "Use claims, not findings; use analysis_goal, not goal.",
                    "Preserve only statements supported by the repository snapshot.",
                ],
                "required_top_level_fields": [
                    "repository",
                    "commit_sha",
                    "analysis_goal",
                    "executive_summary",
                    "decision",
                    "decision_confidence",
                    "claims",
                    "risks",
                    "recommendations",
                    "unknowns",
                ],
                "output_schema": DueDiligenceReport.model_json_schema(),
            }
            repaired_content = self._complete(
                [
                    *messages,
                    {"role": "assistant", "content": content},
                    {
                        "role": "user",
                        "content": json.dumps(repair_payload, ensure_ascii=False),
                    },
                ],
                kwargs,
            )
            try:
                return _parse_report(repaired_content)
            except ValueError as repair_error:
                raise ValueError(
                    "Hy3 report did not match the required schema after one repair attempt."
                ) from repair_error
