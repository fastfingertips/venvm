"""Terminal interaction helpers for venvm."""

from __future__ import annotations

import sys
from typing import Callable, Sequence, TypeVar


T = TypeVar("T")
InputFunction = Callable[[str], str]


def ask_yes_no(prompt: str, input_fn: InputFunction = input) -> bool:
    """Ask a yes/no question until a valid response is received."""

    while True:
        try:
            answer = input_fn(f"{prompt} [Y/n]: ").strip().casefold()
        except (EOFError, KeyboardInterrupt):
            print("\nOperation cancelled.", file=sys.stderr)
            return False
        if answer in {"", "y", "yes"}:
            return True
        if answer in {"n", "no"}:
            return False
        print("Please enter 'y' or 'n'.", file=sys.stderr)


def choose(
    prompt: str,
    options: Sequence[tuple[str, T]],
    input_fn: InputFunction = input,
) -> T | None:
    """Display numbered options and return the selected value."""

    print(prompt)
    for index, (label, _) in enumerate(options, start=1):
        print(f"  {index}. {label}")

    while True:
        try:
            answer = input_fn("Selection: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nOperation cancelled.", file=sys.stderr)
            return None
        try:
            selected = int(answer)
        except ValueError:
            selected = 0
        if 1 <= selected <= len(options):
            return options[selected - 1][1]
        print(f"Please enter a number from 1 to {len(options)}.", file=sys.stderr)
