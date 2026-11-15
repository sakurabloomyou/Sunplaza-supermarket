// みんなのきょう Web版。画面のしくみは試作（ブラウザ版）と同じ。データは store.js。
import { openStore, StoreError, dayKey, nowMin, CODE_LENGTH } from './store.js';

const ICONS={
  clock:'<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>',
  bus:'<rect x="4" y="4" width="16" height="13" rx="3"/><path d="M4 11h16M8 20v-3M16 20v-3"/><circle cx="8" cy="14" r=".6"/><circle cx="16" cy="14" r=".6"/>',
  chat:'<path d="M4 6a3 3 0 0 1 3-3h10a3 3 0 0 1 3 3v7a3 3 0 0 1-3 3h-6l-5 4v-4a3 3 0 0 1-2-3z"/>',
  home:'<path d="M4 11l8-7 8 7v9H4z"/><path d="M10 20v-5h4v5"/>',
  heart:'<path d="M12 20s-7-4.4-7-10a4 4 0 0 1 7-2.6A4 4 0 0 1 19 10c0 5.6-7 10-7 10z"/>',
  clinic:'<rect x="4" y="4" width="16" height="16" rx="3"/><path d="M12 8v8M8 12h8"/>',
  people:'<circle cx="9" cy="8" r="3"/><circle cx="17" cy="9" r="2.4"/><path d="M3 20c0-3.3 2.7-6 6-6s6 2.7 6 6M15 14.5c3 0 6 1.8 6 5.5"/>',
  sprout:'<path d="M12 21v-9"/><path d="M12 12c0-4 3-7 8-7 0 4-3 7-8 7z"/><path d="M12 14c0-3-2.5-5.5-7-5.5 0 3 2.5 5.5 7 5.5z"/>'
};
const svg=k=>`<svg viewBox="0 0 24 24" aria-hidden="true">${ICONS[k]}</svg>`;

const CATS=[
  {id:'A',name:'忘れる・見通し',icon:'clock'},
  {id:'B',name:'デイサービス・外出',icon:'bus'},
  {id:'C',name:'気持ちや行動の変化',icon:'chat'},
  {id:'D',name:'家事・安全',icon:'home'},
  {id:'E',name:'家族の負担',icon:'heart'},
  {id:'F',name:'病院・手続き',icon:'clinic'},
  {id:'G',name:'人とのつながり',icon:'people'},
  {id:'H',name:'元気に過ごしてほしい',icon:'sprout'}
];
const ITEMS=[
  ['A1','A','同じことを何度も聞く',['lockwidget']],
  ['A2','A','ご飯を食べたか忘れる',['mealshow']],
  ['A3','A','薬を飲んだか忘れる・二重に飲む',['med']],
  ['A4','A','日付や曜日がわからなくなる',['dateclock']],
  ['A5','A','約束や通院を忘れる',['reminder3']],
  ['A6','A','家族がどこにいるか不安がる',['whereabouts']],
  ['A7','A','物をなくす・しまった場所を忘れる',['placememo']],
  ['B8','B','お迎えの時間に準備が間に合わない',['packlist']],
  ['B9','B','デイサービスに行きたがらない',['daymotivation']],
  ['B10','B','ひとりで出かけて道に迷わないか心配',['findmy']],
  ['B11','B','夕方になると「帰る」と言い出す',['eveningcalm','voicemsg']],
  ['C12','C','物を盗られたと言う',['tips','placememo']],
  ['C13','C','怒りっぽい・強い言葉や手が出る',['episode']],
  ['C14','C','落ち込む・やる気が出ない',['role']],
  ['C15','C','不安そう・そわそわする',['voicemsg']],
  ['C16','C','夜に眠らない・昼夜が逆になる',['sleep']],
  ['C17','C','声のかけ方で傷つけてしまう',['tips']],
  ['D18','D','火の消し忘れが心配',['firecheck']],
  ['D19','D','同じ物を何度も買う・お金の管理',['shopping']],
  ['D20','D','お風呂や着替えを嫌がる',['photocards']],
  ['D21','D','水分をあまりとらない',['water']],
  ['E22','E','この先どうなるか見通せない',['guide']],
  ['E23','E','家族の中で負担がかたよっている',['share']],
  ['E24','E','仕事と両立できるか不安',['worktools']],
  ['E25','E','自分の心と体が限界に近い',['selfcheck']],
  ['E26','E','誰とどこまで情報を共有するか迷う',['sharescope']],
  ['F27','F','受診のとき様子をうまく伝えられない',['report']],
  ['F28','F','介護保険などの手続きがむずかしい',['procedures']],
  ['G29','G','外に出ず、人と会わなくなった',['social']],
  ['H30','H','物忘れの進み方を少しでもゆるやかにしたい',['lifestyle']]
].map(([id,cat,label,features])=>({id,cat,label,features}));
const FEATURES={
  lockwidget:['ロック画面の「今日のボード」','アプリを開かなくても、今日の予定がいつも見える'],
  mealshow:['ごはん済みの表示','「12:10 お昼ごはん 済み」を本人の画面に出す'],
  med:['服薬チェック','飲み忘れたら家族に通知。済んだ後は「もう飲みました」と表示'],
  dateclock:['日付と曜日の大きな表示','日付・曜日・天気を1画面に'],
  reminder3:['3段階のお知らせ','前日・1時間前・出発時刻に通知'],
  whereabouts:['みんなの予定','「お母さんは仕事、18時に帰ります」を表示'],
  placememo:['しまった場所メモ','写真つきで、どこに置いたかを残す'],
  packlist:['お迎え前の持ち物チェック','写真つきのチェックリスト'],
  daymotivation:['前日のお楽しみ通知','「明日は〇〇さんに会えます」'],
  findmy:['「探す」の設定ガイド','iPhone標準機能の設定手順と、地域の見守り窓口'],
  eveningcalm:['夕方のやすらぎ時間','好きな写真や音楽を夕方に流す'],
  voicemsg:['家族の声メッセージ','「大丈夫だよ」の録音を本人がいつでも再生'],
  tips:['声かけのコツ','場面ごとに、否定しない伝え方を紹介'],
  episode:['できごと記録','いつ・何があったかを10秒で記録'],
  role:['小さな役割と気分の記録','水やりなどの役割に「ありがとう」を送る'],
  sleep:['眠りのリズムづくり','朝の光・散歩・昼寝の時間をお知らせ'],
  firecheck:['火の確認のお知らせ','調理の時間帯のあとに通知'],
  shopping:['買い物メモの共有','家族と本人で同じメモを見る'],
  photocards:['手順の写真カード','お風呂や着替えの手順を写真で'],
  water:['水分チェック','飲む時間のお知らせと記録'],
  guide:['これからの見通しガイド','段階ごとの解説と、地域の相談窓口'],
  share:['家族の分担表','送迎や見守りの担当を割り振る'],
  worktools:['仕事との両立の案内','職場から様子を確認。介護休業などの制度'],
  selfcheck:['家族の気分チェック','週1回、30秒。つらさが続いたら相談先を案内'],
  sharescope:['共有範囲の設定','家族・ケアマネ・デイサービスごとに見せる範囲を決める'],
  report:['受診メモの自動作成','最近1か月の様子をまとめる'],
  procedures:['手続きチェックリスト','要介護認定などの手順と期限'],
  social:['つながりの予定','家族会・認知症カフェ・ビデオ通話を予定に'],
  lifestyle:['生活習慣サポート','運動・食事・交流・血圧の記録を家族と一緒に続ける']
};
const CORE=[
  ['board','今日のボード','「いま」「つぎ」「きょうのみんな」を大きな文字で'],
  ['done','済みチェック','ごはん・薬・水分をワンタップで記録し、家族全員に共有'],
  ['pickup','お迎えカウントダウン','デイサービスのお迎えまでの時間を表示']
];
const FREQ=['ない','たまに','よく','毎日'];
const DEG=['いいえ','少し','かなり','とても'];
// 気持ちや状態をたずねる項目は「程度」で答える
const DEGREE_ITEMS=new Set(['B10','D18','D21','E22','E23','E24','E25','E26','F27','F28','G29','H30']);
const scale=it=>DEGREE_ITEMS.has(it.id)?DEG:FREQ;
const ans=it=>scale(it)[S.freq[it.id]||0];
const BASIC=[
  ['relation','ご本人とのご関係',['子','配偶者','孫','その他']],
  ['living','一緒に住んでいますか',['同居','近くに住む','遠方']],
  ['iphone','ご本人はiPhoneを使いますか',['使う','渡せば使う','使わない']],
  ['day','デイサービスなどの利用',['あり','なし']],
  ['meds','毎日飲む薬',['あり','なし']],
  ['alone','ご本人がひとりで過ごす時間',['ほぼない','日中ある','夜もある']]
];
const DAYS=['月','火','水','木','金','土','日'];


