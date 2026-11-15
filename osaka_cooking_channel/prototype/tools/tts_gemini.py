"""Gemini TTS でナレーション音声を作り、試作動画に合成する。
APIキーは環境の Network secrets（host: generativelanguage.googleapis.com,
header: x-goog-api-key）からプロキシが自動で付ける。コードにキーは書かない。
使い方: python3 tts_gemini.py [--model MODEL] [--cvoice NAME] [--gvoice NAME] [--only C01,G02]
"""
import argparse, base64, json, os, subprocess, sys, urllib.request, urllib.error, wave
HERE=os.path.dirname(os.path.abspath(__file__))
OUT=os.path.join(HERE,'..','audio'); os.makedirs(OUT,exist_ok=True)
src=open(os.path.join(HERE,'make.py')).read()
ns={'PINK':0,'TEAL':0}; exec(src[src.index("C='キャサリン'"):src.index("cache={}")],ns)
STYLE={
 'キャサリン':"# AUDIO PROFILE\nCheerful woman in her early 30s from Osaka, an office worker.\n# DIRECTOR'S NOTES\nKansai-ben (Keihan accent), lively and quick, punchy tsukkomi.\n# TRANSCRIPT\n",
 'ジョージ':"# AUDIO PROFILE\nGentle, refreshing man in his early 30s.\n# DIRECTOR'S NOTES\nStandard Tokyo Japanese accent, calm and warm. Sincere even when saying odd things.\n# TRANSCRIPT\n",
}
def lines():
    n={'キャサリン':0,'ジョージ':0}
    for s,e,scene,who,spk,line,telop,pr in ns['cues']:
        if not line or line=='……': continue
        n[spk]+=1; yield (('C' if spk=='キャサリン' else 'G')+f'{n[spk]:02d}',spk,s,e,line)
def tts(model,voice,text):
    body={"contents":[{"parts":[{"text":text}]}],
          "generationConfig":{"responseModalities":["AUDIO"],
            "speechConfig":{"voiceConfig":{"prebuiltVoiceConfig":{"voiceName":voice}}}}}
    req=urllib.request.Request(f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
        data=json.dumps(body).encode(),headers={"Content-Type":"application/json"})
    import time
    for attempt in range(8):
        try:
            r=json.load(urllib.request.urlopen(req,timeout=120)); break
        except urllib.error.HTTPError as e:
            if e.code not in (429,500,502,503): raise
            msg=e.read().decode(errors='ignore'); wait=30*(attempt+1)
            import re as _re; m=_re.search(r'"retryDelay":\s*"(\d+)',msg)
            if m: wait=min(int(m.group(1))+2,65)
            wait=min(wait,65)
            print(f'  HTTP {e.code} -> {wait}s 待って再試行',flush=True); time.sleep(wait)
    else: raise SystemExit('再試行の上限')
    part=r["candidates"][0]["content"]["parts"][0]["inlineData"]
    return base64.b64decode(part["data"]), part.get("mimeType","")
def save_pcm(path,pcm,rate=24000):
    with wave.open(path,'wb') as w: w.setnchannels(1); w.setsampwidth(2); w.setframerate(rate); w.writeframes(pcm)
if __name__=='__main__':
    ap=argparse.ArgumentParser(); ap.add_argument('--model',required=True)
    ap.add_argument('--cvoice',required=True); ap.add_argument('--gvoice',required=True); ap.add_argument('--only',default='')
    a=ap.parse_args(); only=set(filter(None,a.only.split(',')))
    for fid,spk,s,e,line in lines():
        if only and fid not in only: continue
        if os.path.exists(os.path.join(OUT,fid+'.wav')) and not only: continue
        data,mime=tts(a.model,a.cvoice if spk=='キャサリン' else a.gvoice,STYLE[spk]+line)
        rate=int(mime.split('rate=')[1].split(';')[0]) if 'rate=' in mime else 24000
        p=os.path.join(OUT,fid+'.wav'); save_pcm(p,data,rate)
        dur=float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',p]))
        print(f'{fid} {spk} slot={e-s}s audio={dur:.1f}s {"OVER" if dur>e-s else ""}',flush=True)
