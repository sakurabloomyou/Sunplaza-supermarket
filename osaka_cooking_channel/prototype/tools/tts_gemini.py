"""Gemini TTS でナレーション音声を作り、試作動画に合成する。
APIキーは環境の Network secrets（host: generativelanguage.googleapis.com,
header: x-goog-api-key）からプロキシが自動で付ける。コードにキーは書かない。
使い方: python3 tts_gemini.py [--model MODEL] [--cvoice NAME] [--gvoice NAME] [--only C01,G02]
"""
import argparse, base64, json, os, subprocess, sys, urllib.request, wave
HERE=os.path.dirname(os.path.abspath(__file__))
OUT=os.path.join(HERE,'..','audio'); os.makedirs(OUT,exist_ok=True)
src=open(os.path.join(HERE,'make.py')).read()
ns={'PINK':0,'TEAL':0}; exec(src[src.index("C='キャサリン'"):src.index("cache={}")],ns)
STYLE={
 'キャサリン':"大阪出身の30代前半の女性OLが、大阪弁（京阪式アクセント）で話します。テンポよく、明るく、ツッコミは勢いよく。次のセリフを読んでください：",
 'ジョージ':"30代前半の爽やかで穏やかな男性が、標準語（東京式アクセント）で話します。次のセリフを読んでください：",
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
    r=json.load(urllib.request.urlopen(req,timeout=120))
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
        data,mime=tts(a.model,a.cvoice if spk=='キャサリン' else a.gvoice,STYLE[spk]+line)
        rate=int(mime.split('rate=')[1].split(';')[0]) if 'rate=' in mime else 24000
        p=os.path.join(OUT,fid+'.wav'); save_pcm(p,data,rate)
        dur=float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',p]))
        print(f'{fid} {spk} slot={e-s}s audio={dur:.1f}s {"OVER" if dur>e-s else ""}',flush=True)
