"""無料枠（1モデル1日10回）対策: 複数のセリフを1回の呼び出しでまとめて作り、無音で分割する。
使い方: python3 tts_batch.py --model M --cvoice V --gvoice V [--group 5]"""
import argparse, os, subprocess, wave, numpy as np
import tts_gemini as T
R=24000
def split(pcm,n,min_gap=0.7):
    a=np.frombuffer(pcm,np.int16).astype(np.float32)
    hop=int(.02*R); env=np.array([np.abs(a[i:i+hop]).mean() for i in range(0,len(a),hop)])
    loud=env>200; segs=[];start=None;quiet=0
    for i,l in enumerate(loud):
        if l:
            if start is None: start=i
            quiet=0
        elif start is not None:
            quiet+=1
            if quiet*0.02>=min_gap: segs.append((start,i-quiet+1)); start=None; quiet=0
    if start is not None: segs.append((start,len(loud)))
    if len(segs)!=n: return None
    return [a[max(0,s*hop-int(.05*R)):e*hop+int(.1*R)].astype(np.int16).tobytes() for s,e in segs]
if __name__=='__main__':
    ap=argparse.ArgumentParser(); ap.add_argument('--model',required=True); ap.add_argument('--cvoice',required=True)
    ap.add_argument('--gvoice',required=True); ap.add_argument('--group',type=int,default=5); a=ap.parse_args()
    todo=[x for x in T.lines() if not os.path.exists(os.path.join(T.OUT,x[0]+'.wav'))]
    for spk in ('キャサリン','ジョージ'):
        mine=[x for x in todo if x[1]==spk]
        for i in range(0,len(mine),a.group):
            grp=mine[i:i+a.group]
            text=T.STYLE[spk].replace('# TRANSCRIPT','Leave a clear pause of about two seconds between lines.\n# TRANSCRIPT')
            text+="\n".join(x[4] for x in grp)
            data,mime=T.tts(a.model,a.cvoice if spk=='キャサリン' else a.gvoice,text)
            parts=split(data,len(grp))
            if parts is None:
                p=os.path.join(T.OUT,f'_batch_{grp[0][0]}.wav'); T.save_pcm(p,data)
                print(f'分割失敗 {grp[0][0]}〜{grp[-1][0]}（{p} に保存）',flush=True); continue
            for x,pcm in zip(grp,parts):
                T.save_pcm(os.path.join(T.OUT,x[0]+'.wav'),pcm)
                print(f'{x[0]} slot={x[3]-x[2]}s audio={len(pcm)/2/R:.1f}s',flush=True)
