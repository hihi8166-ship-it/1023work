"""Rebuild the local homepage from the source and actual client-loaded content."""
from pathlib import Path
from urllib.parse import urlparse
import json, re, shutil, urllib.request, subprocess

root=Path(__file__).resolve().parent.parent
qa=root/'.qa'
def get(url,destination):
    destination.parent.mkdir(parents=True,exist_ok=True)
    if not destination.exists():
        command="Invoke-WebRequest -Uri '"+url.replace("'","''")+"' -OutFile '"+str(destination).replace("'","''")+"'"
        subprocess.run(['powershell','-NoProfile','-Command',command],check=True,capture_output=True)

html=(root/'reference.html').read_text(encoding='utf-8')
# Retain the real React client and its original scroll/slider behavior.
for script in re.findall(r'<script[^>]+src="(/_next/[^"]+)"',html):
    destination=root/script.lstrip('/')
    destination.parent.mkdir(parents=True,exist_ok=True)
    captured=qa/destination.name
    if captured.exists(): shutil.copyfile(captured,destination)
    else: get('https://corp.musinsa.com'+script,destination)
    text=destination.read_text(encoding='utf-8')
    # The brand replacement only affects visible Korean copy; endpoints stay intact.
    text=text.replace('무신사','무신사카피').replace('"/images/','"/assets/images/')
    destination.write_text(text,encoding='utf-8')

for css in re.findall(r'<link[^>]+href="(/_next/[^" ]+\.css)"',html):
    get('https://corp.musinsa.com'+css,root/css.lstrip('/'))
    content=(root/css.lstrip('/')).read_text(encoding='utf-8')
    for path in re.findall(r'url\(([^)]+)\)',content):
        path=path.strip('"\'')
        if path.startswith('../media/'):
            get('https://corp.musinsa.com/_next/static/media/'+path[9:],root/'_next/static/media'/path[9:])
        elif path.startswith('/fonts/'):
            get('https://corp.musinsa.com'+path,root/path.lstrip('/'))

assets={}
def localize(value):
    if isinstance(value,dict): return {key:localize(val) for key,val in value.items()}
    if isinstance(value,list): return [localize(val) for val in value]
    if isinstance(value,str):
        if value.startswith('https://d3a9ls0n8d3jx7.cloudfront.net/') and re.search(r'\.(jpg|jpeg|png|webp)(?:\?|$)',value,re.I):
            path='assets/content/'+urlparse(value).path.split('/')[-1]
            assets[value]=path
            get(value,root/path)
            return '/'+path
        # Preserve real destination URLs (including PDF filenames).
        if not value.startswith(('http://','https://')):
            return value.replace('무신사','무신사카피').replace('MUSINSA','MUSINSACOPY').replace('Musinsa','Musinsacopy')
    return value

data=root/'data';data.mkdir(exist_ok=True)
for source,target in [('home-banners','home-banners.json'),('impact-reports','impact-reports.json'),('latest','latest.json')]:
    body=localize(json.loads((qa/source).read_text(encoding='utf-8')))
    (data/target).write_text(json.dumps(body,ensure_ascii=False),encoding='utf-8')

# All responsive images referenced by the actual client components.
for script in (root/'_next/static/chunks').glob('*.js'):
    for path in set(re.findall(r'"(/assets/images/[^"\s]+\.(?:jpg|png|svg|webp))"',script.read_text(encoding='utf-8'))):
        get('https://corp.musinsa.com'+path.replace('/assets/','/'),root/path.lstrip('/'))

# Remove analytics and security challenges from the replica.
html=re.sub(r'<script[^>]+src="https://static\.cloudflareinsights[^>]*>[\s\S]*?</script>','',html)
html=re.sub(r'<script>\(function\(\)\{function c\(\)[\s\S]*?</script>','',html)
html=re.sub(r'<link[^>]+rel="icon"[^>]*>','',html)
html=html.replace('src="/images/','src="/assets/images/')
html=html.replace('<title>MUSINSA</title>','<title>MUSINSACOPY | 무신사카피</title>')
html=html.replace('content="무신사"','content="무신사카피"').replace('content="MUSINSA ','content="MUSINSACOPY ')
html=html.replace('<head>','<head><script src="js/main.js"></script>')
html=html.replace('</head>','<link rel="stylesheet" href="css/style.css"/></head>')
# Readable document formatting, while preserving the exact React hydration markup.
html=html.replace('><','>\n<')
(root/'index.html').write_text(html,encoding='utf-8')
print('Rebuilt full client, responsive images and all homepage API content:',len(assets),'content images')
