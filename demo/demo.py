"""Builds demo/pies-2.gif: the band drawn frame by frame, real photos laid into its thumbnail.

The band lives inside Claude Code's own UI, which no script can drive, so the terminal is
drawn here as asciicast v2 and rendered by agg with the thumbnail left magenta; ffmpeg then
finds the magenta box and lays each photo over it while that snap is on screen.
"""

import json
import subprocess
import tempfile
from pathlib import Path

COLUMNS, ROWS = 80, 22
THUMB_COLUMNS, THUMB_ROWS = 32, 9
HOLD_LIMIT = 4

DEMO = Path(__file__).resolve().parent
TARGET = DEMO / "pies-2.gif"

RESET = "\x1b[0m"
DIM = "\x1b[2m"
BOLD = "\x1b[1m"
INVERSE = "\x1b[7m"
ACCENT = "\x1b[38;5;209m"
USER_LINE = "\x1b[48;5;237m"
KEY = "\x1b[48;5;201m"

THEME = "1e1e2e,cdd6f4,45475a,f38ba8,a6e3a1,f9e2af,89b4fa,f5c2e7,94e2d5,bac2de,585b70,f38ba8,a6e3a1,f9e2af,89b4fa,f5c2e7,94e2d5,a6adc8"

ACTS = [
    (
        "whole",
        "is my pie done?",
        [
            "Yes: the lattice is golden and the berries bubble through.",
            "Give it an hour to cool, or it will run when you slice it.",
        ],
    ),
    (
        "slice",
        "an hour later. how is it looking?",
        [
            "Cooled, and mostly gone: one slice left, and the fork is standing by.",
            "Also, an hour ago it was a white dish. Is there a second pie?",
        ],
    ),
]

PLACEHOLDER = "Ask Claude anything"
SNAP = f"{ACCENT}[ 📷 snap ]{RESET}"
PRESSED = f"{INVERSE}{ACCENT}[ 📷 snap ]{RESET}"


def rule() -> str:
    return DIM + "─" * COLUMNS + RESET


def prompt(text: str = "") -> list[str]:
    typed = f"{text}{INVERSE} {RESET}" if text else DIM + PLACEHOLDER + RESET
    return [rule(), f"{ACCENT}❯{RESET} {typed}", rule(), DIM + "  ? for shortcuts" + RESET]


def thumbnail() -> list[str]:
    side = ["", DIM + "goes with the next message" + RESET, f"{ACCENT}[ retake ]{RESET}", f"{ACCENT}[ drop ]{RESET}"]
    rows = [DIM + "╭" + "─" * THUMB_COLUMNS + "╮" + RESET]
    rows += [DIM + "│" + RESET + KEY + " " * THUMB_COLUMNS + RESET + DIM + "│" + RESET] * THUMB_ROWS
    rows += [DIM + "╰" + "─" * THUMB_COLUMNS + "╯" + RESET]
    return [row + " " + (side[i] if i < len(side) else "") for i, row in enumerate(rows)]


def screen(lines: list[str]) -> str:
    padded = [""] * (ROWS - len(lines)) + lines
    return "\x1b[?25l\x1b[2J\x1b[H" + "\r\n".join(padded[-ROWS:])


def record() -> tuple[list[list], list[tuple[str, float, float]]]:
    events: list[list] = []
    windows: list[tuple[str, float, float]] = []
    clock = 0.0

    def show(lines: list[str], hold: float) -> None:
        nonlocal clock
        events.append([round(clock, 3), "o", screen(lines)])
        clock += hold

    history: list[str] = []
    for n, (photo, question, answer) in enumerate(ACTS, start=1):
        show(history + [SNAP] + prompt(), 1.4)
        show(history + [PRESSED] + prompt(), 0.35)
        show(history + [DIM + "snapping…" + RESET] + prompt(), 1.2)
        shown_at = clock
        show(history + thumbnail() + prompt(), 1.6)
        for i in range(1, len(question) + 1):
            show(history + thumbnail() + prompt(question[:i]), 0.06)
        show(history + thumbnail() + prompt(question), 0.7)
        windows.append((photo, shown_at, clock))

        history += [USER_LINE + f"> {question}".ljust(COLUMNS) + RESET, ""]
        show(history + [SNAP] + prompt(), 0.8)
        history += [
            f"{ACCENT}●{RESET} {BOLD}Read{RESET}(claude-cam/frame-{n}.jpg)",
            DIM + "  ⎿  Read image (184KB)" + RESET,
            "",
        ]
        show(history + [SNAP] + prompt(), 0.9)
        history += [f"{ACCENT}●{RESET} {answer[0]}", f"  {answer[1]}", ""]
        show(history + [SNAP] + prompt(), HOLD_LIMIT)

    show(history + [SNAP] + prompt(), 0.0)
    return events, windows


def ffmpeg(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["ffmpeg", "-hide_banner", "-y", *args], capture_output=True, text=True, check=True)


def key_box(gif: Path, at: float) -> tuple[int, int, int, int]:
    probe = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "stream=width,height", "-of", "csv=p=0", str(gif)],
        capture_output=True, text=True, check=True,
    )
    width, _ = map(int, probe.stdout.strip().split(","))
    frame = subprocess.run(
        ["ffmpeg", "-v", "error", "-ss", f"{at:.2f}", "-i", str(gif), "-frames:v", "1", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
        capture_output=True, check=True,
    ).stdout
    keyed = [
        (i // 3 % width, i // 3 // width)
        for i in range(0, len(frame), 3)
        if frame[i] > 200 and frame[i + 1] < 60 and frame[i + 2] > 200
    ]
    xs, ys = [x for x, _ in keyed], [y for _, y in keyed]
    return max(xs) - min(xs) + 1, max(ys) - min(ys) + 1, min(xs), min(ys)


def main() -> int:
    events, windows = record()
    with tempfile.TemporaryDirectory() as tmp:
        cast, raw = Path(tmp) / "demo.cast", Path(tmp) / "raw.gif"
        header = {"version": 2, "width": COLUMNS, "height": ROWS, "env": {"SHELL": "/bin/zsh", "TERM": "xterm-256color"}}
        cast.write_text("\n".join(json.dumps(line) for line in [header, *events]) + "\n", encoding="utf8")
        subprocess.run(
            ["agg", "--font-size", "20", "--theme", THEME, "--idle-time-limit", str(HOLD_LIMIT), str(cast), str(raw)],
            capture_output=True, check=True,
        )

        w, h, x, y = key_box(raw, (windows[0][1] + windows[0][2]) / 2)
        inputs = ["-i", str(raw)]
        chain = []
        last = "0:v"
        for i, (photo, start, end) in enumerate(windows, start=1):
            inputs += ["-i", str(DEMO / "photos" / f"{photo}.jpg")]
            chain.append(f"[{i}:v]scale={w}:{h}:force_original_aspect_ratio=increase,crop={w}:{h}[p{i}]")
            chain.append(f"[{last}][p{i}]overlay={x}:{y}:format=rgb:enable='between(t,{start - 0.02:.3f},{end - 0.02:.3f})'[v{i}]")
            last = f"v{i}"
        chain.append(f"[{last}]split[a][b];[a]palettegen=stats_mode=full[pal];[b][pal]paletteuse=dither=sierra2_4a")
        ffmpeg(*inputs, "-filter_complex", ";".join(chain), str(TARGET))

    print(TARGET.relative_to(DEMO.parent))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
