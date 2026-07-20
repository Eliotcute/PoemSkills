# Whole Earth XHS Cards

把一段中文内容变成可以直接发布的诗性档案卡片，而不是一套换字复用的社交媒体模板。

## About

`whole-earth-xhs-cards` 是由[适之 Shizhi](https://github.com/Eliotcute)维护的本地 Codex Skill。项目从 *Whole Earth Catalog* 的独立出版气质、早期互联网的信息组织方式，以及用户提供的极简诗性档案卡片中提取视觉语法，再将它改造成适合中文手机阅读的确定性生产流程。

它关注的不是对某张参考图进行像素级复刻，而是建立一套可复用、可检查、可版本管理的编辑设计系统：

- 使用浅白色纤维纸张，而非黄色、米色或做旧羊皮纸；
- 以大面积留白、克制宋体层级和小型偏心焦点保持阅读节奏；
- 让文字与图片产生有意义的空间关系，而非简单套入左右模板；
- 默认一个视觉素材、最多两个，并要求每个素材直接解释本张卡片的具体论点；
- 将无文字素材生成、中文确定性排版、像素 QA 和人工视觉评分分开执行；
- 针对小红书、公众号、横版、竖版及自定义画布分别重新构图，不直接裁切母版。

这个仓库既包含 Codex 的执行说明，也包含渲染器、语义校验、像素 QA、50 组合回归测试和可复现的视觉基线。当前系统已经能够稳定生成独立 PNG，但主题专属配图和更复杂的材料层次仍是从“可发布”提升到“参考图级别”的主要工作。

> 这份 README 面向仓库使用者和维护者。Codex 运行时以 `SKILL.md` 与 `references/` 中的规范为准。

## 当前状态

- 功能可靠性：97/100
- 多尺寸适配：96/100
- 真实素材样张视觉评分：85.0–85.5/100
- 画布回归测试：50/50 通过
- 本地版本：`v0.3.0`

`v0.3.0` 不再把像素 QA 当作设计完成：渲染后必须检查完整图和手机预览，十项视觉评分每项至少 8 分、总分至少 85 分才能最终化。照片、木刻和剪影在最终模式中必须有真实素材文件；程序化植物、路径和模拟文档只能用于明确标记的草稿。

## 快速使用

首次测试新风格时，使用样张模式：

```text
使用 $whole-earth-xhs-cards。
先区分我提供的内容来源和视觉参考，然后制作两张独立的小红书 3:4 样张：
一张图片主导，一张文字主导，不要拼在同一张图里。

要求：
- balanced 模式
- 浅白纤维莎草纸
- 低饱和蓝点缀
- 使用我提供或新生成的主题素材，禁止占位图
- 运行像素 QA，检查手机预览并完成视觉评分

内容：
【粘贴内容】

视觉参考：
【上传参考图】
```

样张确认后再进入生产模式：

```text
使用 $whole-earth-xhs-cards，沿用刚确认的视觉合同，生产剩余 6 张卡片并最终化。
```

只需要可粘贴到 ChatGPT 的提示词时必须明确说明：

```text
使用 $whole-earth-xhs-cards，只输出可复用提示词，不生成图片文件。
```

## 支持规格

| 用途 | 尺寸 |
|---|---:|
| 小红书竖版 | 1242×1660 |
| 公众号主封面 | 900×383 |
| 公众号方形封面 | 500×500 |
| 公众号内文竖图 | 1080×1440 |
| 16:9 横版 | 1920×1080 |
| 9:16 竖版 | 1080×1920 |
| 1:1 方形 | 1080×1080 |
| 4:5 竖版 | 1080×1350 |
| 3:2 横版 | 1800×1200 |
| 自定义 | 明确宽高 |

不同尺寸会重新构图，不会直接裁切同一张母版。

## 生成流程

1. 区分内容来源与视觉参考。
2. 把参考图拆成纸张、留白、视觉群、文字轴、素材处理和失败禁区的空间合同。
3. 将原文拆成卡片序列，并为每张确定唯一核心论点。
4. 为素材填写语义角色与具体理由，最终模式要求真实文件路径。
5. 为每张图建立独立 JSON 规格。
6. 校验规格、系列节奏和素材数量。
7. 确定性排版中文并输出独立 PNG。
8. 检查安全区、文字碰撞、留白、对比度和手机预览。
9. 填写十项视觉评分，修改最低项。
10. 每项至少 8 分且总分至少 85 分后最终化。

如果设计要求文字进入透明剪影或版画的布局区域，必须在 JSON 中显式声明：

```json
{
  "intentional_intersection": {
    "mode": "transparent-only",
    "reason": "让短句穿过素材透明区域，连接图像与核心论点",
    "asset_indices": [0],
    "max_opaque_overlap": 0.0
  }
}
```

`transparent-only` 不允许文字压住不透明像素；`controlled-overlap` 可以设置小于等于 `0.20` 的保守上限。没有声明的相交仍会被 QA 拒绝。

渲染和像素 QA：

```bash
python3 scripts/run_pipeline.py card-01.json card-02.json card-03.json
```

检查图片并填写生成的 `*.visual-review.json` 后最终化：

```bash
python3 scripts/run_pipeline.py --finalize card-01.json card-02.json card-03.json
```

运行全部画布与版式回归测试：

```bash
python3 scripts/test_matrix.py
python3 scripts/test_intentional_intersection.py
python3 scripts/test_typography.py
python3 scripts/test_asset_gate.py
python3 scripts/test_visual_review.py
```

校验 Skill 结构：

```bash
python3 "${CODEX_HOME:-$HOME/.codex}/skills/.system/skill-creator/scripts/quick_validate.py" .
```

## 如何把视觉从 85 分提升到 90 分

### 1. 替换程序化占位素材

这是最重要的一步。最终模式已经禁止用程序化植物和路径承担主题内容；要继续提升，必须使用更准确、更有材料感的照片、木刻、剪影或真实档案。

优先级：

1. 用户拥有或授权的真实图片。
2. 新生成的主题专属无文字版画、剪影或照片。
3. 有来源记录的公共领域或授权档案素材。
4. 能明确解释顺序、比较、边界或信号的抽象图形。
5. 程序化兜底，仅用于抽象结构，并明确告知用户。

### 2. 建立真正的材料层次

参考图不是简单的“白底＋一个图标”。一张卡片通常需要形成一个材料事件，例如：

- 黑白照片与半透明色块交叠；
- 粗粝版画被中文基线穿过；
- 不规则剪影与细引线形成方向；
- 有来源的文档残片与事实说明建立证据关系。

每张最多仍然只使用两个素材。

### 3. 让图文相交，而不是并排

当前渲染器擅长安全、克制的双栏布局。要继续提高，需要增加受控的高级构图规则：

- 标题或短句穿过透明素材，但不影响阅读；
- 细线从具体图像部位连向解释文字；
- 图片打断一条文字基线；
- 同一信息在图像、色块和短注释之间形成三点关系。

不能通过随机重叠制造“设计感”。相交必须帮助理解内容。

### 4. 改善白色纸张质感

纸张仍应一眼看起来是白色。改进方向是增加近看可见的长短纤维、压制纹理和极轻微印刷不均，而不是变黄、加污渍或做旧。

### 5. 手工策划系列节奏

自动 QA 能发现越界和碰撞，但不能判断六张图是否像同一个设计师完成。完整系列应交替变化：

- 素材类型；
- 图片尺度；
- 焦点位置；
- 图文关系；
- 信息密度。

详细的 100 分制验收标准见 [`references/visual-quality-rubric.md`](references/visual-quality-rubric.md)。单张每项至少 8 分，整组至少 85 分，才算稳定达到发布级。历史 `v0.2` 的 76 分基线及逐项得分保留在 [`references/visual-baseline-v0.2.md`](references/visual-baseline-v0.2.md)。

## 核心约束

- 每张卡片独立输出，禁止双联、宫格和对比板。
- 默认一个素材，最多两个。
- 邮票、票据、日期、坐标、路线和档案编号只能在来源真实支持时出现。
- 不在图像模型中排长篇中文；中文由确定性渲染器排版。
- 不模仿或复制具体参考作品、Logo、页面和受版权保护插图。
- 纸张保持浅白，不使用黄色、米色、污渍、烧焦边或重度做旧。

## 仓库结构

```text
whole-earth-xhs-cards/
├── SKILL.md
├── README.md
├── agents/openai.yaml
├── assets/
├── references/
└── scripts/
```

- `SKILL.md`：Codex 的核心执行流程。
- `references/style-system.md`：视觉系统。
- `references/visual-quality-rubric.md`：人工视觉验收标准。
- `references/illustration-prompts.md`：无文字配图提示词。
- `scripts/render_card.py`：确定性 PNG 渲染器。
- `scripts/qa_card.py`：像素和版面 QA。
- `scripts/validate_visual_review.py`：85 分视觉交付门禁。
- `scripts/test_matrix.py`：50 组合回归测试。
- `scripts/test_intentional_intersection.py`：受控相交正反回归测试。
- `scripts/test_typography.py`：中英文换行与中文微文字测试。
- `scripts/test_asset_gate.py`：最终素材路径门槛测试。
- `scripts/test_visual_review.py`：视觉评分门禁测试。

## 本地 Git

查看状态与历史：

```bash
git status
git log --oneline --decorate
```

提交修改：

```bash
git add .
git commit -m "feat: describe the change"
```

发布新的本地版本：

```bash
git tag -a vX.Y.Z -m "Describe this local release"
```
