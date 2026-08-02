"""Terminal interaction helpers for venvm."""

from __future__ import annotations

from contextlib import contextmanager
import os
import shutil
import sys
from typing import Callable, Iterator, Sequence, TextIO, TypeVar


T = TypeVar("T")
InputFunction = Callable[[str], str]
KeyFunction = Callable[[], str]


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


def _choose_numbered(
    prompt: str,
    options: Sequence[tuple[str, T]],
    input_fn: InputFunction,
) -> T | None:
    """Select an option using a line-based numbered prompt."""

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


def _read_windows_key() -> str:
    """Read and normalize one key from a Windows console."""

    import msvcrt

    key = msvcrt.getwch()
    if key in {"\x00", "\xe0"}:
        return {"H": "up", "P": "down"}.get(msvcrt.getwch(), "unknown")
    if key == "\r":
        return "enter"
    if key == "\x1b":
        return "escape"
    if key in {"\x08", "\x7f"}:
        return "backspace"
    if key == "\x03":
        raise KeyboardInterrupt
    return key


def _read_posix_key() -> str:
    """Read and normalize one key from a POSIX terminal."""

    import select

    key = sys.stdin.read(1)
    if key in {"\r", "\n"}:
        return "enter"
    if key in {"\x08", "\x7f"}:
        return "backspace"
    if key == "\x03":
        raise KeyboardInterrupt
    if key != "\x1b":
        return key

    if not select.select([sys.stdin], [], [], 0.05)[0]:
        return "escape"
    if sys.stdin.read(1) != "[":
        return "escape"
    return {"A": "up", "B": "down"}.get(sys.stdin.read(1), "unknown")


@contextmanager
def _terminal_key_reader() -> Iterator[KeyFunction]:
    """Yield a platform-specific key reader and restore terminal state."""

    if os.name == "nt":
        import ctypes
        from ctypes import wintypes

        kernel32 = ctypes.windll.kernel32
        kernel32.GetStdHandle.argtypes = [wintypes.DWORD]
        kernel32.GetStdHandle.restype = wintypes.HANDLE
        kernel32.GetConsoleMode.argtypes = [wintypes.HANDLE, wintypes.LPDWORD]
        kernel32.GetConsoleMode.restype = wintypes.BOOL
        kernel32.SetConsoleMode.argtypes = [wintypes.HANDLE, wintypes.DWORD]
        kernel32.SetConsoleMode.restype = wintypes.BOOL
        output_handle = kernel32.GetStdHandle(wintypes.DWORD(-11))
        previous_mode = wintypes.DWORD()
        if not kernel32.GetConsoleMode(output_handle, ctypes.byref(previous_mode)):
            raise OSError("cannot read Windows console mode")
        if not kernel32.SetConsoleMode(output_handle, previous_mode.value | 0x0004):
            raise OSError("cannot enable Windows virtual terminal mode")
        try:
            yield _read_windows_key
        finally:
            kernel32.SetConsoleMode(output_handle, previous_mode.value)
        return

    import termios
    import tty

    descriptor = sys.stdin.fileno()
    previous = termios.tcgetattr(descriptor)
    try:
        tty.setraw(descriptor)
        yield _read_posix_key
    finally:
        termios.tcsetattr(descriptor, termios.TCSADRAIN, previous)


def _render_menu(
    options: Sequence[tuple[str, T]],
    selected: int,
    number_buffer: str,
    output: TextIO,
    capacity: int,
    previous_lines: int,
) -> int:
    """Render the visible menu window and return its line count."""

    start = min(max(selected - capacity + 1, 0), max(len(options) - capacity, 0))
    visible = options[start : start + capacity]
    if previous_lines:
        output.write(f"\x1b[{previous_lines}A")

    for offset, (label, _) in enumerate(visible, start=start):
        marker = ">" if offset == selected else " "
        output.write(f"\r\x1b[2K{marker} {offset + 1}. {label}\n")

    hint = "Up/Down: move  Enter: select  Number: choose  Esc: cancel"
    if number_buffer:
        hint = f"Selection: {number_buffer}"
    output.write(f"\r\x1b[2K  {hint}\n")
    output.flush()
    return len(visible) + 1


def _choose_interactive(
    prompt: str,
    options: Sequence[tuple[str, T]],
    read_key: KeyFunction,
    output: TextIO,
    terminal_lines: int,
) -> T | None:
    """Select an option using arrow keys or a typed number."""

    output.write(f"{prompt}\n")
    selected = 0
    number_buffer = ""
    capacity = max(1, min(len(options), terminal_lines - 3))
    rendered_lines = _render_menu(
        options,
        selected,
        number_buffer,
        output,
        capacity,
        0,
    )

    while True:
        key = read_key()
        if key == "up":
            selected = (selected - 1) % len(options)
            number_buffer = ""
        elif key == "down":
            selected = (selected + 1) % len(options)
            number_buffer = ""
        elif key == "backspace":
            number_buffer = number_buffer[:-1]
        elif key == "escape":
            return None
        elif key == "enter":
            if not number_buffer:
                return options[selected][1]
            number = int(number_buffer)
            if 1 <= number <= len(options):
                return options[number - 1][1]
            number_buffer = ""
        elif key.isdigit():
            number_buffer += key
        else:
            continue

        rendered_lines = _render_menu(
            options,
            selected,
            number_buffer,
            output,
            capacity,
            rendered_lines,
        )


def choose(
    prompt: str,
    options: Sequence[tuple[str, T]],
    input_fn: InputFunction = input,
) -> T | None:
    """Display options and return the interactively selected value."""

    if not options:
        return None
    is_terminal = sys.stdin.isatty() and sys.stdout.isatty()
    if os.name != "nt" and os.environ.get("TERM") == "dumb":
        is_terminal = False
    if input_fn is not input or not is_terminal:
        return _choose_numbered(prompt, options, input_fn)

    try:
        with _terminal_key_reader() as read_key:
            return _choose_interactive(
                prompt,
                options,
                read_key,
                sys.stdout,
                shutil.get_terminal_size().lines,
            )
    except OSError:
        return _choose_numbered(prompt, options, input_fn)
    except (EOFError, KeyboardInterrupt):
        print("\nOperation cancelled.", file=sys.stderr)
        return None
