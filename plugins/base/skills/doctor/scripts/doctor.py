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

    elapsed = time.time() - t0
    ok_all = all(c["ok"] for c in checks)
    report = {
        "set": args.set,
        "version": spec.get("version") if spec else None,
        "mode": "L1",
        "ok": ok_all,
        "elapsed_seconds": round(elapsed, 3),
        "checks": checks,
        "missing_required_env": missing_env,
        "missing_optional_env": optional_missing if spec else [],
        "next": "可直接开始使用；需要冒烟验证时运行 doctor --live（L2，尚未实现）" if ok_all else "先补齐上面未通过项，不要宣称安装完成",
    }
    if args.live:
        report["live"] = "未实现：L2 冒烟检查留待后续版本，本次只完成了 L1"
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if ok_all else 1

if __name__ == "__main__":
    sys.exit(main())
