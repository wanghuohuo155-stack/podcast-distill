import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "podcast-distill-skill" / "scripts"))

from podcast.config import Config  # noqa: E402
from podcast.evaluator import run_trigger_tests  # noqa: E402


class EvaluatorTest(unittest.TestCase):
    def test_pass_when_bait_clean(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            build = Path(tmp)
            (build / "skills" / "demo" / "tests").mkdir(parents=True)
            data = {
                "skill": "s",
                "version": "0.1.0",
                "test_cases": [
                    {"id": "t1", "type": "should_trigger", "prompt": "上期播客的失败清单怎么用", "expected_behavior": "x"},
                    {"id": "n1", "type": "should_not_trigger", "prompt": "帮我查 API", "expected_behavior": "x"},
                ],
            }
            (build / "skills" / "demo" / "tests" / "trigger.json").write_text(json.dumps(data), encoding="utf-8")
            report = run_trigger_tests(build, Config(project_dir=Path(".")))
            self.assertIn("整体判定: PASS", report.read_text(encoding="utf-8"))

    def test_fail_when_bait_triggered(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            build = Path(tmp)
            (build / "skills" / "demo" / "tests").mkdir(parents=True)
            data = {
                "skill": "s",
                "version": "0.1.0",
                "test_cases": [
                    {"id": "n1", "type": "should_not_trigger", "prompt": "这条金句是哪集的", "expected_behavior": "x"},
                ],
            }
            (build / "skills" / "demo" / "tests" / "trigger.json").write_text(json.dumps(data), encoding="utf-8")
            report = run_trigger_tests(build, Config(project_dir=Path("."), bait_tolerance=0))
            self.assertIn("整体判定: FAIL", report.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