const $=id=>document.getElementById(id);
const ph=(...a)=>a.map(x=>`<span class="ph">${x}</span>`).join('');
const esc=s=>String(s).replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
const selCats=()=>CATS.filter(c=>S.cats.includes(c.id));
const itemScore=it=>(S.freq[it.id]||0)+(S.top.includes(it.id)?3:0);
function featureScores(){
  const m={};
  ITEMS.forEach(it=>{const sc=itemScore(it);if(!sc)return;it.features.forEach(f=>{
    if(!m[f]||m[f].score<sc)m[f]={score:sc,why:[]};
    m[f].why.push(it);
  })});
  if(S.basic.meds==='あり'){m.med=m.med||{score:0,why:[]};m.med.score=Math.max(m.med.score,2);m.med.basic=true}
  return Object.entries(m).filter(([,v])=>v.score>=2).sort((a,b)=>b[1].score-a[1].score);
}
// 最初からオンにするのは「特に気になる3つ」に対応する機能と、薬ありのときの服薬チェックだけ
const recommended=(k,v)=>v.why.some(i=>S.top.includes(i.id))||!!v.basic;
const isOn=(k,v)=>k in S.ovr?S.ovr[k]:(v?recommended(k,v):true);

const STEP_NAMES=['はじめに','基本情報','カテゴリ','具体的な悩み','特に気になる3つ','結果','完了'];



