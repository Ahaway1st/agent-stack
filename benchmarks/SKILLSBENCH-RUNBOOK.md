# SkillsBench 运行手册（dev 套装）

状态：运行环境与口径已备好；实跑阻塞于模型凭据（见文末）。本文件锁定版本与子集规则，凭据到位后照此执行，不要临场改口径。

## 锁定版本
- Benchmark：SkillsBench **v1.1**（git tag `v1.1`，87 个任务，与 v1.0 同一 roster，改为原生 task.md 包格式）。
- 运行器：BenchFlow `>=0.6.3,<0.7`（registry.json 中 v1.1 条目声明的兼容范围）。
- 官方仓库：https://github.com/benchflow-ai/skillsbench（registry.json 在仓库根目录，含每个任务的 commit 与 digest 钉版）。
- 论文：arXiv:2602.12670。已知锚点：curated skills 全域平均 +16.2 个百分点，Software Engineering 域约 +4.5 个百分点。

## 子集规则（Software Eng. 子集）
- 域定义以论文 taxonomy 的 `software-engineering` 域为准（仓库 taxonomy.yaml 列出该域，但 registry 不带逐任务域标签）。
- 开跑前，从论文的任务表提取该域的完整任务清单，冻结写入本次运行记录（任务名 + registry digest），跑完后不许增删。
- 若分层抽样（PRD 11 节），抽样规则与随机种子同样先冻结再跑，并报告样本量。

## 条件与对照
- 同一 harness、同一模型、同一任务清单，两个条件各跑一遍：
  - 条件 A（基线）：只装 base 套装。
  - 条件 B（实验）：装 dev 套装（Claude Code 自动带 base；Codex 先 base 后 dev；DSH 用 install-dsh.sh dev）。
- 每次运行前用 doctor 确认套装状态（L1 必须全过；L2 脚本部分通过）。
- 指标：归一化增益 = (B − A) / (1 − A)（A、B 为任务通过率）；同时报告原始通过率、样本量与置信区间。
- 验收（PRD v1.1）：B 相对 A 正向且统计可分辨；≥20% 归一化增益为挑战目标，不作门槛。

## 开跑步骤（凭据到位后）
1. `git clone https://github.com/benchflow-ai/skillsbench.git && cd skillsbench && git checkout v1.1`
2. 按其 README 安装 BenchFlow（`uv` / pip，以仓库当前说明为准）。
3. 冻结子集清单（见上），分别在条件 A、B 下运行，轨迹与分数留档到本次运行目录。
4. 结果回填 BENCHMARKS.md 的实测表：套装、工具、模型、条件、样本量、通过率、归一化增益、置信区间、运行日期。

## 当前阻塞（2026-11-14 核查）
本机三个 harness 均无模型凭据：Claude Code 未登录、Codex 未登录、环境变量无 ANTHROPIC / OPENAI / DEEPSEEK 等 API key。补上任一凭据即可开跑，例如：
- 在这台机器上完成 `claude` 登录，或
- 提供一个可用的 API key（通过安全方式配置，不要写进仓库文件）。
VibeVideoBench 同理：代码与数据已放出（见 BENCHMARKS.md 更正），阻塞同为模型与生成服务凭据。
