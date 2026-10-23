"""Check the local homepage's files and cached content without installing a build tool."""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote
import json
import re

ROOT = Path(__file__).resolve().parent
missing = []

def local_file(value, parent=ROOT):
    if not value or value.startswith(('https:', 'http:', 'data:', '#', 'mailto:', 'tel:')):
        return
    value = unquote(value.split('?')[0])
    path = ROOT / value.lstrip('/') if value.startswith('/') else parent / value
    if not path.is_file():
        missing.append(str(path.relative_to(ROOT)))

class DocumentCheck(HTMLParser):
    def __init__(self, directory=ROOT):
        super().__init__()
        self.directory = directory
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag in ('script', 'img'):
            local_file(attrs.get('src', ''), self.directory)
        if tag == 'link' and attrs.get('rel') in ('stylesheet', 'icon', 'preload'):
            local_file(attrs.get('href', ''), self.directory)

source = (ROOT / 'index.html').read_text(encoding='utf-8')
DocumentCheck().feed(source)
documents = [ROOT / 'index.html']
for directory in ('company', 'business', 'impact', 'newsroom', 'career', 'ko'):
    documents.extend((ROOT / directory).rglob('index.html'))
for document in documents[1:]:
    DocumentCheck(document.parent).feed(document.read_text(encoding='utf-8'))
assert '<title>MUSINSACOPY</title>' in source
assert 'cloudflareinsights.com' not in source
assert 'js/main.js' in source
styles = list((ROOT / '_next').rglob('*.css')) + list((ROOT / 'css').glob('*.css'))
for css in styles:
    for url in re.findall(r'url\(([^)]+)\)', css.read_text(encoding='utf-8')):
        local_file(url.strip('\"\''), css.parent)

def content_check(value):
    if isinstance(value, dict):
        for key, item in value.items():
            if key.startswith('title') and isinstance(item, str):
                assert not re.search(r'무신사(?!카피)', item), item
            content_check(item)
    elif isinstance(value, list):
        for item in value:
            content_check(item)
    elif isinstance(value, str) and value.startswith('/assets/'):
        local_file(value)

banners = json.loads((ROOT / 'data/home-banners.json').read_text(encoding='utf-8'))
assert len(banners['data']['hero']) == 5
for path in (ROOT / 'data').glob('*.json'):
    content_check(json.loads(path.read_text(encoding='utf-8')))
manifest = json.loads((ROOT / 'data/api-manifest.json').read_text(encoding='utf-8'))
for file in manifest.values():
    local_file(file)
assert len(list((ROOT / 'career/jobs').glob('*/index.html'))) == 101
assert not missing, '\n'.join(missing)
print(f'PASS: {len(documents)} HTML documents, {len(styles)} stylesheets, scripts/images/fonts, {len(manifest)} API responses, 101 job details and branding')
