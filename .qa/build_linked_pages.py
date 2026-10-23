"""Package captured corporate pages as a self-contained static multipage site."""
from pathlib import Path
from urllib.parse import urlparse, parse_qsl, urlencode, unquote, quote
import json,re,hashlib,subprocess

ROOT=Path(__file__).resolve().parent.parent
CAP=ROOT/'.qa/pages'
downloads={}
api=json.loads((ROOT/'data/api-manifest.json').read_text(encoding='utf-8')) if (ROOT/'data/api-manifest.json').exists() else {}
routes={'/':'/','/ko':'/','/company':'/company/','/business':'/business/','/impact':'/impact/','/newsroom/press':'/newsroom/press/','/newsroom/teammusinsa':'/newsroom/teammusinsa/','/newsroom/notice':'/newsroom/notice/','/newsroom/facts':'/newsroom/facts/','/career':'/career/'}
if (ROOT/'js/api-cache.js').exists():
    previous=re.search(r'window\.__COPY_ROUTES__=(.*?);\s*$',(ROOT/'js/api-cache.js').read_text(encoding='utf-8'),re.S)
    if previous:routes.update(json.loads(previous.group(1)))

def brand(text):
    text=re.sub(r'무신사(?!카피)','무신사카피',text)
    text=re.sub(r'MUSINSA(?!COPY)','MUSINSACOPY',text)
    text=re.sub(r'Musinsa(?!copy)','Musinsacopy',text)
    return text

def asset(url):
    parsed=urlparse(url)
    if parsed.hostname=='corp.musinsa.com':
        if parsed.path.startswith('/images/'):
            path='/assets'+unquote(parsed.path)
        elif parsed.path.startswith(('/_next/','/fonts/','/videos/')):
            path=unquote(parsed.path)
        else:return url
    elif parsed.hostname=='d3a9ls0n8d3jx7.cloudfront.net':
        path='/assets/content/'+unquote(parsed.path.split('/')[-1])
    else:return url
    destination=ROOT/path.lstrip('/')
    if not destination.exists():downloads[url]=str(destination)
    return path.replace(' ','%20')

def localize(value):
    if isinstance(value,dict):return {k:localize(v) for k,v in value.items()}
    if isinstance(value,list):return [localize(v) for v in value]
    if isinstance(value,str):
        if value.startswith('http'):
            if re.search(r'\.(?:jpg|jpeg|png|webp|gif|svg|mp4|webm)(?:\?|$)',value,re.I):return asset(value)
            return value
        # CMS articles contain embedded image tags, not just plain image fields.
        urls=set(re.findall(r'https://d3a9ls0n8d3jx7\.cloudfront\.net/[^\s"<>]+',value))
        for url in urls:
            if re.search(r'\.(?:jpg|jpeg|png|webp|gif|svg)(?:\?|$)',url,re.I):value=value.replace(url,asset(url))
        return brand(value)
    return value

def key(url):
    parsed=urlparse(url)
    query=urlencode(sorted(parse_qsl(parsed.query)))
    return parsed.path+('?' + query if query else '')

def script_text(text):
    text=brand(text)
    text=text.replace('"/images/','"/assets/images/').replace("'/images/","'/assets/images/").replace('`/images/','`/assets/images/')
    text=text.replace('https://www.musinsacareers.com/home','/career/')
    text=text.replace('AI 다운로드','SVG 다운로드')
    return text

for folder in sorted(CAP.iterdir()):
    if not folder.is_dir() or not (folder/'network.json').exists() or folder.name.startswith('career'):continue
    records=json.loads((folder/'network.json').read_text(encoding='utf-8'))
    for record in records:
        url=record['url'];parsed=urlparse(url)
        if parsed.hostname=='corp.musinsa.com' and parsed.path.startswith('/_next/') and record.get('file'):
            dest=ROOT/parsed.path.lstrip('/');dest.parent.mkdir(parents=True,exist_ok=True)
            text=(folder/record['file']).read_text(encoding='utf-8')
            if dest.suffix=='.js':text=script_text(text)
            dest.write_text(text,encoding='utf-8')
        elif parsed.hostname=='prd-new-api.corp.musinsa.com' and record.get('file'):
            try:body=json.loads((folder/record['file']).read_text(encoding='utf-8'))
            except json.JSONDecodeError:continue
            filename='/data/pages/'+hashlib.sha256(key(url).encode()).hexdigest()[:16]+'.json'
            dest=ROOT/filename.lstrip('/');dest.parent.mkdir(parents=True,exist_ok=True)
            dest.write_text(json.dumps(localize(body),ensure_ascii=False),encoding='utf-8')
            api[key(url)]=filename
        elif record['type'] in ['Image','Font','Media'] and record['status']==200:
            asset(url)

