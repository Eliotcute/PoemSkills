# Content-first workflow

Use this workflow whenever the input contains a long passage, article, transcript, research note, or screenshot with substantial copy. The visual system begins only after the content has a clear editorial structure.

## 1. Separate source roles

Label every input as one of:

- `content source`: facts, arguments, examples, names, and wording that may appear in the cards;
- `visual reference`: composition, paper, typography, image treatment, and pacing only;
- `reusable asset`: a user-owned or authorized image that may appear in the final work.

Do not copy objects or metadata from a visual reference into the content. A bird, ticket, coordinate, date, place name, stamp, or English label is invalid unless the content source supports it.

## 2. Build the editorial brief

Extract the following before writing cover copy:

| Field | Requirement |
|---|---|
| Topic | One factual sentence |
| Central change | What becomes different after reading this |
| Reader tension | The question, frustration, misconception, or opportunity already felt by the audience |
| Reader payoff | What the reader can understand, decide, or do |
| Strongest evidence | One source-backed example, mechanism, result, or comparison |
| Boundaries | What the source does not prove and what must not be invented |
| Desired action | Save, try, compare, discuss, or continue reading |

If the source has no clear claim, say so and propose the smallest defensible claim. Do not manufacture a dramatic conclusion.

## 3. Write the cover promise

The cover earns the next swipe. It does not summarize every card.

Write three candidates using different angles:

1. `direct value`: what the reader will learn or gain;
2. `change or contrast`: before versus after, old assumption versus new reality;
3. `specific mechanism`: the concrete tool, process, event, or observation that makes the content distinctive.

Then select one. The selected line must be:

- source-faithful;
- understandable without the caption;
- specific enough that it could not title an unrelated post;
- normally 8–18 Chinese characters;
- free of empty commands such as “一定要看”, “建议收藏”, “颠覆认知”, or “真相来了”.

An optional subtitle may clarify the subject in 12–28 Chinese characters. Do not put the whole argument on the cover.

## 4. Turn the source into a swipe sequence

Default to one cover plus five interior cards when the user requests a set without a count.

Use only the steps the source supports:

1. `cover`: promise and subject;
2. `context`: why this matters now;
3. `claim`: the central idea;
4. `mechanism`: how it works;
5. `evidence`: example, screenshot, comparison, or result;
6. `use`: action, checklist, limitation, or conclusion.

Each interior card must contain:

- one claim that can stand alone;
- a 12–28-character core sentence;
- 35–90 Chinese characters of explanation when needed;
- one reason to exist in the sequence;
- no repeated claim from the previous card.

Prefer concrete nouns and verbs from the source. Remove throat-clearing, repeated setup, generic encouragement, and conclusions unsupported by evidence.

## 5. Decide whether an image is necessary

Text is the primary content. Add an image only when it performs one of these roles:

- proves or documents a claim;
- explains a mechanism;
- compares two states;
- locates a real place or object;
- symbolizes one specific idea that would otherwise be difficult to grasp.

No image is better than a generic image. Reject decorative birds, leaves, stamps, paths, maps, browser icons, robotic hands, or fake documents that can be swapped into another topic unchanged.

For each proposed asset, write:

- `asset`;
- `source sentence`;
- `semantic role`;
- `why this asset and not a generic substitute`;
- `source basis`.

## 6. Choose one cover system

### Editorial explanation

Use for tools, arguments, analysis, cases, and instructional content.

- pale-white fibrous paper;
- 60%–78% quiet space;
- a two-to-four-line cover promise at clear phone-reading scale;
- optional relevant monochrome image occupying 20%–38% of the page;
- support line, index, fine rule, and one muted blue mark;
- text and image share an alignment, connector, crop edge, or controlled overlap.

### Printed symbol

Use when the source contains one strong visual metaphor, object, mechanism, or transformation.

- pale-white fibrous paper, never dirty beige;
- one rough printed block occupying 20%–30% of the width;
- inside the block, one topic-specific cutout or negative-space symbol;
- two or three short annotations taken from the source vocabulary;
- one short Chinese cover line or proposition;
- one low-saturation accent: faded blue, brick red, olive, or gray violet.

Do not copy the bird or the words `shore`, `pause`, or `wing` from a reference. Generate a symbol inseparable from the actual topic.

## 7. Prompt-only output order

When the user asks for a prompt, deliver one reusable prompt that forces this order:

1. editorial brief;
2. three cover candidates and one selection;
3. exact cover copy;
4. exact cover hierarchy or carousel script table, according to the requested scope;
5. visual reference contract;
6. asset decision and semantic rationale;
7. text-free asset-generation prompt when needed;
8. final composition prompt with exact Chinese text and line breaks;
9. Xiaohongshu title, caption, and hashtags.

The prompt must say “do not generate images immediately.” The model first returns the content and design plan. It generates only the requested cover or cards after approval, unless the user explicitly says to start directly.

## 8. Reject these outputs

- two style samples when the user asked for one cover;
- an attractive card that fails to explain the source;
- a sparse quote card with no reader payoff;
- a cover filled with the source paragraph;
- a card series whose claims are interchangeable or repetitive;
- a generated picture with Chinese text baked in and misspelled;
- unrelated archival decoration;
- invented metadata;
- a warm, stained, antique parchment look when the requested paper is clean white.
