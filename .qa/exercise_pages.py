from browser import Browser
from pathlib import Path
import time,json
b=Browser();b.size(1440,900);b.call('Runtime.enable');b.call('Network.enable');b.call('Network.setCacheDisabled',{'cacheDisabled':True})
report={}
def go(path):
    b.call('Page.navigate',{'url':'http://127.0.0.1:8080'+path});time.sleep(2)
def event_errors():
    return [e['params']['exceptionDetails'].get('exception',{}).get('description') for e in b.events if e.get('method')=='Runtime.exceptionThrown']
go('/newsroom/press/')
report['newsroom_inputs']=b.evaluate('[...document.querySelectorAll("input")].map(i=>({type:i.type,placeholder:i.placeholder}))')
report['newsroom_buttons']=b.evaluate('[...document.querySelectorAll("button")].map(i=>({text:i.textContent.trim(),label:i.getAttribute("aria-label")}))')
# Use native input events rather than assigning a React-controlled value directly.
b.evaluate('document.querySelector("input[placeholder*=검색]").focus()')
b.call('Input.insertText',{'text':'아디다스'})
b.call('Input.dispatchKeyEvent',{'type':'keyDown','key':'Enter','code':'Enter','windowsVirtualKeyCode':13});b.call('Input.dispatchKeyEvent',{'type':'keyUp','key':'Enter','code':'Enter','windowsVirtualKeyCode':13})
time.sleep(1.5)
report['search_result']=b.evaluate('document.body.innerText.slice(0,1800)')
report['api_queries']=[e['params']['request']['url'] for e in b.events if e.get('method')=='Network.requestWillBeSent' and ('blob:' in e['params']['request']['url'] or 'api/public' in e['params']['request']['url'])][-10:]
go('/career/')
initial=b.evaluate('document.querySelectorAll("[data-testid=공고_아이템]:not([hidden])").length')
b.evaluate('document.querySelector(\'input[id*="29CM"]\').click()');time.sleep(.3)
report['career_filter']={'before':initial,'after':b.evaluate('document.querySelectorAll("[data-testid=공고_아이템]:not([hidden])").length')}
go('/career/faq/')
b.evaluate('document.querySelector("[class*=toggle__ToggleBlockTitleContainer]").click()');time.sleep(.3)
report['faq']=b.evaluate('({expanded:document.querySelector("[class*=toggle__ToggleBlockTitleContainer]").getAttribute("aria-expanded"),height:document.querySelector("[class*=toggle__ToggleContentsContainer]").getBoundingClientRect().height})')
go('/business/')
report['video']=b.evaluate('({video:document.querySelector("video")?.src,ready:document.querySelector("video")?.readyState})')
report['business_buttons']=b.evaluate('[...document.querySelectorAll("button")].map(i=>i.textContent.trim()).filter(Boolean)')
report['errors']=event_errors()
Path('.qa/exercise-result.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(report,ensure_ascii=False),flush=True)
