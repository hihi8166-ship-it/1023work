from browser import Browser
from pathlib import Path
import json,time
b=Browser();b.call('Runtime.enable');b.call('Network.enable');b.call('Network.setCacheDisabled',{'cacheDisabled':True});b.size(1440,900)
results={}
def go(path):
    b.call('Page.navigate',{'url':'http://127.0.0.1:8080'+path});time.sleep(2.5)
def check(name,value):
    results[name]=value
    print(name,json.dumps(value,ensure_ascii=False),flush=True)
    if value is False:raise AssertionError(name)
for label,path in [('Company','/company/'),('Business','/business/'),('Impact','/impact/'),('Newsroom','/newsroom/press/')]:
    go('/')
    b.evaluate('''[...document.querySelectorAll('a')].find(a=>a.textContent.trim()==='''+json.dumps(label)+''').click()''');time.sleep(2)
    check('navigation_'+label,b.evaluate('location.pathname')==path)
go('/')
check('career_menu_local',b.evaluate('document.querySelector(\'a[href="/career/"]\')?.href.includes(location.origin)') is True)
go('/newsroom/press/')
b.evaluate('''[...document.querySelectorAll('a')].find(a=>a.textContent.trim()==='2').click()''');time.sleep(2)
check('pagination',b.evaluate('location.search.includes("page=2") && document.body.innerText.includes("2026.09")'))
go('/newsroom/press/')
b.evaluate('''[...document.querySelectorAll('button')].find(a=>a.textContent.trim()==='#글로벌').click()''');time.sleep(2)
check('hashtag_filter',b.evaluate('location.search.includes("hashtagId=") && !document.body.innerText.includes("1,312건")'))
go('/business/')
b.evaluate('''[...document.querySelectorAll('button')].find(a=>a.textContent.trim()==='오프라인').click()''');time.sleep(1)
check('business_tab',b.evaluate('document.body.innerText.includes("오프라인") && document.querySelector("video").readyState>=2'))
go('/impact/')
check('report_anchor',b.evaluate('!!document.getElementById("report")'))
go('/career/faq/')
b.evaluate('document.querySelector("[class*=toggle__ToggleBlockTitleContainer]").click()');time.sleep(.4)
check('faq_open',b.evaluate('document.querySelector("[class*=toggle__ToggleBlockTitleContainer]").getAttribute("aria-expanded")==="true"'))
for path in ['/','/company/','/business/','/impact/','/newsroom/press/','/career/','/career/faq/','/career/jobs/240841/']:
    b.size(390,844);go(path)
    check('mobile_'+path,b.evaluate('document.documentElement.scrollWidth<=innerWidth'))
    b.screenshot('finished/mobile-'+(path.strip('/').replace('/','-') or 'home'))
go('/')
b.evaluate('document.querySelector("button img[alt=nav_icon]").closest("button").click()');time.sleep(1.5)
b.evaluate('''[...document.querySelectorAll('nav a')].find(a=>a.textContent.trim()==='Business').click()''');time.sleep(2)
check('mobile_navigation',b.evaluate('location.pathname==="/business/"'))
go('/career/')
b.evaluate('document.querySelector(\'button[data-testid="모바일_메뉴_버튼"]\').click()');time.sleep(.2)
check('career_mobile_menu',b.evaluate('!!document.querySelector(".career-overlay")'))
b.evaluate('document.querySelector(\'.career-overlay a[href="/career/faq/"]\').click()');time.sleep(1.5)
check('career_mobile_navigation',b.evaluate('location.pathname==="/career/faq/"'))
custom=[]
for script in ['js/main.js','js/career.js','js/api-cache.js','js/collections.js']:
    code=Path(script).read_text(encoding='utf-8')
    result=b.call('Runtime.compileScript',{'expression':code,'sourceURL':script,'persistScript':False})
    assert 'exceptionDetails' not in result, result
    custom.append(script)
check('javascript_syntax',custom)
results['browser_errors']=[e['params']['exceptionDetails'].get('exception',{}).get('description') for e in b.events if e.get('method')=='Runtime.exceptionThrown']
Path('.qa/navigation-result.json').write_text(json.dumps(results,ensure_ascii=False,indent=2),encoding='utf-8')
assert not results['browser_errors'],results['browser_errors']
print('PASS: navigation, pagination, filters, responsive layouts, mobile menus and JavaScript syntax',flush=True)
