#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
美团黄黑编辑风 · HTML 幻灯片 → PDF 导出
--------------------------------------------------
把 slides/ 下所有页拼成一份带分页的临时文档，用无头 Chrome
的 print-to-pdf 一次性输出为 16:9 多页 PDF（矢量文字，可选中）。

用法:
    python3 scripts/build_pdf.py
    python3 scripts/build_pdf.py --slides slides --out out/deck.pdf

依赖: 仅需 Google Chrome / Chromium（脚本自动探测）。
"""
import argparse, glob, os, re, subprocess, sys, tempfile
from shutil import which

CHROME_CANDIDATES = [
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
    "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
    "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser",
    "google-chrome", "chromium", "chromium-browser",
]
BODY_RE = re.compile(r"<body[^>]*>(.*)</body>", re.S | re.I)


def find_chrome():
    for c in CHROME_CANDIDATES:
        if os.path.sep in c and os.path.isfile(c):
            return c
        if os.path.sep not in c and which(c):
            return which(c)
    sys.exit("✗ 未找到 Chrome/Chromium。请安装 Google Chrome 后重试。")


def build(slides_dir, out_path):
    htmls = sorted(glob.glob(os.path.join(slides_dir, "*.html")))
    if not htmls:
        sys.exit(f"✗ {slides_dir} 下没有 .html 幻灯片")

    theme_abs = "file://" + os.path.abspath(os.path.join(slides_dir, "theme.css"))
    deck_abs = "file://" + os.path.abspath(os.path.join(slides_dir, "deck.css"))
    parts = []
    for h in htmls:
        with open(h, encoding="utf-8") as f:
            m = BODY_RE.search(f.read())
            if m:
                parts.append(m.group(1).strip())

    doc = f"""<!doctype html><html lang="zh-CN"><head><meta charset="utf-8">
<link rel="stylesheet" href="{theme_abs}"><link rel="stylesheet" href="{deck_abs}">
<style>
@page {{ size: 1280px 720px; margin: 0; }}
html, body {{ width: auto; height: auto; overflow: visible; background: #fff; }}
.slide {{ page-break-after: always; }}
.slide:last-child {{ page-break-after: auto; }}
</style></head><body>
{''.join(parts)}
</body></html>"""

    chrome = find_chrome()
    os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
    with tempfile.NamedTemporaryFile("w", suffix=".html", delete=False, encoding="utf-8") as tf:
        tf.write(doc)
        tmp_html = tf.name
    try:
        print(f"→ Chrome: {chrome}\n→ 拼合 {len(htmls)} 页 → PDF")
        subprocess.run([
            chrome, "--headless=new", "--disable-gpu", "--no-sandbox",
            "--no-pdf-header-footer", "--virtual-time-budget=6000",
            f"--print-to-pdf={os.path.abspath(out_path)}",
            "file://" + tmp_html,
        ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print(f"✓ 已导出: {out_path}")
    finally:
        os.unlink(tmp_html)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--slides", default="slides")
    ap.add_argument("--out", default="out/deck.pdf")
    a = ap.parse_args()
    build(a.slides, a.out)
