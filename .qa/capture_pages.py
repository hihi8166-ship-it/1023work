"""Capture each linked page, including content only loaded by its browser client."""
from browser import Browser
from pathlib import Path
import json,time,re,base64

ROOT=Path(__file__).resolve().parent.parent
OUT=ROOT/'.qa/pages'; OUT.mkdir(exist_ok=True)
b=Browser();b.size(1440,900);b.call('Network.setCacheDisabled',{'cacheDisabled':True})
routes=[('/company','company'),('/business','business'),('/impact','impact'),('/newsroom/press','newsroom-press'),('/newsroom/teammusinsa','newsroom-team'),('/newsroom/notice','newsroom-notice'),('/newsroom/facts','newsroom-facts'),('https://www.musinsacareers.com/home','career')]
manifest=[]
for route,name in routes:
    folder=OUT/name;folder.mkdir(exist_ok=True)
    b.events=[]
    url=route if route.startswith('http') else 'https://corp.musinsa.com'+route
    b.navigate(url)
    # Trigger lazy content, menus and page-specific API calls before collecting.
    height=b.evaluate('document.documentElement.scrollHeight')
    for y in range(0,min(height,30000),1000):
        b.evaluate(f'window.scrollTo(0,{y})');time.sleep(.12)
    time.sleep(1)
    b.evaluate('window.scrollTo(0,0)');time.sleep(1)
    b.screenshot('pages/'+name+'/desktop')
    (folder/'live.html').write_text(b.evaluate('document.documentElement.outerHTML'),encoding='utf-8')
    records=[]
    responses=[e['params'] for e in b.events if e.get('method')=='Network.responseReceived']
    for i,entry in enumerate(responses):
        response=entry['response'];record={'url':response['url'],'type':entry['type'],'status':response['status'],'mime':response.get('mimeType','')}
        if entry['type'] in ['Document','Script','Stylesheet','XHR','Fetch'] and response['status']==200 and '_rsc=' not in response['url']:
            try:
                body=b.call('Network.getResponseBody',{'requestId':entry['requestId']})
                filename=f'resource-{i}'
                value=base64.b64decode(body['body']) if body.get('base64Encoded') else body['body'].encode('utf-8')
                (folder/filename).write_bytes(value);record['file']=filename
                if entry['type']=='Document' and response['url'].split('#')[0].rstrip('/')==b.evaluate('location.href').split('#')[0].rstrip('/'):
                    (folder/'source.html').write_bytes(value)
            except Exception as error: record['error']=str(error)[:150]
        records.append(record)
    (folder/'network.json').write_text(json.dumps(records,ensure_ascii=False,indent=2),encoding='utf-8')
    info=b.evaluate('({url:location.href,title:document.title,text:document.body.innerText.slice(0,3500),links:[...document.querySelectorAll("a")].map(a=>({text:a.innerText,href:a.href})),height:document.documentElement.scrollHeight})')
    (folder/'info.json').write_text(json.dumps(info,ensure_ascii=False,indent=2),encoding='utf-8')
    manifest.append({'route':route,'name':name,'title':info['title'],'height':info['height'],'resources':len(records)})
    print(name,info['title'],info['height'],'resources',len(records),flush=True)
(OUT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
