# -*- coding: utf-8 -*-
"""
svgkit.py — 《支付通识·精修版》图表生成工具
================================================================

为什么需要它（而不是直接手写 SVG）？
----------------------------------------------------------------
原版电子书的图是"人工推算坐标"：每根线、每个框的 x/y 都要作者自己算。
只要文字长度一变、节点一增删，连线就会错位——出现箭头从两个方框之间的
缝隙穿过、文字溢出方框边界、分支线不指向节点中心等问题。

本工具把"排布"这件事交给算法：

  · box()      —— 方框内文字自动折行、超长自动缩字号，永不溢出
  · Sequence   —— 时序图：自动分配泳道宽度、自动排消息行距、自动画生命线
  · Layers     —— 分层流程图/决策树：自动水平均分、汽车总线式连线
  · Arch       —— 分层架构图：左侧层名 + 右侧均分盒子

所有图元都使用**内联样式**而非 CSS class，因此同一页面里嵌几十张图也不会
互相污染样式；箭头用手绘三角 path 而不是 <marker>，避免多图 id 冲突。

作者：WorkBuddy   许可：随书自由使用
"""

from html import escape as _esc
import re
import math

__all__ = ["T", "KIND", "uid", "tw", "wrap", "box", "arrow", "elbow", "poly",
           "label", "badge", "Sequence", "Layers", "Arch", "Compare", "svg_page"]

# --------------------------------------------------------------------------
# 主题：全书统一的色板（浅色纸质风格，深蓝 + 金 主色）
# --------------------------------------------------------------------------
T = dict(
    navy="#101d33", navy2="#1b2f4d", navy3="#243c5e",
    gold="#c9a227", gold2="#e3c25a",
    ink="#1c2430", ink2="#445060", muted="#6b7686",
    paper="#fffdf8", sand="#f1eee6",
    blue="#2f6fb0", blue_bg="#eef3f8",
    green="#2f8f5b", green_bg="#eef7f1",
    red="#c4483f", red_bg="#fdf1ef",
    amber="#c07f1b", amber_bg="#fdf6e8",
    line="#d8d2c6", gray="#8a97a8",
    purple="#6b4fa0", purple_bg="#f2eefa",
)

# kind -> (填充, 描边, 文字色, 默认字重)
KIND = {
    "sys":     (T["blue_bg"],   T["blue"],   T["navy"], 600),
    "neutral": (T["sand"],      T["navy3"],  T["navy"], 600),
    "gold":    (T["amber_bg"],  T["gold"],   T["navy"], 600),
    "ok":      (T["green_bg"],  T["green"],  T["navy"], 600),
    "warn":    (T["amber_bg"],  T["amber"],  T["navy"], 600),
    "risk":    (T["red_bg"],    T["red"],    T["navy"], 600),
    "dark":    (T["navy"],      T["navy"],   "#ffffff", 600),
    "dark2":   (T["navy2"],     T["navy2"],  "#ffffff", 600),
    "ghost":   ("#ffffff",      T["gray"],   T["ink2"], 500),
    "purple":  (T["purple_bg"], T["purple"], T["navy"], 600),
    "plain":   ("#ffffff",      T["line"],   T["ink2"], 500),
}

_FONT = "'Noto Sans SC','PingFang SC','Microsoft YaHei',system-ui,sans-serif"

_i = [0]


def uid(p="u"):
    """生成全局唯一 id 前缀（同一页面多图共存时用）。"""
    _i[0] += 1
    return "%s%d" % (p, _i[0])


# --------------------------------------------------------------------------
# 文本度量与折行
# --------------------------------------------------------------------------
def tw(s, fs):
    """估算字符串像素宽度：CJK 记 1.0em，半角记 0.56em。"""
    w = 0.0
    for ch in s:
        w += fs * (1.0 if ord(ch) > 0x2E7F else 0.56)
    return w


_TOKEN = re.compile(r"[A-Za-z0-9][A-Za-z0-9\.\-_/:+]*|.", re.S)


def wrap(text, fs, maxw):
    """按像素宽度折行，尽量不切断英文单词。"""
    out = []
    for para in str(text).split("\n"):
        if not para:
            out.append("")
            continue
        cur = ""
        for tok in _TOKEN.findall(para):
            if tok.isspace() and not cur:
                continue
            if tw(cur + tok, fs) <= maxw or not cur:
                cur += tok
            else:
                out.append(cur.rstrip())
                cur = "" if tok.isspace() else tok
        out.append(cur.rstrip())
    return out


