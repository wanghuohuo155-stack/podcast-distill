"""S2 提取器：按转写标记行（[要点]/[行动]/[金句]/[案例]/[原则]）做确定性提取。"""

from __future__ import annotations

import json
import re
from pathlib import Path

from .config import Config


KIND_PATTERNS: dict[str, re.Pattern] = {
    "insight": re.compile(r"^\[要点\]\s*(.+)$"),
    "action": re.compile(r"^\[行动\]\s*(.+)$"),
    "quote": re.compile(r"^\[金句\]\s*(.+)$"),
    "case": re.compile(r"^\[案例\]\s*(.+)$"),
    "principle": re.compile(r"^\[原则\]\s*(.+)$"),
}

WHEN_RE = re.compile(r"(\[\d{2}:\d{2}:\d{2}\]|下期前|下周|本周|月底)")


def extract_claims(source: str, slug: str, cfg: Config) -> list[dict]:
    if cfg.provider != "mock":
        raise ValueError(f"provider={cfg.provider} 尚未实现（M2 里程碑），当前仅支持 mock")
    claims: list[dict] = []
    for line_no, raw in enumerate(source.splitlines(), 1):
        line = raw.strip()
        if not line:
            continue
        for kind, pattern in KIND_PATTERNS.items():
            m = pattern.match(line)
            if not m:
                continue
            text = m.group(1).strip()
            claim = {
                "claim_id": f"{kind}-{line_no:02d}",
                "skill_slug": slug,
                "kind": kind,
                "title": text[:40],
                "source_chapter": f"第 {line_no} 行",
                "source_quote": line,
                "summary": text,
                "tags": [],
            }
            if kind == "action":
                when = WHEN_RE.search(text)
                if when:
                    claim["when"] = when.group(1)
            claims.append(claim)
            break
    return claims


def write_candidates(build: Path, claims: list[dict]) -> Path:
    cand_dir = build / "candidates"
    cand_dir.mkdir(parents=True, exist_ok=True)
    by_kind: dict[str, list[dict]] = {}
    for claim in claims:
        by_kind.setdefault(claim["kind"], []).append(claim)
    for kind, items in by_kind.items():
        (cand_dir / f"{kind}.json").write_text(
            json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8"
        )
    return cand_dir
