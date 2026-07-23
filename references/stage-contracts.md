# PoemSkills stage contracts

Use versioned artifacts when work crosses specialist boundaries. Human-readable replies may summarize them, but production stages should consume artifacts rather than reconstruct state from conversation memory.

## Pipeline

```text
ContentPlan -> TitlePlan -> DesignPlan -> CardSpec[] -> ArtifactManifest -> ReviewReport
```

Use two artifact states:

- `provisional`: may exist inline in a planning-only conversation, may omit file digests, and must never enter render;
- `validated`: file-backed, schema-checked, and bound to exact upstream SHA-256 digests.

A downstream validated artifact with a stale or missing required digest must be regenerated.

Every file-backed stage artifact requires `status: validated`. The validator rejects `status: provisional`; provisional artifacts stay inline and cannot enter production. Every downstream validation must receive its real upstream files through `--upstream`; a digest-shaped string without those files is not a valid binding.

## ContentPlan

Contract: `poem-content-plan/v1`

Required fields:

- `output_scope`: `cover-only`, `cover-plus-interiors`, or `interiors-only`
- `source_ref`
- `source_digest` for validated artifacts
- `topic`
- `reader_tension`
- `reader_payoff`
- `strongest_evidence`
- `boundaries`
- `desired_action`
- `cover_direction`
- `cards`

Each interior card requires `card_id`, `role`, `claim`, `source_excerpt`, `body`, `reason_to_exist`, `image_need`, and `image_role`. `cover-only` uses an empty `cards` list; other scopes require at least one interior card.

## TitlePlan

Contract: `poem-title-plan/v1`

Required fields:

- `content_plan_digest` for validated artifacts
- `cover_candidates`
- `selected_cover`
- `publishing_titles`
- `selected_publishing_title`
- `publication_package`

`selected_cover` requires `title`, `lines`, `subtitle`, and `selection_reason`. `publication_package` requires `xiaohongshu.title`, `xiaohongshu.body`, non-empty `xiaohongshu.tags`, `wechat.title`, `wechat.summary`, and `alt_text`. Its Xiaohongshu title must match `selected_publishing_title`.

## DesignPlan

Contract: `poem-design-plan/v1`

Required fields:

- `content_plan_digest` for validated artifacts;
- `title_plan_digest` when the output includes a cover;
- `canvas`;
- `reference_contract`;
- `variants`;
- `selected_variant`;
- `production_ready`;
- `card_specs`.

Each variant requires `variant_id`, `name`, `layout_family`, `allowed_layouts`, `asset_strategy`, `composition`, and `why`. `allowed_layouts` may contain only renderable CardSpec layouts. Multiple unresolved variants require `production_ready: false` and an empty `card_specs` list. Only a selected production-ready DesignPlan may compile CardSpecs.

## CardSpec

Contract: `poem-card-spec/v1`

Keep the existing v0.6 content and rendering fields. New production specs add `status: validated`, `content_plan_ref`, `content_plan_digest`, `design_plan_ref`, `design_plan_digest`, `design_variant_id`, and, for covers, `title_plan_ref` plus `title_plan_digest`. The CardSpec file must appear in the DesignPlan's `card_specs`, use its selected variant, and choose one of that variant's allowed layouts. Legacy v0.6 specs remain available only through the explicit `--legacy-v0.6` adapter.

## ArtifactManifest

Contract: `poem-artifact-manifest/v1`

Required fields:

- `card_specs_digest`
- `outputs`

Each output requires `spec`, `image`, `preview`, `qa`, `layout`, and `visual_review`, plus `qa_sha256`, `layout_sha256`, and `visual_review_sha256`. All paths must exist. The three evidence hashes must match the current files. Pixel QA must report `valid: true`, and its spec, image, preview, and layout hashes must also match the current files. `run_pipeline.py` writes this artifact to `artifact-manifest.json` by default.

## ReviewReport

Contract: `poem-review-report/v1`

Required fields:

- `artifact_manifest_digest`
- `approved`
- `deliverable`
- `scores`
- `lowest_category`
- `revision_summary`
- `remaining_risk`

`scores` contains exactly the ten visual-review categories. For a series, each category records the lowest score among all bound cards, so one weak card cannot be hidden by an average. `lowest_category` must name an actual minimum. `revision_summary` and `remaining_risk` must be explicit.

`approved` and `deliverable` may be true only after the bound ArtifactManifest is finalized and deliverable, current pixel QA passes, every evidence path exists, every visual review passes the full scoring gate against current image hashes, and ReviewReport scores match those bound reviews.

## Digest validation

Use:

```bash
python3 scripts/validate_stage_artifact.py content-plan.json --source source.txt
python3 scripts/validate_stage_artifact.py title-plan.json --upstream content-plan.json
python3 scripts/validate_stage_artifact.py design-plan.json --upstream content-plan.json title-plan.json
python3 scripts/validate_stage_artifact.py artifact-manifest.json --upstream card-01.json card-02.json
python3 scripts/validate_stage_artifact.py review-report.json --upstream artifact-manifest.json
```
