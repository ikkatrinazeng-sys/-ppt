#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
美团黄黑编辑风 · 自包含单文件打包
--------------------------------------------------
把 assets/meituan.css 内联进 HTML，产出「双击即用、零外部依赖」的文件：
  1) out/美团样册-单文件.html   —— 全部 15 页竖排、自适应缩放，双击直接看整册
  2) standalone/NN-*.html        —— 每页一个自包含文件，双击单页也不塌

原因：直接双击 .html 用 file:// 打开时，外链 <link href="../assets/meituan.css">
在部分浏览器 / 中文路径 / 文件被移动的情况下会加载失败，导致颜色和定位全丢（黑白塌版）。
内联后就没有这个外部依赖了。

用法:  python3 scripts/bundle_html.py
依赖:  无（纯标准库）
"""
import glob, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BODY_RE = re.compile(r"<body[^>]*>(.*)</body>", re.S | re.I)


def read(p):
    with open(p, encoding="utf-8") as f:
        return f.read()


def main():
    css = (read(os.path.join(ROOT, "slides", "theme.css")) + "\n" +
           read(os.path.join(ROOT, "slides", "deck.css")))
    try:
        import renumber; renumber.renumber(os.path.join(ROOT, "slides"))  # 自动刷页码
    except Exception:
        pass
    slides = sorted(glob.glob(os.path.join(ROOT, "slides", "[0-9]*.html")))
    bodies = []
    os.makedirs(os.path.join(ROOT, "standalone"), exist_ok=True)

    for s in slides:
        body = BODY_RE.search(read(s)).group(1).strip()
        bodies.append(body)
        # 单页自包含文件
        one = (f'<!doctype html><html lang="zh-CN"><head><meta charset="utf-8">'
               f'<title>{os.path.basename(s)}</title>\n<style>\n{css}\n</style></head>\n'
               f'<body>\n{body}\n</body></html>\n')
        with open(os.path.join(ROOT, "standalone", os.path.basename(s)), "w", encoding="utf-8") as f:
            f.write(one)

    # 整册单文件：竖排 + 自适应缩放
    override = """
/* —— 单文件样册：覆盖单页锁定，改为竖排滚动 + 自适应缩放 —— */
html, body { width: auto; height: auto; overflow: auto; }
body { background: #d9d9d9; display: flex; flex-direction: column;
       align-items: center; gap: 26px; padding: 26px 0; }
.slide { flex: none; box-shadow: 0 12px 44px rgba(0,0,0,.32); }
"""
    script = """
<script>
function fit(){ var z=Math.min(1,(window.innerWidth-52)/1280); document.body.style.zoom=z; }
window.addEventListener('resize',fit); fit();
</script>
"""
    deck = (f'<!doctype html><html lang="zh-CN"><head><meta charset="utf-8">'
            f'<meta name="viewport" content="width=device-width,initial-scale=1">'
            f'<title>美团黄黑编辑风 · 样册</title>\n<style>\n{css}\n{override}\n</style></head>\n'
            f'<body>\n{chr(10).join(bodies)}\n{script}\n</body></html>\n')
    out = os.path.join(ROOT, "out", "美团样册-单文件.html")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        f.write(deck)

    print(f"✓ 整册单文件: {out}")
    print(f"✓ 单页自包含: standalone/ （{len(slides)} 个）")
    print("  这些文件已内联 CSS，双击任何浏览器都能正常显示颜色与版式。")


if __name__ == "__main__":
    main()