# --------------------------------------------------------------------------
# 基础图元
# --------------------------------------------------------------------------
def _e(s):
    return _esc(str(s), quote=False)


def label(x, y, text, fs=12, color=None, anchor="middle", bold=False, italic=False,
          dy=0, op=None):
    color = color or T["ink"]
    st = ' font-style="italic"' if italic else ''
    o = ' opacity="%s"' % op if op is not None else ''
    return ('<text x="%.1f" y="%.1f" font-size="%.1f" fill="%s" text-anchor="%s" '
            'font-weight="%d"%s%s>%s</text>'
            % (x, y + dy, fs, color, anchor, 700 if bold else 400, st, o, _e(text)))


def lines_text(x, y, items, fs=12, color=None, anchor="middle", lh=None, bold_first=False):
    """多行文字，items 为字符串列表；返回 SVG。"""
    lh = lh or fs * 1.5
    out = []
    for i, s in enumerate(items):
        c = T["navy"] if (bold_first and i == 0) else (color or T["ink2"])
        b = bold_first and i == 0
        out.append(label(x, y + i * lh, s, fs=fs, color=c, anchor=anchor, bold=b))
    return "".join(out)


def box(x, y, w, h, text="", sub="", kind="sys", fs=13, subfs=11, rx=9,
        stroke_w=1.4, dash=None, bold=None, align="center", pad=9, sub_color=None,
        shadow=False):
    """
    画一个带文字的方框。文字自动折行、过高自动缩字号（这是原版最大的坑）。
    text 主标题，sub 副标题（可含 \n）。
    """
    fill, stroke, tcol, w0 = KIND.get(kind, KIND["sys"])
    bold = w0 if bold is None else bold
    maxw = w - 2 * pad
    rows = []
    if text:
        for ln in wrap(text, fs, maxw):
            rows.append((ln, fs, bold, tcol))
    if sub:
        # 深色底上的副标题若用默认墨色会几乎不可见，这里按底色自动切换
        dcol = sub_color or ("#c9d3e0" if kind in ("dark", "dark2") else T["ink2"])
        for ln in wrap(sub, subfs, maxw):
            rows.append((ln, subfs, 400, dcol))
    if not rows:
        rows = [("", fs, 400, tcol)]
    rows = [r for r in rows]
    lh = lambda f: f * 1.46
    total = sum(lh(f) for _, f, _, _ in rows)
    limit = h - 10
    if total > limit:                      # 内容超高：等比缩字号
        k = max(0.58, limit / total)
        rows = [(t, f * k, b, c) for t, f, b, c in rows]
        total = sum(lh(f) for _, f, _, _ in rows)
    cy = y + (h - total) / 2.0
    o = ['<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="%s" fill="%s" '
         'stroke="%s" stroke-width="%s"%s%s/>'
         % (x, y, w, h, rx, fill, stroke, stroke_w,
            ' stroke-dasharray="%s"' % dash if dash else '',
            ' filter="url(#%s)"' % _SHADOW_ID if shadow else '')]
    for t, f, b, c in rows:
        cy += lh(f)
        ty = cy - lh(f) * 0.30
        if align == "center":
            o.append('<text x="%.1f" y="%.1f" font-size="%.1f" fill="%s" '
                     'text-anchor="middle" font-weight="%d">%s</text>'
                     % (x + w / 2, ty, f, c, b, _e(t)))
        else:  # left
            o.append('<text x="%.1f" y="%.1f" font-size="%.1f" fill="%s" '
                     'text-anchor="start" font-weight="%d">%s</text>'
                     % (x + pad, ty, f, c, b, _e(t)))
    return "".join(o)


_SHADOW_ID = None


def _head(x, y, angle, color, size=7.0):
    """在 (x,y) 处画一个指向 angle 方向的实心三角箭头（不用 marker，避免 id 冲突）。"""
    a = math.radians(angle)
    p2 = (x - size * math.cos(a - 0.40), y - size * math.sin(a - 0.40))
    p3 = (x - size * math.cos(a + 0.40), y - size * math.sin(a + 0.40))
    return ('<path d="M%.1f %.1f L%.1f %.1f L%.1f %.1f Z" fill="%s"/>'
            % (x, y, p2[0], p2[1], p3[0], p3[1], color))


