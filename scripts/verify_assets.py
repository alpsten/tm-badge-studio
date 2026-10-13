#!/usr/bin/env python3
"""Validate the standalone website and retained source artwork without Pillow."""

from hashlib import sha256
from html.parser import HTMLParser
import json
from pathlib import Path
import re
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / 'public'
BADGES = PUBLIC / 'badges'


def require(path):
    if not path.is_file():
        raise ValueError(f'Missing asset: {path.relative_to(ROOT)}')
    return path


def load(path):
    return json.loads(require(path).read_text())


def assigned_json(path):
    return json.loads(require(path).read_text().split('=', 1)[1].strip().rstrip(';'))


def check(condition, message):
    if not condition:
        raise ValueError(message)


def check_hash(path, expected):
    check(sha256(require(path).read_bytes()).hexdigest() == expected, f'Artwork hash differs: {path.relative_to(ROOT)}')


class Links(HTMLParser):
    def __init__(self, page):
        super().__init__()
        self.page = page

    def handle_starttag(self, tag, attrs):
        for key, value in attrs:
            if key not in ('href', 'src') or not value:
                continue
            url = urlsplit(value)
            if url.scheme or url.netloc or not url.path:
                continue
            check(not url.path.startswith('/'), f'Root-relative URL breaks project Pages: {self.page}: {value}')
            target = (self.page.parent / unquote(url.path)).resolve()
            check(target.is_relative_to(PUBLIC), f'URL leaves public directory: {value}')
            require(target / 'index.html' if target.is_dir() else target)


def main():
    require(PUBLIC / 'index.html')
    require(PUBLIC / '.nojekyll')
    for page in PUBLIC.rglob('*.html'):
        Links(page).feed(page.read_text())
    for path in PUBLIC.rglob('*'):
        check(not path.is_symlink(), f'Pages asset is a symlink: {path}')

    manifest = load(BADGES / 'manifest.json')
    ids, exports = set(), set()
    for asset in manifest['assets']:
        check(asset['id'] not in ids, f'Duplicate badge: {asset["id"]}')
        ids.add(asset['id'])
        for size in manifest['sizes']:
            variant = asset['variants'][str(size)]
            path = require(BADGES / variant['path'])
            check(path.stat().st_size == variant['bytes'], f'Export size differs: {path}')
            check(variant['path'] not in exports, f'Duplicate export: {path}')
            exports.add(variant['path'])
    check(len(ids) == manifest['asset_count'], 'Manifest asset count differs')
    check(len(exports) == manifest['webp_file_count'], 'Manifest export count differs')

    corporations = load(BADGES / 'corporations.json')
    logos = load(BADGES / 'logos.json')
    check(assigned_json(BADGES / 'corporations.js') == corporations, 'Corporation JS/JSON differ')
    check(assigned_json(BADGES / 'logos.js') == logos, 'Logo JS/JSON differ')
    configured = {entry['corporation']: entry for entry in load(ROOT / 'scripts/badge_logos.json')['logos']}
    check({entry['id'] for entry in corporations['corporations']} == {entry['corporation'] for entry in logos['logos']} == set(configured), 'Corporation/logo catalogs differ')
    paths = list(corporations['modular_centers'].values()) + list(corporations['modular_frames'].values())
    for entry in corporations['corporations']:
        paths.extend(variant['badge'] for variant in entry['variants'])
        paths.append(entry['distinct_variant']['badge'])
    for root in corporations['ornament_roots'].values():
        paths.extend(f'{root}/{part}.webp' for part in ['wings', 'wings-small', 'wings-border', 'wings-small-border', 'crest', 'outer-border', 'bottom-plate'])
        paths.extend(f'{root}/rank-{rank}.webp' for rank in [1, 3, 5, 10, 20, 25, 50])
    for logo in logos['logos']:
        check_hash(ROOT / 'output/badges/logos/originals' / logo['source'], logo['source_sha256'])
        check(configured[logo['corporation']]['file'] == logo['source'], 'Configured logo source differs')
        paths.append(logo['path'])
    for size in manifest['sizes']:
        for path in paths:
            require(BADGES / str(size) / path)

    gallery = BADGES / 'achievement-concepts'
    sections = re.findall(r"id: '([^']+)', title: '[^']+', data: '([^']+)'", (gallery / 'sections.js').read_text())
    check(bool(sections), 'No achievement sections found')
    achievement_count = 0
    for section, variable in sections:
        page = gallery / section
        masters = ROOT / 'output/imagegen/achievements' / section
        entries = load(masters / 'concepts.json')
        require(page / 'index.html')
        check(assigned_json(page / 'concepts.js') == entries, f'Achievement metadata differs: {section}')
        check(f'window.{variable} =' in (page / 'concepts.js').read_text(), f'Wrong section variable: {section}')
        check(load(page / 'prompts.json') == load(masters / 'prompts.json'), f'Prompt copies differ: {section}')
        check(len({entry['id'] for entry in entries}) == len(entries), f'Duplicate achievement ID: {section}')
        for entry in entries:
            check_hash(page / entry['file'], entry['sourceSha256'])
            check_hash(masters / (entry['id'] + '.png'), entry['sourceSha256'])
        achievement_count += len(entries)

    for name in ('badge-original.png', 'badge-center-mask.png', 'badge-gold-frame-black-center.png', 'palette.json'):
        require(ROOT / 'output/badges' / name)
    for name in ('bottom-plate-silver', 'outer-border-silver', 'wings-ascendant-silver', 'wings-small-silver', 'crest-silver', 'laurels-silver', 'crown-silver', 'wide-hex-gold'):
        require(ROOT / 'output/badges/awards-kit/masters' / (name + '.png'))
    for name in ('bottom-plate-silver', 'wings-silver'):
        require(ROOT / 'output/badges/upgrade-sketch/masters' / (name + '.png'))
    total = sum(path.stat().st_size for path in PUBLIC.rglob('*') if path.is_file())
    print(f'Validated {len(logos["logos"])} logos, {achievement_count} achievements in {len(sections)} sections, {len(exports)} WebP exports, all HTML links, and source masters. Website: {total / 1024**2:.1f} MiB.')


if __name__ == '__main__':
    main()
