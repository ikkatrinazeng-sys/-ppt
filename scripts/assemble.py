#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
声明式排序 —— 换页顺序不用再手动 mv 文件名、手动改页码。
写一个 outline.txt（每行一个版式名，不带 NN- 编号前缀），跑这个脚本，
slides/ 里的文件会按这个顺序自动重排 + 重新编号（01, 02, 03…），
页脚的 "NN / 总数" 也会自动刷新。

用法:
    python3 scripts/assemble.py                    # 用 slides/outline.txt
    python3 scripts/assemble.py --outline my.txt    # 指定别的清单
    python3 scripts/assemble.py --dry-run           # 只预览，不真的改文件
    python3 scripts/assemble.py --write-current      # 把当前顺序写出一份 outline.txt（新项目起手用）

outline.txt 格式（# 开头是注释，空行忽略）：
    cover
    contents
    section          # 章节①
    data
    timeline
    section-tech     # 章节②
    ...
"""
import argparse, glob, os, re, sys

NUM_RE = re.compile(r'^(\d+)-(.+)\.html$')


def scan(slides_dir):
    """返回 { 去掉编号的名字: 完整文件路径 }"""
    mapping = {}
    for f in sorted(glob.glob(os.path.join(slides_dir, "[0-9]*.html"))):
        m = NUM_RE.match(os.path.basename(f))
        if m:
            mapping[m.group(2)] = f
    return mapping


def read_outline(path):
    names = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.split("#", 1)[0].strip()
            if line:
                names.append(line)
    return names


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--slides", default="slides")
    ap.add_argument("--outline", default=None, help="默认 slides/outline.txt")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--write-current", action="store_true",
                     help="把当前 slides/ 顺序写出 outline.txt，不重排")
    a = ap.parse_args()

    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    slides_dir = os.path.join(root, a.slides)
    outline_path = a.outline or os.path.join(slides_dir, "outline.txt")

    mapping = scan(slides_dir)

    if a.write_current:
        names = []
        for f in sorted(glob.glob(os.path.join(slides_dir, "[0-9]*.html"))):
            m = NUM_RE.match(os.path.basename(f))
            if m:
                names.append(m.group(2))
        with open(outline_path, "w", encoding="utf-8") as f:
            f.write("\n".join(names) + "\n")
        print(f"✓ 已按当前顺序写出: {outline_path}（{len(names)} 项，可编辑排序后重跑 assemble.py）")
        return

    if not os.path.isfile(outline_path):
        sys.exit(f"✗ 找不到清单文件: {outline_path}\n"
                  f"  先跑 --write-current 生成一份，再编辑排序。")

    names = read_outline(outline_path)
    if not names:
        sys.exit(f"✗ {outline_path} 是空的")

    missing = [n for n in names if n not in mapping]
    if missing:
        avail = ", ".join(sorted(mapping.keys()))
        sys.exit(f"✗ outline 里这些名字在 slides/ 找不到对应文件: {missing}\n"
                  f"  可用的名字有: {avail}")

    dup = {n for n in names if names.count(n) > 1}
    if dup:
        sys.exit(f"✗ outline 里有重复的名字: {sorted(dup)}")

    # 清单没提到的文件，按原顺序自动追加到末尾——
    # 全部一起连续重编号，避免「未提及文件保留旧编号」跟新编号撞车。
    unused = [n for n in mapping if n not in names]
    final_order = names + unused

    print(f"→ 按 {outline_path} 重排 {len(names)} 页" +
          (f"，另有 {len(unused)} 个未列出的文件按原顺序追加到末尾" if unused else "") + "：")
    plan = [(mapping[n], os.path.join(slides_dir, f"{i:02d}-{n}.html"))
            for i, n in enumerate(final_order, 1)]
    for old, new in plan:
        mark = "  " if os.path.basename(old) == os.path.basename(new) else "→ "
        print(f"  {os.path.basename(old):28s} {mark} {os.path.basename(new)}")

    if a.dry_run:
        print("\n(--dry-run，未实际修改文件)")
        return

    # 用临时后缀两阶段改名，避免中间态互相覆盖
    for old, new in plan:
        os.rename(old, old + ".tmp")
    for old, new in plan:
        os.rename(old + ".tmp", new)

    print(f"\n✓ 重排完成。")

    try:
        import renumber
        total, changed = renumber.renumber(slides_dir)
        print(f"✓ 页码已刷新：共 {total} 页，更新 {changed} 个文件")
    except Exception as e:
        print(f"! 页码未能自动刷新（{e}），可手动跑 python3 scripts/renumber.py")


if __name__ == "__main__":
    main()
