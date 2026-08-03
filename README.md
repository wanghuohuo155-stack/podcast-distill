<h1 align="center">播客蒸馏 · podcast-distill</h1>

<p align="center">
  <b>把播客/长音频转写蒸馏成可验证、可测试、可进化的知识 Skill。</b>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.11%2B-3776AB" alt="Python 3.11+">
  <img src="https://img.shields.io/badge/Tests-17%20passed-2ea44f" alt="17 tests passed">
  <img src="https://img.shields.io/badge/Coverage-84%25-2ea44f" alt="coverage 84%">
  <img src="https://img.shields.io/badge/License-AGPL--3.0-orange" alt="AGPL-3.0">
</p>

---

播客听一小时，金句沉底？podcast-distill 把转写变成能复用的知识 skill：

1. **自动提取** —— 洞见、行动、金句、案例、可复用原则，一条命令
2. **机器校验** —— 引文逐字可定位；行动必须有时间点；金句必须引号包围
3. **可评测可进化** —— trigger 考试 + 误触发遥测 → 人工审批提案

## 快速开始

### 0. 环境要求

- Python 3.11+（仅标准库，无第三方依赖）

### 1. 克隆并自检

```bash
git clone https://github.com/wanghuohuo155-stack/podcast-distill.git
cd podcast-distill
python podcast-distill-skill/scripts/podcast-cli.py doctor
```

### 2. 初始化并摄入转写

```bash
python podcast-distill-skill/scripts/podcast-cli.py init --project .
python podcast-distill-skill/scripts/podcast-cli.py ingest --project . --slug ep12 --source 转写.txt --title "EP12：先写失败清单"
```

转写建议嵌入结构化标记行：`[要点]` `[行动]` `[金句]` `[案例]` `[原则]`
（详见 [references/input-convention.md](references/input-convention.md)）。

### 3. 蒸馏全流程（约 10 秒）

```bash
python podcast-distill-skill/scripts/podcast-cli.py extract --project . --slug ep12
python podcast-distill-skill/scripts/podcast-cli.py verify  --project . --slug ep12
python podcast-distill-skill/scripts/podcast-cli.py check   --project . --slug ep12
python podcast-distill-skill/scripts/podcast-cli.py test    --project . --slug ep12 --mode mock
python podcast-distill-skill/scripts/podcast-cli.py package --project . --slug ep12 --name podcast-pack
python podcast-distill-skill/scripts/podcast-cli.py gate    --pack packs/podcast-pack
```

## 流水线：S0 → S6

| 阶段 | 做什么 | 关键产物 | 闸门 |
|---|---|---|---|
| S0 | 摄入转写 | `episodes/<slug>/source.txt` | 非空、slug 合法 |
| S2 | 五类提取 | `candidates/*.json` | provider=mock（标记行规则） |
| S3 | 引文/行动/金句校验 | `claims.jsonl` | 引文逐字；行动有时间点；金句引号包围 |
| S4 | 构造 SKILL.md | `skills/*/SKILL.md` | R/I/A1/A2/E/B 六段 |
| S5 | trigger 考试 | `TEST_REPORT.md` | 诱饵 0 容忍，通过率 ≥80% |
| S6 | 打包 + 闸门 | `packs/*/pack.json` | 证据四件套 + TEST_REPORT PASS |

## 测试与验证

- 17 个单元测试（unittest）
- 最小可运行检查：`python check.py`
- 覆盖率 84%（门禁 ≥80%）
- CI：Python 3.11 / 3.12 矩阵（GitHub Actions）

## 项目结构

```text
podcast-distill/
├── README.md                  # 本文件
├── check.py                   # 最小可运行检查
├── specs/                     # 四份 JSON Schema（skill/claim/pack/test）
├── references/                # 输入约定（阶段 1 第 1 步）
├── podcast-distill-skill/     # skill 本体（自包含，可安装）
│   ├── SKILL.md               # meta-skill 定义
│   ├── scripts/podcast-cli.py # CLI 入口
│   ├── scripts/podcast/       # 引擎（纯标准库）
│   ├── assets/templates/      # SKILL.md 构造模板
│   └── references/            # 流水线说明
├── examples/                  # 样例转写
├── tests/                     # 17 个单元测试
└── .github/workflows/ci.yml   # CI
```

## 许可证

[AGPL-3.0](LICENSE)
