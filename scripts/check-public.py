"""Check the intended public files, without reading private input directories."""
from pathlib import Path
import json
import hashlib
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
reviewed_illustrations = {'lectures/assets/illustrations/05-campus-map-to-graph.png': 'e93262f0b7103382dc8563f4712364467dbe5bf025f7ee919f99087d3be4ed6d', 'lectures/assets/illustrations/05-discovered-once-ledger.png': '8694879b3f4a0d1ea41be15eb8067b67a83cd11061e70d8fe2b37c53fdc28661', 'lectures/assets/illustrations/06-path-list-vs-moves.png': '6c2015391c8aac8a3bfc7906b78d304172c8d68aaa3e31940cce78c6037b2338', 'lectures/assets/illustrations/07-distinguishing-test.png': '4357b72de1a52b21d16c6af4f37a1e065e293f6e2ec55712449fd20065107424', 'lectures/assets/illustrations/08-cards-to-tree.png': '6ba76923d05a072bbe07846a0439c202d508af5b5871f1dfe5110dac933c6923', 'lectures/assets/illustrations/08-three-stops.png': '923a2d008b719667af7e8231cba3f4d7b8d79b8c037dea85510b38051d7d9c3e', 'lectures/assets/illustrations/09-infix-prefix-same-tree.png': 'e782c5dd50c7bd3405ada426071496c1ff9c2456d5d5ce6be34ec3b735bc68af', 'lectures/assets/illustrations/09-read-eval-print-pipeline.png': '1a2ceaef336487b7b67d739c0e9688a27f24f666290f9001ed5bde891eb8f364', 'lectures/assets/illustrations/10-closure-keeps-e5.png': 'c4023b760c3e862617148d7696f79d7de9010b581ec395a56f3eb9d5c39955c4', 'lectures/assets/illustrations/10-define-adds-binding.png': 'f8b3b2efba047a6238a1a32e5d9ac6aca5dc9e747ffdb0503a7792002492f5af', 'lectures/assets/illustrations/11-script-shared-global.png': 'c025d1579b22a0bd2a9fefd3f3873f217a744df05b4a16b8fdd34d5e6c7066b8', 'lectures/assets/illustrations/12-double-quote-layers.png': 'a85daa9e833d429a76d3c0457e27ff84e7fd74b98b187779eaba6eb7408fd95f', 'lectures/assets/illustrations/12-host-and-target-environments.png': '8570b2db2c51749b9c086c4020cd27dee07125afcf621da4d246e86989de94a1', 'lectures/assets/illustrations/ai03-expected-value-source.png': '4760c247c50081d74fc284a658eaed0afa648b53ef1d1bb3d2783c4b0117ebd0', 'lectures/assets/illustrations/ai03-what-remains-two-desks.png': '912a17a347f42c16f02584761e062f4f9b9a9117cf11304d44e77ef27b274b3f', 'lectures/assets/illustrations/algo04-binary-search-premise.png': '12d019cabb69c194315adfde212412196b6a948dc70361299758a5baaaf2fb37', 'lectures/assets/illustrations/algo04-doubling-square.png': '3ee91c2dad5c6fea59d972ebd3a26859a7b8438447a3baab1efad93f0bb7c0ca', 'lectures/assets/illustrations/algo04-list-pop-shift.png': '089d9154329fceaf5a4f5ba3eddcbbd621725c1516a4899a320da916a3cf9bca', 'lectures/assets/illustrations/closure-environments.png': 'd365da6df1b33eafa8f93f1d985d25755658c672b69e770cd695146170fd4559', 'lectures/assets/illustrations/l13-discussion-cycle-if.png': '1f83d51335c418bfd07130bfa462ce7667123253c53d04db288bd30fea41a37d', 'lectures/assets/illustrations/l13-quote-read-vs-eval.png': 'a08e440610cd64866798ac2844c2cc791f86528fe13989fd751b5c5814d7a73a', 'lectures/assets/illustrations/l14-closure-shared-env-vs-copy.png': 'affd3e3aa22d3e0f32eafd4eb930d5f64d974e76a357d61cb86be1c9d6a58ccb', 'lectures/assets/illustrations/l14-meta-eval-layers-7.png': '8d2cc1ed2444c6fa6ed7d385e6f55078a8907ff1129083a0fda0f5d30bcdc073', 'lectures/assets/illustrations/l15-four-evidence-add10.png': '06d18f58246ba8a70892f6531f7605c1467788a2cae69691ad3ddd7250b80d09', 'lectures/assets/illustrations/l15-review-pair-example-b.png': '78f76892d16c1abb486f719bedbd1301a6e56fb8cb5b201637595f20755e5653', 'lectures/assets/illustrations/learning-five-actions.png': 'b50416152a50471accb16eca2d0472eacd5fd103648ee45623c53d5e5abe9683', 'lectures/assets/illustrations/parser-term.png': '7b33e8a98684d589c3f2d37ff640e08071742a5c5707162e6c03f72da790382a', 'lectures/assets/illustrations/python02-return-vs-print.png': '19e212dadd06176baf533782a5992c1eaca289d5e170dcde784ebcf77a8dac95', 'lectures/assets/illustrations/python02-shared-list-name-tags.png': '01a181f5c85dfd008cdc39fb409c91ebcc17a406afb8c128f02c5fd2a0adcb47', 'lectures/assets/illustrations/repl-error-continuation.png': '302fe417aa0b4405a1c7d0767d6b928fe5cc28348da8c76493ddfa01cb584f1d'}

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
        if name in reviewed_illustrations:
            if hashlib.sha256(path.read_bytes()).hexdigest() != reviewed_illustrations[name]:
                problems.append(f"reviewed illustration SHA differs: {name}")
        elif not name.startswith("output/previews/"):
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
