#!/usr/bin/env python3
"""教材説明文のローカル抽出と、版を固定したjaioの読み取り専用検査。Python 3.9+。"""
from __future__ import annotations

import argparse
from bisect import bisect_right
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass, field
import hashlib
import html
import json
from pathlib import Path
import re
import subprocess
import sys

BASE = Path(__file__).resolve().parents[1]
NETWORK_PROFILE = '(version 1) (allow default) (deny network*)'
RUNNER_VERSION = '1.1.0'
JP = re.compile(r'[ぁ-んァ-ヶ一-龯]')
PROTECTED_HEADING = re.compile(r'演習|設問|確認問題|練習問題|解答|解説例|模範|入力例|出力例|提出|採点|評価基準|仕様|契約|依頼例')
RECAP = re.compile(r'復習|振り返り|ふり返り|前回|再掲|おさらい|まとめ|recap', re.I)
DEFINITION = re.compile(r'定義|用語|とは|役割')
TOKEN = re.compile(r'https?://[^\s"()\[\]{}]+|//[^\n]*|/\*[\s\S]*?\*/|"(?:\\.|[^"\\])*"|(?P<ticks>`+)(?:(?!(?P=ticks)).)*(?P=ticks)|\\.|[A-Za-z_][\w-]*|\s+|.', re.S)
READABLE_CALLS = {'chapter-opener', 'spread', 'panel', 'flow', 'compare', 'check-card', 'text', 'header', 'doc-card', 'badge', 'cap', 'title_page', 'product_chapter', 'reading-map'}
PROTECTED_CALLS = {'artifact', 'sample', 'raw', 'quote', 'source-note', 'screen', 'table', 'task-row'}
READABLE_FIELDS = {'title', 'detail', 'caption', 'body', 'text', 'label', 'def', 'display', 'reading', 'subtitle', 'outputs'}


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def file_sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def read_json(path: Path):
    return json.loads(path.read_text(encoding='utf-8'))


def write_json(path: Path, value):
    with path.open('x', encoding='utf-8') as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2)
        stream.write('\n')


@dataclass
class Fragment:
    text: str
    line: int
    col: int = 1
    role: str = 'body'
    section: str = ''
    approximate: bool = False


@dataclass
class Document:
    source: str
    course: str
    medium: str
    unit: str
    fragments: list[Fragment] = field(default_factory=list)
    corpus: str = ''
    line_map: list[dict] = field(default_factory=list)
    source_root: str = ''


def protected_record(source: str, start: int, end: int, reason: str) -> dict:
    return {'start_line': source.count('\n', 0, start) + 1,
            'end_line': source.count('\n', 0, max(start, end - 1)) + 1,
            'reason': reason, 'sha256': sha(source[start:end].encode())}


def role_for(section: str, definition=False) -> str:
    if definition:
        return 'definition'
    if RECAP.search(section):
        return 'recap'
    if DEFINITION.search(section):
        return 'definition_candidate'
    return 'body'


def mask_inline(text: str) -> str:
    # 構文・コード・リンク先を補助検査だけから除く。元ソースには適用しない。
    for pattern in [r'(`+).*?\1', r'!\[[^\]]*\]\([^)]*\)', r'\]\([^)]*\)', r'https?://[^\s<>]+']:
        text = re.sub(pattern, lambda m: ' ' * len(m[0]), text)
    return text


