"""Resolve local documentary fragments without changing their source or economic data.

The caller must authorize the file before supplying its text. YAML selectors accept
keys, list indexes and declared list identities; a bare selector also searches
recursively, but never chooses silently between several matching passages.
"""
import re
import unicodedata
from urllib.parse import unquote

import yaml
from validate_stacks import UniqueKeyLoader


IDENTITY_KEYS = ('id', 'stack', 'bloc', 'scenario', 'capacite', 'capacite_id', 'capability', 'activite', 'activite_id')


def _pointer(path):
    return '/' + '/'.join(str(part).replace('~', '~0').replace('/', '~1') for part in path)


def _location(path):
    return ' / '.join(str(part) for part in path)


def _yaml_matches(data, fragment):
    # Slash selectors are root-relative. A slash escaped as ~1 remains one key.
    if '/' in fragment:
        parts = [part.replace('~1', '/').replace('~0', '~') for part in fragment.lstrip('/').split('/')]
        candidates = [((), data)]
        for part in parts:
            following = []
            for path, value in candidates:
                if isinstance(value, dict):
                    following.extend((path + (key,), child) for key, child in value.items() if str(key) == part)
                elif isinstance(value, list):
                    for index, child in enumerate(value):
                        # Canonical pointers returned as candidates must remain
                        # unambiguous even when a list identity is a numeric text.
                        numeric_pointer = fragment.startswith('/') and part.isdecimal()
                        identity = not numeric_pointer and isinstance(child, dict) and any(str(child.get(key)) == part for key in IDENTITY_KEYS if key in child)
                        if str(index) == part or identity:
                            following.append((path + (index,), child))
            candidates = following
        return candidates

    matches = {}

    def visit(value, path=(), ancestors=frozenset()):
        if not isinstance(value, (dict, list)) or id(value) in ancestors:
            return
        ancestors = ancestors | {id(value)}
        if isinstance(value, dict):
            if any(str(value.get(key)) == fragment for key in IDENTITY_KEYS if key in value):
                matches[path] = value
            for key, child in value.items():
                child_path = path + (key,)
                if str(key) == fragment:
                    matches[child_path] = child
                visit(child, child_path, ancestors)
        else:
            for index, child in enumerate(value):
                visit(child, path + (index,), ancestors)

    visit(data)
    # Historical references also use dotted paths. Resolve exact keys and native
    # identities first: a capability such as D01.c must never become D01 / c.
    if not matches and '.' in fragment:
        return _yaml_matches(data, fragment.replace('.', '/'))
    return list(matches.items())


def _slug(title):
    title = re.sub(r'<[^>]+>', '', title)
    title = re.sub(r'\[([^]]+)\]\([^)]*\)', r'\1', title)
    title = unicodedata.normalize('NFC', title).strip().lower()
    return re.sub(r'\s', '-', re.sub(r'[^\w\-\s]', '', title))


def _headings(content):
    lines = content.splitlines(keepends=True)
    headings, anchors = [], set()
    fence = None
    for index, line in enumerate(lines):
        marker = re.match(r'^ {0,3}(`{3,}|~{3,})', line)
        if marker:
            if fence is None:
                fence = marker.group(1)
            elif marker.group(1)[0] == fence[0] and len(marker.group(1)) >= len(fence):
                fence = None
            continue
        if fence is not None:
            continue
        match = re.match(r'^ {0,3}(#{1,6})\s+(.+?)\s*$', line)
        if match:
            level, title, start = len(match.group(1)), re.sub(r'\s+#+\s*$', '', match.group(2)), index
        elif index and re.match(r'^ {0,3}(=+|-+)\s*$', line) and lines[index - 1].strip():
            level, title, start = (1 if line.lstrip().startswith('=') else 2), lines[index - 1].strip(), index - 1
        else:
            continue
        base = _slug(title)
        anchor, suffix = base, 0
        while anchor in anchors:
            suffix += 1
            anchor = f'{base}-{suffix}'
        anchors.add(anchor)
        headings.append(dict(level=level, title=title, start=start, anchor=anchor))
    return lines, headings


def document_excerpt(content, suffix, fragment):
    """Return text plus optional focus metadata; absent fragments preserve the text."""
    if not fragment:
        return dict(content=content)
    fragment = unquote(fragment)
    focus = dict(status='missing', fragment=fragment, candidates=[])
    if suffix == '.yaml':
        try:
            data = yaml.load(content, Loader=UniqueKeyLoader)
            matches = _yaml_matches(data, fragment)
        except (yaml.YAMLError, ValueError):
            focus['status'] = 'invalid'
            return dict(content='', focus=focus)
        if len(matches) == 1:
            path, value = matches[0]
            focus.update(status='matched', location=_location(path), reference=_pointer(path))
            # Keep the selected key visible, including when its value is a scalar.
            excerpt = {path[-1]: value} if path and not isinstance(path[-1], int) else value
            return dict(content=yaml.safe_dump(excerpt, allow_unicode=True, sort_keys=False, width=100), focus=focus)
        if matches:
            focus.update(status='ambiguous', candidates=[dict(location=_location(path), reference=_pointer(path)) for path, _ in matches])
    elif suffix == '.md':
        lines, headings = _headings(content)
        target = _slug(fragment)
        matches = [item for item in headings if item['anchor'] == target]
        if len(matches) == 1:
            item = matches[0]
            end = next((other['start'] for other in headings if other['start'] > item['start'] and other['level'] <= item['level']), len(lines))
            focus.update(status='matched', location=item['title'], reference=item['anchor'], line_start=item['start'] + 1, line_end=end)
            return dict(content=''.join(lines[item['start']:end]).rstrip() + '\n', focus=focus)
    else:
        focus['status'] = 'unsupported'
    return dict(content='', focus=focus)
