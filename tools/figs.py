# -*- coding: utf-8 -*-
"""
figs.py — 全书图表集中定义
================================================================
每张图是一个函数，返回 SVG 字符串；build_figs() 汇总成 {名字: svg}。
正文 HTML 中用 <!--FIG:图名--> 引用。

图表编号规则（与章节对应）：
  intro_*   导读篇       eco_*    全景篇
  b1_*      第1章        b2_*     第2章        b3_*   第3章
  c4_*      第4章        c5_*     第5章
  d6_*      第6章        d7_*     第7章        d8_*   第8章
  e9_*      第9章        e10_*    第10章       e11_*  第11章
  f12_*     第12章       f13_*    第13章       f14_*  第14章
  g15_*     第15章       g16_*    第16章
  h17_*     第17章       h18_*    第18章
  faq_*     FAQ 专章
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from svgkit import (T, box, arrow, elbow, poly, label, badge, lines_text,
                    Sequence, Layers, Arch, Compare, svg_page)

FIGS = {}


def reg(name):
    def deco(fn):
        FIGS[name] = fn
        return fn
    return deco


# ==========================================================================
# 导读篇
# ==========================================================================
@reg("intro_case_tree")
def _(fig=None):
    """主线案例决策树：四个分支各自展开候选项，四个选择共同决定资金路径。

    排版要点（相对原版的改进）：
      · 四条分支各自独立成一列，列内左脊 + 短横箭头指向候选项，连线不跨列；
      · 根节点到四列用「一条水平总线」，避免多根斜线互相穿过；
      · 所有坐标由列宽推导，文字再长也不会压到相邻列。
    """
    W = 880
    o = []
    o.append(label(W / 2, 28, "小赵买一杯咖啡 · 四个分支决定这笔钱怎么走",
                   fs=14, color=T["navy"], bold=True))

    # ---- 根节点 ----
    root_w, root_h, root_y = 260, 46, 58
    root_x = (W - root_w) / 2
    o.append(box(root_x, root_y, root_w, root_h, "小赵下单付款 30 元",
                 "同一杯咖啡，分出四条岔路", kind="dark", fs=13.5, subfs=10.5))

    # ---- 四列 ----
    n, gap = 4, 18
    cw = (W - 2 * 30 - (n - 1) * gap) / n
    cols = [30 + i * (cw + gap) for i in range(n)]
    cxs = [x + cw / 2 for x in cols]
    hdr_y, hdr_h = 140, 56
    headers = [
        ("① 在哪儿买？", "渠道性质 → 资金是否被托管", "sys"),
        ("② 用券了吗？", "实付 ≠ 原价 → 退款要拆两笔", "gold"),
        ("③ 用什么付？", "决定走哪条清算通道", "ok"),
        ("④ 钱给谁？", "即时到账 or 担保冻结", "purple"),
    ]
    items = [
        [("麦当劳小程序", "商家自有系统", "sys"),
         ("抖音 / 淘宝", "平台 · 担保交易", "sys"),
         ("便利店扫码", "线下 · 银行卡收单", "sys")],
        [("平台红包 / 商家券", "各出一部分钱", "gold"),
         ("支付渠道立减", "渠道补贴（如随机减）", "gold"),
         ("没用券", "实付 = 原价", "gold")],
        [("微信 / 支付宝零钱", "不出机构，内部记账", "ok"),
         ("储蓄卡", "网联 → 发卡行扣款", "ok"),
         ("信用卡", "网联 → 发卡行授信额度", "ok")],
        [("即时到账", "钱直接算商家的", "purple"),
         ("担保冻结", "确认收货才分账", "purple"),
         ("多级分账", "商家 + 达人 + 平台", "purple")],
    ]

    # ---- 根 → 四列表头：一条水平总线 ----
    bus_y = 122
    o.append(poly([(W / 2, root_y + root_h), (W / 2, bus_y)],
                  color=T["blue"], w=1.8, head=False))
    o.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" '
             'stroke-width="1.8"/>' % (cxs[0], bus_y, cxs[-1], bus_y, T["blue"]))
    for i in range(n):
        o.append(poly([(cxs[i], bus_y), (cxs[i], hdr_y)], color=T["blue"], w=1.8))
    for i, (t, s, k) in enumerate(headers):
        o.append(box(cols[i], hdr_y, cw, hdr_h, t, s, kind=k, fs=14, subfs=10.5))

    # ---- 每条分支下的候选项：左侧竖脊 + 短横箭头 ----
    item_y0, item_h, item_gap = 232, 46, 16
    spine_dx, box_dx = 16, 30
    for i in range(n):
        spine_x = cols[i] + spine_dx
        bx = cols[i] + box_dx
        bw2 = cw - box_dx - 10
        first_cy = item_y0 + item_h / 2
        last_cy = item_y0 + 2 * (item_h + item_gap) + item_h / 2
        o.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" '
                 'stroke-width="1.4"/>' % (spine_x, hdr_y + hdr_h, spine_x, last_cy,
                                           T["gray"]))
        for j, (t, s, k) in enumerate(items[i]):
            iy = item_y0 + j * (item_h + item_gap)
            icy = iy + item_h / 2
            o.append(arrow(spine_x, icy, bx, icy, color=T["gray"], w=1.3, head_size=6))
            o.append(box(bx, iy, bw2, item_h, t, s, kind=k, fs=11.5, subfs=9.5))

    H = item_y0 + 3 * item_h + 2 * item_gap
    o.append(label(W / 2, H + 34,
                   "四个分支的组合 = 这笔钱走哪条路、受什么监管、何时到账；"
                   "后文每个概念都挂在这棵树上讲",
                   fs=12, color=T["muted"]))
    return svg_page(W, H + 48, "".join(o), aria="主线案例决策树")


@reg("intro_reading_map")
def _(fig=None):
    """全书阅读地图：资金线 / 信息线 / 治理线三条主线。"""
    W, H = 820, 420
    o = []
    o.append(label(W/2, 28, "三条主线 · 贯穿全书", fs=14, color=T["navy"], bold=True))
    cols = [
        ("资金线", "钱怎么走", [
            "第1章 三流合一：钱和信息分头走",
            "第2章 谁有资格碰钱：牌照",
            "第3章 钱放在哪：备付金与断直连",
            "第4章 钱何时动：清算与结算",
            "第9章 担保交易：钱先冻住",
        ], "gold"),
        ("信息线", "信号怎么传", [
            "第6章 微信支付 V3 接口",
            "第7章 支付宝开放平台",
            "第13章 幂等与分布式事务",
            "第14章 中台各系统怎么协作",
            "第0章 全景系统调用图",
        ], "sys"),
        ("治理线", "错了怎么兜", [
            "第5章 单边账与日切",
            "第10章 退款体系",
            "第12章 对账系统",
            "第16章 风控体系",
            "第17章 资损防控",
        ], "ok"),
    ]
    colw = (W - 2*36 - 2*24) / 3
    x = 36
    for name, sub, items, kind in cols:
        o.append(box(x, 52, colw, 46, name, sub, kind=kind, fs=15))
        y = 112
        for it in items:
            o.append(box(x, y, colw, 42, it, kind="plain", fs=11.5))
            y += 50
        x += colw + 24
    return svg_page(W, H, "".join(o), aria="阅读地图")


# ==========================================================================
# 第0章 全景
# ==========================================================================
@reg("eco_scenarios")
def _(fig=None):
    """国内支付场景枚举地图：按『谁收钱 / 走什么链路』分类。"""
    W, H = 840, 560
    o = []
    o.append(label(W/2, 28, "国内支付场景全景 · 同类角色归一，每类举 1-2 个例子", fs=14, color=T["navy"], bold=True))
    groups = [
        ("平台型电商", "平台撮合 · 资金先冻结", ["淘宝/天猫（支付宝担保）", "抖音电商（微信/支付宝担保）", "拼多多（担保+分账）"], "sys", 24),
        ("商家自有", "商家自己收 · 即时到账", ["麦当劳小程序（微信JSAPI）", "瑞幸 App（微信/支付宝）", "苹果官网（支付宝 WAP）"], "gold", 24),
        ("线下收单", "扫码 / POS · 银行卡收单", ["便利店聚合码（收钱吧）", "餐厅 POS（银联/银行收单）", "地铁闸机（银联闪付）"], "ok", 24),
        ("转账与红包", "C2C · 余额体系", ["微信转账 / 红包", "支付宝转账", "银行手机银行转账"], "purple", 24),
        ("生活缴费", "公用事业代收", ["水电煤缴费", "ETC 充值", "话费充值"], "warn", 24),
        ("跨境支付", "外卡收单 / 跨境结算", ["境外电商买国内商品", "跨境电商出口收款（连连/PingPong）", "海外留学缴费"], "risk", 24),
    ]
    colw = (W - 2*30 - 3*20) / 4
    y = 56
    for gi in range(0, 6, 4 if False else 4):
        pass
    # 3 列 x 2 行
    positions = [(30, 56), (30 + colw + 20, 56), (30 + 2*(colw+20), 56),
                 (30, 300), (30 + colw + 20, 300), (30 + 2*(colw+20), 300)]
    for (name, sub, items, kind, x), (px, py) in zip(groups, positions):
        o.append(box(px, py, colw, 44, name, sub, kind=kind, fs=13.5))
        yy = py + 56
        for it in items:
            o.append(box(px, yy, colw, 40, it, kind="plain", fs=11.5))
            yy += 48
    o.append(label(W/2, 545, "每一类场景 = 「交易模式 × 支付方式 × 资金路径」的一种组合，后文逐类拆解",
                   fs=12, color=T["muted"]))
    return svg_page(W, H, "".join(o), aria="支付场景全景")


@reg("eco_actors")
def _(fig=None):
    """支付生态角色总图：信息流（蓝）与资金流（金）分色。"""
    W, H = 840, 520
    o = []
    o.append(label(W/2, 28, "支付生态 · 主体关系总图（蓝=信息流，金=资金流）", fs=14, color=T["navy"], bold=True))
    # 顶行：用户 / 商户 / 平台
    top = 56
    bw, bh = 200, 54
    xs = [70, 320, 570]
    o.append(box(xs[0], top, bw, bh, "用户", "掏钱的人", kind="neutral", fs=14))
    o.append(box(xs[1], top, bw, bh, "商户", "提供商品/服务", kind="neutral", fs=14))
    o.append(box(xs[2], top, bw, bh, "平台（可选）", "例：抖音、淘宝、美团\n没有平台时商户=收单方", kind="sys", fs=14))
    # 中行：支付机构 / 清算机构
    mid = 200
    o.append(box(xs[0]+20, mid, 260, 56, "支付机构", "例：微信支付、支付宝、易宝\n需《支付业务许可证》", kind="ok", fs=14))
    o.append(box(xs[2]-20, mid, 260, 56, "清算机构", "例：网联（线上）、银联（卡）\n只做转接清算，不碰用户", kind="purple", fs=14))
    # 底行：银行
    bot = 330
    o.append(box(xs[0], bot, 200, 54, "付款行（发卡行）", "用户银行卡所在银行", kind="gold", fs=13))
    o.append(box(xs[2], bot, 200, 54, "收款行（收单行）", "商户对公账户所在银行", kind="gold", fs=13))
    # 央行
    o.append(box(W/2-130, 430, 260, 56, "中国人民银行（央行/人行）", "发牌照 · 管备付金 · 运营大小额支付系统", kind="dark", fs=13))
    # 连线：信息流
    o.append(arrow(xs[0]+bw/2, top+bh, xs[0]+70+20, mid, color=T["blue"], w=1.8))       # 用户→支付机构
    o.append(arrow(xs[1]+bw/2, top+bh, xs[1]+bw/2, mid-0, color=T["blue"], w=1.2, dash="5 4", head=False))
    o.append(label(xs[1]+bw/2+8, (top+bh+mid)/2+4, "平台把订单转给支付机构", fs=10.5, color=T["blue"], anchor="start"))
    o.append(arrow(xs[2]+bw/2, top+bh, xs[2]-20+130, mid, color=T["blue"], w=1.8))
    o.append(arrow(xs[0]+20+260, mid+28, xs[2]-20, mid+28, color=T["blue"], w=1.8))
    o.append(label(W/2, mid+20, "① 支付请求送清算机构转接（断直连后唯一通路）", fs=10.5, color=T["blue"]))
    o.append(arrow(xs[0]+20, mid+28, xs[0]+bw/2, bot, color=T["blue"], w=1.8))
    o.append(arrow(xs[2]-20+260, mid+28, xs[2]+bw/2, bot, color=T["blue"], w=1.8))
    # 资金流（金色）
    o.append(arrow(xs[0]+bw/2, bot+bh, W/2-130, 448, color=T["gold"], w=2.2))
    o.append(arrow(W/2+130, 448, xs[2]+bw/2, bot+bh, color=T["gold"], w=2.2))
    o.append(label(xs[0]+bw/2-8, (bot+bh+448)/2-2, "资金真实划拨", fs=10.5, color=T["gold"], anchor="end"))
    # 图例（放在央行方框下方，避免遮挡）
    o.append(box(240, 496, 180, 30, "金色=资金真实流动", kind="gold", fs=11))
    o.append(box(430, 496, 180, 30, "蓝色=信息/指令流动", kind="sys", fs=11))
    return svg_page(W, 540, "".join(o), aria="支付生态角色图")


@reg("eco_sys_map")
def _(fig=None):
    """系统调用关系大图：三列式布局，连线全部走列间通道。

    原版问题：箭头从方框边缘穿进相邻列、长斜线跨越多行。
    本版规则：
      · 左列=主流程（自上而下一条竖线），中列=支撑系统（与主流程同行水平相连），
        右列=外部生态（自成一条竖链）；
      · 平台 → 外部只有一条「出口通道」，进/出各占一条竖直车道，绝不穿越方框；
      · 底部是 T+1 对账链路（另一条独立流水线）。
    """
    W, H = 880, 664
    o = []
    o.append(label(W / 2, 26, "一笔担保交易 · 系统调用关系全景图（方框 = 系统，箭头 = 调用/消息方向）",
                   fs=14, color=T["navy"], bold=True))

    # ---------------- 平台内部（虚线大框） ----------------
    o.append('<rect x="16" y="52" width="550" height="436" rx="14" fill="#f6f8fc" '
             'stroke="%s" stroke-width="1.4" stroke-dasharray="7 5"/>' % T["blue"])
    o.append(label(32, 74, "电商平台内部（例：抖音电商）—— 虚线框内是你写的代码",
                   fs=11.5, color=T["blue"], bold=True, anchor="start"))

    # ---------------- 左列：主流程 ----------------
    mx, mw, mcx = 48, 272, 184
    o.append(box(mx, 88, 130, 42, "商品列表", kind="sys", fs=12))
    o.append(box(mx + 142, 88, 130, 42, "购物车", kind="sys", fs=12))
    o.append(arrow(mx + 130, 109, mx + 142, 109, color=T["blue"], w=1.5, head_size=6))
    o.append(box(mx, 150, mw, 46, "收银台", sub="选支付方式 · 拉起收银台", kind="sys", fs=12.5))
    o.append(box(mx, 216, mw, 46, "交易子系统", sub="交易单生命周期", kind="gold", fs=12.5))
    o.append(box(mx, 282, mw, 46, "支付核心", sub="支付单 · 状态机 · 幂等", kind="gold", fs=12.5))
    o.append(box(mx, 348, mw, 46, "渠道子系统", sub="适配微信 / 支付宝 / 抖音支付", kind="gold", fs=12.5))
    o.append(box(mx, 414, mw, 46, "统一网关系统", sub="鉴权 · 路由 · 限流 · 加签", kind="dark", fs=12.5))
    o.append(arrow(255, 130, 255, 150, color=T["blue"], w=1.5, head_size=6))
    for y1, y2 in [(196, 216), (262, 282), (328, 348), (394, 414)]:
        o.append(arrow(mcx, y1, mcx, y2, color=T["blue"], w=1.6))
    o.append(label(196, 268, "③ 创建支付单", fs=10, color=T["gold"], anchor="start"))

    # ---------------- 中列：支撑系统 ----------------
    sx, sw = 386, 170
    o.append(box(sx, 88, 80, 42, "用户系统", sub="登录态", kind="ok", fs=11.5, subfs=9.5))
    o.append(box(sx + 88, 88, 82, 42, "账号系统", sub="实名 · 会话", kind="ok", fs=11.5, subfs=9.5))
    o.append(box(sx, 150, sw, 46, "营销系统", sub="券 · 红包 · 满减", kind="gold", fs=12.5))
    o.append(box(sx, 216, sw, 46, "订单系统", sub="订单状态机", kind="gold", fs=12.5))
    o.append(box(sx, 282, sw, 46, "账务系统", sub="复式记账 · 商户余额", kind="gold", fs=12.5))
    o.append(box(sx, 348, sw, 46, "商家系统", sub="入驻 · 商品 · 结算账单", kind="ok", fs=12.5))
    # 主流程 ←→ 支撑系统（同行水平相连，各自落在两个方框之间）
    sup = [(109, "登录态", "5 4"), (173, "选券 · 算补贴", None),
           (239, "建订单", None), (305, "记复式账", None), (371, "收款方信息", None)]
    for y, txt, dash in sup:
        o.append(arrow(320, y, sx, y, color=T["blue"] if dash else T["gold"],
                       w=1.4, dash=dash, head_size=6))
        if txt:
            o.append(label(353, y - 7, txt, fs=9.5,
                           color=T["blue"] if dash else T["gold"]))

    # ---------------- 右列：外部生态 ----------------
    ex, ew, ecx = 600, 252, 726
    o.append(label(ex, 72, "外部生态（监管世界）", fs=11, color=T["muted"],
                   bold=True, anchor="start"))
    o.append(box(ex, 80, ew, 54, "微信支付 / 支付宝", sub="支付机构（持牌）", kind="ok", fs=13))
    o.append(box(ex, 164, ew, 50, "网联", sub="线上清算 · 转接每笔交易", kind="purple", fs=13))
    o.append(box(ex, 246, ew, 50, "银联", sub="卡组织 · 线下与卡清算", kind="purple", fs=13))
    o.append(box(ex, 328, ew, 50, "发卡行 / 收单行", sub="商业银行（招行 / 建行）", kind="gold", fs=13))
    o.append(box(ex, 410, ew, 54, "中国人民银行", sub="大小额支付系统 · 备付金存管", kind="dark", fs=13))
    for y1, y2, txt, col in [(134, 164, "转接清算", T["purple"]),
                             (214, 246, "卡交易走银联", T["purple"]),
                             (296, 328, "扣款指令", T["blue"]),
                             (378, 410, "资金划拨", T["gold"])]:
        o.append(arrow(ecx, y1, ecx, y2, color=col, w=1.8))
        o.append(label(ecx + 8, (y1 + y2) / 2 + 4, txt, fs=9.5, color=col, anchor="start"))

    # ---------------- 出口通道：去程 / 回程各一条竖直车道 ----------------
    o.append(poly([(320, 427), (576, 427), (576, 107), (ex, 107)],
                  color=T["blue"], w=1.8))
    o.append(poly([(ex, 124), (592, 124), (592, 447), (320, 447)],
                  color=T["blue"], w=1.5, dash="5 4"))
    o.append(label(448, 419, "② 统一下单（网关 → 渠道子系统 → 支付机构）",
                   fs=10, color=T["blue"]))
    o.append(label(448, 474, "⑥ 支付结果回调 → 网关 → 渠道子系统（异步，须查单确认）",
                   fs=10, color=T["blue"]))

    # ---------------- 底部：T+1 对账链路 ----------------
    o.append(label(16, 516, "T+1 日终链路（对账 → 结算）", fs=12.5, color=T["navy"],
                   bold=True, anchor="start"))
    o.append(box(16, 528, 210, 50, "渠道对账文件", sub="微信 / 支付宝 / 银联 T+1 下发",
                 kind="purple", fs=11.5, subfs=9.5))
    o.append(box(250, 528, 150, 50, "对账系统", sub="订单 ↔ 账单核对",
                 kind="purple", fs=11.5, subfs=9.5))
    o.append(box(424, 528, 150, 50, "结算系统", sub="分账 · 解冻 · 提现",
                 kind="purple", fs=11.5, subfs=9.5))
    o.append(box(646, 528, 160, 50, "提现划款", sub="备付金 → 对公卡",
                 kind="purple", fs=11.5, subfs=9.5))
    o.append(arrow(226, 553, 250, 553, color=T["purple"], w=1.6, head_size=6))
    o.append(arrow(400, 553, 424, 553, color=T["purple"], w=1.6, head_size=6))
    o.append(arrow(574, 553, 646, 553, color=T["purple"], w=1.6, head_size=6))
    o.append(arrow(ecx, 528, ecx, 464, color=T["gold"], w=1.8))

    # ---------------- 底部结语 ----------------
    o.append(label(W / 2, 606, "一句话记住：平台内部是「记账」，出了支付机构才是「资金」；"
                               "出了银行才是「清算划拨」",
                   fs=13, color=T["amber"], bold=True))
    o.append(label(W / 2, 632, "担保期中：钱躺在支付机构备付金账户里冻结，谁都不能动 —— "
                               "直到确认收货触发分账",
                   fs=11.5, color=T["muted"]))
    return svg_page(W, H, "".join(o), aria="系统调用关系大图")


@reg("eco_upstream")
def _(fig=None):
    """上下游关系：谁是谁的上游，平级为何还要互相调用。"""
    W, H = 840, 470
    o = []
    o.append(label(W/2, 28, "上下游判定 · 上游=给你输入的一方，下游=接收你输出的一方", fs=14, color=T["navy"], bold=True))
    # 链条
    chain = [
        ("用户", "需求源头", "neutral"),
        ("商户 / 平台", "发起收款", "sys"),
        ("支付机构", "收单·受理", "ok"),
        ("清算机构", "转接清算", "purple"),
        ("商业银行", "账户与资金", "gold"),
        ("央行", "最终结算", "dark"),
    ]
    n = len(chain)
    bw = (W - 2*30 - (n-1)*34) / n
    y = 70
    xs = []
    for i, (nm, sub, kind) in enumerate(chain):
        x = 30 + i*(bw+34)
        xs.append(x)
        o.append(box(x, y, bw, 54, nm, sub, kind=kind, fs=13.5))
        if i < n-1:
            o.append(arrow(x+bw, y+27, x+bw+34, y+27, color=T["blue"], w=1.8))
    o.append(label(W/2, y+96, "上游 → 下游：信息自上而下传递；资金自下而上归集（用户的钱最终在央行体系内完成划拨）",
                   fs=12, color=T["ink2"]))
    # 平级调用案例
    yy = 210
    o.append(label(30, yy, "平级之间也可以互相调用 —— 关键看「谁的场景，谁是通道」", fs=13.5, color=T["navy"], bold=True, anchor="start"))
    o.append(box(30, yy+18, 250, 58, "易宝支付", sub="支付机构（持牌）\n场景：航旅、游戏等行业收单", kind="ok", fs=13))
    o.append(box(360, yy+18, 250, 58, "微信支付", sub="支付机构（持牌）\n场景：社交收银台 · 触达十亿用户", kind="ok", fs=13))
    o.append(arrow(280, yy+47, 360, yy+47, color=T["blue"], w=2))
    o.append(label(320, yy+38, "接入", fs=11, color=T["blue"], bold=True))
    o.append(label(30, yy+96, "① 易宝有行业收单场景，但没有微信那样的 C 端收银台触达 —— 于是把「微信支付」当作一种支付方式提供给商户，钱仍走易宝的商户体系结算。",
                   fs=12, color=T["ink2"], anchor="start"))
    o.append(label(30, yy+120, "② 反过来：微信支付不会「接入易宝」。因为微信自己的收银台就是入口，没有理由把入口让给别人。通道可以有多条，入口只有一个。",
                   fs=12, color=T["ink2"], anchor="start"))
    o.append(box(30, yy+140, 780, 40, "口诀：收单方（接触商户的）是入口，付得越靠近 C 端越强势；接谁的通道，看用户在谁那里。",
                 kind="warn", fs=12))
    return svg_page(W, H, "".join(o), aria="上下游关系")


# ==========================================================================
# 第1章 支付的本质
# ==========================================================================
@reg("b1_three_flows")
def _(fig=None):
    """三流合一：信息流 / 资金流 / 货物流。"""
    W, H = 820, 400
    o = []
    o.append(label(W/2, 28, "支付的本质：三流合一（以抖音电商买咖啡豆为例）", fs=14, color=T["navy"], bold=True))
    lanes = [
        ("信息流", T["blue"], T["blue_bg"], [
            "① 小赵点「立即购买」", "② 交易单+支付单创建", "③ 收银台调起微信支付",
            "④ 微信回调「支付成功」", "⑤ 订单变「已支付·待发货」"]),
        ("资金流", T["gold"], T["amber_bg"], [
            "① 用户卡里扣 59 元", "② T+1 清算后进平台备付金", "③ 冻结（担保期）",
            "④ 确认收货后分账", "⑤ 商户余额 + 52.1 元"]),
        ("货物流", T["green"], T["green_bg"], [
            "① 商家发货", "② 快递在途", "③ 小赵签收",
            "④ 小赵点「确认收货」", "⑤ 触发分账"]),
    ]
    colw = (W - 2*30 - 2*24)/3
    x = 30
    for name, c, bg, items in lanes:
        o.append(box(x, 50, colw, 44, name, kind="dark" if name=="资金流" else ("sys" if name=="信息流" else "ok"), fs=14))
        y = 106
        for it in items:
            o.append(box(x, y, colw, 42, it, kind="plain", fs=11.5,
                         sub_color=T["ink2"]))
            y += 50
        x += colw + 24
    o.append(label(W/2, 372, "三流在「确认收货」这一刻交汇：物流触发信息流，信息流解锁资金流 —— 这就是担保交易的全部秘密",
                   fs=12.5, color=T["amber"], bold=True))
    return svg_page(W, H, "".join(o), aria="三流合一")


@reg("b1_guarantee_compare")
def _(fig=None):
    """无担保 vs 有担保：概念对比 + 例子。"""
    c = Compare(title="无担保交易（即时到账） vs 有担保交易（担保支付）")
    c.add("无担保 · 即时到账", "例：麦当劳小程序点餐", [
        "付完钱，钱立即算商户的",
        "商户见钱发货（其实先货后款也行）",
        "退款 = 商户把已到账的钱退回",
        "资金风险由用户自己承担",
        "适合：强信任、即时交付（快餐/话费）",
    ], kind="sys")
    c.add("有担保 · 担保支付", "例：抖音买咖啡豆（先付款，后到货）", [
        "付完钱，钱先冻结在平台/支付机构",
        "确认收货后，才把钱分给商户",
        "退款 = 解冻，不用动商户的钱",
        "平台替双方「托管信任」",
        "适合：需要物流、有售后纠纷的场景",
    ], kind="ok")
    return c.render()


@reg("b1_instant_vs_settle")
def _(fig=None):
    """「即时到账」vs「T+1 结算」：三层账本轨道 + 微信结算周期表。

    事实来源：腾讯客服《新资金流功能介绍》
      T+1：交易当天实时结算至基本账户，次日提现；
      T+3/T+7：当天入「不可用余额」，第 N 日解冻，N+1 日发起自动提现；
      提现到银行卡：1~3 个工作日到账。
    """
    W = 840
    o = []
    o.append(label(W / 2, 26, "「即时到账」和「T+1 结算」不矛盾 —— 说的是三个不同的「账」",
                   fs=14, color=T["navy"], bold=True))

    rows = [
        ("① 商户号余额", "记账层 · 商户后台可见", [
            ("支付成功 16:48", "储蓄卡扣款成功", "sys"),
            ("实时结算入账", "已扣除手续费", "sys"),
            ("商户后台立刻可见", "基本账户余额 +29.82", "sys"),
        ], "即时到账", "sys"),
        ("② 可提现余额", "解冻层 · 渠道结算周期", [
            ("T+1 日", "渠道与银行完成清算", "gold"),
            ("解冻为可用余额", "从「不可用」变「可用」", "gold"),
            ("可发起提现", "手动或自动提现", "gold"),
        ], "T+1 结算", "gold"),
        ("③ 对公银行卡", "资金层 · 真正的钱", [
            ("发起提现", "商户主动操作", "risk"),
            ("银行处理 1~3 工作日", "以银行到账时间为准", "risk"),
            ("对公卡余额增加", "商户「看到钱」的唯一时刻", "risk"),
        ], "真的钱", "risk"),
    ]
    ry, rh, rgap = 56, 54, 40
    for name, sub, boxes, tag, k in rows:
        o.append(box(20, ry, 160, rh, name, sub, kind=k, fs=12.5, subfs=9.5))
        bx = [200, 382, 564]
        bw = [160, 160, 150]
        for i, (t, s, kind) in enumerate(boxes):
            o.append(box(bx[i], ry, bw[i], rh, t, s, kind=kind, fs=11.5, subfs=9.5))
            if i:
                o.append(arrow(bx[i - 1] + bw[i - 1], ry + rh / 2, bx[i], ry + rh / 2,
                               color=T["blue"], w=1.4, head_size=6))
        arrow_col = {"sys": T["blue"], "gold": T["gold"], "risk": T["red"]}[k]
        o.append(arrow(714, ry + rh / 2, 742, ry + rh / 2, color=arrow_col,
                       w=1.6, head_size=6))
        o.append(box(748, ry, 72, rh, tag, kind=k, fs=11.5))
        ry += rh + rgap
    o.append(label(420, ry + 4, "三条轨道互相独立：账本即时 ≠ 可提现即时 ≠ 银行卡即时",
                   fs=11.5, color=T["muted"]))

    # ---- 微信支付结算周期表 ----
    ty = ry + 26
    o.append(label(20, ty + 12, "微信支付商户的结算周期（官方规则，以商户平台实际配置为准）",
                   fs=12.5, color=T["navy"], bold=True, anchor="start"))

    def cell(x, y, w, h, text, fill="#ffffff", bold=False, fs=11, color=None):
        o.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="%s" '
                 'stroke="%s" stroke-width="1"/>' % (x, y, w, h, fill, T["line"]))
        o.append(label(x + w / 2, y + h / 2 + 4.2, text, fs=fs,
                       color=color or T["ink2"], bold=bold))

    cols_w = [92, 250, 200, 278]
    tx = 20
    head = ["结算周期", "资金入账", "何时可提现", "例子（1 号交易）"]
    hy = ty + 22
    cx = tx
    for i, t in enumerate(head):
        cell(cx, hy, cols_w[i], 30, t, fill=T["navy"], bold=True, color="#fff", fs=11.5)
        cx += cols_w[i]
    body = [
        ("T+1", "交易当天实时结算至基本账户", "次日即可提现", "1 号支付 → 1 号入账，2 号可提现"),
        ("T+3", "当天入「基本账户不可用余额」", "3 号解冻 → 4 号自动提现", "1 号交易 → 3 号解冻，4 号提现"),
        ("T+7", "当天入「基本账户不可用余额」", "7 号解冻 → 8 号自动提现", "1 号交易 → 7 号解冻，8 号提现"),
    ]
    for r, row in enumerate(body):
        yy = hy + 30 + r * 40
        bg = "#f8f6f0" if r % 2 == 0 else "#ffffff"
        cx = tx
        for i, v in enumerate(row):
            cell(cx, yy, cols_w[i], 40, v, fill=bg, bold=(i == 0),
                 fs=10.5 if i else 12, color=T["navy"] if i == 0 else None)
            cx += cols_w[i]

    fy = hy + 30 + 3 * 40 + 16
    o.append(box(20, fy, 800, 46,
                 "结论：商家能「立即看到钱」（第①层账本），但不能「立即拿到现金」（第③层银行卡）。",
                 "「T+1 结算」管的是第①层 → 第②层的解冻周期；提现后还要等银行 1~3 个工作日。"
                 "所以「即时到账」和「T+1 结算」说的是两件事，不矛盾。",
                 kind="warn", fs=12, subfs=11))
    return svg_page(W, fy + 62, "".join(o), aria="即时到账与结算周期")


@reg("b1_direct_path")
def _(fig=None):
    """即时到账的一笔钱完整旅程。"""
    s = Sequence(
        actors=[
            dict(name="小赵", sub="用户", kind="neutral"),
            dict(name="麦当劳小程序", sub="商家自有", kind="sys"),
            dict(name="微信支付", sub="支付机构", kind="ok"),
            dict(name="网联", sub="清算", kind="purple"),
            dict(name="招商银行", sub="小赵的发卡行", kind="gold"),
        ],
        title="即时到账 · 小赵用储蓄卡在麦当劳小程序买套餐（30 元）",
        msg_h=50)
    s.msg(0, 1, "① 选套餐，点「微信支付」")
    s.msg(1, 2, "② 用商户号统一下单（金额 30 元）")
    s.msg(2, 1, "③ 返回 prepay_id + 签名参数", kind="res")
    s.self_msg(1, "收银台调起微信支付控件（用户看到付款页）")
    s.msg(1, 2, "④ 用户确认支付（授权）", kind="req")
    s.msg(2, 3, "⑤ 转接清算请求（断直连后必须走网联）", tag="信息流")
    s.msg(3, 4, "⑥ 消费报文 → 招行（这一步多数教程省略了）", tag="扣款")
    s.msg(4, 3, "⑦ 招行返回：扣款成功，余额 -30.00", kind="res")
    s.msg(3, 2, "⑧ 交易成功回执", kind="res")
    s.msg(2, 1, "⑨ 支付结果回调（带签名，可验证）", kind="res")
    s.sep("T+1 日终（次日凌晨）")
    s.msg(3, 2, "⑩ 轧差清算文件：该商户号今日应收 30 元", kind="fund")
    s.note(2, 3, "资金从用户招行账户，经网联清算，划入微信支付备付金账户（集中存管于央行）", kind="warn")
    s.msg(2, 1, "⑪ 商户号「可提现余额」+30 元（此时仍是微信侧记账）", kind="fund")
    s.self_msg(1, "注意：到这一步，麦当劳的对公银行卡里还没有钱 —— 要商户主动提现才划款")
    return s.render()


# ==========================================================================
# 第2章 参与主体与牌照
# ==========================================================================
@reg("b2_self_pay")
def _(fig=None):
    """平台自建支付：抖音支付 vs 快手（反例），链路只变「支付机构」那一格。

    事实来源：
      · 抖音支付科技有限公司 = 原武汉合众易宝（2014 年获牌，2020 年被字节收购，
        2024 年 6 月经央行批准更名），持「储值账户运营Ⅰ类」；
      · 快手 2020 年拟收购易联支付 50% 股份，交易未落地；易联 2025 年被
        Payoneer（派安盈）100% 收购。快手现仅持华瑞富达「储值账户运营Ⅱ类」
        （预付卡类），没有互联网支付资质。
    """
    W = 840
    o = []
    o.append(label(W / 2, 26, "平台自建支付：链路只变「支付机构」那一格，清算链路一点没变",
                   fs=14, color=T["navy"], bold=True))

    chains = [
        ("链路 A · 借用别人的通道（此前抖音电商用微信支付）", [
            ("抖音电商", "平台（无支付牌照）", "sys"),
            ("微信支付", "财付通 · 支付机构", "ok"),
            ("网联", "清算转接", "purple"),
            ("发卡行", "商业银行", "gold"),
        ], "资金落点：微信支付在央行集中存管的备付金账户"),
        ("链路 B · 用自己的牌照（抖音 App 内选「抖音支付」）", [
            ("抖音电商", "平台", "sys"),
            ("抖音支付", "原合众易宝 · 2024 年更名", "ok"),
            ("网联", "清算转接", "purple"),
            ("发卡行", "商业银行", "gold"),
        ], "资金落点：抖音支付自己在央行集中存管的备付金账户"),
    ]
    bx = [20, 232, 444, 656]
    bw = 172
    cy = 48
    for title, boxes, note in chains:
        o.append(label(20, cy + 12, title, fs=12.5, color=T["navy"], bold=True, anchor="start"))
        yy = cy + 20
        for i, (t, s, k) in enumerate(boxes):
            o.append(box(bx[i], yy, bw, 56, t, s, kind=k, fs=13, subfs=10))
            if i:
                o.append(arrow(bx[i - 1] + bw, yy + 28, bx[i], yy + 28,
                               color=T["blue"], w=1.7))
        o.append(label(20, yy + 74, note, fs=11.5, color=T["gold"], bold=True, anchor="start"))
        cy = yy + 88

    # ---- 两不变一变 ----
    o.append(box(20, cy + 6, 800, 58, "变的只有一格，不变的有两段",
                 "变：钱从「微信的备付金账户」换成「抖音支付的备付金账户」；\n"
                 "不变①：银行卡交易仍必须经网联转接（断直连，第 3 章）—— 自建支付并不能绕过清算机构；\n"
                 "不变②：对账、清结算、备付金监管规则一样，只是换了对手方名称。",
                 kind="warn", fs=12, subfs=11))
    # ---- 中台视角 ----
    o.append(box(20, cy + 76, 800, 52, "对平台中台架构的影响：几乎为零",
                 "渠道子系统新增一个 channel（抖音支付 V3 协议）→ 路由表多一行；"
                 "支付核心、账务、对账、清结算完全复用。这正是把「渠道」抽象出来的价值。",
                 kind="ok", fs=12, subfs=11))
    # ---- 快手反例 ----
    fy = cy + 140
    o.append(label(20, fy, "反例 · 快手：想拿牌照没拿成，只能继续借通道",
                   fs=13, color=T["red"], bold=True, anchor="start"))
    o.append(box(20, fy + 12, 260, 74, "2020 年", "拟以约 3 亿元现金 + 股票收购\n易联支付 50%+ 股份，间接获牌",
                 kind="plain", fs=11.5, subfs=10))
    o.append(arrow(280, fy + 49, 306, fy + 49, color=T["red"], w=1.6))
    o.append(box(306, fy + 12, 250, 74, "交易未落地", "易联支付 2025 年被 Payoneer\n（派安盈）100% 收购，与快手无关",
                 kind="risk", fs=11.5, subfs=10))
    o.append(arrow(556, fy + 49, 582, fy + 49, color=T["red"], w=1.6))
    o.append(box(582, fy + 12, 238, 74, "现状", "仅有华瑞富达「储值账户\n运营Ⅱ类」（预付卡类）",
                 kind="warn", fs=11.5, subfs=10))
    o.append(box(20, fy + 98, 800, 44,
                 "启示：没有「互联网支付」资质，就必须接微信支付 / 支付宝 —— 平台 ≠ 支付机构，这条边界由牌照决定，不由体量决定。",
                 kind="gold", fs=12.5))
    return svg_page(W, fy + 158, "".join(o), aria="平台自建支付")


@reg("b2_licenses")
def _(fig=None):
    """支付业务许可证的主要类型。"""
    W, H = 840, 430
    o = []
    o.append(label(W/2, 28, "《支付业务许可证》（支付牌照）· 央行核发 · 有效期 5 年", fs=14, color=T["navy"], bold=True))
    types = [
        ("网络支付", "互联网收单、移动支付", "微信支付、支付宝、易宝", "ok"),
        ("银行卡收单", "线下 POS / 扫码收单", "银联商务、拉卡拉、通联", "sys"),
        ("预付卡发行与受理", "单用途/多用途预付卡", "资和信、商通卡", "purple"),
        ("电话支付", "固话语音支付", "已基本退出历史舞台", "ghost"),
    ]
    n = len(types)
    bw = (W - 2*30 - (n-1)*20)/n
    x = 30
    for name, scope, eg, kind in types:
        o.append(box(x, 56, bw, 50, name, kind=kind, fs=13.5))
        o.append(box(x, 114, bw, 66, scope, "业务范围", kind="plain", fs=11.5, subfs=10.5))
        o.append(box(x, 188, bw, 62, eg, "代表机构", kind="warn", fs=11.5, subfs=10.5))
        x += bw + 20
    o.append(box(30, 272, 780, 44, "牌照 ≠ 一劳永逸：2016 起央行原则上不再新发牌照，存量牌照成为稀缺资源（收购一家支付公司 ≈ 买「入场券」）",
                 kind="warn", fs=12.5))
    o.append(box(30, 326, 780, 66, "没有牌照能做支付业务吗？",
                 "可以「间接做」：像抖音、美团这样为商户提供收款能力，但资金通道接持牌机构，自己只做「信息层」。这就是后来「断直连」后大平台的合规形态 —— 你负责商户和体验，钱必须过持牌机构的手。",
                 kind="arch" if False else "risk", fs=12.5))
    return svg_page(W, H, "".join(o), aria="牌照类型")


@reg("b2_roles_division")
def _(fig=None):
    """一笔银行卡线上付款，每个角色具体干什么。"""
    W, H = 840, 500
    o = []
    o.append(label(W/2, 28, "角色分工 · 同一笔 30 元付款，六个角色各干一件事", fs=14, color=T["navy"], bold=True))
    roles = [
        ("用户", "发起支付、输入密码/指纹、承担付款义务", "例：小赵在麦当劳小程序点「微信支付」", "neutral"),
        ("商户", "提供商品、申请商户号、接收结算款", "例：麦当劳在微信支付的商户号 mcd_001", "neutral"),
        ("平台（如有）", "撮合交易、决定资金分给谁、处理售后", "例：抖音电商决定这单给商家 52.1、给达人 3 元佣金", "sys"),
        ("支付机构", "受理支付请求、生成支付单、调用清算通道、管理商户余额", "例：微信支付生成支付单，调网联转接", "ok"),
        ("清算机构", "转发报文、日终轧差、生成清算文件", "例：网联把请求转发给招行，T+1 出清算文件", "purple"),
        ("商业银行", "管理用户/商户账户、执行扣款/入账、参与央行清算", "例：招行从小赵卡里扣 30 元；建行把钱入麦当劳对公账户", "gold"),
    ]
    y = 56
    for name, duty, eg, kind in roles:
        o.append(box(30, y, 170, 62, name, kind=kind, fs=13.5))
        o.append(box(208, y, 330, 62, duty, "职责", kind="plain", fs=11.5, subfs=10.5))
        o.append(box(546, y, 264, 62, eg, "例子", kind="warn", fs=11, subfs=10.5))
        y += 72
    return svg_page(W, H, "".join(o), aria="角色分工")


@reg("b2_midboard_pos")
def _(fig=None):
    """支付中台在生态中的位置。"""
    W, H = 840, 330
    o = []
    o.append(label(W/2, 28, "支付中台 = 「业务的统一收单入口」+「渠道的统一适配出口」", fs=14, color=T["navy"], bold=True))
    # 左：业务方
    biz = ["抖音电商", "美团外卖", "快手小店", "自营商城", "线下门店"]
    o.append(label(80, 66, "业务方", fs=13, color=T["ink2"], bold=True, anchor="start"))
    y = 74
    for b in biz:
        o.append(box(30, y, 130, 36, b, kind="sys", fs=12))
        y += 44
    # 中：支付中台
    o.append(box(230, 74, 200, 176, "支付中台", "一个团队服务所有业务\n· 统一支付 API\n· 统一商户/账户\n· 统一风控与对账",
                 kind="gold", fs=15))
    # 右：渠道
    ch = ["微信支付", "支付宝", "银联", "数币运营机构"]
    o.append(label(700, 66, "支付渠道", fs=13, color=T["ink2"], bold=True, anchor="start"))
    y = 74
    for b in ch:
        o.append(box(680, y, 130, 36, b, kind="ok", fs=12))
        y += 44
    for i in range(len(biz)):
        o.append(arrow(160, 92 + i*44, 230, 160, color=T["blue"], w=1.4))
    for i in range(len(ch)):
        o.append(arrow(430, 160, 680, 92 + i*44, color=T["blue"], w=1.4))
    o.append(label(330, 280, "业务方只对接一次（不用每接一个渠道都改代码）", fs=12, color=T["amber"], bold=True))
    o.append(label(530, 280, "渠道换签名/换接口，只改中台一处", fs=12, color=T["amber"], bold=True))
    return svg_page(W, H, "".join(o), aria="中台位置")


def build_figs():
    """执行所有注册的图函数，返回 {名字: svg}。"""
    out = {}
    for name, fn in FIGS.items():
        out[name] = fn()
    return out


# ==========================================================================
# 第3章 监管合规
# ==========================================================================
@reg("b3_duanyilian")
def _(fig=None):
    """断直连前后拓扑对比。"""
    W, H = 840, 470
    o = []
    o.append(label(W/2, 26, "断直连：为什么 2018 年后，支付机构不能直接连银行了", fs=14, color=T["navy"], bold=True))
    # 左：改革前
    o.append(label(215, 58, "改革前（2017 之前）", fs=13, color=T["navy"], bold=True))
    o.append(box(130, 74, 170, 44, "微信支付 / 支付宝", sub="支付机构", kind="ok", fs=12))
    banks = ["工商银行", "建设银行", "农业银行", "招商银行"]
    y = 140
    for b in banks:
        o.append(box(60, y, 140, 38, b, kind="gold", fs=11.5))
        o.append(arrow(215, 96, 130, y+19, color=T["red"], w=1.2, dash="4 3"))
        y += 46
    o.append(label(130, y + 6, "……（当年数十家银行，每家单独谈接口）",
                   fs=11, color=T["muted"]))
    o.append(box(230, 140, 120, 96, "问题", "① 数百家银行直连，协议、接口各不相同\n② 谁也看不清资金全貌\n③ 备付金被挪用风险",
                 kind="risk", fs=11))
    # 右：改革后
    o.append(label(625, 58, "改革后（2018.6 全部完成）", fs=13, color=T["navy"], bold=True))
    o.append(box(540, 74, 170, 44, "微信支付 / 支付宝", sub="支付机构", kind="ok", fs=12))
    o.append(box(560, 150, 130, 46, "网联", sub="唯一转接通道", kind="purple", fs=12.5))
    o.append(arrow(625, 118, 625, 150, color=T["blue"], w=1.8))
    banks2 = ["工商银行", "建设银行", "招商银行", "……全部银行"]
    y = 230
    for b in banks2:
        o.append(box(560, y, 130, 36, b, kind="gold", fs=11.5))
        o.append(arrow(625, 196, 625, y, color=T["blue"], w=1.4))
        y += 44
    o.append(box(30, 410, 780, 44, "「断直连」= 切断支付机构与银行的直接连接，所有交易必须经清算机构转接 —— 央行由此看清每一笔钱",
                 kind="warn", fs=12.5))
    o.append(box(30, 464, 780, 66, "对你的影响",
                 "① 你在支付机构看到的「银行支付」通道配置项变少了 —— 因为通道由清算机构统一裁决；\n"
                 "② 渠道手续费里多了一笔「网联/银联清算费」；\n③ 出现跨行异常时，排查对象从「支付机构↔银行」变成「支付机构↔网联↔银行」三段。",
                 kind="arch", fs=12))
    return svg_page(W, 548, "".join(o), aria="断直连")


@reg("b3_reserve")
def _(fig=None):
    """备付金：从挪用到集中存管。"""
    W, H = 840, 400
    o = []
    o.append(label(W/2, 26, "客户备付金 = 用户付了、商户还没拿走的钱（例：你付了 59 元，商户还没确认收货）",
                   fs=13.5, color=T["navy"], bold=True))
    o.append(box(30, 56, 380, 90, "2019.1.14 之前", "备付金放在支付机构在**各商业银行**开的账户里\n→ 产生利息（诱惑）→ 曾出现挪用、炒股票、买理财的风险事件",
                 kind="risk", fs=12))
    o.append(box(430, 56, 380, 90, "2019.1.14 之后", "备付金 100% 集中缴存到「央行」\n→ 支付机构碰不到这笔钱，只许记账不许动钱\n→ 不再产生利息，支付机构靠手续费吃饭",
                 kind="ok", fs=12))
    o.append(arrow(410, 101, 430, 101, color=T["amber"], w=2))
    o.append(box(30, 166, 780, 62, "备付金不是支付机构的钱！",
                 "它是「待交付」的资金 —— 类似你在房产中介的托管款。支付机构在自家账本上只记「用户存了 59 元、欠商户 59 元」，钱本体始终锁在央行。这就是第 9 章担保交易的信任底座。",
                 kind="warn", fs=12.5))
    o.append(box(30, 240, 780, 66, "三个常被混淆的词",
                 "① 备付金账户（央行里的）—— 钱的本体\n"
                 "② 商户号余额（支付机构账上的）—— 只是一个数字，代表「可以提现多少钱」\n"
                 "③ 平台自有资金账户 —— 平台自己的钱（手续费收入、营销补贴），必须与备付金隔离",
                 kind="arch", fs=12))
    o.append(label(W/2, 340, "面试高频题：为什么备付金集中存管后，支付机构的「余额理财」收益没有了？",
                   fs=12, color=T["muted"]))
    o.append(label(W/2, 366, "答：因为那笔钱从来不属于支付机构，以前是监管真空期的灰色收益，现在归零。", fs=12, color=T["muted"]))
    return svg_page(W, H, "".join(o), aria="备付金")


@reg("b3_aml")
def _(fig=None):
    """反洗钱与 KYC 流程。"""
    d = Layers(width=820, title="KYC（Know Your Customer）· 谁在用这个支付账户", layer_gap=56)
    d.add_layer([dict(id="r", label="用户注册 / 商户入驻", sub="起点", kind="dark", w=240)])
    d.add_layer([
        dict(id="id", label="身份核验", sub="身份证 + 人脸 / 对公账户打款验证", kind="sys", w=230),
        dict(id="risk", label="风险评估", sub="行业、地域、交易模式打分", kind="sys", w=230),
        dict(id="watch", label="名单筛查", sub="制裁名单 / 失信人 / 高风险行业", kind="sys", w=230),
    ])
    d.bus("r", ["id", "risk", "watch"])
    d.add_layer([
        dict(id="ok", label="通过 · 正常使用", sub="按额度分级服务", kind="ok", w=230),
        dict(id="limit", label="受限 · 加强监控", sub="提高核验、降限额", kind="warn", w=230),
        dict(id="reject", label="拒绝 · 上报可疑", sub="反洗钱中心（FIU）", kind="risk", w=230),
    ])
    d.bus("id", ["ok", "limit", "reject"])
    d.bus("risk", ["ok", "limit", "reject"])
    d.bus("watch", ["ok", "limit", "reject"])
    return d.render()


# ==========================================================================
# 第4章 清算 · 结算 · 轧差
# ==========================================================================
@reg("c4_file_delivery")
def _(fig=None):
    """清算/对账文件是怎么送到你手上的：三段传输链路。

    事实来源：
      · 银联《无卡快捷及网关支付技术规范·文件接口规范》：SFTP（SSH2），
        路径=机构标识码/清算日期，23:00 日切，.temp 临时文件机制；
      · 银联一窗办 FAQ：公网方式银联不推送，机构主动到 filedownload.95516.com 拉取；
      · 微信支付 V3 文档：GET /v3/bill/tradebill 返回 download_url（5 分钟内有效），
        次日 9 点生成前一天账单；支付宝 alipay.data.dataservice.bill.downloadurl.query。
    """
    W = 840
    o = []
    o.append(label(W / 2, 26, "清算文件是怎么送到你手上的：三段链路，没有一段是实时推送",
                   fs=14, color=T["navy"], bold=True))

    rows = [
        ("清算机构", "银联 / 网联", "purple",
         "专线 + SFTP 文件交换（机构拉取为主）",
         "① 银联文件服务器路径 = 机构标识码 / 清算日期 / 各类文件，每天 23:00 日切\n"
         "② 公网方式银联不推送，机构自己到 filedownload.95516.com 拉取\n"
         "③ 先传 .temp 临时文件、成功后改名 —— 防止下载到半成品",
         "支付机构", "微信支付 / 支付宝", "ok"),
        ("支付机构", "微信 / 支付宝", "ok",
         "HTTP API：先拿下载链接，再下载文件",
         "① 微信：GET /v3/bill/tradebill → 返回 download_url（5 分钟内有效）\n"
         "② 支付宝：alipay.data.dataservice.bill.downloadurl.query\n"
         "③ 微信次日 9 点生成前一天账单，建议 10 点后再拉，太早会报「生成中」",
         "商户 / 平台", "你的对账系统", "gold"),
        ("商业银行", "开户行", "gold",
         "银企直连 / 企业网银导出 / SFTP",
         "① 银企直连：银行提供的标准化接口，实时性最好，大商户标配\n"
         "② 企业网银：财务人工导出 CSV/Excel，适合小规模\n"
         "③ 对公户流水用于对账第二步：核对「钱是否真的到账」",
         "商户 / 平台", "财务 / 对账系统", "gold"),
    ]
    ry, rh = 52, 116
    for snd, sndsub, sk, title, detail, rcv, rcvsub, rk in rows:
        o.append(box(20, ry, 170, rh, snd, sndsub, kind=sk, fs=13, subfs=10.5))
        o.append(box(212, ry, 424, rh, title, detail, kind="plain", fs=12.5, subfs=10))
        o.append(box(658, ry, 162, rh, rcv, rcvsub, kind=rk, fs=12.5, subfs=10))
        o.append(arrow(190, ry + rh / 2, 212, ry + rh / 2, color=T["purple"], w=1.8, head_size=6))
        o.append(arrow(636, ry + rh / 2, 658, ry + rh / 2, color=T["purple"], w=1.8, head_size=6))
        ry += rh + 28
    o.append(box(20, ry + 8, 800, 54,
                 "共同点：全部是「文件 + 拉取」，没有实时推送。",
                 "所以对账天然是 T+1 批处理任务 —— 定时 Job 到点拉文件、解析、核对，"
                 "而不是订阅一条消息就完事。这也是为什么对账系统都长成「调度 + 解析 + 比对」三件套。",
                 kind="warn", fs=12.5, subfs=11))
    return svg_page(W, ry + 78, "".join(o), aria="清算文件下发")


@reg("c4_four_words")
def _(fig=None):
    """清算/结算/轧差/划拨 四词关系总图。"""
    W, H = 840, 460
    o = []
    o.append(label(W/2, 26, "四个词一张图：清算 ≠ 轧差 ≠ 结算 ≠ 划拨（但它们是同一天的四个阶段）",
                   fs=14, color=T["navy"], bold=True))
    steps = [
        ("① 清算", "Clearing", "算账：交换明细、对账、计算谁该给谁多少", "例：网联把今天微信经手的 2 亿笔交易按银行归类汇总", "sys"),
        ("② 轧差", "Netting", "算账的「技巧」：把多边应收应付抵消成净额", "例：A 银行应付 B 1000 万、应收 B 800 万 → 只需付 200 万", "sys"),
        ("③ 结算", "Settlement", "确定债务：产生不可撤销的付款义务清单", "例：网联向央行大小额系统提交净额划款指令", "gold"),
        ("④ 划拨", "Transfer", "真动钱：资金从 A 银行账户实际到 B 银行账户", "例：央行把 200 万从 A 银行准备金账户划到 B 银行", "risk"),
    ]
    y = 62
    for name, en, what, eg, kind in steps:
        o.append(box(30, y, 120, 64, name, en, kind=kind, fs=13.5, subfs=10))
        o.append(box(158, y, 300, 64, what, kind="plain", fs=12))
        o.append(box(466, y, 344, 64, eg, kind="warn", fs=11))
        y += 76
    o.append(box(30, 374, 780, 62, "所以：清算 ≠ 轧差（轧差只是清算的一种省钱技巧）\n结算 ≠ 划拨（结算是「该付多少」的确定，划拨是「钱真的动了」）",
                 kind="gold", fs=12.5))
    return svg_page(W, H, "".join(o), aria="四词关系")


@reg("c4_netting")
def _(fig=None):
    """轧差计算实例：三家银行一个日终。"""
    W, H = 840, 470
    o = []
    o.append(label(W/2, 26, "轧差实例 · 三家银行一天内的 6 笔互转，最后只需 3 笔净额划款", fs=14, color=T["navy"], bold=True))
    # 明细表
    rows = [
        ("招商→工商", "1000 万"), ("工商→招商", "800 万"),
        ("招商→建设", "500 万"), ("建设→招商", "700 万"),
        ("工商→建设", "300 万"), ("建设→工商", "200 万"),
    ]
    o.append(label(30, 58, "原始明细（逐笔划拨要 6 笔）", fs=12.5, color=T["navy"], bold=True, anchor="start"))
    x = 30
    for i, (a, b) in enumerate(rows):
        o.append(box(x, 68, 125, 36, a + " " + b, kind="plain", fs=10.5))
        x += 133
    # 净额矩阵
    o.append(label(30, 140, "按行汇总 → 轧差", fs=12.5, color=T["navy"], bold=True, anchor="start"))
    # 表格
    def cell(x, y, w, h, text, fill="#ffffff", bold=False, fs=12, color=T["ink"]):
        o.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="%s" stroke="%s" stroke-width="1"/>' % (x, y, w, h, fill, T["line"]))
        o.append(label(x+w/2, y+h/2+4.5, text, fs=fs, color=color, bold=bold))
    tx, ty, cw, ch = 30, 152, 180, 40
    cell(tx, ty, cw, ch, "银行", fill=T["navy"], bold=True, color="#fff")
    cell(tx+cw, ty, cw, ch, "应付合计", fill=T["navy"], bold=True, color="#fff")
    cell(tx+2*cw, ty, cw, ch, "应收合计", fill=T["navy"], bold=True, color="#fff")
    cell(tx+3*cw, ty, cw, ch, "净额（付/收）", fill=T["navy"], bold=True, color="#fff")
    data = [
        ("招商银行", "1500 万", "1500 万", "0（两清）"),
        ("工商银行", "1300 万", "800 万", "净付 500 万"),
        ("建设银行", "900 万", "500 万", "净收 400 万"),
    ]
    for i, r in enumerate(data):
        y = ty + ch*(i+1)
        bg = "#f8f6f0" if i % 2 == 0 else "#ffffff"
        hl = "#fdf6e8" if "0（两清）" not in r[3] else "#eef7f1"
        for j, v in enumerate(r):
            cell(tx+j*cw, y, cw, ch, v, fill=hl if j == 3 else bg, bold=(j == 3))
    # 结果
    o.append(box(30, 320, 400, 56, "逐笔划拨", "6 笔 · 3500 万资金占用", kind="risk", fs=12.5))
    o.append(box(440, 320, 370, 56, "轧差后划拨", "2 笔 · 900 万资金占用\n（工商→建设 400 万、工商→人行 100 万准备金调整）", kind="ok", fs=11))
    o.append(box(30, 392, 780, 44, "轧差的本质：把「多边债务网」变成「简单净额」，大幅减少资金占用和流动性风险",
                 kind="gold", fs=12.5))
    return svg_page(W, H, "".join(o), aria="轧差计算")


@reg("c4_dayend_seq")
def _(fig=None):
    """日终轧差清算时序（用户视角看不到的部分）。"""
    s = Sequence(
        actors=[
            dict(name="网联", sub="清算机构", kind="purple"),
            dict(name="微信支付", sub="备付金在央行", kind="ok"),
            dict(name="招商银行", sub="发卡行", kind="gold"),
            dict(name="央行", sub="大小额系统", kind="dark"),
            dict(name="建设银行", sub="商户开户行", kind="gold"),
        ],
        title="T+1 日终 · 一笔银行卡付款的资金划拨全时序（多数教程省略的部分）",
        msg_h=50)
    s.msg(0, 1, "① 当日交易数据汇总（支付机构 ↔ 网联对账）")
    s.msg(0, 2, "② 与发卡行对账：确认每笔扣款成功")
    s.sep("23:59:59 日切（Cut-off）")
    s.note(0, 2, "日切后，当日交易进入「清算日」，生成清算批次", kind="warn")
    s.msg(0, 3, "③ 提交净额清算指令（轧差后）", kind="fund", tag="清算")
    s.msg(3, 2, "④ 备付金账户记入应收净额", kind="fund")
    s.msg(3, 4, "⑤ 准备金账户间划拨", kind="fund")
    s.msg(3, 1, "⑥ 商户应收净额确认", kind="fund")
    s.sep("次日凌晨（T+1 早）")
    s.msg(1, 0, "⑦ 商户号余额 +N 元（微信侧记账）", kind="fund")
    s.note(1, 0, "注意：到这一步，商户的「对公银行卡」仍然没有钱 —— 钱只是从「冻结」变成「可提现」", kind="risk")
    return s.render()


# ==========================================================================
# 第5章 日切 · 单边账 · 账户体系
# ==========================================================================
@reg("c5_daycut")
def _(fig=None):
    """日切与跨零点订单归属。"""
    W, H = 840, 360
    o = []
    o.append(label(W/2, 26, "日切（Cut-off）· 23:59:59 的那一刀，决定订单算「今天」还是「昨天」", fs=14, color=T["navy"], bold=True))
    # 时间轴
    o.append('<line x1="60" y1="140" x2="780" y2="140" stroke="%s" stroke-width="3"/>' % T["navy3"])
    marks = [(60, "22:00"), (300, "23:59:59"), (540, "00:00:01"), (780, "02:00")]
    for x, t in marks:
        o.append('<line x1="%d" y1="132" x2="%d" y2="148" stroke="%s" stroke-width="2"/>' % (x, x, T["navy3"]))
        o.append(label(x, 120, t, fs=12, color=T["navy"], bold=True))
    o.append(box(70, 160, 220, 46, "小赵 23:58 付款成功", sub="支付日期 = 10月10日", kind="ok", fs=12))
    o.append(box(370, 160, 200, 46, "日切！", sub="清算批次切换", kind="risk", fs=13))
    o.append(box(600, 160, 170, 46, "00:01 老王付款", sub="支付日期 = 10月11日", kind="warn", fs=12))
    o.append(arrow(230, 183, 300, 150, color=T["green"], w=1.4))
    o.append(arrow(610, 183, 540, 150, color=T["amber"], w=1.4))
    o.append(box(60, 240, 720, 60, "为什么重要？",
                 "对账文件、清算批次、手续费计算都以「渠道侧支付日期」为准 —— 不是你系统的下单时间。跨零点订单是单边账重灾区：你的订单表记的是 10月10日，渠道账单却是 10月11日 的批次。",
                 kind="warn", fs=12))
    o.append(box(60, 312, 720, 40, "实践准则：你的对账系统必须按「渠道账单日期」匹配，不能按自己的订单创建日期",
                 kind="gold", fs=12))
    return svg_page(W, H, "".join(o), aria="日切")


@reg("c5_accounts")
def _(fig=None):
    """商户号账户体系：两种余额。"""
    W, H = 840, 430
    o = []
    o.append(label(W/2, 26, "商户号里的两种余额 · 为什么「可提现」≠「可分账」", fs=14, color=T["navy"], bold=True))
    # 商户号
    o.append('<rect x="120" y="56" width="600" height="300" rx="14" fill="#f6f8fc" stroke="%s" stroke-width="1.4"/>' % T["blue"])
    o.append(label(420, 84, "微信支付 · 商户号 mcd_001（麦当劳）", fs=13.5, color=T["navy"], bold=True))
    o.append(box(150, 104, 260, 90, "可用余额（可提现）", "担保交易完成后进入这里\n→ 可以提现到对公银行卡\n→ 也可以用于退款、分账",
                 kind="ok", fs=12.5))
    o.append(box(430, 104, 260, 90, "待结算余额（不可提现）", "T+1 结算前暂时挂账\n→ 清算完成后自动转入可用余额\n→ 期间不能动用",
                 kind="warn", fs=12.5))
    o.append(box(150, 210, 540, 50, "保证金余额（可选）", "平台从每笔交易里扣留的风险金，应对售后赔付", kind="risk", fs=12))
    o.append(box(150, 274, 540, 60, "账务的本质：以上全部只是「微信账本上的数字」",
                 "真正的钱在央行的备付金账户里。商户号余额 ≠ 银行存款 —— 提现时才发生真实的银行划款。",
                 kind="dark", fs=12.5))
    o.append(box(30, 372, 780, 44, "所以「商家看到自己对公账户的钱多了吗？」—— 没有。看到的是微信商户后台的余额数字变了；提现后才动到银行。",
                 kind="gold", fs=12.5))
    return svg_page(W, H, "".join(o), aria="账户体系")


# ==========================================================================
# 第6章 微信支付 V3
# ==========================================================================
@reg("d6_wx_v3_seq")
def _(fig=None):
    """微信 V3 下单-支付-回调完整时序（接口视角）。"""
    s = Sequence(
        actors=[
            dict(name="收银台", sub="平台前端", kind="sys"),
            dict(name="支付核心", sub="平台后端", kind="gold"),
            dict(name="微信支付", sub="V3 API", kind="ok"),
            dict(name="网联", sub="清算", kind="purple"),
            dict(name="发卡行", sub="招行", kind="dark"),
        ],
        title="微信支付 V3 · JSAPI 下单到回调的完整报文旅程",
        msg_h=50)
    s.msg(0, 1, "① 用户点「立即支付」(out_trade_no, amount)")
    s.self_msg(1, "生成支付单（幂等键 out_trade_no）· 金额单位：分")
    s.msg(1, 2, "② POST /v3/pay/transactions/jsapi\n（带商户私钥签名）")
    s.msg(2, 1, "③ 返回 prepay_id（2 小时有效）", kind="res")
    s.self_msg(1, "用 prepay_id 二次签名 → 返回给前端拉起收银台")
    s.msg(0, 0, "④ 调起微信收银台 · 用户输密码", kind="req")
    s.msg(2, 3, "⑤ 转接清算（含网联流水号）")
    s.msg(3, 4, "⑥ 消费报文 → 发卡行（多数时序图省略的环节）", tag="黑盒内")
    s.msg(4, 3, "⑦ 扣款成功 · 返回网联", kind="res")
    s.msg(3, 2, "⑧ 交易成功回执", kind="res")
    s.msg(2, 1, "⑨ 异步回调notify_url（AES-GCM 解密 + 验签）", kind="res")
    s.note(1, 2, "回调不可信！收到后必须回查 GET /v3/pay/transactions/out-trade-no/{no} 确认终态",
           kind="risk")
    s.msg(1, 2, "⑩ 主动查单（终态确认）", kind="req")
    s.sep("如 10 秒内未收到回调")
    s.msg(1, 2, "⑪ 定时补偿查单（1s/10s/1min/10min…）", kind="req")
    return s.render()


@reg("d6_money_path")
def _(fig=None):
    """微信支付两条资金路径：零钱 vs 银行卡。"""
    W, H = 840, 430
    o = []
    o.append(label(W/2, 26, "同一笔 30 元 · 支付方式不同，钱的路径完全不同", fs=14, color=T["navy"], bold=True))
    # 路径A：零钱
    o.append(label(30, 60, "路径 A · 微信零钱支付", fs=13, color=T["navy"], bold=True, anchor="start"))
    chainA = [("小赵零钱", "neutral"), ("微信支付账本", "ok"), ("商户号余额", "gold")]
    x = 30
    for nm, kind in chainA:
        o.append(box(x, 74, 160, 52, nm, kind=kind, fs=12.5))
        x += 180
        if x < 500:
            o.append(arrow(x-20, 100, x, 100, color=T["gold"], w=2))
    o.append(label(30, 152, "① 钱根本没出微信体系：只是账本间转账，秒到，不走网联", fs=11.5, color=T["ink2"], anchor="start"))
    o.append(label(30, 172, "② 发卡行不参与 —— 你妈看不到这条流水，银行账单上没有这 30 元", fs=11.5, color=T["ink2"], anchor="start"))
    # 路径B：银行卡
    o.append(label(30, 220, "路径 B · 银行卡支付", fs=13, color=T["navy"], bold=True, anchor="start"))
    chainB = [("小赵招行卡", "neutral"), ("网联清算", "purple"), ("微信备付金(央行)", "ok"), ("商户号余额", "gold")]
    x = 30
    for nm, kind in chainB:
        o.append(box(x, 234, 180, 52, nm, kind=kind, fs=12.5))
        x += 200
        if x < 760:
            o.append(arrow(x-20, 260, x, 260, color=T["gold"], w=2))
    o.append(label(30, 312, "① 信息流走网联转接，T+1 资金才真正划拨到微信备付金账户", fs=11.5, color=T["ink2"], anchor="start"))
    o.append(label(30, 332, "② 银行流水可见：小赵招行 App 里多了一条「微信支付 30.00」的消费记录", fs=11.5, color=T["ink2"], anchor="start"))
    o.append(box(30, 356, 780, 44, "共同点：无论走哪条路，商户看到的都是「商户号余额 +30」，提现到对公卡才是真资金划转",
                 kind="gold", fs=12.5))
    return svg_page(W, H, "".join(o), aria="资金路径")


# ==========================================================================
# 第7章 支付宝
# ==========================================================================
@reg("d7_wx_vs_ali")
def _(fig=None):
    """微信 vs 支付宝关键差异。"""
    c = Compare(title="微信支付 V3 vs 支付宝开放平台 · 同一件事的两套话术")
    c.add("微信支付 V3", "XML→JSON · 证书+平台证书", [
        "下单：/v3/pay/transactions/jsapi",
        "回调用「证书+AES-GCM」加密",
        "金额单位：分（整数）",
        "退款 /v3/refund/domestic/refunds",
        "回调必须回查 + 幂等（out_trade_no）",
    ], kind="ok")
    c.add("支付宝开放平台", "统一网关 gateway.do", [
        "下单：alipay.trade.create / wap.pay",
        "回调是「表单 POST + RSA2 签名」明文",
        "金额单位：元（字符串，两位小数）",
        "退款 alipay.trade.refund（同步返回）",
        "notify_url 重试 8 次 · 主动查单兜底",
    ], kind="sys")
    return c.render()


# ==========================================================================
# 第8章 银联 · 数币 · 网联
# ==========================================================================
@reg("d8_position")
def _(fig=None):
    """清算机构定位图：谁管哪一段。"""
    W, H = 840, 470
    o = []
    o.append(label(W/2, 26, "一张图分清：央行 · 网联 · 银联 · 支付机构 各管哪一段", fs=14, color=T["navy"], bold=True))
    o.append(box(30, 56, 380, 96, "网联（2017 成立）",
                 "线上支付清算\n例：你在小程序用银行卡付款\n→ 微信/支付宝把请求交给它转接",
                 kind="purple", fs=12.5))
    o.append(box(430, 56, 380, 96, "银联（2002 成立）",
                 "银行卡跨行清算 + 线下收单\n例：你在超市刷 POS 机、ATM 取款\n→ 走银联的银行卡交易",
                 kind="purple", fs=12.5))
    o.append(box(30, 168, 380, 96, "支付机构（持牌）",
                 "面向用户/商户的「收银员」\n例：微信支付、支付宝、易宝\n→ 负责受理、风控、商户服务",
                 kind="ok", fs=12.5))
    o.append(box(430, 168, 380, 96, "商业银行",
                 "账户持有者 · 资金最终在哪里\n例：招行（你）、建行（商户对公）\n→ 参与央行支付系统清算",
                 kind="gold", fs=12.5))
    o.append(box(30, 280, 780, 66, "中国人民银行（央行 / 人行 · 同一个机构）",
                 "① 发牌照、定规则（监管者）\n② 运营大额/小额支付系统（清算的最终执行者）\n③ 集中存管备付金（钱的托管人）",
                 kind="dark", fs=12.5))
    o.append(box(30, 362, 780, 44, "口诀：央行管规则和最终划钱，网联管线上转接，银联管卡片转接，支付机构管「把用户和商户接进来」",
                 kind="gold", fs=12.5))
    o.append(label(W/2, 436, "※ 数字人民币（e-CNY）是第四种形态：央行直接发行的数字现金，支付机构只是「运营机构」",
                   fs=11.5, color=T["muted"]))
    return svg_page(W, H, "".join(o), aria="清算定位")


# ==========================================================================
# 第9章 担保交易
# ==========================================================================
@reg("e9_guarantee_seq")
def _(fig=None):
    """担保交易完整时序：从付款到分账。"""
    s = Sequence(
        actors=[
            dict(name="小赵", sub="买家", kind="neutral"),
            dict(name="抖音电商", sub="平台", kind="sys"),
            dict(name="微信支付", sub="支付机构", kind="ok"),
            dict(name="商家", sub="咖啡豆店", kind="gold"),
        ],
        title="担保交易全时序 · 小赵 59 元买咖啡豆（含担保期与分账）",
        msg_h=50)
    s.msg(0, 1, "① 下单（订单号 T20261010001）")
    s.msg(1, 2, "② 创建支付单（担保交易标记）")
    s.msg(0, 2, "③ 付款 59 元（储蓄卡）", kind="fund")
    s.sep("担保期开始 · 钱冻结")
    s.note(1, 2, "59 元进入平台的「待结算/担保户」，谁都不能动 —— 平台不能花，商家拿不到", kind="warn")
    s.msg(2, 3, "④ 平台通知商家：已收款，可发货（商家还拿不到钱）")
    s.msg(3, 1, "⑤ 商家发货", kind="req")
    s.msg(0, 1, "⑥ 小赵确认收货（或 7 天自动确认）", kind="req")
    s.sep("担保期结束 · 触发分账")
    s.msg(1, 2, "⑦ 发起分账：商家 52.1 / 达人 3 / 平台 3.9", kind="fund")
    s.msg(2, 3, "⑧ 商家余额 +52.1 元（可提现）", kind="fund")
    s.msg(2, 1, "⑨ 达人佣金 +3 元（如另立商户号则到其余额）", kind="fund")
    s.msg(1, 2, "⑩ 平台留存 3.9 元（佣金+手续费）", kind="fund")
    s.note(1, 2, "整个担保期内，这 59 元在央行备付金账户里「睡大觉」—— 集中存管后没有利息，平台赚不到一分钱", kind="risk")
    return s.render()


@reg("e9_fund_location")
def _(fig=None):
    """担保期资金位置图：钱到底在哪。"""
    W, H = 840, 400
    o = []
    o.append(label(W/2, 26, "担保期 7 天 · 那笔 59 元的物理位置与账面位置", fs=14, color=T["navy"], bold=True))
    # 三层
    o.append(box(60, 56, 220, 70, "小赵的招行卡", "账面：-59 元\n日终已扣款", kind="neutral", fs=12.5))
    o.append(box(310, 56, 220, 70, "微信备付金账户（央行）", "物理：这 59 元在这里\n状态：冻结（担保户）", kind="risk", fs=12.5))
    o.append(box(560, 56, 220, 70, "商家视角", "账面：订单「已收款」\n但商户号余额没变", kind="warn", fs=12.5))
    o.append(arrow(280, 91, 310, 91, color=T["gold"], w=2.2))
    o.append(label(295, 80, "T+1", fs=11, color=T["gold"], bold=True))
    o.append(arrow(530, 91, 560, 91, color=T["blue"], w=1.6, dash="5 4"))
    o.append(label(545, 80, "只是", fs=11, color=T["blue"]))
    # 说明
    o.append(box(60, 150, 720, 70, "关键澄清：钱只有一份",
                 "它物理上躺在央行备付金账户（集中存管），微信只是在自家账本上记了一笔「担保户 +59」。平台和商家看到的都是记账数字 —— 这也是为什么担保期资金不能产生利息：钱不是微信的，微信无权让它生息。",
                 kind="warn", fs=12.5))
    o.append(box(60, 236, 350, 70, "小赵 7 天后才确认收货？",
                 "没问题。分账指令可以在担保期后随时发起 —— 微信会先校验「原单是否处于担保冻结」，然后解冻并按比例分配。",
                 kind="ok", fs=12))
    o.append(box(430, 236, 350, 70, "那 7 天里平台亏不亏？",
                 "亏的是资金占用成本（自己的钱压不出去），但不亏利息 —— 备付金本来就没利息。这也是为什么大平台希望用户尽快确认收货。",
                 kind="arch", fs=12))
    o.append(box(60, 322, 720, 44, "一句话：担保期 = 钱在央行睡觉，账在微信记账，单在平台管状态",
                 kind="gold", fs=12.5))
    return svg_page(W, H, "".join(o), aria="担保期资金位置")


# ==========================================================================
# 第10章 退款
# ==========================================================================
@reg("e10_refund_seq")
def _(fig=None):
    """退款时序（原路退回）。"""
    s = Sequence(
        actors=[
            dict(name="支付核心", sub="平台后端", kind="gold"),
            dict(name="微信支付", sub="渠道", kind="ok"),
            dict(name="网联", sub="清算", kind="purple"),
            dict(name="发卡行", sub="招行", kind="dark"),
            dict(name="小赵", sub="用户", kind="neutral"),
        ],
        title="退款时序 · 原路退回（储蓄卡支付的 30 元退回招行卡）",
        msg_h=50)
    s.msg(0, 0, "① 商家/用户发起退款（refund_no 幂等）", kind="req")
    s.msg(0, 1, "② POST /v3/refund/domestic/refunds\n（带原 out_trade_no + 金额）")
    s.msg(1, 0, "③ 受理成功（≠ 到账！）状态：PROCESSING", kind="res")
    s.sep("资金回流（T+1）")
    s.msg(1, 2, "④ 退款清算指令（轧差反向）", kind="fund")
    s.msg(2, 3, "⑤ 发卡行收到入账指令", kind="fund")
    s.msg(3, 4, "⑥ 招行卡余额 +30.00 元", kind="fund")
    s.msg(1, 0, "⑦ 回调退款状态 SUCCESS", kind="res")
    s.note(0, 1, "如果原支付走的是零钱：退款秒到零钱，不经过网联 —— 原路退回的本质是「按原资金路径逆向走一遍」", kind="warn")
    s.msg(0, 0, "⑧ 用户信用卡退款：还要看账单日，可能显示为「负账单」而非实时到账", kind="sys")
    return s.render()


@reg("e10_refund_after_share")
def _(fig=None):
    """分账后退款决策图。"""
    d = Layers(width=820, title="退款难题 · 分账已经发生后，钱从哪退？（两种处理路径）", layer_gap=60)
    d.add_layer([dict(id="r", label="用户申请退款 59 元", sub="但这笔钱早已分给商家 52.1 / 达人 3 / 平台 3.9", kind="risk", w=330)])
    d.add_layer([
        dict(id="a", label="路径 A · 分账回退", sub="向渠道发起「分账回退」，从各收款方余额里把钱要回来", kind="sys", w=380),
        dict(id="b", label="路径 B · 平台垫付", sub="平台先用自有资金退给用户，再慢慢向商家追偿", kind="warn", w=380),
    ])
    d.bus("r", ["a", "b"])
    d.add_layer([
        dict(id="a1", label="商家余额充足", sub="回退成功 · 全额退回", kind="ok", w=180),
        dict(id="a2", label="商家已提现", sub="回退失败！余额不足", kind="risk", w=180),
        dict(id="b1", label="立即到账", sub="用户体验好 · 平台担风险", kind="ok", w=180),
        dict(id="b2", label="后续追偿", sub="扣商家后续结算款 / 法务", kind="warn", w=180),
    ])
    d.bus("a", ["a1", "a2"])
    d.bus("b", ["b1", "b2"])
    d.note(300, 620, "实践：大平台通常两条腿走路 —— 先 B 路径退款保体验，同时对商家发起 A 路径回退，回退失败走协商/风控", kind="warn", w=420)
    return d.render()


# ==========================================================================
# 第11章 分账
# ==========================================================================
@reg("e11_share_seq")
def _(fig=None):
    """分账时序。"""
    s = Sequence(
        actors=[
            dict(name="平台", sub="分账发起方", kind="gold"),
            dict(name="微信支付", sub="执行分账", kind="ok"),
            dict(name="商家商户号", sub="分账接收方1", kind="sys"),
            dict(name="达人商户号", sub="分账接收方2", kind="sys"),
        ],
        title="分账时序 · 确认收货后按比例分配 59 元",
        msg_h=52)
    s.msg(0, 1, "① POST /v3/profitsharing/orders\n（out_order_no, receivers[]）", tag="幂等")
    s.note(0, 1, "关键约束：分账金额 ≤ 冻结金额；分账方必须在「分账接收方」白名单里预先添加", kind="warn")
    s.msg(1, 2, "② 商家 +52.10 元（记入其商户号可用余额）", kind="fund")
    s.msg(1, 3, "③ 达人 +3.00 元", kind="fund")
    s.msg(1, 0, "④ 返回分账结果（FINISHED / PARTIAL）", kind="res")
    s.self_msg(0, "平台留存 3.90 元（默认留在冻结户里，需「解冻剩余资金」指令才到平台商户号）")
    s.sep("如需回退")
    s.msg(0, 1, "⑤ POST /v3/profitsharing/return-orders（分账回退）", kind="req")
    s.msg(1, 2, "⑥ 从商家余额扣回，退回冻结户", kind="fund")
    return s.render()


# ==========================================================================
# 第12章 对账
# ==========================================================================
@reg("f12_recon_flow")
def _(fig=None):
    """T+1 对账流程。"""
    d = Layers(width=820, title="T+1 对账 · 三本账互相核对（你的账 / 渠道的账 / 银行的账）", layer_gap=52)
    d.add_layer([
        dict(id="a", label="渠道对账文件", sub="微信/支付宝 T+1 上午下发账单 CSV", kind="purple", w=240),
        dict(id="b", label="自己的支付流水", sub="支付单表 · 昨日全部记录", kind="sys", w=240),
        dict(id="c", label="银行流水 / 清算文件", sub="商户结算户的实际入账", kind="gold", w=240),
    ])
    d.add_layer([
        dict(id="m1", label="第一步 · 平台 vs 渠道", sub="核对交易明细（金额/状态/手续费）", kind="neutral", w=380),
        dict(id="m2", label="第二步 · 渠道 vs 银行", sub="核对结算款是否真的到账", kind="neutral", w=380),
    ])
    d.bus("a", ["m1"]);  d.bus("b", ["m1"]);  d.bus("c", ["m2"]);  d.bus("a", ["m2"])
    d.add_layer([
        dict(id="ok", label="平账", sub="标记 matched，归档", kind="ok", w=150),
        dict(id="long", label="长款（渠道有我没）", sub="我方漏记 · 补单", kind="warn", w=180),
        dict(id="short", label="短款（我有渠道没）", sub="掉单 · 补偿查单", kind="risk", w=180),
        dict(id="amt", label="金额不平", sub="手续费/红包拆分错", kind="warn", w=150),
    ])
    d.bus("m1", ["ok", "long", "short", "amt"])
    d.bus("m2", ["ok", "long", "short", "amt"])
    return d.render()


# ==========================================================================
# 第13章 分布式事务与幂等
# ==========================================================================
@reg("f13_idempotent")
def _(fig=None):
    """幂等设计：重试为什么安全。"""
    W, H = 840, 400
    o = []
    o.append(label(W/2, 26, "幂等 = 同一笔业务做一百次，效果等于做一次", fs=14, color=T["navy"], bold=True))
    o.append(box(60, 60, 220, 76, "支付核心", "创建支付单\n唯一键 out_trade_no", kind="gold", fs=12.5))
    o.append(box(340, 60, 220, 76, "渠道子系统", "调微信下单\n同一单号重复调 → 返回同一个 prepay_id", kind="ok", fs=12))
    o.append(box(620, 60, 180, 76, "回调处理", "按 out_trade_no 去重\n状态机拒绝重复扣减", kind="sys", fs=12))
    o.append(arrow(280, 98, 340, 98, color=T["blue"], w=1.7))
    o.append(arrow(560, 98, 620, 98, color=T["blue"], w=1.7))
    # 重试示意
    o.append(box(60, 170, 740, 90, "经典翻车现场（没有幂等会怎样）",
                 "① 用户狂点支付按钮 → 生成 3 笔支付单 → 用户被扣 3 次\n"
                 "② 回调重发两次 → 库存被扣两次 / 积分发两次\n"
                 "③ 超时重试调渠道 → 重复扣款，退款都退不清",
                 kind="risk", fs=12.5))
    o.append(box(60, 280, 740, 60, "幂等三板斧",
                 "① 数据库唯一索引兜底（out_trade_no / refund_no / request_id）\n"
                 "② 状态机：终态不可逆（已支付单再收到「支付成功」直接丢弃并告警）\n③ 分布式锁兜住并发（同一单号先抢锁）",
                 kind="ok", fs=12.5))
    o.append(label(W/2, 372, "面试一句话：支付系统宁可慢，不可重；宁可少记，不可多扣", fs=12, color=T["amber"], bold=True))
    return svg_page(W, H, "".join(o), aria="幂等")


# ==========================================================================
# 第14章 支付中台
# ==========================================================================
@reg("f14_arch")
def _(fig=None):
    """支付中台分层架构。"""
    a = Arch(title="支付中台分层架构（每一层都画给你看）", width=840)
    a.add_band("接入层", [dict(label="收银台"), dict(label="统一支付 API"), dict(label="回调中心"), dict(label="开放平台")], tone="sys")
    a.add_band("业务层", [dict(label="支付核心", sub="支付单·状态机"), dict(label="退款"), dict(label="分账"), dict(label="充值提现")], tone="gold")
    a.add_band("渠道层", [dict(label="微信 V3"), dict(label="支付宝"), dict(label="银联"), dict(label="数币")], tone="ok")
    a.add_band("账务层", [dict(label="账务核心"), dict(label="清结算"), dict(label="对账"), dict(label="计费")], tone="purple")
    a.add_band("支撑层", [dict(label="风控"), dict(label="资损监控"), dict(label="配置中心"), dict(label="对账补偿")], tone="risk")
    return a.render()


@reg("f14_state_machine")
def _(fig=None):
    """支付单状态机。箭头标签一律放在状态框上方，避免压住方框。"""
    W = 840
    o = []
    o.append(label(W/2, 26, "支付单状态机 · 只许正向流转，终态靠查单确认", fs=14, color=T["navy"], bold=True))
    # 状态框：5 个，宽 118，间距 36
    states = [
        ("CREATED", "已创建", "sys"),
        ("PAYING", "支付中", "sys"),
        ("SUCCESS", "支付成功", "ok"),
        ("REFUNDED", "已退款", "purple"),
        ("CLOSED", "已关闭", "risk"),
    ]
    sw, sgap, sy, sh = 118, 36, 112, 50
    xs = [58 + i * (sw + sgap) for i in range(5)]
    for (code, name, kind), x in zip(states, xs):
        o.append(box(x, sy, sw, sh, name, code, kind=kind, fs=12.5, subfs=9.5))
    cy = sy + sh / 2            # 137
    # 正向箭头 + 标签（标签放在框上方 y=100，与框错开）
    for i in range(4):
        x1 = xs[i] + sw
        x2 = xs[i + 1]
        o.append(arrow(x1, cy, x2, cy, color=T["blue"], w=1.7))
        o.append(label((x1 + x2) / 2, sy - 10, ["调起支付", "回调 + 查单", "全额退款", "退款成功"][i],
                       fs=10, color=T["blue"], bold=True))
    # 超时关单：从「支付中」底部绕到「已关闭」底部
    o.append(poly([(xs[1] + sw / 2, sy + sh), (xs[1] + sw / 2, sy + sh + 26),
                   (xs[4] + sw / 2, sy + sh + 26), (xs[4] + sw / 2, sy + sh)],
                  color=T["amber"], w=1.4, dash="5 4"))
    o.append(label(W / 2, sy + sh + 46,
                   "超时未支付（2 小时）→ CLOSED（终态，可重新下单）",
                   fs=11, color=T["amber"], bold=True))
    o.append(box(90, 250, 660, 62, "铁律三条",
                 "① SUCCESS 之后不允许再回到 PAYING（资金已动）\n"
                 "② 所有进入终态的判断，必须以「查单结果」为准，回调只是加速器\n"
                 "③ 状态变更前先检查当前状态（CAS），并发回调才不会打架",
                 kind="warn", fs=12))
    o.append(box(90, 326, 660, 58, "状态机与账务的联动",
                 "状态每变一次，账务系统记一笔（复式记账：一边冻结、一边解冻）—— 状态机错了，账就永远对不上。",
                 kind="arch", fs=12))
    return svg_page(W, 400, "".join(o), aria="状态机")


# ==========================================================================
# 第16章 风控
# ==========================================================================
@reg("g16_risk_layers")
def _(fig=None):
    """风控三层。"""
    W, H = 840, 380
    o = []
    o.append(label(W/2, 26, "风控三层 · 事前挡住大部分，事中拦住可疑的，事后追回漏网的", fs=14, color=T["navy"], bold=True))
    layers = [
        ("事前 · 准入风控", "实名认证 / 商户资质审核 / 黑名单拦截 / 设备指纹", "例：新设备 + 新卡 + 高金额 → 触发人脸二次核验", "sys"),
        ("事中 · 交易风控", "规则引擎 + 机器学习模型，毫秒级决策", "例：单笔 >5 万、异地登录 5 分钟后大额 → 延迟结算 / 人工审核", "warn"),
        ("事后 · 资损处置", "拦截出款 / 冻结账户 / 退款 / 法务追偿", "例：盗刷交易，T+1 前拦截提现，把损失控制在平台内部", "risk"),
    ]
    y = 60
    for name, what, eg, kind in layers:
        o.append(box(60, y, 200, 66, name, kind=kind, fs=13))
        o.append(box(270, y, 290, 66, what, kind="plain", fs=11.5))
        o.append(box(570, y, 230, 66, eg, kind="warn", fs=11))
        y += 80
    o.append(box(60, 306, 740, 44, "架构要点：风控是「旁路」不是「主路」—— 主链路超时/宕机时，风控降级为白名单直通，绝不能让风控挂了导致不能付款",
                 kind="gold", fs=12))
    return svg_page(W, H, "".join(o), aria="风控三层")


# ==========================================================================
# 第17章 资损防控
# ==========================================================================
@reg("h17_loss_defense")
def _(fig=None):
    """资损四道防线。"""
    W, H = 840, 400
    o = []
    o.append(label(W/2, 26, "资损防控四道防线 · 一分钱都不能少，一分钱都不能多", fs=14, color=T["navy"], bold=True))
    lines = [
        ("① 事前预防", "代码评审 · 资损红线（金额单位/负数校验/优惠叠加）· 上线前资损仿真", "sys"),
        ("② 事中拦截", "实时资损指标（资金流水对不上立即告警）· 大额延迟结算 · 出款二次确认", "warn"),
        ("③ 事后发现", "准实时对账（分钟级）+ T+1 全量对账 + 资损大盘", "gold"),
        ("④ 兜底处置", "自动熔断出款 · 冻结可疑账户 · 应急预案与追偿 SOP", "risk"),
    ]
    y = 60
    for name, what, kind in lines:
        o.append(box(60, y, 160, 60, name, kind=kind, fs=13))
        o.append(box(230, y, 550, 60, what, kind="plain", fs=12))
        y += 74
    o.append(box(60, 354, 720, 44, "资损定义：任何「账不平」最终都要回答 —— 谁应该有这笔钱？现在这笔钱在哪？缺口是谁的？",
                 kind="gold", fs=12))
    return svg_page(W, 414, "".join(o), aria="资损防线")


# ==========================================================================
# 第18章 职业
# ==========================================================================
@reg("h18_career")
def _(fig=None):
    """能力路线图：五级台阶。"""
    W, H = 840, 330
    o = []
    o.append(label(W/2, 26, "从「会调接口」到「支付中台高级架构师」的五级台阶", fs=14, color=T["navy"], bold=True))
    steps = [
        ("L1", "会调接口", "能接通微信/支付宝 · 会验签 · 会退款", "sys"),
        ("L2", "懂资金", "分得清清算/结算/备付金 · 看得懂对账文件", "ok"),
        ("L3", "会兜底", "幂等 / 状态机 / 补偿 / 对账 / 单边账修复", "gold"),
        ("L4", "能设计", "担保交易 / 分账 / 中台架构 · 多渠道适配", "purple"),
        ("L5", "守得住", "资损防控 / 风控体系 / 合规红线 / 跨境", "risk"),
    ]
    n = len(steps)
    bw = (W - 2*40 - (n-1)*14)/n
    x = 40
    for code, name, what, kind in steps:
        o.append(box(x, 60, bw, 44, code + " · " + name, kind=kind, fs=12.5))
        o.append(box(x, 110, bw, 132, what, kind="plain", fs=11))
        x += bw + 14
    o.append(label(W/2, 286, "每一级都不是「多学几个 API」，而是多承担一类风险 —— L5 的标志是：出事的时候，全公司只能等你说怎么兜",
                   fs=12, color=T["amber"], bold=True))
    return svg_page(W, H, "".join(o), aria="能力台阶")


# ==========================================================================
# FAQ 专章
# ==========================================================================
@reg("faq_coupon")
def _(fig=None):
    """红包/优惠券资金拆解。"""
    W, H = 840, 480
    o = []
    o.append(label(W/2, 26, "红包与优惠券 · 一笔 100 元订单，各出多少钱、退的时候怎么退", fs=14, color=T["navy"], bold=True))
    o.append(label(W/2, 52, "例：商品 100 元 = 平台红包 20 + 商家券 10 + 用户实付 70（微信储蓄卡）", fs=12.5, color=T["ink2"]))
    # 支付时
    o.append(label(30, 90, "支付时 · 三方各出一部分", fs=13, color=T["navy"], bold=True, anchor="start"))
    o.append(box(30, 100, 240, 80, "用户（小赵）", "实付 70 元\n银行卡扣 70，不是 100", kind="neutral", fs=12.5))
    o.append(box(300, 100, 240, 80, "平台", "红包出 20 元\n这是平台的营销费用（自有资金）", kind="sys", fs=12.5))
    o.append(box(570, 100, 240, 80, "商家", "券出 10 元\n少收 10 元货款", kind="gold", fs=12.5))
    o.append(arrow(270, 140, 300, 140, color=T["blue"], w=1.5))
    o.append(arrow(540, 140, 570, 140, color=T["blue"], w=1.5))
    o.append(box(30, 196, 780, 54, "商户实际收到的钱 = 70 + 10 = 80 元（用户实付 + 商家券部分）\n"
                 "平台红包那 20 元由平台和商家按协议结算 —— 可能是平台补贴给商家，也可能是平台与商家分摊",
                 kind="ok", fs=12))
    # 退款时
    o.append(label(30, 286, "退款时 · 原路退回，各退各的", fs=13, color=T["navy"], bold=True, anchor="start"))
    o.append(box(30, 296, 240, 80, "退用户", "70 元原路退回银行卡\n红包 20 元视平台规则\n（过期券通常退回平台）", kind="neutral", fs=11.5))
    o.append(box(300, 296, 240, 80, "退平台", "红包 20 元退回平台营销账户\n券作废或回补库存", kind="sys", fs=11.5))
    o.append(box(570, 296, 240, 80, "退商家", "商家券的 10 元退给商家\n（如券未过期可重新发给用户）", kind="gold", fs=11.5))
    o.append(box(30, 392, 780, 56, "工程要点：支付单必须拆字段记录 —— 订单总额 100 / 商家券 10 / 平台补贴 20 / 用户实付 70\n"
                 "退款接口只退「实付部分」，补贴部分走营销系统自己的退款流程 —— 两套流程，两个幂等键，绝不能混",
                 kind="risk", fs=12))
    return svg_page(W, H, "".join(o), aria="红包优惠券")


@reg("faq_coupon_settle")
def _(fig=None):
    """优惠券的结算与对账口径：渠道只经手「实付」，两边账天生对不平。

    承接 faq_coupon（那讲的是「谁出钱、怎么退」），这张图讲「怎么对账、哪里会资损」。
    """
    W = 840
    o = []
    o.append(label(W / 2, 26, "优惠券 · 渠道只经手「用户实付」—— 所以两边账天生对不平",
                   fs=14, color=T["navy"], bold=True))
    o.append(label(W / 2, 48, "同一笔订单：商品 100 元 = 平台红包 20 + 商家券 10 + 用户实付 70（微信储蓄卡）",
                   fs=12, color=T["ink2"]))

    def panel(px, title, kind, rows, hl_row):
        o.append(box(px, 66, 390, 38, title, kind=kind, fs=13))
        o.append('<rect x="%.1f" y="112" width="390" height="158" rx="9" fill="#ffffff" '
                 'stroke="%s" stroke-width="1.2"/>' % (px, T["line"]))
        yy = 136
        for i, (desc, amt) in enumerate(rows):
            hl = (i == hl_row)
            col = T["gold"] if hl else T["ink2"]
            bold = hl
            o.append(label(px + 16, yy, desc, fs=11.5, color=col, bold=bold, anchor="start"))
            o.append(label(px + 374, yy, amt, fs=12 if hl else 11.5, color=col,
                           bold=bold, anchor="end"))
            if i < len(rows) - 1:
                o.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" '
                         'stroke-width="0.7" stroke-dasharray="3 3"/>'
                         % (px + 14, yy + 11, px + 376, yy + 11, T["line"]))
            yy += 34

    panel(20, "你的支付单（订单维度）", "gold", [
        ("订单总额", "100 元"),
        ("− 平台红包（营销预算，不走渠道）", "−20 元"),
        ("− 商家券（商家让利）", "−10 元"),
        ("用户实付 ← 唯一走渠道的金额", "70 元"),
    ], hl_row=3)
    panel(430, "渠道账单（微信侧 · T+1）", "sys", [
        ("用户实付（应收金额）", "70 元"),
        ("− 手续费（0.6%）", "−0.42 元"),
        ("结算给商户", "69.58 元"),
        ("渠道立减若有 → 单列一列", "渠道出钱"),
    ], hl_row=0)

    o.append(box(20, 288, 800, 52,
                 "对账提醒：你的支付单是 100，渠道账单是 70 —— 不是丢钱，是口径不同。",
                 "对账必须按「用户实付」字段比对；补贴部分由营销系统按券码自己核销核对，"
                 "两套流程各自幂等，绝不能拿订单总额去和渠道账单碰。",
                 kind="risk", fs=12.5, subfs=11))

    o.append(label(20, 372, "四个经典资损点（每一个都真实发生过）",
                   fs=13, color=T["red"], bold=True, anchor="start"))
    pts = [
        ("① 退款把补贴也退成现金", "平台红包 20 元应退回营销账户，若退给用户 = 直接资损 20 元"),
        ("② 渠道立减记错归属", "立减是渠道/银行出的钱，不是商家让利 —— 记进商家应收会结算不平"),
        ("③ 部分退款的券分摊", "满 100 减 20、退 50：券退 10 还是 20？必须定好分摊算法并全链路一致"),
        ("④ 券核销不幂等", "一单多次核销 / 退款后券未回补 —— 营销资金被薅，对账才发现"),
    ]
    for i, (t, d) in enumerate(pts):
        px = 20 + (i % 2) * 410
        py = 384 + (i // 2) * 62
        o.append(box(px, py, 390, 54, t, d, kind="warn", fs=12, subfs=10.5))
    o.append(label(W / 2, 528,
                   "一句话：订单总额是「商业口径」，渠道账单是「资金口径」，中间的差全部由平台内部账务消化",
                   fs=12, color=T["amber"], bold=True))
    return svg_page(W, 548, "".join(o), aria="优惠券结算对账口径")


@reg("faq_t1_timeline")
def _(fig=None):
    """T+1 与担保期 7 天时间轴。"""
    W, H = 840, 400
    o = []
    o.append(label(W/2, 26, "时间轴 · 用户付款后，钱和账在每一天的状态（担保交易）", fs=14, color=T["navy"], bold=True))
    o.append('<line x1="50" y1="150" x2="800" y2="150" stroke="%s" stroke-width="3"/>' % T["navy3"])
    days = [
        (70,  "D0", "10:00 付款 59 元", "钱扣走，进担保冻结", "risk"),
        (215, "D0 深夜", "日切清算", "网联轧差 · 备付金记应收", "purple"),
        (360, "D+1", "备付金入账", "钱物理到达微信备付金（仍冻结）", "ok"),
        (505, "D+1~D+7", "担保期", "钱在央行睡觉 · 无利息", "warn"),
        (650, "D+7", "确认收货 → 分账", "商家 52.1 / 达人 3 / 平台 3.9", "gold"),
    ]
    for x, d, t1, t2, kind in days:
        o.append('<line x1="%d" y1="142" x2="%d" y2="158" stroke="%s" stroke-width="2"/>' % (x, x, T["navy3"]))
        o.append(label(x, 128, d, fs=12.5, color=T["navy"], bold=True))
        o.append(box(x-68, 172, 136, 56, t1, t2, kind=kind, fs=10.5, subfs=9.5))
    o.append(box(50, 260, 740, 56, "回答「中间 7 天钱在哪、有没有收益」",
                 "① D0~D+1：在央行备付金账户（冻结态），微信只能记账不能动\n"
                 "② D+1 起物理到位，仍是担保冻结，不能用于任何支付\n③ 备付金 2019 年后不计利息 —— 平台和微信都赚不到这 7 天的收益",
                 kind="warn", fs=12))
    o.append(box(50, 328, 740, 44, "回答「平台 7 天后才能发起分账吗」—— 不是。用户确认收货的那一刻就可以发起，7 天只是「自动确认」的默认时限",
                 kind="gold", fs=12))
    return svg_page(W, H, "".join(o), aria="时间轴")


@reg("faq_fund_where")
def _(fig=None):
    """即时到账的钱到底在哪：三层澄清。"""
    W, H = 840, 420
    o = []
    o.append(label(W/2, 26, "「即时到账」的三层含义 · 商家问的「钱到哪了」其实是三个不同的问题", fs=14, color=T["navy"], bold=True))
    rows = [
        ("① 微信侧记账", "支付成功那一刻", "商户号「可用余额」+30 元", "这只是微信账本上的数字变动，银行和央行都还没动静", "ok"),
        ("② 备付金入账", "T+1 日终清算后", "微信在央行的备付金账户真的多了 30 元", "这是资金物理到位，但商户还是碰不到", "gold"),
        ("③ 银行卡到账", "商户手动提现后", "对公银行卡余额 +29.7 元（扣提现手续费）", "这是商家「看到钱」的唯一时刻 —— 前面都是账本游戏", "sys"),
    ]
    y = 56
    for t, when, what, note, kind in rows:
        o.append(box(30, y, 170, 66, t, when, kind=kind, fs=12.5))
        o.append(box(208, y, 280, 66, what, kind="plain", fs=12))
        o.append(box(496, y, 314, 66, note, kind="warn", fs=11))
        y += 80
    o.append(box(30, 300, 780, 44, "所以「普通商户即时到账」= 第①层的即时 —— 账本即时，资金仍走 T+1，提现才见真钱",
                 kind="risk", fs=12.5))
    o.append(box(30, 354, 780, 44, "市面上的「二维码收款秒到银行卡」是另一回事：那是收单机构的「垫资」服务（先垫钱给你，T+1 它自己找渠道清算）",
                 kind="arch", fs=12))
    return svg_page(W, H, "".join(o), aria="三层资金")


# ==========================================================================
# 附录B 排查手册
# ==========================================================================
@reg("appx_troubleshoot")
def _(fig=None):
    """线上三大报警的排查决策树。"""
    d = Layers(width=820, title="线上三大报警 · 排查决策树（先定位钱，再定位账，最后定位谁错了）", layer_gap=58)
    d.add_layer([
        dict(id="s1", label="症状 A · 付了钱订单未支付", sub="用户投诉", kind="risk", w=252),
        dict(id="s2", label="症状 B · 被扣了两次", sub="用户投诉", kind="risk", w=252),
        dict(id="s3", label="症状 C · 对账不平", sub="对账系统报警", kind="risk", w=252),
    ])
    d.add_layer([
        dict(id="a1", label="① 调渠道查单", sub="渠道有这笔扣款吗", kind="sys", w=252),
        dict(id="a2", label="① 查我方支付单", sub="是一笔单还是两笔单", kind="sys", w=252),
        dict(id="a3", label="① 给差异分类", sub="长款 / 短款 / 金额不平", kind="sys", w=252),
    ])
    d.bus("s1", ["a1"]); d.bus("s2", ["a2"]); d.bus("s3", ["a3"])
    d.add_layer([
        dict(id="b1", label="渠道有 → 长款（掉单）", sub="回调丢失/落库失败 → 补单发货", kind="ok", w=252),
        dict(id="b2", label="两笔单 → 幂等失效", sub="退一笔给用户 · 补唯一索引", kind="ok", w=252),
        dict(id="b3", label="按第 12 章四类差错修复", sub="补偿查单 / 补单 / 核手续费", kind="ok", w=252),
    ])
    d.bus("a1", ["b1"]); d.bus("a2", ["b2"]); d.bus("a3", ["b3"])
    d.add_layer([
        dict(id="c1", label="渠道无 → 短款", sub="用户侧扣款失败 · 关单 + 安抚用户", kind="warn", w=252),
        dict(id="c2", label="一笔单 → 渠道重复扣款", sub="持流水号找渠道申诉退款", kind="warn", w=252),
        dict(id="c3", label="修复后必须复盘", sub="写故障库 · 补监控 · 补校验", kind="warn", w=252),
    ])
    d.bus("a1", ["c1"]); d.bus("a2", ["c2"]); d.bus("a3", ["c3"])
    return d.render()
