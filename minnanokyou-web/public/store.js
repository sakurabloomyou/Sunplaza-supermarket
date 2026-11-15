// データの保存先。
//  - LocalStore    : この端末（ブラウザ）の中だけ。家族の共有なし。Firebase の設定が空のときに使う。
//  - FirebaseStore : Firebase（Firestore）。家族の間で共有。8けたの招待コードで参加。
import { firebaseConfig } from './firebase-config.js';

export const DEFAULT_ITEMS = [['bf','あさごはん',480,false],['m1','おくすり（朝）',510,true],['lu','おひるごはん',720,false],['m2','おくすり（昼）',750,true],['di','ばんごはん',1080,false],['m3','おくすり（夜）',1110,true]];
export const DEFAULT_PACK = [['a','連絡帳'],['b','着がえ'],['c','タオル'],['d','おくすり'],['e','上ばき']];
export const dayKey = (d = new Date()) => `${d.getFullYear()}-${d.getMonth() + 1}-${d.getDate()}`;
export const nowMin = (d = new Date()) => d.getHours() * 60 + d.getMinutes();
export const CODE_LENGTH = 8;
const INVITE_HOURS = 24;

export class StoreError extends Error {}

export async function openStore() {
  if (firebaseConfig && firebaseConfig.apiKey) {
    const s = new FirebaseStore(firebaseConfig);
    await s.init();
    return s;
  }
  return new LocalStore();
}

function newHousehold({ answers, selfName }) {
  const meds = answers?.basic?.meds === 'あり';
  return {
    selfName: selfName || 'ご本人',
    answers,
    pickup: 620, returnAt: 990,
    items: DEFAULT_ITEMS.filter(i => meds || !i[3]),
    packItems: DEFAULT_PACK,
  };
}

/* ---------------- この端末だけ ---------------- */
class LocalStore {
  constructor() {
    this.mode = 'local';
    this.listeners = new Set();
    try { this.data = JSON.parse(localStorage.getItem('mk-local') || 'null'); } catch { this.data = null; }
  }
  get household() {
    if (!this.data) return null;
    const d = this.data, today = dayKey();
    if (d.dayKey !== today) { d.dayKey = today; d.today = { done: {}, pack: {} }; this._save(false); }
    return { ...d.h, id: 'local', members: d.members, today: d.today, duties: d.duties };
  }
  onChange(fn) { this.listeners.add(fn); return () => this.listeners.delete(fn); }
  _save(emit = true) {
    try { localStorage.setItem('mk-local', JSON.stringify(this.data)); } catch {}
    if (emit) this.listeners.forEach(f => f(this.household));
  }
  async createHousehold({ answers, selfName, myName }) {
    this.data = { h: newHousehold({ answers, selfName }), members: [{ uid: 'me', name: myName, role: 'family' }],
                  dayKey: dayKey(), today: { done: {}, pack: {} }, duties: [] };
    this._save();
  }
  async join() { throw new StoreError('お試しモードでは、招待コードは使えません。Firebase の設定をしてから使ってください。'); }
  async makeInvite() { throw new StoreError('お試しモードでは、家族を招待できません。Firebase の設定をしてから使ってください。'); }
  async toggleDone(key, by) {
    const t = this.household.today; // ensures day roll-over
    if (this.data.today.done[key]) delete this.data.today.done[key];
    else this.data.today.done[key] = { by, at: nowMin() };
    this._save();
  }
  async togglePack(key) { const p = this.data.today.pack; p[key] = !p[key]; this._save(); }
  async addDuty(when, title) { this.data.duties.push({ id: String(Date.now()), when, title, detail: '', assignee: '' }); this._save(); }
  async setAssignee(id, name) { const d = this.data.duties.find(x => x.id === id); if (d) d.assignee = name; this._save(); }
  async removeDuty(id) { this.data.duties = this.data.duties.filter(x => x.id !== id); this._save(); }
  async updateAnswers(answers, selfName) {
    this.data.h.answers = answers;
    if (selfName) this.data.h.selfName = selfName;
    this.data.h.items = newHousehold({ answers }).items;
    this._save();
  }
  async leave() { this.data = null; try { localStorage.removeItem('mk-local'); } catch {} this._save(); }
}

/* ---------------- Firebase（家族で共有） ---------------- */
class FirebaseStore {
  constructor(cfg) { this.cfg = cfg; this.mode = 'firebase'; this.listeners = new Set(); this.unsubs = []; this.state = null; }

  async init() {
    const [{ initializeApp }, A, F] = await Promise.all([
      import('firebase/app'), import('firebase/auth'), import('firebase/firestore')]);
    this.F = F;
    const app = initializeApp(this.cfg);
    this.auth = A.getAuth(app);
    this.db = F.getFirestore(app);
    if (this.cfg.emulatorHost) {   // 開発用（Firebase エミュレーター）
      A.connectAuthEmulator(this.auth, `http://${this.cfg.emulatorHost}:9099`, { disableWarnings: true });
      F.connectFirestoreEmulator(this.db, this.cfg.emulatorHost, 8080);
    }
    if (!this.auth.currentUser) await A.signInAnonymously(this.auth);
    this.uid = this.auth.currentUser.uid;
    let hid = null; try { hid = localStorage.getItem('mk-hid'); } catch {}
    if (hid) await this._subscribe(hid);
  }

  get household() { return this.state; }
  onChange(fn) { this.listeners.add(fn); return () => this.listeners.delete(fn); }
  _emit() { this.listeners.forEach(f => f(this.state)); }

