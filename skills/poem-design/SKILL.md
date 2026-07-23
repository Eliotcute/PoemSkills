---
name: poem-design
description: "Design PoemSkills card layouts, reference contracts, semantic assets, text-free illustration prompts, and render-ready CardSpecs from approved content and titles. Use for PoemSkills 视觉参考、卡片版式、配图提示词、白色纤维纸、诗性极简编辑设计 or explicit $poem-design requests. Do not use for generic product design."
---

# Poem Design 卡片设计

Compile approved copy into a visual system and render-ready card specifications. Do not rewrite claims to fit a layout.

## Required inputs

For planning-only work, accept upstream artifacts marked `status: provisional` and return a provisional DesignPlan. For production, require a validated `ContentPlan` and, for a cover, a validated `TitlePlan`. If the required upstream state is missing, route back before compiling CardSpecs.

Read completely when relevant:

- `../../references/style-system.md` for visual rules and layout families;
- `../../references/canvas-presets.md` for dimensions;
- `../../references/illustration-prompts.md` when an illustration is necessary;
- `../../references/stage-contracts.md` for upstream binding.

When the user requests one reusable copy-paste prompt for standalone ChatGPT, read `../../references/master-prompt.md` and return one tailored fenced prompt immediately. Do not build a DesignPlan or CardSpec for that route. Treat it as a compatibility deliverable, not as the internal multi-Skill workflow.

## Build the reference contract

Translate references into measurable decisions:

- paper and material treatment;
- quiet-space and focal-cluster ratios;
- title/body scale and line length;
- image crop, scale, and position;
- image-text relationship;
- index, rule, source, and accent placement;
- visible failure modes.

Never copy a reference's objects, labels, metadata, or imagery unless they are also authorized content assets.

## Select layouts by card role

Do not reuse one skeleton across the series. Choose among:

- image above, text below;
- text above, image below;
- side-by-side intersection;
- text-led editorial note;
- evidence image with edge annotations;
- source/index closing card.

Vary both focal zone and mechanism on adjacent cards. Preserve one paper, type, accent, and print language across the set.

## Enforce the asset gate

Default to one asset, maximum two. For every asset record:

- `semantic_role`;
- the exact claim it supports;
- `semantic_reason`;
- source basis or generated asset path.

Reject any asset that could be replaced by a random bird, plant, path, stamp, ticket, interface icon, or archive prop without changing meaning. Generate topical assets without text; exact Chinese belongs in deterministic composition.

## Deliver a DesignPlan first

When the user asks for alternatives, return a `poem-design-plan/v1` with `status: provisional`, two or three genuinely different variants, and `production_ready: false`. Do not create multiple render-ready CardSpec sets before one direction is selected.

For every variant, list `allowed_layouts` using only renderable CardSpec layouts: `image-above`, `text-above`, `archive-collage`, `quiet-specimen`, `relief-emblem`, `silhouette-field`, or `text-led-note`.

When one direction is already clear, select it explicitly and set `production_ready: true`. In production, validate the file-backed DesignPlan against ContentPlan and TitlePlan before compiling specs.

## Compile CardSpecs

For card-specific prompt requests, return one numbered block per requested card after the DesignPlan is selected. Each block contains its own text-free asset prompt when an image is justified, plus one exact composition prompt with that card's copy, line breaks, layout, and dimensions. A pure-text card receives only its composition prompt. Never use one plural prompt to request a whole set or multiple variants in one canvas. For production, create one CardSpec JSON per independent output using `../../assets/example-card.json`.

New CardSpecs should include:

```json
{
  "contract": "poem-card-spec/v1",
  "status": "validated",
  "content_plan_ref": "content-plan.json",
  "content_plan_digest": "sha256...",
  "title_plan_ref": "title-plan.json",
  "title_plan_digest": "sha256...",
  "design_plan_ref": "design-plan.json",
  "design_plan_digest": "sha256...",
  "design_variant_id": "selected-variant-id"
}
```

Keep all existing v0.6 content/rendering fields. Validate each new spec with `scripts/validate_card_spec.py`; legacy specs require the explicit `--legacy-v0.6` flag. Route approved specs to `$poem-render`.
