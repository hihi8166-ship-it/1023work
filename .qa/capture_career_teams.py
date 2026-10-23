from browser import Browser
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parent.parent
config=json.loads((ROOT/'data/career-menu.json').read_text(encoding='utf-8'))['design']
ids={item['link']['pageId'] for menu in config['header']['menus'] if menu['name']=='팀 소개' for item in menu['subMenus']}
pages=[page for page in config['pages'] if page['id'] in ids]
b=Browser();b.navigate('https://www.musinsacareers.com/ko/home')
out=ROOT/'.qa/pages/career-teams';out.mkdir(exist_ok=True)
for page in pages:
    html=b.evaluate('fetch('+json.dumps('/ko/'+page['path'])+').then(r=>r.text())')
    (out/(page['path']+'.html')).write_text(html,encoding='utf-8')
    print('Captured career team',page['name'],flush=True)