def markdown(source: str, rel: str, course: str, medium: str, slides=False):
    documents, protected = [], []
    doc = Document(rel, course, medium, '1')
    section, protected_level, fence, quote, front = '', None, None, False, False
    dangerous, slide_index = None, 1
    offsets, pos = [], 0
    lines = source.splitlines(keepends=True)
    for line in lines:
        offsets.append(pos)
        pos += len(line)
    for i, original in enumerate(lines):
        line = original.rstrip('\r\n')
        stripped = line.strip()
        reason = None
        if i == 0 and stripped == '---':
            front = True
            reason = 'frontmatter'
        elif front:
            reason = 'frontmatter'
            if stripped in ('---', '...'):
                front = False
        elif fence:
            reason = 'code'
            if re.fullmatch(re.escape(fence[0]) + '{' + str(fence[1]) + ',}\\s*', stripped):
                fence = None
        elif (m := re.match(r'^(`{3,}|~{3,})', stripped)):
            fence = (m[1][0], len(m[1]))
            reason = 'code'
        elif re.match(r'^ {4}\S|^\t\S', line):
            reason = 'indented-code-or-unknown-block'
        elif slides and stripped == '---':
            if doc.fragments:
                documents.append(doc)
            slide_index += 1
            doc = Document(rel, course, medium, str(slide_index))
            section, protected_level, quote = '', None, False
            # Slidevのスライド別YAMLも本文として検査しない。
            if i + 1 < len(lines) and re.match(r'^[A-Za-z][\w-]*:', lines[i + 1]):
                front = True
            continue
        elif dangerous:
            reason = 'html-' + dangerous
            if (dangerous == '!--' and '-->' in line) or re.search(r'</' + dangerous + r'\s*>', line, re.I):
                dangerous = None
        elif (m := re.search(r'<(script|style|svg|pre|code)\b', line, re.I)):
            tag = m[1].lower()
            reason = 'html-' + tag
            if not re.search(r'</' + tag + r'\s*>', line, re.I):
                dangerous = tag
        elif stripped.startswith('<!--'):
            reason = 'html-comment'
            if '-->' not in stripped:
                dangerous = '!--'
        else:
            heading = re.match(r'^\s{0,3}(#{1,6})\s+(.+)', line)
            if heading:
                level, section = len(heading[1]), heading[2].strip()
                if protected_level is not None and level <= protected_level:
                    protected_level = None
                if PROTECTED_HEADING.search(section):
                    protected_level = level
            if protected_level is not None:
                reason = 'exercise-answer-or-contract-section'
            elif quote or stripped.startswith('>'):
                reason = 'quotation'
                quote = bool(stripped)
            elif stripped.startswith('|') or re.match(r'^\s*\|?\s*:?-{3,}', line):
                reason = 'table-contract-or-values'
            elif re.match(r'^\s*\$\$|^\s*<[/A-Z][^>]*>\s*$', line):
                reason = 'formula-or-component'
        if reason:
            protected.append(protected_record(source, offsets[i], offsets[i] + len(original), reason))
            continue
        # 可視HTML文字だけを残す。属性・SVG/Vue/JSは実行も解析もしない。
        clean = re.sub(r'<!--.*?-->|<[^>]*>', '', line)
        clean = html.unescape(clean).strip()
        if clean and JP.search(mask_inline(clean)):
            doc.fragments.append(Fragment(clean, i + 1, 1, role_for(section), section, clean != line))
    if doc.fragments:
        documents.append(doc)
    return documents, protected


