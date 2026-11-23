/**
 * 忘年会2026 LP — Google Apps Script バックエンド
 *
 * スプレッドシートに紐づけて使います（拡張機能 → Apps Script）。
 * 手順は README.md を参照。
 *
 * シート構成（自動作成）
 *   フォームの回答 1 : Googleフォームの回答（setupForm() で自動リンク）
 *   Questions        : 出題順・ニュース本文・本人・公開状態
 *   Answers          : 回答ログ（1人1問1回のみ）
 */

var MEMBERS = [
  'さわこ', 'まゆ', 'ちさ', 'みも', 'まいける', 'ちゃむ', 'さくら',
  '大ちゃん', 'こーすけ', 'じゅんぺ', 'にいくん', 'ゆうと氏'
];

var SHEET_Q = 'Questions';
var SHEET_A = 'Answers';

/* ---------- Web アプリ ---------- */

function doGet() {
  return HtmlService.createHtmlOutputFromFile('index')
    .setTitle('忘年会2026')
    .addMetaTag('viewport', 'width=device-width, initial-scale=1')
    .setXFrameOptionsMode(HtmlService.XFrameOptionsMode.ALLOWALL);
}

/* ---------- アンケートの文言 ---------- */
var FORM_TITLE = '【ガールズ忘年会2026】事前アンケート';
var FORM_DESC =
  '12/30のガールズ忘年会 with ボーイズで「この大ニュース、誰の？」クイズを出題します。\n' +
  '名前は伏せて出題するので、正直に・ちょっと盛って書いてください！\n' +
  '【回答締切】12月27日（日）23:59\n' +
  '※回答は幹事以外には当日まで見えません。';
var Q_NAME = 'あなたのお名前';
var Q_NEWS = '2026個人的大ニュース';
var Q_NEWS_HELP =
  '例：推しのライブに初参戦した／料理で砂糖と塩をまちがえた　など。1〜2文で、ちょっと盛ってOK！\n' +
  '※「夫が」「子どもが」など、すぐ本人とわかる書き方はちょっとぼかしてね';
var Q_EPI = '当日聞かれたら話したいエピソード（任意）';
var Q_EPI_HELP = '正解発表のあと、司会がネタ振りに使います。LPには表示されません。';
// 以前の質問名（すでに集まった回答の列名）も読めるようにする
var Q_NEWS_ALIASES = [Q_NEWS, '2026年の個人的大ニュース'];

/* ---------- 初期設定（エディタから1回だけ実行） ---------- */

/** 事前アンケート用 Googleフォームを作成し、このスプレッドシートに回答を連携します。 */
function setupForm() {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var form = FormApp.create(FORM_TITLE);
  form.setDescription(FORM_DESC);
  form.setCollectEmail(false);
  form.setLimitOneResponsePerUser(false);
  form.setAllowResponseEdits(true);
  form.addListItem().setTitle(Q_NAME).setChoiceValues(MEMBERS).setRequired(true);
  form.addParagraphTextItem().setTitle(Q_NEWS).setHelpText(Q_NEWS_HELP).setRequired(true);
  form.addParagraphTextItem().setTitle(Q_EPI).setHelpText(Q_EPI_HELP).setRequired(false);
  form.setDestination(FormApp.DestinationType.SPREADSHEET, ss.getId());
  form.setCustomClosedFormMessage('回答の受付は12月27日で締め切りました。当日のクイズをお楽しみに！');

  // 締切：12/28 0:00（日本時間）に自動で回答受付を終了
  PropertiesService.getScriptProperties().setProperty('FORM_ID', form.getId());
  ScriptApp.getProjectTriggers().forEach(function (t) {
    if (t.getHandlerFunction() === 'closeForm') ScriptApp.deleteTrigger(t);
  });
  ScriptApp.newTrigger('closeForm').timeBased().at(new Date('2026-12-28T00:00:00+09:00')).create();

  Logger.log('回答用URL: ' + form.getPublishedUrl());
  Logger.log('編集用URL: ' + form.getEditUrl());
  return form.getPublishedUrl();
}

/**
 * すでに作ったフォームの文言だけを最新にします（URLは変わりません。回答も消えません）。
 * エディタで updateForm を選んで1回実行してください。
 */
