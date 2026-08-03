import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "podcast-distill-skill" / "scripts"))

from podcast.builder import build_skill, validate_skill  # noqa: E402
from podcast.config import Config  # noqa: E402


CLAIMS = [
    {"kind": "insight", "source_quote": "[要点] 决定前先写失败清单。", "summary": "决定前先写失败清单"},
    {"kind": "action", "source_quote": "[行动] [00:28:00] 下期发布前过选题。", "summary": "下期发布前过选题", "when": "[00:28:00]"},
    {"kind": "quote", "source_quote": '[金句] "园丁不问它什么时候开花。"', "summary": "园丁不问开花"},
]

TEMPLATE = """---
name: {{slug}}
description: |
  播客知识辅助。
---

# {{title}}

## R
> {{quote}}

## I
{{insights}}

## A1
{{actions}}

## A2
{{quotes}}

## E
1. 行动验收

## B
不要用于纯信息查询
"""


class BuilderTest(unittest.TestCase):
    def setUp(self) -> None:
        self.cfg = Config(project_dir=Path("."))

    def test_build_and_validate(self) -> None:
        skill_md = build_skill(CLAIMS, TEMPLATE, "ep12-insights", "播客决策辅助")
        self.assertIn("name: ep12-insights", skill_md)
        self.assertIn("决定前先写失败清单", skill_md)
        self.assertEqual(validate_skill(skill_md, self.cfg), [])

    def test_missing_section_fails(self) -> None:
        skill_md = build_skill(CLAIMS, TEMPLATE, "ep12-insights", "播客决策辅助")
        broken = "\n".join(line for line in skill_md.splitlines() if not line.startswith("## B"))
        self.assertTrue(any("缺少段落" in item for item in validate_skill(broken, self.cfg)))


if __name__ == "__main__":
    unittest.main()
