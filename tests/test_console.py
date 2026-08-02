"""Tests for terminal interaction helpers."""

import unittest

from venvm.console import ask_yes_no, choose


def answers(*values: str):
    """Return deterministic answers for an interactive prompt."""

    iterator = iter(values)
    return lambda _prompt: next(iterator)


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


if __name__ == "__main__":
    unittest.main()
