"""Turn source-prepped.png into a looping self-typing ASCII portrait SVG."""

import argparse
import os
from pathlib import Path
from xml.sax.saxutils import escape

import numpy as np
from PIL import Image


ROOT = Path(__file__).resolve().parent.parent

RAMP = " .`:-=+*cs#%@"

CHAR_W = 6.0
LINE_H = 11.0
FONT_SIZE = 10.0

PAD_X = 16.0
PAD_Y = 16.0

BG = "#0d1117"
FG = "#c9d1d9"
CURSOR = "#39d353"

STAGGER = 0.055
ROW_DUR = 0.34
LOOP = 10.0


def to_grid(img: Image.Image, cols: int, max_rows: int) -> list[str]:
    """Convert an image into an ASCII character grid."""

    aspect = CHAR_W / LINE_H

    rows = max(
        1,
        round(img.height / img.width * cols * aspect),
    )

    rows = min(rows, max_rows)

    small = img.convert("L").resize(
        (cols, rows),
        Image.LANCZOS,
    )

    pixels = np.asarray(
        small,
        dtype=np.float32,
    )

    low, high = np.percentile(
        pixels,
        1.0,
    ), np.percentile(
        pixels,
        99.0,
    )

    if high > low:
        pixels = np.clip(
            (pixels - low) * (255.0 / (high - low)),
            0,
            255,
        )

    indexes = (
        ((255.0 - pixels) / 256.0 * len(RAMP))
        .astype(int)
    )

    indexes = np.clip(
        indexes,
        0,
        len(RAMP) - 1,
    )

    return [
        "".join(RAMP[index] for index in row)
        for row in indexes
    ]


def build_svg(lines: list[str], static: bool = False) -> str:
    """Build the animated SVG."""

    cols = max(len(line) for line in lines)

    width = PAD_X * 2 + cols * CHAR_W
    height = PAD_Y * 2 + len(lines) * LINE_H

    defs = []
    body = []

    for i, raw in enumerate(lines):
        stripped = raw.rstrip()

        if not stripped.strip():
            continue

        left = len(stripped) - len(stripped.lstrip())
        segment = stripped[left:]

        x0 = PAD_X + left * CHAR_W
        segment_width = len(segment) * CHAR_W
        y = PAD_Y + i * LINE_H

        begin = round(i * STAGGER, 3)

        if static:
            body.append(
                f'<text '
                f'x="{x0:.1f}" '
                f'y="{y + FONT_SIZE * 0.8:.1f}" '
                f'textLength="{segment_width:.1f}" '
                f'lengthAdjust="spacing" '
                f'xml:space="preserve">'
                f'{escape(segment)}'
                f'</text>'
            )
            continue

        clip_id = f"wipe{i}"

        animation_end = ROW_DUR / LOOP
        hold_end = min(
            animation_end + 0.05,
            0.99,
        )

        defs.append(
            f'<clipPath id="{clip_id}">'
            f'<rect '
            f'x="{x0:.1f}" '
            f'y="{y - 2:.1f}" '
            f'width="{segment_width:.1f}" '
            f'height="{LINE_H + 3:.1f}">'

            f'<animate '
            f'attributeName="width" '
            f'values="0;{segment_width:.1f};'
            f'{segment_width:.1f};0" '
            f'keyTimes="0;'
            f'{animation_end:.4f};'
            f'{hold_end:.4f};1" '
            f'begin="{begin}s" '
            f'dur="{LOOP}s" '
            f'repeatCount="indefinite"/>'

            f'</rect>'
            f'</clipPath>'
        )

        body.append(
            f'<g clip-path="url(#{clip_id})">'
            f'<text '
            f'x="{x0:.1f}" '
            f'y="{y + FONT_SIZE * 0.8:.1f}" '
            f'textLength="{segment_width:.1f}" '
            f'lengthAdjust="spacing" '
            f'xml:space="preserve">'
            f'{escape(segment)}'
            f'</text>'
            f'</g>'
        )

        body.append(
            f'<rect '
            f'x="{x0:.1f}" '
            f'y="{y:.1f}" '
            f'width="{CHAR_W:.1f}" '
            f'height="{LINE_H - 1:.1f}" '
            f'fill="{CURSOR}">'
f'<animate '
            f'attributeName="opacity" '
            f'values="0;0.9;0.9;0" '
            f'keyTimes="0;'
            f'{animation_end:.4f};'
            f'{hold_end:.4f};1" '
            f'begin="{begin}s" '
            f'dur="{LOOP}s" '
            f'repeatCount="indefinite"/>'

            f'<animate '
            f'attributeName="x" '
            f'values="{x0:.1f};'
            f'{x0 + segment_width:.1f};'
            f'{x0 + segment_width:.1f};'
            f'{x0:.1f}" '
            f'keyTimes="0;'
            f'{animation_end:.4f};'
            f'{hold_end:.4f};1" '
            f'begin="{begin}s" '
            f'dur="{LOOP}s" '
            f'repeatCount="indefinite"/>'

            f'</rect>'
        )

    return (
        f'<svg '
        f'xmlns="http://www.w3.org/2000/svg" '
        f'width="{width:.0f}" '
        f'height="{height:.0f}" '
        f'viewBox="0 0 {width:.0f} {height:.0f}" '
        f'role="img" '
        f'aria-label="ASCII portrait">'

        f'<defs>'
        f'{"".join(defs)}'
        f'</defs>'

        f'<rect '
        f'width="{width:.0f}" '
        f'height="{height:.0f}" '
        f'rx="10" '
        f'fill="{BG}"/>'

        f'<g '
        f'font-family="ui-monospace, SFMono-Regular, Menlo, '
        f'Consolas, &quot;DejaVu Sans Mono&quot;, monospace" '
        f'font-size="{FONT_SIZE}" '
        f'fill="{FG}">'

        f'{"".join(body)}'

        f'</g>'
        f'</svg>'
    )


def main() -> int:
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-i",
        "--input",
        default="source-prepped.png",
    )

    parser.add_argument(
        "-o",
        "--out",
        default="avi-ascii.svg",
    )

    parser.add_argument(
        "--cols",
        type=int,
        default=100,
    )

    parser.add_argument(
        "--max-rows",
        type=int,
        default=62,
    )

    args = parser.parse_args()

    input_path = Path(args.input)
    output_path = Path(args.out)

    src = (
        ROOT / input_path
        if not input_path.is_absolute()
        else input_path
    )

    dst = (
        ROOT / output_path
        if not output_path.is_absolute()
        else output_path
    )

    image = Image.open(src)

    lines = to_grid(
        image,
        args.cols,
        args.max_rows,
    )

    static = os.environ.get("STATIC") == "1"

    svg = build_svg(
        lines,
        static,
    )

    dst.write_text(
        svg,
        encoding="utf-8",
    )

    print(
        f"wrote {dst} "
        f"({args.cols} cols x {len(lines)} rows) "
        f"[loop={LOOP}s]"
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())