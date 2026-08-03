"""podcast-distill CLI 入口。"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from podcast.cli import main  # noqa: E402


if __name__ == "__main__":
    raise SystemExit(main())