def arrow(x1, y1, x2, y2, color=None, dash=None, w=1.5, head=True, head_size=7.0):
    """直线箭头。"""
    color = color or T["gray"]
    ang = math.degrees(math.atan2(y2 - y1, x2 - x1))
    ox, oy = (math.cos(math.radians(ang)) * (head_size - 1),
              math.sin(math.radians(ang)) * (head_size - 1)) if head else (0, 0)
    o = ['<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" '
         'stroke-width="%s"%s%s/>'
         % (x1, y1, x2 - ox, y2 - oy, color, w,
            ' stroke-dasharray="%s"' % dash if dash else '',
            ' stroke-linecap="round"')]
    if head:
        o.append(_head(x2, y2, ang, color, head_size))
    return "".join(o)


def poly(points, color=None, dash=None, w=1.5, head=True, head_size=7.0):
    """折线箭头，points=[(x,y),...]。"""
    color = color or T["gray"]
    d = "M" + " L".join("%.1f %.1f" % p for p in points)
    o = ['<path d="%s" fill="none" stroke="%s" stroke-width="%s"%s '
         'stroke-linejoin="round" stroke-linecap="round"/>'
         % (d, color, w, ' stroke-dasharray="%s"' % dash if dash else '')]
    if head and len(points) >= 2:
        (x1, y1), (x2, y2) = points[-2], points[-1]
        ang = math.degrees(math.atan2(y2 - y1, x2 - x1))
        o.append(_head(x2, y2, ang, color, head_size))
    return "".join(o)


def elbow(x1, y1, x2, y2, mode="hv", color=None, dash=None, w=1.5, head=True,
          head_size=7.0, bend=None):
    """直角折线：mode='hv' 先横后竖，'vh' 先竖后横。"""
    if mode == "hv":
        pts = [(x1, y1), (bend if bend is not None else x2, y1), (bend if bend is not None else x2, y2)]
        pts = [(x1, y1), ((bend if bend is not None else x2), y1), (x2, y2)]
    else:
        pts = [(x1, y1), (x1, (bend if bend is not None else y2)), (x2, y2)]
    return poly(pts, color=color, dash=dash, w=w, head=head, head_size=head_size)


def badge(x, y, text, kind="dark", fs=11, padx=9, h=20, anchor="middle", rx=10):
    """小徽章/标签。x 为锚点。返回 (svg, width)。"""
    w = tw(text, fs) + padx * 2
    x0 = x - w / 2 if anchor == "middle" else (x if anchor == "start" else x - w)
    fill, stroke, tcol, _ = KIND.get(kind, KIND["dark"])
    o = ('<rect x="%.1f" y="%.1f" width="%.1f" height="%d" rx="%d" fill="%s" '
         'stroke="%s" stroke-width="1"/>' % (x0, y, w, h, rx, fill, stroke))
    o += ('<text x="%.1f" y="%.1f" font-size="%d" fill="%s" text-anchor="middle" '
          'font-weight="600">%s</text>' % (x0 + w / 2, y + h * 0.70, fs, tcol, _e(text)))
    return o, w


def svg_page(w, h, body, aria="", shadow_def=True):
    """包一层 <svg>。"""
    global _SHADOW_ID
    sid = uid("sh")
    if shadow_def:
        _SHADOW_ID = sid
    defs = ('<defs><filter id="%s" x="-20%%" y="-20%%" width="140%%" height="150%%">'
            '<feDropShadow dx="0" dy="2" stdDeviation="3" flood-color="#101d33" '
            'flood-opacity="0.10"/></filter></defs>' % sid) if shadow_def else ''
    return ('<svg class="svg-fig" viewBox="0 0 %d %d" role="img" aria-label="%s" '
            'font-family="%s">%s<rect width="%d" height="%d" fill="%s"/>%s</svg>'
            % (w, h, _e(aria), _FONT, defs, w, h, T["paper"], body))


