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
--live 做代表性 skill dry-run 与最小子代理派发（30–90s）。v0.1 骨架版尚未实现，脚本会明确标注，不静默跳过。
