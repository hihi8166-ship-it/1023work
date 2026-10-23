"""Complete article routes referenced by search and pagination, preserving existing pages."""
from pathlib import Path
from urllib.parse import urlparse, unquote
from concurrent.futures import ThreadPoolExecutor, as_completed
from html import escape, unescape
import json,re,hashlib,urllib.request,time,argparse

parser=argparse.ArgumentParser()
parser.add_argument('--workers',type=int,default=1)
parser.add_argument('--delay',type=float,default=1.0)
options=parser.parse_args()

ROOT=Path(__file__).resolve().parent.parent
collections=json.loads((ROOT/'.qa/pages/collections.json').read_text(encoding='utf-8'))
manifest=json.loads((ROOT/'data/api-manifest.json').read_text(encoding='utf-8'))
groups={'press':'press-releases','teammusinsa':'team-musinsas','notice':'notices','facts':'announcements'}

def brand(value):
    value=re.sub(r'무신사(?!카피)','무신사카피',value)
    return re.sub(r'MUSINSA(?!COPY)','MUSINSACOPY',value)
def localize(value):
    if isinstance(value,dict):return {key:localize(item) for key,item in value.items()}
    if isinstance(value,list):return [localize(item) for item in value]
    if isinstance(value,str):
        if value.startswith(('http:','https:')):
            parsed=urlparse(value)
            path='/assets/content/'+unquote(parsed.path.split('/')[-1])
            return path if parsed.hostname=='d3a9ls0n8d3jx7.cloudfront.net' and (ROOT/path.lstrip('/')).is_file() else value
        return brand(value)
    return value

templates={}
for group in groups:
    source=next((ROOT/'newsroom'/group/'detail').glob('*/index.html'))
    html=source.read_text(encoding='utf-8')
    title=unescape(re.search(r'<title>([\s\S]*?)</title>',html).group(1))
    templates[group]=(source.parent.name,html,title)

def retrieve(task):
    group,endpoint,row=task
    identifier=str(row['id']);key='/api/public/'+endpoint+'/'+identifier
    output=ROOT/'data/articles'/group/(identifier+'.json')
    output.parent.mkdir(parents=True,exist_ok=True)
    if output.exists():return task,key,'/'+output.relative_to(ROOT).as_posix(),json.loads(output.read_text(encoding='utf-8'))
    if key in manifest:
        body=json.loads((ROOT/manifest[key].lstrip('/')).read_text(encoding='utf-8'))
    else:
        for attempt in range(3):
            try:
                time.sleep(options.delay)
                request=urllib.request.Request('https://prd-new-api.corp.musinsa.com'+key,headers={'User-Agent':'Mozilla/5.0'})
                with urllib.request.urlopen(request,timeout=35) as response:body=json.load(response)
                if not body.get('success'):raise RuntimeError(str(body)[:150])
                break
            except Exception as error:
                if attempt==2:raise
                delay=float(error.headers.get('Retry-After','60')) if getattr(error,'code',0)==429 else attempt+1
                if delay>0:time.sleep(delay)
    body=localize(body)
    output.write_text(json.dumps(body,ensure_ascii=False),encoding='utf-8')
    return task,key,'/'+output.relative_to(ROOT).as_posix(),body

tasks=[]
for group,endpoint in groups.items():
    for row in collections['/api/public/'+endpoint]['data']['data']:tasks.append((group,endpoint,row))
errors=[];created=0;completed=0
with ThreadPoolExecutor(max_workers=options.workers) as executor:
    for future in as_completed([executor.submit(retrieve,task) for task in tasks]):
        try:task,key,file,body=future.result()
        except Exception as error:errors.append(str(error));continue
        group,endpoint,row=task;identifier=str(row['id']);manifest[key]=file
        destination=ROOT/'newsroom'/group/'detail'/identifier/'index.html'
        if not destination.exists():
            old_id,html,old_title=templates[group]
            new_title=brand(body.get('data',{}).get('titleKo') or row.get('titleKo') or row.get('title') or old_title)
            def flight(match):
                data=json.loads(match.group(2))
                if len(data)>1 and isinstance(data[1],str):
                    data[1]=data[1].replace(json.dumps(old_id),json.dumps(identifier))
                    data[1]=data[1].replace(json.dumps(old_title,ensure_ascii=False),json.dumps(new_title,ensure_ascii=False))
                    data[1]=data[1].replace('/detail/'+old_id,'/detail/'+identifier)
                return match.group(1)+'self.__next_f.push('+json.dumps(data,ensure_ascii=False)+')'+match.group(3)
            html=re.sub(r'(<script[^>]*>)self\.__next_f\.push\(([\s\S]*?)\)(</script>)',flight,html)
            html=html.replace('/detail/'+old_id,'/detail/'+identifier)
            html=re.sub(r'<title>[\s\S]*?</title>',lambda _: '<title>'+escape(new_title)+'</title>',html,count=1)
            destination.parent.mkdir(parents=True,exist_ok=True);destination.write_text(html,encoding='utf-8');created+=1
        completed+=1
        if completed%150==0:print('Cached articles',completed,'/',len(tasks),flush=True)

(ROOT/'data/api-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
js=(ROOT/'js/api-cache.js').read_text(encoding='utf-8')
routes=json.loads(re.search(r'window\.__COPY_ROUTES__=(.*?);\s*$',js,re.S).group(1))
for group,endpoint,row in tasks:
    path='/newsroom/'+group+'/detail/'+str(row['id'])
    if (ROOT/path.lstrip('/')/'index.html').is_file():routes[path]=path+'/'
(ROOT/'js/api-cache.js').write_text('window.__COPY_API__='+json.dumps(manifest,ensure_ascii=False)+';\nwindow.__COPY_ROUTES__='+json.dumps(routes,ensure_ascii=False)+';\n',encoding='utf-8')
(ROOT/'.qa/archive-result.json').write_text(json.dumps({'articles':completed,'new_pages':created,'errors':errors},ensure_ascii=False,indent=2),encoding='utf-8')
print('Archive completed:',completed,'articles;',created,'new pages;',len(errors),'errors',flush=True)
if errors:raise SystemExit('\n'.join(errors[:5]))
