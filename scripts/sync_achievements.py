#!/usr/bin/env python3
"""Copy saved achievement masters and placement metadata into the website."""

from hashlib import sha256
import json
from pathlib import Path
import re
import shutil

ROOT = Path(__file__).resolve().parents[1]
GALLERY = ROOT / 'public/badges/achievement-concepts'


def main():
    sections = re.findall(r"id: '([^']+)', title: '[^']+', data: '([^']+)'", (GALLERY / 'sections.js').read_text())
    if not sections:
        raise ValueError('No achievement sections found')
    # Validate every master before changing the public copy. An edited master
    # needs its crop/placement checked and its recorded hash updated first.
    prepared = []
    for section, variable in sections:
        masters = ROOT / 'output/imagegen/achievements' / section
        entries = json.loads((masters / 'concepts.json').read_text())
        for entry in entries:
            image = masters / (entry['id'] + '.png')
            if sha256(image.read_bytes()).hexdigest() != entry['sourceSha256']:
                raise ValueError(f'Changed master requires refitting: {image}')
        prepared.append((section, variable, masters, entries))
    for section, variable, masters, entries in prepared:
        target = GALLERY / section
        for entry in entries:
            output = target / entry['file']
            output.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(masters / (entry['id'] + '.png'), output)
        (target / 'concepts.js').write_text(f'window.{variable} = ' + json.dumps(entries, indent=2) + ';\n')
        shutil.copy2(masters / 'prompts.json', target / 'prompts.json')
    print(f'Synchronized {sum(len(row[3]) for row in prepared)} achievements across {len(prepared)} sections.')


if __name__ == '__main__':
    main()
