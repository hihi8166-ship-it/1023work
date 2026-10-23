from browser import Browser
from pathlib import Path
import json,time
ROOT=Path(__file__).resolve().parent.parent
results=[]
b=Browser();b.call('Runtime.enable');b.call('Network.enable');b.size(1440,900)
groups={'press':'press-releases','teammusinsa':'team-musinsas','notice':'notices','facts':'announcements'}
for group,endpoint in groups.items():
    files=sorted((ROOT/'data/articles'/group).glob('*.json'),key=lambda path:int(path.stem))
    sample=[files[0],files[len(files)//2]] if group=='press' else [files[0]]
    for file in sample:
        data=json.loads(file.read_text(encoding='utf-8'))['data']
        title=data.get('titleKo') or data.get('title')
        path='/newsroom/'+group+'/detail/'+file.stem+'/'
        b.events=[];b.call('Page.enable');b.call('Page.navigate',{'url':'http://127.0.0.1:8080'+path});time.sleep(2.5)
        shown=b.evaluate('document.body.innerText')
        errors=[e['params']['exceptionDetails'].get('exception',{}).get('description') for e in b.events if e.get('method')=='Runtime.exceptionThrown']
        record={'route':path,'title':title,'correct_article':bool(title and title in shown),'errors':errors}
        results.append(record);print(json.dumps(record,ensure_ascii=False),flush=True)
Path('.qa/archive-verification.json').write_text(json.dumps(results,ensure_ascii=False,indent=2),encoding='utf-8')
assert all(row['correct_article'] and not row['errors'] for row in results),results
print('PASS: generated old-article routes load their own content without JavaScript errors')
