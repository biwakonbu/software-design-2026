"""Compare a prose revision with an explicit baseline without changing either tree."""
from pathlib import Path
import argparse
import hashlib
import json
import re
import subprocess


def sha(data):
    return hashlib.sha256(data).hexdigest() if data is not None else None


def prose_path(name):
    path = Path(name)
    if len(path.parts) == 2 and path.parts[0] in {'lectures', 'exercises', 'instructor'} and path.suffix == '.md':
        return path.stem in {f'{n:02d}' for n in range(2, 16)}
    return len(path.parts) == 3 and path.parts[0] == 'examples' and path.name == 'README.md' and path.parts[1][:2] in {f'{n:02d}' for n in range(2, 16)}


def editable_prose(name):
    if not prose_path(name):
        return False
    path = Path(name)
    number = path.stem if path.parts[0] != 'examples' else path.parts[1][:2]
    return number != '02'


def structures(text):
    return {
        'fenced_code': [m.group(0) for m in re.finditer(r'(?ms)^(```|~~~)[^\n]*\n.*?^\1[^\n]*$', text)],
        'headings': re.findall(r'(?m)^#{1,6}\s.*$', text),
        'slide_boundaries': re.findall(r'(?m)^---\s*$', text),
        'frontmatter': re.findall(r'\A---\n.*?\n---', text, re.S),
        'tables': re.findall(r'(?m)^\s*\|.*\|\s*$', text),
        'inline_code': re.findall(r'(?<!`)`[^`\n]+`(?!`)', text),
        'html_tags': re.findall(r'</?[A-Za-z][^>]*>', text),
        'links': re.findall(r'\]\(([^)]+)\)', text),
        'quoted_spans': re.findall(r'「[^」\n]*」|『[^』\n]*』', text),
        'block_quotes': re.findall(r'(?m)^\s*>.*$', text),
        'numeric_tokens': sorted(re.findall(r'\d+(?:\.\d+)?', text)),
    }


def compare_snapshots(baseline, current, allowed_tooling=()):
    allowed = set(allowed_tooling)
    invalid_allowances = sorted(name for name in allowed if not name.startswith('scripts/') or name not in baseline)
    changed, missing, unexpected, structure_changes, tooling_changes = [], [], [], [], []
    checked = 0
    for name, before in sorted(baseline.items()):
        after = current.get(name)
        if after is None:
            missing.append(name)
            continue
        if prose_path(name):
            checked += 1
            first, second = structures(before.decode('utf-8')), structures(after.decode('utf-8'))
            keys = [key for key in first if first[key] != second[key]]
            if keys:
                structure_changes.append({'file': name, 'changed': keys})
        if before == after:
            continue
        changed.append({'file': name, 'baseline_sha256': sha(before), 'current_sha256': sha(after)})
        generated = name.startswith('output/pdf/') and not name.startswith('output/pdf/02-')
        generated = generated or name in {'docs/pdf-manifest.json', 'docs/verification.md'}
        if name in allowed:
            tooling_changes.append(name)
        elif not editable_prose(name) and not generated:
            unexpected.append(name)
    passed = not (missing or unexpected or structure_changes or invalid_allowances)
    return {'passed': passed, 'baseline_files': len(baseline), 'prose_files_checked': checked,
            'changed': changed, 'missing': missing, 'unexpected_changes': unexpected,
            'protected_structure_changes': structure_changes, 'allowed_tooling_changes': tooling_changes,
            'invalid_tooling_allowances': invalid_allowances,
            'limits': ['Numeric token multiplicity is checked; meaning, optionality, difficulty and grading require independent human review.',
                       'New files are outside baseline comparison; run the public-file check and their tests separately.']}


def git(root, *arguments):
    return subprocess.check_output(['git', *arguments], cwd=root)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    baseline = parser.add_mutually_exclusive_group(required=True)
    baseline.add_argument('--base-ref', help='Existing local commit or ref; no network operation is performed.')
    baseline.add_argument('--baseline-dir', type=Path, help='Read only tracked files from this existing baseline checkout.')
    parser.add_argument('--allow-tooling', action='append', default=[], help='Explicitly reviewed scripts/ change to list separately.')
    parser.add_argument('--out', type=Path, help='Optional JSON report outside either source tree.')
    args = parser.parse_args()
    root = args.root.resolve(strict=True)
    if args.baseline_dir:
        original = args.baseline_dir.resolve(strict=True)
        names = [name for name in git(original, 'ls-files', '--cached', '-z').decode().split('\0') if name]
        before = {name: (original / name).read_bytes() for name in names}
        identity = {'baseline_directory': str(original)}
    else:
        ref = git(root, 'rev-parse', '--verify', args.base_ref + '^{commit}').decode().strip()
        names = git(root, 'ls-tree', '-r', '--name-only', '-z', ref).decode().split('\0')
        before = {name: git(root, 'show', f'{ref}:{name}') for name in names if name}
        identity = {'baseline_commit': ref}
    after = {name: (root / name).read_bytes() for name in before if (root / name).is_file() and not (root / name).is_symlink()}
    report = {**identity, **compare_snapshots(before, after, args.allow_tooling)}
    if args.out:
        dest = args.out.resolve()
        inputs = [root] + ([original] if args.baseline_dir else [])
        if any(dest == folder or folder in dest.parents for folder in inputs):
            parser.error('--out must be outside the source trees')
        dest.parent.mkdir(parents=True, exist_ok=True)
        try:
            with dest.open('x', encoding='utf-8') as stream:
                stream.write(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
        except FileExistsError:
            parser.error('--out must be a new file; existing outputs are never overwritten')
    summary = {key: report[key] for key in ['passed', 'baseline_files', 'prose_files_checked', 'missing', 'unexpected_changes', 'protected_structure_changes', 'allowed_tooling_changes', 'invalid_tooling_allowances']}
    print(json.dumps(summary, ensure_ascii=False))
    return 0 if report['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
