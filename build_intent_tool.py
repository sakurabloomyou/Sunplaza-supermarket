"""
意向確認シート v5
・改正保険業法対応（比較推奨規制準拠）
・3社比較表を商品名・固有特約レベルに詳細化
・推奨根拠記録欄の追加
・お客様確認サイン欄追加
・特定リスク把握項目の追加（LP Step4 Q2相当）
・2026年6月施行の改正保険業法参照文言追加
"""
import openpyxl
from openpyxl.styles import PatternFill, Font, Alignment, Border, Side
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.worksheet.properties import WorksheetProperties, Outline
from openpyxl.utils import get_column_letter

wb = openpyxl.Workbook()
ws = wb.active
ws.title = "意向確認シート"

# ─── カラー定数 ───────────────────────────────────────────────
NAVY      = "1C3557"
DARK_NAVY = "16304F"
RED       = "C0392B"
DARK_RED  = "9B2335"
BLUE      = "1B5EB5"
DARK_BLUE = "2146A0"
GREEN     = "2E7D5B"
DARK_GRN  = "1E6644"
L_BLUE    = "DCE8F9"
L_GRN     = "E0F0E8"
L_RED     = "FDECEA"
BG        = "F2F5F1"
WHITE     = "FFFFFF"
YELLOW    = "FFFDE7"
L_YELLOW  = "FFF8E1"
GRAY1     = "EAECE9"
GRAY2     = "BFC5BB"
DARK      = "404B3A"
ORANGE    = "E67E22"
L_ORANGE  = "FEF0E3"

# ─── ヘルパー ─────────────────────────────────────────────────
def F(c): return PatternFill("solid", fgColor=c)
def Fn(c=None, bold=False, sz=10, name="Meiryo UI"):
    return Font(name=name, bold=bold, size=sz, color=c or "000000")
def Al(h="left", v="center", wrap=True, indent=0):
    return Alignment(horizontal=h, vertical=v, wrap_text=wrap, indent=indent)
def Bd(color=GRAY2, style="thin"):
    s = Side(style=style, color=color)
    return Border(top=s, bottom=s, left=s, right=s)

def ms(ws, rng, text, bg, fg=WHITE, bold=True, sz=10,
        h="left", v="center", wrap=True, indent=0):
    ws.merge_cells(rng)
    c = ws[rng.split(":")[0]]
    c.value = text
    c.fill  = F(bg)
    c.font  = Fn(fg, bold, sz)
    c.alignment = Al(h, v, wrap, indent)

def frame(ws, r1, r2, c1, c2, outer="7A8575", inner=GRAY2):
    so = Side(style="medium", color=outer)
    si = Side(style="thin",   color=inner)
    for r in range(r1, r2 + 1):
        for c in range(c1, c2 + 1):
            ws.cell(r, c).border = Border(
                top    = so if r == r1 else si,
                bottom = so if r == r2 else si,
                left   = so if c == c1 else si,
                right  = so if c == c2 else si,
            )

def input_cell(ws, ref, dv=None, color=GREEN):
    c = ws[ref]
    c.fill   = F(YELLOW)
    c.font   = Fn(NAVY, True, 11)
    c.alignment = Al("center", "center", False)
    c.border = Border(
        top=Side(style="medium", color=color),
        bottom=Side(style="medium", color=color),
        left=Side(style="medium", color=color),
        right=Side(style="medium", color=color),
    )

# ─── 列幅・シート背景 ─────────────────────────────────────────
for col, w in [("A",2.5),("B",3),("C",9),("D",44),
               ("E",18),("F",20),("G",20),("H",18)]:
    ws.column_dimensions[col].width = w

for r in range(1, 200):
    ws.row_dimensions[r].height = 16
    for c in range(1, 9):
        ws.cell(r, c).fill = F(BG)

ws.sheet_properties = WorksheetProperties()
ws.sheet_properties.outlinePr = Outline(summaryBelow=False, summaryRight=False)

# ════════════════════════════════════════════════════════════════
#  ヘッダー
# ════════════════════════════════════════════════════════════════
ws.row_dimensions[1].height = 36
ms(ws, "A1:H1",
   "  ■ 自動車保険　意向確認シート（トークスクリプト型）　改正保険業法対応版",
   NAVY, WHITE, True, 13)

ws.row_dimensions[2].height = 18
ms(ws, "A2:H2",
   "  ※ 太字部分はお客様へ読み上げます。黄色セルを入力・選択し、"
   "STEP2は選択後に左端の ＋ ボタンで該当グループを展開してください。"
   "【2026年6月施行 改正保険業法（比較推奨規制）対応】",
   DARK_NAVY, "C8D8F0", False, 8)

# 基本情報
ws.row_dimensions[3].height = 5
ws.row_dimensions[4].height = 20
ws.row_dimensions[5].height = 22
ws.row_dimensions[6].height = 5

