# Daily run: how to make and schedule one Short

Follow these steps in order. Read `CHANNEL_RULES.md` first; its rules override everything else.

## 1. Set up

```bash
bash pipeline/setup.sh
```

## 2. Pick the topic

Take the first `[ ]` topic in `topics.md`. The episode slug is `<posting date>-<short-name>`, for example `2026-11-26-wow-signal`. The posting date is **tomorrow** (India time), which gives the owner a day to review. First check the Metricool planner with `getScheduledPosts`. If tomorrow already has a post at 16:00, use the first free day after it.

## 3. Research

Search the web and open at least 3 reliable sources. Write down every number, date and name you will use. Drop any fact you can't confirm.

## 4. Write the episode

Create `episodes/<slug>/`:

- `scenes.py`, modelled on `episodes/2026-11-25-tunguska/scenes.py`:
  - 8–10 scenes. Each is a function `fn(t) -> PIL.Image` (1080×1920), with a base duration in seconds and caption chunks.
  - Use `lib.py` helpers: `Cam`/`draw_map` for maps (real coastlines, rivers), `glow`, `stars`, `conifer`, `caption`, `top_label`, `text_c`.
  - Draw only maps, skies, landscapes, objects, buildings, diagrams and text. **No people, animals or birds.**
  - Add `SPOKEN` for numbers and names the voice might misread, and `SFX(tr, G)` with natural sounds only.
- `meta.json`: `{"title": ..., "caption": ..., "tags": [...], "sources": [{"title": ..., "url": ...}]}`.

## 5. Check before the full render

```bash
PREVIEW=1 python3 pipeline/build.py episodes/<slug>
```

Open `/tmp/build/<slug>/preview.png` and look at every frame. Fix anything that is cut off, overlapping or unreadable, and anything that breaks the rules.

## 6. Render

```bash
python3 pipeline/build.py episodes/<slug>
```

This writes `videos/<slug>.mp4`. Grab 6 frames with ffmpeg and look at them once more.

## 7. Publish the file

Commit and push to the `daily` branch:

```bash
git add episodes/<slug> videos/<slug>.mp4 topics.md
git commit -m "Short: <title>"
git -c push.negotiate=true push origin daily
```

The public link is `https://raw.githubusercontent.com/armanintelligence/historymystery-videos./daily/videos/<slug>.mp4`. Check it returns HTTP 200 before scheduling.

Delete videos older than 14 days from `videos/` in the same commit. By then Metricool has already copied them.

## 8. Schedule in Metricool

Use brand `8303864`, timezone `Asia/Calcutta`, 16:00 on the posting date. Set providers to youtube, instagram and facebook, with media set to the raw link.

- `youtubeData`: `{"title": <title>, "type": "short", "privacy": "public", "madeForKids": false, "category": "EDUCATION", "tags": [...]}`
- `instagramData`: `{"type": "REEL", "showReelOnFeed": true}`, with no `audioConfiguration`, since the rules ban music.
- `facebookData`: `{"type": "REEL", "title": <title>}`

## 9. Report

Send the channel owner:
- the video file,
- the title and posting time,
- the sources, and
- how to cancel: delete the post in the Metricool planner before 4 PM.
