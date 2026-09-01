"""Generate an animated neofetch-style profile info card."""

import os
import re
from pathlib import Path
from xml.sax.saxutils import escape


ROOT = Path(__file__).resolve().parent.parent


# ---------------------------------------------------------------------------
# Layout
# ---------------------------------------------------------------------------

ASCII_COL_W = 495
CARD_COL_W = 605

W = 760
PAD = 24

BAR_H = 42

FONT = 21
LINE_H = 40
MAX_LINE_H = 43

BLOCK_GAP = 12
WRAP = 50


# ---------------------------------------------------------------------------
# Profile information
# ---------------------------------------------------------------------------

USER = "Mahdi"
HOST = "MahdiHosseinabadi"

ROWS = [
    (
        "Now",
        "Building Unity Games + Front-end work + Back-end work + "
        "UI design + Provision of accounting services",
    ),
    (
        "Stack",
        "C / C++ | C# | Unity | JavaScript | Python | "
        "Sass | Next.js | Git | Office software",
    ),
    (
        "Highlights",
        "Design-to-code handoff, smart contracts, data-heavy UIs",
    ),
    (
        "Learning",
        "Game Development, Website Design",
    ),
    (
        "Reach",
        "@MahdiHosseinabadii · instagram.com/MahdiHosseinabadii",
    ),
]


# ---------------------------------------------------------------------------
# Colors
# ---------------------------------------------------------------------------

BG = "#0d1117"
BAR = "#161b22"
STROKE = "#21262d"

KEY = "#39d353"
VAL = "#c9d1d9"
DIM = "#8b949e"
ACCENT = "#58a6ff"

SWATCH = [
    "#161b22",
    "#0e4429",
    "#006d32",
    "#26a641",
    "#39d353",
    "#69f0a0",
    "#58a6ff",
    "#c9d1d9",
]


# ---------------------------------------------------------------------------
# Font
# ---------------------------------------------------------------------------

MONO = (
    "ui-monospace, SFMono-Regular, Menlo, Consolas, "
    '&quot;DejaVu Sans Mono&quot;, monospace'
)


# ---------------------------------------------------------------------------
# Animation
# ---------------------------------------------------------------------------

# مدت زمان ظاهر شدن هر خط
ANIMATION_DURATION = 1.2

# فاصله شروع هر خط
ANIMATION_DELAY = 0.12

# مدت زمان کامل یک چرخه
LOOP_DURATION = 10.0

# مدت مکث بعد از کامل شدن
HOLD_DURATION = 4.0


def wrap(text: str, width: int) -> list[str]:
    """Wrap text into lines."""

    lines = []
    line = ""

    for word in text.split():
        candidate = f"{line} {word}".strip()

        if len(candidate) > width and line:
            lines.append(line)
            line = word
        else:
            line = candidate

    if line:
        lines.append(line)

    return lines


