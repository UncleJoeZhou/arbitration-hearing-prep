#!/usr/bin/env python3
"""arbitration 系列云盘备存脚本。

用法：
    export ARBITRATION_BACKUP_DIR="$HOME/path/to/Skills Library/法律工作"
    python3 scripts/pack_onedrive.py

环境变量：
    ARBITRATION_BACKUP_DIR  备存输出目录（必填；未设置则报错退出）
    ARBITRATION_SKILLS_DIR  技能根目录（默认 ~/.workbuddy/skills 或同级上级）

产出（写入 ARBITRATION_BACKUP_DIR）：
    arbitration-hearing-prep.zip
    arbitration-award-drafter.zip
    arbitration-series.zip     含两个技能目录及系列路由说明
    arbiter-copilot-assets.zip  Arbiter Copilot 三目录只读灾备（产品资产，非本系列）
    arbitration-series-MANIFEST.md   人可读备存清单（文件明细＋SHA256＋恢复步骤）

铁律：必须用 Python zipfile（对非 ASCII 文件名自动置 UTF-8 标志），
绝不用 macOS 自带 zip 命令（中文文件名不置标志，跨平台解压乱码，
会破坏 references/ 加载路径）。

打包前两道自检（2026-11-06 事故后加固）：
    1. 断链自检：扫描两技能目录内所有 .md 的反引号路径引用，缺文件即拒绝打包。
    2. 回退保护：新包文件数少于同名旧包时拒绝覆盖（防止本机文件丢失后
       把含更多文件的旧备份一并抹掉）。确需覆盖时加 --force。

另：每次备存自动重写 MANIFEST，使云上留有一份不依赖本机即可核对、
可据以恢复的目录清单。Arbiter Copilot 资产包若存在，一并列入清单附录，
但明确标注为产品资产、不属本系列。
"""
import datetime
import glob
import hashlib
import os
import re
import sys
import zipfile

HOME = os.path.expanduser("~")
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_SKILL_ROOT = os.path.dirname(_SCRIPT_DIR)
_DEFAULT_SKILLS = os.path.join(HOME, ".workbuddy", "skills")
SKILLS = os.environ.get("ARBITRATION_SKILLS_DIR") or (
    os.path.dirname(_SKILL_ROOT) if os.path.basename(_SKILL_ROOT) == "arbitration-hearing-prep"
    else _DEFAULT_SKILLS
)
LIB = os.environ.get("ARBITRATION_BACKUP_DIR", "").strip()
MEMBERS = ["arbitration-hearing-prep", "arbitration-award-drafter"]
# Arbiter Copilot 产品资产：只做只读灾备，不纳入本系列路由，也不参与断链自检
# （其内部引用指向桌面工作台与 .arbiter 状态目录，按本系列规则扫描会误判）。
ASSET_MEMBERS = ["arbiter-bench", "arbiter-cockpit", "pixelcourt-cockpit"]
ASSET_ZIP = "arbiter-copilot-assets.zip"
REF = re.compile(r"`([^`\s]+\.(?:md|py))`")


def files_under(root):
    out = []
    for base, _, names in os.walk(root):
        for n in names:
            if n.startswith(".") or "__pycache__" in base:
                continue
            fp = os.path.join(base, n)
            out.append((fp, os.path.relpath(fp, os.path.dirname(root))))
    return sorted(out)


def check_links():
    """返回断链列表；非空则拒绝打包。"""
    bad = []
    for name in MEMBERS:
        root = os.path.join(SKILLS, name)
        for fp in glob.glob(os.path.join(root, "**", "*.md"), recursive=True):
            for ref in set(REF.findall(open(fp, encoding="utf-8").read())):
                if ref.startswith(("references/", "scripts/")):
                    target = os.path.join(root, ref)
                elif ref.startswith(tuple(m + "/" for m in MEMBERS)):
                    target = os.path.join(SKILLS, ref)
                else:
                    continue
                if not os.path.isfile(target):
                    bad.append((os.path.relpath(fp, SKILLS), ref))
    return bad


def old_count(path):
    if not os.path.exists(path):
        return None
    try:
        with zipfile.ZipFile(path) as z:
            return len(z.namelist())
    except zipfile.BadZipFile:
        return -1


