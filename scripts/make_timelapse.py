"""Animated WebP for the documentation: intro photos, then a device's time-lapse with the
segmentation mask and the coverage of the ring's growing area over time.

Needs DWARPH-CV (``pip install -e .`` in a clone of https://github.com/DWARPHs/DWARPH-CV) and
matplotlib. Example (the figure in the documentation):

    python scripts/make_timelapse.py \
        --device-dir /data/Device_mirror/C4E408 --start 20260911_132116 --every-min 60 \
        --intro assets/20260911_151949.jpg "A fleet of DWARPH devices" \
        --intro assets/20260918_132436.jpg "Inside a device: duckweed growing in the reference ring" \
        --out assets/duckweed_segmentation_C4E408.webp --csv coverage_C4E408.csv

Frames: one image every --every-min minutes (the one closest to each time point). Both panels
are undistorted with the camera calibration; the right panel is the model's mask with the
fitted inner edge of the ring in red. Coverage = duckweed area inside the ring / area inside
the ring (``dwarph_cv.ring.ring_coverage``). If the ring is not found in a frame, the last
ring found is used. The curve spans the whole series on a fixed axis and is revealed up to the
frame being shown; grey bands are the program's night (all scheduled lights off), from the
metadata of every image of the series, so the bands are exact to the capture interval. Each
image shows the program's set temperature and light levels at that moment (``.json`` next to
the image). Images are only read.
"""
from __future__ import annotations

import argparse
import datetime as dt
import io
import json
import re
from pathlib import Path

import cv2
import matplotlib
matplotlib.use("Agg")
import matplotlib.dates as mdates  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import torch  # noqa: E402
from PIL import Image, ImageDraw, ImageFont, ImageOps  # noqa: E402

from dwarph_cv.ring import detect_ring, ring_coverage, ring_outline, undistort  # noqa: E402
from dwarph_cv.segmentation.model_utils import load_checkpoint, predict_prob  # noqa: E402
from dwarph_cv.segmentation.weights import resolve_weights  # noqa: E402

TIME_RE = re.compile(r"(\d{8}_\d{6})")
GREEN = np.array([110, 190, 70], np.uint8)
BACKGROUND = np.array([18, 18, 18], np.uint8)
RING = (230, 60, 60)


def read_meta(image: Path) -> dict | None:
    """The device's metadata of one image, or None if it is missing or unreadable."""
    try:
        return json.loads(image.with_suffix(".json").read_text())
    except (OSError, ValueError):
        return None


def setpoints(meta: dict | None) -> dict | None:
    try:
        light = meta["light"]["scheduled"]
        return {"temp": float(meta["environment"]["temperature_setpoint"]),
                "red": float(light["red"]), "blue": float(light["blue"]), "white": float(light["white"])}
    except (TypeError, KeyError, ValueError):
        return None


def night_spans(device_dir: Path, t0: dt.datetime, t1: dt.datetime):
    """(start, end) of the periods when the program had every light off."""
    spans, start, last = [], None, None
    for p in sorted(device_dir.glob("*/*.jpg")):
        m = TIME_RE.match(p.name)
        if not m:
            continue
        t = dt.datetime.strptime(m.group(1), "%Y%m%d_%H%M%S")
        if not t0 <= t <= t1:
            continue
        sp = setpoints(read_meta(p))
        if sp is None:
            continue
        dark = sp["red"] + sp["blue"] + sp["white"] <= 1e-6
        if dark and start is None:
            start = t
        elif not dark and start is not None:
            spans.append((start, t))
            start = None
        last = t
    if start is not None:
        spans.append((start, last))
    return spans


