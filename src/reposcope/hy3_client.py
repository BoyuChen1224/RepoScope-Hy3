from __future__ import annotations

import json

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


def _compact_manifest(manifest: RepositoryManifest) -> dict[str, object]:
    return {
        "source_url": manifest.source_url,
        "commit_sha": manifest.commit_sha,
        "goal": manifest.goal,
        "file_count": manifest.file_count,
        "total_size_bytes": manifest.total_size_bytes,
        "languages": manifest.languages,
        "signals": manifest.signals,
        "warnings": manifest.warnings,
        "documents": [document.model_dump() for document in manifest.documents],
    }


class Hy3ReportGenerator:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.client = OpenAI(base_url=settings.hy3_base_url, api_key=settings.hy3_api_key)

    def generate(self, manifest: RepositoryManifest) -> DueDiligenceReport:
        user_payload = {
            "task": "Produce a repository adoption due-diligence report for the stated goal.",
            "repository_snapshot": _compact_manifest(manifest),
            "output_schema": DueDiligenceReport.model_json_schema(),
        }
        kwargs: dict[str, object] = {}
        if self.settings.hy3_enable_reasoning_effort:
            kwargs["extra_body"] = {
                "chat_template_kwargs": {
                    "reasoning_effort": self.settings.hy3_reasoning_effort,
                }
            }
        response = self.client.chat.completions.create(
            model=self.settings.hy3_model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": json.dumps(user_payload, ensure_ascii=False)},
            ],
            temperature=0.2,
            top_p=1.0,
            response_format={"type": "json_object"},
            **kwargs,
        )
        content = response.choices[0].message.content
        if not content:
            raise RuntimeError("Hy3 returned an empty report.")
        return DueDiligenceReport.model_validate_json(content)
