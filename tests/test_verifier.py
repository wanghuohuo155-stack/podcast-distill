import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "podcast-distill-skill" / "scripts"))

from podcast.config import Config  # noqa: E402
from podcast.verifier import verify_claim  # noqa: E402


SOURCE = (
    '[要点] 决定前先写失败清单。\n'
    '[金句] "园丁不问它什么时候开花。"\n'
    "[行动] [00:28:00] 下期节目发布前用失败清单过选题。\n"
)


class VerifierTest(unittest.TestCase):
    def setUp(self) -> None:
        self.cfg = Config(project_dir=Path("."))

    def _claim(self, **overrides) -> dict:
        claim = {
            "claim_id": "c01",
            "skill_slug": "s",
            "kind": "insight",
            "title": "t",
            "source_chapter": "1",
            "source_quote": "[要点] 决定前先写失败清单。",
            "summary": "s",
        }
        claim.update(overrides)
        return claim

    def test_verified_when_quote_exists(self) -> None:
        self.assertEqual(verify_claim(self._claim(), SOURCE, self.cfg)["status"], "verified")

    def test_unverified_when_quote_missing(self) -> None:
        result = verify_claim(self._claim(source_quote="不在原文"), SOURCE, self.cfg)
        self.assertEqual(result["status"], "unverified")

    def test_unverified_when_quote_too_long(self) -> None:
        cfg = Config(project_dir=Path("."), quote_max_chars=5)
        result = verify_claim(self._claim(), SOURCE, cfg)
        self.assertEqual(result["status"], "unverified")

    def test_action_requires_when(self) -> None:
        claim = self._claim(
            kind="action",
            source_quote="[行动] [00:28:00] 下期节目发布前用失败清单过选题。",
            when="[00:28:00]",
        )
        self.assertEqual(verify_claim(claim, SOURCE, self.cfg)["status"], "verified")
        claim.pop("when")
        self.assertEqual(verify_claim(claim, SOURCE, self.cfg)["status"], "unverified")

    def test_quote_requires_quotes(self) -> None:
        ok = self._claim(
            kind="quote",
            source_quote='[金句] "园丁不问它什么时候开花。"',
        )
        self.assertEqual(verify_claim(ok, SOURCE, self.cfg)["status"], "verified")
        bad = self._claim(kind="quote", source_quote="[金句] 园丁不问它什么时候开花。")
        self.assertEqual(verify_claim(bad, SOURCE, self.cfg)["status"], "unverified")


if __name__ == "__main__":
    unittest.main()
