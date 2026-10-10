#!/usr/bin/env node
// shots.mjs — 给 README 生成截图（走本机 Chrome 无头模式 + CDP 协议）。
//
// 为什么不直接截屏：需要精确截到「某一章里的某一张图」，且要 2x 高清。
// 做法：启动 Chrome --headless --remote-debugging-port，然后用 CDP：
//   1) 导航到 index.html#章节锚点，等该章 .chapter.on 生效；
//   2) 元素模式：隐藏 fixed 的侧栏/进度条，取 .fig-wrap 的文档坐标，
//      用 Page.captureScreenshot 的 clip + captureBeyondViewport 截 2 倍图；
//   3) 视口模式：把视口设成 1600x980@2x，滚到章节顶部截整屏（保留侧栏）。
// 输出：tools/_shots/readme_*.png（2x 原图；之后用 sips 缩放拷入 assets/）。
//
// 用法：node tools/shots.mjs

import { spawn } from 'node:child_process';
import { mkdirSync, writeFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { setTimeout as sleep } from 'node:timers/promises';

const CHROME = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const PORT = 9333;
const ROOT = fileURLToPath(new URL('..', import.meta.url));
const BOOK_URL = encodeURI('file://' + ROOT + 'index.html');
const OUT_DIR = ROOT + 'tools/_shots/';

// ---------------- 极简 CDP 客户端 ----------------
let ws = null;
let msgId = 0;
const pending = new Map();      // id -> {resolve, reject}
const eventWaiters = [];        // {event, predicate, resolve, timer}

function handleRaw(data) {
  const msg = JSON.parse(data);
  if (msg.id && pending.has(msg.id)) {
    const { resolve, reject } = pending.get(msg.id);
    pending.delete(msg.id);
    msg.error ? reject(new Error(msg.error.message)) : resolve(msg.result);
  } else if (msg.method) {
    for (let i = eventWaiters.length - 1; i >= 0; i--) {
      const w = eventWaiters[i];
      if (w.event === msg.method && (!w.predicate || w.predicate(msg.params))) {
        eventWaiters.splice(i, 1);
        clearTimeout(w.timer);
        w.resolve(msg.params);
      }
    }
  }
}

function send(method, params = {}) {
  const id = ++msgId;
  ws.send(JSON.stringify({ id, method, params }));
  return new Promise((resolve, reject) => {
    pending.set(id, { resolve, reject });
    const timer = setTimeout(() => {
      if (pending.has(id)) { pending.delete(id); reject(new Error('CDP 超时: ' + method)); }
    }, 30_000);
    if (false) {} // 占位：pending 的 reject 里带不掉 timer，靠 30s 整体兜底
  });
}

function waitEvent(event, predicate, timeoutMs = 20_000) {
  return new Promise((resolve, reject) => {
    const w = { event, predicate, resolve, timer: null };
    w.timer = setTimeout(() => {
      const i = eventWaiters.indexOf(w);
      if (i >= 0) eventWaiters.splice(i, 1);
      reject(new Error('等待事件超时: ' + event));
    }, timeoutMs);
    eventWaiters.push(w);
  });
}

async function evalJs(expression) {
  const r = await send('Runtime.evaluate', { expression, returnByValue: true });
  if (r.exceptionDetails) throw new Error('页面脚本异常: ' + JSON.stringify(r.exceptionDetails.exception?.description || ''));
  return r.result.value;
}

// ---------------- 截图任务定义 ----------------
// pick:'fig' + idx = 该章里第 idx 个 .fig-wrap（0 起）
const shots = [
  { out: 'readme_cover.png',     mode: 'viewport', chapter: 'sec-cover',      scroll: 0 },
  { out: 'readme_content.png',   mode: 'viewport', chapter: 'ch-04',          anchor: 'ch-04' },
  { out: 'readme_sysmap.png',    mode: 'element',  chapter: 'ch-00',          pick: 'fig', idx: 2 },  // 系统调用关系大图
  { out: 'readme_seq.png',       mode: 'element',  chapter: 'ch-06',          pick: 'fig', idx: 0 },  // 微信 V3 完整时序
  { out: 'readme_fourwords.png', mode: 'element',  chapter: 'ch-04',          pick: 'fig', idx: 0 },  // 清算/结算/轧差/划拨
  { out: 'readme_coupon.png',    mode: 'element',  chapter: 'ch-faq',         pick: 'fig', idx: 3 },  // 优惠券口径
  { out: 'readme_arch.png',      mode: 'element',  chapter: 'ch-14',          pick: 'fig', idx: 0 },  // 支付中台架构
];

async function gotoChapter(target) {
  // 先开一个 about:blank 再导航，保证每次 loadEventFired 都会触发
  await send('Page.navigate', { url: 'about:blank' });
  await sleep(150);
  const loaded = waitEvent('Page.loadEventFired', null, 20_000);
  // 封面不带锚点；其余章节用 #章节id，页面加载时会按 hash 直达该章
  const hash = target.chapter === 'sec-cover' ? '' : '#' + target.chapter;
  await send('Page.navigate', { url: BOOK_URL + hash });
  await loaded;
  // 等目标章节显示（.chapter.on），封面恒显示
  for (let i = 0; i < 30; i++) {
    const on = await evalJs(
      `(() => { const el = document.querySelector('#${target.chapter}');
        return el ? (el.classList.contains('on') || el.classList.contains('cover')) : false; })()`);
    if (on) return;
    await sleep(250);
  }
  throw new Error('章节未显示: ' + target.chapter);
}

async function takeOne(target) {
  await gotoChapter(target);
  await sleep(800); // 等 fade 动画与字体渲染

  if (target.mode === 'viewport') {
    // 整屏：保留侧栏，滚到章节顶部
    const y = target.anchor
      ? await evalJs(`Math.max(0, document.querySelector('#${target.anchor}').getBoundingClientRect().top + window.scrollY - 14)`)
      : (target.scroll || 0);
    await evalJs(`window.scrollTo({ top: ${y}, behavior: 'instant' })`);
    await sleep(500);
    const shot = await send('Page.captureScreenshot', { format: 'png' });
    writeFileSync(OUT_DIR + target.out, Buffer.from(shot.data, 'base64'));
    return;
  }

  // 元素模式：隐藏 fixed 元素，回到页首取文档坐标，clip 截图
  await evalJs(`document.querySelectorAll('.toc,.toc-toggle,#backtop,#progress').forEach(e => e.style.display = 'none')`);
  await evalJs(`window.scrollTo({ top: 0, behavior: 'instant' })`);
  await sleep(300);
  const rect = await evalJs(`
    (() => {
      const el = document.querySelectorAll('#${target.chapter} .fig-wrap')[${target.idx}];
      if (!el) return null;
      const r = el.getBoundingClientRect();
      return JSON.stringify({ x: r.x, y: r.y + window.scrollY, w: r.width, h: r.height });
    })()`);
  if (!rect) throw new Error(`找不到图: ${target.chapter} 第 ${target.idx} 个 fig-wrap`);
  const { x, y, w, h } = JSON.parse(rect);
  const pad = 14;
  const shot = await send('Page.captureScreenshot', {
    format: 'png',
    clip: { x: x - pad, y: y - pad, width: w + pad * 2, height: h + pad * 2, scale: 2 },
    captureBeyondViewport: true,
  });
  writeFileSync(OUT_DIR + target.out, Buffer.from(shot.data, 'base64'));
}

// ---------------- 主流程 ----------------
mkdirSync(OUT_DIR, { recursive: true });
const proc = spawn(CHROME, [
  '--headless=new', '--disable-gpu', '--hide-scrollbars',
  '--force-color-profile=srgb', '--no-first-run', '--no-default-browser-check',
  `--remote-debugging-port=${PORT}`,
  '--user-data-dir=/tmp/paybook-shots-profile',
  '--window-size=1600,1000', 'about:blank',
], { stdio: 'ignore' });

try {
  // 轮询等调试端口就绪
  let targets = null;
  for (let i = 0; i < 50; i++) {
    await sleep(200);
    try {
      const res = await fetch(`http://127.0.0.1:${PORT}/json/list`);
      const list = await res.json();
      const page = list.find(t => t.type === 'page');
      if (page) { targets = page; break; }
    } catch { /* 端口未就绪，继续等 */ }
  }
  if (!targets) throw new Error('Chrome 调试端口未就绪');

  ws = new WebSocket(targets.webSocketDebuggerUrl);
  await new Promise((resolve, reject) => {
    ws.onopen = resolve;
    ws.onerror = reject;
  });
  ws.onmessage = e => handleRaw(e.data);
  await send('Page.enable');
  // 视口统一 1600x980、2 倍密度（截图更清晰）
  await send('Emulation.setDeviceMetricsOverride', { width: 1600, height: 980, deviceScaleFactor: 2, mobile: false });

  for (const t of shots) {
    process.stdout.write('截图 ' + t.out + ' ... ');
    await takeOne(t);
    console.log('ok');
  }
  console.log('全部完成 → ' + OUT_DIR);
} finally {
  proc.kill();
}
