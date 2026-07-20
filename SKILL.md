---
name: whole-earth-xhs-cards
description: "Create publish-ready poetic archival cards and editorial graphics for Xiaohongshu, WeChat Official Accounts, landscape decks, stories/reels, and custom canvases. Use pale-white fibrous paper, generous negative space, readable editorial typography, and semantically relevant text-image intersections. Mix at most two visual assets per card from monochrome photos, documents, relief prints, silhouettes, and restrained color blocks. Use for 全球概览、Whole Earth Catalog、莎草纸、古典互联网、诗性档案、极简拼贴 or high-end retro editorial visuals. Offer aesthetic-first, readability-first, and balanced modes."
---

# Whole Earth Xiaohongshu Cards

Create original cards that inherit an editorial system, not a facsimile of a copyrighted page. Never reuse the Whole Earth Catalog logo, exact page scans, or its copyrighted illustrations unless the user supplied them with permission.

## Workflow

1. Parse the input into: topic, audience, desired card count, copy-only or image-card output, illustration preference, and call to action.
2. If visual direction is not sufficiently specified, ask focused questions one at a time or in a very short group. Prioritize: output platform or canvas preset; `aesthetic` / `readable` / `balanced`; preferred asset pairing; accent color or black-and-white; approximate card count. Do not ask questions whose answers are already present. Default to `balanced`, simplified Chinese, and the platform's standard preset. Use Xiaohongshu 3:4 only when the user asks for Xiaohongshu or gives no platform but explicitly asks for social cards.
3. Read `references/style-system.md` and `references/canvas-presets.md` before composing any card. Read `references/visual-quality-rubric.md` when generating final images, reviewing visual quality, or matching user references.
4. Plan the carousel as an alternating visual rhythm. Every card may combine text and imagery, but rotate the dominant weight: image-led → text-led → object-led → diagram-led → image-led → source/recap. Do not split the series into generic “text cards” and “picture cards.”
5. Choose a content-density mode:
   - `aesthetic`: one readable core sentence of 12–36 Chinese characters; optional nonessential microtext.
   - `readable`: title plus 70–140 Chinese characters, divided into 2–4 short blocks.
   - `balanced`: one 12–28-character core statement plus 40–90 characters of supporting copy. Use this by default.
6. Default to one visual asset. Add a second only when it has a distinct semantic or structural job. Count a photo, ticket/document fragment, relief-print illustration, silhouette, or colored shape as one asset. Connector lines and tiny index marks do not count. For each asset, state `semantic_role`; reject it if its relationship to the card's claim cannot be explained in one sentence.
7. Choose a layout from `archive-collage`, `quiet-specimen`, `relief-emblem`, `silhouette-field`, or `text-led-note`. Read `references/style-system.md` for their constraints.
8. Write one JSON spec per final PNG. Validate every spec with `scripts/validate_card_spec.py`, then validate the full sequence with `scripts/validate_series.py`.
9. Use image generation only for text-free source assets. For topic-bearing relief prints, photographs, objects, animals, anatomy, people, or places, attempt a newly generated or supplied asset first. Use the renderer's programmatic fallback only for abstract structure—sequence, comparison, a simple signal, or a restrained color block—and never present its generic plant/path mark as a bespoke topical illustration.
10. Render every approved spec with `scripts/render_card.py`. Do not stop after writing a plan or prompt when the user asked for images.
11. Run `scripts/qa_card.py` against every PNG and inspect its generated phone-size preview. Then score the result with `references/visual-quality-rubric.md`; revise the lowest-scoring category first. Do not treat pixel QA as proof of aesthetic quality.
12. Export each requested canvas as an independent image. Never combine multiple cards, variants, or style samples into one side-by-side sheet.
13. Deliver one PNG file per card or variant. For Xiaohongshu also deliver title/caption/hashtags; for WeChat deliver article title/summary/alt text; for video/story deliver title/safe-zone copy/description; do not force Xiaohongshu metadata onto other formats.

## Content Contract

Before rendering, produce a UTF-8 JSON file using the schema in `assets/example-card.json`. Required fields are `canvas_preset`, `width`, `height`, `priority`, `layout`, `cluster_zone`, `title`, `body`, and `output`. Set `priority` to `aesthetic`, `readable`, or `balanced`; set `layout` to one of the five supported layouts; list no more than two entries in `assets`. For every asset, use a fixed `semantic_role` from `explain`, `document`, `locate`, `sequence`, `compare`, or `symbolize-specific-idea`, plus a concrete `semantic_reason` tied to the exact claim. Tickets and documents additionally require a real `source_basis` and file `path`. When essential text is deliberately meant to enter an asset's layout region, add `intentional_intersection` with `mode`, `reason`, `asset_indices`, and a conservative `max_opaque_overlap`; otherwise QA treats the overlap as an error.

Run the complete pipeline:

```bash
python3 scripts/run_pipeline.py card-01.json card-02.json card-03.json
```

