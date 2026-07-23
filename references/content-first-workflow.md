# Content-first editorial workflow

Use this reference only for `$poem-content`. It turns long Chinese source material into a source-faithful `ContentPlan`; it does not write final cover titles, choose layouts, or generate images.

## 1. Separate source roles

Label every input as one of:

- `content_source`: facts, arguments, examples, names, and wording that may appear in cards;
- `visual_reference`: appearance only, never evidence for a claim;
- `reusable_asset`: a user-owned or authorized image or file.

Do not import objects, labels, dates, or facts from a visual reference into content.

## 2. Establish source boundaries

Record:

- source name or user-provided identifier;
- exact source text or a stable local path;
- SHA-256 digest when the plan will continue downstream;
- names, dates, numbers, causal claims, and quotations that require exact preservation;
- claims the source does not establish.

If the source has no clear conclusion, choose the smallest defensible claim. Do not manufacture a dramatic change.

## 3. Build the editorial brief

Extract:

- output scope: `cover-only`, `cover-plus-interiors`, or `interiors-only`;

| Field | Requirement |
| --- | --- |
| Topic | One factual sentence |
| Central change | What becomes different after reading |
| Reader tension | Existing question, frustration, misconception, or opportunity |
| Reader payoff | What the reader can understand, decide, or do |
| Strongest evidence | One concrete mechanism, case, result, or comparison |
| Boundaries | What must not be inferred or invented |
| Desired action | Continue, save, try, compare, discuss, or verify |
| Cover direction | One angle only; not final cover wording |

Prefer concrete nouns and verbs from the source. Remove throat-clearing, repeated setup, generic encouragement, and unsupported conclusions.

## 4. Extract claims before cards

List every distinct claim in the source. For each claim record:

- exact source excerpt or faithful source summary;
- evidence type;
- reader value;
- dependencies on earlier claims;
- whether it can stand alone.

Merge duplicates. Remove claims that merely restate the topic. Order remaining claims so a reader can follow them without the original source.

## 5. Build the swipe sequence

Default to five interior cards when the user requests a set without a count. For `cover-only`, keep the interior-card list empty. Choose only roles the source supports:

- `context`: why this matters now;
- `claim`: the central assertion;
- `mechanism`: how or why it works;
- `evidence`: concrete example, comparison, result, or source object;
- `use`: action, checklist, limitation, or decision;
- `source`: provenance, boundary, or continuation.

Each card needs:

- one unique claim;
- a 12-28-character core sentence;
- normally 35-90 supporting Chinese characters;
- one source excerpt;
- one reason to exist;
- no repeated function from the preceding card.

Do not write the final cover title here. The cover direction becomes input to `$poem-title`.

## 6. Decide whether content needs an image

Only classify the semantic need; do not art-direct the image.

Allowed roles:

- `explain` a mechanism;
- `document` a source-backed object or event;
- `compare` two states;
- `locate` a real place or object;
- `sequence` a process;
- `symbolize-specific-idea` when no literal evidence is viable.

Use `none` when text is sufficient. Reject “create atmosphere” as an image reason.

## 7. Deliver and validate

Return a readable brief and card table, then write `poem-content-plan/v1` when another stage follows. The artifact must match `references/stage-contracts.md`.

Reject the plan when:

- a card has no source excerpt;
- two cards make the same claim;
- the reader payoff is only mood;
- evidence is replaced by an attractive metaphor;
- a fact or outcome is stronger than the source;
- the plan already contains visual layout instructions.