def build(target_h: float | None = None) -> str:
    """Build the animated SVG."""

    static = os.environ.get("STATIC") == "1"

    key_w = max(
        len(key)
        for key, _ in ROWS
    ) + 2

    # -----------------------------------------------------------------------
    # Prepare content
    # -----------------------------------------------------------------------

    items: list[tuple[str, str, str]] = []

    items.append(
        (
            "",
            f"{USER}@{HOST}",
            "host",
        )
    )

    items.append(
        (
            "",
            "-" * (len(USER) + len(HOST) + 1),
            "rule",
        )
    )

    for key, value in ROWS:
        wrapped = wrap(value, WRAP)

        for index, chunk in enumerate(wrapped):
            items.append(
                (
                    key if index == 0 else "",
                    chunk,
                    "row",
                )
            )

    # -----------------------------------------------------------------------
    # Calculate height
    # -----------------------------------------------------------------------

    body_top = (
        BAR_H
        + BLOCK_GAP
        + PAD / 2
    )

    chrome = (
        body_top
        + BLOCK_GAP
        + 40
        + PAD / 2
    )

    line_h = LINE_H

    height = int(
        chrome
        + len(items) * LINE_H
    )

    if target_h and target_h > height:
        line_h = min(
            MAX_LINE_H,
            (target_h - chrome) / len(items),
        )

        height = int(target_h)

    # -----------------------------------------------------------------------
    # SVG parts
    # -----------------------------------------------------------------------

    parts = [
        # Background
        f'<rect '
        f'width="{W}" '
        f'height="{height}" '
        f'rx="10" '
        f'fill="{BG}"/>',

        # Top bar
        f'<path '
        f'd="M0 10a10 10 0 0 1 10-10'
        f'h{W - 20}'
        f'a10 10 0 0 1 10 10'
        f'v{BAR_H - 10}'
        f'H0z" '
        f'fill="{BAR}"/>',

        # Divider
        f'<line '
        f'x1="0" '
        f'y1="{BAR_H}" '
        f'x2="{W}" '
        f'y2="{BAR_H}" '
        f'stroke="{STROKE}"/>',

        # Window buttons
        f'<circle '
        f'cx="24" '
        f'cy="{BAR_H / 2}" '
        f'r="6" '
        f'fill="#ff5f56"/>',

        f'<circle '
        f'cx="46" '
        f'cy="{BAR_H / 2}" '
        f'r="6" '
        f'fill="#ffbd2e"/>',

        f'<circle '
        f'cx="68" '
        f'cy="{BAR_H / 2}" '
        f'r="6" '
        f'fill="#27c93f"/>',

        # Terminal title
        f'<text '
        f'x="{W / 2}" '
        f'y="{BAR_H / 2 + 5}" '
        f'text-anchor="middle" '
        f'font-size="13" '
        f'fill="{DIM}">'
        f'{escape(USER)}@{escape(HOST)}: ~ — neofetch'
        f'</text>',
    ]

    # -----------------------------------------------------------------------
    # Content rows
    # -----------------------------------------------------------------------

    for index, (key, value, kind) in enumerate(items):

        y = (
            body_top
            + index * line_h
            + FONT
        )

        if static:
            animation_style = ""
            animation_class = ""
        else:
            delay = (
                index
                * ANIMATION_DELAY
            )

            animation_style = (
                f' style="'
                f'animation-delay:{delay:.2f}s"'
            )

            animation_class = ' class="animated-line"'

        # ---------------------------------------------------------------
        # Host
        # ---------------------------------------------------------------

        if kind == "host":

            parts.append(
                f'<text'
                f'{animation_class}'
                f'{animation_style} '
                f'x="{PAD}" '
                f'y="{y:.1f}" '
                f'fill="{KEY}" '
                f'font-weight="700">'
                f'{escape(value)}'
                f'</text>'
            )

        # ---------------------------------------------------------------
        # Separator
        # ---------------------------------------------------------------

        elif kind == "rule":

            parts.append(
                f'<text'
                f'{animation_class}'
                f'{animation_style} '
                f'x="{PAD}" '
                f'y="{y:.1f}" '
                f'fill="{DIM}">'
                f'{escape(value)}'
                f'</text>'
            )

        # ---------------------------------------------------------------
        # Normal row
        # ---------------------------------------------------------------

        else:

            label = (
                f"{key}:".ljust(key_w)
                if key
                else " " * key_w
            )

            parts.append(
                f'<text'
                f'{animation_class}'
                f'{animation_style} '
                f'x="{PAD}" '
                f'y="{y:.1f}" '
                f'xml:space="preserve">'

                f'<tspan '
                f'fill="{KEY}" '
                f'font-weight="700">'
                f'{escape(label)}'
                f'</tspan>'

                f'<tspan '
                f'fill="{VAL if key else DIM}">'
                f'{escape(value)}'
                f'</tspan>'

                f'</text>'
            )

    # -----------------------------------------------------------------------
    # Color swatches
    # -----------------------------------------------------------------------

    swatch_y = (
        height
        - PAD
        - 12
    )

    for index, color in enumerate(SWATCH):

        if static:
            animation_style = ""
            animation_class = ""
        else:
            delay = (
                len(items)
                * ANIMATION_DELAY
                + index * 0.08
            )

            animation_style = (
                f' style="'
                f'animation-delay:{delay:.2f}s"'
            )

            animation_class = ' class="animated-line"'

        parts.append(
            f'<rect'
            f'{animation_class}'
            f'{animation_style} '
            f'x="{PAD + index * 26}" '
            f'y="{swatch_y}" '
            f'width="20" '
            f'height="20" '
            f'rx="4" '
            f'fill="{color}" '
            f'stroke="{STROKE}"/>'
        )

    # -----------------------------------------------------------------------
    # Footer command
    # -----------------------------------------------------------------------

    parts.append(
        f'<text '
        f'x="{W - PAD}" '
        f'y="{swatch_y + 15}" '
        f'text-anchor="end" '
        f'font-size="12" '
        f'fill="{ACCENT}">'
        f'./whoami --verbose'
        f'</text>'
    )

    # -----------------------------------------------------------------------
    # CSS animation
    # -----------------------------------------------------------------------

    if static:

        style = ""

    else:

        style = f"""
<style>

@keyframes neofetch-in-out {{
    0% {{
        opacity: 0;
        transform: translateX(-20px);
    }}

    12% {{
        opacity: 1;
        transform: translateX(0);
    }}

    65% {{
        opacity: 1;
        transform: translateX(0);
    }}

    100% {{
        opacity: 0;
        transform: translateX(20px);
    }}
}}

.animated-line {{
    animation:
        neofetch-in-out
        {LOOP_DURATION:.1f}s
        ease-in-out
        infinite;
}}

@media (prefers-reduced-motion: reduce) {{
    .animated-line {{
        animation: none;
        opacity: 1;
        transform: none;
    }}
}}

</style>
"""

    # -----------------------------------------------------------------------
    # Final SVG
    # -----------------------------------------------------------------------

    return (
        f'<svg '
        f'xmlns="http://www.w3.org/2000/svg" '
        f'width="{W}" '
        f'height="{height}" '
        f'viewBox="0 0 {W} {height}" '
        f'role="img" '
        f'aria-label="Profile info card">'

        f'{style}'

        f'<g '
        f'font-family="{MONO}" '
        f'font-size="{FONT}">'

        f'{"".join(parts)}'

        f'</g>'

        f'</svg>'
    )


def match_portrait_height() -> float | None:
    """Match the card height to the ASCII portrait."""

    portrait = ROOT / "avi-ascii.svg"

    if not portrait.exists():
        return None

    head = portrait.read_text(
        encoding="utf-8"
    )[:400]

    width_match = re.search(
        r'\bwidth="([\d.]+)"',
        head,
    )

    height_match = re.search(
        r'\bheight="([\d.]+)"',
        head,
    )

    if not width_match or not height_match:
        return None

    portrait_width = float(
        width_match.group(1)
    )

    portrait_height = float(
        height_match.group(1)
    )

    rendered_height = (
        portrait_height
        / portrait_width
        * ASCII_COL_W
    )

    return (
        rendered_height
        / CARD_COL_W
        * W
    )


def main() -> int:
    """Generate info-card.svg."""

    output = ROOT / "info-card.svg"

    target_height = match_portrait_height()

    svg = build(target_height)

    output.write_text(
        svg,
        encoding="utf-8",
    )

    print(
        f"wrote {output}"
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())