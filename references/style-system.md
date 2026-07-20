# Whole Earth–inspired card system

## Visual thesis

Treat every card as a sparse poetic archive sheet: a small event of image and language floating on tactile pale-white paper. The visual authority comes from restraint, distance, imperfect print matter, and editorial placement—not information density.

## Source observations

The June 1975 catalog supplies the editorial grammar: narrow multi-column text; asymmetric modules; abrupt changes in headline scale; black-and-white photographs, relief prints, diagrams, maps, product cuts, and captions; thin rules; page numbers; and small editorial labels. Adapt that grammar to the user's cleaner material direction: pure-white papyrus instead of yellowed catalog stock.

## Palette

- Paper: `#FAFAF7` or `#FFFFFF`
- Fiber: `#E7E5DE`
- Ink: `#11110F`
- Secondary ink: `#565650`
- Brick accent: `#8A3B2B`
- Olive accent: `#667044`
- Faded blue accent: `#3D6270`

Use one accent only. Keep color coverage below 5% of the page.

## Paper

The substrate must read as pure white immediately. Build it from a white base with exceptionally subtle cool ivory-gray fibers, sparse cross-woven papyrus strands, and delicate pressed-pulp embossing visible only on close inspection. Keep texture contrast under roughly 4%; preserve large clean white areas and airy negative space. Do not darken the edges. Do not add yellow cast, beige wash, sepia, stains, foxing, dirt, ink specks, burned edges, tears, rolled-scroll effects, or legibility-reducing grunge. “Papyrus” describes the tactile fibers, not an antique color treatment.

## Typography

- Main Chinese title: Song/Ming-style serif or a robust CJK serif when available; otherwise use a heavy CJK system face.
- Body Chinese: readable serif or humanist sans; never use tiny faux-newspaper type below mobile-reading size.
- Latin metadata: Georgia/Times-style serif or condensed sans in uppercase with generous tracking.
- Keep hierarchy restrained. Use the exact mobile-readable ranges in “Text and phone readability” below; do not create poster-scale headlines.

## Priority modes

### `aesthetic`

Keep the composition extremely sparse. The core statement must still be readable on a phone, but supporting text may behave as faint archival residue. Use 82%–90% quiet space and a 10%–18% focal cluster.

### `readable`

Preserve the style while increasing the core text to clear phone-reading scale. Divide copy into short blocks around the image instead of creating a large article column. Use 65%–78% quiet space and a 20%–32% focal cluster.

### `balanced`

Use one clearly readable central sentence plus smaller supporting fragments. Use 72%–85% quiet space and a 15%–26% focal cluster. Default to this mode.

## Reference contract

When matching a supplied reference, convert visible decisions into a short contract before writing card specs. Record:

1. `quiet_space`: estimated empty-paper percentage;
2. `focal_box`: left/center/right, upper/middle/lower, and approximate width/height percentages;
3. `copy_box`: position, width, title line count, body line count, and alignment axis;
4. `material`: photo, cutout, relief, document, or text-only;
5. `relationship`: edge alignment, overlap, threading, connector, interrupted baseline, or deliberate separation;
6. `micro_system`: indices, true source notes, fine rules, and accent position;
7. `reject`: the three most visible ways a result could drift from the reference.

Adjectives are not a reference contract. “高级、极简、复古、有呼吸感” must be translated into measurable placement and scale decisions.

For the quiet two-page editorial direction supplied by the user, use these production recipes:

- `image-led editorial`: one topic-specific monochrome asset occupies roughly 38%–48% of width and 28%–40% of height, usually in the middle/lower left or right. Place a restrained title and 3–5 short support lines along one image edge. Keep the opposite upper quadrant nearly empty. Use one thin rule and 1–3 small indices.
- `text-led editorial`: a 48%–60%-wide copy group floats around 28%–48% of canvas height. Use a two-line core statement and two separated supporting fragments. A tiny asset is optional, never required. Put indices in distant corners and use one small slash or dot to tension the empty field.
- `material collage`: use a real monochrome photo plus one verified document fragment only when both belong to the same evidence chain. Let one overlap the other; do not arrange them as two equal cards.

These recipes are independent outputs, never two pages placed side by side in one exported image.

## Layout families

### `archive-collage`

Combine one monochrome photograph with one document fragment or small color block only when both refer to the same subject, place, event, process, or evidence chain. A ticket is valid only for actual travel/transport/time/provenance content. Overlap them slightly. Place the cluster off-center around 45%–65% of the page height. Scatter 2–4 short text fragments nearby. Never use a scrapbook pile or generic vintage ephemera.

### `quiet-specimen`

Place one small object, shell, organ sketch, plant fragment, or archival artifact close to a horizontal or vertical axis. Let a single line of Chinese text pass behind, in front of, or beside it. Add at most one secondary asset. Suitable for calm explanatory cards.

