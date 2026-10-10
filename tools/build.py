# -*- coding: utf-8 -*-
"""
build.py — 把 src/parts/*.html + 图表 + 模板组装成 index.html

为什么要有构建脚本？
  图是 Python 生成的 SVG，正文是 HTML 片段；两者通过占位符连接：
      <!--FIG:fig_id-->  会被替换成 figs.py 里对应名字的 SVG
  这样改图不用动正文，改正文不用动图，最后一键合成单文件电子书。

章节元数据约定：每个 part 文件第一行写
  <!-- meta: id=ch-01 | grp=第一篇 · 基础与监管 | label=第1章 支付的本质与全景 -->
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

from figs import build_figs          # noqa: E402

SRC = os.path.join(ROOT, "src")
PARTS = os.path.join(SRC, "parts")
OUT = os.path.join(ROOT, "index.html")


def read(p):
    with open(p, encoding="utf-8") as f:
        return f.read()


def main():
    figs = build_figs()
    template = read(os.path.join(SRC, "template.html"))

    files = sorted(f for f in os.listdir(PARTS) if f.endswith(".html"))
    if not files:
        print("!! src/parts 下没有章节文件");  return 1

    chapters, bodies = [], []
    for fn in files:
        html = read(os.path.join(PARTS, fn))
        m = re.search(r"<!--\s*meta:\s*(.+?)-->", html)
        if not m:
            print("!! 缺少 meta 注释:", fn);  return 1
        meta = dict(kv.strip().split("=", 1) for kv in m.group(1).split("|"))
        html = re.sub(r"<!--\s*meta:\s*.+?-->\s*", "", html, count=1)
        # 替换图表占位符
        def sub_fig(mo):
            name = mo.group(1)
            if name not in figs:
                raise SystemExit("!! 图不存在: %s (在 %s)" % (name, fn))
            return figs[name]
        html = re.sub(r"<!--FIG:([A-Za-z0-9_]+)-->", sub_fig, html)
        # 检查是否还有未替换的占位
        left = re.findall(r"<!--FIG:[A-Za-z0-9_]+-->", html)
        if left:
            raise SystemExit("!! 占位符未替换: %s" % left)
        chapters.append(meta)
        bodies.append(html)

    # 封面
    cover_path = os.path.join(SRC, "cover.html")
    cover = read(cover_path) if os.path.exists(cover_path) else ""

    html = (template
            .replace("{{BOOK_TITLE}}", "支付通识 · 精修版")
            .replace("{{BOOK_SHORT}}", "支付通识")
            .replace("{{BOOK_SUB}}", "基于真实世界的一本支付小书 · 精修版")
            .replace("{{COVER}}", cover)
            .replace("{{CHAPTERS}}", "\n".join(bodies))
            .replace("{{CHAPTERS_JSON}}", __import__("json").dumps(
                [dict(id=c["id"], label=c["label"], grp=c.get("grp", "")) for c in chapters],
                ensure_ascii=False)))

    with open(OUT, "w", encoding="utf-8") as f:
        f.write(html)
    n_fig = len(figs)
    print("构建完成 ->", OUT)
    print("  章节: %d | 图表: %d | 大小: %.1f KB"
          % (len(chapters), n_fig, os.path.getsize(OUT) / 1024))
    return 0


if __name__ == "__main__":
    sys.exit(main())