def typst(source: str, rel: str, course: str, medium: str, terms: dict[str, str]):
    tokens = [(m[0], m.start(), m.end()) for m in TOKEN.finditer(source)]
    significant = [i for i, t in enumerate(tokens) if not t[0].isspace() and not t[0].startswith(('//', '/*'))]
    next_token = {i: significant[n + 1] for n, i in enumerate(significant[:-1])}
    pairs, stack = {}, []
    for i, (text, _, _) in enumerate(tokens):
        if text in ('(', '[', '{'):
            stack.append(i)
        elif text in (')', ']', '}'):
            if not stack or tokens[stack[-1]][0] != {')': '(', ']': '[', '}': '{'}[text]:
                raise ValueError(f'{rel}: unmatched Typst delimiter')
            start = stack.pop()
            pairs[start] = i
    if stack:
        raise ValueError(f'{rel}: unclosed Typst delimiter')
    excluded, protected, replacement = [], [], {}
    for i in significant:
        name, start, _ = tokens[i]
        j = next_token.get(i)
        if j is None or tokens[j][0] not in ('(', '[') or j not in pairs:
            continue
        end_i = pairs[j]
        trailing = next_token.get(end_i)
        if trailing is not None and tokens[trailing][0] == '[' and trailing in pairs:
            end_i = pairs[trailing]
        end = tokens[end_i][2]
        if name in PROTECTED_CALLS:
            excluded.append((start, end))
            protected.append(protected_record(source, start, end, 'typst-' + name))
        elif name == 'term':
            invocation = source[tokens[j][1]:tokens[pairs[j]][2]]
            match = re.search(r'"([^"\\]+)"', invocation)
            if match and match[1] in terms:
                replacement[i] = (end_i, terms[match[1]])
    # 構文の範囲を字句トークンから判定する。コード式中の任意文字列は採用しない。
    line_starts = [0] + [m.end() for m in re.finditer('\n', source)]
    by_line = defaultdict(list)
    stacks, skip_ids, section = [], set(), ''
    heading_buffer = []
    previous_sig = None
    skip_until = -1
    for i, (text, start, end) in enumerate(tokens):
        if text in ('(', '[', '{'):
            owner = tokens[previous_sig][0] if previous_sig is not None else ''
            if text == '[' and owner == '(' and stacks and stacks[-1][1] in {'spread', 'product_chapter'}:
                owner = 'heading:' + stacks[-1][1]
                heading_buffer = []
            elif text == '[' and owner == ':':
                key = re.search(r'([\w-]+)\s*:\s*$', source[max(0, start - 80):start])
                if key and key[1] in ('title', 'detail', 'label', 'display', 'reading'):
                    owner = 'label:' + key[1]
                elif key and key[1] == 'caption':
                    owner = 'caption'
            stacks.append((text, owner))
        elif text in (')', ']', '}'):
            _, closing_owner = stacks.pop()
            if closing_owner.startswith('heading:'):
                section = ''.join(heading_buffer).strip()
        in_markup = bool(stacks and stacks[-1][0] == '[')
        owners = {owner for _, owner in stacks}
        if i <= skip_until or any(a <= start < b for a, b in excluded):
            pass
        elif i in replacement and in_markup:
            skip_until, value = replacement[i]
            line = bisect_right(line_starts, start)
            end_offset = tokens[skip_until][2]
            tail = source[end_offset:source.find('\n', end_offset) if '\n' in source[end_offset:] else len(source)]
            role = role_for(section) if tail.strip() else 'label'
            by_line[line].append((start, value, role, section, role == 'label'))
        elif text == '#':
            if i in next_token:
                skip_ids.add(next_token[i])
        elif text.startswith(('//', '/*', '`', 'http://', 'https://')):
            protected.append(protected_record(source, start, end, 'typst-comment-or-code'))
        elif i not in skip_ids and text.startswith('"'):
            before = source[max(0, start - 55):start]
            key = re.search(r'([\w-]+)\s*:\s*$', before)
            readable = (key and key[1] in READABLE_FIELDS) or bool(owners & READABLE_CALLS) or in_markup
            if readable:
                try:
                    value = json.loads(text)
                except ValueError:
                    value = text[1:-1]
                if JP.search(value) and not re.search(r'https?://|\.(?:typ|py|md)$', value):
                    heading = bool(stacks and stacks[-1][1] in {'spread', 'chapter-opener', 'product_chapter'} and not key)
                    if heading:
                        section = value
                    if not PROTECTED_HEADING.search(section):
                        line = bisect_right(line_starts, start)
                        role = ('heading' if heading else 'definition' if key and key[1] == 'def'
                                else 'caption' if key and key[1] == 'caption' else 'label')
                        by_line[line].append((start, value, role, section, True))
        elif in_markup and i not in skip_ids and text not in ('(', ')', '[', ']', '{', '}', '#'):
            if not PROTECTED_HEADING.search(section):
                line = bisect_right(line_starts, start)
                owner = stacks[-1][1]
                role = ('heading' if owner.startswith('heading:') else 'caption' if 'caption' in owner
                        else 'label' if owner.startswith('label:') or 'check-card' in owners else role_for(section))
                if role == 'heading':
                    heading_buffer.append(text)
                by_line[line].append((start, text, role, section, False))
        if not text.isspace() and not text.startswith(('//', '/*')):
            previous_sig = i
    doc = Document(rel, course, medium, '1')
    for line, pieces in sorted(by_line.items()):
        groups, buffer = [], []
        for piece in pieces:
            if piece[4]:
                if buffer:
                    groups.append(buffer)
                    buffer = []
                groups.append([piece])
            else:
                if buffer and buffer[0][2:4] != piece[2:4]:
                    groups.append(buffer)
                    buffer = []
                buffer.append(piece)
        if buffer:
            groups.append(buffer)
        for group in groups:
            value = ''.join(piece[1] for piece in group).strip()
            if value and JP.search(mask_inline(value)):
                start, _, role, heading, _ = group[0]
                col = start - line_starts[line - 1] + 1
                doc.fragments.append(Fragment(value, line, col, role, heading, True))
    return ([doc] if doc.fragments else []), protected


