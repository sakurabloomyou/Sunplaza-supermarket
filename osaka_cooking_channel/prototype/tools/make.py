import math, subprocess, re
from PIL import Image, ImageDraw, ImageFont, ImageFilter
W,H,FPS=1280,720,12
F='/usr/share/fonts/truetype/ipafont-gothic/ipag.ttf'
def font(sz): return ImageFont.truetype(F,sz)
both=Image.open('both.png')
bw,bh=both.size
cath=both.crop((0,0,505,bh)); geo=both.crop((470,0,bw,bh))
def fade_edge(img,side):
    a=img.getchannel('A'); w,h=img.size; m=Image.new('L',(w,h),255); d=ImageDraw.Draw(m)
    for i in range(30):
        x = w-1-i if side=='r' else i
        d.line([(x,0),(x,h)],fill=int(255*i/30))
    from PIL import ImageChops
    img=img.copy(); img.putalpha(ImageChops.multiply(a,m)); return img
cath=fade_edge(cath,'r'); geo=fade_edge(geo,'l')
def sc(img,h): return img.resize((int(img.width*h/img.height),h),Image.LANCZOS)
CATH=sc(cath,560); GEO=sc(geo,560); BOTH=sc(both,560)

PINK=(236,112,150); TEAL=(38,150,150); CREAM=(250,240,230); INK=(70,50,60)

def logo(d,cx,cy,s=1.0,sub=True):
    def t(txt,sz,col,y,stroke=0):
        f=font(int(sz*s)); w=d.textlength(txt,font=f)
        d.text((cx-w/2,y),txt,font=f,fill=col,stroke_width=stroke,stroke_fill=(255,255,255))
    f=font(int(110*s)); mw=d.textlength('ええやん適当で',font=f)
    fs=font(int(38*s)); d.text((cx-mw/2,cy-int(55*s)),'キャサリンの',font=fs,fill=TEAL,stroke_width=3,stroke_fill='white')
    d.text((cx-mw/2,cy),'ええやん適当で',font=f,fill=PINK,stroke_width=int(6*s),stroke_fill='white')
    if sub: t('OL平日ごはん',55,TEAL,cy+int(125*s),3)

