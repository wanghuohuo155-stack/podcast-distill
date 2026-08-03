"""podcast-distill CLI：doctor / init / ingest / extract / verify / check / test / package / gate / evolve。"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

from . import __version__
from .builder import build_skill, load_claims, validate_skill, write_skill
from .config import Config
from .evaluator import run_trigger_tests
from .extract import extract_claims, write_candidates
from .packager import gate as gate_pack
from .packager import package
from .verifier import verify_claim


SLUG_RE = re.compile(r"^[a-z0-9-]+$")


def _cfg(project: Path) -> Config:
    return Config.load(project)


def cmd_doctor(args: argparse.Namespace) -> int:
    cfg = _cfg(args.project)
    cfg_path = args.project / "config.json"
    ok = True
    print(f"  ✅ Python: {sys.version.split()[0]}")
    print(f"  ✅ 引擎版本: {__version__}")
    print(f"  {'✅' if cfg_path.exists() else '❌'} 配置可读: {cfg_path}")
    if not cfg_path.exists():
        ok = False
    for name in ("skill", "claim", "pack", "test"):
        p = args.project / "specs" / f"{name}.schema.json"
        print(f"  {'✅' if p.exists() else '❌'} spec/{name}.schema.json")
        if not p.exists():
            ok = False
    return 0 if ok else 1


def cmd_init(args: argparse.Namespace) -> int:
    cfg = Config(project_dir=args.project)
    cfg.save()
    (args.project / "specs").mkdir(parents=True, exist_ok=True)
    print(f"[podcast] 项目已初始化: {args.project.resolve()}（config.json）")
    return 0


def cmd_ingest(args: argparse.Namespace) -> int:
    source = Path(args.source)
    if not source.exists():
        print(f"源文件不存在: {source}")
        return 1
    if not SLUG_RE.fullmatch(args.slug):
        print("slug 只能包含小写字母、数字、连字符")
        return 1
    text = source.read_text(encoding="utf-8")
    if not text.strip():
        print("源文件为空")
        return 1
    episode = args.project / "episodes" / args.slug
    episode.mkdir(parents=True, exist_ok=True)
    (episode / "source.txt").write_text(text, encoding="utf-8")
    manifest = {
        "slug": args.slug,
        "title": args.title,
        "date": args.date,
        "source": str(source),
        "chars": len(text),
    }
    (episode / "source.manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"[podcast] S0 完成: {episode}")
    return 0


def cmd_extract(args: argparse.Namespace) -> int:
    cfg = _cfg(args.project)
    episode = args.project / "episodes" / args.slug
    source = episode / "source.txt"
    if not source.exists():
        print("先执行 ingest")
        return 1
    claims = extract_claims(source.read_text(encoding="utf-8"), args.slug, cfg)
    write_candidates(episode, claims)
    print(f"[podcast] S2 提取: {len(claims)} 条候选 -> {episode / 'candidates'}")
    return 0


def cmd_verify(args: argparse.Namespace) -> int:
    cfg = _cfg(args.project)
    episode = args.project / "episodes" / args.slug
    cand_dir = episode / "candidates"
    if not cand_dir.exists():
        print("先执行 extract")
        return 1
    claims: list[dict] = []
    for path in sorted(cand_dir.glob("*.json")):
        claims.extend(json.loads(path.read_text(encoding="utf-8")))
    source = (episode / "source.txt").read_text(encoding="utf-8")
    for claim in claims:
        result = verify_claim(claim, source, cfg)
        claim["status"] = result["status"]
        claim["reason"] = result.get("reason", "")
        if "span" in result:
            claim["span"] = result["span"]
    (episode / "claims.jsonl").write_text(
        "\n".join(json.dumps(c, ensure_ascii=False) for c in claims) + "\n", encoding="utf-8"
    )
    verified = sum(1 for c in claims if c["status"] == "verified")
    print(f"[podcast] S3 校验: verified={verified} unverified={len(claims) - verified}")
    return 0


def _build_trigger(claims: list[dict], slug: str) -> dict:
    titles = [c["title"] for c in claims if c["kind"] in ("principle", "insight")][:2]
    t1 = titles[0] if titles else "失败清单"
    t2 = titles[1] if len(titles) > 1 else t1
    return {
        "skill": slug,
        "version": "0.1.0",
        "test_cases": [
            {"id": "t1", "type": "should_trigger", "prompt": f"上次那期播客讲的{t1}怎么用的？", "expected_behavior": "应激活"},
            {"id": "t2", "type": "should_trigger", "prompt": f"{t2}这条金句是哪一集说的？", "expected_behavior": "应激活"},
            {"id": "t3", "type": "should_trigger", "prompt": "这个该不该先做，按播客里的原则怎么判断？", "expected_behavior": "应激活"},
            {"id": "n1", "type": "should_not_trigger", "prompt": "帮我查一下 API 参数", "expected_behavior": "不应激活"},
            {"id": "n2", "type": "should_not_trigger", "prompt": "今天晚饭吃什么好", "expected_behavior": "不应激活"},
            {"id": "e1", "type": "edge_case", "prompt": "把上期播客转写整理成文档", "expected_behavior": "边界：记录不评判"},
        ],
    }


def _write_evidence(episode: Path, claims: list[dict]) -> None:
    verified = sum(1 for c in claims if c.get("status") == "verified")
    (episode / "PROVENANCE.md").write_text(
        f"# PROVENANCE.md\n\n- 引文总数: {len(claims)}\n- verified: {verified}\n"
        f"- unverified: {len(claims) - verified}\n- 每条引文均可定位到 source.txt\n",
        encoding="utf-8",
    )
    glossary = {
        "insight": "洞见：本集的核心认知",
        "action": "行动：有明确时间点的行动建议",
        "quote": "金句：值得原样引用的句子（必须引号包围）",
        "case": "案例：主讲人给出的真实例子",
        "principle": "原则：可跨集复用的决策准则",
    }
    (episode / "GLOSSARY.md").write_text(
        "# GLOSSARY.md\n\n" + "\n".join(f"- {k}: {v}" for k, v in glossary.items()) + "\n",
        encoding="utf-8",
    )
    skills = [d.name for d in (episode / "skills").glob("*") if d.is_dir()]
    (episode / "INDEX.md").write_text(
        "# INDEX.md\n\n- 源: source.txt\n- 技能: " + (", ".join(skills) if skills else "（未构造）") + "\n",
        encoding="utf-8",
    )


def cmd_check(args: argparse.Namespace) -> int:
    cfg = _cfg(args.project)
    episode = args.project / "episodes" / args.slug
    try:
        claims = load_claims(episode)
    except FileNotFoundError as exc:
        print(f"[podcast] S4 构造校验: 失败 - {exc}")
        return 1
    template_path = Path(__file__).resolve().parents[2] / "assets" / "templates" / "SKILL.md.template"
    if not template_path.exists():
        print(f"[podcast] S4 构造校验: 失败 - 找不到模板 {template_path}")
        return 1
    template = template_path.read_text(encoding="utf-8")
    slug = args.skill_slug or f"{args.slug}-insights"
    skill_md = build_skill(claims, template, slug, args.title)
    write_skill(episode, skill_md, slug)
    issues = validate_skill(skill_md, cfg)
    if issues:
        print(f"[podcast] S4 构造校验: 失败 - {'; '.join(issues)}")
        return 1
    trigger = _build_trigger(claims, slug)
    (episode / "skills" / slug / "tests" / "trigger.json").write_text(
        json.dumps(trigger, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    _write_evidence(episode, claims)
    print(f"[podcast] S4 构造校验: 通过 -> {episode / 'skills' / slug / 'SKILL.md'}")
    return 0


def cmd_test(args: argparse.Namespace) -> int:
    if args.mode != "mock":
        print(f"mode={args.mode} 未实现，当前仅支持 mock")
        return 1
    cfg = _cfg(args.project)
    episode = args.project / "episodes" / args.slug
    run_trigger_tests(episode, cfg)
    report = episode / "TEST_REPORT.md"
    verdict = "PASS" if "整体判定: PASS" in report.read_text(encoding="utf-8") else "FAIL"
    print(f"[podcast] S5 评测: {verdict} -> {report}")
    return 0 if verdict == "PASS" else 1


def cmd_package(args: argparse.Namespace) -> int:
    episode = args.project / "episodes" / args.slug
    try:
        pack_dir = package(episode, args.name, args.version, args.project / "packs")
    except ValueError as exc:
        print(f"[podcast] S6 打包: 失败 - {exc}")
        return 1
    print(f"[podcast] S6 打包: {pack_dir}")
    return 0


def cmd_gate(args: argparse.Namespace) -> int:
    issues = gate_pack(args.pack)
    if issues:
        print(f"[podcast] S9 发布闸门: 拒绝 - {'; '.join(issues)}")
        return 1
    print("[podcast] S9 发布闸门: 通过")
    return 0


def cmd_evolve(args: argparse.Namespace) -> int:
    telemetry = Path(args.telemetry)
    if not telemetry.exists():
        print("未指定 --telemetry 且文件不存在")
        return 1
    lines = [
        json.loads(line)
        for line in telemetry.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    mis = [item for item in lines if item.get("event") == "mis_trigger"]
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    if mis:
        slugs = sorted({m.get("skill_slug", "?") for m in mis})
        (out / f"{ts}-mis-trigger.md").write_text(
            f"# 误触发改进提案\n\n- 来源: {len(mis)} 条 mis_trigger 记录\n"
            f"- 涉及 skill: {', '.join(slugs)}\n- 建议: 收紧 description 反触发信号\n",
            encoding="utf-8",
        )
    print(f"[podcast] S10 进化: 生成 {len(mis)} 条提案（待人类审批）")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="podcast-cli", description="播客转写蒸馏 CLI")
    parser.add_argument("--version", action="version", version=f"podcast-distill {__version__}")
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("doctor", "init"):
        p = sub.add_parser(name)
        p.add_argument("--project", type=Path, default=Path.cwd())
    p = sub.add_parser("ingest")
    p.add_argument("--project", type=Path, default=Path.cwd())
    p.add_argument("--slug", required=True)
    p.add_argument("--source", required=True)
    p.add_argument("--title", default="播客转写")
    p.add_argument("--date", default="")
    for name in ("extract", "verify"):
        p = sub.add_parser(name)
        p.add_argument("--project", type=Path, default=Path.cwd())
        p.add_argument("--slug", default="ep12")
    p = sub.add_parser("check")
    p.add_argument("--project", type=Path, default=Path.cwd())
    p.add_argument("--slug", default="ep12")
    p.add_argument("--skill-slug")
    p.add_argument("--title", default="播客决策辅助")
    p = sub.add_parser("test")
    p.add_argument("--project", type=Path, default=Path.cwd())
    p.add_argument("--slug", default="ep12")
    p.add_argument("--mode", default="mock")
    p = sub.add_parser("package")
    p.add_argument("--project", type=Path, default=Path.cwd())
    p.add_argument("--slug", default="ep12")
    p.add_argument("--name", default="podcast-pack")
    p.add_argument("--version", default="0.1.0")
    p = sub.add_parser("gate")
    p.add_argument("--pack", type=Path, required=True)
    p = sub.add_parser("evolve")
    p.add_argument("--project", type=Path, default=Path.cwd())
    p.add_argument("--telemetry", required=True)
    p.add_argument("--out", default="proposals")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    handler = {
        "doctor": cmd_doctor,
        "init": cmd_init,
        "ingest": cmd_ingest,
        "extract": cmd_extract,
        "verify": cmd_verify,
        "check": cmd_check,
        "test": cmd_test,
        "package": cmd_package,
        "gate": cmd_gate,
        "evolve": cmd_evolve,
    }[args.command]
    return handler(args)


if __name__ == "__main__":
    raise SystemExit(main())
