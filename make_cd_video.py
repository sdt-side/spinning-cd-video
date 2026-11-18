#!/usr/bin/env python3
"""ジャケットの横で半月のCDが回る動画を作る。

手続き的な生成です。動画生成モデルは使いません。
盤面テクスチャを PIL で1フレームずつ回転させ、ffmpeg に流し込んで
10秒ループ（240フレーム @24fps、時計回りにちょうど1回転）を作ります。

使い方:
  # バランス確認用の静止画
  python3 make_cd_video.py --jacket jacket.jpg --disc disc.png --still balance.png
  # 10秒ループ
  python3 make_cd_video.py --jacket jacket.jpg --disc disc.png --loop loop10.mp4

曲のミックスは README の ffmpeg コマンドを参照。
"""
import argparse
import subprocess

import numpy as np
from PIL import Image


def parse_args():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--jacket", required=True, help="ジャケット画像（完成品）")
    p.add_argument("--disc", required=True, help="盤面テクスチャ（正方形、円が内接）")
    p.add_argument("--still", help="バランス確認用の静止画を出力するパス")
    p.add_argument("--loop", help="10秒ループ動画を出力するパス")
    p.add_argument("--width", type=int, default=1080, help="フレーム幅 (default: 1080)")
    p.add_argument("--height", type=int, default=720, help="フレーム高さ (default: 720)")
    p.add_argument("--disc-diameter", type=int, default=640,
                   help="盤面の直径 px (default: 640)")
    p.add_argument("--bg", type=int, default=255,
                   help="背景の明るさ 0-255 (default: 255 = 白)")
    p.add_argument("--ccw", action="store_true",
                   help="反時計回りにする（既定は時計回り）")
    p.add_argument("--fps", type=int, default=24)
    return p.parse_args()


def compose_frame(jacket_np, tex_img, angle_deg, fw, fh, d, bg):
    """1フレームを組む。ジャケットは左に置き、盤面中心はジャケットの
    右端（= ジャケット幅の位置）に一致させる。"""
    jacket_w = jacket_np.shape[1]
    px = jacket_w - d // 2          # 盤面の左端（中心がジャケット右端）
    py = fh // 2 - d // 2           # 盤面の上端（縦は中央）
    rot = tex_img.rotate(angle_deg, resample=Image.BICUBIC).resize(
        (d, d), Image.LANCZOS)
    # 円形マスク（縁を少しだけぼかす）
    yy, xx = np.mgrid[0:d, 0:d]
    rr = np.hypot(xx - d / 2, yy - d / 2) / (d / 2)
    alpha = np.clip((1.0 - rr) / 0.004, 0, 1).astype(np.float32)[..., None]
    frame = np.full((fh, fw, 3), bg, np.float32)
    x0, x1 = max(px, 0), min(px + d, fw)
    y0, y1 = max(py, 0), min(py + d, fh)
    sub = np.asarray(rot).astype(np.float32)[y0 - py:y1 - py, x0 - px:x1 - px]
    a = alpha[y0 - py:y1 - py, x0 - px:x1 - px]
    frame[y0:y1, x0:x1] = frame[y0:y1, x0:x1] * (1 - a) + sub * a
    # ジャケットを上に貼る（盤面の左半分がジャケットに隠れる）
    frame[:, :jacket_w] = jacket_np
    return np.clip(frame, 0, 255).astype(np.uint8)


def main():
    args = parse_args()
    fw, fh, d = args.width, args.height, args.disc_diameter
    # ジャケットはフレームの高さに合わせて正方形にリサイズ
    jacket = Image.open(args.jacket).convert("RGB").resize((fh, fh), Image.LANCZOS)
    jacket_np = np.asarray(jacket).astype(np.float32)
    tex = Image.open(args.disc).convert("RGB")

    if args.still:
        frame = compose_frame(jacket_np, tex, 0.0, fw, fh, d, args.bg)
        Image.fromarray(frame).save(args.still)
        print(f"still -> {args.still}")
        return

    if not args.loop:
        raise SystemExit("--still か --loop のどちらかを指定してください")

    frames = args.fps * 10  # 10秒で1回転
    sign = 1.0 if args.ccw else -1.0  # PIL の rotate は正が反時計回り
    cmd = [
        "ffmpeg", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24",
        "-s", f"{fw}x{fh}", "-r", str(args.fps), "-i", "-", "-an",
        "-c:v", "libx264", "-pix_fmt", "yuv420p",
        "-color_primaries", "bt709", "-color_trc", "bt709",
        "-colorspace", "bt709", "-color_range", "tv",
        "-crf", "18", "-preset", "medium", args.loop,
    ]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE,
                            stderr=subprocess.DEVNULL)
    for f in range(frames):
        angle = sign * 360.0 * f / frames
        frame = compose_frame(jacket_np, tex, angle, fw, fh, d, args.bg)
        proc.stdin.write(frame.tobytes())
    proc.stdin.close()
    proc.wait()
    print(f"loop -> {args.loop}")


if __name__ == "__main__":
    main()
