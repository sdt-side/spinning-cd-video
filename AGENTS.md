# AGENTS.md

Instructions for AI agents (Codex, Muse, and others) working in this repository.

## What this repository is

A complete, self-contained method for making "jacket + spinning CD" videos
procedurally with Python (PIL) and ffmpeg — no video generation model.
The full method lives in the README: `README.md` (Japanese),
`README.en.md` (English), `README.ko.md` (Korean). **Read the README first.**
If you edit the method, keep all three language versions in sync.

## Workflow — always two phases, in this order

1. **Phase 1 — finish the still images.** Composite the jacket design onto
   the design surface of the blank jacket, and build the disc-face texture
   from the jacket design. Then render ONE balance-check still in the final
   layout and **get the user's approval before rendering any video**.
2. **Phase 2 — video.** Run `make_cd_video.py` (layouts: `side` = 3:2 with
   jacket, `halfmoon` = 9:16 disc only), then mix the song with the ffmpeg
   command in the README.

Never skip the balance-still approval. Fixing layout after animation is the
most expensive mistake in this workflow.

## Fixed materials — do not regenerate

The four blank base images in the repository root are the standard. Use the
measured geometry from the README's "Base materials" section.

- `IMG_3354.webp` — blank CD jacket (design surface: x 201..1517, y 95..1547)
- `IMG_3353.webp` — blank silver CD (center (770, 808), radius ~700)
- `IMG_3356.jpeg` — blank LP jacket (design surface: x 52..1584, y 11..1593)
- `IMG_3357.jpeg` — blank vinyl LP (center (802, 802), radius 768)

Do not paint over photos to fake a blank, and do not substitute newly
generated blanks — dimensions and texture must stay identical across jobs.

## Disc-face design rules

- Base colour may be full-bleed to the rim.
- Text and logos stay inside the printable band: out to 93% of the radius,
  nothing inside the hub clear zone (~36% of the radius). Hub stays clear.
- Zoning: title top-centre, small marks at the left/right midline,
  track/info lines bottom-centre, small rights text along the rim.

## Rendering rules

- Rotation is clockwise (like a real CD), exactly one revolution per
  10 seconds, constant speed, center fixed, no wobble, no zoom.
- The printed design rotates rigidly with the disc.
- Verify visually: extract frames near 0°/90°/180°/270° into a contact sheet
  and look at them. Numeric checks alone are not verification.
- Output: H.264 / yuv420p / bt709 / faststart (iPhone-playable).
- **Every version gets a new file name. Never overwrite an earlier output.**

## House rules

- Do not edit `LICENSE`.
- The four `IMG_*` files are binary assets supplied by the owner. Use them
  as inputs; do not try to recreate, recompress, or replace them.
