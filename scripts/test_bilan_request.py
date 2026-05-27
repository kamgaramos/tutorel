import urllib.request

url = 'http://localhost:5000/api/rapports/bilan?debut=2026-05-20&fin=2026-05-26'
print('Requesting', url)
try:
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req, timeout=15) as r:
        print('STATUS', r.status)
        headers = r.getheaders()
        for k, v in headers:
            print(f'{k}: {v}')
        data = r.read()
        out = 'bilan_test.pdf'
        with open(out, 'wb') as f:
            f.write(data)
        print(f'WROTE {len(data)} bytes to {out}')
except Exception as e:
    print('ERROR', e)
