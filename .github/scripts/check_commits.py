"""Validate commit subjects against the repository convention."""

from __future__ import annotations

import re
import subprocess
import sys


ZERO_SHA = "0" * 40
SUBJECT_PATTERN = re.compile(
    r"^(build|chore|ci|docs|feat|fix|perf|refactor|revert|style|test)"
    r"(\([a-z0-9][a-z0-9._/-]*\))?!?: [a-z0-9].*$"
)


def validate_subject(subject: str, *, is_root: bool = False) -> list[str]:
    """Return validation errors for a commit subject."""
    if is_root and subject == "Initial commit":
        return []

    errors = []
    if len(subject) > 45:
        errors.append(f"exceeds 45 characters ({len(subject)})")
    if subject != subject.lower():
        errors.append("must be entirely lowercase")
    if not SUBJECT_PATTERN.fullmatch(subject):
        errors.append("must use conventional commit format")
    return errors


def git_output(*args: str) -> str:
    """Run Git and return stripped standard output."""
    result = subprocess.run(
        ["git", *args],
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def collect_commits(base: str, head: str) -> list[tuple[str, str]]:
    """Collect commit hashes and subjects for a push or pull request range."""
    revision = head
    if base and base != ZERO_SHA:
        try:
            git_output("rev-parse", "--verify", f"{base}^{{commit}}")
        except subprocess.CalledProcessError:
            pass
        else:
            revision = f"{base}..{head}"
    output = git_output("log", "--format=%H%x09%s", revision)
    if not output:
        return []
    return [line.split("\t", 1) for line in output.splitlines()]


def is_root_commit(commit: str) -> bool:
    """Return whether a commit has no parents."""
    return len(git_output("rev-list", "--parents", "-n", "1", commit).split()) == 1


def main() -> int:
    """Validate the requested Git commit range."""
    if len(sys.argv) != 3:
        print("usage: check_commits.py BASE HEAD", file=sys.stderr)
        return 2

    failures = []
    for commit, subject in collect_commits(sys.argv[1], sys.argv[2]):
        errors = validate_subject(subject, is_root=is_root_commit(commit))
        if errors:
            failures.append(f"{commit[:7]} {subject!r}: {', '.join(errors)}")

    if failures:
        print("Invalid commit subjects:", file=sys.stderr)
        for failure in failures:
            print(f"- {failure}", file=sys.stderr)
        return 1

    print("Commit subjects are valid.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
