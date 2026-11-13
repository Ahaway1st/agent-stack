# Agent Stack — AI 工具「套装化」安装仓库

一个「交给 AI 就装」的套装仓库：把仓库链接和目标（开发 / 视频 / 综合）告诉 AI 工具，AI 自行完成 skills、plugins、MCP 的安装、配置与自检；每个套装附带基于公开 benchmark 的能力增幅目标，见 [BENCHMARKS.md](BENCHMARKS.md)。产品定义见 [PRD.md](PRD.md)（v1.1，2026-11-14；v1.0 原文归档于 PRD-v1.0.md）。

## 套装

| 套装 ID | 名称 | 定位 | 依赖 |
|---|---|---|---|
| base | 基础套装 | 文件/检索增强、长任务状态管理、doctor 自检 | 无 |
| dev | AI 软件开发套装 | 规划 → TDD 实现 → 审查/CI 的开发链路 | base |
| video | AI 视频创作套装 | brief → 分镜/提示词 → 生成编排 → FFmpeg 后期交付 | base |
| all | 综合套装 | base+dev+video 并集 + 跨场景路由；上下文占用更高，不适合只做单一场景 | base、dev、video |

## 使用方式

对你的 AI 工具说一句即可，例如：「照这个仓库装，装开发套装：https://github.com/Ahaway1st/agent-stack」。AI 应读取 [AGENTS.md](AGENTS.md) 执行：注册 marketplace → 安装套装 → 运行 doctor L1 自检 → 按契约报告。

手动等价命令（供排查）：

- Claude Code：`claude plugin marketplace add Ahaway1st/agent-stack` 然后 `claude plugin install <set>@agent-stack`（依赖由 plugin.json 的 dependencies 自动解析）
- Codex：`codex plugin marketplace add Ahaway1st/agent-stack` 然后 `codex plugin add <set>@agent-stack`（Codex 侧先装 base 再装目标套装）

## 支持边界（v1）

- 首要支持：Claude Code、Codex CLI、DeepSeek Harness (DSH)。
- 验证状态（2026-11-14，本地源实测；GitHub 远程源待仓库推送后复测）：
  - Claude Code 2.1.323：marketplace validate 通过；install dev 自动带上 base 依赖 ✔
  - Codex CLI 0.164：marketplace add / plugin add 均可装；但**不自动解析依赖**，需先装 base ✔（差异已写入 AGENTS.md）
  - doctor L1：四套全部通过，单套检查约 0.001s ✔
  - DSH 路径、skills CLI 回退路径：**尚未实测**，使用时以 doctor 报告为准，不要预设成功。
- 仓库不内置任何密钥；缺失的环境变量会由 doctor 列为「待使用者提供」。
- v1 安装是一次性快照，不做自动更新。

## 自检

    python3 plugins/base/skills/doctor/scripts/doctor.py --set dev

L1 结构检查 <5s、不消耗 token、不执行用户脚本，覆盖率目标 100%（套装声明的必需组件）。L2（--live）冒烟检查在后续版本实现。
