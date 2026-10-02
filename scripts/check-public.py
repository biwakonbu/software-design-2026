"""Check the intended public files, without reading private input directories."""
from pathlib import Path
import json
import re
import subprocess
import sys

root = Path(__file__).resolve().parents[1]
names = subprocess.check_output(["git", "ls-files", "--cached", "--others", "--exclude-standard", "-z"], cwd=root).decode().split("\0")
secret_patterns = [
    re.compile(r"gh[pousr]_[A-Za-z0-9]{30,}"),
    re.compile(r"github_pat_[A-Za-z0-9_]{30,}"),
    re.compile(r"AKIA[A-Z0-9]{16}"),
    re.compile(r"sk-[A-Za-z0-9_-]{30,}"),
    re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
]
source_patterns = [
    re.compile("/" + "Users/"),
    re.compile("osaka-" + "sandai\\.ac\\.jp", re.I),
    re.compile("oaisdmnt" + r"[^\s]*blob\.core\.windows\.net", re.I),
]
problems = []
pdf_count = 0
for name in filter(None, names):
    path = root / name
    if not path.is_file():
        continue
    if path.is_symlink():
        problems.append(f"symlink: {name}")
    if any(part in {"private-source", "private-source-review", "originals", "private-images"} for part in path.relative_to(root).parts):
        problems.append(f"private source: {name}")
    if path.name.startswith(".env") or path.name == "credentials.json" or path.suffix in {".pem", ".key", ".p12"}:
        problems.append(f"credential file: {name}")
    if path.suffix == ".pdf":
        pdf_count += 1
        text = subprocess.check_output(["pdftotext", str(path), "-"], text=True)
    elif path.suffix.lower() in {".png", ".jpg", ".jpeg", ".woff", ".woff2"}:
        if not name.startswith("output/previews/"):
            problems.append(f"unexpected binary visual: {name}")
        continue
    else:
        try:
            text = path.read_text()
        except UnicodeDecodeError:
            problems.append(f"unreviewed binary: {name}")
            continue
    for pattern in secret_patterns + source_patterns:
        if pattern.search(text):
            problems.append(f"sensitive pattern: {name}")

lessons = json.loads((root / "docs/curriculum.json").read_text())
for lesson in lessons:
    for folder in ("lectures", "exercises", "instructor"):
        if not (root / folder / f'{lesson["id"]}.md').is_file():
            problems.append(f'missing: {folder}/{lesson["id"]}.md')
    if not (root / "examples" / lesson["example"] / "README.md").is_file():
        problems.append(f'missing example: {lesson["example"]}')
if problems:
    print("Public check failed:")
    print("\n".join(sorted(set(problems))))
    sys.exit(1)
print(f"Public check passed: {len(list(filter(None, names)))} intended files, {pdf_count} PDFs, no private source/secret patterns.")