for folder in sorted(CAP.iterdir()):
    source=folder/'source.html'
    if not source.exists() or folder.name.startswith('career'):continue
    name=folder.name
    route='/'+name.replace('newsroom-','newsroom/').replace('newsroom/team','newsroom/teammusinsa')
    # Route maps for detail captures use their original pathname directly.
    info=json.loads((folder/'info.json').read_text(encoding='utf-8'))
    route=urlparse(info['url']).path
    routes[route]=route.rstrip('/')+'/'
    html=brand(source.read_text(encoding='utf-8')).replace('AI 다운로드','SVG 다운로드')
    html=re.sub(r'<script[^>]+src="https://static\.cloudflareinsights[^>]*>[\s\S]*?</script>','',html)
    html=re.sub(r'<script>\(function\(\)\{function c\(\)[\s\S]*?</script>','',html)
    html=html.replace('src="/images/','src="/assets/images/')
    html=html.replace('https://www.musinsacareers.com/home','/career/')
    html=html.replace('<head>','<head><script src="/js/api-cache.js"></script><script src="/js/collections.js"></script><script src="/js/main.js"></script>')
    html=html.replace('</head>','<link rel="stylesheet" href="/css/style.css"/></head>')
    dest=ROOT/route.strip('/')/'index.html';dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_text(html,encoding='utf-8')

# Collect image literals that become visible only after changing tabs or menus.
for script in (ROOT/'_next/static/chunks').glob('*.js'):
    text=script.read_text(encoding='utf-8')
    for path in set(re.findall(r'["\'`](/assets/images/[^"\'`$]+\.(?:jpg|jpeg|png|webp|svg|gif))',text)):
        asset('https://corp.musinsa.com'+path.replace('/assets/','/',1))

(ROOT/'data/api-manifest.json').write_text(json.dumps(api,ensure_ascii=False,indent=2),encoding='utf-8')
(ROOT/'js/api-cache.js').write_text('window.__COPY_API__='+json.dumps(api,ensure_ascii=False)+';\nwindow.__COPY_ROUTES__='+json.dumps(routes,ensure_ascii=False)+';\n',encoding='utf-8')

def archive_localize(value):
    if isinstance(value,dict):return {k:archive_localize(v) for k,v in value.items()}
    if isinstance(value,list):return [archive_localize(v) for v in value]
    if isinstance(value,str):
        if value.startswith('http'):
            if urlparse(value).hostname=='d3a9ls0n8d3jx7.cloudfront.net':
                path='/assets/content/'+unquote(urlparse(value).path.split('/')[-1])
                if (ROOT/path.lstrip('/')).is_file():return path
            return value
        return brand(value)
    return value
collections=CAP/'collections.json'
if collections.exists():
    body=archive_localize(json.loads(collections.read_text(encoding='utf-8')))
    (ROOT/'js/collections.js').write_text('window.__COPY_COLLECTIONS__='+json.dumps(body,ensure_ascii=False)+';\n',encoding='utf-8')
else:(ROOT/'js/collections.js').write_text('window.__COPY_COLLECTIONS__={};',encoding='utf-8')
(ROOT/'.qa/page-downloads.json').write_text(json.dumps([{'url':url,'target':target} for url,target in downloads.items()],ensure_ascii=False),encoding='utf-8')

# Restore shared wordmarks after scripts/styles were copied.
for script in (ROOT/'_next/static/chunks').glob('*.js'):
    script.write_text(script_text(script.read_text(encoding='utf-8')),encoding='utf-8')
home=ROOT/'index.html';html=home.read_text(encoding='utf-8')
html=html.replace('src="js/main.js"','src="/js/main.js"').replace('href="css/style.css"','href="/css/style.css"').replace('https://www.musinsacareers.com/home','/career/')
if '/js/api-cache.js' not in html:html=html.replace('<head>','<head><script src="/js/api-cache.js"></script>')
if '/js/collections.js' not in html:html=html.replace('<head>','<head><script src="/js/collections.js"></script>')
home.write_text(html,encoding='utf-8')
print('Built',len(routes),'routes;',len(api),'API responses;',len(downloads),'assets to download.')