for i, lbl in enumerate(["日　付", "担当者名", "お客様名", "支　店"]):
    ws.cell(4, 3+i).value = lbl
    ws.cell(4, 3+i).fill  = F(NAVY)
    ws.cell(4, 3+i).font  = Fn(WHITE, True, 8)
    ws.cell(4, 3+i).alignment = Al("center")
    ws.cell(5, 3+i).fill  = F(YELLOW)
    ws.cell(5, 5+i-2 if i else 5, 3).alignment = Al("center")
    ws.cell(5, 3+i).alignment = Al("center")
    ws.cell(5, 3+i).border = Bd(GRAY2)

# ════════════════════════════════════════════════════════════════
#  STEP 1　行7〜14
# ════════════════════════════════════════════════════════════════
ws.row_dimensions[7].height  = 22
ws.row_dimensions[8].height  = 55
ws.row_dimensions[9].height  = 70
ws.row_dimensions[10].height = 26
ws.row_dimensions[11].height = 20
ws.row_dimensions[12].height = 20
ws.row_dimensions[13].height = 20
ws.row_dimensions[14].height = 5

ms(ws, "B7:H7", "  STEP 1　　はじめに・契約方法の確認", BLUE, WHITE, True, 11)

ms(ws, "B8:C8", "📣 読み上げ①\n（開始前）", DARK_BLUE, "C5D8F5", True, 8, "center")
opening = (
    "「本日は自動車保険のご案内をいたします。当社は複数の保険会社の商品を取り扱っており、"
    "お客様のご意向・ご状況に合った保険をご提案するために、まずいくつかお伺いします。\n"
    "ご確認いただいた内容は意向確認の記録として残させていただきます。よろしいですか？」\n"
    "※保険業法第294条の3（情報提供義務）および2026年6月施行の改正保険業法施行規則第227条の2に基づき実施"
)
ms(ws, "D8:H8", opening, L_BLUE, NAVY, True, 10, "left", "center", True, 1)

ms(ws, "B9:C9", "📣 読み上げ②\n（契約方法）", DARK_BLUE, "C5D8F5", True, 8, "center")
script1 = (
    "「当社では●社の自動車保険を扱っています。"
    "そのうち 給与天引き（団体割引）が使えるのは 損保ジャパン・三井住友海上・東京海上 の3社です。\n"
    "通販型のソニー損保 へのお取り次ぎも可能で、クレジットカード払いや口座振替の一般契約もご案内できます。\n\n"
    "どのご契約方法をご希望ですか？」"
)
ms(ws, "D9:H9", script1, "EBF2FC", NAVY, True, 10, "left", "center", True, 1)

ms(ws, "B10:F10",
   "  ▶ お客様のご希望の契約方法（右の黄色セルで選択してください）",
   L_YELLOW, RED, True, 9, "left")
ws["G10"].value = "契約方法 →"
ws["G10"].fill  = F(RED)
ws["G10"].font  = Fn(WHITE, True, 8)
ws["G10"].alignment = Al("center", "center", False)

input_cell(ws, "H10", color=RED)

dv1 = DataValidation(
    type="list",
    formula1='"①給与天引き（団体割引）,②一般契約（クレカ・口振）,③通販型（ソニー損保）"',
    allow_blank=True, showDropDown=False
)
dv1.sqref = "H10"
ws.add_data_validation(dv1)

choices = [
    (11, "①", "給与天引き（団体割引）",  "→ 下のグループ「①②」を展開", GREEN, L_GRN),
    (12, "②", "一般契約（クレカ・口振）","→ 下のグループ「①②」を展開", BLUE,  L_BLUE),
    (13, "③", "通販型（ソニー損保）",    "→ 下のグループ「③」を展開",  RED,   L_RED),
]
for row, num, label, guide, hc, bc in choices:
    ws.cell(row, 2).value = num
    ws.cell(row, 2).fill  = F(hc)
    ws.cell(row, 2).font  = Fn(WHITE, True, 9)
    ws.cell(row, 2).alignment = Al("center")
    ws.cell(row, 3).value = label
    ws.cell(row, 3).fill  = F(bc)
    ws.cell(row, 3).font  = Fn(hc, True, 9)
    ws.cell(row, 3).alignment = Al("left")
    ws.merge_cells(f"D{row}:H{row}")
    ws.cell(row, 4).value = guide
    ws.cell(row, 4).fill  = F(bc)
    ws.cell(row, 4).font  = Fn(DARK, False, 8)
    ws.cell(row, 4).alignment = Al("left")

frame(ws, 7, 13, 2, 8)

ws.row_dimensions[15].height = 24
ms(ws, "B15:E15",
   "  ▼  ①② 給与天引き・一般契約 ─── 下のグループ ＋ で展開",
   L_GRN, GREEN, True, 9)
