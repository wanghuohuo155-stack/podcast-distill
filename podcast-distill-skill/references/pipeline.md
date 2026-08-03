# 流水线说明（S0–S6）

| 阶段 | 命令 | 做什么 | 闸门 |
|---|---|---|---|
| S0 | ingest | 复制转写文本 + 清单 | 非空、slug 合法 |
| S2 | extract | 按标记行提取五类候选 | provider=mock（规则） |
| S3 | verify | 引文定位 + 行动时间点 + 金句引号 | 无 unverified 要求由闸门执行 |
| S4 | check | 模板构造 SKILL.md + 六段校验 + trigger/证据 | 结构校验通过 |
| S5 | test | trigger 评测（mock 关键词判定） | 诱饵 0 容忍、通过率 ≥80% |
| S6 | package/gate | 打包 + 证据四件套 + TEST_REPORT PASS | 缺证据即拒绝 |

## 输入约定

转写建议嵌入结构化标记行：`[要点]` `[行动]` `[金句]` `[案例]` `[原则]`。
纯自由对话转写也能摄入，但提取率取决于文本可解析度（LLM provider 为 M2 增强项）。
