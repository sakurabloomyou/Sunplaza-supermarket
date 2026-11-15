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

  const hdr = (t) => ({ text: t, options: { bold: true, color: C.background1, fill: { color: C.accent1 } } });
  const tblBorder = { type: 'solid', pt: 0.75, color: 'D5DDD9' };
  const bullets = (items) => items.map((t, j) => ({ text: t, options: { bullet: true, breakLine: j < items.length - 1 } }));
  const card = (s, x, y, w, h, fill, name) => s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w, h, rectRadius: 0.12, fill: { color: fill }, line: { type: 'none' }, objectName: name });
  const tx = (s, t, o) => s.addText(t, { isTextBox: true, margin: 0, color: C.text1, valign: 'top', ...o });

  // ===== 1. 表紙 =====
  pres.addSection({ title: 'はじめに' });
  let s = pres.addSlide({ masterName: 'TITLE_DARK', sectionTitle: 'はじめに' });
  s.addImage({ data: ic.sun, x: 0.8, y: 1.0, w: 0.9, h: 0.9, objectName: 'sunrise icon', altText: '朝日のマーク' });
  s.addText('みんなのきょう\n収益化の道筋（提案）', { placeholder: 'title' });
  s.addText('無料の実証から、企業の福利厚生として収入を得るまで。2026年11月　制作チーム', { placeholder: 'body' });
  s.addNotes('結論は「見守りに必要な機能はずっと無料。収入は企業の福利厚生（社員の仕事と介護の両立支援）から得る」です。金額はすべて仮定で、Phase 0〜1 で確かめます。');

  // ===== 2. 結論 =====
  s = content('はじめに', '結論：収入は企業の「介護両立支援」から得る');
  tx(s, '毎日の見守りに必要な機能はずっと無料。お金は、社員の介護を支えたい企業からいただく', { x: 0.6, y: 1.35, w: 12.1, h: 0.6, fontSize: 18, color: C.accent1, bold: true });
  [
    ['Phase 0（〜2027年2月）', 'まず実証', '無料のWeb版を5〜10家庭で4週間。続くか・負担が減るかを測る', ic.check],
    ['Phase 1（2027年3〜8月）', '企業で試す', '知り合いの企業1〜2社で試験導入。導入事例をつくる', ic.building],
    ['Phase 2（2027年9月〜）', '企業に広げる', '従業員50〜300人の企業を中心に10社。iPhoneアプリも公開', ic.chart],
  ].forEach(([p, h, b, icn], i) => {
    const x = 0.6 + i * 4.1;
    card(s, x, 2.25, 3.8, 3.9, C.background2, `summary card ${i + 1}`);
    circleIcon(s, icn, x + 0.3, 2.5, 0.8, C.accent1, `summary ${i + 1}`);
    tx(s, p, { x: x + 0.3, y: 3.45, w: 3.2, h: 0.35, fontSize: 12, color: C.accent2, bold: true });
    tx(s, h, { x: x + 0.3, y: 3.8, w: 3.2, h: 0.5, fontSize: 22, bold: true });
    tx(s, b, { x: x + 0.3, y: 4.4, w: 3.2, h: 1.6, fontSize: 14 });
  });
  note(s, '現在地：無料のWeb版は公開済み（家族共有・招待コード・説明書）。iPhoneアプリはコード一式あり。金額・時期はすべて提案段階の仮定です。');

  // ===== 3. 社会課題と市場 =====
  pres.addSection({ title: '課題と市場' });
  s = content('課題と市場', 'なぜ今か：認知症の家族を、働きながら支える人が増える');
  [['471.6万人', '高齢者の認知症\n（2025年推計）'], ['318万人', '働きながら介護する人\n（2030年見込み）'], ['約9.1兆円', '両立が難しいことによる\n経済損失（2030年試算）'], ['10.6万人', '介護を理由に仕事を\n辞めた人（2022年）']].forEach(([n, l], i) => {
    const x = 0.6 + (i % 2) * 2.95, y = 1.45 + Math.floor(i / 2) * 2.45;
    card(s, x, y, 2.75, 2.25, i === 0 ? C.background2 : C.accent6, `stat ${i + 1}`);
    tx(s, n, { x: x + 0.2, y: y + 0.25, w: 2.4, h: 0.8, fontSize: 30, bold: true, color: i === 0 ? C.accent1 : C.accent2 });
    tx(s, l, { x: x + 0.2, y: y + 1.15, w: 2.4, h: 0.9, fontSize: 13 });
  });
  tx(s, 'アプリが解決すること', { x: 6.75, y: 1.45, w: 5.95, h: 0.45, fontSize: 18, bold: true, color: C.accent1 });
  s.addTable([
    [hdr('家族の困りごと'), hdr('アプリでの解決')],
    ['先の見通しが持てない（1位 44.7%）', '今日のボードで予定・済みが一目で分かる'],
    ['離れた親のご飯・薬が心配', '「済み」を記録し、家族全員にすぐ届く'],
    ['同じことを何度も聞かれる', 'ご本人の画面に「いま」「つぎ」を大きく表示'],
    ['介護が一人に偏る', '分担表で役割を分け合える'],
  ], { x: 6.75, y: 2.0, w: 5.95, colW: [2.75, 3.2], fontSize: 12, color: C.text1, valign: 'middle', border: tblBorder, rowH: [0.4, 0.75, 0.75, 0.75, 0.75], objectName: 'issue table' });
  note(s, '出典：厚生労働省研究班（2024年公表）、経済産業省（2023年3月）、総務省 就業構造基本調査（2022年）、ニッセイ基礎研究所（2019年7月）。効果はPhase 0で確かめる。診断・治療・予防はしない。');

  // ===== 4. だれが払うか =====
  s = content('課題と市場', 'だれが払うか：最初は企業。法律と国の評価が後押しする');
  s.addTable([
    [hdr('払う人'), hdr('収入までの早さ'), hdr('理由')],
    [{ text: '企業（福利厚生）', options: { bold: true, color: C.accent1 } }, { text: '早い', options: { bold: true, color: C.accent1 } }, '2025年4月から、介護の個別周知・意向確認、40歳頃の情報提供などが事業主の義務に'],
    ['個人・家族', '遅い', 'App Store公開が先。安全に関わる機能は有料にできない'],
    ['自治体', '遅い', '予算は年度単位。実績が先に必要（認知症基本法 2024年1月施行）'],
    ['介護事業所', '中くらい', '国の導入補助はあるが、対象になるかは確認が必要'],
  ], { x: 0.6, y: 1.45, w: 7.4, colW: [1.9, 1.5, 4.0], fontSize: 13, color: C.text1, valign: 'middle', border: tblBorder, rowH: [0.42, 0.95, 0.85, 0.85, 0.85], objectName: 'payer table' });
  card(s, 8.35, 1.45, 4.35, 4.0, C.background2, 'tailwind card');
  tx(s, '企業を後押しするもの', { x: 8.65, y: 1.65, w: 3.8, h: 0.45, fontSize: 18, bold: true, color: C.accent1 });
  tx(s, bullets(['育児・介護休業法の改正（2025年4月）で、介護の両立支援が事業主の義務に', '健康経営優良法人の2026年度の改訂で、育児・介護との両立支援が主な改訂ポイントに', '国が経営者向けガイドラインを公表（経済産業省、2024年3月）']),
    { x: 8.65, y: 2.2, w: 3.85, h: 3.1, fontSize: 13, paraSpaceAfter: 8 });
  note(s, '出典：厚生労働省「育児・介護休業法 改正のポイント」、経済産業省「健康経営優良法人2026 認定要件の改訂」関連資料、同「仕事と介護の両立支援に関する経営者向けガイドライン」（2024年3月26日）。');

  // ===== 5. ターゲット =====
  pres.addSection({ title: '企業向け戦略' });
  s = content('企業向け戦略', 'ターゲット：従業員50〜300人の企業から');
  card(s, 0.6, 1.45, 5.9, 4.9, C.background2, 'size card');
  circleIcon(s, ic.building, 0.9, 1.7, 0.75, C.accent1, 'size');
  tx(s, '規模：50〜300人', { x: 1.85, y: 1.75, w: 4.5, h: 0.65, fontSize: 22, bold: true, valign: 'middle' });
  tx(s, bullets(['法改正の義務は企業の規模に関係なくかかる', '人事・総務が少人数で、研修や相談窓口を自前で用意しにくい', '社長・人事に直接会いやすく、決めるのが早い', '介護の両立支援の助成金（中小企業向け）を使う企業と相性がよい', '大企業は Phase 3 以降（調達が長く、実績が必要）']),
    { x: 0.9, y: 2.65, w: 5.4, h: 3.6, fontSize: 14, paraSpaceAfter: 6 });
  tx(s, '業種：選ぶ基準と例（仮説）', { x: 6.9, y: 1.45, w: 5.8, h: 0.5, fontSize: 20, bold: true });
  [['40〜50代の社員が多い', '親の介護が始まる年代'], ['勤務中に私用の電話をしにくい', '「済み」の共有で確認の電話が要らない'], ['地域に根ざし、転勤が少ない', '親の近くで働く社員が多い']].forEach(([h, b], i) => {
    const y = 2.05 + i * 0.95;
    s.addShape(pres.shapes.OVAL, { x: 6.9, y: y + 0.08, w: 0.45, h: 0.45, fill: { color: C.accent1 }, line: { type: 'none' }, objectName: `criterion ${i + 1}` });
    tx(s, String(i + 1), { x: 6.9, y: y + 0.08, w: 0.45, h: 0.45, fontSize: 14, bold: true, color: C.background1, align: 'center', valign: 'middle' });
    tx(s, h, { x: 7.55, y, w: 5.15, h: 0.4, fontSize: 15, bold: true });
    tx(s, b, { x: 7.55, y: y + 0.42, w: 5.15, h: 0.4, fontSize: 13, color: C.accent5 });
  });
  card(s, 6.9, 5.0, 5.8, 1.35, C.accent6, 'industry examples');
  tx(s, '当てはまりそうな業種の例：製造業、物流、小売・スーパー、地域の金融機関、病院・介護事業所（職員も家族の介護者に）', { x: 7.1, y: 5.12, w: 5.4, h: 1.1, fontSize: 13, color: C.accent2, bold: true, valign: 'middle' });
  note(s, '業種別の介護者の割合は全国データを確認できていないため、業種は仮説。Phase 1 の試験導入先でこの基準が当てはまるかを確かめる。');

  // ===== 6. 勝算 =====
  s = content('企業向け戦略', '勝算：需要は強い。勝ち筋は「人ではなく毎日の道具」');
  const swot = [
    ['需要がある', C.background2, C.accent1, ['介護の両立支援が企業の義務になった（2025年4月）', '働きながら介護する人は2030年に318万人の見込み']],
    ['ほかと違う点', C.background2, C.accent1, ['既存の企業向けサービスは相談・研修が中心（例：月額5,000円から）', 'こちらは家族が毎日使う道具。相談・研修と併用できる', '家族の健康情報を会社に渡さない']],
    ['弱み', C.accent6, C.accent2, ['導入実績と利用データがまだない', '営業の担当者がいない', 'Web版は閉じているとお知らせが届かない']],
    ['勝つための条件', C.accent6, C.accent2, ['Phase 0 で「続く・負担が減る」を数字で示す', 'Phase 1 で導入事例を1社つくる', '社労士など、企業に信頼されている人と組む']],
  ];
  swot.forEach(([h, fill, hc, items], i) => {
    const x = 0.6 + (i % 2) * 6.15, y = 1.45 + Math.floor(i / 2) * 2.5;
    card(s, x, y, 5.95, 2.3, fill, `win card ${i + 1}`);
    tx(s, h, { x: x + 0.3, y: y + 0.2, w: 5.35, h: 0.4, fontSize: 17, bold: true, color: hc });
    tx(s, bullets(items), { x: x + 0.3, y: y + 0.7, w: 5.4, h: 1.5, fontSize: 13, paraSpaceAfter: 4 });
  });
  note(s, '勝算は条件付き。既存サービスの料金例：一般社団法人 両立支援協会（月額5,000円から、PR TIMES）。導入実績ができるまでは確実とは言えない。');

  // ===== 7. PR =====
  s = content('企業向け戦略', 'PRと販売：信頼されている人を通じて、事例で広げる');
  card(s, 0.6, 1.45, 12.1, 1.0, C.accent1, 'message band');
  tx(s, '伝えること：「社員の親の“きょう”を、職場から見守れる。家族の情報は会社に渡りません」', { x: 0.9, y: 1.45, w: 11.5, h: 1.0, fontSize: 18, bold: true, color: C.background1, valign: 'middle' });
  [
    ['1', '知り合いの企業', '人事・総務に直接提案。30日の無料試用', 'Phase 1'],
    ['2', '社労士と組む', '介護の両立支援や助成金を相談される社労士から紹介', 'Phase 1〜2'],
    ['3', '地域の場で話す', '商工会議所・業界団体の「仕事と介護」セミナーで登壇', 'Phase 2'],
    ['4', '事例を発信', '導入事例とPhase 0の結果をプレスリリース・SNSで', 'Phase 2'],
  ].forEach(([n, h, b, ph], i) => {
    const x = 0.6 + i * 3.08;
    card(s, x, 2.75, 2.85, 2.9, C.background2, `channel ${n}`);
    s.addShape(pres.shapes.OVAL, { x: x + 0.25, y: 2.95, w: 0.55, h: 0.55, fill: { color: C.accent2 }, line: { type: 'none' }, objectName: `channel number ${n}` });
    tx(s, n, { x: x + 0.25, y: 2.95, w: 0.55, h: 0.55, fontSize: 16, bold: true, color: C.background1, align: 'center', valign: 'middle' });
    tx(s, ph, { x: x + 0.95, y: 3.05, w: 1.8, h: 0.35, fontSize: 12, bold: true, color: C.accent2 });
    tx(s, h, { x: x + 0.25, y: 3.7, w: 2.4, h: 0.45, fontSize: 17, bold: true });
    tx(s, b, { x: x + 0.25, y: 4.25, w: 2.4, h: 1.3, fontSize: 14 });
  });
  card(s, 0.6, 5.85, 12.1, 0.55, C.accent6, 'materials band');
  tx(s, '用意するもの：1枚の紹介資料／30日の無料試用／導入事例（福利厚生代行サービスへの掲載は実績ができてから）', { x: 0.85, y: 5.85, w: 11.7, h: 0.55, fontSize: 13, bold: true, color: C.accent2, valign: 'middle' });

  // ===== 8. 道筋と収入 =====
  pres.addSection({ title: '実行' });
  s = content('実行', '道筋と収入の見込み（仮定の試算）');
  s.addChart(pres.charts.BAR, [
    { name: '企業', labels: ['Phase 0', 'Phase 1', 'Phase 2'], values: [0, 20000, 100000] },
    { name: '個人（手数料15%差引後）', labels: ['Phase 0', 'Phase 1', 'Phase 2'], values: [0, 0, 40800] },
  ], { x: 0.6, y: 1.4, w: 6.3, h: 5.0, barDir: 'col', barGrouping: 'stacked',
    chartColors: [HEX.accent1, HEX.accent3], showValue: true, dataLabelPosition: 'ctr', dataLabelFormatCode: '#,##0', dataLabelFontSize: 11, dataLabelColor: 'FFFFFF',
    showLegend: true, legendPos: 'b', legendFontSize: 12, legendFontFace: '+mn-lt',
    catAxisLabelColor: HEX.accent5, valAxisLabelColor: HEX.accent5, catAxisLabelFontFace: '+mn-lt', valAxisLabelFontFace: '+mn-lt', dataLabelFontFace: '+mn-lt',
    valAxisLabelFormatCode: '#,##0', valGridLine: { color: 'E3E9E6', size: 0.5 }, catGridLine: { style: 'none' },
    showTitle: true, title: '月あたりの収入（円）', titleFontSize: 14, titleColor: HEX.dk1, titleFontFace: '+mn-lt', objectName: 'revenue chart' });
  s.addTable([
    [hdr('フェーズ'), hdr('やること'), hdr('収入（月・仮）')],
    ['0：〜2027年2月', '無料で5〜10家庭', '0円'],
    ['1：2027年3〜8月', '企業2社で試験導入', '2万円'],
    ['2：2027年9月〜', '企業10社＋iPhone版で個人100家庭', { text: '約14万円', options: { bold: true, color: C.accent1 } }],
    ['3：2028年3月〜', '自治体・介護事業所', '未定'],
  ], { x: 7.2, y: 1.45, w: 5.5, colW: [2.0, 2.3, 1.2], fontSize: 12, color: C.text1, valign: 'middle', border: tblBorder, rowH: [0.4, 0.62, 0.62, 0.8, 0.62], objectName: 'phase table' });
  tx(s, bullets(['企業：1社 月1万円（仮。従業員300人まで）', '個人：月480円（仮）。Apple の手数料15%を差し引き', '料金は Phase 1 の聞き取りで決める']),
    { x: 7.2, y: 4.75, w: 5.5, h: 1.6, fontSize: 13, paraSpaceAfter: 4 });
  note(s, '企業の料金は、相談・研修型サービスの例（月額5,000円から）を参考にした仮の値。App Store の手数料は Small Business Program 参加時15%（Apple）。');

  // ===== 9. 費用とリスク =====
  s = content('実行', '費用とリスク');
  s.addTable([
    [hdr('費用'), hdr('金額'), hdr('時期')],
    ['Firebase（無料プラン）', '0円（1日の上限あり）', 'Phase 0〜'],
    ['閉じていても届くお知らせ', '従量課金。要試算', 'Phase 1'],
    ['Apple Developer Program', '年99米ドル', 'Phase 2'],
    ['法務・商標', '見積もりが必要', 'Phase 1'],
  ], { x: 0.6, y: 1.45, w: 5.6, colW: [2.4, 2.1, 1.1], fontSize: 12, color: C.text1, valign: 'middle', border: tblBorder, rowH: [0.4, 0.62, 0.62, 0.62, 0.62], objectName: 'cost table' });
  s.addTable([
    [hdr('リスク'), hdr('対策')],
    ['医療機器とみなされる', '「予防」「改善」と書かない。不安があれば厚労省・PMDAに相談'],
    ['家族の健康情報の扱い', '会社には個人が分からない利用状況だけを渡す。同意の取り方を法務と決める'],
    ['企業が払う形が App Store の決まりに合わない', '法務と Apple に事前に確認'],
    ['導入実績がなく売れない', 'Phase 0 の数字と Phase 1 の事例を先につくる'],
  ], { x: 6.5, y: 1.45, w: 6.2, colW: [2.3, 3.9], fontSize: 12, color: C.text1, valign: 'middle', border: tblBorder, rowH: [0.4, 0.78, 0.78, 0.78, 0.78], objectName: 'risk table' });
  card(s, 0.6, 4.65, 5.6, 1.6, C.background2, 'free principle');
  tx(s, 'ずっと無料にするもの', { x: 0.85, y: 4.8, w: 5.1, h: 0.4, fontSize: 15, bold: true, color: C.accent1 });
  tx(s, '今日のボード、ごはん・おくすりの「済み」、お迎え、お知らせ、ご本人の画面。広告は入れない', { x: 0.85, y: 5.25, w: 5.1, h: 0.9, fontSize: 13 });
  note(s, '広告を入れない理由：健康に関わるデータの広告利用は App Review Guidelines 5.1.3 で禁止。ご本人の誤操作や信頼の低下も避ける。');

  // ===== 10. 決めてほしいこと =====
  s = pres.addSlide({ masterName: 'TITLE_DARK', sectionTitle: '実行' });
  s.addText('決めてほしいこと', { placeholder: 'title' });
  s.addText([
    { text: '1. Phase 0 の協力家庭（5〜10家庭）を集める担当と時期', options: { breakLine: true } },
    { text: '2. 試験導入をお願いする企業の候補（50〜300人、知り合いの人事・総務）', options: { breakLine: true } },
    { text: '3. 組む社労士の候補と、法務への相談の予算', options: { breakLine: true } },
    { text: '4. 「安全に関わる機能は無料・広告なし」の方針への合意', options: { breakLine: true } },
    { text: '次に進む目安：4週間後も6割の家庭が使っている／家族の満足度が5段階で4以上', options: { fontSize: 15, color: C.accent3, paraSpaceBefore: 14 } },
  ], { placeholder: 'body' });
  s.addNotes('出典一覧：厚生労働省研究班 2024年公表／経済産業省 2023年3月推計・2024年3月26日ガイドライン／総務省 就業構造基本調査 2022年／ニッセイ基礎研究所 2019年7月／厚生労働省 育児・介護休業法 改正のポイント（2025年4月1日施行）／認知症基本法 2024年1月1日施行／経済産業省 健康経営優良法人 認定要件（2026年度）／両立支援協会 PR TIMES（月額5,000円から）／Apple Small Business Program・App Review Guidelines／Firebase 料金ページ。次に進む目安の数字はチームで決める案。');

  await pres.writeFile({ fileName: 'minnanokyou_monetization_plan.pptx' });
  await applyTheme('minnanokyou_monetization_plan.pptx', THEME);
  console.log('written');
})();