ms(ws, "F15:H15",
   "  ▼  ③ 通販型 ─── 下のグループ ＋ で展開",
   L_RED, RED, True, 9)

# ════════════════════════════════════════════════════════════════
#  STEP 2（①②）行16〜52 ← グループ折りたたみ
#  16-24: 意向把握
#  25-29: 補償確認
#  30-36: 特定リスク把握（NEW）
#  37-46: 3社比較＋推奨根拠（NEW詳細化）
#  47-49: お客様確認サイン（NEW）
# ════════════════════════════════════════════════════════════════
ws.row_dimensions[16].height = 22
ws.row_dimensions[17].height = 18
ws.row_dimensions[18].height = 55
ws.row_dimensions[19].height = 18
for r in range(20, 25):
    ws.row_dimensions[r].height = 20
ws.row_dimensions[25].height = 5
ws.row_dimensions[26].height = 20
for r in range(27, 30):
    ws.row_dimensions[r].height = 20
ws.row_dimensions[30].height = 5

ms(ws, "B16:H16",
   "  STEP 2　　意向確認（重視事項・補償内容・リスク把握）　給与天引き・一般契約の方",
   GREEN, WHITE, True, 11)

ms(ws, "B17:C17", "📋 スクリプト", DARK_GRN, "B8DEC9", True, 8, "center")
ms(ws, "D17:H17", "", DARK_GRN, "B8DEC9", False, 8)

script2a = (
    "「自動車保険でいちばん大切にしていることを教えていただけますか？"
    "いくつかお伺いしてもよいでしょうか？\n"
    "当てはまるものに○をつけてください。（複数回答可）」"
)
ms(ws, "D18:H18", script2a, "EDF7F2", NAVY, True, 10, "left", "center", True, 1)
ms(ws, "B18:C18", "📣 読み上げ", L_GRN, GREEN, True, 8, "center")

ms(ws, "B19:C19", "重視事項\n（複数可）", DARK_GRN, "B8DEC9", True, 8, "center")
ms(ws, "D19:F19", "お客様の重視事項",     DARK_GRN, "B8DEC9", True, 8, "center")
ms(ws, "G19:H19", "各社の強み（参考）",   DARK_GRN, "B8DEC9", True, 8, "center")

priority_items = [
    ("保険料をできるだけ抑えたい",          "損保ジャパン（多様なプラン）／三井住友海上（ネット割引）"),
    ("補償をしっかり充実させたい",          "東京海上（総合型・特約充実）／損保ジャパン（幅広い特約）"),
    ("事故時の対応・サポートを重視したい",  "三井住友海上（示談交渉◎）／東京海上（専任担当）"),
    ("手続きが簡単・わかりやすいものがいい","三井住友海上（シンプル設計・見積り速い）"),
    ("担当者に相談しながら決めたい",        "3社すべて対応可。担当者によるサポート"),
]
dv_prio = DataValidation(type="list", formula1='"○,−"',
                          allow_blank=True, showDropDown=False)
ws.add_data_validation(dv_prio)
prio_cells = []

for i, (item, note) in enumerate(priority_items):
    row = 20 + i
    ws.cell(row, 2).value = f"  {chr(9312+i)}"
    ws.cell(row, 2).fill  = F(GREEN)
    ws.cell(row, 2).font  = Fn(WHITE, True, 10)
    ws.cell(row, 2).alignment = Al("center")

    ws.merge_cells(f"C{row}:F{row}")
    ws.cell(row, 3).value = f"  {item}"
    ws.cell(row, 3).fill  = F(L_GRN)
    ws.cell(row, 3).font  = Fn(NAVY, False, 9)
    ws.cell(row, 3).alignment = Al("left")

    ws.merge_cells(f"G{row}:G{row}")
    ws.cell(row, 7).value = f"  {note}"
    ws.cell(row, 7).fill  = F("F8FFF9")
    ws.cell(row, 7).font  = Fn(DARK, False, 8)
    ws.cell(row, 7).alignment = Al("left")

    input_cell(ws, f"H{row}", color=GREEN)
    prio_cells.append(f"H{row}")

dv_prio.sqref = " ".join(prio_cells)

ms(ws, "B26:H26", "  補償内容の確認（意向把握の必須事項）",
   DARK_GRN, WHITE, True, 9)