def bg_super(section):
    im=Image.new('RGB',(W,H),(253,236,240)); d=ImageDraw.Draw(im)
    d.rectangle([0,560,W,H],fill=(240,225,215))
    cols={'野菜':[(120,190,110),(230,200,120),(170,120,190)],'精肉':[(235,150,150),(220,120,120),(245,190,180)],
          '豆腐・卵・チーズ':[(250,250,240),(250,220,120),(245,200,90)],'乾麺':[(200,170,120),(230,210,170),(180,150,110)],
          'カレールウ':[(200,50,50),(230,160,60),(180,60,40)],'レジ':[(200,200,210),(180,180,200),(210,210,220)],'入口':[(200,230,220),(230,220,200),(220,200,230)]}[section]
    for row,y in enumerate([150,290,430]):
        d.rectangle([0,y+105,W,y+120],fill=(210,180,170))
        for i,x in enumerate(range(20,W,70)):
            c=cols[(i+row)%3]; d.rounded_rectangle([x,y+30,x+55,y+105],8,fill=c,outline=(255,255,255),width=2)
    d.rounded_rectangle([W//2-200,20,W//2+200,95],20,fill=TEAL)
    f=font(46); w=d.textlength(section,font=f); d.text((W//2-w/2,32),section,font=f,fill='white')
    return im
def bg_kitchen():
    im=Image.new('RGB',(W,H),(255,244,236)); d=ImageDraw.Draw(im)
    for x in range(0,W,80):
        for y in range(0,430,80): d.rectangle([x+2,y+2,x+78,y+78],outline=(245,215,215),width=2)
    d.rectangle([0,430,W,H],fill=(250,215,220)); d.rectangle([0,430,W,460],fill=(255,255,255))
    d.rounded_rectangle([780,370,1180,440],12,fill=(200,200,205))
    for cx in (880,1080): d.ellipse([cx-55,380,cx+55,420],outline=(90,90,100),width=4)
    return im
def bg_dining():
    im=Image.new('RGB',(W,H),(250,240,225)); d=ImageDraw.Draw(im)
    d.rectangle([0,0,W,60],fill=(240,225,205))
    d.rounded_rectangle([340,470,940,520],15,fill=(200,150,110)); d.rectangle([380,520,410,H],fill=(180,130,95)); d.rectangle([870,520,900,H],fill=(180,130,95))
    return im
def bg_title():
    im=Image.new('RGB',(W,H),(252,228,236)); d=ImageDraw.Draw(im)
    for i in range(0,W+H,60): d.line([(i,0),(i-H,H)],fill=(255,240,245),width=20)
    return im

def prop(d,label,x,y,color):
    d.rounded_rectangle([x-110,y-60,x+110,y+60],25,fill=color,outline='white',width=5)
    f=font(34); 
    lines=label.split('\n')
    for i,l in enumerate(lines):
        w=d.textlength(l,font=f); d.text((x-w/2,y-20*len(lines)+i*40+2),l,font=f,fill='white',stroke_width=2,stroke_fill=INK)

def wrap(text,f,maxw,d):
    out=[];cur=''
    for ch in text:
        if d.textlength(cur+ch,font=f)>maxw: out.append(cur);cur=ch
        else: cur+=ch
    out.append(cur); return out

# cues: (start, end, scene, who_on_screen, speaker, line, telop, prop)
C='キャサリン'; G='ジョージ'
cues=[
(0,5,'title',None,None,'','',None),
(5,12,('super','入口'),'C',C,'ちょっと聞いて！ うちの課長、お昼に家系ラーメン食べに行ってん','今日の愚痴',None),
(12,20,('super','野菜'),'C',C,'2時間半、帰ってこおへんかってん。2時間半やで？','昼休み＝2時間半',('玉ねぎ',(190,140,90))),
(20,26,('super','野菜'),'C',C,'戻ってきて何て言うた思う？『いや〜並んでてさ』やて','「並んでてさ」',('セリ',(90,170,90))),
(26,33,('super','野菜'),'C',C,'旅行行ってたんか！ ほんならお土産はどこやねん！','旅行行ってたんか！',('セリ',(90,170,90))),
(33,41,('super','精肉'),'C',C,'その間の電話、全部うちが取ったんよ。『席を外しております』って何回言うたか','「席を外しております」×∞',('豚こま',(220,120,130))),
(41,47,('super','豆腐・卵・チーズ'),'C',C,'チーズものせたいな…いや、やめとこ。脂は課長だけで十分や','',('チーズ',(235,180,60))),
(47,52,('super','乾麺'),'C',C,'麺の話聞いたら、麺の口になってしもた。悔しい','麺の口',('そば\n(乾麺)',(160,120,80))),
(52,56,('super','カレールウ'),'C',C,'並ばんでも食べれる麺にしたろ','',('カレールウ',(200,50,50))),
(56,60,('super','レジ'),'C',C,'よっしゃ、帰ろ','',None),
(60,65,'kitchen','C',C,'そんなわけで今日は、せりカレーそばを作ろかな','せりカレーそば',None),
(65,70,'kitchen','C',C,'よっしゃ、いくで！','エプロン装着！',('エプロン\n装着',PINK)),
(70,85,'kitchen','C',C,'材料はこれ。ほぼ切って入れるだけ','材料（2人分）',('材料一覧',TEAL)),
(85,105,'kitchen','C',C,'玉ねぎはくし切り。…あかん、目にしみる。コンタクトの時は全然平気やったのに、ICLしてから弱くなってん。みんなどう対策してんの？','みんなの対策、コメントで教えて！',('玉ねぎ1/2\nくし切り',(190,140,90))),
(105,120,'kitchen','C',C,'セリは5センチくらい。根っこも入れるで。ここがおいしいとこやから、捨てたらもったいない','根っこも入れる！',('セリ 5cm\n根っこも',(90,170,90))),
(120,130,'kitchen','C',C,'根っこまで大事にする女、キャサリン。課長の話は根っこから聞いてへんけど','一人ボケ',('根っこ',(150,120,80))),
(130,150,'kitchen','C',C,'鍋にお水600、めんつゆ大さじ2、お酒大さじ1。火をつけて。そば用のお湯も隣でわかしとこ','工程1：水600cc＋めんつゆ（2倍）大さじ2＋酒大さじ1',('鍋\n火にかける',(120,120,140))),
(150,165,'kitchen','C',C,'ふつふつしてきたら、豚こまと玉ねぎを入れる','工程2：豚こま150g＋玉ねぎ',('豚こま\n＋玉ねぎ',(220,120,130))),
(165,175,'kitchen','C',C,'お肉の色が変わったら…火が通ったな','',None),
(175,190,'kitchen','C',C,'ここでカレールウ2袋、どーん！ ダマにならんように、よく混ぜて。もうええ匂い','工程3：パウダールウ2袋（4皿分）',('カレールウ\n2袋',(200,50,50))),
(190,210,'kitchen','C',C,'5分煮込むで。5分やで、課長。2時間半ちゃうで。その間にそばをゆでとこ。袋の時間より1分短めで','工程4：5分煮込む／そばは表示より1分短く',('5:00',(80,80,90))),
(210,222,'kitchen','C',C,'セリ投入！ 根っこも！','工程4：セリを入れる（根っこも！）',('セリ投入',(90,170,90))),
(222,238,'kitchen','C',C,'片栗粉大さじ2、お水大さじ4で溶いて、混ぜながら入れる。とろみがつくと麺によく絡むんよ','工程5：水溶き片栗粉（大さじ2＋水大さじ4）',('水溶き\n片栗粉',(170,170,190))),
(238,244,'kitchen','C',C,'見て、このとろとろ。ええやん','とろみで麺に絡む',('とろとろ',(170,110,40))),
(244,249,'kitchen','C',C,'そばもゆであがったで。湯切りして…','',('湯切り',(160,120,80))),
(249,260,'kitchen','C',C,'カレーの中にドボン！ さっと絡ませる。1分短めにゆでたんは、このため','工程6：そばを鍋に入れて、カレーに絡ませる',('ドボン！',(170,110,40))),
(260,270,'kitchen','C',C,'仕上げに鰹節を少しだけ。…踊ってる。できた〜！ 並ばんでも食べれるで、課長','完成！せりカレーそば',('せりカレー\nそば',(170,110,40))),
(270,276,'dining','G',G,'ただいま。カレーのいい匂いがするね','',None),
(276,281,'dining','G',G,'……','',('ずるずる',(170,110,40))),
(281,287,'dining','G',G,'地球が逆回転するくらい美味しいよ！','地球が逆回転するくらい美味しいよ！',None),
(287,290,'dining','Cbig',C,'どういうこっちゃ！','どういうこっちゃ！',None),
(290,298,'end',None,None,'','チャンネル登録してな！',None),
]
cache={}
def bg_for(scene):
    key=str(scene)
    if key not in cache:
        if scene=='title' or scene=='end': cache[key]=bg_title()
        elif scene=='kitchen': cache[key]=bg_kitchen()
        elif scene=='dining': cache[key]=bg_dining()
        else: cache[key]=bg_super(scene[1])
    return cache[key]
def fmt(t): return f'{int(t)//60}:{int(t)%60:02d}'
ff=subprocess.Popen(['ffmpeg','-y','-loglevel','error','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','-',
  '-f','lavfi','-i','anullsrc=r=44100:cl=stereo','-shortest','-c:v','libx264','-pix_fmt','yuv420p','-crf','23','-preset','medium','-c:a','aac','proto.mp4'],stdin=subprocess.PIPE)
for (s,e,scene,who,spk,line,telop,pr) in cues:
    base=bg_for(scene)
    for k in range(int((e-s)*FPS)):
        t=s+k/FPS; lt=k/FPS
        im=base.copy().convert('RGBA'); d=ImageDraw.Draw(im)
        if scene=='title':
            logo(d,W//2,230); f=font(60); txt='第1回　せりカレーそば'
            if lt>2: w=d.textlength(txt,font=f); d.text((W/2-w/2,500),txt,font=f,fill=INK,stroke_width=4,stroke_fill='white')
        if scene=='end':
            logo(d,W//2,200,0.9)
            f=font(56); w=d.textlength(telop,font=f); d.text((W/2-w/2,520),telop,font=f,fill=PINK,stroke_width=5,stroke_fill='white')
            im.alpha_composite(sc(BOTH,330),(60,360))
        bob=int(6*math.sin(t*3))
        if who=='C': im.alpha_composite(CATH,(120,130+bob))
        if who=='G': im.alpha_composite(GEO,(100,130+bob))
        if who=='Cbig':
            big=sc(cath,1300); z=big.crop((0,0,big.width,720)); im.alpha_composite(z,(250,-60+bob))
        if pr:
            pop=min(1,lt*4); 
            if pop>0.2: prop(d,pr[0],900,300,pr[1])
        if telop and scene!='end':
            f=font(40 if len(telop)<18 else 32)
            big = telop in ('旅行行ってたんか！','どういうこっちゃ！','地球が逆回転するくらい美味しいよ！')
            if big: f=font(64)
            lines=wrap(telop,f,720 if not big else 1100,d)
            y=130 if not big else (115 if isinstance(scene,tuple) else 60)
            for i,l in enumerate(lines):
                w=d.textlength(l,font=f); x=(1240-w) if not big else (W-w)/2
                d.text((x,y+i*(f.size+8)),l,font=f,fill=PINK if big else TEAL,stroke_width=6,stroke_fill='white')
        if line:
            f=font(34); lines=wrap(line,f,1080,d)
            bh2=40+len(lines)*44
            d.rounded_rectangle([60,H-bh2-30,W-60,H-20],20,fill=(255,255,255,235),outline=PINK if spk==C else TEAL,width=4)
            nf=font(26); d.rounded_rectangle([80,H-bh2-50,80+d.textlength(spk,font=nf)+30,H-bh2-12],12,fill=PINK if spk==C else TEAL)
            d.text((95,H-bh2-45),spk,font=nf,fill='white')
            for i,l in enumerate(lines): d.text((95,H-bh2-5+i*44),l,font=f,fill=INK)
        d.rounded_rectangle([10,10,300,48],10,fill=(0,0,0,110)); d.text((20,16),f'試作 ep001  {fmt(t)} / 4:58',font=font(22),fill='white')
        ff.stdin.write(im.convert('RGB').tobytes())
ff.stdin.close(); ff.wait()