const blank=()=>({step:-1,sub:0,basic:{},days:[],cats:[],freq:{},top:[],free:'',ovr:{},tab:'today',role:'',myName:'',selfName:'',showPack:false,editing:false});
const KEY='mk-device-v1';
let S=blank();
try{const s=JSON.parse(localStorage.getItem(KEY)||'null');if(s&&typeof s==='object')S=Object.assign(blank(),s)}catch(e){}
const save=()=>{try{localStorage.setItem(KEY,JSON.stringify(S))}catch(e){}};
let store=null, H=null;
const hm=m=>`${Math.floor(m/60)}:${String(m%60).padStart(2,'0')}`;
const COLORS=['#1F5A4E','#8A4B00','#44524E','#6B4E8A','#2F6B8A'];
const av=(n,i=0)=>`<span class="av2" style="background:${COLORS[Math.abs([...(n||'?')].reduce((a,c)=>a+c.charCodeAt(0),0))%COLORS.length]}">${esc((n||'?')[0])}</span>`;
const me=()=>S.role==='self'?(H?.selfName||'ご本人'):(S.myName||'家族');
const isStandalone=()=>window.matchMedia('(display-mode: standalone)').matches||navigator.standalone===true;
const isIOS=()=>/iPhone|iPad|iPod/.test(navigator.userAgent);
const dateLabel=(d=new Date())=>`${d.getMonth()+1}月${d.getDate()}日（${'日月火水木金土'[d.getDay()]}）`;
const answersOf=()=>({basic:S.basic,days:S.days,cats:S.cats,freq:S.freq,top:S.top,ovr:S.ovr,free:S.free});
function loadAnswers(a){if(!a)return;S.basic=a.basic||{};S.days=a.days||[];S.cats=a.cats||[];S.freq=a.freq||{};S.top=a.top||[];S.ovr=a.ovr||{}}
const items=()=>(H?.items||[]).map(i=>Array.isArray(i)?{key:i[0],title:i[1],min:i[2],med:i[3]}:i);
const packs=()=>(H?.packItems||[]).map(p=>Array.isArray(p)?{key:p[0],title:p[1]}:p);
const usesDay=()=>H?.answers?.basic?.day==='あり';
const WD='日月火水木金土';
/** 今日がデイサービスの日か（基本情報で選んだ曜日。曜日が未選択なら毎日扱い） */
const dayServiceToday=()=>{if(!usesDay())return false;const ds=H.answers.days||[];return !ds.length||ds.includes(WD[new Date().getDay()])};
const nextDayServiceLabel=()=>{const ds=H?.answers?.days||[];if(!ds.length)return '';for(let i=1;i<=7;i++){const w=WD[(new Date().getDay()+i)%7];if(ds.includes(w))return i===1?'あした':`${w}曜日`}return ''};

