#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动页码 —— 按 slides/ 里文件名顺序，把每页的「NN / 总数」刷成正确值。
加页 / 删页 / 换序后跑一次即可，无需手动改页码。
（三个导出脚本会在开头自动调用它，一般不用手动运行。）

用法:  python3 scripts/renumber.py
"""
import glob, os, re, sys

PAGENO = re.compile(r'>\s*\d{1,2}\s*/\s*\d{1,2}\s*<')  # 只匹配「>NN / TT<」页码文本


def renumber(slides_dir):
    files = sorted(glob.glob(os.path.join(slides_dir, "[0-9]*.html")))
    total = len(files)
    changed = 0
    for i, f in enumerate(files, 1):
        s = open(f, encoding="utf-8").read()
        new = PAGENO.sub(f'>{i:02d} / {total}<', s)
        if new != s:
            open(f, "w", encoding="utf-8").write(new)
            changed += 1
    return total, changed


if __name__ == "__main__":
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    total, changed = renumber(os.path.join(root, "slides"))
    print(f"✓ 页码已刷新：共 {total} 页，更新 {changed} 个文件")
