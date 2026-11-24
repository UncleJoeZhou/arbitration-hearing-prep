# Word / HTML 排版技术要点

庭审材料的技术实现要点，保证"数据准确、渲染干净、风格统一"。

## 1. 数据与渲染分离（防再生幻觉）

- 权威数据（争议焦点、法条、参考案例、问题清单、当事人信息）集中存放在一处数据定义中。
- 渲染脚本**复用**这份数据（用 `exec` 截取到渲染标记前的数据段，或 `import`），**不重新 OCR 取值、不复制粘贴**——从源头杜绝二次录入出错。
- 示例：`exec(open("数据脚本.py").read().split("# 渲染")[0], ns)` 取出数据变量。

## 2. 渲染层统一清理 clean()

- 在渲染层加一个 `clean(s)` 函数，对所有进入文档的文本统一清理：
  - 去失效 markdown 标记 `**`；
  - 去跳脱话术（对照 style-rules.md 的禁用表）；
  - 去彩色标记性标签（正则 `【(?:核心|关键|举证责任)[^】]*】`）；
  - 去 emoji、去面向裁判者不宜的内部措辞（OCR 纠错过程等）。
- docx 在 `para()` 等渲染函数入口对 text 统一 `clean`；html 在 `esc()` 内先 `clean` 再转义。

## 3. 风格统一（一处改全文档生效）

- 把字体常量 `CN=HEI="宋体"`、颜色常量 `DARK=ACCENT=GREY=RGBColor(0,0,0)` 统一设为宋体与黑色，所有渲染调用这些常量，即实现"通篇宋体、通篇黑色"，无需逐处改。

## 4. python-docx 中文字体

- 仅设 `run.font.name` 对中文不够，须设 OOXML 的 `w:rFonts` 的 `w:eastAsia`（及 ascii/hAnsi）：
```python
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
def set_cjk(run, name="宋体"):
    run.font.name = name
    rpr = run._element.get_or_add_rPr()
    rf = rpr.find(qn('w:rFonts'))
    if rf is None:
        rf = OxmlElement('w:rFonts'); rpr.append(rf)
    rf.set(qn('w:eastAsia'), name); rf.set(qn('w:ascii'), name); rf.set(qn('w:hAnsi'), name)
```

## 5. 图片嵌入

- **Word**：`doc.add_picture(文件路径, width=Cm(n))`，居中。
- **HTML**：base64 嵌入（`<img src="data:image/png;base64,...">`），自包含、不依赖外部图床，方便单文件查看。

## 6. 输出

- Word 主件（.docx）＋ HTML 辅件（.html）。
- 嵌入：案件事实时间轴图、双方主张对比图、关键合同条款截图。
- 验证：统计段落/表格/图片数；检查字体集合（仅宋体）、颜色集合（仅黑）；确认跳脱话术、失效 `**`、内部措辞计数为 0。

## 7. 交付整理

- 规范命名、编号排序，整理进一个文件夹供发飞书/归档。
- **原文件保留、仅复制**，不移动、不删除。
- 三份以上材料须逐一核对归属（我方/对方/程序）再命名，不张冠李戴。

## 8. 运行时

- 优先用明确的 Python 解释器路径（managed 运行时或项目 venv），避免依赖不确定的 `PATH`。
- 依赖（python-docx 等）装入隔离 venv，不污染用户环境。