class JSONPositions:
    """標準JSONとして検証し、JSON Pointerと各文字列の位置を復元する。"""
    def __init__(self, source: str):
        self.source = source
        self.data = json.loads(source)
        self.decoder = json.JSONDecoder()
        self.strings = {}
        self.parse(0, '')

    def ws(self, i):
        while i < len(self.source) and self.source[i].isspace():
            i += 1
        return i

    def parse(self, i, pointer):
        i = self.ws(i)
        start = i
        if self.source[i] == '{':
            i = self.ws(i + 1)
            while self.source[i] != '}':
                key, end = self.decoder.raw_decode(self.source, i)
                i = self.ws(end) + 1
                i = self.parse(i, pointer + '/' + key.replace('~', '~0').replace('/', '~1'))
                i = self.ws(i)
                if self.source[i] == ',':
                    i = self.ws(i + 1)
            return i + 1
        if self.source[i] == '[':
            n, i = 0, self.ws(i + 1)
            while self.source[i] != ']':
                i = self.ws(self.parse(i, pointer + '/' + str(n)))
                n += 1
                if self.source[i] == ',':
                    i = self.ws(i + 1)
            return i + 1
        value, end = self.decoder.raw_decode(self.source, i)
        if isinstance(value, str):
            self.strings[pointer] = (value, start, end)
        return end


def slide_json(source: str, rel: str, course: str, medium: str):
    parsed = JSONPositions(source)
    if not isinstance(parsed.data, list) or not all(isinstance(x, dict) for x in parsed.data):
        raise ValueError(f'{rel}: content.json must be an array of slide objects')
    documents, protected = [], []
    visible = re.compile(r'^/(\d+)/(title|body|caption|foot|rows/\d+/(?:label|text)|items/\d+/(?:title|body)|(?:left|right)/(?:label|title|points/\d+))$')
    for n, obj in enumerate(parsed.data):
        doc = Document(rel, course, medium, str(n + 1))
        section = obj.get('title', '')
        is_exercise = PROTECTED_HEADING.search(section) or 'exercise' in obj.get('session', '')
        for pointer, (value, start, end) in parsed.strings.items():
            if not pointer.startswith('/' + str(n) + '/'):
                continue
            match = visible.fullmatch(pointer)
            if not match or is_exercise:
                protected.append(protected_record(source, start, end, 'slide-protected-field:' + pointer))
                continue
            if JP.search(value):
                line = source.count('\n', 0, start) + 1
                col = start - source.rfind('\n', 0, start)
                value = value.replace('\n', ' ')
                role = 'heading' if match[2] == 'title' else role_for(section)
                doc.fragments.append(Fragment(value, line, col, role, section, True))
        if doc.fragments:
            documents.append(doc)
    return documents, protected


def term_registry(root: Path, targets: list[Path]) -> dict[str, dict[str, str]]:
    result = {}
    for path in targets:
        if path.name == 'terms.typ':
            source = path.read_text(encoding='utf-8')
            result[str(path.parent)] = dict(re.findall(r'"([^"\\]+)"\s*:\s*\(\s*display\s*:\s*"([^"\\]+)"', source))
    return result


def serialize_document(doc: Document, out: Path, n: int):
    doc.corpus = f'corpus/{doc.course}-{n:05d}.md'
    lines, mapping = [], []
    for i, fragment in enumerate(doc.fragments):
        # 各抽出ブロックの元行を保持。再結合は文の意味判断に使わない。
        text = '# ' + fragment.text if fragment.role == 'heading' else '- ' + fragment.text if fragment.role == 'label' else fragment.text
        lines.append(text)
        mapping.append(asdict(fragment))
        following = doc.fragments[i + 1] if i + 1 < len(doc.fragments) else None
        continuation = (following is not None and following.line == fragment.line + 1
                        and following.section == fragment.section and following.role == fragment.role
                        and fragment.role not in ('heading', 'label')
                        and not re.search(r'[。！？!?]$', fragment.text)
                        and not re.match(r'^(?:#+\s|[-*+]\s|\d+[.)]\s)', following.text)
                        and not re.match(r'^(?:#+\s|[-*+]\s|\d+[.)]\s)', fragment.text))
        if not continuation:
            lines.append('')
            mapping.append({})
    with (out / doc.corpus).open('x', encoding='utf-8') as stream:
        stream.write('\n'.join(lines) + '\n')
    doc.line_map = mapping
    data = asdict(doc)
    data['corpus_sha256'] = file_sha(out / doc.corpus)
    return data


def exclusive_output(out: Path, roots: list[Path]):
    out = out.resolve()
    for root in roots:
        root = root.resolve()
        if out == root or root in out.parents:
            raise ValueError('output must be outside the source repository')
    out.mkdir(parents=True, exist_ok=False)
    (out / 'corpus').mkdir()
    return out


