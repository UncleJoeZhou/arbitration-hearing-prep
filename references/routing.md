# arbitration 系列路由说明

本文件解决一个问题：本机同时存在两套仲裁相关技能，名称相近、业务环节有交叠，容易误路由。此处划清边界，并分配互不冲突的触发词。

## 一、两套体系的性质

| 维度 | arbitration 系列 | Arbiter Copilot 资产 |
| --- | --- | --- |
| 目录 | `arbitration-hearing-prep`、`arbitration-award-drafter` | `arbiter-bench`、`arbiter-cockpit`、`pixelcourt-cockpit` |
| 性质 | 人读的方法论与文书交付体系 | 桌面产品 Arbiter Copilot 的配套技能组 |
| 依赖 | 无。纯文本规则＋通用文件工具 | 案件根 `.arbiter/` 状态目录、自定义 MCP（`127.0.0.1:7820`）、六段流水线脚本与自检 |
| 使用者视角 | 律师或仲裁员在对话里交付案件材料，要求直接拿到可用的文书 | 仲裁员在办案台里推进案件状态、定立场、组装裁决 |
| 产出物 | Word 主件、HTML 辅件、可视化图、规范命名的交付文件夹 | `.arbiter/workspace-state.json` 等 JSON 状态文件，供工作台读取 |
| 案件范围 | 任意新收材料，不要求历史状态 | 已建立 `.arbiter/` 状态目录的案件 |
| 状态 | 本系列为现行工作体系 | 属于既有资产，保留不动 |

两者不是同一层东西。前者是「人怎么把活干完、文书长什么样」，后者是「软件怎么记状态、怎么走门禁」。业务环节虽有交叠，产出形态与消费对象不同，不构成可互相替代的重复。

## 二、环节交叠的实情

| 环节 | Arbiter 侧 | arbitration 侧 |
| --- | --- | --- |
| 争点与提问清单 | `arbiter-bench` 的 1.2 五柱研判，产出 `analysisPanelState`，原文明确「不写法条依据」，是仲裁员的审理地图 | `arbitration-hearing-prep` 产出 Word 庭审问题清单，含法条核验、参考案例、发问对象、设问目的 |
| 裁决书 | `arbiter-bench` 的 1.6 裁决组装，脚本缝合已确认段落，原文写明「组装不是创作」，带硬门禁 | `arbitration-award-drafter` 从程序稿创作终版裁决书，补仲裁庭意见与裁决主文，含签发前自检 |

二者理论上可前后接力：先由裁决书起草技能形成说理，再由组装环节纳入状态机。任何一侧被清理，链条即断。

## 三、路由判别（按顺序执行）

第一步，看案件状态与用户措辞。案件目录已存在 `.arbiter/`，或用户明说「办案台、进卷、解析材料、五柱、审理答题表、定立场、程序稿校准、争点说理、裁决组装、`bind_workspace`、`claim_intake`」之一，走 Arbiter 资产，不走本系列。

第二步，看交付物要求。用户要求直接产出 Word／HTML 庭前材料、庭审问题清单、争议焦点与法律依据分析，且未提办案台，走 `arbitration-hearing-prep`。

第三步，看文书阶段。用户拿来程序性裁决书，要求转终版、补仲裁庭意见、起草裁决主文、做签发前核对，走 `arbitration-award-drafter`。

第四步，仍无法判别时，问一句用户，不要凭关键词自行选技能，更不要同时启动两套。

## 四、触发词分配

### 4.1 `arbitration-hearing-prep` 独占触发词

庭审问题清单、庭前问题清单、庭审提纲、发问清单、出庭材料、争议焦点与法律依据、争议焦点分析报告、按庭审准备体系做、按 arbitration 庭审准备做、直接出 Word、整理发飞书。

### 4.2 `arbitration-award-drafter` 独占触发词

程序稿转最终裁决书、帮我写裁决书、补充仲裁庭意见、起草裁决主文、填写五裁决、仲裁庭意见怎么写、审计裁决书、裁决书终稿核对、签发前检查。

### 4.3 保留给 Arbiter 资产、本系列不作主触发的词

办案台、进卷、解析缺口、五柱研判、读卷分析、审理答题表、定立场、程序稿校准、争点说理、整案组装、导入导出终版、`bind_workspace`、`claim_intake`、`open_workbench`。

### 4.4 中性词的处理

「争议焦点」「提问清单」「裁决书」三个词两边都会出现。单独出现时不得直接选技能，必须回到第三节的判别流程，结合「有无 `.arbiter/` 状态目录」与「要 JSON 状态还是要 Word 交付件」判断。本系列各技能的触发条件中，这三个词一律带限定语使用，不单独作为触发依据。

## 五、边界维护规则

一、本系列只改自己目录下的文件。Arbiter 资产属既有产品配套，其顶层 `SKILL.md`、六个子技能、自检脚本、合成夹具均不修改，避免破坏 29 模块自检与桌面工作台兼容性。

二、消歧采取单边策略：本系列改用具体独占触发词，并在各技能中写明「不适用情形」；Arbiter 侧保持原样。理由是本系列由当前会话直接维护，改动可控且可回退。

三、新增仲裁技能一律以 `arbitration-` 前缀命名，并在 `description` 中标注系列归属、独占触发词、不适用情形，同时更新本文件的触发词分配表。

四、每次改动本系列任一文件后，建议重跑云盘备存，使备份包与本机保持一致。备存一律用 Python `zipfile`，不得使用 macOS 自带 `zip` 命令。先设置 `ARBITRATION_BACKUP_DIR`，再执行：`python3 scripts/pack_onedrive.py`。

五、备存脚本 `scripts/pack_onedrive.py` 在打包前执行两道自检：断链自检（扫描两技能目录内全部 `.md` 的反引号路径引用，缺文件即拒绝打包）与回退保护（新包文件数少于同名旧包时拒绝覆盖）。不得绕过；确需覆盖旧包须显式加 `--force` 并先说明原因。脚本每次自动重写 `arbitration-series-MANIFEST.md`（包内文件明细、SHA-256、恢复步骤），使云上备份不依赖本机记忆即可核对与恢复。Arbiter 资产包只做只读灾备，不纳入本系列路由与断链自检。

## 六、备存位置

由环境变量 `ARBITRATION_BACKUP_DIR` 指定（例如个人云盘下的 `Skills Library/法律工作/`），产出：

- `arbitration-hearing-prep.zip`
- `arbitration-award-drafter.zip`
- `arbitration-series.zip`（系列总包，含两个技能目录及本路由说明）
- `arbiter-copilot-assets.zip`（Arbiter Copilot 三目录只读灾备，产品资产，非本系列）
- `arbitration-series-MANIFEST.md`（人可读清单：文件明细、SHA-256、恢复步骤、边界声明）

备存脚本为 `arbitration-hearing-prep/scripts/pack_onedrive.py`，改后重跑即可刷新四个包与清单。恢复时只取 `arbitration-series.zip` 即可重建本系列；用 Python `zipfile` 解压后跑一次脚本做断链自检，确认零断链再投入使用。
