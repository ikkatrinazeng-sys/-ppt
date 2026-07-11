#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Contact sheet —— 一张图看完整套 deck。
换完肤、拼完稿，不用一页页翻或开长条单文件，跑这个直接出一张
缩略图九宫格，几秒钟内确认「整套长什么样、有没有明显问题」。

原理：先把每页渲染成 PNG，再拼一个 CSS Grid 网页把这些图铺上去
（贴文件名/页码标签），最后把这个网页整体截屏——缩放和排版都交给
浏览器做，不用手撸图像处理代码。

用法:
    python3 scripts/contact_sheet.py                 # → out/contact-sheet.png
    python3 scripts/contact_sheet.py --cols 5         # 每行 5 张

依赖: 仅需 Google Chrome / Chromium（脚本自动探测）。
"""
import argparse, glob, math, os, subprocess, sys, tempfile
from shutil import which

SLIDE_W, SLIDE_H = 1280, 720
CHROME_CANDIDATES = [
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
    "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
    "google-chrome", "chromium", "chromium-browser",
]


def find_chrome():
    for c in CHROME_CANDIDATES:
        if os.path.sep in c and os.path.isfile(c):
            return c
        if os.path.sep not in c and which(c):
            return which(c)
    sys.exit("✗ 未找到 Chrome/Chromium。请安装 Google Chrome 后重试。")


def render_png(chrome, html_path, png_path, w, h, scale=1):
    subprocess.run([
        chrome, "--headless=new", "--disable-gpu", "--hide-scrollbars",
        "--no-sandbox", "--force-color-profile=srgb",
        f"--force-device-scale-factor={scale}",
        f"--window-size={w},{h}", "--virtual-time-budget=4000",
        "--default-background-color=FFFFFFFF",
        f"--screenshot={png_path}", "file://" + os.path.abspath(html_path),
    ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def build_grid_html(items, cols, cell_w):
    cell_h = round(cell_w * SLIDE_H / SLIDE_W)
    cards = "".join(f"""
      <div class="card">
        <img src="file://{png}">
        <div class="lab">{idx:02d} · {name}</div>
      </div>""" for idx, name, png in items)
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>
      body{{margin:0;background:#EDEDED;font-family:-apple-system,'PingFang SC',sans-serif;}}
      .grid{{display:grid;grid-template-columns:repeat({cols},{cell_w}px);gap:14px;padding:14px;}}
      .card{{background:#fff;box-shadow:0 1px 4px rgba(0,0,0,.18);}}
      .card img{{display:block;width:{cell_w}px;height:{cell_h}px;object-fit:cover;}}
      .lab{{font-size:11px;color:#555;padding:4px 8px;border-top:1px solid #eee;
            white-space:nowrap;overflow:hidden;text-overflow:ellipsis;}}
      </style></head><body><div class="grid">{cards}</div></body></html>"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--slides", default="slides")
    ap.add_argument("--out", default="out/contact-sheet.png")
    ap.add_argument("--cols", type=int, default=4)
    ap.add_argument("--cell-width", type=int, default=300, help="每张缩略图宽度(px)")
    a = ap.parse_args()

    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    slides_dir = os.path.join(root, a.slides)
    files = sorted(glob.glob(os.path.join(slides_dir, "[0-9]*.html")))
    if not files:
        sys.exit("✗ 没有找到幻灯片")

    chrome = find_chrome()
    cols = a.cols
    rows = math.ceil(len(files) / cols)
    print(f"→ 渲染 {len(files)} 页缩略图（{cols} 列 x {rows} 行）…")

    with tempfile.TemporaryDirectory() as tmp:
        items = []
        for i, f in enumerate(files, 1):
            png = os.path.join(tmp, f"s{i:02d}.png")
            render_png(chrome, f, png, SLIDE_W, SLIDE_H)
            items.append((i, os.path.basename(f), png))
            print(f"  [{i}/{len(files)}] {os.path.basename(f)}")

        grid_html = build_grid_html(items, cols, a.cell_width)
        grid_path = os.path.join(tmp, "_grid.html")
        with open(grid_path, "w", encoding="utf-8") as gf:
            gf.write(grid_html)

        sheet_w = cols * (a.cell_width + 14) + 14
        cell_h = round(a.cell_width * SLIDE_H / SLIDE_W) + 24  # +标签高度
        sheet_h = rows * (cell_h + 14) + 14

        out_path = os.path.join(root, a.out)
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        render_png(chrome, grid_path, out_path, sheet_w, sheet_h)

    print(f"✓ 已生成: {out_path}")


if __name__ == "__main__":
    main()