def extract(profile: str, root: Path, out: Path, book_root: Path | None = None):
    root = root.resolve(strict=True)
    spec = read_json(BASE / 'profiles' / (profile + '.json'))
    if book_root is not None:
        if profile != 'bootcamp':
            raise ValueError('--book-root is only valid for bootcamp')
        book_root = book_root.resolve(strict=True)
    roots = [root] + ([book_root] if book_root else [])
    selected = {}
    for target in spec['targets']:
        pattern, source_root = target['glob'], root
        if target['medium'] == 'book' and book_root is not None:
            pattern = pattern.removeprefix('products/bootcamp/books/*/')
            source_root = book_root
        for path in sorted(source_root.glob(pattern)):
            if path.is_file():
                if path.is_symlink() or source_root not in path.resolve().parents:
                    raise ValueError(f'source path escapes root or is a symlink: {path}')
                selected[path] = (target, source_root)
    if not selected:
        raise ValueError('profile found no input files')
    out = exclusive_output(out, roots)
    registry = term_registry(root, list(selected))
    sources, documents = [], []
    for path, (target, source_root) in sorted(selected.items()):
        rel, data = path.relative_to(source_root).as_posix(), path.read_bytes()
        source = data.decode('utf-8')
        adapter, medium = target['adapter'], target['medium']
        entry = {'path': rel, 'root': str(source_root), 'course': spec['course'], 'sha256': sha(data), 'adapter': adapter, 'protected': []}
        if adapter == 'protected' or (profile == 'bootcamp' and '-exercise' in path.stem):
            docs = []
            entry['status'] = 'protected_file'
            entry['protected'] = [protected_record(source, 0, len(source), 'exercise-file')]
        elif adapter == 'renderer':
            if not (path.parent / 'content.json').is_file():
                raise ValueError(f'{rel}: no content.json adapter; TSX execution is prohibited')
            docs = []
            entry['status'] = 'renderer_not_prose; content.json analyzed separately'
        else:
            if adapter.startswith('markdown'):
                docs, protected = markdown(source, rel, spec['course'], medium, adapter == 'markdown-slides')
            elif adapter == 'typst':
                terms_path = path.parent.parent if path.parent.name == 'chapters' else path.parent
                docs, protected = typst(source, rel, spec['course'], medium, registry.get(str(terms_path), {}))
            elif adapter == 'slide-json':
                docs, protected = slide_json(source, rel, spec['course'], medium)
            else:
                raise ValueError('unknown adapter: ' + adapter)
            entry['status'] = 'extracted' if docs else 'no_static_prose'
            entry['protected'] = protected
        for doc in docs:
            doc.source_root = str(source_root)
            documents.append(serialize_document(doc, out, len(documents) + 1))
        sources.append(entry)
    manifest = {'schema_version': 1, 'profile': profile, 'roots': [str(r) for r in roots], 'sources': sources, 'documents': documents,
                'coverage': 'static source prose only; not full rendered material or semantic completeness',
                'limits': ['Typst macros, imports and dynamic content are not evaluated.',
                           'Exercise/answer/contracts, tables, code, quotes and slide speaker/chat samples are protected.',
                           'Flattened locations preserve source lines; columns can be approximate.',
                           'Generated corpus link/heading structure is not the original structure.']}
    write_json(out / 'manifest.json', manifest)
    return manifest


def verify_inputs(manifest: dict, out: Path):
    mismatches = []
    for src in manifest['sources']:
        path = Path(src['root']) / src['path']
        if path.is_symlink() or file_sha(path) != src['sha256']:
            mismatches.append(src['path'])
    for doc in manifest['documents']:
        if file_sha(out / doc['corpus']) != doc['corpus_sha256']:
            mismatches.append(doc['corpus'])
    if mismatches:
        raise ValueError('inputs changed; extract a fresh corpus: ' + ', '.join(mismatches[:8]))


def duplicate_class(locations: list[dict]) -> tuple[str, str]:
    if len(locations) < 2:
        return 'review_required', '比較対象の位置が不足しています。'
    if len({x['course'] for x in locations}) > 1:
        return 'shared_foundation_candidate', '異なる教材の共通基礎です。用途と深さを確認し、削除を自動決定しません。'
    if any(x.get('role') in ('definition', 'definition_candidate', 'recap') for x in locations):
        return 'learning_repetition_candidate', '定義または復習としての再掲候補です。学習上の必要性を人が確認します。'
    if {x['medium'] for x in locations} >= {'book', 'slides'}:
        return 'book_slide_alignment', '参照用の本と授業投影の共通説明です。媒体別の必要性と一致を確認します。'
    if len({(x.get('source_root', ''), x['source']) for x in locations}) == 1:
        return 'within_material_review', '同一資料内の繰返し候補です。不要と確定していません。'
    return 'cross_material_review', '別の章・資料間の繰返し候補です。目的・前提・読者を確認します。'


