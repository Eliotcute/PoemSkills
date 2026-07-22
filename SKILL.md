---
name: poemskills
description: "Turn long Chinese source text into content-first Xiaohongshu covers and explanatory editorial card series with a poetic archival print language, then compose publish-ready visuals for Xiaohongshu, WeChat, landscape, portrait, and custom canvases. Use for PoemSkills、诗歌 Skills、长文提炼、封面文案、文字卡片、配图提示词、全球概览、Whole Earth Catalog、浅白纤维莎草纸、古典互联网、诗性档案、极简独立出版物、参考图匹配 or high-end editorial collage. This is an editorial card skill, not a generic poetry-writing skill. Supports reusable prompts, content plans, one-cover production, explicit style comparisons, topic-specific assets, deterministic Chinese typography, phone preview QA, and a mandatory visual-review gate."
---

# PoemSkills Editorial Cards

Create an original editorial system, not a facsimile of a copyrighted page. Never reuse a reference logo, page scan, photograph, ticket, or illustration unless the user supplied it and authorized reuse.

## Route the deliverable

Choose exactly one mode before working:

1. `prompt-only`: Use when the user asks for a reusable ChatGPT/image prompt. Fill `references/master-prompt.md`; deliver one copy-paste prompt plus any source-specific interpretation requested. Do not render files.
2. `content-plan`: Use when the user supplies long text and asks what the cover or carousel should say, but does not ask for image files. Deliver the editorial brief, cover copy, card script, and asset concepts.
3. `cover-production`: Use when the user asks for a cover or cover illustration. Produce the requested number of independent covers; default to one, never two.
4. `style-sample`: Use only when the user explicitly asks to compare styles, test the Skill, or requests two samples. Produce the requested independent variants and never combine them in one canvas.
5. `series-production`: Use when the user asks for a complete card set or approves the content and visual system. Produce the requested full set.

A supplied reference image controls appearance only. It does not imply `style-sample`, authorize its contents, or change the requested output count.

Do not answer a file-generation request with only strategy, prompts, or JSON.

## Pass the content gate first

When the source is a long passage, an article, a transcript, or a screenshot containing substantial copy, read `references/content-first-workflow.md` before designing. Do not begin with layout selection.

Extract and verify:

- the topic in one sentence;
- the central change, tension, or question;
- the reader payoff;
- the strongest source-backed evidence or example;
- one cover promise;
- one exact claim per interior card;
- facts, names, dates, and claims that must not be invented.

The cover is a promise, not a summary. Interior cards explain that promise. Do not paste the source into a sparse layout, turn every paragraph into poetic fragments, or let aesthetics replace the argument.

For a direct generation request, complete the editorial brief internally and proceed. Otherwise show the brief, cover copy, and card script before generating visuals.

## Build a reference contract

When the user supplies visual references, inspect them before choosing a layout. Separate content sources from style references. Record a concise reference contract containing:

- paper color and tactile treatment;
- approximate quiet-space and focal-cluster ratios;
- image crop, scale, and material treatment;
- title/body scale, line length, and alignment axes;
- positions of image, copy, rules, indices, and accent marks;
- the image-text relationship to preserve;
- visible failure modes to reject.

Do not reduce a reference to adjectives such as “高级、极简、复古.” Translate it into spatial decisions. If the bundled renderer cannot express the contract, use or create a deterministic compositor that can; do not force the request through a mismatched template.

Read `references/style-system.md` and `references/canvas-presets.md` before composing. Read `references/visual-quality-rubric.md` before reviewing or delivering.

For the user's current reference family, distinguish two reusable systems:

- `editorial-explanation`: readable cover or interior copy, one small relevant photo or no image, distant indices, thin rules, and muted blue marks;
- `printed-symbol`: one rough low-saturation color block containing a topic-specific cutout or negative-space symbol, two or three truthful annotations, and one short Chinese line.

Never reuse the reference bird, seascape, ticket, coordinates, dates, or English labels unless the source content independently supports them.

## Plan the cover and series

1. Parse topic, audience, goal, platform, canvas, card count, content priority, available source assets, illustration preference, accent, and CTA.
2. Ask at most three questions only when missing choices materially change the result. Defaults for direct requests: simplified Chinese, `balanced`, the named platform preset, clean pale-white fibrous paper, black ink, and one muted blue accent.
3. Write three cover lines from different content angles, select the strongest, and explain the selection in one sentence. Keep cover text source-faithful rather than clickbait.
4. Give every interior card one exact claim. Order claims so the reader can follow the argument without the original source.
5. Alternate image-led, text-led, material-led, relief-led, diagram-led, and source/recap mechanisms without repeating both layout and focal zone on adjacent cards.
6. Default to one visual asset. Use a second only when it performs a separate necessary role.