coverage_items = [
    ("車両保険の加入希望",    '"ご希望あり,検討中,不要"',         "車両保険あり・なしで保険料が大きく変わります"),
    ("運転者の範囲",          '"本人のみ,家族限定,限定なし"',     "限定なしは保険料が高くなる場合があります"),
    ("年間走行距離の目安",    '"5,000km未満,〜10,000km,10,000km超"',"距離が多いほどリスクが高まる場合があります"),
]
for i, (label, formula, note) in enumerate(coverage_items):
    row = 27 + i
    ws.cell(row, 2).value = f"  {chr(9312+5+i)}"
    ws.cell(row, 2).fill  = F(DARK_GRN)
    ws.cell(row, 2).font  = Fn(WHITE, True, 9)
    ws.cell(row, 2).alignment = Al("center")

    ws.merge_cells(f"C{row}:E{row}")
    ws.cell(row, 3).value = f"  {label}"
    ws.cell(row, 3).fill  = F(L_GRN)
    ws.cell(row, 3).font  = Fn(NAVY, False, 9)
    ws.cell(row, 3).alignment = Al("left")

    ws.merge_cells(f"F{row}:G{row}")
    ws.cell(row, 6).value = f"  {note}"
    ws.cell(row, 6).fill  = F("F8FFF9")
    ws.cell(row, 6).font  = Fn(DARK, False, 8)
    ws.cell(row, 6).alignment = Al("left")

    input_cell(ws, f"H{row}", color=DARK_GRN)
    dv_cov = DataValidation(type="list", formula1=formula,
                             allow_blank=True, showDropDown=False)
    dv_cov.sqref = f"H{row}"
    ws.add_data_validation(dv_cov)

frame(ws, 16, 29, 2, 8)

# ── 特定リスク把握（行31〜36） ────────────────────────────────
ws.row_dimensions[31].height = 20
ws.row_dimensions[32].height = 18
for r in range(33, 37):
    ws.row_dimensions[r].height = 20
ws.row_dimensions[36].height = 5

ms(ws, "B31:H31",
   "  特定リスク把握　　気になるリスク・トラブルはありますか？（LP Step4対応・複数可）",
   ORANGE, WHITE, True, 9)

ms(ws, "B32:C32", "リスク\n把握",        "D35400", "FFE0C0", True, 8, "center")
ms(ws, "D32:F32", "リスク項目",           "D35400", "FFE0C0", True, 8, "center")
ms(ws, "G32:H32", "対応する補償・特約",   "D35400", "FFE0C0", True, 8, "center")

risk_items = [
    ("自転車・歩行者との事故",    "対人賠償保険（無制限推奨）／個人賠償責任特約"),
    ("故障・レッカー手配",        "ロードサービス（搬送距離・回数）を各社比較"),
    ("あおり運転・危険運転被害",  "弁護士費用特約（法的対応費用をカバー）"),
    ("当て逃げ・駐車場トラブル",  "車両保険（エコノミー型で当て逃げ補償）"),
]
dv_risk = DataValidation(type="list", formula1='"○ 気になる,− 特になし"',
                          allow_blank=True, showDropDown=False)
ws.add_data_validation(dv_risk)
risk_cells = []

for i, (risk, coverage) in enumerate(risk_items):
    row = 33 + i
    ws.cell(row, 2).value = f"  R{i+1}"
    ws.cell(row, 2).fill  = F(ORANGE)
    ws.cell(row, 2).font  = Fn(WHITE, True, 9)
    ws.cell(row, 2).alignment = Al("center")

    ws.merge_cells(f"C{row}:F{row}")
    ws.cell(row, 3).value = f"  {risk}"
    ws.cell(row, 3).fill  = F(L_ORANGE)
    ws.cell(row, 3).font  = Fn(NAVY, False, 9)
    ws.cell(row, 3).alignment = Al("left")

    ws.merge_cells(f"G{row}:G{row}")
    ws.cell(row, 7).value = f"  {coverage}"
    ws.cell(row, 7).fill  = F("FFF8F0")
    ws.cell(row, 7).font  = Fn(DARK, False, 8)
    ws.cell(row, 7).alignment = Al("left")

    input_cell(ws, f"H{row}", color=ORANGE)
    risk_cells.append(f"H{row}")

dv_risk.sqref = " ".join(risk_cells)
frame(ws, 31, 35, 2, 8)

# ── STEP2-2: 3社提案（行37〜46） ─────────────────────────────
ws.row_dimensions[37].height = 22
ws.row_dimensions[38].height = 18
ws.row_dimensions[39].height = 68
ws.row_dimensions[40].height = 18
for r in range(41, 45):
    ws.row_dimensions[r].height = 48
ws.row_dimensions[45].height = 20
ws.row_dimensions[46].height = 5

ms(ws, "B37:H37",
   "  STEP 2-2　　3社ご提案（意向確認結果をふまえて）",
   DARK_GRN, WHITE, True, 11)