def map_location(location: dict, docs: dict) -> dict:
    corpus = location['file'].replace('\\', '/')
    key = 'corpus/' + corpus.split('/corpus/')[-1] if '/corpus/' in corpus else corpus
    doc = docs.get(key)
    if not doc:
        return {'corpus': corpus, 'mapped': False, 'approximate': True}
    span = location.get('span') or {}
    index = max(0, span.get('line', 1) - 1)
    mapping = doc['line_map']
    fragment = mapping[index] if index < len(mapping) and mapping[index] else {}
    if not fragment:
        fragment = next((x for x in mapping[index:] if x), {}) or next((x for x in reversed(mapping[:index]) if x), {})
    return {'source': doc['source'], 'source_root': doc.get('source_root', ''), 'course': doc['course'], 'medium': doc['medium'], 'unit': doc['unit'],
            'line': fragment.get('line'), 'col': fragment.get('col', 1), 'role': fragment.get('role', 'body'),
            'section': fragment.get('section', ''), 'mapped': bool(fragment),
            'approximate': bool(location.get('approximate') or fragment.get('approximate') or span.get('col', 1) != 1)}


def map_diagnostic(diagnostic: dict, docs: dict) -> list[dict]:
    # jaioのcross-doc診断ではlocationsに相手だけが入り、主位置はfile/spanにある。
    locations = [{'file': diagnostic['file'], 'span': diagnostic.get('span')}]
    locations.extend(diagnostic.get('locations', []))
    unique, seen = [], set()
    for location in locations:
        span = location.get('span') or {}
        key = (location['file'], span.get('line'), span.get('col'))
        if key not in seen:
            unique.append(map_location(location, docs))
            seen.add(key)
    return unique


def supplementary(manifest: dict):
    findings, paragraphs = [], defaultdict(list)
    for doc in manifest['documents']:
        for fragment in doc['fragments']:
            body = mask_inline(fragment['text'])
            location = {k: doc[k] for k in ('source', 'course', 'medium', 'unit')}
            location['source_root'] = doc.get('source_root', '')
            location.update({k: fragment[k] for k in ('line', 'col', 'role', 'section', 'approximate')})
            if re.search(r'(適切に|いい感じに|うまく(?!いった|いく|でき)|必要に応じて|適宜|十分に|きちんと)[^。！？!?]{0,25}(確認|設定|作成|修正|対応|検証|整理)', body):
                findings.append({'rule_id': 'material/ambiguous-instruction', 'origin': 'supplement', 'severity': 'info',
                                 'locations': [location], 'review_question': '具体的な対象・操作・判定条件が近くにあるか確認してください。',
                                 'limitation': '近傍の説明を理解しない字句検査です。曖昧さを確定しません。'})
            normalized = re.sub(r'\s+', '', body).strip('#*- ')
            if len(normalized) >= 60:
                paragraphs[normalized].append(location)
    for text, locations in paragraphs.items():
        if len(locations) > 1:
            classification, reason = duplicate_class(locations)
            findings.append({'rule_id': 'material/repeated-block', 'origin': 'supplement', 'severity': 'info',
                             'normalized_sha256': sha(text.encode()), 'chars': len(text), 'locations': locations,
                             'classification': classification, 'review_question': reason,
                             'limitation': '同一抽出ブロックの一致だけを検出します。意味的な重複を確定しません。'})
    return findings


def config_for(profile: str) -> str:
    config = (BASE / 'configs/materials.jaio.toml').read_text(encoding='utf-8')
    if profile in ('university', 'bootcamp'):
        settings = read_json(BASE / 'profiles' / (profile + '.json'))
        for key in ('long_sentence_min_chars', 'no_comma_min_chars'):
            config, count = re.subn(r'^' + key + r' = \d+$', key + ' = ' + str(settings[key]), config, flags=re.M)
            if count != 1:
                raise ValueError('threshold key is missing or duplicated: ' + key)
    return config


