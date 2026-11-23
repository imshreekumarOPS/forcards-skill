---
name: forcards
description: Forcards skill. Create a carousel post (slide PNGs) in a clean "listcards" style (white canvas, rounded outline cards, pink bullets, pink-marker title) from a topic, notes, transcript or article. Use when the user asks to make, write or render a carousel / slides / swipe post, or batch several.
---

# Forcards: carousel workflow

Turns notes into 8-10 rounded-card slides (PNG) in one consistent style.

`SKILL_DIR` = the base directory shown when this skill loads (the folder that contains this file). Always use absolute paths. Do not write files inside `SKILL_DIR`: content and output go in the user's working folder.

- Copy rules + design spec: `SKILL_DIR/DESIGN-SPEC.md` (read once per session before writing)
- Content template: `SKILL_DIR/content/_template.md`; a finished example: `SKILL_DIR/content/example.md`
- Renderer: `SKILL_DIR/render.py`
- Theme numbers: `SKILL_DIR/formats/listcards/theme.yaml`

## One-time setup

The renderer needs Python 3.9+ and a Chromium browser (Edge or Chrome is used if installed).

```
python -m pip install -r SKILL_DIR/requirements.txt
python -m playwright install chromium     # only if neither Edge nor Chrome is installed
```

If `python -c "import playwright, jinja2, yaml"` already works, skip this.

## Steps

1. **Get the source.** Use the user's notes, transcript or link. If only a topic is given, research it (web search, then read primary pages) and base every fact on a source. Never invent statistics, quotes or attributions; drop anything unconfirmed.
2. **Outline** 8-10 cards in a logical or chronological order (10 cards = two full slides).
3. **Write** `<cwd>/carousel/<slug>.md` from the template:
   - Title: `<Subject> on how to ==<outcome>==` (highlight 1-3 words).
   - Each card: short imperative/rule heading (2-6 words), then **exactly 4 bullets** in the order claim, evidence, rule, takeaway; one sentence each, 8-24 words, sentence case, period at end, straight quotes, no bold/emoji.
   - Speaker quotes only if they are real and short.
4. **Render:**
   `python -I "SKILL_DIR/render.py" "<cwd>/carousel/<slug>.md" [--size S]`
   Output lands in `<cwd>/carousel/out/<slug>[-<size>]/slide-NN.png` (use `--out DIR` to change the folder).
   Sizes (each goes to its own folder):
   - default `ref` = 1920x2596
   - `ig` = 1080x1350 (4:5), `ig-tall` = 1080x1440 (3:4)
   - `x` = 1080x1920 (9:16), `x-compact` = 9:16 with smaller type (about 5 cards/slide)
   Use `x-compact` when the user wants fewer slides.
5. **Check:** open the PNGs. Look for: a card taller than a slide (render warns), one-word orphan lines (reword the bullet), a nearly empty last slide (rebalance or add `<!-- slide -->`), typos.
6. **Deliver:** give the full path of the output folder and the slide count. Do not post anywhere.

## Batch

One `.md` per post, then pass all of them to a single `render.py` call.

## Changing the look

Global: `SKILL_DIR/formats/listcards/theme.yaml`. Per post: a `theme:` block in the content front matter, e.g.

```yaml
theme:
  colors: {accent: "#0A84FF", highlight: "#BFE0FF"}
```

A new look = a new folder `SKILL_DIR/formats/<name>/` (copy `listcards`, edit `theme.yaml` and `template.html.j2`) and `format: <name>` in the front matter.
