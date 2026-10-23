from browser import Browser
from pathlib import Path
import json,time,base64
ROOT=Path(__file__).resolve().parent.parent
CAP=ROOT/'.qa/pages'
b=Browser();b.size(1440,900)

# Career uses its own recruiting design; retain that design rather than the corporate header.
for route,name in [('https://www.musinsacareers.com/ko/home','career'),('https://www.musinsacareers.com/ko/benefit','career-benefit'),('https://www.musinsacareers.com/ko/faq','career-faq'),('https://www.musinsacareers.com/ko/o/240841','career-job')]:
    folder=CAP/name;folder.mkdir(exist_ok=True);b.events=[]
    b.navigate(route)
    b.screenshot('pages/'+name+'/reference')
    styles=b.evaluate(r'''[...document.styleSheets].filter(s=>s.ownerNode?.tagName==='STYLE').map(s=>{try{return [...s.cssRules].map(r=>r.cssText).join('\n')}catch{return ''}}).join('\n')''')
    (folder/'inline.css').write_text(styles,encoding='utf-8')
    (folder/'live.html').write_text(b.evaluate('document.documentElement.outerHTML'),encoding='utf-8')
    info=b.evaluate('({url:location.href,title:document.title,text:document.body.innerText,links:[...document.querySelectorAll("a")].map(a=>({text:a.innerText,href:a.href})),inputs:[...document.querySelectorAll("input")].map(i=>({type:i.type,id:i.id,placeholder:i.placeholder})),buttons:[...document.querySelectorAll("button")].map(i=>({text:i.innerText,name:i.name,testid:i.getAttribute("data-testid")}))})')
    (folder/'info.json').write_text(json.dumps(info,ensure_ascii=False,indent=2),encoding='utf-8')
    records=[]
    for i,entry in enumerate([e['params'] for e in b.events if e.get('method')=='Network.responseReceived']):
        response=entry['response'];record={'url':response['url'],'type':entry['type'],'status':response['status'],'mime':response.get('mimeType','')}
        if entry['type'] in ['Document','Stylesheet','XHR','Fetch'] and response['status']==200 and 'google' not in response['url']:
            try:
                body=b.call('Network.getResponseBody',{'requestId':entry['requestId']})
                filename=f'resource-{i}'
                (folder/filename).write_bytes(base64.b64decode(body['body']) if body.get('base64Encoded') else body['body'].encode('utf-8'))
                record['file']=filename
                if entry['type']=='Document':(folder/'source.html').write_text(body['body'],encoding='utf-8')
            except Exception:pass
        records.append(record)
    (folder/'network.json').write_text(json.dumps(records,ensure_ascii=False,indent=2),encoding='utf-8')
    print('Career captured',name,flush=True)

b.navigate('https://corp.musinsa.com/newsroom/press')
collections={}
for endpoint in ['press-releases','team-musinsas','notices','announcements']:
    value=b.evaluate('fetch('+json.dumps('https://prd-new-api.corp.musinsa.com/api/public/'+endpoint+'?lang=ko&page=1&limit=2000')+').then(r=>r.json())')
    collections['/api/public/'+endpoint]=value
    print('Collected',endpoint,len(value.get('data',{}).get('data',[])),flush=True)
(CAP/'collections.json').write_text(json.dumps(collections,ensure_ascii=False),encoding='utf-8')

# Fetch the actual document for every article linked from the initial newsroom lists.
links=set()
for folder in CAP.iterdir():
    if folder.is_dir() and folder.name.startswith('newsroom-') and (folder/'info.json').exists():
        for link in json.loads((folder/'info.json').read_text(encoding='utf-8'))['links']:
            if 'corp.musinsa.com/newsroom/' in link['href'] and '/detail/' in link['href']:links.add(link['href'])
for index,url in enumerate(sorted(links)):
    route=url.split('corp.musinsa.com')[-1]
    folder=CAP/('detail-'+route.replace('/','-').strip('-'));folder.mkdir(exist_ok=True)
    source=b.evaluate('fetch('+json.dumps(url)+').then(r=>r.text())')
    (folder/'source.html').write_text(source,encoding='utf-8')
    (folder/'info.json').write_text(json.dumps({'url':url,'title':route},ensure_ascii=False),encoding='utf-8')
    # The article API is loaded by the detail client, so capture it on real navigation.
    b.events=[];b.call('Page.navigate',{'url':url});time.sleep(1.3)
    records=[]
    b.evaluate('document.readyState')
    for i,entry in enumerate([e['params'] for e in b.events if e.get('method')=='Network.responseReceived']):
        response=entry['response'];record={'url':response['url'],'type':entry['type'],'status':response['status'],'mime':response.get('mimeType','')}
        if entry['type'] in ['Script','Stylesheet','XHR','Fetch'] and response['status']==200 and '_rsc=' not in response['url']:
            try:
                body=b.call('Network.getResponseBody',{'requestId':entry['requestId']})
                if not body.get('base64Encoded'):
                    filename=f'resource-{i}';(folder/filename).write_text(body['body'],encoding='utf-8');record['file']=filename
            except Exception:pass
        records.append(record)
    (folder/'network.json').write_text(json.dumps(records,ensure_ascii=False,indent=2),encoding='utf-8')
    print('Article',index+1,'/',len(links),route,flush=True)
