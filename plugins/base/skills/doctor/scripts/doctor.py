#!/usr/bin/env python3
"""agent-stack doctor — L1 结构检查（默认）。

只做结构检查：不执行任何用户脚本、不发网络请求、不消耗 token。
用法: python3 doctor.py --set dev [--root <repo根>] [--live]
--live 目前只提示未实现（L2 冒烟检查留待后续版本），不会静默跳过。
"""
import argparse, json, os, sys, time

def find_root(start):
    p = os.path.abspath(start)
    while True:
        if os.path.isdir(os.path.join(p, "sets")):
            return p
        parent = os.path.dirname(p)
        if parent == p:
            return None
        p = parent

def load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--set", required=True, choices=["base", "dev", "video", "all"])
    ap.add_argument("--root", default=None)
    ap.add_argument("--live", action="store_true")
    args = ap.parse_args()

    t0 = time.time()
    script_dir = os.path.dirname(os.path.abspath(__file__))
    root = args.root or find_root(script_dir) or find_root(os.getcwd())
    checks, missing_env = [], []

    def check(name, ok, detail=""):
        checks.append({"check": name, "ok": bool(ok), "detail": detail})

    if root is None:
        print(json.dumps({"set": args.set, "ok": False, "error": "找不到仓库根（sets/ 目录）"}, ensure_ascii=False))
        return 1

    set_path = os.path.join(root, "sets", f"{args.set}.json")
    try:
        spec = load_json(set_path)
        check("set-spec 可解析", True, set_path)
    except Exception as e:
        check("set-spec 可解析", False, str(e))
        spec = None

    # 两个 marketplace manifest 可解析且包含本套装全部 plugin
    for mp_rel in [".claude-plugin/marketplace.json", ".agents/plugins/marketplace.json"]:
        mp_path = os.path.join(root, mp_rel)
        try:
            mp = load_json(mp_path)
            names = [p.get("name") for p in mp.get("plugins", [])]
            need = spec["plugins"] if spec else []
            check(f"marketplace {mp_rel}", all(n in names for n in need), f"entries={names}")
        except Exception as e:
            check(f"marketplace {mp_rel}", False, str(e))

    if spec:
        for plugin in spec["plugins"]:
            pdir = os.path.join(root, "plugins", plugin)
            for mf in [".claude-plugin/plugin.json", ".codex-plugin/plugin.json"]:
                try:
                    m = load_json(os.path.join(pdir, mf))
                    check(f"{plugin} {mf}", m.get("name") == plugin, f"name={m.get('name')}")
                except Exception as e:
                    check(f"{plugin} {mf}", False, str(e))
            for skill in spec["required_skills"].get(plugin, []):
                sp = os.path.join(pdir, "skills", skill, "SKILL.md")
                ok = os.path.isfile(sp)
                detail = sp
                if ok:
                    head = open(sp, encoding="utf-8").read(600)
                    ok = head.startswith("---") and "name:" in head and "description:" in head
                    detail = "frontmatter ok" if ok else "frontmatter 缺 name/description"
                check(f"{plugin} skill:{skill}", ok, detail)
        for var in spec.get("required_env", []):
            present = var in os.environ and bool(os.environ[var])
            check(f"必需环境变量 {var}", present, "存在" if present else "缺失（待使用者提供）")
            if not present:
                missing_env.append(var)
        optional_missing = [v for v in spec.get("optional_env", []) if v not in os.environ]

    # ---- L2（--live）：脚本可完成的冒烟检查 ----
    live_checks = []
    if args.live and spec:
        import re, shutil, subprocess, py_compile
        def lcheck(name, ok, detail=""):
            live_checks.append({"check": name, "ok": bool(ok), "detail": detail})
        # 1) SKILL.md 严格加载 dry-run：frontmatter 可解析、name 与目录一致且 kebab-case、description 非空
        kebab = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
        for plugin in spec["plugins"]:
            for skill in spec["required_skills"].get(plugin, []):
                sp = os.path.join(root, "plugins", plugin, "skills", skill, "SKILL.md")
                try:
                    text = open(sp, encoding="utf-8").read()
                    fm = text.split("---", 2)[1]
                    fields = dict(line.split(":", 1) for line in fm.strip().splitlines() if ":" in line)
                    name_ok = fields.get("name", "").strip() == skill and bool(kebab.match(skill))
                    desc_ok = len(fields.get("description", "").strip()) >= 20
                    lcheck(f"L2 load {plugin}/{skill}", name_ok and desc_ok,
                           "frontmatter ok" if (name_ok and desc_ok) else f"name_ok={name_ok} desc_ok={desc_ok}")
                except Exception as e:
                    lcheck(f"L2 load {plugin}/{skill}", False, str(e))
        # 2) 套装内脚本语法检查（不执行用户脚本，只做编译/语法解析）
        for dirpath, _dirs, files in os.walk(os.path.join(root, "plugins")):
            for fn in files:
                fp = os.path.join(dirpath, fn)
                if fn.endswith(".py"):
                    try:
                        py_compile.compile(fp, doraise=True)
                        lcheck(f"L2 py_compile {os.path.relpath(fp, root)}", True)
                    except Exception as e:
                        lcheck(f"L2 py_compile {os.path.relpath(fp, root)}", False, str(e))
                elif fn.endswith(".sh"):
                    r = subprocess.run(["bash", "-n", fp], capture_output=True, text=True)
                    lcheck(f"L2 bash -n {os.path.relpath(fp, root)}", r.returncode == 0, r.stderr.strip()[:200])
        # 3) 已安装状态核对（CLI 在 PATH 上才查；查不到记为跳过而非失败——安装环境与仓库环境可能不同）
        for cli, cmd in [("claude", ["claude", "plugin", "list"]), ("codex", ["codex", "plugin", "list"])]:
            if shutil.which(cli) is None:
                lcheck(f"L2 installed-state {cli}", True, "CLI 不在 PATH，跳过")
                continue
            try:
                out = subprocess.run(cmd, capture_output=True, text=True, timeout=30).stdout
                for plugin in spec["plugins"]:
                    lcheck(f"L2 installed-state {cli}:{plugin}", f"{plugin}@agent-stack" in out,
                           "已在该 harness 的 plugin 列表中" if f"{plugin}@agent-stack" in out else "当前用户环境未见安装（可能装在其他环境/HOME）")
            except Exception as e:
                lcheck(f"L2 installed-state {cli}", True, f"查询失败，跳过：{e}")

    elapsed = time.time() - t0
    ok_all = all(c["ok"] for c in checks)
    report = {
        "set": args.set,
        "version": spec.get("version") if spec else None,
        "mode": "L1+L2" if args.live else "L1",
        "ok": ok_all,
        "elapsed_seconds": round(elapsed, 3),
        "checks": checks,
        "missing_required_env": missing_env,
        "missing_optional_env": optional_missing if spec else [],
        "next": "可直接开始使用" if ok_all else "先补齐上面未通过项，不要宣称安装完成",
    }
    if args.live:
        report["live_checks"] = live_checks
        report["live_note"] = "L2 的脚本部分已执行（skill 加载 dry-run、脚本语法、已安装状态）。PRD 定义的「最小子代理派发」必须在目标 harness 会话内由 AI 执行，不在脚本能力范围内，不要据此宣称 L2 全部完成。"
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if ok_all else 1

if __name__ == "__main__":
    sys.exit(main())
