"""S5 评测器（mock）：按触发词对 trigger.json 用例做确定性判定，产出 TEST_REPORT.md。"""

from __future__ import annotations

import json
from pathlib import Path

from .config import Config


TRIGGER_WORDS = ("播客", "金句", "失败清单", "该不该先做", "行动", "上期")


def _mock_judge(prompt: str) -> bool:
    return any(w in prompt for w in TRIGGER_WORDS)


def run_trigger_tests(build: Path, cfg: Config) -> Path:
    candidates = list((build / "skills").glob("*/tests/trigger.json"))
    if not candidates:
        raise FileNotFoundError(f"找不到 trigger.json（应位于 {build / 'skills' / '<skill>' / 'tests'}）")
    trigger_path = candidates[0]
    data = json.loads(trigger_path.read_text(encoding="utf-8"))
    cases = data["test_cases"]
    results: list[dict] = []
    bait_fail = 0
    pass_count = 0
    for case in cases:
        judge = _mock_judge(case["prompt"])
        if case["type"] == "should_trigger":
            ok = judge
            if not ok:
                bait_fail += 1
        elif case["type"] == "should_not_trigger":
            ok = not judge
            if not ok:
                bait_fail += 1
        else:
            ok = True
        if ok:
            pass_count += 1
        results.append(
            {
                "id": case["id"],
                "type": case["type"],
                "ok": ok,
                "prompt": case["prompt"][:60],
            }
        )
    rate = pass_count / len(cases) if cases else 0.0
    verdict = "PASS" if rate >= cfg.min_pass_rate and bait_fail <= cfg.bait_tolerance else "FAIL"
    lines = [
        "# TEST_REPORT.md",
        f"- 整体判定: {verdict}",
        f"- 通过率: {rate * 100:.1f}%（目标 ≥{cfg.min_pass_rate * 100:.0f}%）",
        f"- 诱饵失败: {bait_fail}（容忍 {cfg.bait_tolerance}）",
        "- 用例明细:",
    ]
    lines += [f"  - {r['id']} [{r['type']}] {'✅' if r['ok'] else '❌'} {r['prompt']}" for r in results]
    report = build / "TEST_REPORT.md"
    report.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return report