  async _subscribe(hid) {
    const F = this.F; this.unsubs.forEach(u => u()); this.unsubs = [];
    this.hid = hid; try { localStorage.setItem('mk-hid', hid); } catch {}
    const parts = { h: null, members: [], today: { done: {}, pack: {} }, duties: [] };
    const build = () => {
      if (!parts.h) return;
      this.state = { ...parts.h, id: hid, members: parts.members, today: parts.today, duties: parts.duties };
      this._emit();
    };
    const hRef = F.doc(this.db, 'households', hid);
    const first = await F.getDoc(hRef).catch(() => null);
    if (!first || !first.exists()) { this.state = null; try { localStorage.removeItem('mk-hid'); } catch {} this._emit(); return; }
    parts.h = first.data();
    this.unsubs.push(F.onSnapshot(hRef, s => { if (s.exists()) { parts.h = s.data(); build(); } }));
    this.unsubs.push(F.onSnapshot(F.collection(hRef, 'members'), q => { parts.members = q.docs.map(d => ({ uid: d.id, ...d.data() })); build(); }));
    this.unsubs.push(F.onSnapshot(F.collection(hRef, 'duties'), q => { parts.duties = q.docs.map(d => ({ id: d.id, ...d.data() })); build(); }));
    this._dayKey = dayKey();
    this.unsubs.push(F.onSnapshot(F.doc(hRef, 'days', this._dayKey), s => {
      const d = s.exists() ? s.data() : {}; parts.today = { done: d.done || {}, pack: d.pack || {} }; build(); }));
    build();
  }

  async createHousehold({ answers, selfName, myName }) {
    const F = this.F;
    const hRef = F.doc(F.collection(this.db, 'households'));
    await F.setDoc(hRef, { ...newHousehold({ answers, selfName }), items: newHousehold({ answers }).items.map(i => ({ key: i[0], title: i[1], min: i[2], med: i[3] })),
                            packItems: DEFAULT_PACK.map(p => ({ key: p[0], title: p[1] })), ownerUid: this.uid, createdAt: F.serverTimestamp() });
    await F.setDoc(F.doc(hRef, 'members', this.uid), { name: myName, role: 'family', code: '' });
    await this._subscribe(hRef.id);
  }

  async makeInvite() {
    const F = this.F;
    for (let i = 0; i < 5; i++) {
      const code = String(Math.floor(Math.random() * 1e8)).padStart(CODE_LENGTH, '0');
      const ref = F.doc(this.db, 'invites', code);
      const old = await F.getDoc(ref).catch(() => null);
      if (old && old.exists() && old.data().expires.toMillis() > Date.now()) continue;
      const expires = F.Timestamp.fromMillis(Date.now() + INVITE_HOURS * 3600e3);
      try {
        await F.setDoc(ref, { householdId: this.hid, expires, createdBy: this.uid });
        return { code, expires: expires.toDate() };
      } catch (e) { continue; }
    }
    throw new StoreError('招待コードを作れませんでした。通信できる場所で、もう一度お試しください。');
  }

  async join(code, { name, role }) {
    const F = this.F;
    const inv = await F.getDoc(F.doc(this.db, 'invites', code)).catch(() => null);
    if (!inv || !inv.exists()) throw new StoreError('このコードは見つかりませんでした。数字をもう一度確かめてください。');
    const { householdId, expires } = inv.data();
    if (expires.toMillis() < Date.now()) throw new StoreError('このコードは有効期限（24時間）が切れています。ご家族に新しいコードを作ってもらってください。');
    await F.setDoc(F.doc(this.db, 'households', householdId, 'members', this.uid), { name: name || '', role, code });
    await this._subscribe(householdId);
  }

  _day() { return this.F.doc(this.db, 'households', this.hid, 'days', dayKey()); }
  async toggleDone(key, by) {
    const F = this.F, cur = this.state?.today?.done?.[key];
    await F.setDoc(this._day(), { done: { [key]: cur ? F.deleteField() : { by, at: nowMin() } } }, { merge: true });
  }
  async togglePack(key) {
    const F = this.F, cur = !!this.state?.today?.pack?.[key];
    await F.setDoc(this._day(), { pack: { [key]: !cur } }, { merge: true });
  }
  async addDuty(when, title) { const F = this.F; await F.addDoc(F.collection(this.db, 'households', this.hid, 'duties'), { when, title, detail: '', assignee: '' }); }
  async setAssignee(id, name) { const F = this.F; await F.updateDoc(F.doc(this.db, 'households', this.hid, 'duties', id), { assignee: name }); }
  async removeDuty(id) { const F = this.F; await F.deleteDoc(F.doc(this.db, 'households', this.hid, 'duties', id)); }
  /** 困りごとの選び直し。家族グループ・記録・分担はそのまま。薬の有無が変わったら、ごはん・おくすりの一覧も合わせる。 */
  async updateAnswers(answers, selfName) {
    const F = this.F;
    const items = newHousehold({ answers }).items.map(i => ({ key: i[0], title: i[1], min: i[2], med: i[3] }));
    await F.updateDoc(F.doc(this.db, 'households', this.hid), { answers, items, ...(selfName ? { selfName } : {}) });
  }
  async leave() {
    const F = this.F;
    if (this.hid) await F.deleteDoc(F.doc(this.db, 'households', this.hid, 'members', this.uid)).catch(() => {});
    this.unsubs.forEach(u => u()); this.unsubs = []; this.state = null; this.hid = null;
    try { localStorage.removeItem('mk-hid'); } catch {}
    this._emit();
  }
}