function s1(b,f){
  b.innerHTML=`<h2 class="h">${ph('まず、','暮らしのことを','教えてください')}</h2>
  <label class="field"><span>あなたのお名前（家族の中での呼ばれ方）</span><input id="myName" maxlength="12" placeholder="例：さくら" value="${esc(S.myName||'')}"></label>
  <label class="field"><span>ご本人の呼び名</span><input id="selfName" maxlength="12" placeholder="例：お母さん" value="${esc(S.selfName||'')}"></label>`+BASIC.map(([k,q,opts])=>`<div class="q"><span>${q}</span><div class="chips">${opts.map(o=>`<button class="chip" type="button" data-k="${k}" data-v="${o}" aria-pressed="${S.basic[k]===o}">${o}</button>`).join('')}</div>${k==='day'&&S.basic.day==='あり'?`<div class="days" aria-label="利用する曜日">${DAYS.map(d=>`<button class="chip" type="button" data-day="${d}" aria-pressed="${S.days.includes(d)}">${d}</button>`).join('')}</div>`:''}</div>`).join('');
  b.querySelectorAll('[data-k]').forEach(el=>el.onclick=()=>{const k=el.dataset.k,v=el.dataset.v;S.basic[k]=S.basic[k]===v?undefined:v;keep(()=>s1(b,f))});
  b.querySelectorAll('[data-day]').forEach(el=>el.onclick=()=>{const d=el.dataset.day;S.days=S.days.includes(d)?S.days.filter(x=>x!==d):[...S.days,d];keep(()=>s1(b,f))});
  $('myName').oninput=e=>{S.myName=e.target.value.trim();save()};
  $('selfName').oninput=e=>{S.selfName=e.target.value.trim();save()};
  f.innerHTML=`<p class="err" id="nameErr" hidden>あなたのお名前を入れてください。</p><button class="btn" type="button" id="n">次へ</button><button class="btn ghost" type="button" id="later">とばして、あとで設定する</button>`;
  $('n').onclick=()=>{if(!S.myName){$('nameErr').hidden=false;$('myName').focus();return}go(2)};
  $('later').onclick=()=>{if(!S.myName){$('nameErr').hidden=false;$('myName').focus();return}S.cats=[];S.freq={};S.top=[];go(5)};
}
function keep(fn){const b=$('body'),y=b.scrollTop;fn();b.scrollTop=y;save()}
function s2(b,f){
  b.innerHTML=`<h2 class="h">${ph('気になることを','選んでください')}</h2><p class="lead">いくつ選んでもかまいません。</p><div class="cats">${CATS.map(c=>`<button class="cat" type="button" data-c="${c.id}" aria-pressed="${S.cats.includes(c.id)}">${svg(c.icon)}<span>${ph(...({C:['気持ちや','行動の変化'],H:['元気に過ごして','ほしい'],B:['デイサービス・','外出']}[c.id]||[c.name]))}</span><span class="ck"></span></button>`).join('')}</div>`;
  b.querySelectorAll('[data-c]').forEach(el=>el.onclick=()=>{const c=el.dataset.c;
    if(S.cats.includes(c)){S.cats=S.cats.filter(x=>x!==c);ITEMS.filter(i=>i.cat===c).forEach(i=>{delete S.freq[i.id];S.top=S.top.filter(t=>t!==i.id)})}else S.cats=[...S.cats,c];
    keep(()=>s2(b,f))});
  f.innerHTML=`<button class="btn" type="button" id="n">${S.cats.length?'次へ':'選ばずに進む'}</button>`;
  $('n').onclick=()=>{S.sub=0;S.cats.length?go(3):go(5)};
}
function s3(b,f){
  const cs=selCats();const c=cs[S.sub];if(!c){go(4);return}
  const items=ITEMS.filter(i=>i.cat===c.id);
  b.innerHTML=`<div class="catlabel">${svg(c.icon)}<span>${c.name}（${S.sub+1} / ${cs.length}）</span></div><h2 class="h">${ph('あてはまるものを','選んでください')}</h2>`+
  items.map(it=>`<div class="item"><span>${it.label}</span><div class="freq" role="group" aria-label="${esc(it.label)}">${scale(it).map((fq,i)=>`<button class="chip" type="button" data-i="${it.id}" data-f="${i}" aria-pressed="${(S.freq[it.id]||0)===i&&S.freq[it.id]!==undefined}">${fq}</button>`).join('')}</div></div>`).join('')+
  (S.sub===cs.length-1?`<div class="q"><span>この中にない悩み（任意）</span><textarea id="free" placeholder="例：夜中に何度も家族を起こす">${esc(S.free)}</textarea></div>`:'');
  b.querySelectorAll('[data-i]').forEach(el=>el.onclick=()=>{const id=el.dataset.i,v=+el.dataset.f;S.freq[id]=v;if(v<2)S.top=S.top.filter(t=>t!==id);keep(()=>s3(b,f))});
  const t=$('free');if(t)t.oninput=()=>{S.free=t.value;save()};
  f.innerHTML=`<button class="btn" type="button" id="n">次へ</button>`;
  $('n').onclick=()=>{if(S.sub<cs.length-1){S.sub++;render()}else go(4)};
}
function s4(b,f){
  const cand=ITEMS.filter(i=>(S.freq[i.id]||0)>=2).sort((a,b)=>S.freq[b.id]-S.freq[a.id]);
  const full=S.top.length>=3;
  b.innerHTML=`<h2 class="h">${ph('特に気になるものを、','3つまで','選んでください')}</h2><p class="counter">${S.top.length} / 3 選択中</p>`+
  (full?`<p class="full">3つ選びました。選び直すときは、選んだものをもう一度押して外してください。</p>`:'')+
  (cand.length?`<div class="tops">${cand.map(it=>{const r=S.top.indexOf(it.id);const dim=full&&r<0;return `<button class="top${dim?' dim':''}" type="button" data-t="${it.id}" aria-pressed="${r>=0}"${dim?' aria-disabled="true"':''}><span class="n">${r>=0?r+1:''}</span><span>${it.label}</span><span class="f">${ans(it)}</span></button>`}).join('')}</div>`
  :`<div class="empty">「よく」「毎日」「かなり」「とても」を選んだ悩みがないので、この画面はとばせます。</div>`);
  b.querySelectorAll('[data-t]').forEach(el=>el.onclick=()=>{const id=el.dataset.t;
    if(S.top.includes(id))S.top=S.top.filter(t=>t!==id);else if(S.top.length<3)S.top=[...S.top,id];
    keep(()=>s4(b,f))});
  f.innerHTML=`<button class="btn" type="button" id="n">${cand.length?'次へ':'とばして次へ'}</button>`;$('n').onclick=()=>go(5);
}
function coreList(){return CORE.filter(([k])=>k!=='pickup'||S.basic.day==='あり')}
function whyText(k,v){
  if(v.basic&&!v.why.length)return '理由：基本情報で「薬あり」';
  const top=v.why.filter(i=>S.top.includes(i.id));
  const it=(top[0]||v.why.sort((a,b)=>itemScore(b)-itemScore(a))[0]);
  return `理由：「${it.label}」${ans(it)}${S.top.includes(it.id)?'・特に気になる':''}`;
}
function s5(b,f){
  const fs=featureScores();
  const rec=fs.filter(([k,v])=>recommended(k,v)),more=fs.filter(([k,v])=>!recommended(k,v));
  const swi=(k,on)=>`<button class="sw" type="button" role="switch" data-sw="${k}" data-on="${on}" aria-checked="${on}" aria-label="${esc(FEATURES[k]?FEATURES[k][0]:CORE.find(c=>c[0]===k)[1])}"></button>`;
  const card=([k,v])=>{const on=isOn(k,v);return `<div class="feat ${on?'star':''}"><div class="t">${on?'<span class="onb">★ オン</span>':'<span class="offb">オフ</span>'}<b>${FEATURES[k][0]}</b><span>${FEATURES[k][1]}</span><em>${esc(whyText(k,v))}</em></div>${swi(k,on)}</div>`};
  const nOn=fs.filter(([k,v])=>isOn(k,v)).length;
  b.innerHTML=`<h2 class="h">${nOn?ph('ご家庭に合わせて、',`${nOn}つの機能を`,'オンにしました'):ph('ご家庭に合わせた機能は、','まだオフです')}</h2><p class="lead">ほかの機能も、必要になったらここでオンにできます。</p>`+
  `<div class="sect">特に気になることに合わせた機能</div>`+
  (rec.length?`<div class="feats">${rec.map(card).join('')}</div>`:`<div class="empty">特に気になるものが選ばれていないので、ここは空です。下の「ほかにおすすめ」から選べます。</div>`)+
  `<div class="sect">みなさん共通の基本機能</div><div class="feats">${coreList().map(([k,n,d])=>{const on=isOn(k);return `<div class="feat"><div class="t"><span class="${on?'onb':'offb'}">${on?'オン':'オフ'}</span><b>${n}</b><span>${d}${k==='pickup'&&S.days.length?`（${S.days.join('・')}）`:''}</span></div>${swi(k,on)}</div>`}).join('')}</div>`+
  (more.length?`<div class="sect">ほかにおすすめ（いまはオフ）</div><div class="feats">${more.map(card).join('')}</div>`:'')+
  (S.basic.iphone==='使わない'?`<div class="empty">ご本人がiPhoneを使わないため、ご本人用の画面は作らず、ご家族の画面だけで使います。</div>`:'');
  b.querySelectorAll('[data-sw]').forEach(el=>el.onclick=()=>{S.ovr[el.dataset.sw]=el.dataset.on!=='true';keep(()=>s5(b,f))});
  f.innerHTML=`<button class="btn" type="button" id="n">はじめる</button>`;
  $('n').onclick=()=>go(6);
}


