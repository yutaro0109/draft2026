#!/usr/bin/env python3
"""Best-effort public HTML parser. Source markup/API has not been validated live.
Fails closed: never invents picks. Keeps previous data on parsing failures.
"""
import json,re,sys,datetime
from pathlib import Path
import requests
from bs4 import BeautifulSoup

BASE=Path(__file__).resolve().parent
URL="https://2026.draft-kaigi.jp/index.html"
TEAMS={"東北楽天":"楽天","楽天":"楽天","中日":"中日","千葉ロッテ":"ロッテ","ロッテ":"ロッテ","東京ヤクルト":"ヤクルト","ヤクルト":"ヤクルト","オリックス":"オリックス","広島東洋":"広島","広島":"広島","北海道日本ハム":"日本ハム","日本ハム":"日本ハム","横浜DeNA":"DeNA","DeNA":"DeNA","埼玉西武":"西武","西武":"西武","読売":"巨人","巨人":"巨人","福岡ソフトバンク":"ソフトバンク","ソフトバンク":"ソフトバンク","阪神":"阪神"}
def norm(s):
    return re.sub(r'[\s　・･]','',str(s)).replace('髙','高').replace('﨑','崎').replace('澤','沢')
def teamof(s):
    v=norm(s)
    for key in sorted(TEAMS,key=len,reverse=True):
        if norm(key) in v:return TEAMS[key]
    return None
def parse(html):
    soup=BeautifulSoup(html,"html.parser")
    for el in soup(['script','style','noscript','svg']):el.decompose()
    # Only the confirmed selections section is eligible; first-round bids are not confirmed picks.
    heading=soup.find(string=re.compile('これまでの全指名'))
    if not heading:return [],False
    parent=heading.parent
    following=[]
    for el in parent.next_elements:
        if getattr(el,'name',None) in ('h1','h2') and el is not parent:break
        if getattr(el,'name',None) in ('tr','li'):following.append(el.get_text(' ',strip=True))
    # Fallback: flattened text after the confirmed picks heading.
    if not following:
        text=soup.get_text('\n',strip=True).split('これまでの全指名',1)[-1]
        following=[x.strip() for x in text.splitlines() if x.strip()]
    out=[]
    for line in following:
        if not re.search(r'(?:育成\s*)?\d+\s*(?:位|巡目)',line):continue
        t=teamof(line)
        if not t:continue
        m=re.search(r'(育成)?\s*(\d+)\s*(?:位|巡目)',line)
        if not m:continue
        kind='育成' if m.group(1) or '育成' in line[:m.start()+2] else '支配下'
        rank=int(m.group(2))
        # Accept only unambiguous structured rows with a distinct player name.
        cleaned=re.sub(r'(育成)?\s*\d+\s*(?:位|巡目)',' ',line)
        cleaned=re.sub('|'.join(re.escape(x) for x in sorted(TEAMS,key=len,reverse=True)),' ',cleaned)
        words=[x for x in re.split(r'\s+',cleaned.strip()) if x]
        words=[w for w in words if w not in ('確定','指名','選択','投手','捕手','内野手','外野手','育成')]
        if not words:continue
        name=words[0]
        if not re.match(r'^[一-龯々ぁ-んァ-ヶー]{2,12}$',name):continue
        if any(x['team']==t and x['round']==rank and x['kind']==kind for x in out):continue
        out.append({'team':t,'round':rank,'kind':kind,'name':name,'school':' '.join(words[1:])})
    return out,True

def main():
    path=BASE/'data.json'
    prev=json.loads(path.read_text(encoding='utf8'))
    now=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat(timespec='seconds')
    try:
        res=requests.get(URL,timeout=20,headers={'User-Agent':'DraftDashboardPersonal/1.0 (low-frequency GitHub Actions fetch)'})
        res.raise_for_status()
        picks,found=parse(res.text)
        if not found:raise ValueError('Confirmed picks section not found; source markup may have changed')
        # Empty list is expected before the draft. After picks begin, never replace nonempty data with empty.
        if prev.get('picks') and not picks:raise ValueError('Parser returned zero picks after prior successful picks')
        # Prevent accidental loss of prior confirmed picks due to partial page responses.
        if len(picks)<len(prev.get('picks',[])):raise ValueError('Parsed fewer picks than previous data')
        # If content contains picks but parser did not recognize them, fail rather than pretending success.
        if not picks and ('指名開始前' not in res.text and '未確定' not in res.text):
            raise ValueError('Cannot verify empty draft board; inspect source format')
        data={'updated_at':now,'source':URL,'status':'waiting' if not picks else 'ok','picks':picks}
    except Exception as exc:
        data={**prev,'status':'error','error':str(exc),'checked_at':now}
        print('Fetch/parse failed:',exc,file=sys.stderr)
    path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print('status',data['status'],'picks',len(data['picks']))
if __name__=='__main__':main()