# --------------------------------------------------------------------------
# 时序图
# --------------------------------------------------------------------------
class Sequence:
    """
    时序图。自动做三件事：
      1. 每个参与者的泳道宽度 = 其标题盒所需宽度（不再挤压文字）
      2. 消息行距自动堆叠，长标签自动折行
      3. 生命线从顶到底自动贯通

    actors: [dict(name=, sub=, kind=)] 或 [(name, sub), ...] 或 [name, ...]
    msg(a, b, text, kind)  kind: req 请求 / res 响应 / fund 资金 / sys 系统内部
    self_msg(a, text)
    note(a, b, text)     跨参与者注释
    group(a, b, text)    跨参与者分组框（如"担保期""断直连后"）
    gap(h)               人为留白
    """

    def __init__(self, actors, msg_h=50, top=98, bottom=54, margin=34,
                 lane_min=136, note_h=0, show_actors_bottom=True, title=None):
        self.actors = []
        for a in actors:
            if isinstance(a, str):
                self.actors.append(dict(name=a, sub="", kind="sys"))
            elif isinstance(a, dict):
                self.actors.append(dict(name=a.get("name", ""), sub=a.get("sub", ""),
                                        kind=a.get("kind", "sys")))
            else:
                self.actors.append(dict(name=a[0], sub=a[1] if len(a) > 1 else "",
                                        kind="sys"))
        self.msg_h = msg_h
        self.top = top + (22 if title else 0)
        self.bottom = bottom
        self.margin = margin
        self.lane_min = lane_min
        self.show_bottom = show_actors_bottom
        self.title = title
        self.items = []          # 顺序化的元素
        self._need = [0] * len(self.actors)

    # ---- 布局 ----
    def _compute_x(self):
        n = len(self.actors)
        bw = []
        for i, a in enumerate(self.actors):
            t = max(tw(a["name"], 13), tw(a["sub"], 10.5) if a["sub"] else 0)
            bw.append(max(t + 26, 108))
        lw = [max(bw[i], self.lane_min) for i in range(n)]
        xs, cx = [], self.margin
        for i in range(n):
            xs.append(cx)
            cx += lw[i]
        self.lane_x, self.lane_w = xs, lw
        self.cx = [xs[i] + lw[i] / 2.0 for i in range(n)]
        self.W = int(cx + self.margin)

    def _y(self):
        return self._cur_y

    # ---- 元素 ----
    def msg(self, a, b, text, kind="req", dashed=None, w=None, color=None,
            label_dy=-7, label_side="above", tag=None, fs=11.5):
        if kind == "req":
            color = color or T["blue"]
            w = w or 1.7
            dashed = False if dashed is None else dashed
        elif kind == "res":
            color = color or T["gray"]
            w = w or 1.4
            dashed = True if dashed is None else dashed
        elif kind == "fund":
            color = color or T["gold"]
            w = w or 2.4
            dashed = False if dashed is None else dashed
        elif kind == "sys":
            color = color or T["navy3"]
            w = w or 1.4
            dashed = True if dashed is None else dashed
        elif kind == "back":
            color = color or T["red"]
            w = w or 1.6
            dashed = True if dashed is None else dashed
        self.items.append(dict(t="msg", a=a, b=b, text=text, color=color, w=w,
                               dashed=dashed, label_dy=label_dy, side=label_side,
                               tag=tag, fs=fs))
        return self

    def self_msg(self, a, text, kind="req", indent=54):
        color = T["blue"] if kind == "req" else T["navy3"]
        self.items.append(dict(t="self", a=a, text=text, color=color, indent=indent))
        return self

    def note(self, a, b, text, kind="warn", h=None, fs=11.5):
        fill, stroke, _, _ = KIND.get(kind, KIND["warn"])
        rows = wrap(text, fs, 300)
        h = h or (len(rows) * fs * 1.55 + 16)
        self.items.append(dict(t="note", a=a, b=b, text=text, h=h, fs=fs,
                               fill=fill, stroke=stroke))
        return self

    def group(self, a, b, text, kind="plain", pad=26, fs=11.5):
        self.items.append(dict(t="group", a=a, b=b, text=text, pad=pad, fs=fs))
        return self

    def gap(self, h=16):
        self.items.append(dict(t="gap", h=h))
        return self

    def sep(self, text="", y_pad=10, fs=11.5):
        self.items.append(dict(t="sep", text=text, y_pad=y_pad, fs=fs))
        return self

    # ---- 渲染 ----
    def render(self):
        self._compute_x()
        W = self.W
        # 先算 y
        y = self.top
        laid = []
        first_msg = True
        for it in self.items:
            if it["t"] == "msg":
                need = self.msg_h
                if it["tag"]:
                    need += 14
                # 消息标签向上折行时，最高行可能压进上方元素（顶部参与者盒 /
                # note 警示框）。按实际行数把该消息往下推，保证不压。
                if it["a"] != it["b"] and it.get("side", "above") == "above":
                    x1, x2 = self.cx[it["a"]], self.cx[it["b"]]
                    maxw = max(abs(x2 - x1) - 14, 96)
                    rows = wrap(it["text"], it["fs"], maxw)
                    label_top = (y + self.msg_h / 2.0) - 7 \
                        - (len(rows) - 1) * it["fs"] * 1.45 - it["fs"] * 0.92
                    if first_msg:
                        floor = y - 6 + 2        # 顶部参与者盒下缘 + 2px 缓冲
                    elif laid and laid[-1]["t"] == "note":
                        floor = laid[-1]["y"] + laid[-1]["h"] + 4  # 上方警示框下缘
                    else:
                        floor = None
                    if floor is not None and label_top < floor:
                        y += floor - label_top
                    first_msg = False
                laid.append(dict(it, y=y))
                y += need
            elif it["t"] == "self":
                rows = wrap(it["text"], 11, 190)
                h = max(52, len(rows) * 17 + 40)
                laid.append(dict(it, y=y, rows=rows, h=h))
                y += h
            elif it["t"] == "note":
                # 布局高度必须与渲染高度一致：渲染时按「盒宽-22」重新折行，
                # 行数可能比这里预估的多，导致盒子比布局预期的高、压到下方。
                nx1, nx2 = self.cx[it["a"]], self.cx[it["b"]]
                nw = abs(nx2 - nx1) + 36
                nrows = wrap(it["text"], it["fs"], nw - 22)
                nh = max(it["h"], len(nrows) * it["fs"] * 1.6 + 16)
                laid.append(dict(it, y=y + 8, h=nh))
                y += nh + 18
            elif it["t"] == "gap":
                laid.append(dict(it, y=y))
                y += it["h"]
            elif it["t"] == "sep":
                laid.append(dict(it, y=y + it["y_pad"]))
                y += it["y_pad"] * 2 + 10
            elif it["t"] == "group":
                laid.append(it)
        body_end = y + 6
        # group 需要知道起止 y：用两遍
        gy = {}
        i = 0
        H = int(body_end + self.bottom)
        self.H = H
        if self.title:
            H += 0
        # 重算 H（title 已含在 top 里，此处无需再加）
        out = []
        if self.title:
            out.append(label(W / 2, 24, self.title, fs=14, color=T["navy"], bold=True))
        # 生命线
        for i in range(len(self.actors)):
            out.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" '
                       'stroke-width="1" stroke-dasharray="4 5"/>'
                       % (self.cx[i], self.top - 6, self.cx[i], body_end,
                          T["line"] if False else "#b9c2cf"))
        # 分组框（背景层，需在消息之下）→ 简化：分组框先画
        groups = [l for l in laid if l["t"] == "group"]
        for g in groups:
            pass
        # 消息
        for it in laid:
            t = it["t"]
            if t == "gap" or t == "group":
                continue
            if t == "sep":
                yy = it["y"]
                o = ['<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" '
                     'stroke-width="1.2" stroke-dasharray="6 5"/>'
                     % (self.margin - 12, yy, W - self.margin + 12, yy, T["gold"])]
                if it["text"]:
                    wd = tw(it["text"], it["fs"]) + 22
                    o.append('<rect x="%.1f" y="%.1f" width="%.1f" height="20" rx="10" '
                             'fill="%s"/>' % (W / 2 - wd / 2, yy - 10, wd, T["paper"]))
                    o.append(label(W / 2, yy + 4.6, it["text"], fs=it["fs"],
                                   color=T["amber"], bold=True))
                out.append("".join(o))
            elif t == "note":
                x1 = self.cx[it["a"]]
                x2 = self.cx[it["b"]]
                x = min(x1, x2) - 18
                w = abs(x2 - x1) + 36
                rows = wrap(it["text"], it["fs"], w - 22)
                hh = max(it["h"], len(rows) * it["fs"] * 1.6 + 16)
                out.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="8" '
                           'fill="%s" stroke="%s" stroke-width="1"/>'
                           % (x, it["y"], w, hh, it["fill"], it["stroke"]))
                for k, r in enumerate(rows):
                    out.append(label(x + w / 2, it["y"] + 8 + it["fs"] * 1.58 * (k + 1) - 3,
                                     r, fs=it["fs"], color=T["ink"], bold=True))
            elif t == "msg":
                a, b = it["a"], it["b"]
                x1, x2 = self.cx[a], self.cx[b]
                yy = it["y"] + (self.msg_h / 2.0)
                o = []
                if a == b:
                    o.append(poly([(x1, yy - 12), (x1 + 46, yy - 12), (x1 + 46, yy + 12),
                                   (x1, yy + 12)], color=it["color"], w=it["w"],
                                  dash=it["dashed"]))
                    out.append("".join(o))
                    out.append(label(x1 + 54, yy + 4, it["text"], fs=it["fs"],
                                     color=it["color"], anchor="start"))
                else:
                    o.append(poly([(x1, yy), (x2, yy)], color=it["color"], w=it["w"],
                                  dash=it["dashed"]))
                    out.append("".join(o))
                    lw_ = abs(x2 - x1)
                    maxw = max(lw_ - 14, 96)
                    rows = wrap(it["text"], it["fs"], maxw)
                    if it["side"] == "above":
                        for k, r in enumerate(rows):
                            ly = yy - 7 - (len(rows) - 1 - k) * (it["fs"] * 1.45)
                            # 白底避免压线
                            wd = tw(r, it["fs"]) + 8
                            out.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" '
                                       'fill="%s" opacity="0.92"/>'
                                       % ((x1 + x2) / 2 - wd / 2, ly - it["fs"] * 0.92,
                                          wd, it["fs"] * 1.4, T["paper"]))
                            out.append(label((x1 + x2) / 2, ly, r, fs=it["fs"],
                                             color=it["color"], bold=False))
                if it["tag"]:
                    tsvg, twd = badge((x1 + x2) / 2, yy + 8, it["tag"], kind="gold", fs=10)
                    out.append(tsvg)
            elif t == "self":
                x1 = self.cx[it["a"]]
                yy = it["y"]
                ind = it["indent"]
                o = [poly([(x1, yy + 6), (x1 + ind, yy + 6), (x1 + ind, yy + it["h"] - 18),
                           (x1, yy + it["h"] - 18)], color=it["color"], w=1.6)]
                out.append("".join(o))
                for k, r in enumerate(it["rows"]):
                    out.append(label(x1 + ind + 8, yy + 10 + 15 * (k + 1), r, fs=11,
                                     color=it["color"], anchor="start"))
        # 顶部/底部参与者盒
        for i, a in enumerate(self.actors):
            w = max(tw(a["name"], 13), tw(a["sub"], 10.5) if a["sub"] else 0) + 26
            w = max(w, 108)
            fill, stroke, tcol, _ = KIND.get(a["kind"], KIND["sys"])
            yb = self.top - 6 - 42
            out.append(box(self.cx[i] - w / 2, yb, w, 42, a["name"], a["sub"],
                           kind=a["kind"], fs=13, subfs=10.5, rx=9))
            if self.show_bottom:
                out.append(box(self.cx[i] - w / 2, body_end + 8, w, 38, a["name"],
                               kind=a["kind"], fs=12, subfs=10, rx=9))
        return svg_page(W, int(self.H), "".join(out), aria="时序图")


