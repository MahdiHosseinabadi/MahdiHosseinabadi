"""Compose the ASCII portrait and info card into one responsive SVG.

The portrait and info card are combined into a single SVG so they stay
side-by-side and scale together instead of wrapping into separate rows.

    python scripts/compose_whoami.py

Output:
    whoami.svg
"""

import math
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent

# Overall width of the combined image.
TARGET_W = 1100

# Space between portrait and information card.
GAP = 18

# Layout weights:
# portrait = 40%
# info card = 60%
PANELS = [
    ("avi-ascii.svg", 45),
    ("info-card.svg", 55),
]


def split_svg(path: Path) -> tuple[float, float, str]:
    """Return SVG viewBox width, height and inner SVG content."""

    text = path.read_text(encoding="utf-8")

    root = re.match(r"<svg\b[^>]*>", text)

    if not root:
        raise SystemExit(
            f"{path.name}: no root <svg> tag"
        )

    view_box = re.search(
        r'viewBox="([^"]+)"',
        root.group(0),
    )

    if not view_box:
        raise SystemExit(
            f"{path.name}: root <svg> has no viewBox"
        )

    values = (
        view_box.group(1)
        .replace(",", " ")
        .split()
    )

    if len(values) != 4:
        raise SystemExit(
            f"{path.name}: invalid viewBox"
        )

    _, _, vw, vh = (
        float(value)
        for value in values
    )

    inner = text[root.end():]

    closing = inner.rfind("</svg>")

    if closing == -1:
        raise SystemExit(
            f"{path.name}: closing </svg> not found"
        )

    inner = inner[:closing]

    return vw, vh, inner


def main() -> int:

    panels = []

    # ---------------------------------------------------------
    # Load all SVG panels
    # ---------------------------------------------------------

    for filename, weight in PANELS:

        path = ROOT / filename

        if not path.exists():
            raise SystemExit(
                f"{filename} missing -- generate it first"
            )

        vw, vh, inner = split_svg(path)

        panels.append(
            {
                "vw": vw,
                "vh": vh,
                "inner": inner,
                "weight": weight,
            }
        )

    # ---------------------------------------------------------
    # Calculate available width
    # ---------------------------------------------------------

    usable_width = (
        TARGET_W
        - GAP * (len(panels) - 1)
    )

    total_weight = sum(
        panel["weight"]
        for panel in panels
    )

    # ---------------------------------------------------------
    # Calculate panel dimensions
    # ---------------------------------------------------------

    for panel in panels:

        panel["w"] = (
            usable_width
            * panel["weight"]
            / total_weight
        )

        panel["h"] = (
            panel["vh"]
            / panel["vw"]
            * panel["w"]
        )

    # The combined SVG height follows the tallest panel.
    height = math.ceil(
        max(
            panel["h"]
            for panel in panels
        )
    )

    # ---------------------------------------------------------
    # Build combined SVG
    # ---------------------------------------------------------

    body = []

    x = 0.0

    for panel in panels:

        body.append(
            f"""
            <svg
                x="{x:.2f}"
                y="0"
                width="{panel["w"]:.2f}"
                height="{panel["h"]:.2f}"
                viewBox="0 0 {panel["vw"]:g} {panel["vh"]:g}"
                preserveAspectRatio="xMidYMid meet"
                overflow="visible"
            >
                {panel["inner"]}
            </svg>
            """
        )

        x += (
            panel["w"]
            + GAP
        )

    # ---------------------------------------------------------
    # Final SVG
    # ---------------------------------------------------------

    output = f"""
<svg
    xmlns="http://www.w3.org/2000/svg"
    width="{TARGET_W}"
    height="{height}"
    viewBox="0 0 {TARGET_W} {height}"
    role="img"
    aria-label="Mahdi Hosseinabadi ASCII portrait and profile information"
>
    {"".join(body)}
</svg>
""".strip()

    destination = ROOT / "whoami.svg"

    destination.write_text(
        output,
        encoding="utf-8",
    )

    print(
        f"wrote {destination} "
        f"({TARGET_W}x{height})"
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
