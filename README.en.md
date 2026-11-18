[日本語](README.md) | English | [한국어](README.ko.md)

# How to make a jacket + spinning CD video

A procedure for making a video where a half-moon CD sits beside its jacket and the disc makes exactly one clockwise revolution in 10 seconds.

Frames are rendered procedurally — rotated one by one in Python (PIL). **No video generation model is used.** A 10-second loop is rendered, repeated to the length of the song, and the song is mixed in. Because the original image itself is rotated, the disc design never degrades.

This is the record of the form completed for "Fleeting Four Seasons (Japanese ver.)".

## The overall flow

The work has two phases. **First, finish the still images from the base materials; then turn them into a video with Python.** Do not reverse the order.

**Phase 1: materials → finished images (still-image work)**

1. Jacket: composite the jacket design onto the design surface (the black card) of the blank jacket to make the "finished jacket image"
2. Disc: build the disc-face design from the jacket design on top of the blank disc, producing the "disc texture" (rules in "Disc-face design rules" below)
3. Place the finished jacket and disc in the final layout and make one "balance-check still"; get approval at this point

**Phase 2: finished images → video (Python)**

4. Render a 10-second loop (one revolution) with `make_cd_video.py`
5. Repeat the loop, mix the song in, and cut to the song's length

`make_cd_video.py` only ever receives the finished images from Phase 1. Every design decision is settled in Phase 1 — that is the point of this method.

## Finished-form specifications

| Item | Value |
|---|---|
| Frame | 1080×720 (3:2) |
| Background | White |
| Jacket | 720×720, on the left |
| Disc diameter | 640px (against the 720px jacket height) |
| Disc position | Center aligned with the jacket's right edge; only the right half is visible — a half moon |
| Rotation | Clockwise (the same direction as a real CD), exactly one revolution in 10 seconds, constant speed |
| Loop | 10 seconds (240 frames @24fps), repeated to the song's length |
| Audio | The song mixed in as-is. Video length = song length |
| Output | H.264 / yuv420p / bt709 / faststart (playable on iPhone) |

## What you need

- A jacket image (finished; a photo including the case is fine, or just the design surface)
- A disc-face design image (a square texture with the disc inscribed)
- A song file (the video length follows this file)

## Base materials (required)

If the blank base materials are not fixed, the case and disc dimensions and positions drift every time. Use these four as the standard (repository root, all 1600×1600).

For CD:

- `IMG_3354.webp` — blank black jacket (in a clear jewel case, with a white spine strip)
  - Design surface (the black card): **x 201..1517, y 95..1547**. Paste the design inside this area
- `IMG_3353.webp` — blank unprinted silver CD (on white)
  - Disc center **(770, 808)**, radius **about 700** (slightly elliptical — normalize to a circle when building the texture)

For records (LP) — the video rules are the same as CD (half moon, one revolution per 10 seconds). The label face is rebuilt from the jacket design:

- `IMG_3356.jpeg` — blank black LP jacket (matte black sleeve, white spine edge)
  - Design surface (the black front): **x 52..1584, y 11..1593**
- `IMG_3357.jpeg` — blank black LP record (plain white label)
  - Disc center **(802, 802)**, radius **768**, label radius **about 327**

