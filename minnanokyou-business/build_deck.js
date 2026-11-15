const pptxgen = require('pptxgenjs');
const React = require('react');
const ReactDOMServer = require('react-dom/server');
const sharp = require('sharp');
const fa = require('react-icons/fa');
const { applyTheme } = require('/root/.claude/skills/synced/87014927-dff5-4c30-92c6-29ab60e5fd43_3d32d3db-cc0b-469b-beb4-8b235c3b3cd1/pptx/scripts/apply_theme.js');

const THEME = {
  name: 'Minna no Kyou',
  headFontFace: 'Yu Gothic',
  bodyFontFace: 'Yu Gothic',
  colors: {
    dk1: '1D2A27', lt1: 'FFFFFF', dk2: '1F5A4E', lt2: 'EEF4F1',
    accent1: '1F5A4E', accent2: '8A4B00', accent3: 'F4C978', accent4: 'DCEBE6', accent5: '44524E', accent6: 'FBEBCF',
    hlink: '1F5A4E', folHlink: '44524E',
  },
};
const HEX = THEME.colors;

async function icon(Comp, color, size = 256) {
  const svg = ReactDOMServer.renderToStaticMarkup(React.createElement(Comp, { color: '#' + color, size }));
  const buf = await sharp(Buffer.from(svg)).png().toBuffer();
  return 'image/png;base64,' + buf.toString('base64');
}