function updateForm() {
  var id = PropertiesService.getScriptProperties().getProperty('FORM_ID');
  if (!id) throw new Error('フォームIDが見つかりません。Googleフォームの編集画面で直接直してください');
  var form = FormApp.openById(id);
  form.setTitle(FORM_TITLE);
  form.setDescription(FORM_DESC);
  var done = [];
  form.getItems().forEach(function (it) {
    var t = it.getTitle();
    if (Q_NEWS_ALIASES.indexOf(t) >= 0) { it.asParagraphTextItem().setTitle(Q_NEWS).setHelpText(Q_NEWS_HELP); done.push('大ニュース'); }
    else if (t === Q_EPI) { it.asParagraphTextItem().setHelpText(Q_EPI_HELP); done.push('エピソード'); }
  });
  Logger.log('更新しました：タイトル・説明文・' + done.join('・'));
  return done;
}

/** 回答受付を終了（締切トリガーから自動実行。手動実行でも可） */
function closeForm() {
  var id = PropertiesService.getScriptProperties().getProperty('FORM_ID');
  if (id) FormApp.openById(id).setAcceptingResponses(false);
}

/** 幹事用PINを設定します（エディタで PIN を書き換えて1回実行）。 */
function setAdminPin() {
  var PIN = '1230'; // ← 好きな数字に変更してから実行
  PropertiesService.getScriptProperties().setProperty('ADMIN_PIN', PIN);
  Logger.log('ADMIN_PIN を設定しました');
}

/* ---------- 内部ヘルパー ---------- */

function ss_() { return SpreadsheetApp.getActiveSpreadsheet(); }

function sheet_(name, header) {
  var sh = ss_().getSheetByName(name);
  if (!sh) {
    sh = ss_().insertSheet(name);
    sh.appendRow(header);
    sh.setFrozenRows(1);
  }
  return sh;
}

function qSheet_() { return sheet_(SHEET_Q, ['no', 'owner', 'news', 'status']); }   // status: hidden / open / revealed
function aSheet_() { return sheet_(SHEET_A, ['timestamp', 'player', 'no', 'guess']); }

function checkPin_(pin) {
  var p = PropertiesService.getScriptProperties().getProperty('ADMIN_PIN');
  if (!p) throw new Error('PINが未設定です（Apps Script で setAdminPin を実行してください）');
  if (String(pin) !== String(p)) throw new Error('PINが違います');
}

function rows_(sh) {
  var v = sh.getDataRange().getValues();
  v.shift();
  return v.filter(function (r) { return r[0] !== ''; });
}

function newsCol_(header) {
  for (var k = 0; k < Q_NEWS_ALIASES.length; k++) { var i = header.indexOf(Q_NEWS_ALIASES[k]); if (i >= 0) return i; }
  return -1;
}

function findResponseSheet_() {
  var sheets = ss_().getSheets();
  for (var i = 0; i < sheets.length; i++) {
    var h = sheets[i].getRange(1, 1, 1, Math.max(1, sheets[i].getLastColumn())).getValues()[0];
    if (h.indexOf(Q_NAME) >= 0 && newsCol_(h) >= 0) return sheets[i];
  }
  throw new Error('フォームの回答シートが見つかりません（setupForm を実行しましたか？）');
}

/* ---------- 公開API（クライアントから google.script.run で呼ぶ） ---------- */

/** 画面表示用の状態。本人名は「正解発表済み」の問題だけ返します。 */
function getState(player) {
  var qs = rows_(qSheet_());
  var as = rows_(aSheet_());
  var mine = {};
  var answeredCount = {};
  var votes = {}; // 問題No → { 予想した名前: 票数 }
  as.forEach(function (a) {
    answeredCount[a[2]] = (answeredCount[a[2]] || 0) + 1;
    if (a[1] === player) mine[a[2]] = a[3];
    votes[a[2]] = votes[a[2]] || {};
    votes[a[2]][a[3]] = (votes[a[2]][a[3]] || 0) + 1;
  });
  var questions = qs.map(function (q) {
    var revealed = q[3] === 'revealed';
    return {
      no: q[0],
      news: q[3] === 'hidden' ? null : q[2],
      status: q[3],
      owner: revealed ? q[1] : null,
      isMine: q[1] === player,
      myGuess: mine[q[0]] || null,
      answered: answeredCount[q[0]] || 0,
      // みんなの予想と正解数は、正解発表後だけ返す
      votes: revealed ? (votes[q[0]] || {}) : null,
      correct: revealed ? ((votes[q[0]] || {})[q[1]] || 0) : null
    };
  });
  return { members: MEMBERS, questions: questions, ranking: ranking_(qs, as) };
}

