---
name: doctor
description: 套装自检：按 sets/<set>.json 做 L1 结构检查（skill 文件、plugin manifest、marketplace、必需环境变量存在性），<5s、不消耗 token、不执行用户脚本；--live 才做冒烟执行。安装完成后必须运行并报告，未通过不宣称安装完成。
---

# doctor

## 运行（L1，默认）
    python3 plugins/base/skills/doctor/scripts/doctor.py --set <base|dev|video|all>

在已安装的 plugin 环境中，用本 skill 所在目录的 scripts/doctor.py，并以 --root 指向套装仓库/安装根。

## 报告契约
向使用者报告：套装名与版本、目标工具、已安装组件清单、L1 逐项结果、未满足的必需环境变量（「待使用者提供」清单）、下一步建议。
必需密钥只检查存在性，不验证有效性，不把任何密钥值写进报告。

## L2
--live 执行脚本可完成的冒烟检查：每个必需 skill 的 frontmatter 严格解析与命名校验（加载 dry-run）、套装内脚本的语法检查、以及 Claude Code / Codex 当前用户环境的已安装状态核对。
PRD 定义的「最小子代理派发」必须在目标 harness 会话内由 AI 执行：L1+L2 脚本部分通过后，由 AI 在该会话里派发一个最小子代理、让它按某个已装 skill 的触发条件做一次无副作用的演练，再把结果补进报告。在此之前不要宣称 L2 全部完成。
