from browser import Browser
from pathlib import Path
import json,time
ROOT=Path(__file__).resolve().parent.parent
CAP=ROOT/'.qa/pages'
links=sorted({x['href'] for x in json.loads((CAP/'career/info.json').read_text(encoding='utf-8'))['links'] if '/ko/o/' in x['href']})
b=Browser();b.navigate('https://www.musinsacareers.com/ko/home')
out=CAP/'career-jobs';out.mkdir(exist_ok=True)
for start in range(0,len(links),8):
    batch=links[start:start+8]
    result=b.evaluate('Promise.all('+json.dumps(batch)+'.map(async url=>({url,html:await fetch(url).then(r=>r.text())})))')
    for entry in result:
        identifier=entry['url'].split('/')[-1]
        (out/(identifier+'.html')).write_text(entry['html'],encoding='utf-8')
    print('Captured job descriptions',min(start+8,len(links)),'/',len(links),flush=True)
