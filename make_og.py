#!/usr/bin/env python3
"""
make_og.py — generate a 1200x630 Open Graph image for winnowed.app.

Reuses the exported apple-touch-icon.png as the brand mark so the leaf
matches exactly what shows up as the favicon, iOS home-screen icon, and
browser tab everywhere else.

Usage
-----
Place this script in a directory that also contains apple-touch-icon.png,
then run:

    python3 make_og.py

Or point it explicitly at your icon and a different output location:

    python3 make_og.py --icon /path/to/apple-touch-icon.png --out /path/to/

Output
------
Writes og-image.png (1200x630 PNG) to the output directory.

Requirements
------------
- Pillow:  pip install Pillow
- Fraunces and Inter installed as system fonts. Download from Google Fonts:
    https://fonts.google.com/specimen/Fraunces
    https://fonts.google.com/specimen/Inter
  On macOS, open each TTF with Font Book and click Install.
"""

import argparse
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter


# ----------------------------------------------------------------------------
# Canvas and palette — drawn from winnowed.app's existing stylesheet
# ----------------------------------------------------------------------------

W, H = 1200, 630
PAD = 96                                # outer page margin

CREAM       = (250, 245, 236)           # #FAF5EC body background
CREAM_SHADE = (240, 232, 216)           # slightly deeper for vignette
INK         = (42, 42, 40)              # #2A2A28 primary text
MUTED       = (117, 110, 98)            # secondary text / URL
SAGE_DARK   = (74, 107, 62)             # #4A6B3E accent for italic line


# ----------------------------------------------------------------------------
# Font discovery
# ----------------------------------------------------------------------------

FONT_ROOTS = [
    Path.home() / "Library/Fonts",
    Path("/Library/Fonts"),
    Path("/System/Library/Fonts"),
    Path("/System/Library/Fonts/Supplemental"),
    Path("/usr/share/fonts"),
    Path("/usr/local/share/fonts"),
]


def find_first(patterns):
    """Return the first font file that matches any of the glob patterns."""
    for root in FONT_ROOTS:
        if not root.exists():
            continue
        for pattern in patterns:
            for match in root.rglob(pattern):
                return match
    return None


def load_fonts():
    """Locate Fraunces + Inter. Exit with instructions if either is missing."""
    fraunces_bold = find_first([
        "Fraunces-SemiBold.ttf",
        "Fraunces-Bold.ttf",
        "Fraunces-Medium.ttf",
    ])
    fraunces_italic = find_first([
        "Fraunces-SemiBoldItalic.ttf",
        "Fraunces-MediumItalic.ttf",
        "Fraunces-BoldItalic.ttf",
        "Fraunces-Italic.ttf",
    ])
    fraunces_regular = find_first(["Fraunces-Regular.ttf"])
    fraunces_variable = find_first([
        "Fraunces[opsz,SOFT,WONK,wght].ttf",
        "Fraunces[opsz,wght].ttf",
        "Fraunces-VariableFont*.ttf",
    ])

    inter_medium = find_first(["Inter-Medium.ttf", "Inter-Medium.otf"])
    inter_regular = find_first(["Inter-Regular.ttf", "Inter-Regular.otf"])
    inter_variable = find_first([
        "Inter[slnt,wght].ttf",
        "Inter-VariableFont*.ttf",
        "InterVariable.ttf",
    ])

    fraunces = fraunces_bold or fraunces_regular or fraunces_variable
    fraunces_it = fraunces_italic or fraunces_variable or fraunces
    inter = inter_medium or inter_regular or inter_variable

    missing = []
    if fraunces is None:
        missing.append("Fraunces — https://fonts.google.com/specimen/Fraunces")
    if inter is None:
        missing.append("Inter — https://fonts.google.com/specimen/Inter")

    if missing:
        print("Could not locate required fonts:")
        for m in missing:
            print(f"  • {m}")
        print()
        print("On macOS: download the TTFs, then open each with Font Book")
        print("and click Install. Re-run this script afterward.")
        sys.exit(1)

    return {
        "headline": fraunces,
        "headline_italic": fraunces_it,
        "body": inter,
    }


# ----------------------------------------------------------------------------
# Drawing helpers
# ----------------------------------------------------------------------------

