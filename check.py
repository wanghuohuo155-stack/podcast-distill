"""最小可运行检查：python check.py。任何核心逻辑写错都会以非零退出码失败。"""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "podcast-distill-skill" / "scripts"))

from podcast import builder, packager, verifier  # noqa: E402
from podcast.config import Config  # noqa: E402


SOURCE = (
    '[要点] 决定前先写失败清单。\n'
    '[金句] "园丁不问它什么时候开花，而是问什么会杀死它。"\n'
    "[行动] [00:28:00] 下期节目发布前用失败清单过选题。\n"
)


def main() -> int:
    cfg = Config(project_dir=Path(tempfile.mkdtemp()))

    # 1. 引文校验：真引文 verified，假引文 unverified
    good = {
        "claim_id": "i01",
        "skill_slug": "ep12-insights",
        "kind": "insight",
        "title": "失败清单",
        "source_chapter": "1",
        "source_quote": "[要点] 决定前先写失败清单。",
        "summary": "决定前先写失败清单",
    }
    assert verifier.verify_claim(good, SOURCE, cfg)["status"] == "verified"
    bad = dict(good)
    bad["source_quote"] = "不在原文的句子"
    assert verifier.verify_claim(bad, SOURCE, cfg)["status"] == "unverified"

    # 2. 行动时间点：缺 when 必须 unverified
    action = {
        "claim_id": "a01",
        "skill_slug": "s",
        "kind": "action",
        "title": "过选题",
        "source_chapter": "3",
        "source_quote": "[行动] [00:28:00] 下期节目发布前用失败清单过选题。",
        "summary": "下期发布前用失败清单过选题",
        "when": "[00:28:00]",
    }
    assert verifier.verify_claim(action, SOURCE, cfg)["status"] == "verified"
    no_when = dict(action)
    no_when.pop("when")
    assert verifier.verify_claim(no_when, SOURCE, cfg)["status"] == "unverified"

    # 3. 金句引号：未引号包围必须 unverified
    quote_ok = {
        "claim_id": "q01",
        "skill_slug": "s",
        "kind": "quote",
        "title": "金句",
        "source_chapter": "2",
        "source_quote": '[金句] "园丁不问它什么时候开花，而是问什么会杀死它。"',
        "summary": "园丁不问开花",
    }
    assert verifier.verify_claim(quote_ok, SOURCE, cfg)["status"] == "verified"
    quote_bad = dict(quote_ok)
    quote_bad["source_quote"] = "[金句] 园丁不问它什么时候开花。"
    assert verifier.verify_claim(quote_bad, SOURCE, cfg)["status"] == "unverified"

    # 4. 六段结构：完整通过，缺 B 段必须失败
    skill_md = """---
name: demo
description: |
  演示用。
---
## R
x
## I
x
## A1
x
## A2
x
## E
x
## B
x
"""
    assert builder.validate_skill(skill_md, cfg) == []
    broken = "\n".join(line for line in skill_md.splitlines() if not line.startswith("## B"))
    assert any("缺少段落" in item for item in builder.validate_skill(broken, cfg))

    # 5. 发布闸门：缺 TEST_REPORT 失败，PASS 后通过
    with tempfile.TemporaryDirectory() as tmp:
        build = Path(tmp) / "demo"
        (build / "skills" / "demo-skill" / "tests").mkdir(parents=True)
        (build / "skills" / "demo-skill" / "SKILL.md").write_text(skill_md, encoding="utf-8")
        for name in ("PROVENANCE.md", "GLOSSARY.md", "INDEX.md"):
            (build / name).write_text("x", encoding="utf-8")
        assert packager.validate_build_dir(build), "缺少 TEST_REPORT.md 时应失败"
        (build / "TEST_REPORT.md").write_text("# TEST_REPORT.md\n- 整体判定: PASS\n", encoding="utf-8")
        assert packager.validate_build_dir(build) == []

    print("check OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
