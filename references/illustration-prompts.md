# Relief-print illustration prompts

Use these prompts to generate the image asset only. Typeset all Chinese text afterward.

## Asset brief before prompting

Write these fields before calling an image model:

- exact claim the asset must explain;
- central subject and required supporting forms;
- semantic role;
- intended crop: compact marginal cut, horizontal specimen, vertical branch, or central emblem;
- desired occupied area in the final card;
- one-color material treatment;
- removable background requirement;
- topic-specific objects that must be present;
- generic or decorative objects that must not appear.

Do not generate until the asset would fail the “random lighthouse” test: replacing it with an unrelated vintage object must materially weaken the claim.

## Master prompt — English

```text
A single-color black relief-print illustration of [CENTRAL SUBJECT], surrounded and partially interwoven with [SURROUNDING PLANTS / OBJECTS / SYMBOLS RELEVANT TO THE TOPIC]. Hand-carved folk woodcut and crude small-press linocut appearance. Thick irregular black outlines, visibly wobbly contours, blunt V-shaped carved hatch marks, repetitive leaf-vein or texture cuts, uneven ink coverage, clogged black patches, dry-print gaps, tiny white chips and broken edges inside the black shapes. Flat frontal or side-on silhouette, naive but immediately readable anatomy, almost no perspective and no modeled shading. Dense organic composition around one clear central figure. Generate an isolated asset on a transparent background. If transparency is unavailable, use a completely flat uniform #FAFAF7 background with no fiber, shadow, edge, frame, or paper texture so it can be cleanly removed. Raw handmade illustration presented with elegant restraint. Image only, no text, no letters, no numbers, no caption, no border, no logo, no signature, no watermark, no color.

Negative prompt: fine Victorian engraving, delicate botanical etching, hair-thin crosshatching, accurate scientific plate, smooth vector line art, clean digital inking, tattoo flash, Art Nouveau, ukiyo-e, Chinese ink wash, watercolor, storybook illustration, kawaii, photorealism, glossy 3D, polished rendering, cinematic lighting, gradients, drop shadows, sepia wash, colored ink, typography, labels, poster layout, yellow paper, cream paper, beige paper, brown paper, antique parchment, dirty newsprint, stains, foxing, mold, burn marks, dark vignette, torn edges, excessive grain.
```

## 中文版

```text
生成一幅单色纯黑的凸版印刷插图：主体是【中心主体】，四周由【与主题有关的植物／器物／象征元素】密集包围并与主体交错。采用粗粝的小型出版社民间木刻或油毡版画质感，不是精致古典铜版画。

必须具有：粗而不均匀的黑色外轮廓；肉眼可见的手工抖动；短促、笨拙、重复的刻刀排线；大片堵墨的黑块；干印造成的断线和白色缺口；边缘带有小碎屑；造型扁平；几乎没有透视和明暗塑造；解剖或结构可以朴拙，但主体必须一眼可辨。只使用炭黑油墨和纸张本色。

只生成独立插图素材，背景透明。若模型不能生成透明背景，则使用完全均匀的 #FAFAF7 浅白底，不要在素材内部生成纸张纤维、阴影、边缘、边框或局部纸片。最终莎草纸纹理应在整张卡片合成阶段统一添加，避免素材周围出现矩形色差。

只生成插图，不要文字、字母、数字、标签、边框、标志、签名和水印，不要任何彩色。

排除：维多利亚精细雕版、纤细植物铜版画、发丝般精确排线、科学教材写实、光滑矢量线稿、干净数字描边、纹身图案、新艺术风格、浮世绘、中国水墨、水彩、儿童绘本、可爱卡通、照片写实、精致医学 3D、电影光影、渐变、投影、棕褐色滤镜、彩色油墨、完整海报排版、黄纸、米色纸、棕色纸、羊皮纸、旧报纸、污渍、霉斑、虫斑、烧焦边、暗角、破损边缘和浓重颗粒。
```

## Composition controls

Append one of these only when needed:

- `central emblem`: one centered subject, plants radiating outward, roughly symmetrical but visibly handmade.
- `vertical branch`: a tall branch or vessel runs from bottom to top, with the subject perched or attached at the center.
- `horizontal specimen`: one long object or organ with dense leaves/tools above and below, suitable for a wide crop.
- `small marginal cut`: compact isolated icon with an irregular edge and at least 35% empty paper around it.

If the result looks too elegant, add: `coarser carving, fewer but thicker cuts, cheaper reproduction, more broken ink edges, less anatomical precision, no fine engraving detail`.

## Rejection checklist

Reject and regenerate when any answer is yes:

1. Could the image illustrate an unrelated topic unchanged?
2. Is the subject rendered as a smooth icon, polished vector, fine engraving, cute drawing, or 3D object?
3. Does it contain words, letters, numbers, UI labels, logos, signatures, or watermarks?
4. Does it contain yellow, beige, dirty, torn, shadowed, or textured paper inside the asset rectangle?
5. Are there extra props that do not explain the exact card claim?
6. Is the silhouette unreadable at the intended 14%–28% card size?

Only save accepted assets into the project. Record the final prompt and source path next to the card specification.