def pack_one(name, force=False):
    src = os.path.join(SKILLS, name)
    dst = os.path.join(LIB, name + ".zip")
    items = files_under(src)
    prev = old_count(dst)
    if prev is not None and len(items) < prev and not force:
        raise RuntimeError(
            f"{name}.zip 回退保护：本机 {len(items)} 文件 < 旧包 {prev} 文件，"
            f"拒绝覆盖。先查是否丢文件，确需覆盖加 --force。"
        )
    with zipfile.ZipFile(dst, "w", zipfile.ZIP_DEFLATED) as z:
        for fp, arc in items:
            z.write(fp, arc)
    return dst, os.path.getsize(dst), len(items), prev


def pack_series(force=False):
    dst = os.path.join(LIB, "arbitration-series.zip")
    items = []
    for name in MEMBERS:
        items += files_under(os.path.join(SKILLS, name))
    routing = os.path.join(SKILLS, MEMBERS[0], "references", "routing.md")
    extra = [(routing, "arbitration-series-路由说明.md")] if os.path.isfile(routing) else []
    count = len(items) + len(extra)
    prev = old_count(dst)
    if prev is not None and count < prev and not force:
        raise RuntimeError(
            f"arbitration-series.zip 回退保护：本次 {count} 文件 < 旧包 {prev} 文件，"
            f"拒绝覆盖。先查是否丢文件，确需覆盖加 --force。"
        )
    with zipfile.ZipFile(dst, "w", zipfile.ZIP_DEFLATED) as z:
        for fp, arc in items + extra:
            z.write(fp, arc)
    return dst, os.path.getsize(dst), count, prev


def pack_assets(force=False):
    """Arbiter Copilot 产品资产的只读灾备。目录缺失时跳过重打，保留云上旧包。"""
    dst = os.path.join(LIB, ASSET_ZIP)
    roots = [os.path.join(SKILLS, n) for n in ASSET_MEMBERS]
    missing = [n for n, r in zip(ASSET_MEMBERS, roots) if not os.path.isdir(r)]
    prev = old_count(dst)
    if missing:
        note = "跳过（目录不存在：" + "、".join(missing) + "），保留云上旧包"
        return dst, os.path.getsize(dst) if os.path.isfile(dst) else 0, None, prev, note
    # 用 files_under 全量收录，包含 arbiter-bench/demo 下的演示 .arbiter 状态数据
    # （属产品自带样例，非真实案件材料；清单附录会注明口径）。
    items = []
    for r in roots:
        items += files_under(r)
    items.sort(key=lambda x: x[1])
    if prev is not None and len(items) < prev and not force:
        raise RuntimeError(
            f"{ASSET_ZIP} 回退保护：本机 {len(items)} 文件 < 旧包 {prev} 文件，"
            f"拒绝覆盖。确需覆盖加 --force。"
        )
    with zipfile.ZipFile(dst, "w", zipfile.ZIP_DEFLATED) as z:
        for fp, arc in items:
            z.write(fp, arc)
    return dst, os.path.getsize(dst), len(items), prev, None


