import urllib.request,urllib.error,json
url='https://prd-new-api.corp.musinsa.com/api/public/press-releases/1731'
request=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0'})
try:
    response=urllib.request.urlopen(request,timeout=20)
except urllib.error.HTTPError as error:
    response=error
print('status',response.status)
print(json.dumps({key:value for key,value in response.headers.items() if any(item in key.lower() for item in ['retry','rate','limit'])}))
