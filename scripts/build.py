"""Helper script to run local quality checks."""

import subprocess
import sys


COMMANDS = [
    [sys.executable, "-m", "compileall", "src", "tests", "scripts"],
    [sys.executable, "scripts/generate_synthetic_dataset.py"],
]


def main() -> int:
    """Run all checks in sequence."""

    for command in COMMANDS:
        result = subprocess.run(command, check=False)
        if result.returncode != 0:
            return result.returncode
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
