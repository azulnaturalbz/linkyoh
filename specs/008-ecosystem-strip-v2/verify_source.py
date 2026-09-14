"""Read public hub artifacts; verify local copies and record immutable QA inputs."""

import hashlib
import json
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent / 'evidence'
BASE = 'https://silvatech.bz/brand/'


class StyleParser(HTMLParser):
    in_style = False
    css = ''

    def handle_starttag(self, tag, attrs):
        if tag == 'style':
            self.in_style = True

    def handle_endtag(self, tag):
        if tag == 'style':
            self.in_style = False

    def handle_data(self, data):
        if self.in_style:
            self.css += data


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    receipt = {'checked_at': datetime.now(timezone.utc).isoformat(), 'remote': {}, 'local_sha256': {}}
    documents = {}
    for name in ('ecosystem-strip.html', 'silvatech-ui.css'):
        with urlopen(BASE + name, timeout=30) as response:
            if response.status != 200 or response.url != BASE + name:
                raise ValueError('Unexpected published artifact response')
            documents[name] = response.read()
            if b'strip v2 2026-09-14' not in documents[name]:
                raise ValueError('Unexpected published artifact version')
            receipt['remote'][name] = {'url': response.url, 'status': response.status, 'sha256': sha(documents[name])}
    parser = StyleParser()
    parser.feed(documents['ecosystem-strip.html'].decode())
    copies = {
        'static/lab/assets/silvatech-ui.css': documents['silvatech-ui.css'],
        'static/css/ecosystem-strip.css': (parser.css.strip() + '\n').encode(),
    }
    for name, data in copies.items():
        if (ROOT / name).read_bytes() != data:
            raise ValueError('Published CSS mismatch: ' + name)
        receipt['local_sha256'][name] = sha(data)
    OUT.mkdir(exist_ok=True)
    fixture = ROOT / 'linkyohapp/test_fixtures/ecosystem-strip-v2.html'
    fixture.parent.mkdir(exist_ok=True)
    fixture.write_bytes(documents['ecosystem-strip.html'])
    receipt['reference_fixture'] = str(fixture.relative_to(ROOT))
    (OUT / 'source.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print(json.dumps(receipt, indent=2))


if __name__ == '__main__':
    main()
