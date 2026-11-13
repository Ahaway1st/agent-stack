# BENCHMARKS

按套装 × 工具 × 场景记录评测。原则：没有实测就写「未测」，不把公开 benchmark 的数字冒充本套装成绩。

## 本套装实测结果（v0.1 骨架）

| 套装 | 工具 | 场景 | 条件 | 指标 | 状态 |
|---|---|---|---|---|---|
| dev | Claude Code / Codex / DSH | SkillsBench Software Eng. 子集 | base vs dev | 归一化增益，目标 ≥20% | 未测 |
| video | Claude Code / Codex / DSH | VibeVideoBench 子集 | base vs video | L2 Pass (Strict) 提升，目标 ≥8 个百分点（或等效 Human Elo） | 未测 |
| all | 同上 | 开发+视频连续任务 | 专用套装分别装 vs all | 完成度差异、上下文占用、skill 选择错误率 | 未测 |

## 公开锚点（已核查，2026-11-14）

### SkillsBench（arXiv:2602.12670，2026-02）
- 86 个任务（论文 v1 口径）、11 个领域、7 个 agent-model 配置；curated skills 平均 +16.2 个百分点。
- 注意：Software Engineering 领域增幅只有约 +4.5 个百分点，是各域中偏弱的——dev 套装 ≥20% 归一化增益的目标定在 SE 子集上，难度显著高于全域平均，立项时要意识到这一点。
- PRD v1.0 曾引用的单模型数字（Opus 4.5 无 skills 22.0 → 有 skills 45.3、归一化约 29.9%；GPT-5.2 约 20.3%）未逐项核对到论文表格，且疑似为全域口径而非 SE 子集口径，已在 PRD v1.1 中删除，不再作锚点。

### VibeVideoBench（2026-10 发布，239 个任务）
- 官方 leaderboard：Claude Code + Opus 5.5 的 L2 Strict 76.3%，Codex CLI + GPT-6 Astra 74.5%——与 PRD 引用一致。
- 风险：该 benchmark 截至核查时代码与数据为「coming soon」、未经同行评审、评审团包含参赛模型本身。在其代码/数据正式放出前，video 套装的评测可能无法实际执行，F8 的交付时间取决于它。
- PRD v1.0 曾引用的 DSH + DeepSeek-V4.1-Flash 57.6% 未在公开页面逐项核到，已在 PRD v1.1 中删除，核实前不作锚点。

## 执行约定
- 套装内容变更时，重跑该套装对应子集，并报告样本量与置信区间，不把小样本差异读成确定性结论。
- 三个 harness 分别报告，不假设跨工具等价。