/* ---------- 画面の切り替え ---------- */
function render(){
  const st=S.step;
  $('backBtn').disabled=st===6;
  $('topbar').hidden=st===-1||st===8||st===9;
  $('screen').classList.toggle('is-launch',st===-1);
  const showProg=st>=1&&st<=5;
  $('prog').style.visibility=showProg?'visible':'hidden';
  if(showProg){$('progText').textContent=`${st} / 5　${STEP_NAMES[st]}`;$('progBar').style.width=(st/5*100)+'%'}
  const b=$('body'),f=$('foot');b.classList.remove('self');
  ({'-1':sLaunch,1:s1,2:s2,3:s3,4:s4,5:s5,6:s6,7:s7,8:s8,9:s9,12:sInvite})[st](b,f);
  b.scrollTop=0; save();
}
function go(n){S.step=n;if(n===3&&S.sub>=selCats().length)S.sub=0;render()}

function installBanner(){
  if(isStandalone()||!isIOS())return '';
  return `<div class="banner"><b>ホーム画面に追加して使ってください</b>Safari の下の共有ボタン（四角から矢印）→「ホーム画面に追加」。ホーム画面から開かないと、データが別々になります。</div>`;
}

function sLaunch(b,f){
  b.innerHTML=`<div class="lh">
    <div class="brandrow"><div class="mark" aria-hidden="true"><svg viewBox="0 0 1024 1024" fill="none" stroke-linecap="round"><defs><radialGradient id="bgln" cx="50%" cy="62%" r="75%"><stop offset="0" stop-color="#2F7666"/><stop offset=".58" stop-color="#1F5A4E"/><stop offset="1" stop-color="#184A40"/></radialGradient><radialGradient id="glln" cx="512" cy="640" r="330" gradientUnits="userSpaceOnUse"><stop offset="0" stop-color="#F4C978" stop-opacity=".35"/><stop offset="1" stop-color="#F4C978" stop-opacity="0"/></radialGradient></defs><rect width="1024" height="1024" fill="url(#bgln)"/><circle cx="512" cy="640" r="330" fill="url(#glln)"/><path d="M322 640a190 190 0 0 1 380 0" stroke="#F4C978" stroke-width="58"/><path d="M512 330v-86M300 418l-60-60M724 418l60-60" stroke="#F4C978" stroke-width="54"/><path d="M200 640h624" stroke="#FFFFFF" stroke-width="58"/><path d="M330 748h364" stroke="#FFFFFF" stroke-opacity=".55" stroke-width="40"/></svg></div>
    <div class="nm"><b>みんなのきょう</b></div></div>
    <div class="for"><p>もの忘れが気になり始めた方（軽度認知症・MCI）と、そのご家族のためのアプリ</p>
      <dl class="rl"><dt>ご家族</dt><dd>予定を入れて、離れていても様子を確認</dd><dt>ご本人</dt><dd>ボードで、今日のことがわかる</dd></dl></div>
    <h2 class="tag">家族の予定を、<br>ご本人のスマホにも。</h2>
  </div>
  ${installBanner()}
  <p class="disc">このアプリは診断や治療をするものではありません。健康や治療について判断するときは、医師にご相談ください。</p>
  <p class="mode">${store.mode==='local'?'お試しモード（この端末の中だけに保存）':'家族共有モード'}　<a href="guide.html">使い方（説明書）</a></p>`;
  f.innerHTML=`<p class="startnote">約3分の質問で、ご家庭に合う機能を選びます</p><button class="btn" type="button" id="n">家族として始める</button><button class="btn ghost" type="button" id="code">招待コードを入力する</button>`;
  $('n').onclick=()=>go(1);
  $('code').onclick=()=>go(7);
}

/* 6. 完了 → 家族グループを作る */
function s6(b,f){
  const fs=featureScores().filter(([k,v])=>isOn(k,v));
  const core=coreList().filter(([k])=>isOn(k));
  const order=[...core.map(c=>c[1]),...fs.map(([k])=>FEATURES[k][0])];
  b.innerHTML=`<div class="hero"><b>${S.editing?'選び直しが終わりました':'設定が終わりました'}</b><span>${S.editing?'「保存してホームへ」を押すと、家族全員のアプリに反映されます。記録や分担表はそのまま残ります。':'「ホームへ進む」を押すと、家族グループを作ります。そのあと「家族を招待する」から、ご家族やご本人を招待できます。'}</span></div>
  <div class="sect">ホームに並ぶ機能</div><div class="home">${order.map((n,i)=>`<div class="tile"><i>${i+1}</i><span>${n}</span></div>`).join('')||'<div class="empty">オンの機能がありません。</div>'}</div>
  <p class="err" id="mkErr" hidden></p>`;
  f.innerHTML=`<button class="btn" type="button" id="n">${S.editing?'保存してホームへ':'ホームへ進む'}</button><button class="btn ghost" type="button" id="re">設定を見直す</button>`;
  $('re').onclick=()=>go(5);
  $('n').onclick=async()=>{
    $('n').disabled=true;
    try{
      if(S.editing){await store.updateAnswers(answersOf(),S.selfName);S.editing=false}
      else await store.createHousehold({answers:answersOf(),selfName:S.selfName||'ご本人',myName:S.myName});
      S.role='family';S.tab='today';go(8)}
    catch(e){$('mkErr').textContent='家族グループを作れませんでした。通信できる場所で、もう一度お試しください。';$('mkErr').hidden=false;$('n').disabled=false}
  };
}

