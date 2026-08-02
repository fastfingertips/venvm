from __future__ import annotations

import subprocess
import unittest
from unittest.mock import patch

import check_commits


class CommitMessageTests(unittest.TestCase):
    def test_accepts_conventional_lowercase_subject(self) -> None:
        self.assertEqual(check_commits.validate_subject("fix: handle missing script"), [])

    def test_accepts_initial_subject_only_for_root_commit(self) -> None:
        self.assertEqual(
            check_commits.validate_subject("Initial commit", is_root=True),
            [],
        )
        self.assertTrue(check_commits.validate_subject("Initial commit"))

    def test_rejects_uppercase_subject(self) -> None:
        errors = check_commits.validate_subject("fix: Handle missing script")

        self.assertIn("must be entirely lowercase", errors)

    def test_rejects_subject_longer_than_limit(self) -> None:
        errors = check_commits.validate_subject("fix: " + "a" * 41)

        self.assertIn("exceeds 45 characters (46)", errors)

    def test_rejects_non_conventional_subject(self) -> None:
        errors = check_commits.validate_subject("handle missing script")

        self.assertIn("must use conventional commit format", errors)

    @patch.object(check_commits, "git_output")
    def test_missing_base_validates_full_history(self, git_output) -> None:
        git_output.side_effect = [
            subprocess.CalledProcessError(128, ["git", "rev-parse"]),
            "abc123\tfix: handle missing script",
        ]

        commits = check_commits.collect_commits("missing", "head")

        self.assertEqual(commits, [["abc123", "fix: handle missing script"]])
        git_output.assert_called_with("log", "--format=%H%x09%s", "head")


if __name__ == "__main__":
    unittest.main()
