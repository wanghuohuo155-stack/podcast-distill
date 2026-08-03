import shutil
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "podcast-distill-skill" / "scripts"))

from podcast.cli import main  # noqa: E402


class CliPipelineTest(unittest.TestCase):
    def test_full_pipeline(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            shutil.copytree(ROOT / "specs", project / "specs")
            source = ROOT / "examples" / "sample-transcript.txt"
            self.assertEqual(main(["init", "--project", str(project)]), 0)
            self.assertEqual(main(["doctor", "--project", str(project)]), 0)
            self.assertEqual(main(["ingest", "--project", str(project), "--slug", "ep12", "--source", str(source)]), 0)
            self.assertEqual(main(["extract", "--project", str(project), "--slug", "ep12"]), 0)
            self.assertEqual(main(["verify", "--project", str(project), "--slug", "ep12"]), 0)
            self.assertEqual(main(["check", "--project", str(project), "--slug", "ep12", "--title", "先写失败清单"]), 0)
            self.assertEqual(main(["test", "--project", str(project), "--slug", "ep12", "--mode", "mock"]), 0)
            self.assertEqual(main(["package", "--project", str(project), "--slug", "ep12", "--name", "demo-pack"]), 0)
            self.assertEqual(main(["gate", "--pack", str(project / "packs" / "demo-pack")]), 0)
            self.assertTrue((project / "episodes" / "ep12" / "skills" / "ep12-insights" / "SKILL.md").exists())

    def test_ingest_missing_source_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            self.assertNotEqual(main(["ingest", "--project", str(project), "--slug", "ep12", "--source", str(project / "nope.txt")]), 0)


if __name__ == "__main__":
    unittest.main()
