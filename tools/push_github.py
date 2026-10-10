# -*- coding: utf-8 -*-
"""push_github.py — 通过 GitHub REST API 把本项目推送为一次 commit。

为什么不用 git push：本机到 github.com:443 直连超时（被墙），
但 api.github.com 可达，因此走 Contents/Git Data API。

用法：
    python3 push_github.py "commit message"
需要：gh 已登录（取 token），或环境变量 GH_TOKEN。
"""
import base64
import json
import os
import subprocess
import sys
import urllib.request

REPO = "xiaozhameng/pay-knowledge"
BRANCH = "main"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

INCLUDE_DIRS = ["src", "tools"]
INCLUDE_FILES = ["index.html", "README.md", ".gitignore"]
EXCLUDE_PARTS = ("/_preview/", "/_smoke/", "_shots/", ".DS_Store")


def token():
    tok = os.environ.get("GH_TOKEN")
    if tok:
        return tok.strip()
    return subprocess.run(["gh", "auth", "token"], capture_output=True,
                          text=True).stdout.strip()


class Api:
    def __init__(self, tok):
        self.tok = tok
        self.n = 0

    def req(self, method, path, payload=None):
        self.n += 1
        url = "https://api.github.com/repos/%s/%s" % (REPO, path)
        data = json.dumps(payload).encode() if payload is not None else None
        r = urllib.request.Request(url, data=data, method=method)
        r.add_header("Authorization", "Bearer %s" % self.tok)
        r.add_header("Accept", "application/vnd.github+json")
        r.add_header("User-Agent", "pay-knowledge-pusher")
        try:
            with urllib.request.urlopen(r, timeout=60) as resp:
                body = resp.read().decode()
                return json.loads(body) if body else {}
        except urllib.error.HTTPError as e:
            print("HTTP %s on %s %s" % (e.code, method, path))
            print(e.read().decode()[:800])
            raise


def collect_files():
    files = []
    for f in INCLUDE_FILES:
        p = os.path.join(ROOT, f)
        if os.path.exists(p):
            files.append((f, p))
    for d in INCLUDE_DIRS:
        for base, _, names in os.walk(os.path.join(ROOT, d)):
            for n in sorted(names):
                p = os.path.join(base, n)
                rel = os.path.relpath(p, ROOT)
                if any(x in ("/" + rel + "/") for x in EXCLUDE_PARTS) or n == ".DS_Store":
                    continue
                files.append((rel.replace(os.sep, "/"), p))
    return sorted(set(files))


def main():
    msg = sys.argv[1] if len(sys.argv) > 1 else "update book"
    api = Api(token())
    files = collect_files()
    print("待推送 %d 个文件：" % len(files))
    for rel, p in files:
        print("   %-42s %6.1f KB" % (rel, os.path.getsize(p) / 1024))

    # 1. 分支最新 commit 与 tree
    ref = api.req("GET", "git/ref/heads/%s" % BRANCH)
    parent = ref["object"]["sha"]
    commit = api.req("GET", "git/commits/%s" % parent)
    base_tree = commit["tree"]["sha"]
    print("基线 commit:", parent[:10], "tree:", base_tree[:10])

    # 2. 逐文件建 blob
    tree_items = []
    for rel, p in files:
        with open(p, "rb") as fh:
            content = base64.b64encode(fh.read()).decode()
        blob = api.req("POST", "git/blobs",
                       {"content": content, "encoding": "base64"})
        tree_items.append({"path": rel, "mode": "100644", "type": "blob",
                           "sha": blob["sha"]})
        print("  blob ok:", rel)

    # 3. 建 tree / commit / 更新 ref
    tree = api.req("POST", "git/trees", {"base_tree": base_tree,
                                         "tree": tree_items})
    new_commit = api.req("POST", "git/commits", {
        "message": msg, "tree": tree["sha"], "parents": [parent]})
    api.req("PATCH", "git/refs/heads/%s" % BRANCH, {"sha": new_commit["sha"],
                                                    "force": False})
    print("推送完成 -> commit", new_commit["sha"][:10],
          "| 共 %d 次请求" % api.n)
    print("https://github.com/%s/commit/%s" % (REPO, new_commit["sha"]))


if __name__ == "__main__":
    main()