script2a2 = (
    "「ありがとうございます。いただいたご意向をもとに、"
    "損保ジャパン・三井住友海上・東京海上の3社でお見積りをご用意します。\n"
    "─── 募集人ポイント（顧客の意向に基づく推奨根拠を説明してください）──────────────────\n"
    "・保険料重視 → 三井住友海上のシンプルプランが競争力あり。ネット割引も活用可\n"
    "・補償充実重視 → 東京海上の総合型、または損保ジャパンの幅広い特約構成\n"
    "・事故対応重視 → 三井住友海上の示談交渉サービス、東京海上の専任担当制度\n"
    "・手続き簡便重視 → 三井住友海上のシンプル設計はお客様にとって分かりやすい\n"
    "必ず3社のお見積りをお客様にご提示し、推奨理由をご説明ください。」"
)
ms(ws, "D38:H38", script2a2, "EDF7F2", NAVY, True, 9, "left", "center", True, 1)
ms(ws, "B38:C38", "📣 読み上げ\n+ ポイント", DARK_GRN, "B8DEC9", True, 8, "center")

ms(ws, "B39:C39", "会社・商品名",           DARK, GRAY1, True, 8, "center")
ms(ws, "D39:E39", "主な強み・固有特約",      DARK, GRAY1, True, 8, "center")
ms(ws, "F39:G39", "顧客への一言",            DARK, GRAY1, True, 8, "center")
ws.cell(39, 8).value = "提案"
ws.cell(39, 8).fill  = F(DARK)
ws.cell(39, 8).font  = Fn(GRAY1, True, 8)
ws.cell(39, 8).alignment = Al("center")

# 3社の詳細情報（商品名・固有特約レベル）
companies = [
    (
        RED,   L_RED,
        "損保ジャパン\n「THE クルマの保険」",
        "・つながるドラレコ（安全運転スコア割引 最大20%）\n"
        "・故障運搬時車両損害特約（最大30万円）\n"
        "・代車費用特約（30日型）",
        "取引歴が長く特約の選択肢が豊富。\nドラレコ割引で保険料を抑えたい方に。",
    ),
    (
        GREEN, L_GRN,
        "三井住友海上\n「GK クルマの保険」",
        "・プレミアムドラレコ（360°全方位・AI事故状況分析）\n"
        "・雹災緊急アラート（業界唯一）\n"
        "・LINE連携で手続き完結",
        "シンプル設計で手続き楽々。\n保険料重視・手続き簡便を求める方に。",
    ),
    (
        BLUE,  L_BLUE,
        "東京海上日動\n「トータルアシスト」",
        "・DAP（ドライブエージェントパーソナル）\n"
        "・入院時選べるアシスト特約（自動付帯）\n"
        "・エコノミー型（当て逃げ補償あり）",
        "業界最大手の手厚い補償。\n事故後サポート・補償充実を重視する方に。",
    ),
]
dv_prop = DataValidation(type="list",
    formula1='"◎提案する,○提案する,△保留,×見送り"',
    allow_blank=True, showDropDown=False)
ws.add_data_validation(dv_prop)
prop_cells = []

for i, (hc, bc, name, feat, tip) in enumerate(companies):
    row = 41 + i
    ws.merge_cells(f"B{row}:C{row}")
    ws.cell(row, 2).value = name
    ws.cell(row, 2).fill  = F(hc)
    ws.cell(row, 2).font  = Fn(WHITE, True, 9)
    ws.cell(row, 2).alignment = Al("center", "center", True)

    ws.merge_cells(f"D{row}:E{row}")
    ws.cell(row, 4).value = feat
    ws.cell(row, 4).fill  = F(bc)
    ws.cell(row, 4).font  = Fn(DARK, False, 8)
    ws.cell(row, 4).alignment = Al("left", "top", True, 1)

    ws.merge_cells(f"F{row}:G{row}")
    ws.cell(row, 6).value = tip
    ws.cell(row, 6).fill  = F(WHITE)
    ws.cell(row, 6).font  = Fn("2A3328", False, 8)
    ws.cell(row, 6).alignment = Al("left", "top", True)

    input_cell(ws, f"H{row}", color=hc)
    prop_cells.append(f"H{row}")

dv_prop.sqref = " ".join(prop_cells)

# 推奨根拠記録欄（行45）
ws.row_dimensions[45].height = 28
ms(ws, "B45:D45",
   "  📝 推奨根拠記録（比較推奨規制必須）",
   DARK_NAVY, WHITE, True, 9)
ms(ws, "E45:F45",
   "上記のご意向（           ）に照らし、",
   L_BLUE, NAVY, False, 9)
ws.cell(45, 7).value = "推奨会社 →"
ws.cell(45, 7).fill  = F(NAVY)
ws.cell(45, 7).font  = Fn(WHITE, True, 8)
ws.cell(45, 7).alignment = Al("center", "center", False)
ws["H45"].fill  = F(YELLOW)
ws["H45"].font  = Fn(NAVY, True, 10)
ws["H45"].alignment = Al("center", "center", False)
ws["H45"].border = Border(
    top=Side(style="medium", color=NAVY),
    bottom=Side(style="medium", color=NAVY),
    left=Side(style="medium", color=NAVY),
    right=Side(style="medium", color=NAVY),
)
dv_rec = DataValidation(type="list",
    formula1='"損保ジャパン,三井住友海上,東京海上日動,お客様選択"',
    allow_blank=True, showDropDown=False)
