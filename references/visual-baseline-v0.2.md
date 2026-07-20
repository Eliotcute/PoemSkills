# Visual baseline — v0.2.0

This file makes the reported 76/100 visual score reproducible. Re-score after meaningful changes to assets, paper, typography, composition, or series rhythm; never overwrite this historical baseline.

## Evaluation identity

- Skill version: `v0.2.0`
- Commit: `023190e1908916d3a2648be107782ebb76f3b5c0` for the documentation release; the evaluated renderer behavior is the renderer contained by that tagged commit.
- Evaluation date: `2026-07-20`
- Canvas: Xiaohongshu portrait, 1242×1660
- Evaluated artifacts: `assets/e2e/card-01.png` through `card-05.png`
- Phone previews: `assets/e2e/card-01-preview.png` through `card-05-preview.png`
- Reference direction: the four user-supplied pale-paper poetic archival cards discussed during this project; they are not copied into the repository because they are third-party reference works.
- Evaluation method: one series-level score using `references/visual-quality-rubric.md`, supported by per-card preview inspection.

## Score breakdown

| Category | Score | Evidence and deduction |
|---|---:|---|
| Semantic specificity | 8 | Subjects correspond to the claims, but several plant/path metaphors remain interchangeable with unrelated self-improvement topics. |
| Material quality | 5 | Most assets are renderer-generated marks rather than convincing photographs, cutouts, scans, or topic-specific relief prints. |
| Paper tactility | 7 | Paper is clean and pale, but fiber and pressed-pulp texture are barely visible in the phone previews. |
| Composition | 7 | Layout is stable and restrained, but most cards still read as a text block plus a separate icon. |
| Typography | 8 | Chinese copy remains readable and hierarchy is controlled; microtext sometimes behaves like repeated template labeling. |
| Image–text intersection | 5 | Connectors exist on some cards, but true controlled intersection and threading are largely absent. |
| Negative space | 9 | The series maintains confident quiet space without filling the canvas unnecessarily. |
| Series rhythm | 8 | Focal zones and layout families vary coherently, although repeated black plant language still reduces material rhythm. |
| Mobile readability | 9 | Core and support copy remain readable in 375×500 previews. |
| Provenance and restraint | 10 | No invented archival dates, coordinates, routes, tickets, or document numbers appear. |
| **Total** | **76/100** | Raw rubric total. |

## Reported baseline

The explicit rubric total and the reported project baseline are both `76/100`. Future comparisons must preserve the same categories and reference set, or clearly state why the comparison is not like-for-like.

## Primary blockers to 85+

1. Replace the generic programmatic plant and path marks with topic-specific generated or supplied materials.
2. Add convincing material variety across the series: photograph, irregular cutout, rough relief, restrained color field, or verified document fragment.
3. Introduce declared, controlled image–text intersections that remain readable and pass opaque-pixel QA.
4. Strengthen full-resolution white-paper fibers without introducing beige or distress.
5. Replace repeated English labels with content-specific annotations or remove them.

## Re-evaluation protocol

1. Render the same five JSON specifications at the recorded canvas.
2. Inspect all five 375×500 previews and at least two full-resolution exports.
3. Score every rubric category from 0–10 with one written evidence sentence.
4. Record the evaluated commit, date, artifacts, raw total, and rounded headline score in a new immutable baseline file.
5. Do not claim improvement when the assets or reference set changed without stating that the comparison is not like-for-like.