# --------------------------------------------------------------------------
# 分层流程图 / 决策树
# --------------------------------------------------------------------------
class Layers:
    """
    纵向分层的流程图 / 决策树。
      add_layer([node,...])   依次追加一层（层内水平均分）
      link(a, b, ...)         跨层连线
      bus(parent, [children]) 一对多的"总线式"分支（一条主干 + 水平分配）
    节点：dict(id=, label=, sub=, kind=, w=)
    """

    def __init__(self, width=780, margin=34, layer_gap=58, node_gap=20, node_h=50,
                 title=None):
        self.W = width
        self.margin = margin
        self.layer_gap = layer_gap
        self.node_gap = node_gap
        self.node_h = node_h
        self.layers = []
        self.edges = []
        self.buses = []
        self.notes = []
        self.title = title
        self.top = 26 + (26 if title else 0)

    def add_layer(self, nodes, h=None):
        self.layers.append([dict(n) for n in nodes])
        if h:
            self.node_h = h
        return self

    def link(self, a, b, text=None, kind="req", mode="vh", dash=None, color=None, w=None):
        self.edges.append(dict(a=a, b=b, text=text, kind=kind, mode=mode, dash=dash,
                               color=color, w=w))
        return self

    def bus(self, parent, children, texts=None, kind="req"):
        self.buses.append(dict(p=parent, c=list(children), texts=texts or [], kind=kind))
        for c in children:
            self.edges.append(dict(a=parent, b=c, bus=True))
        return self

    def note(self, x, y, text, kind="warn", w=230, fs=11.5):
        self.notes.append(dict(x=x, y=y, text=text, kind=kind, w=w, fs=fs))
        return self

    def render(self):
        pos = {}
        y = self.top
        for li, layer in enumerate(self.layers):
            hs = self.node_h
            n = len(layer)
            ws = [nd.get("w") or 150 for nd in layer]
            tot = sum(ws) + self.node_gap * (n - 1)
            avail = self.W - 2 * self.margin
            if tot > avail:                     # 太宽：等比压缩
                k = avail / tot
                ws = [w * k for w in ws]
                tot = avail
            x = (self.W - tot) / 2.0
            for i, nd in enumerate(layer):
                nd["_x"], nd["_y"], nd["_w"] = x, y, ws[i]
                nd["_h"] = hs
                pos[nd["id"]] = nd
                x += ws[i] + self.node_gap
            y += hs + self.layer_gap
        self.H = int(y - self.layer_gap + 30)
        out = []
        if self.title:
            out.append(label(self.W / 2, 26, self.title, fs=14, color=T["navy"], bold=True))
        # 边（先画线，后画盒子）
        for e in self.edges:
            if e.get("bus"):
                continue
            a, b = pos.get(e["a"]), pos.get(e["b"])
            if not a or not b:
                continue
            color = e.get("color") or (T["blue"] if e["kind"] != "fund" else T["gold"])
            ax, ay = a["_x"] + a["_w"] / 2, a["_y"] + a["_h"]
            bx, by = b["_x"] + b["_w"] / 2, b["_y"]
            if e["mode"] == "vh":
                mid = (ay + by) / 2
                out.append(poly([(ax, ay), (ax, mid), (bx, mid), (bx, by)],
                                color=color, w=e.get("w") or 1.5, dash=e.get("dash")))
            else:
                midx = (ax + bx) / 2
                out.append(poly([(ax, ay), (ax, midx), (bx, midx), (bx, by)],
                                color=color, w=e.get("w") or 1.5, dash=e.get("dash")))
            if e.get("text"):
                mx, my = (ax + bx) / 2, (ay + by) / 2
                wd = tw(e["text"], 11) + 10
                out.append('<rect x="%.1f" y="%.1f" width="%.1f" height="16" rx="8" '
                           'fill="%s" stroke="%s" stroke-width="0.8"/>'
                           % (mx - wd / 2, my - 8, wd, T["paper"], T["line"]))
                out.append(label(mx, my + 3.6, e["text"], fs=11, color=color))
        # 总线
        for b in self.buses:
            p = pos.get(b["p"])
            if not p:
                continue
            px, py = p["_x"] + p["_w"] / 2, p["_y"] + p["_h"]
            cs = [(pos[c], t) for c, t in zip(b["c"], b["texts"] + [""] * len(b["c"]))]
            bus_y = min(c[0]["_y"] for c in cs) - 26
            color = T["gold"] if b["kind"] == "fund" else T["blue"]
            out.append(poly([(px, py), (px, bus_y)], color=color, w=1.8, head=False))
            xs = [c[0]["_x"] + c[0]["_w"] / 2 for c in cs]
            if len(xs) > 1:
                out.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" '
                           'stroke-width="1.8"/>' % (min(xs), bus_y, max(xs), bus_y, color))
            for (node, t) in cs:
                cx = node["_x"] + node["_w"] / 2
                out.append(poly([(cx, bus_y), (cx, node["_y"])], color=color, w=1.8))
                if t:
                    wd = tw(t, 10.5) + 10
                    out.append('<rect x="%.1f" y="%.1f" width="%.1f" height="15" rx="7" '
                               'fill="%s" stroke="%s" stroke-width="0.8"/>'
                               % (cx - wd / 2, bus_y + 4, wd, T["paper"], T["line"]))
                    out.append(label(cx, bus_y + 15, t, fs=10.5, color=color))
        # 盒子
        for layer in self.layers:
            for nd in layer:
                out.append(box(nd["_x"], nd["_y"], nd["_w"], nd["_h"],
                               nd.get("label", ""), nd.get("sub", ""),
                               kind=nd.get("kind", "sys"), fs=nd.get("fs", 12.5),
                               subfs=nd.get("subfs", 10.5), rx=nd.get("rx", 9)))
        # 注释
        for nt in self.notes:
            rows = wrap(nt["text"], nt["fs"], nt["w"] - 20)
            hh = len(rows) * nt["fs"] * 1.6 + 14
            fill, stroke, _, _ = KIND.get(nt["kind"], KIND["warn"])
            out.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="8" '
                       'fill="%s" stroke="%s" stroke-width="1"/>'
                       % (nt["x"], nt["y"], nt["w"], hh, fill, stroke))
            for k, r in enumerate(rows):
                out.append(label(nt["x"] + nt["w"] / 2, nt["y"] + 8 + nt["fs"] * 1.6 * k + 4,
                                 r, fs=nt["fs"], color=T["ink2"]))
        return svg_page(self.W, self.H, "".join(out), aria="流程图")


