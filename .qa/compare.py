from browser import Browser
from pathlib import Path
import time,json
b=Browser()
b.call('Network.setCacheDisabled',{'cacheDisabled':True})
b.call('Runtime.enable');b.call('Log.enable')
results={}
for width,height in [(1440,900),(390,844)]:
    for label,url in [('reference','https://corp.musinsa.com/'),('local','http://127.0.0.1:8080/')]:
        b.size(width,height);b.navigate(url)
        # Freeze both hero sliders on the same first slide for a fair comparison.
        b.evaluate('''(() => {const button=document.querySelector("button[aria-label='Go to slide 1']");button?.dispatchEvent(new PointerEvent('pointerdown',{bubbles:true}));button?.click();for(let i=1;i<500;i++)clearInterval(i)})()''')
        time.sleep(2)
        b.screenshot(f'{label}-{width}-landing')
        results[f'{label}-{width}']=b.evaluate('({viewport:[innerWidth,innerHeight],overflow:document.documentElement.scrollWidth>innerWidth,main:document.querySelector("main").getBoundingClientRect().toJSON(),sections:[...document.querySelectorAll("section")].map(s=>({top:s.getBoundingClientRect().top,height:s.offsetHeight})),brokenImages:[...document.images].filter(i=>i.complete&&!i.naturalWidth).map(i=>i.src)})')
        if width==1440:
            for index,name in [(0,'company'),(1,'history'),(2,'business'),(4,'newsroom')]:
                b.evaluate(f'window.scrollTo(0,document.querySelectorAll("section")[{index}].getBoundingClientRect().top+scrollY)')
                time.sleep(2.5);b.screenshot(f'{label}-{width}-{name}')
        else:
            b.evaluate('window.scrollTo(0,0)');time.sleep(.5)
            b.evaluate('document.querySelector("button img[alt=\'nav_icon\']")?.closest("button").click()')
            time.sleep(2);b.screenshot(f'{label}-{width}-menu')
    print('Checked',width,flush=True)
errors=[]
for e in b.events:
    if e.get('method')=='Runtime.exceptionThrown':
        detail=e['params']['exceptionDetails']
        errors.append({'url':detail.get('url'),'description':detail.get('exception',{}).get('description',detail.get('text'))})
    if e.get('method')=='Network.responseReceived' and e['params']['response']['status']>=400:
        errors.append({'url':e['params']['response']['url'],'status':e['params']['response']['status']})
Path('.qa/comparison.json').write_text(json.dumps({'layouts':results,'errors':errors},ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'layouts':results,'errors':errors},ensure_ascii=False),flush=True)