/* 7. 招待コードで参加 */
function s7(b,f){
  b.innerHTML=`<h2 class="h">${ph('招待コードを','入力してください')}</h2>
  <p class="lead">ご家族から届いた${CODE_LENGTH}けたの数字です。</p>
  ${installBanner()}
  <div class="code" id="codeBox">${[...Array(CODE_LENGTH).keys()].map(i=>`<input id="c${i}" inputmode="numeric" maxlength="1" aria-label="${i+1}けため" autocomplete="one-time-code">`).join('')}</div>
  <div class="q"><span>どちらで使いますか</span><div class="chips">
    <button class="chip" type="button" data-r="self" aria-pressed="${S.role==='self'}">ご本人として</button>
    <button class="chip" type="button" data-r="family" aria-pressed="${S.role==='family'}">家族として</button></div></div>
  <label class="field" id="nameF" ${S.role==='family'?'':'hidden'}><span>あなたのお名前</span><input id="jName" maxlength="12" placeholder="例：たろう" value="${esc(S.myName||'')}"></label>
  <p class="err" id="codeErr" hidden></p>`;
  const ins=[...b.querySelectorAll('.code input')];
  ins.forEach((el,i)=>{
    el.oninput=()=>{const v=el.value.replace(/\D/g,'');if(v.length>1){v.slice(0,CODE_LENGTH-i).split('').forEach((c,j)=>{if(ins[i+j])ins[i+j].value=c});(ins[Math.min(i+v.length,CODE_LENGTH-1)]).focus();return}el.value=v;if(v&&ins[i+1])ins[i+1].focus()};
    el.onkeydown=e=>{if(e.key==='Backspace'&&!el.value&&ins[i-1])ins[i-1].focus()};
    el.onpaste=e=>{const t=(e.clipboardData.getData('text')||'').replace(/\D/g,'').slice(0,CODE_LENGTH);if(t){e.preventDefault();t.split('').forEach((c,j)=>{if(ins[j])ins[j].value=c});(ins[t.length]||ins[CODE_LENGTH-1]).focus()}};
  });
  b.querySelectorAll('[data-r]').forEach(el=>el.onclick=()=>{S.role=el.dataset.r;b.querySelectorAll('[data-r]').forEach(x=>x.setAttribute('aria-pressed',x.dataset.r===S.role));$('nameF').hidden=S.role!=='family';save()});
  $('jName').oninput=e=>{S.myName=e.target.value.trim();save()};
  f.innerHTML=`<button class="btn" type="button" id="n">参加する</button>`;
  $('n').onclick=async()=>{
    const code=ins.map(x=>x.value).join('');const e=$('codeErr');e.hidden=true;
    if(code.length<CODE_LENGTH){e.textContent=`${CODE_LENGTH}けたの数字をすべて入れてください。`;e.hidden=false;return}
    if(!S.role){e.textContent='「ご本人として」か「家族として」を選んでください。';e.hidden=false;return}
    if(S.role==='family'&&!S.myName){e.textContent='あなたのお名前を入れてください。';e.hidden=false;return}
    $('n').disabled=true;$('n').textContent='参加しています…';
    try{await store.join(code,{name:S.role==='family'?S.myName:'',role:S.role});S.tab='today';go(S.role==='self'?9:8)}
    catch(err){e.textContent=err instanceof StoreError?err.message:'参加できませんでした。通信できる場所で、もう一度お試しください。';e.hidden=false;$('n').disabled=false;$('n').textContent='参加する'}
  };
}