(async () => {
  const pres = new pptxgen();
  pres.layout = 'LAYOUT_WIDE'; // 13.33 x 7.5
  pres.title = 'みんなのきょう 収益化の道筋';
  pres.author = 'みんなのきょう 制作チーム';
  pres.theme = { headFontFace: THEME.headFontFace, bodyFontFace: THEME.bodyFontFace };
  const C = pres.SchemeColor;
  const W = 13.333;

  // ---------- layouts ----------
  pres.defineSlideMaster({
    title: 'TITLE_DARK',
    background: { color: C.accent1 },
    objects: [
      { placeholder: { options: { name: 'title', type: 'title', x: 0.8, y: 2.0, w: 11.7, h: 1.7, fontSize: 44, bold: true, color: C.background1, valign: 'bottom', align: 'left' }, text: '' } },
      { placeholder: { options: { name: 'body', type: 'body', x: 0.8, y: 3.9, w: 11.7, h: 2.6, fontSize: 20, color: C.accent4, valign: 'top', align: 'left' }, text: '' } },
    ],
  });
  pres.defineSlideMaster({
    title: 'CONTENT',
    background: { color: C.background1 },
    margin: [0.5, 0.6, 0.6, 0.6],
    objects: [
      { placeholder: { options: { name: 'title', type: 'title', x: 0.6, y: 0.35, w: 12.1, h: 0.9, fontSize: 30, bold: true, color: C.text1, valign: 'middle', align: 'left' }, text: '' } },
      { text: { text: 'みんなのきょう　収益化の道筋（提案）', options: { x: 0.6, y: 7.0, w: 8, h: 0.3, fontSize: 10, color: C.accent5 } } },
    ],
    slideNumber: { x: 12.2, y: 7.0, w: 0.5, h: 0.3, fontSize: 10, color: C.accent5, align: 'right' },
  });

  const content = (sec, title) => {
    const s = pres.addSlide({ masterName: 'CONTENT', sectionTitle: sec });
    s.addText(title, { placeholder: 'title' });
    return s;
  };
  const note = (s, t) => s.addText(t, { x: 0.6, y: 6.55, w: 12.1, h: 0.35, fontSize: 10, color: C.accent5, isTextBox: true, margin: 0, objectName: 'source' });

  const ic = {
    sun: await icon(fa.FaSun, HEX.accent3), users: await icon(fa.FaUsers, 'FFFFFF'), building: await icon(fa.FaBuilding, 'FFFFFF'),
    landmark: await icon(fa.FaLandmark, 'FFFFFF'), hands: await icon(fa.FaHandsHelping, 'FFFFFF'), phone: await icon(fa.FaMobileAlt, 'FFFFFF'),
    shield: await icon(fa.FaShieldAlt, 'FFFFFF'), chart: await icon(fa.FaChartLine, 'FFFFFF'), check: await icon(fa.FaCheck, 'FFFFFF'),
    globe: await icon(fa.FaGlobeAsia, 'FFFFFF'), book: await icon(fa.FaBookOpen, 'FFFFFF'), apple: await icon(fa.FaApple, 'FFFFFF'),
  };
  const circleIcon = (s, data, x, y, d, fill, name) => {
    s.addShape(pres.shapes.OVAL, { x, y, w: d, h: d, fill: { color: fill }, line: { type: 'none' }, objectName: name + ' circle' });
    s.addImage({ data, x: x + d * 0.25, y: y + d * 0.25, w: d * 0.5, h: d * 0.5, objectName: name + ' icon', altText: name });
  };

  // ---------- 1. title ----------
  pres.addSection({ title: 'はじめに' });
  let s = pres.addSlide({ masterName: 'TITLE_DARK', sectionTitle: 'はじめに' });
  s.addImage({ data: ic.sun, x: 0.8, y: 1.0, w: 0.9, h: 0.9, objectName: 'sunrise icon', altText: '朝日のマーク' });
  s.addText('みんなのきょう\n収益化の道筋（提案）', { placeholder: 'title' });
  s.addText('無料の試用から、法人向けの小さな収入へ。2026年11月　制作チーム', { placeholder: 'body' });
  s.addNotes('同僚向けの提案です。結論は「最初の収入は企業の介護両立支援から得て、見守りに必要な機能はずっと無料にする」です。金額はすべて仮定の試算で、Phase 0 の実証で確かめます。');

  // ---------- 2. summary ----------
  s = content('はじめに', '結論：最初の収入は「企業の介護両立支援」から');
  s.addText('毎日の見守りに必要な機能はずっと無料。お金は、家族を支える側（企業・自治体）からいただく', {
    x: 0.6, y: 1.35, w: 12.1, h: 0.6, fontSize: 18, color: C.accent1, bold: true, isTextBox: true, margin: 0 });
  const sumCards = [
    ['まず実証', 'Phase 0（〜3か月）', '無料のWeb版で5〜10家庭に使ってもらい、続くか・支払う気持ちがあるかを測る', ic.check],
    ['法人で収入', 'Phase 1（4〜9か月）', '社員の「仕事と介護の両立」を支える福利厚生として、企業1〜2社に有料で試してもらう', ic.building],
    ['個人・自治体へ', 'Phase 2〜3（10か月〜）', 'iPhoneアプリで個人向けの有料プラン、その後に自治体・介護事業所との連携', ic.landmark],
  ];
  sumCards.forEach(([h, p, b, icn], i) => {
    const x = 0.6 + i * 4.1;
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y: 2.25, w: 3.8, h: 3.9, rectRadius: 0.12, fill: { color: C.background2 }, line: { type: 'none' }, objectName: `summary card ${i + 1}` });
    circleIcon(s, icn, x + 0.3, 2.5, 0.8, C.accent1, `summary ${i + 1}`);
    s.addText(p, { x: x + 0.3, y: 3.45, w: 3.2, h: 0.35, fontSize: 12, color: C.accent2, bold: true, isTextBox: true, margin: 0 });
    s.addText(h, { x: x + 0.3, y: 3.8, w: 3.2, h: 0.5, fontSize: 22, color: C.text1, bold: true, isTextBox: true, margin: 0 });
    s.addText(b, { x: x + 0.3, y: 4.4, w: 3.2, h: 1.6, fontSize: 14, color: C.text1, valign: 'top', isTextBox: true, margin: 0 });
  });
  note(s, '金額・期間はすべて提案段階の仮定です。Phase 0 の結果で見直します。');
  s.addNotes('3つのフェーズで段階的に進めます。いきなり個人から月額をいただくのではなく、最初は法人。理由は次のスライド以降で説明します。');

  // ---------- 3. why now ----------
  pres.addSection({ title: '市場と根拠' });
  s = content('市場と根拠', 'なぜ今か：働きながら家族を支える人が増えている');
  const stats = [
    ['471.6万人', '高齢者の認知症（2025年推計）\n高齢者の12.9%', '厚生労働省 研究班（2024年公表）'],
    ['約28%', '高齢者の認知症＋MCI\n（2022年）', '同上'],
    ['318万人', '働きながら家族を介護する\n「ビジネスケアラー」（2030年見込み）', '経済産業省（2023年3月）'],
    ['約9.1兆円', '仕事と介護の両立が難しいことによる\n経済損失（2030年試算）', '同上'],
  ];
  stats.forEach(([n, l, src], i) => {
    const x = 0.6 + i * 3.08;
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y: 1.6, w: 2.85, h: 3.9, rectRadius: 0.12, fill: { color: i < 2 ? C.background2 : C.accent6 }, line: { type: 'none' }, objectName: `stat card ${i + 1}` });
    s.addText(n, { x: x + 0.2, y: 1.9, w: 2.45, h: 1.1, fontSize: 32, bold: true, color: i < 2 ? C.accent1 : C.accent2, isTextBox: true, margin: 0 });
    s.addText(l, { x: x + 0.2, y: 3.1, w: 2.45, h: 1.4, fontSize: 14, color: C.text1, valign: 'top', isTextBox: true, margin: 0 });
    s.addText(src, { x: x + 0.2, y: 4.75, w: 2.45, h: 0.5, fontSize: 10, color: C.accent5, valign: 'top', isTextBox: true, margin: 0 });
  });
  s.addText('家族の困りごとの1位は「先の見通しが立たない」44.7%（ニッセイ基礎研究所、2019年7月調査）。予定と記録を共有するこのアプリの役割と重なる', {
    x: 0.6, y: 5.75, w: 12.1, h: 0.6, fontSize: 14, color: C.text1, isTextBox: true, margin: 0 });
  note(s, '出典の詳細は最後のスライド。ビジネスケアラーと経済損失は経済産業省の委託による推計です。');

  // ---------- 3b. social issues ----------
  s = content('市場と根拠', 'このアプリが解決する社会課題');
  const ih = (t) => ({ text: t, options: { bold: true, color: C.background1, fill: { color: C.accent1 } } });
  const issueRows = [
    [ih('社会課題'), ih('アプリでの解決のしかた'), ih('期待する変化（Phase 0 で確かめる）')],
    ['先の見通しが持てない', '今日のボードで、予定・お迎え・済みが一目で分かる', '「今日は大丈夫か」という不安が減る'],
    ['同じことを何度も聞かれる', 'ご本人の画面に大きな文字で「いま」「つぎ」を表示', 'ご本人が自分で確かめ、聞き返しが減る'],
    ['離れた親のご飯・薬が心配', '「済み」をワンタップで記録し、家族全員にすぐ反映', '確認の電話が減り、飲み忘れに早く気づける'],
    ['介護が一人に偏る', '家族の分担表と記録で、だれが何をしたかが見える', '遠くの家族も役割を持てる'],
    ['仕事と介護の両立が難しい', '職場からも様子が分かる。企業の福利厚生として導入', '休む・辞めることを減らす手助けになる'],
    ['ご本人の自立と尊厳', 'ご本人が自分で「済み」を押せる。責めない言葉づかい', '自分で生活を回す人でいられる'],
  ];
  s.addTable(issueRows, { x: 0.6, y: 1.4, w: 12.1, colW: [3.0, 5.0, 4.1], fontSize: 13, color: C.text1, valign: 'middle',
    border: { type: 'solid', pt: 0.75, color: 'D5DDD9' }, rowH: [0.42, 0.62, 0.62, 0.62, 0.62, 0.62, 0.62], objectName: 'social issue table' });
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 0.6, y: 5.95, w: 12.1, h: 0.5, rectRadius: 0.08, fill: { color: C.accent6 }, line: { type: 'none' }, objectName: 'scope callout' });
  s.addText('解決しないこと：病気の診断・治療・予防（「進行を遅らせる」とは言わない）、緊急時の対応、位置の見守り', {
    x: 0.8, y: 5.95, w: 11.8, h: 0.5, fontSize: 13, color: C.accent2, bold: true, valign: 'middle', isTextBox: true, margin: 0 });
  note(s, '効果はまだ確かめていません。Phase 0 で継続率・「済み」の記録数・家族の満足度・聞き返しや確認の電話の回数の変化を測ります。');
  s.addNotes('左が社会課題、中央がアプリの仕組み、右が期待する変化です。右の列はまだ仮説で、Phase 0 で確かめます。認知症基本法（2024年1月施行）がめざす共生の考え方にも沿っています。');

  // ---------- 4. where we are ----------
  s = content('市場と根拠', '現在地：Web版は公開済み、iPhoneアプリはコードまで');
  const now = [
    ['Web版（無料）', '公開済み。家族共有・8けたの招待コード・済みチェック・ご本人の画面・説明書', ic.globe, true],
    ['iPhoneアプリ', 'コード一式あり。Mac でのビルド・実機テストはこれから', ic.apple, false],
    ['App Store の準備', '名前・説明文・説明画像5枚・アイコン・審査メモ', ic.phone, true],
    ['設計の根拠', '家族の悩み30項目と対応機能、見やすい配色、法務の確認リスト', ic.book, true],
  ];
  now.forEach(([h, b, icn, done], i) => {
    const y = 1.5 + i * 1.2;
    circleIcon(s, icn, 0.6, y, 0.85, done ? C.accent1 : C.accent2, `status ${i + 1}`);
    s.addText(h, { x: 1.7, y, w: 3.4, h: 0.85, fontSize: 18, bold: true, color: C.text1, valign: 'middle', isTextBox: true, margin: 0 });
    s.addText(b, { x: 5.1, y, w: 7.6, h: 0.85, fontSize: 14, color: C.text1, valign: 'middle', isTextBox: true, margin: 0 });
  });
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 0.6, y: 6.0, w: 12.1, h: 0.5, rectRadius: 0.08, fill: { color: C.accent6 }, line: { type: 'none' }, objectName: 'gap callout' });
  s.addText('まだないもの：アプリを閉じているときのお知らせ（Web版）、利用者の実データ、支払う意向の確認', {
    x: 0.8, y: 6.0, w: 11.8, h: 0.5, fontSize: 14, color: C.accent2, bold: true, valign: 'middle', isTextBox: true, margin: 0 });

  // ---------- 5. who pays ----------
  pres.addSection({ title: '収益化の道筋' });
  s = content('収益化の道筋', 'だれが払うか：4つの候補のうち、企業が最も早い');
  const hdr = (t) => ({ text: t, options: { bold: true, color: C.background1, fill: { color: C.accent1 } } });
  const rows = [
    [hdr('払う人'), hdr('何に払うか'), hdr('根拠'), hdr('収入までの早さ'), hdr('難しさ')],
    ['個人・家族', '月額の有料プラン', '予定共有アプリの有料版の例：月300円（TimeTree）', '遅い（App Store 公開後）', '支払う人が少ない可能性。安全機能は有料にできない'],
    [{ text: '企業（福利厚生）', options: { bold: true, color: C.accent1 } }, '社員の介護と仕事の両立支援', '2025年4月から介護の個別周知・意向確認などが事業主の義務に', { text: '早い', options: { bold: true, color: C.accent1 } }, '営業が必要。導入先の評価をどう示すか'],
    ['自治体', '認知症施策・家族支援', '認知症基本法（2024年1月施行）。自治体の計画づくりは努力義務', '遅い（予算は年度単位）', '実績と信頼が先に必要'],
    ['介護事業所', '家族との連絡のデジタル化', '介護テクノロジー導入の補助（国2/3・都道府県が実施）', '中くらい', '補助の対象になるかは確認が必要'],
  ];
  s.addTable(rows, { x: 0.6, y: 1.45, w: 12.1, colW: [1.9, 2.2, 3.7, 1.9, 2.4], fontSize: 13, color: C.text1, valign: 'middle',
    border: { type: 'solid', pt: 0.75, color: 'D5DDD9' }, rowH: [0.45, 0.95, 0.95, 0.95, 0.95], objectName: 'payer comparison' });
  note(s, '企業の行は強調。金額の例は TimeTree の App Store 掲載（月300円・年3,000円）。補助の対象可否は都道府県の要綱で確認が必要です。');

  // ---------- 6. why companies ----------
  s = content('収益化の道筋', '企業向けから始める理由と、提供する内容');
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 0.6, y: 1.45, w: 5.9, h: 4.9, rectRadius: 0.12, fill: { color: C.background2 }, line: { type: 'none' }, objectName: 'reasons card' });
  s.addText('理由', { x: 0.9, y: 1.65, w: 5.3, h: 0.45, fontSize: 20, bold: true, color: C.accent1, isTextBox: true, margin: 0 });
  s.addText([
    { text: '法律で企業の取り組みが求められている：2025年4月から、介護に直面した社員への制度の周知・意向確認、40歳頃の情報提供などが事業主の義務に', options: { bullet: true, breakLine: true } },
    { text: '国が経営者向けガイドラインを公表（経済産業省、2024年3月）', options: { bullet: true, breakLine: true } },
    { text: '社員は無料で使え、家族に「お金の話」をしなくてよい', options: { bullet: true, breakLine: true } },
    { text: '1社の契約で、数十家庭の利用データが早く集まる', options: { bullet: true } },
  ], { x: 0.9, y: 2.2, w: 5.4, h: 4.0, fontSize: 14, color: C.text1, valign: 'top', paraSpaceAfter: 8, isTextBox: true, margin: 0 });
  s.addText('企業に提供するもの（案）', { x: 7.0, y: 1.5, w: 5.7, h: 0.45, fontSize: 20, bold: true, color: C.text1, isTextBox: true, margin: 0 });
  const offer = [['社員と家族のアプリ利用', 'プラス機能を含めて社員の家族グループに提供', ic.users], ['介護の両立の案内', 'アプリ内で会社の制度・相談窓口を表示', ic.hands], ['利用の報告', '個人が分からない形の利用状況（人数・継続率）を定期報告', ic.chart]];
  offer.forEach(([h, b, icn], i) => {
    const y = 2.15 + i * 1.4;
    circleIcon(s, icn, 7.0, y, 0.8, C.accent1, `offer ${i + 1}`);
    s.addText(h, { x: 8.0, y, w: 4.7, h: 0.4, fontSize: 16, bold: true, color: C.text1, isTextBox: true, margin: 0 });
    s.addText(b, { x: 8.0, y: y + 0.42, w: 4.7, h: 0.8, fontSize: 14, color: C.text1, valign: 'top', isTextBox: true, margin: 0 });
  });
  note(s, '利用状況の報告は、家族の健康情報が会社に渡らない形に限る（法務の確認が必要）。');

  // ---------- 7. roadmap ----------
  s = content('収益化の道筋', '道筋：4つのフェーズで、小さく確かめながら広げる');
  const phases = [
    ['Phase 0', '〜2027年2月', '無料で実証', ['Web版を5〜10家庭で4週間', '続くか・役立つかを測る', '支払う意向を聞く'], C.accent5],
    ['Phase 1', '2027年3〜8月', '企業で試験導入', ['企業1〜2社と有料の試験契約', '閉じていても届くお知らせを追加', 'プライバシー・利用規約を整える'], C.accent1],
    ['Phase 2', '2027年9月〜2028年2月', 'iPhoneアプリ公開', ['App Store に公開（無料＋プラス）', '企業を5社に', '個人向けの有料プランを開始'], C.accent1],
    ['Phase 3', '2028年3月〜', '自治体・事業所へ', ['自治体の家族支援事業に提案', '介護事業所との連絡機能', '実績データで信頼をつくる'], C.accent2],
  ];
  s.addShape(pres.shapes.LINE, { x: 0.9, y: 2.0, w: 11.5, h: 0, line: { color: 'D5DDD9', width: 3 }, objectName: 'timeline line' });
  phases.forEach(([p, when, h, items, col], i) => {
    const x = 0.6 + i * 3.08;
    s.addShape(pres.shapes.OVAL, { x: x + 0.15, y: 1.75, w: 0.5, h: 0.5, fill: { color: col }, line: { color: 'FFFFFF', width: 2 }, objectName: `phase dot ${i}` });
    s.addText(p, { x, y: 2.45, w: 2.85, h: 0.4, fontSize: 18, bold: true, color: col, isTextBox: true, margin: 0 });
    s.addText(when, { x, y: 2.85, w: 2.85, h: 0.35, fontSize: 12, color: C.accent5, isTextBox: true, margin: 0 });
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y: 3.3, w: 2.85, h: 3.0, rectRadius: 0.1, fill: { color: C.background2 }, line: { type: 'none' }, objectName: `phase card ${i}` });
    s.addText(h, { x: x + 0.2, y: 3.45, w: 2.45, h: 0.45, fontSize: 16, bold: true, color: C.text1, isTextBox: true, margin: 0 });
    s.addText(items.map((t, j) => ({ text: t, options: { bullet: true, breakLine: j < items.length - 1 } })),
      { x: x + 0.2, y: 3.95, w: 2.5, h: 2.25, fontSize: 13, color: C.text1, valign: 'top', paraSpaceAfter: 6, isTextBox: true, margin: 0 });
  });
  note(s, '時期は提案です。次のフェーズに進むかは、前のフェーズの指標（スライド13）で判断します。');

  // ---------- 8. revenue scenario ----------
  s = content('収益化の道筋', '収入の見込み（仮定の試算）：Phase 2 で月約19万円');
  s.addChart(pres.charts.BAR, [
    { name: '企業', labels: ['Phase 0', 'Phase 1', 'Phase 2'], values: [0, 60000, 150000] },
    { name: '個人（手数料15%差引後）', labels: ['Phase 0', 'Phase 1', 'Phase 2'], values: [0, 0, 40800] },
  ], { x: 0.6, y: 1.45, w: 6.9, h: 4.9, barDir: 'col', barGrouping: 'stacked',
    chartColors: [HEX.accent1, HEX.accent3], showValue: true, dataLabelPosition: 'ctr', dataLabelFormatCode: '#,##0', dataLabelFontSize: 11, dataLabelColor: 'FFFFFF',
    showLegend: true, legendPos: 'b', legendFontSize: 12, legendFontFace: '+mn-lt',
    catAxisLabelColor: HEX.accent5, valAxisLabelColor: HEX.accent5, catAxisLabelFontFace: '+mn-lt', valAxisLabelFontFace: '+mn-lt', dataLabelFontFace: '+mn-lt',
    valAxisLabelFormatCode: '#,##0', valGridLine: { color: 'E3E9E6', size: 0.5 }, catGridLine: { style: 'none' },
    showTitle: true, title: '月あたりの収入（円）', titleFontSize: 14, titleColor: HEX.dk1, titleFontFace: '+mn-lt', objectName: 'revenue chart' });
  s.addText('試算の仮定', { x: 7.9, y: 1.5, w: 4.8, h: 0.45, fontSize: 20, bold: true, color: C.text1, isTextBox: true, margin: 0 });
  s.addText([
    { text: '企業：1社 月3万円（仮）。Phase 1 は2社、Phase 2 は5社', options: { bullet: true, breakLine: true } },
    { text: '個人：月480円（仮）× 100家庭。Apple の手数料15%（Small Business Program）を引いて 40,800円', options: { bullet: true, breakLine: true } },
    { text: 'Phase 2 の合計：約19万円／月（年 約230万円）', options: { bullet: true, bold: true, color: C.accent1, breakLine: true } },
    { text: '金額・社数はすべて仮定。企業向けの相場は確認できていないため、Phase 0〜1 の聞き取りで決める', options: { bullet: true } },
  ], { x: 7.9, y: 2.05, w: 4.8, h: 4.3, fontSize: 14, color: C.text1, valign: 'top', paraSpaceAfter: 8, isTextBox: true, margin: 0 });
  note(s, 'App Store の手数料：Small Business Program 参加で15%（Apple）。月480円は予定共有アプリ（月300円）と見守りサービス（月1,078円）の間に置いた仮の値。');

  // ---------- 9. costs ----------
  s = content('収益化の道筋', 'かかる費用：Phase 0 はほぼ0円、Phase 1 から少しずつ');
  const crow = (a, b, c) => [a, b, c];
  s.addTable([
    [hdr('費用'), hdr('金額'), hdr('いつから')],
    crow('Firebase（データ・公開）無料プラン', '0円（1日の上限あり：読み込み5万回など）', 'Phase 0'),
    crow('閉じていても届くお知らせ（Firebase 従量課金）', '使った分だけ。無料枠あり。金額は利用量で要試算', 'Phase 1'),
    crow('Apple Developer Program', '年99米ドル', 'Phase 2'),
    crow('Mac（iPhoneアプリの作成）', '持っている人の協力で0円', 'Phase 2'),
    crow('法務（利用規約・プライバシー・薬機法の確認）', '確認できていない（見積もりが必要）', 'Phase 1'),
    crow('商標の出願', '確認できていない（見積もりが必要）', 'Phase 1〜2'),
  ], { x: 0.6, y: 1.45, w: 12.1, colW: [5.0, 5.0, 2.1], fontSize: 14, color: C.text1, valign: 'middle',
    border: { type: 'solid', pt: 0.75, color: 'D5DDD9' }, rowH: 0.62, objectName: 'cost table' });
  note(s, '出典：Firebase 料金ページ、Apple Developer Program。金額が未確認のものは「見積もりが必要」としています。');

  // ---------- 10. free vs paid ----------
  s = content('収益化の道筋', '無料と有料の線引き：安全に関わる機能は有料にしない');
  const col = (x, head, fill, headColor, items, name) => {
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y: 1.45, w: 5.85, h: 4.85, rectRadius: 0.12, fill: { color: fill }, line: { type: 'none' }, objectName: name });
    s.addText(head, { x: x + 0.35, y: 1.65, w: 5.2, h: 0.5, fontSize: 22, bold: true, color: headColor, isTextBox: true, margin: 0 });
    s.addText(items.map((t, j) => ({ text: t, options: { bullet: true, breakLine: j < items.length - 1 } })),
      { x: x + 0.35, y: 2.3, w: 5.2, h: 3.8, fontSize: 15, color: C.text1, valign: 'top', paraSpaceAfter: 8, isTextBox: true, margin: 0 });
  };
  col(0.6, 'ずっと無料', C.background2, C.accent1, ['今日のボード（いま・つぎ・きょうのみんな）', 'ごはん・おくすりの「済み」と記録', 'お迎えまでの時間・持ち物', 'お知らせ（届く仕組みができたら）', 'ご本人の画面', '悩みに合わせた機能、家族4人まで'], 'free column');
  col(6.85, 'プラス（有料・案）', C.accent6, C.accent2, ['家族10人まで、ご本人2人（ご両親など）', '記録を期間の制限なく保存', '受診メモのPDF作成', '写真つきの持ち物・手順カード', '家族の声メッセージ', 'ケアマネ・デイサービスとの共有'], 'paid column');
  note(s, '広告は入れない（健康に関わるデータの広告利用は App Review Guidelines 5.1.3 で禁止）。');

  // ---------- 11. risks ----------
  pres.addSection({ title: '実行' });
  s = content('実行', 'リスクと対策');
  s.addTable([
    [hdr('リスク'), hdr('起きること'), hdr('対策')],
    ['医療機器に当たるとみなされる', '販売できない・広告規制', '「予防」「改善」と書かない。不安があれば厚労省・PMDA に相談'],
    ['健康情報の扱い', '家族の信頼を失う', 'Web版は運営者がデータを預かる。プライバシーポリシーと同意の取り方を法務と整える'],
    ['個人での App Store 申請', '審査で法人を求められる', 'まず個人で申請。差し戻されたら法人化か協力法人を検討'],
    ['1人の支払いで家族全員が使える形', 'App Store の決まりに合わない可能性', '法務と Apple に事前に確認。企業契約は App 外の契約で行う'],
    ['お知らせが届かない（Web版）', '飲み忘れ・お迎えの見逃し', 'Phase 1 で届く仕組みを追加。それまでは「届かない」と明示'],
  ], { x: 0.6, y: 1.45, w: 12.1, colW: [3.1, 3.0, 6.0], fontSize: 13, color: C.text1, valign: 'middle',
    border: { type: 'solid', pt: 0.75, color: 'D5DDD9' }, rowH: [0.45, 0.85, 0.85, 0.85, 0.85, 0.85], objectName: 'risk table' });
  note(s, '企業との契約を App の外で結ぶ場合も、アプリ内で機能を開放する方法が App Store の決まり（3.1.1 など）に合うかは確認が必要です。');

  // ---------- 12. KPI ----------
  s = content('実行', 'Phase 0 で確かめること（次に進む判断の目安）');
  const kpis = [['4週間後も使っている家庭', '6割以上', '続く価値があるか'], ['1日の「済み」記録', '1家庭 3件以上', '毎日使われているか'], ['家族の満足度', '5段階で 4以上', '負担が減ったか'], ['お金を払ってもよい', '半数以上が「はい」', 'いくらなら払うかも聞く']];
  kpis.forEach(([h, v, b], i) => {
    const x = 0.6 + (i % 2) * 6.15, y = 1.5 + Math.floor(i / 2) * 2.45;
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w: 5.95, h: 2.2, rectRadius: 0.12, fill: { color: C.background2 }, line: { type: 'none' }, objectName: `kpi card ${i + 1}` });
    s.addText(h, { x: x + 0.35, y: y + 0.25, w: 5.3, h: 0.45, fontSize: 16, bold: true, color: C.text1, isTextBox: true, margin: 0 });
    s.addText(v, { x: x + 0.35, y: y + 0.75, w: 5.3, h: 0.8, fontSize: 32, bold: true, color: C.accent1, isTextBox: true, margin: 0 });
    s.addText(b, { x: x + 0.35, y: y + 1.6, w: 5.3, h: 0.4, fontSize: 13, color: C.accent5, isTextBox: true, margin: 0 });
  });
  note(s, '目安の数値はチームで決める案です（根拠となる統計はありません）。');

  // ---------- 13. ask ----------
  s = pres.addSlide({ masterName: 'TITLE_DARK', sectionTitle: '実行' });
  s.addText('決めてほしいこと', { placeholder: 'title' });
  s.addText([
    { text: '1. Phase 0 の協力家庭（5〜10家庭）を集める担当と時期', options: { breakLine: true } },
    { text: '2. 企業向けの試験導入先の候補（知り合いの人事・総務担当など）', options: { breakLine: true } },
    { text: '3. 法務への相談（プライバシー・利用規約・薬機法）の予算', options: { breakLine: true } },
    { text: '4. 「安全に関わる機能は無料」という方針への合意' },
  ], { placeholder: 'body' });
  s.addNotes('最後に4つの決めごとをお願いします。特に1と4は今日決めたいところです。');

  // ---------- 14. sources ----------
  s = content('実行', '出典');
  s.addText([
    '厚生労働省 研究班「認知症及び軽度認知障害の有病率調査並びに将来推計」2024年公表（mhlw.go.jp/content/001279920.pdf）',
    '経済産業省 ビジネスケアラーの推計（2023年3月）、「仕事と介護の両立支援に関する経営者向けガイドライン」2024年3月26日（meti.go.jp）',
    'ニッセイ基礎研究所 家族介護者調査（2019年7月）（nli-research.co.jp）',
    '厚生労働省 育児・介護休業法 改正のポイント（2025年4月1日施行）（mhlw.go.jp）',
    '認知症基本法（2024年1月1日施行）、認知症施策推進基本計画（2024年12月閣議決定）（厚生労働省資料）',
    '厚生労働省 介護テクノロジー導入支援事業（地域医療介護総合確保基金）、補助金ポータルの都道府県別掲載（2025年度）',
    'Apple App Store Small Business Program（手数料15%）、App Review Guidelines 1.4.1・2.3.7・3.1.1・5.1.1(ix)・5.1.3',
    'Firebase 料金ページ（2026年11月に検索）、TimeTree App Store 掲載（月300円）、ソフトバンク みまもりサービス（月1,078円）',
  ].map((t, j, a) => ({ text: t, options: { bullet: true, breakLine: j < a.length - 1 } })),
  { x: 0.6, y: 1.45, w: 12.1, h: 5.0, fontSize: 13, color: C.text1, valign: 'top', paraSpaceAfter: 6, isTextBox: true, margin: 0 });

  await pres.writeFile({ fileName: 'minnanokyou_monetization_plan.pptx' });
  await applyTheme('minnanokyou_monetization_plan.pptx', THEME);
  console.log('written');
})();
