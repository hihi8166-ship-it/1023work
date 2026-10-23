from browser import Browser
from pathlib import Path
import time,json
b=Browser(); b.size(1440,900)
b.call('Network.setCacheDisabled',{'cacheDisabled':True})
b.call('Runtime.enable');b.call('Log.enable')
b.navigate('http://127.0.0.1:8080/');b.screenshot('after-desktop')
print(b.evaluate('JSON.stringify({title:document.title,text:document.body.innerText.slice(0,450),sections:[...document.querySelectorAll("section")].map(s=>({id:s.id,top:s.getBoundingClientRect().top,height:s.offsetHeight})),images:[...document.images].filter(i=>i.getBoundingClientRect().top<900&&i.getBoundingClientRect().bottom>0).map(i=>({src:i.src,complete:i.complete,width:i.naturalWidth,rect:i.getBoundingClientRect().toJSON()}))})'))
for e in b.events:
    if e.get('method') in ['Runtime.exceptionThrown','Log.entryAdded']:
        print('BROWSER',json.dumps(e['params'],ensure_ascii=False)[:1400])
    if e.get('method')=='Network.responseReceived' and e['params']['response']['status']>=400:
        print('HTTP ERROR',e['params']['response']['status'],e['params']['response']['url'])
