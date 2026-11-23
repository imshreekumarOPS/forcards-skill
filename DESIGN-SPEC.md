# Format spec: `listcards`

Measured from a 1920 x 2596 px reference carousel (two slides). The numbers live in
`formats/listcards/theme.yaml`; this file explains the *why* so new content stays on-pattern.

## Visual system

| Element | Spec |
| --- | --- |
| Canvas | 1920 x 2596 (about 3:4), pure white `#FFFFFF`. No imagery, logos, handles or page numbers. |
| Margins | 112 px left, right and bottom. Content is vertically centered, so a half-full last slide still looks intentional. |
| Title (slide 1 only) | Inter Bold 66 px, tracking about -0.047em, `#111`, one line, left aligned. Pattern: `<Subject> on how to <outcome>`. The 2-3 key words get a **pink marker** (`#FFA6CC`, 44 px tall, sitting on the lower half of the text, 11 px side padding). |
| Title to first card | 74 px |
| Card | White, 2 px `#E6E6E6` border, 24 px radius, **no shadow**, full content width (1696 px), 32 px gap between cards. |
| Card padding | 52 px sides, 45 px top, 41 px bottom. |
| Card heading | Inter SemiBold 38 px, `#111`, tracking -0.019em, sentence case, no punctuation. |
| Bullets | Inter Regular 32 px, `#222`, 50 px line pitch, 13 px between bullets. Dot is a hot pink-red `#FF006C`, 11 px, indented 16 px; text starts 49 px from the card edge (hanging indent). |
| Density | **5 cards per slide x 4 bullets per card.** Cards size to content (about 398 px for 4 one-line bullets, about 447 px when one bullet wraps). Slide 2 continues exactly like slide 1 minus the title. |
| Colour discipline | Only three non-neutral colours exist: marker pink (title only), dot red (bullets only), and border grey. Nothing else is coloured. |

Rendering notes: grayscale antialiasing (no LCD fringes), straight quotes (`"` and `'`) as in the reference.

## Copy patterns (this is what makes it read like the reference)

**Title**
- `Person/Thing on how to <verb phrase>`. Short (5-7 words), sentence case, no colon, no emoji.
- Highlight only the payoff words (`==win attention==`), never more than 3 words.

**Card headings** (2-6 words)
- Imperative coaching voice or a crisp rule: *Start with the title and thumbnail*, *Obsess over the first minute*, *Raise the stakes as you go*, *Don't let retention die*.
- Or a blunt statement: *No does not mean no*, *Add a wow factor*.
- Parallel feel across the deck; the order tells a story (beginning to end, or step 1 to step N).

**Bullets** (exactly 4 per card, 8-24 words, max 2 lines)
Each card follows the same arc, in this order:
1. **Claim**: the principle in plain words.
2. **Evidence / example**: a concrete number, named example or contrast (`21 million of 60 million`, `Ketchup` vs `Front Yard`).
3. **Mechanism or rule**: why it works or what to do.
4. **Takeaway**: a short, punchy closer (`Subpar is not okay.`).

Style rules:
- One full sentence per bullet, ends with a period. A second short sentence is fine (`... click off.`).
- Sentence case. No bold, no emoji, no hashtags, no arrows.
- Plain words. Define any acronym the first time it appears (`CTR ... click-through rate`).
- Keep the speaker's own phrases in straight double quotes (`"It's important we never lose our wow."`). Never invent quotes.
- Specific beats general: numbers, names, before/after pairs.
- Bullets inside a card should not repeat each other; each adds a new fact.

**Deck shape**: 10 cards (= 2 full slides) is the reference. 5-10 cards also works; the packer handles the rest.