def analyze(out: Path, binary: Path):
    out = out.resolve(strict=True)
    manifest_bytes = (out / 'manifest.json').read_bytes()
    manifest = json.loads(manifest_bytes)
    manifest_sha = sha(manifest_bytes)
    verify_inputs(manifest, out)
    if file_sha(out / 'manifest.json') != manifest_sha:
        raise ValueError('manifest changed during analysis; extract a fresh corpus')
    pin = read_json(BASE / 'configs/jaio-provenance.json')
    binary = binary.resolve(strict=True)
    if file_sha(binary) != pin['binary_sha256']:
        raise ValueError('jaio binary differs from reviewed pin; review new source/build before changing provenance')
    if sys.platform != 'darwin' or not Path('/usr/bin/sandbox-exec').is_file():
        raise ValueError('this verified runner requires macOS sandbox-exec; do not silently run without network denial')
    guard = ['/usr/bin/sandbox-exec', '-p', NETWORK_PROFILE, str(binary)]
    version = subprocess.run(guard + ['--version'], text=True, capture_output=True, timeout=90)
    if version.returncode or version.stdout.strip() != 'jaio ' + pin['version']:
        raise ValueError('jaio guarded launch failed: ' + version.stderr.strip()[:400])
    config = out / 'jaio.toml'
    with config.open('x', encoding='utf-8') as stream:
        stream.write(config_for(manifest['profile']))
    if not manifest['documents']:
        raise ValueError('no prose extracted; cannot claim analysis completed')
    completed = subprocess.run(guard + ['check', 'corpus', '--config', 'jaio.toml', '--format', 'json'],
                               cwd=out, text=True, capture_output=True, timeout=300)
    with (out / 'jaio.stderr.txt').open('x', encoding='utf-8') as stream:
        stream.write(completed.stderr)
    if completed.returncode not in (0, 1, 2) or not completed.stdout.strip().startswith('{'):
        raise ValueError('jaio failed without a JSON report: ' + completed.stderr[:300])
    report = json.loads(completed.stdout)
    write_json(out / 'jaio.raw.json', report)
    if report.get('schema_version') != 2:
        raise ValueError('unsupported jaio JSON schema')
    docs = {d['corpus']: d for d in manifest['documents']}
    findings = []
    for diagnostic in report['diagnostics']:
        mapped = map_diagnostic(diagnostic, docs)
        finding = {'rule_id': diagnostic['rule_id'], 'origin': 'jaio', 'severity': diagnostic['severity'],
                   'locations': mapped, 'review_questions': diagnostic.get('review_questions', []),
                   'measurements': diagnostic.get('measurements', []), 'limitations': diagnostic.get('limitations', [])}
        if any(k in diagnostic['rule_id'] for k in ('duplication', 'repeated-quote')):
            valid = [x for x in mapped if x.get('mapped')]
            finding['classification'], finding['classification_reason'] = duplicate_class(valid)
        findings.append(finding)
    findings.extend(supplementary(manifest))
    # 通常checkは上位3ペアを表示する。公式dumpで全ペアを別欄に残す。
    dump = subprocess.run(guard + ['dump', 'corpus', 'corpus', '--config', 'jaio.toml'],
                          cwd=out, text=True, capture_output=True, timeout=300)
    if dump.returncode not in (0, 1, 2) or not dump.stdout.strip().startswith('{'):
        raise ValueError('jaio dump corpus failed: ' + dump.stderr[:300])
    corpus = json.loads(dump.stdout)
    write_json(out / 'jaio.corpus.json', corpus)
    if corpus.get('kind') != 'jaio/dump-corpus' or corpus.get('version') != 2:
        raise ValueError('unsupported jaio dump corpus schema')
    same_context = (corpus['context']['config_fingerprint'] == report['context']['config_fingerprint']
                    and corpus['context']['sources'] == report['context']['sources'])
    pairs = []
    for pair in corpus['duplicates']:
        # 0.80未満を混ぜない。thresholdは実装検証済みの共通設定に固定する。
        if pair['score'] < 0.80:
            continue
        locations = [map_location({'file': pair[key], 'span': {'line': 1, 'col': 1}, 'approximate': True}, docs) for key in ('a', 'b')]
        for key, location in zip(('a', 'b'), locations):
            roles = {f['role'] for f in docs[pair[key]]['fragments']}
            if 'definition' in roles:
                location['role'] = 'definition_candidate'
            elif 'recap' in roles:
                location['role'] = 'recap'
        classification, reason = duplicate_class(locations)
        pairs.append({'origin': 'jaio/dump-corpus', 'similarity': pair['score'],
                      'intersection': pair['intersection'], 'union': pair['union'],
                      'locations': locations, 'classification': classification, 'review_question': reason,
                      'limitation': '文書全体の語彙類似度です。表示行は資料の入口で、重複区間そのものではありません。'})
    verify_inputs(manifest, out)
    if file_sha(out / 'manifest.json') != manifest_sha:
        raise ValueError('manifest changed during analysis; extract a fresh corpus')
    complete = (completed.returncode != 2 and report['summary'].get('analysis_complete') is True
                and dump.returncode != 2 and corpus.get('analysis_complete') is True and same_context)
    observed_version = report.get('tool', {}).get('version')
    if observed_version != pin['version']:
        complete = False
    result = {'schema_version': 1, 'runner_version': RUNNER_VERSION, 'analysis_complete': complete, 'completion_status': 'human_review_required',
              'profile': manifest['profile'], 'input_files': len(manifest['sources']), 'extracted_documents': len(docs),
              'protected_files': sum(s['status'] == 'protected_file' for s in manifest['sources']),
              'jaio_summary': report['summary'], 'jaio_context': report['context'],
              'rule_counts': dict(Counter(f['rule_id'] for f in findings)),
              'classification_counts': dict(Counter(f['classification'] for f in findings if 'classification' in f)),
              'duplication_pair_count': len(pairs), 'pair_classification_counts': dict(Counter(p['classification'] for p in pairs)),
              'duplication_pairs': pairs,
              'provenance': {'binary_sha256': pin['binary_sha256'], 'version': observed_version,
                             'config_sha256': file_sha(config), 'manifest_sha256': manifest_sha,
                             'runner_sha256': file_sha(Path(__file__)),
                             'network_guard': NETWORK_PROFILE, 'jaio_exit_code': completed.returncode,
                             'jaio_dump_exit_code': dump.returncode, 'check_dump_context_matches': same_context,
                             'source_and_corpus_hashes_verified_before_and_after': True},
              'limits': manifest['limits'], 'findings': findings}
    write_json(out / 'report.json', result)
    return result


