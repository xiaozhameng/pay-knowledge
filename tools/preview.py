# -*- coding: utf-8 -*-
"""preview.py — 把指定（或全部）图表渲染成一个可直接截图的 HTML 页面。

用法：
    python3 preview.py intro_case_tree eco_sys_map      # 只渲染这两张
    python3 preview.py                                  # 渲染全部
输出：
    tools/_preview/index.html      （每张图一屏，带图名标题）
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from figs import build_figs  # noqa: E402

names = sys.argv[1:]
figs = build_figs()
if names:
    picked = [(n, figs[n]) for n in names if n in figs]
    missing = [n for n in names if n not in figs]
    if missing:
        print("未找到:", missing)
else:
    picked = sorted(figs.items())

out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_preview")
os.makedirs(out_dir, exist_ok=True)

cards = []
for name, svg in picked:
    cards.append(
        '<div class="card"><div class="nm">%s</div>%s</div>' % (name, svg)
    )

html = """<!DOCTYPE html><html><head><meta charset="utf-8"><title>图表巡检</title>
<style>
body{margin:0;background:#dfe3ea;font-family:'PingFang SC',sans-serif}
.card{background:#fff;margin:0;padding:0;border-bottom:6px solid #dfe3ea}
.nm{font:600 13px/1 'PingFang SC',sans-serif;color:#12306b;padding:8px 14px;background:#cdd6e3}
.svg-fig{display:block;width:100%;height:auto}
</style></head><body>
__CARDS__
</body></html>""".replace("__CARDS__", "".join(cards))

p = os.path.join(out_dir, "index.html")
open(p, "w", encoding="utf-8").write(html)
print("渲染 %d 张 → %s" % (len(picked), p))
