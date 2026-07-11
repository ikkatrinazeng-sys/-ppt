#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
溢出检测 —— 拼稿子时最容易踩的坑：标题/公司名一长，
版式是绝对定位在 1280x720 画布里的，超出画布不会报错，只会被裁切，
肉眼一页页翻很难发现。这个脚本用无头 Chrome 跑一遍所有页，
把「超出画布边界」的元素找出来，标好页面、标签和溢出方向。

原理：把探测脚本临时注入每页 HTML 末尾，执行后把结果写进一个隐藏
<div id="__overflow_result__">，再用 chrome --dump-dom 把执行后的
DOM 抓出来解析——不依赖任何 Python 第三方库。

用法:
    python3 scripts/check_overflow.py                       # 检查 slides/ 全部页
    python3 scripts/check_overflow.py --slide 07-content.html

退出码: 有溢出返回 1，全部正常返回 0（可接入 CI / 导出前检查）。
"""
import argparse, glob, html, json, os, re, subprocess, sys, tempfile
from shutil import which

SLIDE_W, SLIDE_H = 1280, 720
CHROME_CANDIDATES = [
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
    "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
    "google-chrome", "chromium", "chromium-browser",
]

PROBE_JS = f"""
(function(){{
  const W={SLIDE_W}, H={SLIDE_H}, TOL=1;
  const out=[];
  document.querySelectorAll('.slide *').forEach(el=>{{
    if(el.id==='__overflow_result__') return;
    const cs=getComputedStyle(el);
    if(cs.display==='none'||cs.visibility==='hidden'||cs.opacity==='0') return;
    const r=el.getBoundingClientRect();
    if(r.width<=0||r.height<=0) return;
    const overR=r.right-W, overB=r.bottom-H, overL=-r.left, overT=-r.top;
    const worst=Math.max(overR, overB, overL, overT);
    if(worst>TOL){{
      out.push({{
        tag: el.tagName.toLowerCase(),
        cls: (typeof el.className==='string') ? el.className.split(' ')[0] : '',
        text: (el.textContent||'').trim().slice(0,24),
        overRight: Math.round(overR), overBottom: Math.round(overB),
        overLeft: Math.round(overL), overTop: Math.round(overT),
      }});
    }}
  }});
  const d=document.createElement('div');
  d.id='__overflow_result__';
  d.style.display='none';
  d.textContent=JSON.stringify(out);
  document.body.appendChild(d);
}})();
"""

RESULT_RE = re.compile(
    r'<div id="__overflow_result__"[^>]*>(.*?)</div>', re.S)


def find_chrome():
    for c in CHROME_CANDIDATES:
        if os.path.sep in c and os.path.isfile(c):
            return c
        if os.path.sep not in c and which(c):
            return which(c)
    sys.exit("✗ 未找到 Chrome/Chromium。请安装 Google Chrome 后重试。")


def check_one(chrome, html_path):
    src = open(html_path, encoding="utf-8").read()
    injected = src.replace(
        "</body>", f"<script>{PROBE_JS}</script></body>", 1)
    with tempfile.NamedTemporaryFile(
        "w", suffix=".html", delete=False, encoding="utf-8",
        dir=os.path.dirname(os.path.abspath(html_path)),
    ) as tf:
        tf.write(injected)
        tmp_path = tf.name
    try:
        out = subprocess.run(
            [chrome, "--headless=new", "--disable-gpu", "--no-sandbox",
             "--virtual-time-budget=4000",
             "--window-size=%d,%d" % (SLIDE_W, SLIDE_H),
             "--dump-dom", "file://" + tmp_path],
            capture_output=True, text=True, timeout=30,
        ).stdout
        m = RESULT_RE.search(out)
        if not m:
            return None  # 抓不到结果，视为无法判定（不计入溢出）
        return json.loads(html.unescape(m.group(1)))
    finally:
        os.unlink(tmp_path)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--slides", default="slides")
    ap.add_argument("--slide", default=None, help="只检查单个文件名，如 07-content.html")
    a = ap.parse_args()

    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    slides_dir = os.path.join(root, a.slides)
    files = sorted(glob.glob(os.path.join(slides_dir, "[0-9]*.html")))
    if a.slide:
        files = [f for f in files if os.path.basename(f) == a.slide]
    if not files:
        sys.exit("✗ 没有找到幻灯片")

    chrome = find_chrome()
    any_overflow = False
    print(f"→ 检查 {len(files)} 页是否超出 {SLIDE_W}x{SLIDE_H} 画布…\n")
    for f in files:
        name = os.path.basename(f)
        issues = check_one(chrome, f)
        if issues is None:
            print(f"  ? {name} — 无法判定（探测脚本未执行，可忽略）")
            continue
        if not issues:
            print(f"  ✓ {name}")
            continue
        any_overflow = True
        print(f"  ✗ {name} —— {len(issues)} 处溢出")
        for it in issues[:6]:
            dirs = []
            if it["overRight"] > 0: dirs.append(f"右超{it['overRight']}px")
            if it["overBottom"] > 0: dirs.append(f"下超{it['overBottom']}px")
            if it["overLeft"] > 0: dirs.append(f"左超{it['overLeft']}px")
            if it["overTop"] > 0: dirs.append(f"上超{it['overTop']}px")
            tag = f"<{it['tag']}{'.'+it['cls'] if it['cls'] else ''}>"
            txt = f' "{it["text"]}"' if it["text"] else ""
            print(f"      {tag}{txt} — {', '.join(dirs)}")
        if len(issues) > 6:
            print(f"      …还有 {len(issues)-6} 处")

    print()
    if any_overflow:
        print("✗ 存在溢出，建议缩短文案 / 调小字号 / 换更短的版式再导出。")
        sys.exit(1)
    print("✓ 全部页面都在画布内，可以导出了。")


if __name__ == "__main__":
    main()
