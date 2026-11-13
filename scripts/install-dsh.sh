#!/usr/bin/env bash
# Agent Stack → DeepSeek Harness (dsh) 安装脚本
#
# dsh 没有 marketplace 机制；它用文件系统提供者按优先级扫描 skills 根：
#   项目 .dsh/skills（最高）→ 项目 .agents/skills → … → 用户 ~/.dsh/skills → ~/.agents/skills
# 本脚本把指定套装的 skills 按 sets/<set>.json 的顺序（base 在前）复制到目标根。
#
# 用法:
#   scripts/install-dsh.sh <base|dev|video|all> [--project] [--target DIR]
#     --project   装到当前项目的 ./.dsh/skills（默认装到 ~/.dsh/skills）
#     --target    显式指定目标目录（优先于 --project）
#
# 安全：只复制本仓库 plugins/*/skills/ 下的文件，不执行任何被复制的内容；
#       不写任何密钥。MCP 配置不走此脚本（dsh 的 MCP 是 Cordis 插件，需单独按 dsh 文档接入，
#       本仓库 v1 的套装暂无 MCP 组件）。
set -euo pipefail

SET="${1:-}"
if [[ -z "$SET" ]]; then
  echo "用法: install-dsh.sh <base|dev|video|all> [--project] [--target DIR]" >&2
  exit 2
fi
shift || true

TARGET=""
PROJECT=0
while [[ $# -gt 0 ]]; do
  case "$1" in
    --project) PROJECT=1 ;;
    --target) TARGET="${2:?--target 需要目录参数}"; shift ;;
    *) echo "未知参数: $1" >&2; exit 2 ;;
  esac
  shift
done

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SPEC="$ROOT/sets/$SET.json"
[[ -f "$SPEC" ]] || { echo "找不到套装定义: $SPEC" >&2; exit 1; }

if [[ -z "$TARGET" ]]; then
  if [[ "$PROJECT" == "1" ]]; then TARGET="$PWD/.dsh/skills"; else TARGET="$HOME/.dsh/skills"; fi
fi
mkdir -p "$TARGET"

# 按 sets/<set>.json 的 plugins 顺序逐个 plugin 复制其 skills/
PLUGINS="$(python3 -c "import json;print(' '.join(json.load(open('$SPEC'))['plugins']))")"
echo "套装: $SET（plugins: $PLUGINS）"
echo "目标: $TARGET"
COUNT=0
for plugin in $PLUGINS; do
  SRC="$ROOT/plugins/$plugin/skills"
  [[ -d "$SRC" ]] || { echo "缺失 skills 目录: $SRC" >&2; exit 1; }
  for skill_dir in "$SRC"/*/; do
    name="$(basename "$skill_dir")"
    rm -rf "${TARGET:?}/$name"
    cp -R "$skill_dir" "$TARGET/$name"
    echo "  installed: $name（from $plugin）"
    COUNT=$((COUNT+1))
  done
done
echo "完成: 共 $COUNT 个 skill 已写入 $TARGET"
echo "下一步: 在 dsh 中这些 skill 会被文件系统提供者自动发现（模型先看到 name + description，正文按需加载）。"
echo "自检: python3 \"$ROOT/plugins/base/skills/doctor/scripts/doctor.py\" --set $SET"
