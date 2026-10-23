from browser import Browser
from pathlib import Path
import time,json
p=Path('_next/static/chunks/aee6c7720838f8a2.js')
original=p.read_text(encoding='utf-8')
debug='function rK(e){window.__hydration={type:typeof e.type==="string"?e.type:"component",props:Object.keys(e.pendingProps||{}),expected:typeof e.pendingProps?.children==="string"?e.pendingProps.children:null,node:rH?.outerHTML||rH?.textContent,previous:rH?.previousSibling?.outerHTML,parent:rH?.parentElement?.outerHTML?.slice(0,2500),ancestors:(()=>{let a=e,r=[];for(let i=0;i<8&&a;i++,a=a.return)r.push(typeof a.type==="string"?a.type:typeof a.type);return r})()};'
try:
    p.write_text(original.replace('function rK(e){',debug),encoding='utf-8')
    b=Browser();b.size(1440,900);b.call('Network.setCacheDisabled',{'cacheDisabled':True});b.navigate('http://127.0.0.1:8080/')
    print(json.dumps(b.evaluate('window.__hydration'),ensure_ascii=False,indent=2))
finally:
    p.write_text(original,encoding='utf-8')
