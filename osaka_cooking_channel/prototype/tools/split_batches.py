import os, wave, numpy as np
import tts_gemini as T
R=24000; hop=int(.02*R)
def load(p):
    w=wave.open(p); return np.frombuffer(w.readframes(w.getnframes()),np.int16)
def gaps(a,th=200):
    env=np.array([np.abs(a[i:i+hop].astype(np.float32)).mean() for i in range(0,len(a),hop)])
    loud=env>th; idx=np.where(loud)[0]; first,last=idx[0],idx[-1]
    g=[];i=first
    while i<=last:
        if not loud[i]:
            j=i
            while j<=last and not loud[j]: j+=1
            g.append((i,j)); i=j
        else: i+=1
    return first,last,g
todo=[x for x in T.lines() if not os.path.exists(os.path.join(T.OUT,x[0]+'.wav'))]
for f in sorted(os.listdir(T.OUT)):
    if not f.startswith('_batch_'): continue
    start=f[7:-4]; spk='キャサリン' if start[0]=='C' else 'ジョージ'
    mine=[x for x in todo if x[1]==spk]; k=[x[0] for x in mine].index(start); grp=mine[k:k+(5 if spk=='キャサリン' else 2)]
    a=load(os.path.join(T.OUT,f)); first,last,g=gaps(a)
    import itertools
    cand=[x for x in g if (x[1]-x[0])*.02>=0.25]
    chars=np.array([len(x[4]) for x in grp],float); tot=(last-first)*.02
    best=None
    for combo in itertools.combinations(cand,len(grp)-1):
        b=[first]+[c for gg in combo for c in gg]+[last+1]
        durs=np.array([(e-s_)*.02 for s_,e in zip(b[0::2],b[1::2])])
        exp=tot*chars/chars.sum()
        score=sum((e-s_)*.02 for s_,e in combo)-1.5*np.abs(np.log(durs/exp)).sum()
        if best is None or score>best[0]: best=(score,combo)
    cut=list(best[1])
    bounds=[first]+[c for gg in cut for c in gg]+[last+1]
    print(f, 'gaps(s):',[round((e-s)*.02,2) for s,e in cut])
    for x,(s,e) in zip(grp,zip(bounds[0::2],bounds[1::2])):
        seg=a[max(0,s*hop-int(.05*R)):e*hop+int(.1*R)]
        T.save_pcm(os.path.join(T.OUT,x[0]+'.wav'),seg.tobytes())
        print(f'  {x[0]} slot={x[3]-x[2]}s audio={len(seg)/R:.1f}s chars={len(x[4])}')
