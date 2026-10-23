import sys, json, time, urllib.request, base64
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / '.qa-tools'))
import websocket

class Browser:
    def __init__(self):
        targets=json.load(urllib.request.urlopen('http://localhost:9222/json'))
        target=next(t for t in targets if t['type']=='page')
        self.ws=websocket.create_connection(target['webSocketDebuggerUrl'],origin='http://localhost:9222',timeout=45)
        self.counter=0
        self.events=[]
    def call(self,method,params=None):
        self.counter+=1
        self.ws.send(json.dumps({'id':self.counter,'method':method,'params':params or {}}))
        while True:
            response=json.loads(self.ws.recv())
            if response.get('id')==self.counter:
                if 'error' in response: raise RuntimeError(response['error'])
                return response.get('result',{})
            self.events.append(response)
    def evaluate(self,expression):
        result=self.call('Runtime.evaluate',{'expression':expression,'returnByValue':True,'awaitPromise':True})
        if 'exceptionDetails' in result: raise RuntimeError(result['exceptionDetails'])
        return result['result'].get('value')
    def size(self,width,height):
        self.call('Emulation.setDeviceMetricsOverride',{'width':width,'height':height,'deviceScaleFactor':1,'mobile':width<700})
    def navigate(self,url):
        self.call('Page.enable')
        self.call('Network.enable')
        self.call('Page.navigate',{'url':url})
        time.sleep(7)
        self.evaluate('document.fonts.ready.then(()=>true)')
    def screenshot(self,name):
        data=self.call('Page.captureScreenshot',{'format':'png','captureBeyondViewport':False})
        target=Path(__file__).parent/(name+'.png')
        target.parent.mkdir(parents=True,exist_ok=True)
        target.write_bytes(base64.b64decode(data['data']))

if __name__=='__main__':
    b=Browser();b.size(1440,900)
    for label,url in [('original','https://corp.musinsa.com/'),('before','http://127.0.0.1:8080/')]:
        b.navigate(url);b.screenshot(label)
        print(label,b.evaluate('JSON.stringify({title:document.title,body:document.body.innerText.slice(0,700),fonts:document.fonts.status,sections:[...document.querySelectorAll("section")].map(s=>({top:s.getBoundingClientRect().top,height:s.offsetHeight})),heading:[...document.querySelectorAll("h1")].slice(0,3).map(e=>({text:e.innerText,font:getComputedStyle(e).font,rect:e.getBoundingClientRect().toJSON()}))})'))
