# 「podcast-distill」Skill — 终极目标、行动计划与落地方案

> 角色视角：10x 程序员 / Software Fellow
> 版本：v0.1（提案）| 日期：2026-08-03 | 状态：立项确认

## 0. 一句话定位

podcast-distill 能把播客/长音频转写文本蒸馏成可验证、可测试、可进化的播客知识 skill 包：自动提取洞见、行动、金句、案例与可复用原则，每条结论都能追溯到转写原文。

## 1. 为什么做（痛点）

- 播客动辄一小时，听完即忘，金句和行动建议沉没在音频里
- 转写文本又长又乱，人工整理成本高
- 跨集沉淀的原则（如"先写失败清单"）从未被复用

## 2. 终极目标与验收标准

```
Done when:
- [ ] python check.py 退出码 0
- [ ] 全部单元测试通过（unittest）
- [ ] 样例播客转写能跑通 extract → verify → check → test → package → gate
- [ ] 行动校验器：缺时间点的行动必须 unverified
- [ ] 金句校验器：未用引号包围的金句必须 unverified
- [ ] 发布审计清单全过（LICENSE 全文 / 无绝对路径 / 版本同步 / 敏感信息零命中）
- [ ] GitHub 仓库 podcast-distill 创建成功，main 推送成功，Pages 根 URL 返回 200
```

## 3. 核心方法论

流水线（按领域裁剪为 S0–S6）：

| 阶段 | 做什么 | 关键产物 | 闸门 |
|---|---|---|---|
| S0 摄入 | 读入转写文本 | source.txt + 清单 | 非空、元数据完整 |
| S2 提取 | 洞见/行动/金句/案例/原则 | candidates/*.json | 引文 ≤150 字 |
| S3 校验 | 引文定位 + 行动时间点 + 金句引号 | claims.jsonl | 逐字 verified |
| S4 构造 | 组装 SKILL.md | skills/*/SKILL.md | 六段结构校验 |
| S5 评测 | trigger 考试 | TEST_REPORT.md | 诱饵 0 容忍 |
| S6 打包/闸门 | pack + 安检 | packs/*/pack.json | 证据四件套 + TEST_REPORT PASS |

进化闭环（S10 简化）：telemetry.jsonl → proposals/（人工审批）。

## 4. 里程碑

- M0 骨架：目录、4 份 JSON Schema、引文/行动/金句校验器、CI 骨架
- M1 核心：CLI 全命令、mock 提取器（结构化标记）、评测、打包闸门
- M2 增强：LLM provider（自由对话提取）、真实播客验证、效果基线

## 5. 风险与对策

- 转写是自由对话，规则提取率低 → 输入约定先行：转写中嵌入 `[要点]`/`[行动]`/`[金句]` 标记行；无标记的自由文本归 M2 LLM provider
- 金句难以界定 → 校验器要求引号包围（`""` 或 `「」`），不满足即 unverified
- 行动无时间概念 → 校验器要求时间点（时间戳或相对时间词）

## 6. 命名与安装

- 文件夹名：podcast-distill
- 展示名：播客蒸馏
- 安装：$CODEX_HOME/skills/podcast-distill
