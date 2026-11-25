# Daily long video: make and schedule one long video

One long, horizontal video a day: the full version of the story told in that day's Short. Read `CHANNEL_RULES.md` first; its rules override everything here. The steps match `DAILY_RUN.md` except where noted.

## 1. Set up

```bash
bash pipeline/setup.sh
```

## 2. Pick the date and topic

- The posting slot is **19:00 India time** (Asia/Calcutta) **tomorrow**. The run happens in the early afternoon, after the daily Short run has scheduled tomorrow's Short.
- Check the Metricool planner with `getScheduledPosts` for tomorrow. If it already has a long video (a post at 19:00, or a YouTube post whose type is `video`), stop: tomorrow is already done.
- The Short at 16:00 on the same day is expected. Long videos are the one exception to "one post a day". Never schedule two long videos on the same day.
- Topic: the Short scheduled for tomorrow (its `[x]` line in `topics.md` carries tomorrow's date), so the Short and the long video tell the same story on the same day. If that topic already has a folder in `long/`, or tomorrow has no Short, use the most recent `[x]` topic that has no folder in `long/` yet.
- Slug: `<posting date>-<short-name>-long`, for example `2026-11-29-wow-signal-long`.

## 3. Research

Start from the Short's `meta.json` sources, then go deeper: at least 5 reliable sources. Write down every number, date, name and quote you use, with the page it came from. Drop anything you can't confirm, and say "about", "still debated" or give a range where sources disagree.

## 4. Write the episode

Create `long/<slug>/scenes.py` and `meta.json`, modelled on `long/2026-11-29-wow-signal-long/`:

- **6–8 minutes**, about 900–1,100 spoken words, 18–25 scenes grouped into numbered chapters (shown with `top_label`, e.g. `CHAPTER 2 · THE BIG EAR`).
- Horizontal 1920×1080. Build with `HM_FORMAT=long` (it switches `lib.py` to the long layout: captions centred at y≈940, top label at y=70). Keep visuals between y=110 and y=830.
- Each caption chunk must fit on **2 lines** (≈90 characters). Split longer sentences into chunks with "…".
- Same visual rules as the Shorts: maps, skies, landscapes, objects, buildings, diagrams and text only. **No people, animals or birds. No music.** Natural sounds only in `SFX`.
- Last spoken line stays "Follow for more unexplained history." (the default outro).
- `meta.json`: `{"title", "description", "tags", "sources"}`. The description has a 1–2 sentence summary, chapter timestamps (`0:00 Intro` first, computed from the built timeline), and the sources list.

## 5. Check before the full render

```bash
HM_FORMAT=long PREVIEW=1 python3 pipeline/build.py long/<slug>
```

Look at every frame of `/tmp/build/<slug>/preview.png` (crop it, it is wide). Fix anything cut off, overlapping, unreadable or against the rules.

## 6. Render

```bash
HM_FORMAT=long nohup python3 pipeline/build.py long/<slug> > /tmp/long_build.log 2>&1 &
```

It takes about 20–30 minutes; poll the log. It writes `videos/<slug>.mp4`. Check the length is 6–8 minutes and the file is **under 95 MB** (GitHub rejects files over 100 MB). Look at at least 12 frames spread across the video.

## 7. Thumbnail

Make `videos/<slug>.jpg` (1280×720, under 2 MB) in the channel style: one big line of text, no faces or figures, nothing misleading.

## 8. Publish the files

```bash
git add long/<slug> videos/<slug>.mp4 videos/<slug>.jpg
git commit -m "Long: <title>"
git -c push.negotiate=true push origin daily
```

Check both raw links return HTTP 200:
`https://raw.githubusercontent.com/armanintelligence/historymystery-videos./daily/videos/<slug>.mp4` (and `.jpg`).

## 9. Schedule in Metricool

Brand `8303864`, timezone `Asia/Calcutta`, 19:00 on the posting date. Providers: **youtube and facebook only** (not Instagram). Media: the raw mp4 link. `text`: the description from `meta.json`.

- `youtubeData`: `{"title": <title>, "type": "video", "privacy": "public", "madeForKids": false, "category": "EDUCATION", "tags": [...]}`
- `facebookData`: `{"type": "POST", "title": <title>}`
- `videoThumbnailUrl`: the raw jpg link. If Metricool rejects the post because of the thumbnail, schedule it again without it and mention that in the report.

## 10. Report

Send the owner the video file, the title, the posting date and time, the sources, and how to cancel: delete the post in the Metricool planner before 7 PM on the posting date.