dv_rec.sqref = "H45"
ws.add_data_validation(dv_rec)

frame(ws, 37, 45, 2, 8)

# お客様確認サイン欄（行47〜49）
ws.row_dimensions[47].height = 24
ws.row_dimensions[48].height = 28
ws.row_dimensions[49].height = 5

ms(ws, "B47:H47",
   "  ✍ お客様確認サイン（比較推奨規制・同意記録）",
   DARK_NAVY, WHITE, True, 10)

ws.row_dimensions[48].height = 30
ms(ws, "B48:E48",
   "  「上記の比較内容・推奨根拠を確認しました。"
   "内容は私の意向と合致しています。」",
   L_BLUE, NAVY, False, 9)
ws.cell(48, 6).value = "確認日 →"
ws.cell(48, 6).fill  = F(DARK_NAVY)
ws.cell(48, 6).font  = Fn(WHITE, True, 8)
ws.cell(48, 6).alignment = Al("center", "center", False)
ws["G48"].fill  = F(YELLOW)
ws["G48"].font  = Fn(DARK, False, 9)
ws["G48"].alignment = Al("center", "center", False)
ws["G48"].border = Bd(DARK_NAVY, "medium")

ws.cell(48, 8).value = "サイン"
ws.cell(48, 8).fill  = F(YELLOW)
ws.cell(48, 8).font  = Fn(DARK, False, 9)
ws.cell(48, 8).alignment = Al("center", "center", False)
ws.cell(48, 8).border = Border(
    top=Side(style="medium", color=DARK_NAVY),
    bottom=Side(style="medium", color=DARK_NAVY),
    left=Side(style="medium", color=DARK_NAVY),
    right=Side(style="medium", color=DARK_NAVY),
)
frame(ws, 47, 48, 2, 8)

# ── STEP2 ①② グループ設定（16〜49） ─────────────────────────
for r in range(16, 50):
    ws.row_dimensions[r].outline_level = 1
    ws.row_dimensions[r].hidden = True

# ════════════════════════════════════════════════════════════════
#  STEP 2（③通販型）行51〜57 ← グループ折りたたみ
# ════════════════════════════════════════════════════════════════
ws.row_dimensions[51].height = 22
ws.row_dimensions[52].height = 18
ws.row_dimensions[53].height = 60
ws.row_dimensions[54].height = 60
ws.row_dimensions[55].height = 22
ws.row_dimensions[56].height = 20
ws.row_dimensions[57].height = 5

ms(ws, "B51:H51",
   "  STEP 2　　ソニー損保ご案内　　通販型をご希望の方",
   RED, WHITE, True, 11)

ms(ws, "B52:C52", "📋 スクリプト", DARK_RED, "F5C0BB", True, 8, "center")
ms(ws, "D52:H52", "",             DARK_RED, "F5C0BB", False, 8)

script_b1 = (
    "「それではソニー損保をご案内しますので、お客様のご状況を確認させてください。\n"
    "ソニー損保はインターネットでお客様ご自身に直接ご契約いただく通販型です。"
    "当社（代理店）が契約を代理するものではなく、申込内容・告知内容はお客様ご自身でご入力・ご確認いただきます。"
    "手続きはお客様側のご対応となりますが、よろしいでしょうか？」"
)
ms(ws, "D53:H53", script_b1, "FEF5F4", NAVY, True, 9, "left", "center", True, 1)
ms(ws, "B53:C53", "📣 読み上げ①", L_RED, RED, True, 8, "center")

script_b2 = (
    "「事故時のサポートはソニー損保のコールセンター対応が基本となり、"
    "当社担当者が直接サポートすることは難しくなります。\n"
    "ご契約後の変更・事故対応についてもソニー損保に直接ご連絡いただくことになります。\n"
    "この点をご了解いただいたうえでご希望ですか？」"
)
ms(ws, "D54:H54", script_b2, "FEF5F4", NAVY, True, 9, "left", "center", True, 1)
ms(ws, "B54:C54", "📣 読み上げ②\n（留意事項）", L_RED, RED, True, 8, "center")

ms(ws, "B55:C55", "✏️ お客様確認", DARK_RED, "F5C0BB", True, 8, "center")
ms(ws, "D55:E55", "通販型の特性（直接契約・コールセンター）を理解の上、ソニー損保を希望する",
   L_RED, DARK, False, 8)
ms(ws, "F55:G55", "← お客様の意向を選択",
   L_RED, DARK_RED, False, 8)

input_cell(ws, "H55", color=RED)
dv_b = DataValidation(type="list",
    formula1='"はい（取り次ぎ確定）,再検討（3社比較に戻る）,見送り"',
    allow_blank=True, showDropDown=False)
