import urllib.request
import json

BASE = 'http://localhost:5000'
DEBUT = '2026-05-20'
FIN = '2026-05-26'

def fetch_json():
    url = f"{BASE}/api/rapports/bilan/data?debut={DEBUT}&fin={FIN}"
    print('Requesting JSON:', url)
    try:
        with urllib.request.urlopen(url, timeout=15) as r:
            print('STATUS', r.status)
            ct = r.getheader('Content-Type')
            print('Content-Type:', ct)
            data = r.read()
            try:
                obj = json.loads(data.decode('utf-8'))
                with open('scripts/bilan_data.json', 'w', encoding='utf-8') as f:
                    json.dump(obj, f, ensure_ascii=False, indent=2)
                print('WROTE scripts/bilan_data.json')
                print('RESPONSE:', obj if isinstance(obj, dict) else type(obj))
            except Exception as e:
                print('JSON PARSE ERROR', e)
                print(data[:500])
    except Exception as e:
        print('ERROR fetching JSON:', e)


def fetch_pdf():
    url = f"{BASE}/api/rapports/bilan?debut={DEBUT}&fin={FIN}"
    print('Requesting PDF:', url)
    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=30) as r:
            print('STATUS', r.status)
            ct = r.getheader('Content-Type')
            print('Content-Type:', ct)
            data = r.read()
            out = 'scripts/bilan_test.pdf'
            with open(out, 'wb') as f:
                f.write(data)
            print(f'WROTE {len(data)} bytes to {out}')
    except Exception as e:
        print('ERROR fetching PDF:', e)

if __name__ == '__main__':
    fetch_json()
    fetch_pdf()
