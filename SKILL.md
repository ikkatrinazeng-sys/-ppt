---
name: brand-deck
description: 生成「大厂编辑风」的高设计感 PPT（16:9 HTML 幻灯片，可一键导出 PDF 与 PPTX），并支持一键换品牌皮肤。默认皮肤为美团黄黑（美团黄 #FFD100 + 墨黑 + 暖白），巨型标题、色块高亮、编号章节、黑白照拼贴、图表、手写体点缀。当用户要做大厂风 / 编辑风 / 某公司品牌风（如 B站粉、抖音黑金）的演示、汇报、路演、品牌介绍时使用——只需给出该公司 VI（主色/墨/底/字体/logo），整册即可换皮。

---

# 大厂编辑风 · 可换肤 Deck System

一套「**皮肤（VI）与骨架（版式+内容）分离**」的幻灯片系统。骨架是大厂编辑风的高设计感版式，皮肤是各公司品牌 VI。**HTML 是设计母本**，无头 Chrome 渲染，一键导出 **PDF（矢量）** 与 **PPTX（图片全铺，100% 保真）**。默认皮肤：美团黄黑。

## 何时用
- 用户要「大厂风 / 编辑风」的 PPT、汇报、路演、品牌页
- 用户给出某公司 VI，要一套「一眼是该品牌、但设计感远强于官网」的演示

## 🚀 第一步：先问用户这两件事（INTAKE）
**被调用后，先别急着生成**——先向用户确认下面两组信息，再据此「换肤 + 填内容」。

**问题 ①：你公司的图片 / logo / VI 是什么？**（决定「皮肤」）
- 发一张 **公司 logo / 品牌图 / 官网截图**，我来**提取主色和墨色**；或直接给 **主色 hex**
- 公司 **中文名 + 英文名**（用于徽标）
- （可选）字体偏好、是否有指定辅助色
- → 拿到后：看图取色，写进 [slides/theme.css](slides/theme.css)（`--brand-primary` / `--brand-ink` / `--brand-bg` / `--brand-chart-*` + `--brand-logo-cn/en`），即完成整册换皮。

**问题 ②：这份 PPT 要做什么？**（决定「内容」）
- 场景：融资路演 / 品牌介绍 / 季度汇报 / 产品发布 / 述职 …
- 受众 + 大致页数
- 核心内容：要讲哪几块、有哪些关键数据 / 案例 / 团队
- → 拿到后：从 17 种版式里挑合适的页，复制改写文案与数据。

> 问不全也能开工：VI 至少要「**主色 + 公司名**」，内容至少要「**场景 + 3~5 个要点**」，其余用合理默认补齐并向用户说明。
> 用户只给一张 logo 图时：用视觉识别其主色作 `--brand-primary`、深色作 `--brand-ink`，公司名填 logo 文案，即可先出一版换皮样册给用户确认。

## ⭐ 换肤（RESKIN）—— 本 skill 的核心能力
**换公司 = 只改 [slides/theme.css](slides/theme.css) 一个文件**，17 页 + 图表 + 星芒 + 角标细节整体换皮。
1. 拿到用户公司 VI，改 `theme.css` 里的：`--brand-primary`（主色）、`--brand-ink`（墨）、`--brand-bg`（页底）、`--brand-chart-3/4`（图表辅助色）、`--font-*`（字体）、`--brand-logo-cn`/`--brand-logo-en`（徽标中英文）。
2. 已备示例皮肤在 [themes/](themes/)：`meituan.css`（默认）、`bilibili.css`（B站粉）。换肤 = 把某个 `themes/x.css` 覆盖到 `slides/theme.css`，或直接改 `theme.css`。
3. **皮肤只管样式**：颜色、字体、logo 自动全局生效。**页面标题 / 正文 / 数据是「内容」**，随每份 deck 重写（正文里出现的品牌名，如页脚署名，也属内容，一并替换）。
4. 改完跑 `bundle_html.py` + 导出脚本刷新产物。

## 架构（皮肤 / 骨架分离）
- [slides/theme.css](slides/theme.css) —— **皮肤**：全部品牌 token（`--brand-*`）+ 字体 + logo 文案。换肤只动它。
- [slides/deck.css](slides/deck.css) —— **骨架引擎**：所有版式/组件，只引用 `var(--brand-*)`，不含任何硬编码品牌色。勿改。
- 每页 `<link theme.css><link deck.css>`；SVG 上色用工具类 `.f-primary/.f-ink/.s-primary/…`（引用变量，故图表也换皮）。

## 设计基调（美团默认皮肤，务必守住版式手法）
- **主调**：编辑风 · **明度**：浅色为主（主色底 / 墨底只作节奏撞色点）
- **主色三角色**：**关键词高亮块 / 撞色底 / 数据英雄块**，不铺满、不做渐变
- **字体**：西文巨字 Archivo Black｜中文思源黑 Heavy（Noto Sans SC 900）｜点缀 Caveat 手写体（英文短句）
- **母题**：小型大写标签 + 2px 墨线页眉页脚（页码）｜关键词高亮块 / 墨块反白｜四角星芒｜四角定位角标
- 细节规范见 [reference/design-spec.md](reference/design-spec.md)

