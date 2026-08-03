"""S3 校验器：引文逐字定位 + 行动时间点 + 金句引号。"""

from __future__ import annotations

import json
import re
from pathlib import Path

from .config import Config


def normalize(text: str) -> str:
    return re.sub(r"\s+", "", text)


def _quoted(text: str) -> bool:
    # 剥离 [金句] 标记前缀后，正文必须被引号包围
    body = re.sub(r"^\[[^\]]+\]\s*", "", text).strip()
    return (body.startswith('"') and body.endswith('"')) or (
        body.startswith("「") and body.endswith("」")
    )


def verify_claim(claim: dict, source: str, cfg: Config) -> dict:
    quote = claim.get("source_quote", "")
    if not quote:
        return {"status": "unverified", "reason": "缺少 source_quote"}
    if len(quote) > cfg.quote_max_chars:
        return {"status": "unverified", "reason": f"引文超过 {cfg.quote_max_chars} 字上限"}
    norm_source = normalize(source)
    norm_quote = normalize(quote)
    idx = norm_source.find(norm_quote)
    if idx < 0:
        return {"status": "unverified", "reason": "引文未在源文本中找到"}
    if claim.get("kind") == "action":
        if not claim.get("when"):
            return {"status": "unverified", "reason": "行动缺少时间点（时间戳或相对时间词）"}
    if claim.get("kind") == "quote":
        if not _quoted(quote):
            return {"status": "unverified", "reason": "金句必须用引号（\"\" 或 「」）包围"}
    return {"status": "verified", "span": [idx, idx + len(norm_quote)]}


def verify_claims_file(claims_path: Path, source: str, cfg: Config) -> list[dict]:
    if not claims_path.exists():
        raise FileNotFoundError(f"找不到 claims 文件: {claims_path}")
    claims = [
        json.loads(line)
        for line in claims_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    results = []
    for claim in claims:
        result = verify_claim(claim, source, cfg)
        result["claim_id"] = claim.get("claim_id", "?")
        result["source_quote"] = claim.get("source_quote", "")
        results.append(result)
    return results