def pick_frames(device_dir: Path, start: dt.datetime, every: dt.timedelta,
                tolerance=dt.timedelta(minutes=10)):
    files = []
    for p in sorted(device_dir.glob("*/*.jpg")):
        m = TIME_RE.match(p.name)
        if m and p.stat().st_size > 0:
            t = dt.datetime.strptime(m.group(1), "%Y%m%d_%H%M%S")
            if t >= start:
                files.append((t, p))
    picked, target, i = [], start, 0
    while files and target <= files[-1][0]:
        while i + 1 < len(files) and abs(files[i + 1][0] - target) <= abs(files[i][0] - target):
            i += 1
        if abs(files[i][0] - target) < tolerance:
            picked.append(files[i])
        target += every
    return picked


def font(size):
    try:
        return ImageFont.truetype("DejaVuSans-Bold.ttf", size)
    except OSError:
        return ImageFont.load_default()


def label(img: Image.Image, text: str, xy, f, anchor="la") -> None:
    d = ImageDraw.Draw(img)
    x0, y0, x1, y1 = d.textbbox(xy, text, font=f, anchor=anchor)
    d.rounded_rectangle((x0 - 10, y0 - 7, x1 + 10, y1 + 7), 8, fill=(0, 0, 0))
    d.text(xy, text, font=f, fill=(255, 255, 255), anchor=anchor)


