# Visual quality rubric

Use this rubric after pixel QA. Pixel QA proves that a card fits; this rubric decides whether it looks authored rather than templated.

## Scoring

Score each category from 0–10. A publish-ready card should score at least 8 in every category and at least 85/100 overall. A series should not be accepted merely because its average passes if one card has an unrelated asset or visibly broken composition.

Record the ten scores in the generated `*.visual-review.json`. Pixel QA and a visually approved review are separate gates. A pending, incomplete, sub-85, or individually sub-8 review is not deliverable.

| Category | 8–10 standard | Common failure |
|---|---|---|
| Semantic specificity | The cover promise is source-backed; every card claim and material is inseparable from the source | Attractive fragments replace the argument, or a generic bird, leaf, ticket, shell, or path could be swapped in unchanged |
| Material quality | Real or newly generated photo, cutout, relief, scan, or purposeful abstract mark has convincing texture | Programmatic placeholder presented as a bespoke illustration |
| Paper tactility | White at first glance; fibers become visible at close view without yellow cast | Flat digital white or dirty beige parchment |
| Composition | Image, text, connector, and accent form one focal event | “Text column + icon” placed as separate objects |
| Typography | Restrained hierarchy, deliberate wrapping, readable body, useful microtext | Default line wrapping, repeated labels, or poster headline scale |
| Image–text intersection | At least one intentional spatial relationship clarifies meaning | Image and copy merely sit side by side |
| Negative space | Quiet space creates tension and emphasis rather than emptiness | Everything sits in one predictable middle cluster |
| Series rhythm | Mechanism, scale, crop, and focal zone vary while the system remains coherent | Six near-identical cards with the same plant or icon |
| Mobile readability | A cover promise is understood in two seconds; interior core and support copy are readable at target preview size | Essential content survives only when zoomed or the cover communicates only a mood |
| Provenance and restraint | Metadata is verified; no decorative archival fiction | Invented dates, coordinates, ticket numbers, stamps, or routes |

## Hard gates

Reject the card or series when any gate fails:

1. A topic-bearing card uses a generic programmatic plant or path instead of a supplied or newly generated topic-specific asset.
2. A photograph, ticket, document, date, coordinate, place, or archival record lacks a real source basis.
3. Two assets perform the same decorative role.
4. Essential Chinese copy is embedded inside a generated image instead of typeset deterministically.
5. The paper is yellow, beige, stained, burned, heavily distressed, or visibly composed from multiple paper rectangles.
6. Two cards or variants are combined inside one exported canvas.
7. Adjacent cards repeat both the same layout family and the same focal zone.
8. A long source was styled without first extracting a cover promise and one exact claim per interior card.

## Asset ladder

Choose the highest viable tier:

1. User-owned or licensed source image that directly documents the claim.
2. Newly generated topic-specific text-free relief print, cutout, photograph, or material fragment.
3. Public-domain or licensed archival source with recorded provenance.
4. Purposeful abstract asset that explains structure: sequence, comparison, boundary, signal, or location.
5. Programmatic fallback. Use only for abstract structure and disclose it; never use it to impersonate a topic-specific illustration.

## Reference-level production loop

1. Write the exact claim for the card.
2. Write the asset's semantic role and reason before generating or sourcing it.
3. Generate or source the asset without text and without internal paper texture.
4. Reject the asset if the subject is wrong, generic, overly polished, or stylistically unrelated.
5. Compose exact Chinese copy with the deterministic renderer.
6. If text deliberately enters an asset region, declare the selected asset and opaque-overlap limit in `intentional_intersection`; never disable collision QA globally.
7. Inspect the target-size preview.
8. Score the card with this rubric.
9. Revise the lowest-scoring category first; do not compensate for an irrelevant image with stronger typography.
10. Run `scripts/run_pipeline.py --finalize ...`; delivery is allowed only when the visual-review validator passes.

## Route from 76 to 90+

The renderer alone cannot close the full gap. Prioritize work in this order:

1. Replace generic fallbacks with topic-specific generated or supplied assets. Expected gain: 6–8 points.
2. Add multiple real material treatments: monochrome photo, irregular cutout, rough relief, translucent color block, and verified document fragment. Expected gain: 3–5 points.
3. Make image and text form a shared event through controlled overlap, threading, connector lines, and interrupted baselines. Expected gain: 2–4 points.
4. Improve paper texture at full resolution while keeping the phone view white and quiet. Expected gain: 1–2 points.
5. Curate series rhythm manually after automated QA. Expected gain: 2–3 points.

Target interpretation:

- 76: clean and usable, but visibly template-led.
- 85: publish-ready editorial system with relevant assets and convincing material variety.
- 90+: consistently authored, topic-specific, visually nuanced, and difficult to confuse with a generic social template.
