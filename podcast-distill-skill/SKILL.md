---
name: podcast-distill
description: 播客蒸馏——把播客/长音频转写文本蒸馏成可验证、可测试、可进化的播客知识 skill 包。使用场景：把转写变成 skill、拆播客、播客蒸馏、从转写提取洞见/行动/金句/案例/原则并打包。不适用于：纯问答、普通文本归档。
---

# 播客蒸馏

把播客转写文本按 S0–S6 流水线蒸馏成 skill 包：摄入 → 提取（洞见/行动/金句/案例/原则）→ 引文/行动时间点/金句引号校验 → 构造 SKILL.md → trigger 评测 → 打包与发布闸门。

## 快速使用

```bash
python podcast-distill-skill/scripts/podcast-cli.py doctor
python podcast-distill-skill/scripts/podcast-cli.py init --project .
python podcast-distill-skill/scripts/podcast-cli.py ingest --project . --slug ep12 --source 转写.txt
python podcast-distill-skill/scripts/podcast-cli.py extract --project . --slug ep12
python podcast-distill-skill/scripts/podcast-cli.py verify --project . --slug ep12
python podcast-distill-skill/scripts/podcast-cli.py check --project . --slug ep12
python podcast-distill-skill/scripts/podcast-cli.py test --project . --slug ep12 --mode mock
python podcast-distill-skill/scripts/podcast-cli.py package --project . --slug ep12 --name podcast-pack
python podcast-distill-skill/scripts/podcast-cli.py gate --pack packs/podcast-pack
```

## 输入约定与校验规则

- 结构化标记行：`[要点]` `[行动]` `[金句]` `[案例]` `[原则]`（详见 references/input-convention.md）
- 引文必须逐字出现在转写原文
- 行动必须含时间点（时间戳或相对时间词），金句必须引号包围，否则 unverified
- SKILL.md 必须含 R/I/A1/A2/E/B 六段；发布前 TEST_REPORT 必须 PASS