/* 8. 家族のホーム */
const TAB_ICONS={today:'<svg viewBox="0 0 24 24"><rect x="4" y="5" width="16" height="15" rx="3"/><path d="M4 10h16M9 3v4M15 3v4"/></svg>',log:'<svg viewBox="0 0 24 24"><path d="M6 5h12M6 12h12M6 19h8"/></svg>',share:'<svg viewBox="0 0 24 24"><circle cx="9" cy="8" r="3"/><circle cx="17" cy="9" r="2.4"/><path d="M3 20c0-3.3 2.7-6 6-6s6 2.7 6 6M15 14.5c3 0 6 1.8 6 5.5"/></svg>'};
function s8(b,f){
  if(!H){b.innerHTML=`<div class="empty">家族グループを読み込んでいます…</div>`;f.innerHTML='';return}
  loadAnswers(H.answers);
  const t=S.tab, now=nowMin(), left=H.pickup-now, done=H.today.done, pack=H.today.pack;
  const head=`<div class="apphd"><div><div class="d">${dateLabel()}　いま ${hm(now)}</div><h2>${{today:'きょう',log:'きょうの記録',share:'家族の分担表'}[t]}</h2></div><span class="who-chip">${esc(S.myName||'家族')}（家族）</span></div>`;
  let body='';
  if(t==='today'){
    const enabled=featureScores().filter(([k,v])=>isOn(k,v)).map(([k])=>FEATURES[k][0]);
    const pk=packs();
    body=(usesDay()&&!dayServiceToday()?`<div class="cdcard"><span class="k">デイサービス</span><span class="t">きょうはお休みの日です。つぎは${nextDayServiceLabel()}です</span></div>`:'')+(dayServiceToday()?`<div class="cdcard"><span class="k">デイサービスのお迎えまで</span>
      ${left>0?`<span class="n">あと${left}<small>分</small></span><span class="t">${hm(H.pickup)} にお迎えが来ます</span><div class="prog2"><i style="width:${Math.max(4,Math.min(100,100-left/120*100))}%"></i></div>`:`<span class="n" style="font-size:28px">お迎えの時間です</span>`}
      <button class="linkbtn" type="button" id="pkT">${S.showPack?'持ち物を閉じる':'お迎え前の持ち物を見る'}（${pk.filter(p=>pack[p.key]).length} / ${pk.length}）</button>
      ${S.showPack?`<div class="pk">${pk.map(p=>`<button class="pkrow" type="button" data-pk="${p.key}" aria-pressed="${!!pack[p.key]}"><span class="bx"></span>${esc(p.title)}</button>`).join('')}</div>`:''}
    </div>`:'')+`
    <div class="sect">ごはん・おくすり</div>
    <div class="dlist">${items().map(it=>{const d=done[it.key];const late=!d&&now>it.min+30;return `<div class="drow ${d?'done':''}"><div class="nm2"><b>${esc(it.title)}</b><span>${d?`${esc(d.by)}・${hm(d.at)}`:`${hm(it.min)}ごろ`}${late?'　<span class="late">まだです</span>':''}</span></div><button class="dbtn ${d?'on':''}" type="button" data-d="${it.key}" aria-pressed="${!!d}">${d?'済み':'済みにする'}</button></div>`}).join('')}</div>
    ${enabled.length?`<div class="sect">ご家庭に合わせてオンにした機能</div><div class="morefeat">${enabled.map(n=>`<span>${n}</span>`).join('')}</div>`:''}
    <div class="banner"><b>お知らせについて</b>Web版では今のところ、アプリを閉じているときのお知らせは届きません。開いている間は、画面が1分ごとに新しくなります。</div>
    <div style="display:flex;flex-direction:column">
    <button class="linkbtn" type="button" id="toInv">家族を招待する ›</button>
    <button class="linkbtn" type="button" id="redo">困りごとを選び直す ›</button>
    <a class="linkbtn" href="guide.html" style="text-decoration:none;display:flex;align-items:center">使い方（説明書） ›</a>
    <button class="linkbtn" type="button" id="toSelf">ご本人の画面を見る ›</button>
    <button class="linkbtn" type="button" id="leave">この端末を家族グループから外す</button></div>
    <p class="mode">${store.mode==='local'?'お試しモード（この端末の中だけに保存）':'家族共有モード'}</p>`;
  }else if(t==='log'){
    const r=Object.entries(done).map(([k,v])=>({at:v.at,by:v.by,t:`${items().find(i=>i.key===k)?.title||k} 済み`})).sort((a,b)=>a.at-b.at);
    body=r.length?`<div class="tline">${r.map(x=>`<span class="tm">${hm(x.at)}</span>${av(x.by)}<span>${esc(x.by)}　${esc(x.t)}</span>`).join('')}</div>`:`<div class="empty">まだ記録がありません。「済みにする」を押すと、ここに並びます。</div>`;
    body+=`<p class="hint">ご家族みんなが同じ記録を見ています。</p>`;
  }else{
    const ds=[...H.duties].sort((a,b)=>String(a.when).localeCompare(String(b.when),'ja'));
    body=`<div class="dlist">${ds.map(d=>`<div class="duty"><span class="dd">${esc(d.when)}</span><span class="ww"><b>${esc(d.title)}</b>${d.assignee?`<span>担当：${esc(d.assignee)}</span>`:''}</span>${d.assignee?`<button class="dbtn" type="button" data-un="${d.id}">外す</button>`:`<button class="dbtn" type="button" data-take="${d.id}">引き受ける</button>`}</div>`).join('')||'<div class="empty">まだ予定がありません。下から追加できます。</div>'}</div>
    <div class="sect">予定を追加</div>
    <div class="addduty"><input id="dWhen" placeholder="いつ（例：火）" maxlength="10" aria-label="いつ"><input id="dTitle" placeholder="内容（例：通院の付きそい）" maxlength="30" aria-label="内容"></div>
    <button class="btn" type="button" id="dAdd">追加する</button>`;
  }
  b.innerHTML=head+body;
  f.innerHTML=`<div class="tabs" role="tablist">${[['today','きょう'],['log','記録'],['share','分担']].map(([k,n])=>`<button class="tab" type="button" role="tab" data-tab="${k}" aria-current="${t===k}">${TAB_ICONS[k]}${n}</button>`).join('')}</div>`;
  f.querySelectorAll('[data-tab]').forEach(el=>el.onclick=()=>{S.tab=el.dataset.tab;render()});
  b.querySelectorAll('[data-d]').forEach(el=>el.onclick=()=>store.toggleDone(el.dataset.d,me()));
  b.querySelectorAll('[data-pk]').forEach(el=>el.onclick=()=>store.togglePack(el.dataset.pk));
  b.querySelectorAll('[data-take]').forEach(el=>el.onclick=()=>store.setAssignee(el.dataset.take,S.myName||'家族'));
  b.querySelectorAll('[data-un]').forEach(el=>el.onclick=()=>store.setAssignee(el.dataset.un,''));
  const add=$('dAdd');if(add)add.onclick=()=>{const w=$('dWhen').value.trim(),ti=$('dTitle').value.trim();if(w&&ti)store.addDuty(w,ti)};
  const pkT=$('pkT');if(pkT)pkT.onclick=()=>{S.showPack=!S.showPack;keep(()=>s8(b,f))};
  const ts=$('toSelf');if(ts)ts.onclick=()=>{S.role='self';go(9)};
  const ti=$('toInv');if(ti)ti.onclick=()=>go(12);
  const rd=$('redo');if(rd)rd.onclick=()=>{loadAnswers(H.answers);S.selfName=H.selfName||S.selfName;S.editing=true;S.sub=0;go(1)};
  const lv=$('leave');if(lv)lv.onclick=async()=>{if(lv.dataset.sure){await store.leave();S=blank();save();render()}else{lv.dataset.sure='1';lv.textContent='もう一度押すと外します（記録は家族グループに残ります）'}};
}