The pipeline validates every spec, checks series rhythm, renders every PNG, and runs pixel QA. The renderer creates `*.layout.json`; QA creates `*-preview.png` plus `*.qa.json`. Use the individual validator/renderer/QA scripts only for debugging, or use another deterministic compositor when the bundled renderer cannot express a necessary, user-requested composition.

After changing the renderer or adding a canvas preset, run the 50-case regression matrix:

```bash
python3 scripts/test_matrix.py
```

## Image Generation Route

When an illustration would materially improve the card, first read `references/illustration-prompts.md`. Generate the illustration without Chinese words, logos, UI chrome, or a complete card layout. Treat the user's bird-and-leaves reference as the relief-print target: crude black carved marks presented on clean pale-white fibrous paper, not a refined antique engraving and not dirty catalog stock.

Use a prompt shaped like:

> A single-color black relief-print illustration of [SUBJECT], hand-carved folk woodcut / linocut appearance, surrounded or interwoven with [PLANT / SYMBOLIC ELEMENTS]. Thick irregular black outlines, blunt carved hatch marks, uneven ink coverage, small white chips and gaps inside the black shapes, flattened anatomy, frontal or side-on silhouette, no realistic depth. Isolated asset on transparent background; if transparency is unavailable, use one completely flat uniform #FAFAF7 background with no texture, shadow, border, or paper edge. No words, letters, numbers, logo, signature, watermark, or color.

Then add the saved asset through the JSON `assets` list. Keep generated imagery subordinate to the information. Add the continuous fibrous paper texture only once during final-card composition.

## Output Rules

- Use simplified Chinese unless requested otherwise.
- Choose a canvas preset from `references/canvas-presets.md`, or use `custom` with explicit width and height.
- Scale safe margins proportionally. Use roughly 5.5%–7% of the short edge; respect platform crop-safe zones.
- Keep roughly 70%–88% of the canvas visually quiet. Let the focal cluster occupy about 12%–30%.
- Use one muted accent at most, covering under 5% of the card. Black-and-white is valid.
- Set essential Chinese copy large enough for phone reading. Microtext may be tiny only when it is atmospheric and expendable.
- Shorten copy for compact canvases instead of forcing portrait-card density into 500×500 or 900×383 exports.
- Use no more than two visual assets per card.
- Every asset must be relevant to the exact card content. Do not use generic vintage props as atmosphere.
- Use tickets, receipts, stamps, maps, dates, coordinates, route lines, and place names only when the content genuinely involves travel, place, chronology, transaction, provenance, or documentary evidence. Never invent plausible-looking metadata merely for decoration.
- Interpret 莎草纸 as clean pure-white handmade papyrus: white at first glance, with only faint ivory-gray fibers and delicate pressed-pulp texture visible up close. Never make it yellow, beige, brown, stained, burned, dirty, heavily distressed, or antique-looking.
- Avoid big poster headlines, thick horizontal rules, full-page frames, multi-column article layouts, decorative boxes, centered quote-template layouts, scrapbook clutter, rounded app cards, gradients, and glossy product mockups.
- Avoid fine Victorian engraving, delicate botanical etching, smooth vector line art, tattoo flash, Japanese ukiyo-e, Chinese ink wash, cute storybook illustration, photorealism, polished anatomy rendering, and decorative Art Nouveau curves. These are visually different from the rough catalog relief print in the reference.
- Do not reproduce reference pages pixel-for-pixel.

## Asset Rights and Provenance

- Treat user-supplied references as direction unless the user explicitly authorizes reuse.
- Do not lift tickets, photographs, scans, logos, signatures, watermarks, or illustrations from someone else's design.
- Use user-owned, licensed, public-domain, or newly generated assets. Record the source/license for externally sourced material.
- Remove or replace real personal data, ticket numbers, addresses, names, barcodes, and identifying marks unless the user explicitly wants and is authorized to publish them.

## Failure Recovery

- If the image model produces embedded or incorrect text, reject it and regenerate the asset without text.
- If a generated asset includes a watermark, logo, signature, or third visual object, reject or crop it before composition.
- If image generation is unavailable or fails, use a semantically honest abstract fallback, tell the user that the result uses a fallback, and do not disguise a generic plant or path as a subject-specific image.
- If a chosen asset pairing cannot express the topic clearly, propose another pairing instead of forcing the motif.
- If an asset's `semantic_role` is vague, decorative, or interchangeable with any topic, remove it.
- If the user requests multiple ratios, reuse the content strategy but create separately composed variants. Give them the same `series_id` and distinct `variant_id` values so series QA stays meaningful.
- If the content cannot fit at phone-readable size, split it across cards; never solve overflow by shrinking essential text into microtext.
- When style approval is needed, generate one sample card first. Generate a second alternative only when the user explicitly requests comparison. Never place alternatives side by side in one image.

## Prompt-Only Delivery

If the user asks only for a reusable prompt rather than files, provide the prompt in `references/master-prompt.md`, replacing bracketed variables with their subject and constraints. Keep the exact-text rule: generate backgrounds/illustrations separately and overlay Chinese text in a deterministic design tool.