def intro_frame(path: Path, caption: str, size: tuple[int, int]) -> Image.Image:
    with Image.open(path) as im:
        photo = ImageOps.exif_transpose(im).convert("RGB")
    W, H = size
    caption_h = 70
    photo = ImageOps.contain(photo, (W, H - caption_h), Image.LANCZOS)
    canvas = Image.new("RGB", size, (18, 18, 18))
    canvas.paste(photo, ((W - photo.width) // 2, (H - caption_h - photo.height) // 2))
    label(canvas, caption, (W // 2, H - caption_h // 2), font(26), anchor="mm")
    return canvas


def curve_frame(times, cover, k, width, height, nights=()):
    fig = plt.figure(figsize=(width / 100, height / 100), dpi=100)
    ax = fig.add_axes([0.08, 0.2, 0.89, 0.72])
    ax.set_facecolor("white")
    for a, b in nights:
        ax.axvspan(a, b, color="#e4e6e9", lw=0, zorder=0)
    ax.plot(times[: k + 1], cover[: k + 1], color="#3f8f29", lw=2)
    ax.plot(times[k], cover[k], "o", color="#3f8f29", ms=7)
    ax.set_xlim(times[0], times[-1])
    ax.set_ylim(0, min(100, max(cover) * 1.1))
    ax.set_ylabel("ring covered (%)")
    ax.xaxis.set_major_locator(mdates.DayLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%d %b"))
    ax.grid(alpha=0.3)
    if nights:
        ax.text(0.995, 1.02, "grey: night (lights off)", transform=ax.transAxes, ha="right", va="bottom",
                fontsize=9, color="#6b7280")
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=100)
    plt.close(fig)
    return Image.open(buf).convert("RGB").resize((width, height))


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--device-dir", type=Path, required=True)
    p.add_argument("--start", required=True, help="YYYYMMDD_HHMMSS")
    p.add_argument("--every-min", type=float, default=60)
    p.add_argument("--weights", default="unet_r34_duckweed", help="released model name or a .pt file")
    p.add_argument("--intro", nargs=2, action="append", default=[], metavar=("IMAGE", "CAPTION"),
                   help="title frame shown before the time-lapse (repeatable)")
    p.add_argument("--intro-ms", type=int, default=3000)
    p.add_argument("--surface-offset-mm", type=float, default=0.0,
                   help="water surface below the ring's inner edge (see dwarph_cv.ring.coverage)")
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--panel", type=int, default=512, help="size of the image and mask panels (px)")
    p.add_argument("--curve-height", type=int, default=280)
    p.add_argument("--frame-ms", type=int, default=100)
    p.add_argument("--quality", type=int, default=70)
    p.add_argument("--csv", type=Path, help="also write the coverage time series here")
    a = p.parse_args(argv)

    device_dir = a.device_dir.expanduser().resolve()
    out = a.out.expanduser().resolve()
    if device_dir in out.parents:
        raise SystemExit("REFUSING: output inside the image folder")
    start = dt.datetime.strptime(a.start, "%Y%m%d_%H%M%S")
    frames_in = pick_frames(device_dir, start, dt.timedelta(minutes=a.every_min))
    print(f"{len(frames_in)} frames: {frames_in[0][0]} -> {frames_in[-1][0]}")

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model, ck = load_checkpoint(resolve_weights(a.weights), device)
    S = a.panel
    panels, cover, rows, last_ring, n_carried, sets = [], [], [], None, 0, []
    for t, path in frames_in:
        sets.append(setpoints(read_meta(path)))
        bgr = cv2.imread(str(path))
        rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
        mask = predict_prob(model, rgb, device) >= ck["threshold"]
        ring = detect_ring(bgr, name=path.name, timestamp=t)
        if ring["status"] == "ok":
            last_ring = ring
        elif last_ring is not None:
            ring, n_carried = last_ring, n_carried + 1
        c = ring_coverage(mask.astype(np.uint8), ring, surface_offset=a.surface_offset_mm / 1000)
        cover.append(100 * c["ring_coverage"])
        rows.append((t, path.name, ring["status"], c["ring_coverage"], float(mask.mean())))

        und_rgb = undistort(rgb)
        und_mask = undistort(mask.astype(np.uint8), interpolation=cv2.INTER_NEAREST) > 0
        shown = Image.fromarray(und_rgb).resize((S, S), Image.LANCZOS)
        m_img = np.where(und_mask[..., None], GREEN, BACKGROUND)
        outline = ring_outline(ring)
        if outline is not None:
            cv2.ellipse(m_img, outline, RING, thickness=6)
        panels.append((shown, Image.fromarray(m_img).resize((S, S), Image.BILINEAR)))
    if n_carried:
        print(f"ring not found in {n_carried} frames: the previous ring was used")
    times = [t for t, _ in frames_in]
    nights = night_spans(device_dir, times[0], times[-1])
    if a.csv:
        a.csv.write_text("timestamp,image,ring_status,ring_coverage,image_coverage\n" + "".join(
            f"{t:%Y-%m-%d %H:%M:%S},{n},{s},{rc:.6f},{ic:.6f}\n" for t, n, s, rc, ic in rows))

    size = (2 * S, S + a.curve_height)
    frames = [intro_frame(Path(img), cap, size) for img, cap in a.intro]
    durations = [a.intro_ms] * len(frames)
    f_big, f_small = font(22), font(18)
    for k, (t, (shown, m)) in enumerate(zip(times, panels)):
        canvas = Image.new("RGB", size, (255, 255, 255))
        canvas.paste(shown, (0, 0))
        canvas.paste(m, (S, 0))
        label(canvas, f"{t:%d %b  %H:%M}", (20, S - 38), f_big)
        if sets[k] is not None:
            sp = sets[k]
            label(canvas, f"set {sp['temp']:.0f} °C   light: red {100 * sp['red']:.0f} %, blue {100 * sp['blue']:.0f} %",
                  (20, S - 84), f_small)
        label(canvas, "image", (20, 16), f_small)
        label(canvas, f"model mask: {cover[k]:.0f} % of the ring", (S + 20, 16), f_small)
        canvas.paste(curve_frame(times, cover, k, 2 * S, a.curve_height, nights), (0, S))
        frames.append(canvas)
        durations.append(a.frame_ms)
    durations[-1] = 2000
    frames[0].save(out, save_all=True, append_images=frames[1:], duration=durations, loop=0,
                   quality=a.quality, method=6, minimize_size=True)
    print(f"{out}: {len(frames)} frames ({len(a.intro)} intro), {out.stat().st_size / 1e6:.2f} MB, "
          f"ring coverage {cover[0]:.1f} % -> {cover[-1]:.1f} %")


if __name__ == "__main__":
    main()
