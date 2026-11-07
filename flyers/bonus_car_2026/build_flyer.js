// ボーナス×カーローン×団体扱自動車保険 PRチラシ（A4縦・片面）
// 生成: node build_flyer.js  → bonus_car_flyer.pptx
const pptxgen = require("pptxgenjs");
const React = require("react");
const ReactDOMServer = require("react-dom/server");
const sharp = require("sharp");
const fa = require("react-icons/fa");

const FONT = "BIZ UDPGothic";
const COL = {
  green: "0F4D36", green2: "1E6B4C", tint: "EEF5F0", red: "C8102E",
  redDark: "9E0B22", gold: "E3B23C", goldLight: "FFE7A3", ink: "1F2A24",
  gray: "5B6660", white: "FFFFFF", line: "CFDCD4",
};

async function icon(Comp, color, size = 256) {
  const svg = ReactDOMServer.renderToStaticMarkup(
    React.createElement(Comp, { color: "#" + color, size: String(size) }));
  const buf = await sharp(Buffer.from(svg)).png().toBuffer();
  return "image/png;base64," + buf.toString("base64");
}

(async () => {
  const pres = new pptxgen();
  pres.defineLayout({ name: "A4_PORTRAIT", width: 8.27, height: 11.69 });
  pres.layout = "A4_PORTRAIT";
  pres.theme = { headFontFace: FONT, bodyFontFace: FONT };
  pres.title = "ボーナスでクルマ買っちゃう？！ PRチラシ";

  const s = pres.addSlide();
  s.background = { color: COL.white };
  const W = 8.27, M = 0.4, CW = W - M * 2;
  const T = (text, o) => s.addText(text, { isTextBox: true, fontFace: FONT, margin: 0, ...o });

  // ===== ヘッダー（クリスマスグリーン） =====
  s.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: W, h: 3.45, fill: { color: COL.green }, line: { type: "none" }, objectName: "header_bg" });
  const snow = await icon(fa.FaSnowflake, COL.white);
  const star = await icon(fa.FaStar, COL.gold);
  [[6.9, 0.25, 0.55, 55], [7.55, 1.0, 0.32, 65], [5.55, 0.18, 0.28, 70], [0.12, 3.12, 0.25, 70],
   [7.65, 2.75, 0.45, 60], [3.6, 3.17, 0.2, 70], [3.55, 0.12, 0.2, 75]].forEach(([x, y, d, t], i) =>
    s.addImage({ data: snow, x, y, w: d, h: d, transparency: t, objectName: "deco_snow_" + i }));
  [[6.35, 1.05, 0.2], [7.25, 2.2, 0.16], [5.2, 0.62, 0.14]].forEach(([x, y, d], i) =>
    s.addImage({ data: star, x, y, w: d, h: d, objectName: "deco_star_" + i }));

  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: M, y: 0.38, w: 3.1, h: 0.42, rectRadius: 0.21, fill: { color: COL.red }, line: { type: "none" } });
  T("2026 冬のボーナス特別企画", { x: M, y: 0.38, w: 3.1, h: 0.42, fontSize: 14, bold: true, color: COL.white, align: "center", valign: "middle", objectName: "header_badge" });

  T("ボーナスで", { x: M, y: 0.98, w: 5.0, h: 0.75, fontSize: 40, bold: true, color: COL.white, valign: "middle", objectName: "title_line1" });
  T("クルマ買っちゃう？！", { x: M, y: 1.72, w: CW, h: 0.95, fontSize: 50, bold: true, color: COL.gold, valign: "middle", objectName: "title_line2" });
  T("クルマ選びと一緒に、ローンと保険もおトクにそろえませんか？", { x: M, y: 2.78, w: CW, h: 0.4, fontSize: 15, color: COL.white, valign: "middle", objectName: "header_lead" });

  // 車アイコン（赤い円）
  s.addShape(pres.shapes.OVAL, { x: 3.55, y: 0.93, w: 0.78, h: 0.78, fill: { color: COL.red }, line: { color: COL.gold, width: 2.5 } });
  s.addImage({ data: await icon(fa.FaCarSide, COL.white), x: 3.69, y: 1.07, w: 0.5, h: 0.5, objectName: "icon_car" });

  // ===== POINT 1 カーローン =====
  const y1 = 3.7, h1 = 2.95;
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: M, y: y1, w: CW, h: h1, rectRadius: 0.15, fill: { color: COL.tint }, line: { color: COL.line, width: 1 }, objectName: "card_loan" });
  s.addShape(pres.shapes.OVAL, { x: M + 0.25, y: y1 + 0.2, w: 0.5, h: 0.5, fill: { color: COL.red }, line: { type: "none" } });
  s.addImage({ data: await icon(fa.FaYenSign, COL.white), x: M + 0.37, y: y1 + 0.32, w: 0.26, h: 0.26 });
  T([{ text: "POINT 1　", options: { color: COL.red } }, { text: "おトクな固定金利のカーローン", options: { color: COL.green } }],
    { x: M + 0.9, y: y1 + 0.2, w: 6.2, h: 0.5, fontSize: 20, bold: true, valign: "middle", objectName: "loan_heading" });

  // 大きな金利
  T("固定金利", { x: M + 0.3, y: y1 + 0.9, w: 3.2, h: 0.35, fontSize: 16, bold: true, color: COL.green, objectName: "loan_rate_label" });
  T([{ text: "年", options: { fontSize: 26 } }, { text: "2.90", options: { fontSize: 66 } }, { text: "%", options: { fontSize: 32 } }],
    { x: M + 0.3, y: y1 + 1.2, w: 3.3, h: 1.0, bold: true, color: COL.red, valign: "bottom", objectName: "loan_rate_main" });

  // 適用条件ボックス
  const bx = M + 3.7, bw = CW - 3.7 - 0.3;
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: bx, y: y1 + 0.9, w: bw, h: 1.35, rectRadius: 0.1, fill: { color: COL.white }, line: { color: COL.red, width: 1.5 } });
  T("この金利の適用条件", { x: bx + 0.2, y: y1 + 1.0, w: bw - 0.4, h: 0.32, fontSize: 13, bold: true, color: COL.red, objectName: "loan_cond_label" });
  T([{ text: "現在ご契約の自動車保険の等級が" }, { text: "7等級以上", options: { color: COL.red, fontSize: 18 } }, { text: "の方" }],
    { x: bx + 0.2, y: y1 + 1.35, w: bw - 0.4, h: 0.8, fontSize: 14, bold: true, color: COL.ink, valign: "top", lineSpacingMultiple: 1.15, objectName: "loan_cond_text" });

  // 該当しない方
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: M + 0.3, y: y1 + 2.33, w: CW - 0.6, h: 0.4, rectRadius: 0.08, fill: { color: COL.white }, line: { type: "none" } });
  T([{ text: "上記条件に該当しない方　" }, { text: "固定金利 年3.10%", options: { bold: true, color: COL.green, fontSize: 15 } }],
    { x: M + 0.5, y: y1 + 2.33, w: CW - 1.0, h: 0.4, fontSize: 13, color: COL.ink, valign: "middle", objectName: "loan_rate_sub" });

  T([{ text: "※2026年10月1日〜2027年3月31日までの融資実行分に適用する金利です。", options: { breakLine: true } }, { text: "※ご利用には所定の審査があります。　取扱金融機関：〇〇〇〇〇" }],
    { x: M, y: y1 + h1 + 0.05, w: 5.7, h: 0.36, fontSize: 9, color: COL.gray, valign: "middle", objectName: "loan_note" });

  // ===== POINT 2 団体扱自動車保険 =====
  const y2 = 7.2, h2 = 3.0;
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: M, y: y2, w: CW, h: h2, rectRadius: 0.15, fill: { color: COL.tint }, line: { color: COL.line, width: 1 }, objectName: "card_insurance" });
  s.addShape(pres.shapes.OVAL, { x: M + 0.25, y: y2 + 0.2, w: 0.5, h: 0.5, fill: { color: COL.red }, line: { type: "none" } });
  s.addImage({ data: await icon(fa.FaShieldAlt, COL.white), x: M + 0.37, y: y2 + 0.32, w: 0.26, h: 0.26 });
  T([{ text: "POINT 2　", options: { color: COL.red } }, { text: "団体扱自動車保険がおトク", options: { color: COL.green } }],
    { x: M + 0.9, y: y2 + 0.2, w: 4.85, h: 0.5, fontSize: 19, bold: true, valign: "middle", objectName: "ins_heading" });

  // 30%OFF バッジ
  s.addShape(pres.shapes.OVAL, { x: 6.2, y: y2 - 0.2, w: 1.55, h: 1.55, fill: { color: COL.red }, line: { color: COL.gold, width: 3 }, objectName: "ins_badge" });
  T([{ text: "従業員割引", options: { fontSize: 12, breakLine: true } }, { text: "30%", options: { fontSize: 32, color: COL.goldLight, breakLine: true } }, { text: "OFF", options: { fontSize: 16 } }],
    { x: 6.2, y: y2 - 0.15, w: 1.55, h: 1.45, bold: true, color: COL.white, align: "center", valign: "middle", lineSpacingMultiple: 0.9, objectName: "ins_badge_text" });

  T("一般契約と比べて、こんなに安い！（年間保険料例）", { x: M + 0.3, y: y2 + 0.8, w: 5.4, h: 0.35, fontSize: 14, bold: true, color: COL.ink, objectName: "ins_lead" });

  const hd = (t, fill) => ({ text: t, options: { bold: true, color: COL.white, fill: { color: fill }, align: "center" } });
  const cell = (t, o = {}) => ({ text: t, options: { align: "center", color: COL.ink, fill: { color: COL.white }, ...o } });
  const rows = [
    [hd("保険料例", COL.green2), hd("一般契約", "6B7570"), hd("団体扱（当代理店）", COL.red), hd("年間差額", COL.green2)],
    [cell("例1：〇〇〇〇", { align: "left" }), cell("〇〇,〇〇〇円"), cell("〇〇,〇〇〇円", { bold: true, color: COL.red, fontSize: 14 }), cell("〇〇,〇〇〇円 おトク", { bold: true, color: COL.green })],
    [cell("例2：〇〇〇〇", { align: "left" }), cell("〇〇,〇〇〇円"), cell("〇〇,〇〇〇円", { bold: true, color: COL.red, fontSize: 14 }), cell("〇〇,〇〇〇円 おトク", { bold: true, color: COL.green })],
  ];
  s.addTable(rows, { x: M + 0.3, y: y2 + 1.22, w: CW - 0.6, colW: [1.55, 1.45, 1.8, 2.07], rowH: [0.36, 0.42, 0.42],
    fontFace: FONT, fontSize: 12, valign: "middle", margin: [0, 0.08, 0, 0.08], border: { type: "solid", pt: 0.75, color: COL.line }, objectName: "ins_table" });

  // メリットチップ
  const chips = [["保険料は給与天引き", fa.FaWallet], ["事故時も代理店がサポート", fa.FaHandsHelping], ["ご家族のクルマも相談OK", fa.FaUsers]];
  const cw = (CW - 0.6 - 0.2 * 2) / 3;
  for (let i = 0; i < chips.length; i++) {
    const cx = M + 0.3 + i * (cw + 0.2), cy = y2 + 2.57;
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: cx, y: cy, w: cw, h: 0.36, rectRadius: 0.18, fill: { color: COL.white }, line: { color: COL.green2, width: 1 } });
    s.addImage({ data: await icon(chips[i][1], COL.green2), x: cx + 0.12, y: cy + 0.08, w: 0.2, h: 0.2 });
    T(chips[i][0], { x: cx + 0.38, y: cy, w: cw - 0.45, h: 0.36, fontSize: 10.5, bold: true, color: COL.green, valign: "middle", objectName: "ins_chip_" + (i + 1) });
  }
  T("※保険料例の前提条件：〇〇〇〇〇（記入欄：年齢条件・ノンフリート等級・車種・補償内容・払込方法 等）",
    { x: M, y: y2 + h2 + 0.06, w: CW, h: 0.28, fontSize: 9, color: COL.gray, valign: "middle", objectName: "ins_note" });

  // ===== お問い合わせ =====
  const y3 = 10.56, h3 = 0.84;
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: M, y: y3, w: CW, h: h3, rectRadius: 0.12, fill: { color: COL.red }, line: { type: "none" }, objectName: "cta_bg" });
  s.addImage({ data: await icon(fa.FaGift, COL.gold), x: M + 0.2, y: y3 + 0.15, w: 0.55, h: 0.55 });
  T("ローンも保険も、まずは当代理店へご相談ください！", { x: M + 0.9, y: y3 + 0.06, w: 5.4, h: 0.36, fontSize: 15, bold: true, color: COL.white, valign: "middle", objectName: "cta_message" });
  T([{ text: "〇〇〇〇保険サービス株式会社　内線：〇〇〇〇", options: { breakLine: true } }, { text: "E-mail：〇〇〇〇@〇〇〇〇　受付：平日 9:00〜17:00" }],
    { x: M + 0.9, y: y3 + 0.44, w: 5.4, h: 0.34, fontSize: 10, color: COL.white, valign: "middle", objectName: "cta_contact" });
  s.addShape(pres.shapes.RECTANGLE, { x: W - M - 0.9, y: y3 + 0.07, w: 0.7, h: 0.7, fill: { color: COL.white }, line: { type: "none" }, objectName: "qr_placeholder" });
  T("QR", { x: W - M - 0.9, y: y3 + 0.07, w: 0.7, h: 0.7, fontSize: 12, bold: true, color: COL.gray, align: "center", valign: "middle", objectName: "qr_label" });

  T("引受保険会社：〇〇〇〇株式会社　取扱代理店：〇〇〇〇保険サービス株式会社　募集文書番号：〇〇〇〇-〇〇〇〇（2026年〇月作成）",
    { x: M, y: 11.44, w: CW, h: 0.2, fontSize: 8, color: COL.gray, valign: "middle", objectName: "legal_footer" });

  await pres.writeFile({ fileName: __dirname + "/bonus_car_flyer.pptx" });
  console.log("written");
})();
