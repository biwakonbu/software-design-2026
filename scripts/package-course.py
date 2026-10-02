"""Package only git's intended public files; excludes source originals and runtime caches."""
from pathlib import Path
import argparse
import subprocess
import zipfile

parser = argparse.ArgumentParser()
parser.add_argument("--output", default="tmp/software-design-2026.zip")
args = parser.parse_args()
root = Path(__file__).resolve().parents[1]
target = (root / args.output).resolve()
target.parent.mkdir(parents=True, exist_ok=True)
names = subprocess.check_output(["git", "ls-files", "--cached", "--others", "--exclude-standard", "-z"], cwd=root).decode().split("\0")
with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as bundle:
    for name in sorted(filter(None, names)):
        path = root / name
        if path.is_file() and not path.is_symlink() and path != target:
            bundle.write(path, f"software-design-2026/{name}")
print(f"Created {target.name}: {target.stat().st_size} bytes")
