#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
一键换肤 —— 传入主色 + 公司名，自动生成 slides/theme.css（整册换皮）。
辅助色（深主色/浅主色/图表色/页底）自动从主色推导，也可显式覆盖。

例：
  # 换成 B站粉
  python3 scripts/reskin.py --primary "#FB7299" --logo-cn "B站" --logo-en "bilibili"

  # 深色皮肤（黑金）+ 顺带把正文里的旧品牌名也替换掉
  python3 scripts/reskin.py --primary "#FFCC33" --dark \\
      --logo-cn "抖音" --logo-en "douyin" --rename "美团=抖音" --rename "MEITUAN=douyin"

依赖：无（纯标准库）
"""
import argparse, glob, os, re, sys


def hexv(h):
    h = h.lstrip('#')
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))


def tohex(rgb):
    return '#' + ''.join(f'{max(0,min(255,round(c))):02X}' for c in rgb)


def mix(a, b, t):  # t=0 -> a, t=1 -> b
    ra, rb = hexv(a), hexv(b)
    return tohex(tuple(ra[i] + (rb[i]-ra[i])*t for i in range(3)))


def darken(a, f):  # f<1 变深
    return tohex(tuple(c*f for c in hexv(a)))


def lum(a):  # 感知亮度 0-255
    r, g, b = hexv(a)
    return 0.299*r + 0.587*g + 0.114*b


def build_theme(a):
    p = a.primary
    dark = a.dark
    ink = a.ink or ('#F5F5F5' if dark else '#141414')
    bg = a.bg or ('#0E0E10' if dark else mix(p, '#FFFFFF', 0.955))  # 浅色默认取主色极浅调
    ink2 = a.ink2 or (mix(ink, bg, 0.18) if dark else mix('#141414', '#FFFFFF', 0.14))
    pdeep = a.primary_deep or darken(p, 0.88)
    psoft = a.primary_soft or mix(p, '#FFFFFF', 0.80)
    c3 = a.chart3 or darken(p, 0.78)
    c4 = a.chart4 or ('#4A4B50' if dark else '#C9C6BC')
    gray = a.gray or ('#9499A0' if dark else '#8C8B84')
    gray2 = a.gray2 or ('#6B6E76' if dark else '#B9B7AD')
    line = a.line or (mix(bg, ink, 0.16) if dark else mix(p, '#FFFFFF', 0.86))
    white = '#FFFFFF'
    onp = '#141414' if lum(p) > 140 else '#FFFFFF'   # 主色底上的文字：浅主色配深字
    onp2 = mix(onp, p, 0.15)

    return f"""/* ============================================================
   品牌皮肤 · THEME  —— 由 reskin.py 生成（{a.logo_en}）
   换公司只改这一个文件；辅助色可手动微调。
   ============================================================ */
@import url('https://fonts.googleapis.com/css2?family=Archivo:ital,wght@0,400;0,600;0,800;0,900;1,800&family=Noto+Sans+SC:wght@200;300;400;500;700;900&family=Caveat:wght@700&display=swap');

:root {{
  /* —— 主色系 —— */
  --brand-primary:      {p};
  --brand-primary-deep: {pdeep};
  --brand-primary-soft: {psoft};
  --brand-ink:          {ink};
  --brand-ink-2:        {ink2};
  --brand-bg:           {bg};
  --brand-white:        {white};

  /* —— 主色底上的文字色 —— */
  --brand-on-primary:   {onp};
  --brand-on-primary-2: {onp2};

  /* —— 中性灰阶 —— */
  --brand-gray:   {gray};
  --brand-gray-2: {gray2};
  --brand-line:   {line};

  /* —— 图表辅助色 —— */
  --brand-chart-3: {c3};
  --brand-chart-4: {c4};

  /* —— 字体族 —— */
  --font-display: 'Archivo', 'Noto Sans SC', system-ui, sans-serif;
  --font-cjk:     'Noto Sans SC', 'PingFang SC', system-ui, sans-serif;
  --font-script:  'Caveat', cursive;

  /* —— 品牌文本 —— */
  --brand-logo-cn: "{a.logo_cn}";
  --brand-logo-en: "{a.logo_en}";
}}
"""


def rename_in_slides(root, pairs):
    n = 0
    for f in sorted(glob.glob(os.path.join(root, "slides", "[0-9]*.html"))):
        s = open(f, encoding="utf-8").read()
        o = s
        for old, new in pairs:
            s = s.replace(old, new)
        if s != o:
            open(f, "w", encoding="utf-8").write(s)
            n += 1
    return n


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--primary", required=True, help="主品牌色，如 #FB7299")
    ap.add_argument("--logo-cn", required=True, dest="logo_cn", help="徽标中文名")
    ap.add_argument("--logo-en", required=True, dest="logo_en", help="徽标英文名")
    ap.add_argument("--ink"); ap.add_argument("--bg")
    ap.add_argument("--ink2"); ap.add_argument("--primary-deep", dest="primary_deep")
    ap.add_argument("--primary-soft", dest="primary_soft")
    ap.add_argument("--chart3"); ap.add_argument("--chart4")
    ap.add_argument("--gray"); ap.add_argument("--gray2"); ap.add_argument("--line")
    ap.add_argument("--dark", action="store_true", help="深色皮肤（墨色转浅、页底转深）")
    ap.add_argument("--rename", action="append", default=[], metavar="OLD=NEW",
                    help="替换正文里的旧品牌名（可多次），如 --rename 美团=B站")
    ap.add_argument("--out", default=None, help="输出路径，默认 slides/theme.css")
    a = ap.parse_args()

    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    out = a.out or os.path.join(root, "slides", "theme.css")
    open(out, "w", encoding="utf-8").write(build_theme(a))
    print(f"✓ 已生成皮肤: {out}")

    if a.rename:
        pairs = []
        for r in a.rename:
            if "=" in r:
                old, new = r.split("=", 1); pairs.append((old, new))
        if pairs:
            n = rename_in_slides(root, pairs)
            print(f"✓ 正文品牌名替换 {pairs} → 改动 {n} 个文件")

    print("→ 接着跑：python3 scripts/bundle_html.py && python3 scripts/build_pptx.py && python3 scripts/build_pdf.py")


if __name__ == "__main__":
    main()
