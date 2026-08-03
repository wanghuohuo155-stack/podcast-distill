"""项目配置：config.json 的加载、默认值与落盘。"""

from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass
from pathlib import Path


CONFIG_NAME = "config.json"


@dataclass
class Config:
    """引擎配置。所有阈值都有默认值，可在 config.json 中覆盖。"""

    project_dir: Path
    provider: str = "mock"  # mock | openai（openai 未实现，传入即报错）
    quote_max_chars: int = 150
    min_pass_rate: float = 0.80
    bait_tolerance: int = 0
    api_key_env: str = "OPENAI_API_KEY"
    base_url: str = ""
    model: str = ""

    def to_dict(self) -> dict:
        data = asdict(self)
        data["project_dir"] = str(self.project_dir)
        return data

    def save(self) -> None:
        self.project_dir.mkdir(parents=True, exist_ok=True)
        (self.project_dir / CONFIG_NAME).write_text(
            json.dumps(self.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8"
        )

    @classmethod
    def load(cls, project_dir: Path) -> "Config":
        cfg_path = Path(project_dir) / CONFIG_NAME
        data: dict = {}
        if cfg_path.exists():
            data = json.loads(cfg_path.read_text(encoding="utf-8"))
        data.pop("project_dir", None)
        known = {f for f in cls.__dataclass_fields__}
        for key in [k for k in data if k not in known]:
            data.pop(key)
        if os.environ.get("PODCAST_PROVIDER"):
            data["provider"] = os.environ["PODCAST_PROVIDER"]
        if os.environ.get("PODCAST_BASE_URL"):
            data["base_url"] = os.environ["PODCAST_BASE_URL"]
        if os.environ.get("PODCAST_MODEL"):
            data["model"] = os.environ["PODCAST_MODEL"]
        if os.environ.get("PODCAST_API_KEY_ENV"):
            data["api_key_env"] = os.environ["PODCAST_API_KEY_ENV"]
        return cls(project_dir=Path(project_dir).resolve(), **data)
