#!/usr/bin/env python3
"""校验本技能目录内 Markdown 反引号路径引用是否存在。

用法（在技能根目录或任意位置）：
    python3 scripts/check_links.py
"""
from __future__ import annotations

import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REF = re.compile(r"`([^`\s]+\.(?:md|py))`")


def main() -> int:
    bad: list[tuple[str, str]] = []
    for base, _, names in os.walk(ROOT):
        if "__pycache__" in base or "/.git/" in base.replace("\\", "/"):
            continue
        for name in names:
            if not name.endswith(".md"):
                continue
            path = os.path.join(base, name)
            text = open(path, encoding="utf-8").read()
            for m in REF.finditer(text):
                ref = m.group(1)
                if ref.startswith("http"):
                    continue
                candidates = [
                    os.path.join(ROOT, ref),
                    os.path.join(os.path.dirname(path), ref),
                    os.path.join(ROOT, "references", os.path.basename(ref)),
                    os.path.join(ROOT, "scripts", os.path.basename(ref)),
                ]
                if not any(os.path.isfile(c) for c in candidates):
                    bad.append((os.path.relpath(path, ROOT), ref))
    if bad:
        print("断链：")
        for src, ref in bad:
            print(f"  {src} → {ref}")
        return 1
    print("断链自检：通过")
    return 0


if __name__ == "__main__":
    sys.exit(main())
