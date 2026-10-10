# -*- coding: utf-8 -*-
"""冒烟测试：把 svgkit 的几种图各生成一张，人工/程序检查对齐与溢出。"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from svgkit import Sequence, Layers, Arch, Compare, box, arrow, elbow, poly, badge, label, T

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_smoke")
os.makedirs(OUT, exist_ok=True)

# ---------- 1. 时序图 ----------
s = Sequence(
    actors=[
        dict(name="用户", sub="C 端", kind="neutral"),
        dict(name="商户小程序", sub="商户自有系统", kind="sys"),
        dict(name="微信支付", sub="支付机构", kind="ok"),
        dict(name="网联", sub="清算机构", kind="purple"),
        dict(name="发卡行", sub="工商银行", kind="gold"),
    ],
    title="图例 · 小程序内用银行卡支付（含网联↔发卡行内部交互）",
    msg_h=50,
)
s.msg(0, 1, "① 下单并选择「银行卡支付」")
s.msg(1, 2, "② 统一下单 /v3/pay/transactions/jsapi")
s.msg(2, 1, "③ 返回 prepay_id", kind="res")
s.self_msg(1, "拉起收银台，调起微信支付控件")
s.msg(1, 3, "④ 签约支付请求（转接清算）", kind="req")
s.msg(3, 4, "⑤ 转发消费报文至发卡行", kind="req")
s.msg(4, 3, "⑥ 返回扣款结果", kind="res")
s.msg(3, 2, "⑦ 返回交易结果", kind="res")
s.note(3, 4, "这一段是原版缺失的「黑盒」：网联→发卡行的报文交互。", kind="warn")
s.msg(2, 1, "⑧ 支付结果通知（回调 + 签名）", kind="res")
s.sep("T+1 日终")
s.msg(3, 4, "⑨ 日终轧差后资金划拨", kind="fund")
open(os.path.join(OUT, "01_sequence.html"), "w").write(
    "<html><meta charset='utf-8'><body style='background:#eee;font-family:sans-serif'>"
    + s.render() + "</body></html>")

# ---------- 2. 决策树 ----------
d = Layers(title="图例 · 付款决策树（分支连线由算法保证落在节点中心）")
d.add_layer([dict(id="root", label="小赵下单付款", sub="起点", kind="dark", w=200)])
d.add_layer([dict(id="q1", label="在哪儿买？", sub="渠道性质决定资金托管方式", kind="neutral", w=300)])
d.add_layer([
    dict(id="a", label="商家自有系统", sub="例：麦当劳小程序", kind="sys"),
    dict(id="b", label="电商平台", sub="例：抖音、淘宝", kind="sys"),
    dict(id="c", label="线下扫码", sub="例：超市聚合码", kind="sys"),
])
d.add_layer([
    dict(id="p1", label="零钱 / 余额", sub="机构内部记账", kind="gold"),
    dict(id="p2", label="储蓄卡", sub="走网联 → 发卡行", kind="gold"),
    dict(id="p3", label="信用卡", sub="走网联 + 卡组织", kind="gold"),
])
d.link("root", "q1")
d.bus("q1", ["a", "b", "c"])
d.link("a", "p1")
d.link("b", "p2")
d.link("c", "p3")
open(os.path.join(OUT, "02_layers.html"), "w").write(
    "<html><meta charset='utf-8'><body style='background:#eee'>" + d.render() + "</body></html>")

# ---------- 3. 架构图 ----------
a = Arch(title="图例 · 支付中台分层架构")
a.add_band("接入层", [dict(label="收银台"), dict(label="统一支付网关"), dict(label="开放 API")], tone="sys")
a.add_band("核心层", [dict(label="交易子系统"), dict(label="订单系统"), dict(label="账务系统"), dict(label="渠道子系统")], tone="gold")
a.add_band("支撑层", [dict(label="清结算"), dict(label="对账"), dict(label="风控"), dict(label="商户/用户")], tone="ok")
open(os.path.join(OUT, "03_arch.html"), "w").write(
    "<html><meta charset='utf-8'><body style='background:#eee'>" + a.render() + "</body></html>")

# ---------- 4. 对比图 ----------
c = Compare(title="图例 · 无担保交易 vs 有担保交易")
c.add("无担保交易（即时到账）", "麦当劳小程序", ["付款即到商户余额", "商户自主发货", "平台不承担退款兜底", "资金 T+1 结算"], kind="sys")
c.add("有担保交易", "抖音 / 淘宝", ["付款先冻结在平台", "确认收货才分账", "平台承担交易担保", "可分账 / 可分账回退"], kind="ok")
open(os.path.join(OUT, "04_compare.html"), "w").write(
    "<html><meta charset='utf-8'><body style='background:#eee'>" + c.render() + "</body></html>")

print("生成完毕 ->", OUT)
for f in sorted(os.listdir(OUT)):
    print(" ", f, os.path.getsize(os.path.join(OUT, f)), "bytes")
