# 给 AI 的安装说明（Agent Stack）

使用者把本仓库链接和套装意图交给你，你负责完成安装、配置与自检，并按报告契约汇报。使用者不需要手动执行命令。

## 1. 意图映射
- 「开发套装 / dev」→ 安装 dev（依赖 base，见第 2 节的工具差异）
- 「视频套装 / video」→ 安装 video（依赖 base）
- 「全套 / 综合 / all」→ 安装 all
- 「基础 / base」→ 只装 base
- 未指定 → 先问一句要哪个套装，不要默认全装（综合套装上下文占用更高）

## 2. 工具探测与安装路由
先探测当前 harness，再选路：

- Claude Code（已实测，Claude Code 2.1.323，2026-11-14，本地源）：
  claude plugin marketplace add Ahaway1st/agent-stack
  claude plugin install <set>@agent-stack
  依赖在各 plugin 的 .claude-plugin/plugin.json 的 dependencies 中声明（如 dev → ["base"]），由 Claude Code 自动解析——实测 install dev@agent-stack 时自动带上 base（"+ 1 dependency: base"）。
- Codex（已实测，Codex CLI 0.164，2026-11-14，本地源）：
  codex plugin marketplace add Ahaway1st/agent-stack
  codex plugin add <set>@agent-stack
  已实测：Codex 不会自动解析 plugin 依赖——单独装 dev 后 base 仍显示未安装。所以装 dev/video/all 时，必须先显式装 base，再装目标套装。
- DeepSeek Harness (DSH)：把目标套装各 plugin 的 skills/ 目录复制或链接到 ~/.dsh/skills/（或项目 .dsh/skills/），MCP 配置写入 DSH 配置层。此路径未经 v1 实测，完成后必须用 doctor 验证，并在报告中标注「DSH 路径未验证」。
- 其他支持 skills CLI 的工具（回退路径）：
  npx skills add Ahaway1st/agent-stack --skill <set>
  marketplace 路径不可用时才走回退；回退后同样必须跑 doctor。注意：skills CLI 的 add 命令已实测存在，但 --skill 的套装语义未逐项验证，且它分发的是散装 SKILL.md，与 plugin 套装语义不完全等价，报告时要说明。

本地/离线测试可用本地路径代替 Ahaway1st/agent-stack 作为 marketplace 源。

## 3. 安装后强制自检（契约）
安装动作完成后，必须运行 doctor 的 L1 默认模式：
    python3 plugins/base/skills/doctor/scripts/doctor.py --set <set>
报告必须包含：套装名与版本、目标工具、已安装组件清单、L1 逐项结果、未满足的必需环境变量、下一步建议。
未通过 → 不宣称安装完成，按失败处理报告具体失败点。
--live（L2）仅在 L1 通过后、使用者需要时运行；v0.1 骨架版 L2 未实现，脚本会明确标注。

## 4. 密钥与敏感配置
仓库不内置、不存储任何密钥。缺失的环境变量列成「待使用者提供」清单，不要静默跳过、不要写占位值。套装中的 hooks / MCP 配置在安装前先摘要呈现给使用者。

## 5. 失败处理
marketplace 路径不可用（版本差异、权限）→ 回退 skills CLI 路径 → 仍失败则报告具体失败点，不宣称成功。