# 云上除系列三包外，另有 Arbiter Copilot 产品资产的只读灾备包；
# 仅列入清单附录，不纳入本系列路由与断链自检。
ASSET_ZIPS = [ASSET_ZIP]


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def write_manifest():
    """在云上写一份人可读的备存清单，使恢复不依赖本机记忆。"""
    manifest = os.path.join(LIB, "arbitration-series-MANIFEST.md")
    core = [m + ".zip" for m in MEMBERS] + ["arbitration-series.zip"]
    extra = [n for n in ASSET_ZIPS if os.path.isfile(os.path.join(LIB, n))]
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    lines = [
        "# arbitration 系列 · 云盘备存清单",
        "",
        f"- 生成时间：{now}",
        f"- 备存位置：`{LIB}`",
        f"- 本机源：`{SKILLS}/arbitration-hearing-prep/`、`{SKILLS}/arbitration-award-drafter/`",
        "- 打包方式：Python `zipfile`（中文名条目置 UTF-8 标志），禁用 macOS 自带 `zip`。",
        "- 备存脚本：`arbitration-hearing-prep/scripts/pack_onedrive.py`，改动任一文件后重跑即刷新本清单。",
        "",
        "## 一、系列备份包",
        "",
        "| 包 | 大小 | 文件数 | SHA-256 |",
        "|---|---:|---:|---|",
    ]
    for n in core:
        p = os.path.join(LIB, n)
        if not os.path.isfile(p):
            continue
        with zipfile.ZipFile(p) as z:
            cnt = len(z.namelist())
        lines.append(f"| `{n}` | {os.path.getsize(p)} B | {cnt} | `{sha256(p)}` |")
    lines += ["", "### 包内文件明细", ""]
    for n in core:
        p = os.path.join(LIB, n)
        if not os.path.isfile(p):
            continue
        lines.append(f"**{n}**")
        lines.append("")
        with zipfile.ZipFile(p) as z:
            for name in sorted(z.namelist()):
                lines.append(f"- `{name}`")
        lines.append("")
    lines += [
        "## 二、恢复步骤",
        "",
        "1. 从云上取 `arbitration-series.zip`，用 Python 解压（勿用 macOS 归档实用工具处理中文名）：",
        "   `python3 -c \"import zipfile; zipfile.ZipFile('arbitration-series.zip').extractall('<目标skills目录>')\"`",
        "2. 解压后应得到两个技能目录与 `arbitration-series-路由说明.md`；逐一核对上表文件数。",
        "3. 跑断链自检：",
        "   `python3 ~/.workbuddy/skills/arbitration-hearing-prep/scripts/pack_onedrive.py`",
        "   该命令会扫描全部 `.md` 反引号路径引用，缺文件即拒绝打包并打印断链位置。",
        "4. 如需单技能恢复，用对应的单包即可（`arbitration-hearing-prep.zip` 或 `arbitration-award-drafter.zip`）。",
        "",
        "## 三、边界声明",
        "",
        "- 本系列为纯方法论与文书交付体系，不依赖 `.arbiter/` 状态目录或任何 MCP 服务。",
        "- Arbiter Copilot 属桌面产品资产，靠 `.arbiter/` JSON 状态机驱动，与本系列不是同一层，不互相替代。",
        "- 判别顺序见 `arbitration-hearing-prep/references/routing.md` 第三节；中性词「争议焦点」「提问清单」「裁决书」不单独作触发依据。",
    ]
    if extra:
        lines += ["", "## 附录 · 非系列资产（仅作灾备，不参与路由）", ""]
        for n in extra:
            p = os.path.join(LIB, n)
            with zipfile.ZipFile(p) as z:
                cnt = len(z.namelist())
            lines.append(f"- `{n}`：{os.path.getsize(p)} B，{cnt} 文件，SHA-256 `{sha256(p)}`。")
            lines.append("  内容为 Arbiter Copilot 三个技能目录的只读副本，用于防本机误删；不作为本系列技能调用。")
            lines.append("  其中含 `arbiter-bench/demo/` 下自带的演示 `.arbiter` 状态数据，属产品样例，非真实案件材料。")
    with open(manifest, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    # 云上文件统一为 644，避免个别包被写成 700 后其他设备/账号取用不便。
    for n in core + extra + [os.path.basename(manifest)]:
        p = os.path.join(LIB, n)
        if os.path.isfile(p):
            os.chmod(p, 0o644)
    return manifest


if __name__ == "__main__":
    force = "--force" in sys.argv
    if not LIB:
        print(
            "请设置环境变量 ARBITRATION_BACKUP_DIR 为备存输出目录，例如：\n"
            "  export ARBITRATION_BACKUP_DIR=\"$HOME/Library/CloudStorage/"
            "<你的云盘>/Skills Library/法律工作\""
        )
        sys.exit(1)
    os.makedirs(LIB, exist_ok=True)

    bad = check_links()
    if bad:
        print("断链自检未通过，已拒绝打包：")
        for src, ref in bad:
            print(f"  {src} → {ref}")
        sys.exit(1)
    print("断链自检：通过（引用全部存在）")

    try:
        for name in MEMBERS:
            p, size, n, prev = pack_one(name, force)
            print(f"单包  {os.path.basename(p):42s} {size:>8d} B  {n} 文件"
                  + (f"（旧包 {prev} 文件）" if prev is not None else ""))
        p, size, n, prev = pack_series(force)
        print(f"总包  {os.path.basename(p):42s} {size:>8d} B  {n} 文件"
              + (f"（旧包 {prev} 文件）" if prev is not None else ""))
        p, size, n, prev, note = pack_assets(force)
        if note:
            print(f"资产  {os.path.basename(p):42s} {note}")
        else:
            print(f"资产  {os.path.basename(p):42s} {size:>8d} B  {n} 文件"
                  + (f"（旧包 {prev} 文件）" if prev is not None else ""))
    except RuntimeError as e:
        print(f"备存中止：{e}")
        sys.exit(2)

    mf = write_manifest()
    print(f"清单  {os.path.basename(mf):42s} {os.path.getsize(mf):>8d} B")
