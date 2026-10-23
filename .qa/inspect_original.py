from browser import Browser
from pathlib import Path
import json,time
b=Browser();b.size(1440,900);b.navigate('https://corp.musinsa.com/');time.sleep(4)
Path('.qa/original-live.html').write_text(b.evaluate('document.documentElement.outerHTML'),encoding='utf-8')
events=b.events
requests=[e['params'] for e in events if e.get('method')=='Network.responseReceived']
Path('.qa/network.json').write_text(json.dumps(requests,ensure_ascii=False,indent=2),encoding='utf-8')
for entry in requests:
    response=entry['response'];url=response['url']
    print(response['status'],entry['type'],url)
    if entry['type'] in ['Fetch','XHR','Script']:
        try:
            body=b.call('Network.getResponseBody',{'requestId':entry['requestId']})
            if not body.get('base64Encoded'):
                name=url.split('/')[-1].split('?')[0] or 'response'
                Path('.qa/'+name).write_text(body['body'],encoding='utf-8')
        except Exception as ex: print('Cannot read',str(ex)[:100])
b.screenshot('original-hero')
print('DOM TOP',b.evaluate('document.querySelector("body").innerHTML.slice(0,25000)'))
