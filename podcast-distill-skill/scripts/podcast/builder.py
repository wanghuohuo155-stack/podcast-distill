"""S4 构造器：从 claims 组装 SKILL.md（模板替换）+ 六段结构校验。"""

from __future__ import annotations

import json
import re
from pathlib import Path

from .config import Config


REQUIRED_SECTIONS = ("## R", "## I", "## A1", "## A2", "## E", "## B")


def validate_skill(skill_md: str, cfg: Config) -> list[str]:
    issues: list[str] = []
    lines = [line.strip() for line in skill_md.splitlines()]
    missing = [s for s in REQUIRED_SECTIONS if not any(line.startswith(s) for line in lines)]
    if missing:
        issues.append(f"缺少段落: {', '.join(missing)}")
    fm = re.match(r"^---\n(.*?)\n---", skill_md, re.DOTALL)
    if not fm:
        issues.append("缺少 frontmatter")
    elif "name:" not in fm.group(1) or "description:" not in fm.group(1):
        issues.append("frontmatter 必须含 name 和 description")
    return issues


def build_skill(claims: list[dict], template: str, skill_slug: str, title: str) -> str:
    def bullets(kind: str) -> str:
        items = [c for c in claims if c["kind"] == kind][:5]
        if not items:
            return "- （无）"
        if kind == "action":
            return "\n".join(
                f"- {c['summary']}（时间点 {c.get('when', '?')}）" for c in items
            )
        if kind == "quote":
            return "\n".join(f"- {c['summary']}" for c in items)
        return "\n".join(f"- {c['summary']}" for c in items)

    first = next((c for c in claims if c["kind"] in ("quote", "insight")), claims[0])
    quote = first["source_quote"]
    if len(quote) > 150:
        quote = quote[:150] + "…"
    return (
        template.replace("{{slug}}", skill_slug)
        .replace("{{title}}", title)
        .replace("{{quote}}", quote)
        .replace("{{insights}}", bullets("insight"))
        .replace("{{actions}}", bullets("action"))
        .replace("{{quotes}}", bullets("quote"))
        .replace("{{principles}}", bullets("principle"))
    )


def write_skill(build: Path, skill_md: str, skill_slug: str) -> Path:
    skill_dir = build / "skills" / skill_slug
    (skill_dir / "tests").mkdir(parents=True, exist_ok=True)
    (skill_dir / "SKILL.md").write_text(skill_md, encoding="utf-8")
    return skill_dir


def load_claims(build: Path) -> list[dict]:
    claims_path = build / "claims.jsonl"
    if not claims_path.exists():
        raise FileNotFoundError(f"找不到 claims 文件: {claims_path}")
    return [
        json.loads(line)
        for line in claims_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
