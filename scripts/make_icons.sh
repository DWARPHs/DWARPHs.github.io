#!/bin/sh
# Make the site icons from assets/DWARPH-logo.svg (re-run after changing the logo).
# Needs rsvg-convert and ImageMagick (magick). Writes assets/icons/.
set -eu
cd "$(dirname "$0")/.."
LOGO=assets/DWARPH-logo.svg
OUT=assets/icons
mkdir -p "$OUT"
TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT

# square, transparent, logo centred with a small margin
square() {  # size margin_percent output
  inner=$(( $1 * (100 - 2 * $2) / 100 ))
  rsvg-convert -w "$inner" -h "$inner" --keep-aspect-ratio "$LOGO" -o "$TMP/l.png"
  magick "$TMP/l.png" -background none -gravity center -extent "$1x$1" "$3"
}

# SVG favicon: the logo with a square viewBox (sharp at every size in modern browsers)
python3 - "$LOGO" "$OUT/favicon.svg" <<'PY'
import re, sys
s = open(sys.argv[1]).read()
m = re.search(r'viewBox="([\d.\-]+) ([\d.\-]+) ([\d.]+) ([\d.]+)"', s)
x, y, w, h = map(float, m.groups())
side = max(w, h) * 1.04
vb = f'viewBox="{x - (side - w) / 2:g} {y - (side - h) / 2:g} {side:g} {side:g}"'
s = s.replace(m.group(0), vb, 1)
s = re.sub(r'(<svg\b[^>]*?)\swidth="[^"]*"', r'\1 width="512"', s, count=1)
s = re.sub(r'(<svg\b[^>]*?)\sheight="[^"]*"', r'\1 height="512"', s, count=1)
open(sys.argv[2], "w").write(s)
PY

for n in 16 32 48 64; do square "$n" 2 "$TMP/f$n.png"; done
magick "$TMP/f16.png" "$TMP/f32.png" "$TMP/f48.png" "$TMP/f64.png" "$OUT/favicon.ico"
cp "$TMP/f32.png" "$OUT/favicon-32.png"
square 192 4 "$OUT/icon-192.png"
square 512 4 "$OUT/icon-512.png"
square 160 0 "$TMP/apple.png"   # iOS draws transparency as black: white tile
magick "$TMP/apple.png" -background white -gravity center -extent 180x180 -flatten "$OUT/apple-touch-icon.png"
square 120 0 "$OUT/logo-sidebar.png"

# link preview image (1200x630): logo and title on white
rsvg-convert -h 460 --keep-aspect-ratio "$LOGO" -o "$TMP/og_logo.png"
magick -size 1200x630 xc:white "$TMP/og_logo.png" -gravity west -geometry +70+0 -composite \
  -font DejaVu-Sans-Bold -pointsize 92 -fill '#1d2b1f' -gravity northwest -annotate +620+190 'DWARPH' \
  -font DejaVu-Sans -pointsize 34 -fill '#4a5a4c' -annotate +624+310 'an open platform for' \
  -annotate +624+356 'automated duckweed' -annotate +624+402 'phenotyping' \
  "$OUT/og-image.png"
ls -l "$OUT"
