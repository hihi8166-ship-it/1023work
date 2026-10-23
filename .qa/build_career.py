"""Finish the saved recruiting pages without discarding the existing corporate pages."""
from pathlib import Path
from urllib.parse import urlparse, unquote
from html import unescape, escape
import json,re,hashlib

ROOT=Path(__file__).resolve().parent.parent
CAP=ROOT/'.qa/pages'
downloads={}
asset_map={}
def brand(value):
    value=re.sub(r'무신사(?!카피)','무신사카피',value)
    return re.sub(r'MUSINSA(?!COPY)','MUSINSACOPY',value)

def asset(url,mime=''):
    url=unescape(url)
    if url.startswith('/cdn-cgi/'):
        url='https://www.musinsacareers.com'+url
    parsed=urlparse(url)
    if parsed.scheme not in ('http','https'):return url
    if url in asset_map:return asset_map[url]
    name=unquote(parsed.path.split('/')[-1])
    ext=Path(name).suffix.lower()
    if ext not in ('.png','.jpg','.jpeg','.webp','.gif','.svg','.woff','.woff2','.mp4'):
        ext='.svg' if 'svg' in mime else '.png'
        name='image'+ext
    name=re.sub(r'[^a-zA-Z0-9._-]','_',name)
    path='/assets/career/'+hashlib.sha256(url.encode()).hexdigest()[:12]+'-'+name
    asset_map[url]=path
    destination=ROOT/path.lstrip('/')
    if not destination.exists():downloads[url]=str(destination)
    return path

# Reuse the captured CSS, including dynamically created CSS-in-JS rules.
for folder in CAP.glob('career*'):
    manifest=folder/'network.json'
    if not manifest.exists():continue
    for record in json.loads(manifest.read_text(encoding='utf-8')):
        url=record['url'];parsed=urlparse(url)
        if record['type']=='Stylesheet' and record.get('file') and parsed.hostname=='www.musinsacareers.com':
            destination=ROOT/parsed.path.lstrip('/')
            destination.parent.mkdir(parents=True,exist_ok=True)
            destination.write_bytes((folder/record['file']).read_bytes())
        if record['type'] in ('Image','Font','Media') and record['status']==200:
            asset(url,record.get('mime',''))

def local_links(html):
    def link(match):
        before,value,after=match.groups()
        url=urlparse(unescape(value))
        path=url.path.rstrip('/')
        if url.hostname in ('corp.musinsa.com','newsroom.musinsa.com'):
            target='/newsroom/press/' if url.hostname.startswith('newsroom.') else ('/' if path in ('','/ko') else path+'/')
        elif url.hostname in ('www.musinsacareers.com','musinsacareers.com') or value.startswith('/ko'):
            if re.search(r'/o/\d+/apply',path):target='https://www.musinsacareers.com'+path
            elif re.search(r'/o/\d+$',path):target='/career/jobs/'+path.split('/')[-1]+'/'
            elif path.endswith('/benefit'):target='/career/benefit/'
            elif path.endswith('/faq'):target='/career/faq/'
            elif (CAP/'career-teams'/(path.split('/')[-1]+'.html')).exists():target='/career/'+path.split('/')[-1]+'/'
            elif path in ('','/ko','/ko/home','/home'):target='/career/'
            else:target='https://www.musinsacareers.com'+path
        else:return match.group()
        return before+target+('#'+url.fragment if url.fragment else '')+after
    return re.sub(r'(href=")([^"]+)(")',link,html)

def transform(source,route,inline_css=''):
    # Keep the captured document/CSS, replacing only hosted data/runtime dependencies.
    html=re.sub(r'<script\b[^>]*>[\s\S]*?</script>','',source,flags=re.I)
    html=re.sub(r'<link\b(?=[^>]*\bas="script")[^>]*>','',html,flags=re.I)
    html=re.sub(r'<noscript\b[^>]*>[\s\S]*?</noscript>','',html,flags=re.I)
    # Original styles are in the saved stylesheets and inline style snapshot.
    if inline_css:
        html=re.sub(r'<style\b[^>]*>[\s\S]*?</style>','',html,flags=re.I)
        html=html.replace('</head>','<style>'+inline_css+'</style></head>')
    html=re.sub(r'https://cdn\.jsdelivr\.net/gh/orioncactus/pretendard/[^"<>\s]+','/css/career-font.css',html)
    # Images without filename extensions are emitted by the original CDN proxy.
    def image(match):
        prefix,url,suffix=match.groups()
        if url.startswith(('http','/cdn-cgi/')):return prefix+asset(url)+suffix
        return match.group()
    html=re.sub(r'((?:src|poster|imageUrl)=")([^"]+)(")',image,html)
    html=re.sub(r'(<link[^>]+href=")(/cdn-cgi/[^"]+)(")',lambda m:m[1]+asset(m[2])+m[3],html)
    for url,path in sorted(asset_map.items(),key=lambda pair:-len(pair[0])):
        html=html.replace(url,path).replace(escape(url,quote=True),path)
    html=brand(local_links(html))
    html=html.replace('</head>','<link rel="stylesheet" href="/css/career-font.css"/><link rel="stylesheet" href="/css/career.css"/></head>')
    html=html.replace('</body>','<script src="/js/career.js"></script></body>')
    destination=ROOT/route.strip('/')/'index.html'
    destination.parent.mkdir(parents=True,exist_ok=True)
    destination.write_text(html,encoding='utf-8')

for name,route in [('career','/career/'),('career-benefit','/career/benefit/'),('career-faq','/career/faq/')]:
    folder=CAP/name
    source=(folder/'live.html').read_text(encoding='utf-8')
    css=(folder/'inline.css').read_text(encoding='utf-8')
    transform(source,route,css)

for path in (CAP/'career-jobs').glob('*.html'):
    transform(path.read_text(encoding='utf-8'),'/career/jobs/'+path.stem+'/')
for path in (CAP/'career-teams').glob('*.html'):
    transform(path.read_text(encoding='utf-8'),'/career/'+path.stem+'/')

# The original recruiting menu configuration supplies external/team menu links.
career=CAP/'career'
network=json.loads((career/'network.json').read_text(encoding='utf-8'))
boot=next(r for r in network if r['url'].endswith('/boot') and r.get('file'))
config=json.loads((career/boot['file']).read_text(encoding='utf-8'))['data']
(ROOT/'data/career-menu.json').write_text(brand(json.dumps(config,ensure_ascii=False)),encoding='utf-8')
(ROOT/'.qa/career-downloads.json').write_text(json.dumps([{'url':url,'target':path} for url,path in downloads.items()],ensure_ascii=False),encoding='utf-8')
print('Finished Career, benefits, FAQ and',len(list((CAP/'career-jobs').glob('*.html'))),'job detail pages;',len(downloads),'assets to download.')
