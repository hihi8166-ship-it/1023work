from browser import Browser
from pathlib import Path
import json,time
b=Browser();b.call('Network.setCacheDisabled',{'cacheDisabled':True});b.call('Runtime.enable');b.call('Log.enable');b.size(1440,900)
routes=['/','/company/','/business/','/impact/','/newsroom/press/','/newsroom/teammusinsa/','/newsroom/notice/','/newsroom/facts/','/newsroom/press/detail/1741/','/newsroom/teammusinsa/detail/76/','/career/','/career/benefit/','/career/faq/','/career/jobs/240841/']
results=[]
for route in routes:
    b.events=[]
    b.call('Page.enable');b.call('Network.enable');b.call('Page.navigate',{'url':'http://127.0.0.1:8080'+route});time.sleep(2.5)
    b.evaluate('document.fonts.ready.then(()=>true)')
    info=b.evaluate('({title:document.title,text:document.body.innerText.slice(0,650),length:document.body.innerText.length,height:document.documentElement.scrollHeight,overflow:document.documentElement.scrollWidth>innerWidth,broken:[...document.images].filter(i=>i.complete&&!i.naturalWidth).map(i=>i.src),headings:[...document.querySelectorAll("h1,h2")].slice(0,3).map(e=>e.innerText)})')
    info['route']=route
    info['errors']=[e['params']['exceptionDetails'].get('exception',{}).get('description',e['params']['exceptionDetails']['text']) for e in b.events if e.get('method')=='Runtime.exceptionThrown']
    info['http_errors']=[{'url':e['params']['response']['url'],'status':e['params']['response']['status']} for e in b.events if e.get('method')=='Network.responseReceived' and e['params']['response']['status']>=400]
    results.append(info);b.screenshot('finished/'+route.strip('/').replace('/','-') if route!='/' else 'finished/home')
    print(route,info['title'],'text',info['length'],'errors',len(info['errors']),'HTTP errors',len(info['http_errors']),'broken',len(info['broken']),flush=True)
Path('.qa/linked-smoke.json').write_text(json.dumps(results,ensure_ascii=False,indent=2),encoding='utf-8')
