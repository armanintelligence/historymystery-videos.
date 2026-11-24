# Channel rules: historymystery2027

Faceless channel: **unexplained history, investigated with science.** Every video must follow these rules. They are not optional.

## Content rules (set by the channel owner)

1. **No faces of living beings.** No people, animals, birds or insects, in any video, thumbnail, cover frame or trailer. That includes silhouettes with faces, portraits, historical photos that show people, mascots and cartoon characters. Plants (trees, stumps, grass, crops) are fine.
2. **No nudity.** Nothing even partly revealing, including in historical artwork.
3. **No music.** No piano, violin, drums, synths or any instrument, and nothing tune-like. Natural sounds only: wind, rumble, explosions, water, fire, waves, wood snapping. Never add platform music (Instagram audio, TikTok auto-music, YouTube audio library).

## Visual style

- Dark navy background, amber (#FF963C) highlight, cyan (#6ED2FF) secondary, white text, Inter fonts.
- Made of maps, diagrams, skies, landscapes, objects, buildings, cross-sections, globes and timelines, drawn in code (`pipeline/lib.py`).
- Vertical 1080×1920, 30 fps. Keep important things between y=220 and y=1150. Captions go in the box at y≈1360, never at the very bottom or the right edge, where YouTube's buttons sit.
- Burnt-in captions: every narrated line, with key words in amber.

## Narration

- AI narrator voice `bm_george` (Kokoro, British male, documentary tone), speed 0.92.
- Calm, factual, curious. Short sentences. Hook in the first 3 seconds.
- Spell numbers out in `SPOKEN` when the voice might misread them.
- Last spoken line: "Follow for more unexplained history."

## Accuracy

- Every fact in a script must come from a reliable source (encyclopaedia, museum, university, space agency, major news). List the sources in the episode's `meta.json`.
- If sources disagree, say "about", give a range, or say "still debated".
- Avoid topics that touch religious belief or sacred sites, current politics, or recent tragedies with living victims.

## Format

- **Daily Short:** 45–80 seconds, 8–10 scenes, one topic, one surprising question.
- Posted at **4 PM India time** (Asia/Calcutta) on YouTube (Short), Instagram (Reel) and Facebook (Reel) through Metricool.
- Title: one strong emotion or curiosity word at most, under 70 characters.
- `madeForKids: false`, category `EDUCATION`.
