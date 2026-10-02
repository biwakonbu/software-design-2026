"""Render every handout page with Poppler; QA images stay outside version control."""
from pathlib import Path
import argparse
import json
import subprocess

parser = argparse.ArgumentParser()
parser.add_argument("--destination", default="tmp/pdf-qa")
parser.add_argument("--scale", type=int, default=1600)
args = parser.parse_args()
root = Path(__file__).resolve().parents[1]
dest = Path(args.destination).resolve()
manifest = []
lessons = json.loads((root / "docs/curriculum.json").read_text())
expected = {lesson["pdf"] for lesson in lessons}
missing = [name for name in expected if not (root / name).is_file()]
if missing:
    raise SystemExit(f"Missing PDFs: {missing}")
for source in sorted((root / "output/pdf").glob("*.pdf")):
    if not source.is_file():
        raise SystemExit(f"Missing PDF: {source}")
    target = dest / source.stem
    target.mkdir(parents=True, exist_ok=True)
    subprocess.run(["pdftoppm", "-scale-to", str(args.scale), "-png", str(source), str(target / "page")], check=True)
    files = sorted(target.glob("page-*.png"))
    manifest.append({"pdf": str(source.relative_to(root)), "rendered_pages": len(files)})
    print(f'{source.stem}: {len(files)} pages rendered')
(dest / "render-manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
