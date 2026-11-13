#!/usr/bin/env bash
# Agent Stack → skills CLI（Vercel Labs）回退安装脚本
#
# 实测结论（2026-11-14，skills CLI 当前版本）：
# - CLI 能从本仓库发现全部 13 个 skill（嵌套在 plugins/<set>/skills/ 下也能找到）。
# - 但 --skill 只认 skill 名，不认套装名：--skill dev 会失败并列出可用 skill 清单。
# - 因此本脚本按 sets/<set>.json 把套装展开为逐个 skill 名来装（含 base 的 skill，
#   因为回退路径没有 plugin 依赖解析，少装 base 是最常见的错误）。
# 装好的 skill 落在当前项目的 .agents/skills/（及所选 agent 的目录），是散装 SKILL.md，
# 与 plugin 路径的语义差异：没有 plugin 版本管理与依赖关系，更新靠 skills update。
#
# 用法: scripts/install-skills-cli.sh <base|dev|video|all> [--global]
set -euo pipefail

SET="${1:-}"
if [[ -z "$SET" ]]; then
  echo "用法: install-skills-cli.sh <base|dev|video|all> [--global]" >&2
  exit 2
fi
GLOBAL_FLAG=""
[[ "${2:-}" == "--global" ]] && GLOBAL_FLAG="-g"

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SPEC="$ROOT/sets/$SET.json"
[[ -f "$SPEC" ]] || { echo "找不到套装定义: $SPEC" >&2; exit 1; }

mapfile -t SKILLS < <(python3 -c "
import json
spec = json.load(open('$SPEC'))
seen = []
for plugin in spec['plugins']:
    for s in spec['required_skills'].get(plugin, []):
        if s not in seen:
            seen.append(s)
print('\n'.join(seen))
")
echo "套装 $SET 展开为 ${#SKILLS[@]} 个 skill: ${SKILLS[*]}"

ARGS=()
for s in "${SKILLS[@]}"; do ARGS+=(--skill "$s"); done
# shellcheck disable=SC2086
npx -y skills add Ahaway1st/agent-stack "${ARGS[@]}" $GLOBAL_FLAG -y
echo "完成。自检: 在目标工具中确认上述 skill 可见；散装路径无 doctor 依赖解析，缺哪个补哪个（重跑本脚本即可）。"
