# BENCHMARKS

按套装 × 工具 × 场景记录评测。原则：没有实测就写「未测」，不把公开 benchmark 的数字冒充本套装成绩。

## 本套装实测结果（v0.1 骨架）

| 套装 | 工具 | 场景 | 条件 | 指标 | 状态 |
|---|---|---|---|---|---|
| dev | Claude Code / Codex / DSH | SkillsBench Software Eng. 子集 | base vs dev | 归一化增益，v1.1 验收为正向且统计可分辨（≥20% 为挑战目标） | 未测（阻塞：本机无任何模型凭据，见下方补记） |
| video | Claude Code / Codex / DSH | VibeVideoBench 子集 | base vs video | L2 Pass (Strict) 提升，目标 ≥8 个百分点（或等效 Human Elo） | 未测（阻塞：同上） |
| all | 同上 | 开发+视频连续任务 | 专用套装分别装 vs all | 完成度差异、上下文占用、skill 选择错误率 | 未测 |

## 公开锚点（已核查，2026-11-14）

### SkillsBench（arXiv:2602.12670，2026-02）
- 86 个任务（论文 v1 口径）、11 个领域、7 个 agent-model 配置；curated skills 平均 +16.2 个百分点。
- 注意：Software Engineering 领域增幅只有约 +4.5 个百分点，是各域中偏弱的——dev 套装 ≥20% 归一化增益的目标定在 SE 子集上，难度显著高于全域平均，立项时要意识到这一点。
- PRD v1.0 曾引用的单模型数字（Opus 4.5 无 skills 22.0 → 有 skills 45.3、归一化约 29.9%；GPT-5.2 约 20.3%）未逐项核对到论文表格，且疑似为全域口径而非 SE 子集口径，已在 PRD v1.1 中删除，不再作锚点。

### VibeVideoBench（2026-10 发布，239 个任务）
- 官方 leaderboard：Claude Code + Opus 5.5 的 L2 Strict 76.3%，Codex CLI + GPT-6 Astra 74.5%——与 PRD 引用一致。
- 状态更正（2026-11-14 晚）：代码与数据已经放出——官方仓库 vibevideobench/vibevideobench 已公开，数据集在 Hugging Face（diaomuxi/vibevideobench，239 个任务，含任务、rubric 与测验）。此前「coming soon」是核查时的旧状态。仍成立的两点：未经同行评审、评审团包含参赛模型本身，引用分数时保留说明。
- PRD v1.0 曾引用的 DSH + DeepSeek-V4.1-Flash 57.6% 未在公开页面逐项核到，已在 PRD v1.1 中删除，核实前不作锚点。

## 路径与冒烟验证补记（2026-11-14 晚）

- skills CLI 回退路径已逐项验证：CLI 能从本仓库发现全部 13 个 skill；但 --skill 只认 skill 名、不认套装名（--skill dev 实测失败）。仓库已提供 scripts/install-skills-cli.sh 按 sets 定义展开安装，实测 dev 套装展开的 8 个 skill 全部正确落位（.agents/skills/）。
- doctor L2 子代理派发演练已完成一次：子代理按 dev 的 plan-spec skill 对玩具需求（给 doctor 加 --version）产出规格，六段格式齐全，文中引用的文件与版本事实均经真实读取核对（四个 sets 均为 0.2.0），结论 DRILL-OK。此为助理侧的等价演练，不等同于在 Claude Code / Codex 会话内的派发。
- DSH 模型侧终验仍未完成：尝试过 dsh web 的本地接口，未找到免凭据的 skill 目录端点（目录经会话内的 skill 工具向模型暴露）；终验需要 DeepSeek API key 跑一次真实会话。
- benchmark 实跑的统一阻塞（2026-11-14 核查）：本机 Claude Code、Codex 均未登录模型账号，环境变量中无 ANTHROPIC / OPENAI / DEEPSEEK 等 API key。SkillsBench 官方仓库（benchflow-ai/skillsbench）已拉取到本地待用；补上任一模型凭据后即可按上方口径开跑。

## 执行约定
- 套装内容变更时，重跑该套装对应子集，并报告样本量与置信区间，不把小样本差异读成确定性结论。
- 三个 harness 分别报告，不假设跨工具等价。