dv_b.sqref = "H55"
ws.add_data_validation(dv_b)

frame(ws, 51, 56, 2, 8)

# ── STEP2 ③ グループ設定（51〜57） ───────────────────────────
for r in range(51, 58):
    ws.row_dimensions[r].outline_level = 1
    ws.row_dimensions[r].hidden = True

# ════════════════════════════════════════════════════════════════
#  意向と最終契約の確認（常時表示）
# ════════════════════════════════════════════════════════════════
ws.row_dimensions[59].height = 22
ws.row_dimensions[60].height = 40
ws.row_dimensions[61].height = 5

ms(ws, "B59:H59",
   "  ■ 意向と最終選択の確認（契約前に必ず実施）",
   NAVY, WHITE, True, 10)

final_confirm = (
    "「本日ご提案した○○（会社名）の○○プランは、先ほどお伺いしたご意向（○○を重視）"
    "に沿ったものです。ご確認いただけますか？」\n"
    "→ 異なる商品をご選択の場合は、右の欄にその理由を記録してください。"
)
ms(ws, "D60:G60", final_confirm, L_BLUE, NAVY, False, 9, "left", "center", True, 1)
ms(ws, "B60:C60", "📣 確認・記録", NAVY, "93B8DC", True, 8, "center")
ws["H60"].fill  = F(YELLOW)
ws["H60"].font  = Fn(DARK, False, 9)
ws["H60"].alignment = Al("left", "top", True)
ws["H60"].border = Bd(NAVY, "medium")
frame(ws, 59, 60, 2, 8)

# ════════════════════════════════════════════════════════════════
#  メモ欄
# ════════════════════════════════════════════════════════════════
ws.row_dimensions[62].height = 20
ws.row_dimensions[63].height = 75
ws.row_dimensions[64].height = 5
ws.row_dimensions[65].height = 20
ws.row_dimensions[66].height = 30
ws.row_dimensions[67].height = 5

ms(ws, "B62:H62", "  📝 面談メモ・お客様の声", DARK, WHITE, True, 10)
ws.merge_cells("B63:H63")
ws["B63"].fill = F(YELLOW)
ws["B63"].alignment = Alignment(horizontal="left", vertical="top",
                                  wrap_text=True, indent=1)
ws["B63"].border = Border(
    top=Side(style="medium", color="7A8575"),
    bottom=Side(style="medium", color="7A8575"),
    left=Side(style="medium", color="7A8575"),
    right=Side(style="medium", color="7A8575"),
)
frame(ws, 62, 63, 2, 8)

ms(ws, "B65:H65", "  📌 次回アクション", DARK, WHITE, True, 10)
ws.merge_cells("B66:H66")
ws["B66"].fill = F(YELLOW)
ws["B66"].alignment = Alignment(horizontal="left", vertical="top",
                                  wrap_text=True, indent=1)
ws["B66"].border = Border(
    top=Side(style="medium", color="7A8575"),
    bottom=Side(style="medium", color="7A8575"),
    left=Side(style="medium", color="7A8575"),
    right=Side(style="medium", color="7A8575"),
)
frame(ws, 65, 66, 2, 8)

ws.row_dimensions[68].height = 18
ms(ws, "B68:H68",
   "  ＊本シートは2026年6月施行の改正保険業法（比較推奨規制、保険業法施行規則第227条の2）に基づく"
   "意向確認記録として活用してください。面談後は必ず保存・アーカイブをお願いします。",
   NAVY, "93B8DC", False, 7)

# ════════════════════════════════════════════════════════════════
#  Sheet 2: 比較推奨チェックリスト（改訂版）
# ════════════════════════════════════════════════════════════════
ws2 = wb.create_sheet("比較推奨チェックリスト")

for r in range(1, 70):
    ws2.row_dimensions[r].height = 16
    for c in range(1, 8):
        ws2.cell(r, c).fill = F("F5F7F4")

for col, w in [("A",3),("B",4),("C",44),("D",22),("E",10),("F",10),("G",10)]:
    ws2.column_dimensions[col].width = w

ws2.row_dimensions[1].height = 34
ws2.merge_cells("A1:G1")
ws2["A1"].value = "  ■ 比較推奨チェックリスト（改正保険業法対応・金融庁指針準拠）"
ws2["A1"].fill  = F(NAVY)
ws2["A1"].font  = Fn(WHITE, True, 13)
ws2["A1"].alignment = Al("left", "center")

ws2.row_dimensions[2].height = 18
ws2.merge_cells("A2:G2")
ws2["A2"].value = (
    "  面談後に全項目を確認し、すべて「✅ 済」になっていることを確認してください。"
    "【根拠：2026年6月施行 改正保険業法施行規則第227条の2】"
)
ws2["A2"].fill  = F(DARK_NAVY)
ws2["A2"].font  = Fn("C8D8F0", False, 8)
ws2["A2"].alignment = Al("left", "center")