### `relief-emblem`

Use one rough black relief-print subject as the primary asset, either alone or paired with one restrained color block. Keep the relief print between 14% and 28% of the canvas; do not let it become a full-page illustration. Use 1–3 fine connector lines and compact labels.

### `silhouette-field`

Use one black silhouette or cutout paired with one translucent photograph, cloud-like shape, or muted color mark. Build a small constellation of dates, dots, plus signs, and short words around it. Avoid centered symmetry.

### `text-led-note`

Make one readable Chinese proposition the main event without turning it into a big headline. Pair it with one small image or material fragment. Break supporting copy into 2–3 distant annotations. Maintain generous negative space.

## Image language

Use the supplied bird-among-leaves reference as the image-language anchor.

The target is a cheap, tactile relief-print reproduction:

- One-color black ink only; the paper supplies every light tone.
- Thick, irregular outer contours that visibly wobble like a hand-cut block.
- Short, blunt, repetitive carved marks inside feathers, leaves, organs, tools, or objects.
- Uneven blacks: clogged ink in some areas, dry gaps and white chips in others.
- Flat silhouette and weak perspective; the subject reads immediately from a distance.
- Naive but confident anatomy. Do not polish the drawing into a museum-grade natural-history plate.
- Dense organic framing is welcome: leaves, roots, vessels, tools, wires, stars, or other topic-relevant forms may grow around and through the central subject.
- Print it on pristine pure-white papyrus paper. The black ink may retain handmade relief-print imperfections, but the paper remains clean, luminous, and elegant.
- Keep the illustration free of embedded words so Chinese text can be typeset separately.

The drawing is closer to folk woodcut, linocut, and rubber-stamp relief printing than to a fine engraving. Preserve rough carved marks while presenting them on a refined white substrate with generous negative space. Use hard rectangular crops or irregular hand-cut silhouettes.

Reject these common failure modes: precise scientific engraving, hair-thin crosshatching, polished vector icons, smooth digital ink, tattoo flash, Art Nouveau poster work, Chinese ink painting, watercolor, sepia photography, photorealistic organs, kawaii drawing, and generic “vintage botanical” clip art.

## Text and display readability

- Use `references/canvas-presets.md`. Size values below are calibrated for a 1242 px-wide Xiaohongshu export; scale proportionally for other canvases and validate at the target display size.
- Essential Chinese core sentence at 1242 px width: normally 48–72 px in `balanced`, 52–80 px in `readable`, and never below 44 px in `aesthetic`.
- Supporting Chinese: normally 34–46 px. Keep line length around 12–20 Chinese characters.
- Microtext: 20–27 px, typewriter/monospace appearance, but never place facts the reader must understand only in microtext.
- Downsample every export to a 375×500 px phone preview. The core sentence must remain comfortably readable without zooming; supporting text must remain decipherable; only atmospheric microtext may become difficult to read.
- Keep essential text contrast at least 4.5:1 against the paper. Do not use low-opacity gray for essential facts, actions, disclaimers, or source names.
- Avoid conventional large cover titles. Let scale changes remain subtle: roughly 1.3×–1.8× rather than 3×–5×.
- Use short, spatial fragments. Do not set 150 characters as a continuous block.

## Asset limit

Use at most two of these on one card: monochrome photo, ticket/document, relief print, silhouette, color block. A photograph clipped into two overlapping rectangles still counts as one asset if it is the same source. Typography, connector lines, dots, dates, and index marks do not count.

## Semantic asset gate

Default to one asset. Before accepting any asset, answer:

1. What exact sentence or fact on this card does the asset clarify, symbolize, document, or organize?
2. Would replacing it with a random lighthouse, bird, ticket, shell, or stamp preserve the meaning? If yes, the asset is generic and must be rejected.
3. Is the depicted place, date, coordinate, number, route, ticket, or document present in the source material? If not, do not invent it.
4. Does the second asset add a new necessary role rather than merely making the card look richer? If not, remove it.

Allowed roles: `explain`, `document`, `locate`, `sequence`, `compare`, or `symbolize-specific-idea`. “Create atmosphere” alone is not enough.

## Series rhythm

Keep paper, typography, microtext treatment, and one accent family stable. Alternate the dominant mechanism: collage → text-led → relief emblem → readable note → silhouette field → quiet source card. Do not repeat the same cluster position on adjacent cards.

## Copy rhythm

Use editorial labels such as `FIELD NOTE`, `TOOL`, `SIGNAL`, `CHECK`, `SOURCE`, `INDEX`, paired with Chinese section names. Use specific assertions and visible hierarchy. Limit exclamation marks to zero or one across the entire carousel.
