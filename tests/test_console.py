"""Tests for terminal interaction helpers."""

from io import StringIO
import unittest

from venvm.console import _choose_interactive, ask_yes_no, choose


def answers(*values: str):
    """Return deterministic answers for an interactive prompt."""

    iterator = iter(values)
    return lambda _prompt: next(iterator)


def keys(*values: str):
    """Return a deterministic key reader for an interactive menu."""

    iterator = iter(values)
    return lambda: next(iterator)


class ConsoleTests(unittest.TestCase):
    """Verify prompt validation and selection behavior."""

    def test_ask_yes_no_retries_invalid_input(self) -> None:
        self.assertTrue(ask_yes_no("Continue?", answers("invalid", "y")))

    def test_choose_retries_out_of_range_input(self) -> None:
        result = choose(
            "Pick",
            [("first", "a"), ("second", "b")],
            answers("3", "2"),
        )
        self.assertEqual(result, "b")

    def test_interactive_choose_supports_arrow_keys(self) -> None:
        result = _choose_interactive(
            "Pick",
            [("first", "a"), ("second", "b")],
            keys("down", "enter"),
            StringIO(),
            terminal_lines=10,
        )

        self.assertEqual(result, "b")

    def test_interactive_choose_supports_number_input(self) -> None:
        result = _choose_interactive(
            "Pick",
            [("first", "a"), ("second", "b")],
            keys("2", "enter"),
            StringIO(),
            terminal_lines=10,
        )

        self.assertEqual(result, "b")

    def test_interactive_choose_supports_multi_digit_number(self) -> None:
        options = [(f"option {number}", number) for number in range(1, 13)]

        result = _choose_interactive(
            "Pick",
            options,
            keys("1", "2", "enter"),
            StringIO(),
            terminal_lines=10,
        )

        self.assertEqual(result, 12)

    def test_interactive_choose_scrolls_visible_window(self) -> None:
        output = StringIO()

        result = _choose_interactive(
            "Pick",
            [("first", "a"), ("second", "b"), ("third", "c")],
            keys("down", "down", "enter"),
            output,
            terminal_lines=5,
        )

        self.assertEqual(result, "c")
        self.assertIn("> 3. third", output.getvalue())

    def test_interactive_choose_can_be_cancelled(self) -> None:
        result = _choose_interactive(
            "Pick",
            [("first", "a")],
            keys("escape"),
            StringIO(),
            terminal_lines=10,
        )

        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()
