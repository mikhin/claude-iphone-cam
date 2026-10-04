"""Writes demo/demo.cast: the snap, the thumbnail and the answer, drawn frame by frame.

The band lives inside Claude Code's own UI, which no script can drive, so the frames
are drawn here as the terminal would show them and written straight to asciicast v2.
"""

import json
import sys

COLUMNS, ROWS = 80, 18

RESET = "\x1b[0m"
DIM = "\x1b[2m"
BOLD = "\x1b[1m"
INVERSE = "\x1b[7m"
ACCENT = "\x1b[38;5;209m"
USER_LINE = "\x1b[48;5;237m"


def bg(code: int) -> str:
    return f"\x1b[48;5;{code}m"


PALETTE = {"t": bg(110), "p": bg(255), "c": bg(215), "l": bg(172)}

PIE = [
    "tttppppppppppppppppttt",
    "ttppcclcclccpppppppptt",
    "tpcclcclcclcpppppppppt",
    "tpcclcclcclcclcclcclpt",
    "tppcclcclcclcclcclcppt",
    "ttppcclcclcclcclccpptt",
    "tttppppppppppppppppttt",
]

PICTURE = ["".join(PALETTE[cell] + " " for cell in row.lower()) for row in PIE]

QUESTION = "is my pie done?"
ANSWER = [
    "Yes: the crust is golden and the filling bubbles through the lattice.",
    "Also, one slice is missing, so the taste test seems to be under way.",
]


def rule() -> str:
    return DIM + "─" * COLUMNS + RESET


def prompt(text: str, placeholder: bool = False) -> list[str]:
    typed = DIM + text + RESET if placeholder else text + INVERSE + " " + RESET
    return [rule(), f"{ACCENT}❯{RESET} {typed}", rule(), DIM + "  ? for shortcuts" + RESET]


def thumbnail(side: list[str]) -> list[str]:
    top = DIM + "╭" + "─" * 22 + "╮" + RESET
    bottom = DIM + "╰" + "─" * 22 + "╯" + RESET
    rows = [top] + [DIM + "│" + RESET + row + RESET + DIM + "│" + RESET for row in PICTURE] + [bottom]
    return [row + " " + (side[i] if i < len(side) else "") for i, row in enumerate(rows)]


def screen(lines: list[str]) -> str:
    padded = [""] * (ROWS - len(lines)) + lines
    return "\x1b[?25l\x1b[2J\x1b[H" + "\r\n".join(padded[-ROWS:])


def main() -> int:
    target = sys.argv[1]
    events: list[list] = []
    clock = 0.0

    def show(lines: list[str], hold: float) -> None:
        nonlocal clock
        events.append([round(clock, 3), "o", screen(lines)])
        clock += hold

    snap = f"{ACCENT}[ 📷 snap ]{RESET}"
    pressed = f"{INVERSE}{ACCENT}[ 📷 snap ]{RESET}"
    ready = [
        "",
        DIM + "goes with the next message" + RESET,
        f"{ACCENT}[ retake ]{RESET}",
        f"{ACCENT}[ drop ]{RESET}",
    ]

    show([snap] + prompt("Ask Claude anything", placeholder=True), 1.6)
    show([pressed] + prompt("Ask Claude anything", placeholder=True), 0.35)
    show([DIM + "snapping…" + RESET] + prompt("Ask Claude anything", placeholder=True), 1.4)
    show(thumbnail(ready) + prompt("Ask Claude anything", placeholder=True), 1.2)
    for i in range(1, len(QUESTION) + 1):
        show(thumbnail(ready) + prompt(QUESTION[:i]), 0.06)
    show(thumbnail(ready) + prompt(QUESTION), 0.8)

    asked = [USER_LINE + f"> {QUESTION}".ljust(COLUMNS) + RESET, ""]
    reading = asked + [
        f"{ACCENT}●{RESET} {BOLD}Read{RESET}(claude-cam/frame-1.jpg)",
        DIM + "  ⎿  Read image (62KB)" + RESET,
        "",
    ]
    show(asked + [snap] + prompt("Ask Claude anything", placeholder=True), 0.9)
    show(reading + [snap] + prompt("Ask Claude anything", placeholder=True), 1.0)
    answer = [f"{ACCENT}●{RESET} {ANSWER[0]}", f"  {ANSWER[1]}", ""]
    show(reading + answer + [snap] + prompt("Ask Claude anything", placeholder=True), 4.0)
    show(reading + answer + [snap] + prompt("Ask Claude anything", placeholder=True), 0.0)

    header = {"version": 2, "width": COLUMNS, "height": ROWS, "env": {"SHELL": "/bin/zsh", "TERM": "xterm-256color"}}
    with open(target, "w", encoding="utf8") as cast:
        cast.write(json.dumps(header) + "\n")
        for event in events:
            cast.write(json.dumps(event) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