/** 回答を登録。同じ人・同じ問題は1回だけ（2回目以降はエラー）。 */
function submitAnswer(player, no, guess) {
  if (MEMBERS.indexOf(player) < 0) throw new Error('名前を選んでください');
  if (MEMBERS.indexOf(guess) < 0) throw new Error('回答が不正です');
  var lock = LockService.getScriptLock();
  lock.waitLock(10000);
  try {
    var q = rows_(qSheet_()).filter(function (r) { return String(r[0]) === String(no); })[0];
    if (!q) throw new Error('問題が見つかりません');
    if (q[3] !== 'open') throw new Error('この問題は回答受付中ではありません');
    if (q[1] === player) throw new Error('自分のニュースには回答できません');
    var dup = rows_(aSheet_()).some(function (a) { return a[1] === player && String(a[2]) === String(no); });
    if (dup) throw new Error('この問題はすでに回答済みです（変更できません）');
    aSheet_().appendRow([new Date(), player, Number(no), guess]);
  } finally {
    lock.releaseLock();
  }
  return getState(player);
}

function ranking_(qs, as) {
  var owner = {};
  qs.forEach(function (q) { if (q[3] === 'revealed') owner[q[0]] = q[1]; });
  var score = {};
  MEMBERS.forEach(function (m) { score[m] = 0; });
  as.forEach(function (a) { if (owner[a[2]] && owner[a[2]] === a[3]) score[a[1]]++; });
  return MEMBERS.map(function (m) { return { name: m, score: score[m] }; })
    .sort(function (x, y) { return y.score - x.score; });
}

/* ---------- 幹事用API ---------- */

/** フォームの回答から出題リストを作成（順番はシャッフル）。既存の Questions / Answers は消去。 */
function adminBuildQuestions(pin) {
  checkPin_(pin);
  var rs = findResponseSheet_();
  var v = rs.getDataRange().getValues();
  var h = v.shift();
  var iName = h.indexOf(Q_NAME), iNews = newsCol_(h);
  var latest = {}; // 同じ人が複数回答した場合は最新を採用
  v.forEach(function (r) { if (r[iName]) latest[r[iName]] = r[iNews]; });
  var list = Object.keys(latest).map(function (k) { return [k, latest[k]]; });
  for (var i = list.length - 1; i > 0; i--) {
    var j = Math.floor(Math.random() * (i + 1));
    var t = list[i]; list[i] = list[j]; list[j] = t;
  }
  var qs = qSheet_(); qs.clear(); qs.appendRow(['no', 'owner', 'news', 'status']);
  var as = aSheet_(); as.clear(); as.appendRow(['timestamp', 'player', 'no', 'guess']);
  list.forEach(function (r, idx) { qs.appendRow([idx + 1, r[0], r[1], 'hidden']); });
  var missing = MEMBERS.filter(function (m) { return !latest[m]; });
  return { count: list.length, missing: missing };
}

/** 問題の状態を変更：open（出題）/ revealed（正解発表）/ hidden（隠す） */
function adminSetStatus(pin, no, status) {
  checkPin_(pin);
  if (['hidden', 'open', 'revealed'].indexOf(status) < 0) throw new Error('status不正');
  var sh = qSheet_();
  var v = sh.getDataRange().getValues();
  for (var i = 1; i < v.length; i++) {
    if (String(v[i][0]) === String(no)) {
      var cur = v[i][3];
      if (status === 'revealed' && cur !== 'open') throw new Error('出題中の問題だけ正解発表できます');
      if (status === 'open') {
        for (var j = 1; j < v.length; j++) if (j !== i && v[j][3] === 'open') throw new Error('Q.' + v[j][0] + ' がまだ出題中です。先に正解発表してください');
      }
      sh.getRange(i + 1, 4).setValue(status);
      break;
    }
  }
  return adminGetState(pin);
}

/** 幹事画面用：本人名・エピソードも含む */
function adminGetState(pin) {
  checkPin_(pin);
  var qs = rows_(qSheet_());
  var as = rows_(aSheet_());
  var epi = {};
  try {
    var rs = findResponseSheet_();
    var v = rs.getDataRange().getValues(); var h = v.shift();
    var iName = h.indexOf(Q_NAME), iEpi = h.indexOf(Q_EPI);
    v.forEach(function (r) { if (iEpi >= 0) epi[r[iName]] = r[iEpi]; });
  } catch (e) { /* 回答シート未作成 */ }
  return {
    members: MEMBERS,
    questions: qs.map(function (q) {
      var ans = as.filter(function (a) { return String(a[2]) === String(q[0]); });
      return {
        no: q[0], owner: q[1], news: q[2], status: q[3], episode: epi[q[1]] || '',
        answered: ans.length,
        correct: ans.filter(function (a) { return a[3] === q[1]; }).length
      };
    }),
    ranking: ranking_(qs, as)
  };
}
