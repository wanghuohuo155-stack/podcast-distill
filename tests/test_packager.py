import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "podcast-distill-skill" / "scripts"))

from podcast.packager import gate, package, validate_build_dir  # noqa: E402


def _make_build(root: Path, with_report: bool) -> Path:
    build = root / "demo"
    (build / "skills" / "demo-skill" / "tests").mkdir(parents=True)
    (build / "skills" / "demo-skill" / "SKILL.md").write_text("---\nname: demo-skill\ndescription: 演示\n---\n## R\n## I\n## A1\n## A2\n## E\n## B\n", encoding="utf-8")
    for name in ("PROVENANCE.md", "GLOSSARY.md", "INDEX.md"):
        (build / name).write_text("x", encoding="utf-8")
    if with_report:
        (build / "TEST_REPORT.md").write_text("# TEST_REPORT.md\n- 整体判定: PASS\n", encoding="utf-8")
    return build


class PackagerTest(unittest.TestCase):
    def test_missing_report_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            build = _make_build(Path(tmp), with_report=False)
            self.assertTrue(validate_build_dir(build))

    def test_pass_with_report(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            build = _make_build(Path(tmp), with_report=True)
            self.assertEqual(validate_build_dir(build), [])

    def test_package_and_gate(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            build = _make_build(root, with_report=True)
            pack = package(build, "demo-pack", "0.1.0", root / "packs")
            self.assertTrue((pack / "pack.json").exists())
            self.assertEqual(gate(pack), [])


if __name__ == "__main__":
    unittest.main()