The black area of the jacket is the design surface. Do not make blanks by painting over a photo — prepare them as genuinely blank objects (texture and dimensions won't stay stable otherwise).

## Disc-face design rules

Respect the printable area of a real CD.

- The base colour may fill the whole face out to the rim (full-bleed solid)
- But **element placement (text, logos) stays inside the printable band**: out to 93% of the radius on the outside, and nothing inside the hub clear zone (about 36% of the radius)
- Zoning examples:
  - Title: top centre
  - Small marks: around the left/right midline
  - Track / info lines: bottom centre
  - Small rights text: along the inside of the rim
- Keep the hub area clear (leave the blank material's hub as-is)

## Procedure

The flow above, broken into work steps (1–3 are Phase 1, 4–5 are Phase 2).

1. **Prepare the disc texture** — make the disc design into a square texture. Fit the circle's center and radius to the material (circle detection on generated images gets dragged by shadows and backdrops; fitting the bounding box of a saturation mask proved stable).
2. **Assemble the jacket** — paste the design onto the design surface of the jacket material.
3. **Make one balance-check still** — render a still in the final ratio and layout, and **always get approval before animating**. Fixing after animation costs much more rework.
4. **Render the 10-second loop** — `make_cd_video.py` generates frames one by one and streams them into ffmpeg. The rotation angle for frame f is `-360 × f / 240` degrees (PIL's `rotate` is counter-clockwise for positive angles, so clockwise is negative).
5. **Mix the song** — repeat the loop and cut at the song's length (command below).
6. **Verify** — extract frames near 0°/90°/180°/270° into a contact sheet and check by eye that the hub doesn't wobble and no seam appears. Never pass on numeric checks alone.
7. **Deliver under a new file name** — overwriting the same name can make the receiving client show a cached older version. Give every version a new name (…_v2, …_v3).

## Usage

```bash
# Balance-check still
python3 make_cd_video.py --jacket jacket.jpg --disc disc_texture.png --still balance.png

# 10-second loop
python3 make_cd_video.py --jacket jacket.jpg --disc disc_texture.png --loop loop10.mp4

# Mix the song to finish (example: a 138-second song)
ffmpeg -stream_loop 14 -i loop10.mp4 -i song.m4a \
  -map 0:v -map 1:a -t 138.0 \
  -c:v libx264 -pix_fmt yuv420p \
  -color_primaries bt709 -color_trc bt709 -colorspace bt709 -color_range tv \
  -crf 20 -maxrate 7000k -bufsize 14000k \
  -c:a aac -b:a 192k -movflags +faststart -video_track_timescale 15360 \
  output_v1.mp4
```

Mixing note: `-shortest` combined with stream copy may not cut at the song's length. Re-encode and cut with `-t <song seconds>`.

## Spec prompt for an AI agent

Assuming the disc, jacket and audio are already decided — a form you can hand to an AI agent as-is:

```
Generate a CD video in Python.

[Inputs (all final)]
- Jacket image: <file>
- CD disc-face design image: <file>
- Audio file: <file> (the video length follows the audio)

[Layout]
- Frame 1080x720 (3:2), white background
- Jacket placed on the left at 720x720
- The CD's center aligned with the jacket's right edge, diameter 640px,
  so only the right half is visible — a half moon
- First show me one balance-check still in this layout.
  Animate only after I approve it.

[Rotation]
- Clockwise, exactly one revolution in 10 seconds, constant speed
- Center fixed, no wobble, no zoom
- The printed design rotates rigidly together with the disc

[Audio and output]
- Mix the audio in as-is, repeating the rotation loop to the audio's length
- H.264 / yuv420p / bt709 / faststart, playable on iPhone
- Use a new output file name every time (never overwrite)
```

## The other form: 9:16 half-moon only (no jacket)

A form that shows **the disc alone**, large. The disc's center sits on the left edge of the frame and it rotates as a "half moon" with only its right half visible. Use it when the disc design itself is the subject; it is also the CD kit's standard form (9:16).

The flow is the same two phases. In Phase 1, finish only the disc texture (no jacket is made); in Phase 2, pass `--layout halfmoon`.

| Item | Value |
|---|---|
| Frame | 720×1280 (9:16) |
| Background | White |
| Jacket | None |
| Disc position | Center on the **left edge, vertically centred** (x=0, y=height÷2). Only the right half is visible |
| Disc diameter | Frame height × 0.89 (about 1140px at 720×1280) — a size that leaves a little margin at top and bottom |
| Rotation | Clockwise, exactly one revolution in 10 seconds, constant speed. Center does not move |
| Audio | None (silent), or mix a song in with the same procedure as the 3:2 version |

Usage:

```bash
# Balance-check still
python3 make_cd_video.py --layout halfmoon --disc disc_texture.png --still balance.png

# 10-second loop
python3 make_cd_video.py --layout halfmoon --disc disc_texture.png --loop loop10.mp4
```

Concrete instructions for an AI agent (9:16 version):

```
Generate a video of a CD disc spinning on its own, in Python.

[Inputs (final)]
- CD disc-face design image: <file> (a square disc texture)
- Audio file: <file> (optional; if used, the video length follows the audio)

[Layout]
- Frame 720x1280 (9:16), white background, no jacket
- Place the CD's center on the left edge of the frame, vertically centred,
  so only the right half is visible — a half moon
- The CD's diameter is about 0.89x the frame height
- First show me one balance-check still in this layout. Animate only after I approve it.

[Rotation]
- Clockwise, exactly one revolution in 10 seconds, constant speed
- Center fixed, no wobble, no zoom
- The printed design rotates rigidly together with the disc

[Output]
- H.264 / yuv420p / bt709 / faststart, playable on iPhone
- Use a new output file name every time (never overwrite)
```

## License

MIT License — see [LICENSE](LICENSE).