# --------------------------------------------------------------------------
# 分层架构图
# --------------------------------------------------------------------------
class Arch:
    """分层架构图：左侧层名标签条 + 右侧均分盒子。"""

    def __init__(self, width=800, margin=24, band_gap=12, label_w=96, title=None):
        self.W = width
        self.margin = margin
        self.band_gap = band_gap
        self.label_w = label_w
        self.bands = []
        self.title = title
        self.top = 24 + (26 if title else 0)

    def add_band(self, name, nodes, tone="sys", node_h=44, inner_gap=10, sub="",
                 note=None):
        self.bands.append(dict(name=name, nodes=nodes, tone=tone, node_h=node_h,
                               inner_gap=inner_gap, sub=sub, note=note))
        return self

    def render(self):
        out = []
        if self.title:
            out.append(label(self.W / 2, 26, self.title, fs=14, color=T["navy"], bold=True))
        y = self.top
        for b in self.bands:
            x0 = self.margin + self.label_w
            x1 = self.W - self.margin
            nh = b["node_h"]
            hh = nh + 14
            fillmap = {"sys": ("#f7fafd", T["blue"]), "gold": ("#fdfaf0", T["gold"]),
                       "ok": ("#f5fbf7", T["green"]), "risk": ("#fdf6f5", T["red"]),
                       "neutral": ("#faf8f4", T["navy3"]), "purple": ("#f8f6fd", T["purple"])}
            bandfill, bandstroke = fillmap.get(b["tone"], fillmap["sys"])
            out.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="12" '
                       'fill="%s" stroke="%s" stroke-width="1" stroke-dasharray="0"/>'
                       % (self.margin, y, self.W - 2 * self.margin, hh, bandfill,
                          bandstroke))
            # 左侧层名
            out.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="9" '
                       'fill="%s"/>' % (self.margin + 6, y + 7, self.label_w - 14, nh,
                                        T["navy"]))
            out.append(label(self.margin + 6 + (self.label_w - 14) / 2, y + 7 + nh / 2 + 4.6,
                             b["name"], fs=12.5, color=T["gold2"], bold=True))
            n = len(b["nodes"])
            avail = (x1 - x0) - 12
            gw = b["inner_gap"]
            w = (avail - gw * (n - 1)) / n
            x = x0 + 6
            for nd in b["nodes"]:
                out.append(box(x, y + 7, w, nh, nd.get("label", ""), nd.get("sub", ""),
                               kind=nd.get("kind", b["tone"]), fs=12, subfs=10, rx=8))
                x += w + gw
            if b.get("note"):
                out.append(label(self.W - self.margin + 4, y + hh / 2, "", fs=10))
            y += hh + self.band_gap
        self.H = int(y - self.band_gap + 24)
        return svg_page(self.W, self.H, "".join(out), aria="架构图")


