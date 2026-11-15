"""audio/*.wav を各セリフの開始時刻に配置して narration.wav を作り、映像と合成する。
枠より長いセリフは最大1.25倍まで速める。それでも長いものは一覧に出す。"""
import os, subprocess, wave, numpy as np
from tts_gemini import lines
HERE=os.path.dirname(os.path.abspath(__file__)); A=os.path.join(HERE,'..','audio'); R=24000
TOTAL=298; mix=np.zeros(int(TOTAL*R)+R,np.float32); report=[]
def load(p):
    w=wave.open(p); return np.frombuffer(w.readframes(w.getnframes()),np.int16).astype(np.float32)/32768
def trim(a,th=0.01):
    idx=np.where(np.abs(a)>th)[0]
    return a[max(0,idx[0]-int(.05*R)):idx[-1]+int(.1*R)] if len(idx) else a
for fid,spk,s,e,line in lines():
    p=os.path.join(A,fid+'.wav')
    if not os.path.exists(p): report.append(f'{fid} 音声なし'); continue
    a=trim(load(p)); slot=e-s-0.3; dur=len(a)/R; speed=1.0
    if dur>slot:
        speed=min(1.25,dur/slot); tmp=p+'.fast.wav'
        subprocess.run(['ffmpeg','-y','-loglevel','error','-i',p,'-af',f'atempo={speed:.3f}',tmp],check=True)
        a=trim(load(tmp)); os.remove(tmp)
    st=int((s+0.15)*R); mix[st:st+len(a)]+=a
    report.append(f'{fid} 枠{e-s}s 音声{dur:.1f}s 速度x{speed:.2f}'+('  ※はみ出し' if len(a)/R>e-s else ''))
mix=np.clip(mix*0.95,-1,1)
out=os.path.join(HERE,'..','narration.wav')
with wave.open(out,'wb') as w: w.setnchannels(1); w.setsampwidth(2); w.setframerate(R); w.writeframes((mix*32767).astype(np.int16).tobytes())
print('\n'.join(report))