ws2.row_dimensions[3].height = 18
ws2.merge_cells("C3:D3")
ws2.cell(3, 3).value = "  確認項目"
ws2.cell(3, 3).fill  = F(DARK)
ws2.cell(3, 3).font  = Fn(GRAY1, True, 8)
ws2.cell(3, 3).alignment = Al("left")
for i, lbl in enumerate(["SJ", "MSI", "TN"], start=5):
    ws2.cell(3, i).value = lbl
    ws2.cell(3, i).fill  = F(DARK)
    ws2.cell(3, i).font  = Fn(GRAY1, True, 8)
    ws2.cell(3, i).alignment = Al("center")

dv_c = DataValidation(type="list", formula1='"✅ 済,⬜ 未,N/A"',
                       allow_blank=True, showDropDown=False)
ws2.add_data_validation(dv_c)
c_cells = []

checklist = [
    ("① 事前確認（意向把握）", GREEN, [
        "お客様の意向（重視事項）を確認した",
        "補償内容の希望（車両保険・運転者範囲等）を確認した",
        "特定リスク把握（自転車事故・レッカー・あおり・当て逃げ）を確認した",
        "複数社（3社）の見積りを取得した",
        "各社の保険料・補償内容を比較説明した",
    ]),
    ("② 比較推奨の実施", DARK_GRN, [
        "お客様の意向に照らして比較対象3社を選定し、選定理由を説明できる",
        "各社の特徴・強みをお客様の意向と紐づけて説明した",
        "推奨・非推奨の根拠が顧客の意向に基づいていることを確認した",
        "商品名・固有特約レベルで3社の違いを説明した",
    ]),
    ("③ 推奨根拠の記録", BLUE, [
        "推奨する会社・商品とその理由を意向確認シートに記録した",
        "お客様が選んだ会社・商品を記録した",
        "意向と異なる商品を選択した場合、その理由を確認・記録した",
        "お客様確認サイン欄に日付・サインをいただいた",
    ]),
    ("④ コンプライアンス", RED, [
        "特定会社への一方的な誘導はなく、公平な比較を実施した",
        "意向確認の内容をお客様に読み上げ・確認いただいた",
        "推奨内容がお客様の意向に沿うことを口頭で説明した",
        "本シートを保管・アーカイブ予定（改正保険業法施行規則第227条の2）",
    ]),
]

row = 4
for section, color, items in checklist:
    ws2.row_dimensions[row].height = 20
    ws2.merge_cells(f"B{row}:G{row}")
    ws2.cell(row, 2).value = f"  【 {section} 】"
    ws2.cell(row, 2).fill  = F(DARK)
    ws2.cell(row, 2).font  = Fn(WHITE, True, 9)
    ws2.cell(row, 2).alignment = Al("left")
    row += 1

    for item in items:
        ws2.row_dimensions[row].height = 20
        ws2.cell(row, 2).value = "▸"
        ws2.cell(row, 2).fill  = F(color)
        ws2.cell(row, 2).font  = Fn(WHITE, True, 9)
        ws2.cell(row, 2).alignment = Al("center")

        ws2.merge_cells(f"C{row}:D{row}")
        ws2.cell(row, 3).value = f"  {item}"
        ws2.cell(row, 3).fill  = F("FAFBFA")
        ws2.cell(row, 3).font  = Fn(NAVY, False, 9)
        ws2.cell(row, 3).alignment = Al("left")

        for c in [5, 6, 7]:
            ws2.cell(row, c).fill   = F(YELLOW)
            ws2.cell(row, c).font   = Fn("000000", True, 11)
            ws2.cell(row, c).alignment = Al("center")
            ws2.cell(row, c).border = Border(
                top=Side(style="medium", color=color),
                bottom=Side(style="medium", color=color),
                left=Side(style="medium", color=color),
                right=Side(style="medium", color=color),
            )
            c_cells.append(f"{get_column_letter(c)}{row}")

        row += 1

    ws2.row_dimensions[row].height = 4
    row += 1

dv_c.sqref = " ".join(c_cells)

ws2.merge_cells(f"B{row}:G{row}")
ws2.cell(row, 2).value = (
    "  ＊推奨根拠は必ず「顧客の意向との対応関係」で記録してください"
    "（2026年6月施行 改正保険業法施行規則第227条の2）。"
)
ws2.cell(row, 2).fill  = F(NAVY)
ws2.cell(row, 2).font  = Fn("93B8DC", False, 7)
ws2.cell(row, 2).alignment = Al("left", "center")
ws2.row_dimensions[row].height = 18

# ─── 保存 ─────────────────────────────────────────────────────
out = "/home/user/Sunplaza-supermarket/intent_tool.xlsx"
wb.save(out)
print(f"Saved: {out}")
