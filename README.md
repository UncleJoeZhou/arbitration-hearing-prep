# arbitration-hearing-prep

Agent Skill：仲裁 / 诉讼 **庭审准备**工作体系。

读透材料 → 锁定核心条款 → 归纳争议焦点 → 核验法条与案例 → 设计分层庭审问题清单 → 输出 Word + HTML。

适用于 [Agent Skills](https://agentskills.io) 标准客户端（Cursor、Claude Code、Codex 等）。

## 快速安装

### 方式 A：一键安装（推荐）

```bash
npx skills add UncleJoeZhou/arbitration-hearing-prep -g
```

若提示选择 agent，选你正在用的（如 `cursor`）。

### 方式 B：手动安装到 Cursor（全局）

```bash
git clone https://github.com/UncleJoeZhou/arbitration-hearing-prep.git \
  ~/.cursor/skills/arbitration-hearing-prep
```

项目内安装（仅当前仓库可用）：

```bash
git clone https://github.com/UncleJoeZhou/arbitration-hearing-prep.git \
  .cursor/skills/arbitration-hearing-prep
```

兼容路径：也可装到 `~/.agents/skills/arbitration-hearing-prep`。

安装后**重启 Cursor / 新开 Agent 对话**，在聊天里用 `/` 搜索 `arbitration-hearing-prep`，或直接说「按庭审准备体系做庭审问题清单」。

## 怎么用

1. 把案件材料（PDF / 扫描件 / 图片 / 文本）放到当前工作区或直接丢进对话。
2. 说清需求，例如：「梳理争议焦点并出庭审问题清单，直接出 Word」。
3. Agent 应按本技能跑完六步并交付 Word 主件 + HTML 辅件。

生成 Word 时若环境缺少依赖：

```bash
python3 -m pip install python-docx
```

法条与案例核验依赖你可用的权威检索来源（本技能不捆绑任何付费数据库）。

## 目录

```
SKILL.md
references/
  accuracy-rules.md
  style-rules.md
  question-list-design.md
  docx-html-render.md
  routing.md
scripts/
  check_links.py          # 校验文档交叉引用
```

## 三大铁律

1. 事实核验抗幻觉
2. 正式文书风格
3. 问题清单分层设计（每问：发问对象 / 依据条款 / 问题 / 设问目的）

## License

MIT
