import urllib.request, json, sys

url = 'http://127.0.0.1:5000/chat'
payload = {'mensaje':'Quiero un RPG'}
req = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'), headers={'Content-Type':'application/json'})
try:
    with urllib.request.urlopen(req, timeout=10) as r:
        print('STATUS', r.status)
        print(r.read().decode('utf-8'))
except Exception as e:
    print('ERROR', e)
    sys.exit(1)