def paint_background(img):
    """Flat cream fill with a soft off-center vignette for paper-like depth."""
    ImageDraw.Draw(img).rectangle([0, 0, W, H], fill=CREAM)

    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    od.ellipse(
        [int(W * 0.35), int(H * 0.40), int(W * 1.30), int(H * 1.50)],
        fill=(*CREAM_SHADE, 95),
    )
    overlay = overlay.filter(ImageFilter.GaussianBlur(radius=180))
    img.paste(overlay, (0, 0), overlay)


def paste_icon(img, icon_path, x, y, size):
    """Composite the brand icon at (x, y), resized to size×size."""
    icon = Image.open(icon_path).convert("RGBA")
    icon = icon.resize((size, size), Image.LANCZOS)
    img.paste(icon, (x, y), icon)


def measure(draw, text, font):
    bbox = draw.textbbox((0, 0), text, font=font)
    return bbox[2] - bbox[0], bbox[3] - bbox[1]


# ----------------------------------------------------------------------------
# Composition
# ----------------------------------------------------------------------------

def make_og(icon_path, out_path):
    fonts = load_fonts()

    img = Image.new("RGB", (W, H), CREAM)
    paint_background(img)
    draw = ImageDraw.Draw(img)

    f_brand = ImageFont.truetype(str(fonts["headline"]), 36)
    f_head = ImageFont.truetype(str(fonts["headline"]), 96)
    f_head_it = ImageFont.truetype(str(fonts["headline_italic"]), 96)
    f_tag = ImageFont.truetype(str(fonts["body"]), 24)
    f_url = ImageFont.truetype(str(fonts["body"]), 22)

    # Top-left: icon + wordmark
    icon_size = 72
    icon_x, icon_y = PAD, PAD - 12
    paste_icon(img, icon_path, icon_x, icon_y, icon_size)

    _, brand_h = measure(draw, "Winnowed", f_brand)
    draw.text(
        (icon_x + icon_size + 20, icon_y + (icon_size - brand_h) // 2 - 4),
        "Winnowed",
        font=f_brand,
        fill=INK,
    )

    # Middle: two-line headline, left-aligned and vertically centered
    line1 = "Keep what counts."
    line2 = "Cut the rest."
    _, h1 = measure(draw, line1, f_head)
    _, h2 = measure(draw, line2, f_head_it)
    line_gap = 14
    total = h1 + h2 + line_gap

    center_y = int(H * 0.50) - 20
    line1_y = center_y - total // 2
    line2_y = line1_y + h1 + line_gap

    draw.text((PAD, line1_y), line1, font=f_head, fill=INK)
    draw.text((PAD, line2_y), line2, font=f_head_it, fill=SAGE_DARK)

    # Tagline below the headline
    tagline = "A subscription tracker designed around a quarterly review ritual."
    draw.text(
        (PAD, line2_y + h2 + 44),
        tagline,
        font=f_tag,
        fill=MUTED,
    )

    # Bottom-right: URL
    url = "winnowed.app"
    uw, uh = measure(draw, url, f_url)
    draw.text(
        (W - PAD - uw, H - PAD - uh + 12),
        url,
        font=f_url,
        fill=SAGE_DARK,
    )

    img.save(out_path, optimize=True)
    print(f"Wrote {out_path} ({img.size[0]}×{img.size[1]})")


# ----------------------------------------------------------------------------
# Entry point
# ----------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Generate the winnowed.app Open Graph image."
    )
    parser.add_argument(
        "--icon",
        default="apple-touch-icon.png",
        help="Path to apple-touch-icon.png (default: ./apple-touch-icon.png)",
    )
    parser.add_argument(
        "--out",
        default=".",
        help="Output directory (default: current directory)",
    )
    args = parser.parse_args()

    icon_path = Path(args.icon).expanduser().resolve()
    if not icon_path.exists():
        print(f"Could not find icon at {icon_path}")
        print()
        print("Pass --icon /path/to/apple-touch-icon.png, or run this script")
        print("from the directory where apple-touch-icon.png already lives.")
        sys.exit(1)

    out_dir = Path(args.out).expanduser().resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "og-image.png"

    make_og(icon_path, out_path)


if __name__ == "__main__":
    main()
