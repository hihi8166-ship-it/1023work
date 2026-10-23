from browser import Browser
from pathlib import Path
import time,json
b=Browser();b.call('Runtime.enable');b.call('Network.setCacheDisabled',{'cacheDisabled':True})
b.size(1440,900);b.navigate('http://127.0.0.1:8080/')
b.evaluate('document.querySelector("button[aria-label=\'Go to slide 3\']").click()')
time.sleep(1.7)
assert b.evaluate('document.querySelector("main").innerText.includes("라이즈 은석")'), 'Hero slide 3 did not activate'
b.evaluate('document.querySelector("a[href=\'/business\']").click()');time.sleep(2)
assert b.evaluate('location.pathname==="/" && Math.abs(document.querySelector("#business").getBoundingClientRect().top-100)<10'), 'Business navigation failed'
b.evaluate('window.scrollTo(0,document.querySelector("#newsroom").getBoundingClientRect().top+scrollY)');time.sleep(1)
before=b.evaluate('document.querySelector("#newsroom .swiper-wrapper").style.transform')
b.evaluate('[...document.querySelectorAll("#newsroom button")].at(-1).click()');time.sleep(1)
after=b.evaluate('document.querySelector("#newsroom .swiper-wrapper").style.transform')
assert before!=after, 'News next button did not move slides'
b.size(390,844);b.navigate('http://127.0.0.1:8080/')
b.evaluate('document.querySelector("button img[alt=\'nav_icon\']").closest("button").click()');time.sleep(1.6)
assert b.evaluate('!!document.querySelector("button img[alt=\'close_icon\']")'), 'Mobile menu did not open'
b.screenshot('final-mobile-menu')
b.evaluate('[...document.querySelectorAll("nav a")].find(a=>a.getAttribute("href")==="/business").click()');time.sleep(2)
assert b.evaluate('!document.querySelector("button img[alt=\'close_icon\']")'), 'Mobile menu did not close on navigation'
assert b.evaluate('location.pathname==="/"'), 'Mobile link left the page'
b.evaluate('window.scrollTo(0,0)');time.sleep(1)
b.screenshot('final-mobile')
errors=[e['params']['exceptionDetails'].get('exception',{}).get('description') for e in b.events if e.get('method')=='Runtime.exceptionThrown']
assert not errors, errors
report={'hero_slides':'PASS','desktop_navigation':'PASS','news_carousel':'PASS','mobile_menu_open_close':'PASS','mobile_navigation':'PASS','browser_errors':errors}
Path('.qa/interactions.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(report))
