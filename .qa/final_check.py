from browser import Browser
from pathlib import Path
import json,time
ROOT=Path(__file__).resolve().parent.parent
b=Browser();b.call('Runtime.enable');b.call('Network.enable');b.call('Network.setCacheDisabled',{'cacheDisabled':True});b.size(1440,900)
results=[]
for path in ['/','/company/','/business/','/impact/','/newsroom/press/','/career/','/career/musinsatech/','/career/musinsa-commerce-main/','/career/29cm-commerce-main/']:
    b.events=[];b.call('Page.enable');b.call('Page.navigate',{'url':'http://127.0.0.1:8080'+path});time.sleep(2.5)
    b.evaluate('document.fonts.ready.then(()=>true)')
    record=b.evaluate('({path:location.pathname,title:document.title,height:document.documentElement.scrollHeight,overflow:document.documentElement.scrollWidth>innerWidth,brokenImages:[...document.images].filter(img=>img.complete&&!img.naturalWidth).map(img=>img.src)})')
    record['exceptions']=[e['params']['exceptionDetails'].get('exception',{}).get('description') for e in b.events if e.get('method')=='Runtime.exceptionThrown']
    record['http_errors']=[e['params']['response']['url'] for e in b.events if e.get('method')=='Network.responseReceived' and e['params']['response']['status']>=400]
    results.append(record);b.screenshot('finished/final-'+(path.strip('/').replace('/','-') or 'home'))
    print(record['path'],'exceptions',len(record['exceptions']),'HTTP errors',len(record['http_errors']),'overflow',record['overflow'],flush=True)
for script in ['js/main.js','js/career.js','js/api-cache.js','js/collections.js']:
    result=b.call('Runtime.compileScript',{'expression':(ROOT/script).read_text(encoding='utf-8'),'sourceURL':script,'persistScript':False})
    assert 'exceptionDetails' not in result,result
Path('.qa/final-check.json').write_text(json.dumps(results,ensure_ascii=False,indent=2),encoding='utf-8')
assert all(not row['exceptions'] and not row['http_errors'] and not row['brokenImages'] and not row['overflow'] for row in results),results
print('PASS: final desktop pages, team subpages, assets and custom JavaScript syntax')