For Xiaohongshu:

- cover headline: normally 8–18 Chinese characters, two to four short lines;
- optional cover subtitle: 12–28 Chinese characters;
- interior core sentence: 12–28 Chinese characters;
- interior explanation: normally 35–90 Chinese characters in one to three blocks;
- default series when the user asks for a set without a count: one cover plus five interior cards.

Use these density rules:

- `aesthetic`: 12–36 essential Chinese characters, with optional nonessential microtext.
- `readable`: a short title plus 70–140 Chinese characters in 2–4 spatial blocks.
- `balanced`: a 12–28-character core statement plus 40–90 supporting characters.

## Enforce the asset gate

For every asset, write `semantic_role` and a concrete `semantic_reason`. Allowed roles are `explain`, `document`, `locate`, `sequence`, `compare`, and `symbolize-specific-idea`.

Final mode rules:

- `mono-photo`, `relief-print`, `silhouette`, `ticket`, and `document` require a real supplied, generated, licensed, or public-domain file path.
- Tickets and documents also require a truthful `source_basis`.
- Generic plants, birds, paths, stamps, coordinates, dates, and archival props may not stand in for a topic-specific image.
- Programmatic plants, paths, and mock documents are allowed only with `"render_mode": "draft"`; they are never final deliverables.
- A restrained `color-block` may be generated programmatically because it is structural, not topical.

When an illustration is needed, read `references/illustration-prompts.md`. Generate only a text-free source asset. Inspect it for subject accuracy, rough material quality, unwanted text, logos, watermarks, extra objects, dirty paper, and style drift before composition. If image generation is unavailable, ask for a source asset or deliver the asset prompt; do not pretend a placeholder is a finished illustration.

## Write card specifications

Write one UTF-8 JSON spec per PNG using `assets/example-card.json`. Required fields are `canvas_preset`, `width`, `height`, `priority`, `layout`, `cluster_zone`, `title`, `body`, and `output`.

Use `"render_mode": "final"` for deliverables and `"render_mode": "draft"` only for explicit layout tests. Preserve deliberate line breaks in title and body. Use no more than two assets.

Mark each specification as `cover` or `interior`. A cover must pass the thumbnail test: at 375 px wide, its promise is understood in two seconds. An interior card must remain useful after the cover is removed.

If essential text deliberately enters an asset region, add `intentional_intersection` with `mode`, `reason`, `asset_indices`, and a conservative `max_opaque_overlap`. Never disable collision QA globally.

## Render and review

Run the rendering stage:

```bash
python3 scripts/run_pipeline.py card-01.json card-02.json
```

This stage validates specs, validates series rhythm, renders independent PNGs, runs pixel QA, creates phone previews, and writes a pending `*.visual-review.json`. It does not make the files deliverable.

Inspect every full-size PNG and phone preview. Fill all ten scores in the visual-review file using `references/visual-quality-rubric.md`. State the weakest category and what was revised. Revise the weakest category first.

Finalization requires every category to score at least 8, the total to reach at least 85, and `approved` to be true:

```bash
python3 scripts/run_pipeline.py --finalize card-01.json card-02.json
```

Do not deliver a card merely because pixel QA passed. Reject broken Latin wrapping, missing Chinese glyphs, generic assets, flat template composition, unrelated archival decoration, weak phone readability, and reference mismatch.

After changing the renderer or canvas behavior, run:

```bash
python3 scripts/test_matrix.py
python3 scripts/test_intentional_intersection.py
python3 scripts/test_typography.py
python3 scripts/test_asset_gate.py
python3 scripts/test_visual_review.py
```

## Deliver

- Export every card or variant as an independent image at the requested ratio.
- Never combine samples, variants, or cards in a diptych, grid, contact sheet, or comparison board.
- For Xiaohongshu, also deliver title options, caption, and hashtags.
- For prompt-only and content-plan modes, deliver the editorial brief, selected cover line, the exact script for the requested output scope, asset rationale, text-free asset prompt, and final composition prompt. Do not invent interior cards when the user requests only a cover.
- For WeChat, deliver article title, summary, and alt text.
- For story/video formats, deliver title, safe-zone copy, and description.
- Report source paths, generated asset prompts, final PNG paths, previews, QA results, and visual-review scores.

Use clean white fibrous paper, restrained Song/Ming typography, truthful metadata, one muted accent at most, and topic-specific material. Detailed visual rules live in `references/style-system.md`; do not duplicate them here.
