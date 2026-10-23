"""Run the unchanged public launcher and save its actual output."""

from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
lines = []
for option in ("--setup", "--check"):
    command = [sys.executable, "tools/run.py", option]
    result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, encoding="utf-8", check=True)
    lines.extend(["Command: python tools/run.py " + option, result.stdout.rstrip(), result.stderr.rstrip(), ""])
text = "\n".join(lines)
(ROOT / "tests" / "public_checks.txt").write_text(text, encoding="utf-8")
print(text)
