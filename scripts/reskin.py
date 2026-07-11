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

  # 用真实 logo 图片（而非文字方块）
  python3 scripts/reskin.py --primary "#FB7299" --logo-en "bilibili" \\
      --logo-image ./bilibili-logo.png

依赖：无（纯标准库）
"""
import argparse, base64, glob, mimetypes, os, re, sys


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


def lum(a):  # 感知亮度 0-255（用于 on-primary 深浅二选一，简单加权即可）
    r, g, b = hexv(a)
    return 0.299*r + 0.587*g + 0.114*b


def wcag_luminance(hexcolor):
    """WCAG 相对亮度（0~1），标准 sRGB 伽马校正公式。"""
    def chan(c):
        c = c / 255.0
        return c/12.92 if c <= 0.03928 else ((c+0.055)/1.055) ** 2.4
    r, g, b = hexv(hexcolor)
    return 0.2126*chan(r) + 0.7152*chan(g) + 0.0722*chan(b)


def contrast_ratio(a, b):
    """WCAG 对比度，返回如 4.5 这样的数值，越大越清楚。"""
    la, lb = wcag_luminance(a), wcag_luminance(b)
    lighter, darker = max(la, lb), min(la, lb)
    return (lighter + 0.05) / (darker + 0.05)


def check_contrast(pairs):
    """pairs: [(标签, 前景色, 背景色, 建议阈值)] -> 打印警告，返回是否有问题。"""
    warned = False
    for label, fg, bg, min_ratio in pairs:
        ratio = contrast_ratio(fg, bg)
        if ratio < min_ratio:
            warned = True
            print(f"  ⚠ {label}：对比度 {ratio:.1f}:1（建议 ≥{min_ratio}:1）"
                  f"—— {fg} / {bg} 偏灰糊，正式使用前建议手动调深/调浅其中一色。")
    return warned


def derive(a):
    """从命令行参数推导出完整色板，返回 dict（供渲染 CSS 和对比度检查共用）。"""
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

    logo_cn = a.logo_cn
    logo_image = 'none'
    if a.logo_image:
        if not os.path.isfile(a.logo_image):
            sys.exit(f"✗ 找不到 logo 图片: {a.logo_image}")
        mime = mimetypes.guess_type(a.logo_image)[0] or 'image/png'
        b64 = base64.b64encode(open(a.logo_image, 'rb').read()).decode('ascii')
        logo_image = f'url("data:{mime};base64,{b64}")'
        logo_cn = ''  # 图片模式：清空文字，避免和图标重叠

    return dict(p=p, ink=ink, bg=bg, ink2=ink2, pdeep=pdeep, psoft=psoft,
                c3=c3, c4=c4, gray=gray, gray2=gray2, line=line, white=white,
                onp=onp, onp2=onp2, logo_cn=logo_cn, logo_image=logo_image)


def build_theme(a):
    d = derive(a)
    p, ink, bg, ink2 = d['p'], d['ink'], d['bg'], d['ink2']
    pdeep, psoft, c3, c4 = d['pdeep'], d['psoft'], d['c3'], d['c4']
    gray, gray2, line, white = d['gray'], d['gray2'], d['line'], d['white']
    onp, onp2 = d['onp'], d['onp2']
    logo_cn, logo_image = d['logo_cn'], d['logo_image']

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
  --brand-logo-cn: "{logo_cn}";
  --brand-logo-en: "{a.logo_en}";

  /* —— 真实 logo 图片（可选）—— */
  --brand-logo-image: {logo_image};
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
    ap.add_argument("--logo-cn", default="", dest="logo_cn",
                    help="徽标中文方块字（用 --logo-image 时可不填，会自动清空）")
    ap.add_argument("--logo-en", required=True, dest="logo_en", help="徽标英文名")
    ap.add_argument("--logo-image", dest="logo_image", default=None,
                    help="真实 logo 图片路径（PNG/SVG/JPG），会 base64 内嵌进 theme.css，"
                         "优先于 --logo-cn 显示")
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

    if not a.logo_cn and not a.logo_image:
        sys.exit("✗ 请提供 --logo-cn（文字方块字）或 --logo-image（真实 logo 图片）二选一")

    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    out = a.out or os.path.join(root, "slides", "theme.css")
    open(out, "w", encoding="utf-8").write(build_theme(a))
    print(f"✓ 已生成皮肤: {out}")

    d = derive(a)
    print("\n→ 对比度自检（WCAG，大字/粗体标题按 ≥3:1，正文按 ≥4.5:1）：")
    warned = check_contrast([
        ("正文墨色 vs 页底",       d['ink'],  d['bg'],      4.5),
        ("次级墨色 vs 页底",       d['ink2'], d['bg'],      3.0),
        ("主色高亮块文字 vs 主色", d['onp'],  d['p'],       3.0),
        ("主色 vs 页底（可辨识度）", d['p'],  d['bg'],      1.6),
    ])
    if not warned:
        print("  ✓ 全部达标，配色清晰可读。")

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