## 十七种版式原型（在 `slides/` 里，直接复制改写）
| 文件 | 版式 | 用途 |
|---|---|---|
| `01-cover.html` | 封面：巨字 + 高亮块 + 手写点缀 | 开场 |
| `02-contents.html` | 目录（当前项黄条高亮） | 议程 |
| `03-section.html` | 章节页：黄底撞色 + 巨型编号 + 反白墨块 | 分节①（章节 01） |
| `04-data.html` | 黄色英雄数字 + 数据网格 | 数据/指标 |
| `05-timeline.html` | 横向时间轴 | 历程/路线 |
| `06-section-tech.html` | 章节页：巨型黄填充+黑描边编号 | 分节②（章节 02·描边版） |
| `07-content.html` | 三栏编辑卡片（中卡反黑做焦点） | 要点罗列 |
| `08-storyboard.html` | 满黄画布 + `▶▶▶` + 编号照片网格 | 流程/分镜/案例走查 |
| `09-image-text.html` | 左右图文（黑白照 + 黄色偏移块） | 案例/图文 |
| `10-team.html` | 黑白人物卡 + 黑色大数字卡 | 团队/嘉宾 |
| `11-duo.html` | 双人物大图 + 墨条名牌 + 引言 | 对话/双负责人 |
| `12-cover-b.html` | 封面 B：满黄 + 巨型描边字母母题 | 转场/大标题（撞色版） |
| `13-charts-growth.html` | 柱状图 + 折线图（纯 SVG） | 增长/趋势数据 |
| `14-charts-structure.html` | 环形图 + 横向排名条（纯 SVG/CSS） | 占比/结构/排名 |
| `15-data-yellow.html` | 满黄数据页：墨色英雄块 + 黑线数据网格 | 数据（撞色版） |
| `16-quote.html` | 墨底金句（黄字高亮） | 观点/金句 |
| `17-closing.html` | 黄底结束页 + 联系方式 | 收尾（放最后） |

## ⚠️ 查看方式（重要）
`slides/*.html` 现在引用**同级** `meituan.css`（`slides/meituan.css`）——避免 Safari 用 `file://` 打开时拦截「向上跨目录」加载的老问题。查看方式按稳妥程度排：
- **双击单页**：`slides/NN-*.html` 现在同级引用 CSS，Chrome/Safari 双击一般都正常。
- **零依赖保底**：若个别浏览器仍拦本地文件，跑 `python3 scripts/bundle_html.py`，打开 `standalone/NN-*.html`（单页内联，零外部依赖）或 `out/美团样册-单文件.html`（整册）。
- **最稳交付**：直接发 `out/deck.pptx`（每页全铺图，任何设备都对）。
- **开发预览**：本地服务器 `python3 -m http.server 4507` + Chrome 开 `index.html`（放映器）。

> 关键：`meituan.css` 必须和 `slides/*.html` 待在同一目录。移动幻灯片时**带上它**，否则又会黑白塌版。

## 生成一份新 deck 的流程
1. **选版式**：按内容从上表挑对应 `slides/*.html`，复制成新序号文件，改写文案。保持页眉 logo、页脚页码、`kicker` 标签结构不动。
2. **配图**：`07-image-text` 用 `<img>`，务必套 `.photo`（自动转黑白灰度 + 黄色偏移块）。占位可用 `https://picsum.photos/ID/700/700`，交付时替换为真实图。
3. **预览**：`.claude/launch.json` 已配 `deck`（`python3 -m http.server 4507`）。启动后开 `http://localhost:4507/index.html` —— 带键盘翻页（←/→）和全屏放映（F）。
4. **导出**：
   - PDF（矢量、可选中文字）：`python3 scripts/build_pdf.py`  → `out/deck.pdf`
   - PPTX（每页全铺高清图，PowerPoint/WPS 可打开）：`python3 scripts/build_pptx.py` → `out/deck.pptx`
   - 两个脚本自动探测本机 Chrome，无需服务器。PPTX 额外需 `pip install python-pptx`。

## 保持风格一致的硬规矩
- 每页**只保留一个视觉焦点**（一句巨字 / 一组数据 / 一张图），其余压成小字注释
- 主色**克制**：一页里主色块不超过两处；不配第三种彩色，只主色+墨+白
- 中文标题一律思源黑 **Heavy(900)**，行高 `1.12` 左右（避免叠字），字距微负
- 大写英文标签才用 `letter-spacing`；正文不拉字距
- 星芒母题每页 0~1 个，别撒满
- 页码 / 章节名的版面家具（`.furn-top` / `.furn-bot`）每页都保留，这是「编辑感」的骨架
- **新页只用 `var(--brand-*)` 和 `.f-*/.s-*` 工具类，绝不写死品牌 hex**，否则换肤会漏

## 文件地图
```
大厂ppt风格/
├─ SKILL.md                技能入口（本文件）
├─ index.html              放映/浏览器（键盘翻页 + 全屏）
├─ slides/                 17 种版式原型 + 样式表
│   ├─ theme.css           ★ 皮肤：品牌 token / 字体 / logo 文案（换肤只改这个）
│   └─ deck.css            骨架引擎：全部版式组件（引用 var(--brand-*)）
├─ themes/                 示例皮肤：meituan.css（默认）/ bilibili.css（B站粉）
├─ scripts/
│   ├─ build_pdf.py        → out/deck.pdf（矢量）
│   ├─ build_pptx.py       → out/deck.pptx（图片全铺）
│   └─ bundle_html.py      → 内联 CSS 的自包含 HTML（双击即用）
├─ standalone/             每页自包含 HTML（bundle_html.py 生成）
├─ reference/design-spec.md 设计规范细则
└─ out/                    导出产物（deck.pdf / deck.pptx / 美团样册-单文件.html）
```
> 换肤命令示例：`cp themes/bilibili.css slides/theme.css` 然后跑 `bundle_html.py` + 导出脚本。
```