# --------------------------------------------------------------------------
# 左右对比图
# --------------------------------------------------------------------------
class Compare:
    """概念对比图：左右两栏 + 中间 VS。"""
    def __init__(self, width=780, title=None, vs="VS"):
        self.W = width
        self.title = title
        self.vs = vs
        self.cols = []

    def add(self, title, sub, rows, kind="sys"):
        self.cols.append(dict(title=title, sub=sub, rows=rows, kind=kind))
        return self

    def render(self):
        out = []
        top = 20
        if self.title:
            out.append(label(self.W / 2, 26, self.title, fs=14, color=T["navy"], bold=True))
            top = 48
        m = 20
        gap = 66
        n = len(self.cols)
        w = (self.W - 2 * m - gap * (n - 1)) / n
        y = top
        # 头部
        maxrows = max(len(c["rows"]) for c in self.cols)
        head_h = 54
        row_h = 34
        H = top + head_h + maxrows * row_h + 40
        x = m
        for c in self.cols:
            out.append(box(x, y, w, head_h, c["title"], c["sub"], kind=c["kind"],
                           fs=14, subfs=11, rx=10))
            yy = y + head_h + 10
            for r in c["rows"]:
                fill = "#ffffff"
                out.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="7" '
                           'fill="%s" stroke="%s" stroke-width="1"/>'
                           % (x + 8, yy, w - 16, row_h - 6, fill, T["line"]))
                out.append(label(x + w / 2, yy + (row_h - 6) / 2 + 4.4, r, fs=11.5,
                                 color=T["ink2"]))
                yy += row_h
            x += w + gap
        if n == 2:
            mx = m + w + gap / 2
            out.append('<circle cx="%.1f" cy="%.1f" r="19" fill="%s"/>'
                       % (mx, y + 34, T["navy"]))
            out.append(label(mx, y + 39, self.vs, fs=12, color=T["gold2"], bold=True))
        return svg_page(self.W, int(H), "".join(out), aria="对比图")
