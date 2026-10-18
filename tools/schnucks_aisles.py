#!/usr/bin/env python3
"""Look up real aisle locations at Schnucks Ballwin (15425 Manchester Rd, store 106) via the public schnucks.com
search page in headless Chrome (store selected the same way a shopper would). Needs: google-chrome and
websocket-client (python3 -m venv /tmp/cdpvenv && /tmp/cdpvenv/bin/pip install websocket-client)."""
import json, subprocess, time, urllib.request, websocket, sys, threading
class C:
    def __init__(s, port=9334):
        s.p = subprocess.Popen(["google-chrome","--headless=new","--no-sandbox","--disable-gpu",f"--remote-debugging-port={port}",
          "--user-data-dir=/tmp/schprof-%d" % port,"--remote-allow-origins=*","--window-size=1280,1000",
          "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36","about:blank"],
          stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(3)
        tabs = json.load(urllib.request.urlopen(f"http://127.0.0.1:{port}/json"))
        s.ws = websocket.create_connection([t for t in tabs if t["type"]=="page"][0]["webSocketDebuggerUrl"], timeout=60)
        s.n=0; s.events=[]
    def cmd(s, m, **params):
        s.n+=1; s.ws.send(json.dumps({"id":s.n,"method":m,"params":params}))
        while True:
            r=json.loads(s.ws.recv())
            if r.get("id")==s.n: return r.get("result", r)
            s.events.append(r)
    def drain(s, secs):
        s.ws.settimeout(0.5); end=time.time()+secs
        while time.time()<end:
            try: s.events.append(json.loads(s.ws.recv()))
            except Exception: pass
        s.ws.settimeout(60)
    def ev(s, js):
        r=s.cmd("Runtime.evaluate", expression=js, awaitPromise=True, returnByValue=True)
        return r.get("result",{}).get("value", r)
    def close(s): s.p.terminate()

def setup():
    c=C(); c.cmd("Network.enable"); c.cmd("Page.enable")
    c.cmd("Page.navigate", url="https://schnucks.com/shop"); c.drain(10)
    c.ev("[...document.querySelectorAll('button,a')].find(b=>/Select a store/i.test(b.innerText)).click()"); c.drain(3)
    c.ev("(()=>{const i=[...document.querySelectorAll('input')].filter(i=>/Store Name/.test(i.placeholder)).find(i=>i.offsetParent); i.focus()})()")
    c.cmd("Input.insertText", text="Ballwin"); c.drain(1)
    for t in ("keyDown","keyUp"): c.cmd("Input.dispatchKeyEvent", type=t, key="Enter", code="Enter", windowsVirtualKeyCode=13)
    c.drain(5)
    r=c.ev("""(()=>{const bs=[...document.querySelectorAll('button')].filter(b=>/Set As My Store/.test(b.innerText)&&b.offsetParent);
     const hit=bs.find(b=>{let p=b; for(let k=0;k<6&&!/\\d{5}/.test(p.innerText);k++) p=p.parentElement; return /15425/.test(p.innerText)}); if(hit){hit.click();return 'ok'} return 'no'})()""")
    c.drain(5); assert r=='ok'; return c
def search_bodies(c, term, wait=12):
    c.events.clear()
    c.cmd("Page.navigate", url="https://schnucks.com/shop/search?searchTerm="+term.replace(' ','%20')); c.drain(wait)
    out=[]
    for e in c.events:
        if e.get("method")=="Network.responseReceived" and "/item-catalog-api/v1/items?" in e["params"]["response"]["url"]:
            b=c.cmd("Network.getResponseBody", requestId=e["params"]["requestId"])
            if "body" in b: out.append(json.loads(b["body"]))
    return out

# ---- CLI ----------------------------------------------------------------
# Usage: /tmp/cdpvenv/bin/python tools/schnucks_aisles.py "crushed tomatoes" "soy sauce" ...
# Prints the top in-store locations at Schnucks Ballwin (store 106) for each search term.
if __name__ == "__main__":
    terms = sys.argv[1:] or ["crushed tomatoes"]
    c = setup()
    try:
        for term in terms:
            items = [i for b in search_bodies(c, term, wait=8) for i in (b.get("data") or [])]
            print(f"\n== {term}")
            for i in items[:5]:
                loc = i.get("location") or {}
                print(f"   {i['name'][:55]:55} | {loc.get('longDescription')} | group={loc.get('groupDescription')} order={loc.get('groupDisplayOrder')}")
    finally:
        c.close()