/* 12. 家族を招待する */
let lastInvite=null;
function sInvite(b,f){
  const names=(H?.members||[]).map(m=>m.role==='self'?`${esc(H.selfName||'ご本人')}（ご本人）`:esc(m.name||'家族'));
  b.innerHTML=`<h2 class="h">${ph('家族を','招待する')}</h2>
  <p class="lead">ご家族やご本人のスマホで入力する、${CODE_LENGTH}けたのコードを作ります。コードは24時間だけ使えます。</p>
  ${lastInvite?`<div class="codeshow" aria-label="${lastInvite.code.split('').join(' ')}">${lastInvite.code.slice(0,4)} ${lastInvite.code.slice(4)}</div><p class="hint" style="text-align:center">${lastInvite.expires.toLocaleString('ja-JP',{month:'numeric',day:'numeric',hour:'numeric',minute:'2-digit'})} まで使えます</p>`:''}
  <p class="err" id="invErr" hidden></p>
  <div class="sect">参加している人</div><div class="morefeat">${names.map(n=>`<span>${n}</span>`).join('')||'<span>まだいません</span>'}</div>
  <p class="hint">コードを知っている人は参加できます。コードは家族だけに送ってください。</p>`;
  f.innerHTML=`<button class="btn" type="button" id="mk">${lastInvite?'新しいコードを作る':'招待コードを作る'}</button>${lastInvite?`<button class="btn ghost" type="button" id="cp">コードと説明をコピー</button>`:''}`;
  $('mk').onclick=async()=>{$('mk').disabled=true;try{lastInvite=await store.makeInvite();render()}catch(e){$('invErr').textContent=e instanceof StoreError?e.message:'招待コードを作れませんでした。';$('invErr').hidden=false;$('mk').disabled=false}};
  const cp=$('cp');if(cp)cp.onclick=async()=>{const t=`「みんなのきょう」の招待コード：${lastInvite.code}（24時間有効）\n${location.origin+location.pathname} を開き、ホーム画面に追加してから「招待コードを入力する」に入れてください。`;
    try{await navigator.clipboard.writeText(t);cp.textContent='コピーしました'}catch(e){cp.textContent='コピーできませんでした。コードを書き写してください'}};
}

/* 9. ご本人の画面 */
function s9(b,f){
  if(!H){b.innerHTML=`<div class="empty">ご家族の予定を読み込んでいます…</div>`;f.innerHTML='';return}
  const now=nowMin(), left=H.pickup-now, done=H.today.done;
  const nowItem=items().find(it=>!done[it.key]&&it.min<=now+60)||null;
  const laterItem=items().find(it=>!done[it.key]&&it.min>now+60&&it!==nowItem)||null;
  const allDone=items().every(it=>done[it.key]);
  let nextText='';
  if(dayServiceToday()&&left>0)nextText=`${hm(H.pickup)}　${ph('デイサービスの','お迎え')}<br>あと${left}分`;
  else if(dayServiceToday()&&now<H.returnAt)nextText=`${hm(H.returnAt)}　${ph('デイサービスから','おうちに','帰ります')}`;
  else if(laterItem)nextText=`${hm(laterItem.min)}　${esc(laterItem.title)}`;
  else if(allDone&&items().length)nextText='きょうのごはんとおくすりは、ぜんぶ済みました';
  const fam=(H.members||[]).filter(m=>m.role==='family').map(m=>m.name).filter(Boolean);
  b.classList.add('self');
  b.innerHTML=`<div class="sd"><small>きょうは</small>${dateLabel()}</div>
  <div class="sblock now"><span class="k">いま</span><span class="v">${nowItem?ph(esc(nowItem.title)+'の','時間です'):'ゆっくり過ごしましょう'}</span></div>
  ${nowItem?`<button class="sbig" type="button" id="sd">${esc(nowItem.title)}を「済み」にする</button>`:''}
  ${nextText?`<div class="sblock next"><span class="k">つぎ</span><span class="v">${nextText}</span></div>`:''}
  <div class="sblock"><span class="k">きょうのみんな</span><div class="smem">${fam.map(n=>`<div><b>${esc(n)}</b><span>家族</span></div>`).join('')||'<div><span>ご家族の予定はまだありません</span></div>'}</div></div>`;
  f.innerHTML=S.role==='self'&&(H.members||[]).some(m=>m.uid===store.uid&&m.role==='self')?'':`<button class="btn ghost" type="button" id="fam">家族の画面にもどる</button>`;
  const sd=$('sd');if(sd)sd.onclick=()=>store.toggleDone(nowItem.key,H.selfName||'ご本人');
  const fb=$('fam');if(fb)fb.onclick=()=>{S.role='family';S.tab='today';go(8)};
}

/* 戻るボタン */
$('backBtn').onclick=()=>{
  if(S.step===3&&S.sub>0){S.sub--;render();return}
  if(S.step===4){if(S.cats.length){S.sub=selCats().length-1;go(3)}else go(2);return}
  if(S.step===5&&!S.cats.length){go(2);return}
  if(S.step===1&&S.editing){S.editing=false;go(8);return}
  if(S.step===1||S.step===7){go(-1);return}
  if(S.step===12){go(8);return}
  go(Math.max(-1,S.step-1));
};

/* スプラッシュ（その日の最初だけ2秒） */
function splash(){
  const el=$('splash');let last='';try{last=localStorage.getItem('mk-splash')||''}catch(e){}
  if(last===dayKey()){el.hidden=true;return}
  el.hidden=false;try{localStorage.setItem('mk-splash',dayKey())}catch(e){}
  const t=setTimeout(()=>el.hidden=true,2000);el.onclick=()=>{clearTimeout(t);el.hidden=true};
}

/* 起動 */
(async()=>{
  splash();
  try{store=await openStore()}catch(e){$('body').innerHTML=`<div class="empty">起動できませんでした。通信できる場所で開き直してください。</div>`;return}
  H=store.household;
  store.onChange(h=>{H=h;if(S.step===8||S.step===9||S.step===12){const b=$('body'),y=b.scrollTop;render();b.scrollTop=y}});
  if(H&&S.role&&S.step<8&&!S.editing)S.step=S.role==='self'?9:8;
  if(!H&&S.step>=8)S.step=-1;
  render();
  setInterval(()=>{if(S.step===8||S.step===9){const b=$('body'),y=b.scrollTop;render();b.scrollTop=y}},60000);
  if('serviceWorker' in navigator)navigator.serviceWorker.register('./sw.js').catch(()=>{});
})();
