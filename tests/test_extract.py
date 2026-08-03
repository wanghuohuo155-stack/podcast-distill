import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "podcast-distill-skill" / "scripts"))

from podcast.config import Config  # noqa: E402
from podcast.extract import extract_claims  # noqa: E402


SOURCE = """[要点] 决定前先写失败清单。
[行动] [00:28:00] 下期节目发布前用失败清单过选题。
[金句] "园丁不问它什么时候开花。"
[案例] 上次产品改版先列 12 种失败方式。
[原则] 预算不足时优先砍非核心功能。
"""


class ExtractTest(unittest.TestCase):
    def setUp(self) -> None:
        self.cfg = Config(project_dir=Path("."))

    def test_extract_all_kinds(self) -> None:
        claims = extract_claims(SOURCE, "ep12", self.cfg)
        kinds = [c["kind"] for c in claims]
        self.assertEqual(kinds, ["insight", "action", "quote", "case", "principle"])

    def test_action_when(self) -> None:
        claims = extract_claims(SOURCE, "ep12", self.cfg)
        action = next(c for c in claims if c["kind"] == "action")
        self.assertEqual(action["when"], "[00:28:00]")

    def test_openai_provider_unsupported(self) -> None:
        cfg = Config(project_dir=Path("."), provider="openai")
        with self.assertRaises(ValueError):
            extract_claims(SOURCE, "ep12", cfg)


if __name__ == "__main__":
    unittest.main()
