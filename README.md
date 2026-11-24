# arbitration-hearing-prep

Agent Skill：仲裁 / 诉讼 **庭审准备**工作体系（「arbitration 仲裁系列」第一篇）。

从收到案件材料到交付庭审问题清单：读透材料 → 锁定核心条款 → 归纳争议焦点 → 检索核验法条与案例 → 设计分层庭审问题清单 → 排版输出（Word 主件＋HTML 辅件）。

## 安装

将本目录放到 Agent Skills 目录下，例如：

```bash
git clone https://github.com/UncleJoeZhou/arbitration-hearing-prep.git \
  ~/.agents/skills/arbitration-hearing-prep
```

具体路径以你使用的客户端（Cursor / Claude Code / 其他）为准，确保能加载 `SKILL.md`。

## 何时触发

交付仲裁或诉讼材料，并需要：

- 庭审问题清单 / 庭前问题清单 / 庭审提纲 / 发问清单
- 出庭材料、争议焦点与法律依据分析
- 按庭审准备体系做、直接出 Word、整理发飞书

详见 `SKILL.md` 与 `references/routing.md`（含与其他技能的路由边界）。

## 目录结构

```
SKILL.md                          # 技能入口与流程
references/
  accuracy-rules.md               # 事实核验抗幻觉
  style-rules.md                  # 正式文书风格
  question-list-design.md         # 问题清单分层设计
  docx-html-render.md             # Word/HTML 排版要点
  routing.md                      # 系列路由与触发词分配
scripts/
  pack_onedrive.py                # 可选：云盘备存（需 ARBITRATION_BACKUP_DIR）
```

## 三大铁律

1. **事实核验抗幻觉** — 以原始材料为准；法条、案例可核验
2. **正式文书风格** — 公文表述，面向裁判者
3. **问题清单分层设计** — 每问含发问对象、依据条款、问题、设问目的

## 可选备存脚本

```bash
export ARBITRATION_BACKUP_DIR="$HOME/path/to/backup-dir"
python3 scripts/pack_onedrive.py
```

## License

MIT