def compare(inputs: list[Path], out: Path):
    manifests = [(p.resolve(strict=True), read_json(p / 'manifest.json')) for p in inputs]
    for path, manifest in manifests:
        verify_inputs(manifest, path)
    roots = sorted({root for _, manifest in manifests for root in manifest['roots']})
    out = exclusive_output(out, [Path(root) for root in roots])
    docs, sources = [], []
    for _, manifest in manifests:
        sources.extend(manifest['sources'])
        for item in manifest['documents']:
            doc = Document(item['source'], item['course'], item['medium'], item['unit'], [Fragment(**f) for f in item['fragments']])
            doc.source_root = item.get('source_root', '')
            docs.append(serialize_document(doc, out, len(docs) + 1))
    manifest = {'schema_version': 1, 'profile': 'combined', 'roots': roots, 'sources': sources, 'documents': docs,
                'limits': ['Combined cross-course candidates require pedagogical review.', 'Static extraction limits from each source manifest apply.']}
    write_json(out / 'manifest.json', manifest)
    return manifest


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    for command in ('extract', 'run'):
        item = sub.add_parser(command)
        item.add_argument('--profile', choices=('university', 'bootcamp'), required=True)
        item.add_argument('--root', type=Path, required=True)
        item.add_argument('--out', type=Path, required=True)
        item.add_argument('--book-root', type=Path, help='Bootcampだけ、最新の書籍作業版ディレクトリを明示する')
        if command == 'run':
            item.add_argument('--jaio', type=Path, required=True)
    item = sub.add_parser('analyze')
    item.add_argument('--out', type=Path, required=True)
    item.add_argument('--jaio', type=Path, required=True)
    item = sub.add_parser('compare')
    item.add_argument('--inputs', type=Path, nargs='+', required=True)
    item.add_argument('--out', type=Path, required=True)
    item.add_argument('--jaio', type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        if args.command in ('run', 'extract'):
            manifest = extract(args.profile, args.root, args.out, args.book_root)
        elif args.command == 'compare':
            manifest = compare(args.inputs, args.out)
        if args.command == 'extract':
            print(json.dumps({'input_files': len(manifest['sources']), 'extracted_documents': len(manifest['documents']), 'manifest': str(args.out / 'manifest.json')}, ensure_ascii=False))
            return 0
        result = analyze(args.out, args.jaio)
        print(json.dumps({k: result[k] for k in ('analysis_complete', 'completion_status', 'input_files', 'extracted_documents', 'rule_counts', 'duplication_pair_count', 'pair_classification_counts')}, ensure_ascii=False))
        return 0 if result['analysis_complete'] else 2
    except (ValueError, OSError, subprocess.TimeoutExpired) as error:
        print('error: ' + str(error), file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())
