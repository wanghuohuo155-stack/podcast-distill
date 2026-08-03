"""S6 打包器 + 发布闸门：证据四件套 + TEST_REPORT 必须 PASS。"""

from __future__ import annotations

import json
import shutil
from datetime import datetime, timezone
from pathlib import Path


def validate_build_dir(build: Path) -> list[str]:
    issues: list[str] = []
    for name in ("PROVENANCE.md", "GLOSSARY.md", "INDEX.md", "TEST_REPORT.md"):
        if not (build / name).exists():
            issues.append(f"缺少 {name}")
    test_report = build / "TEST_REPORT.md"
    if test_report.exists() and "整体判定: PASS" not in test_report.read_text(encoding="utf-8"):
        issues.append("TEST_REPORT 判定不是 PASS（评测未通过，禁止打包）")
    skill_dirs = list((build / "skills").glob("*")) if (build / "skills").exists() else []
    if not any(d.is_dir() and (d / "SKILL.md").exists() for d in skill_dirs):
        issues.append("skills/ 下缺少含 SKILL.md 的 skill")
    return issues


def package(build: Path, name: str, version: str, out_root: Path) -> Path:
    issues = validate_build_dir(build)
    if issues:
        raise ValueError("打包失败: " + "; ".join(issues))
    pack_dir = out_root / name
    if pack_dir.exists():
        shutil.rmtree(pack_dir)
    (pack_dir / "skills").mkdir(parents=True, exist_ok=True)
    for skill_dir in (build / "skills").iterdir():
        if skill_dir.is_dir():
            shutil.copytree(skill_dir, pack_dir / "skills" / skill_dir.name)
    pack_json = {
        "name": name,
        "version": version,
        "hosts": ["codex", "claude", "cursor"],
        "skills": [d.name for d in (build / "skills").iterdir() if d.is_dir()],
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    (pack_dir / "pack.json").write_text(
        json.dumps(pack_json, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return pack_dir


def gate(pack: Path) -> list[str]:
    issues: list[str] = []
    pack_json = pack / "pack.json"
    if not pack_json.exists():
        return ["缺少 pack.json"]
    data = json.loads(pack_json.read_text(encoding="utf-8"))
    if not data.get("name") or not data.get("version"):
        issues.append("pack.json 缺 name/version")
    for skill_dir in (pack / "skills").glob("*"):
        if not (skill_dir / "SKILL.md").exists():
            issues.append(f"{skill_dir.name} 缺 SKILL.md")
    return issues
