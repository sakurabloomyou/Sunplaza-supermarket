"""
意向確認シート（トークスクリプト型）Excelツール生成スクリプト v2
・ STEP1 スクリプト内に H7 ドロップダウンを配置
・ STEP2 ①② / ③ をアウトライングループで折りたたみ表示
・ A/B ラベル削除
"""
import openpyxl
from openpyxl.styles import PatternFill, Font, Alignment, Border, Side
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.worksheet.properties import WorksheetProperties, Outline
from openpyxl.utils import get_column_letter

wb = openpyxl.Workbook()
ws = wb.active
ws.title = "意向確認シート"

# ─── カラー ───────────────────────────────────────────────────
NAVY   = "1C3557"
RED    = "C0392B"
BLUE   = "1B5EB5"
GREEN  = "2E7D5B"
L_BLUE = "DCE8F9"
L_GRN  = "E0F0E8"
L_RED  = "FDECEA"
BG     = "F2F5F1"
WHITE  = "FFFFFF"
YELLOW = "FFFDE7"
GRAY1  = "EAECE9"
GRAY2  = "BFC5BB"
DARK   = "404B3A"

# ─── ヘルパー ─────────────────────────────────────────────────
def F(c): return PatternFill("solid", fgColor=c)
def Fn(c=None, bold=False, sz=10, name="Meiryo UI"):
    return Font(name=name, bold=bold, size=sz, color=c or "000000")
def Al(h="left", v="center", wrap=True, indent=0):
    return Alignment(horizontal=h, vertical=v, wrap_text=wrap, indent=indent)
def Bd(color=GRAY2, style="thin"):
    s = Side(style=style, color=color)
    return Border(top=s, bottom=s, left=s, right=s)
def BdOuter(color="7A8575"):
    s = Side(style="medium", color=color)
    return Border(top=s, bottom=s, left=s, right=s)

def ms(ws, rng, text, bg, fg="FFFFFF", bold=True, sz=10,
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

# ─── 列幅・初期行高・背景 ─────────────────────────────────────
for col, w in [("A",2.5),("B",3),("C",9),("D",46),
               ("E",18),("F",20),("G",20),("H",18)]:
    ws.column_dimensions[col].width = w

for r in range(1, 130):
    ws.row_dimensions[r].height = 16
    for c in range(1, 9):
        ws.cell(r, c).fill = F(BG)

# ─── アウトライン設定（＋ボタンをグループの上に表示） ────────
ws.sheet_properties = WorksheetProperties()
ws.sheet_properties.outlinePr = Outline(summaryBelow=False, summaryRight=False)

# ════════════════════════════════════════════════════════════════
#  ヘッダー
# ════════════════════════════════════════════════════════════════
ws.row_dimensions[1].height = 36
ms(ws, "A1:H1",
   "  ■ 自動車保険　意向確認シート（トークスクリプト型）",
   NAVY, "FFFFFF", True, 13)

ws.row_dimensions[2].height = 18
ms(ws, "A2:H2",
   "  ※ 太字部分はお客様へ読み上げてください。黄色セルを入力・選択し、"
   "選択後は対応する下のグループ ＋ を展開してください。",
   "16304F", "C8D8F0", False, 8)

# ─── 基本情報 ──────────────────────────────────────────────────
ws.row_dimensions[3].height = 5
ws.row_dimensions[4].height = 20
ws.row_dimensions[5].height = 22
ws.row_dimensions[6].height = 5

for i, (col, lbl) in enumerate([("C","日　付"),("D","担当者名"),("E","お客様名"),("F","支店")]):
    ws.cell(4, 3+i).value = lbl
    ws.cell(4, 3+i).fill  = F(NAVY)
    ws.cell(4, 3+i).font  = Fn("FFFFFF", True, 8)
    ws.cell(4, 3+i).alignment = Al("center")
    ws.cell(5, 3+i).fill  = F(YELLOW)
    ws.cell(5, 3+i).font  = Fn("000000", False, 10)
    ws.cell(5, 3+i).alignment = Al("center")
    ws.cell(5, 3+i).border = Bd(GRAY2)

ws.cell(4, 8).value = "契約方法"
ws.cell(4, 8).fill  = F(RED)
ws.cell(4, 8).font  = Fn("FFFFFF", True, 8)
ws.cell(4, 8).alignment = Al("center")

# ════════════════════════════════════════════════════════════════
#  STEP 1  ─  行7〜13
# ════════════════════════════════════════════════════════════════
ws.row_dimensions[7].height  = 22
ws.row_dimensions[8].height  = 18
ws.row_dimensions[9].height  = 80
ws.row_dimensions[10].height = 26
ws.row_dimensions[11].height = 20
ws.row_dimensions[12].height = 20
ws.row_dimensions[13].height = 20
ws.row_dimensions[14].height = 5

# STEP1 ヘッダー B7:F7（H7をドロップダウン専用に空ける）
ms(ws, "B7:F7",
   "  STEP 1　　契約方法の確認",
   BLUE, "FFFFFF", True, 11)

# G7: ドロップダウンのラベル
ws["G7"].value = "契約方法を選択 ▼"
ws["G7"].fill  = F(RED)
ws["G7"].font  = Fn("FFFFFF", True, 8)
ws["G7"].alignment = Al("center", "center", False)

# H7: ドロップダウンセル（value は設定しない ← 重要）
ws["H7"].fill  = F(YELLOW)
ws["H7"].font  = Fn(NAVY, True, 11)
ws["H7"].alignment = Al("center", "center", False)

ms(ws, "B8:C8", "📋 スクリプト", "2146A0", "C5D8F5", True, 8, "center")
ms(ws, "D8:H8", "", "2146A0", "C5D8F5", False, 8)

script1 = (
    "「当社では●社の自動車保険を扱っています。\n"
    "そのうち 給与天引き（団体割引）が使えるのは 損保ジャパン・三井住友海上・東京海上 の3社です。\n"
    "通販型のソニー損保 へのお取り次ぎも可能で、"
    "クレジットカード払いや口座振替の一般契約もご案内できます。\n\n"
    "どのご契約方法をご希望ですか？」"
)
ms(ws, "D9:H9", script1, "EBF2FC", NAVY, True, 10, "left", "center", True, 1)
ms(ws, "B9:C9", "📣 読み上げ", L_BLUE, BLUE, True, 8, "center")

# 行10: ドロップダウン専用の目立つ入力行
ms(ws, "B10:F10", "  ▶ お客様のご希望の契約方法（右の黄色セルで選択してください）",
   "FFF8E1", "C0392B", True, 9, "left")
ms(ws, "G10:G10", "契約方法 →", RED, "FFFFFF", True, 8, "center")
# H10 にもドロップダウンを追加（H7 と同じ内容、より目立つ位置）

# 選択肢の説明（行11〜13）
choices = [
    (11, "①", "給与天引き（団体割引）",    "→ 下のグループ「①②」を展開",  GREEN, L_GRN),
    (12, "②", "一般契約（クレカ・口振）",   "→ 下のグループ「①②」を展開",  BLUE,  L_BLUE),
    (13, "③", "通販型（ソニー損保）",       "→ 下のグループ「③」を展開",    RED,   L_RED),
]
for row, num, label, guide, hc, bc in choices:
    ws.cell(row, 2).value = num
    ws.cell(row, 2).fill  = F(hc)
    ws.cell(row, 2).font  = Fn("FFFFFF", True, 9)
    ws.cell(row, 2).alignment = Al("center")

    ws.cell(row, 3).value = label
    ws.cell(row, 3).fill  = F(bc)
    ws.cell(row, 3).font  = Fn(hc, True, 9)
    ws.cell(row, 3).alignment = Al("left")

    ws.merge_cells(f"D{row}:G{row}")
    ws.cell(row, 4).value = guide
    ws.cell(row, 4).fill  = F(bc)
    ws.cell(row, 4).font  = Fn(DARK, False, 8)
    ws.cell(row, 4).alignment = Al("left")

    ws.cell(row, 8).fill = F(bc)

# ── フレーム適用（frame の後で H7/H10 ボーダーを上書き） ──────
frame(ws, 7, 13, 2, 8)

# H7 ボーダー（frame の後に適用して目立つ赤枠に）
ws["H7"].border = Border(
    top=Side(style="medium", color=RED),
    bottom=Side(style="medium", color=RED),
    left=Side(style="medium", color=RED),
    right=Side(style="medium", color=RED),
)
# H10 も同様
ws["H10"].fill   = F(YELLOW)
ws["H10"].font   = Fn(NAVY, True, 11)
ws["H10"].alignment = Al("center", "center", False)
ws["H10"].border = Border(
    top=Side(style="medium", color=RED),
    bottom=Side(style="medium", color=RED),
    left=Side(style="medium", color=RED),
    right=Side(style="medium", color=RED),
)

# ── データ検証：H7 と H10 の両方に同じドロップダウンを設定 ───
dv1 = DataValidation(
    type="list",
    formula1='"①給与天引き（団体割引）,②一般契約（クレカ・口振）,③通販型（ソニー損保）"',
    allow_blank=True, showDropDown=False
)
dv1.sqref = "H7 H10"
ws.add_data_validation(dv1)

# ─── 分岐ガイド行（常時表示） ─────────────────────────────────
ws.row_dimensions[15].height = 20
ms(ws, "B15:E15",
   "  ▼  ①② 給与天引き・一般契約 ─── 下のグループ「＋」で展開",
   L_GRN, GREEN, True, 8)
ms(ws, "F15:H15",
   "  ▼  ③ 通販型 ─── 下のグループ「＋」で展開",
   L_RED, RED, True, 8)

# ════════════════════════════════════════════════════════════════
#  STEP 2（①②）  ─  行16〜36  ← グループ折りたたみ
# ════════════════════════════════════════════════════════════════
# グループ先頭のラベル行（展開後に最初に見える行）
ws.row_dimensions[16].height  = 22
ws.row_dimensions[17].height  = 18
ws.row_dimensions[18].height  = 60
ws.row_dimensions[19].height  = 20
ws.row_dimensions[20].height  = 20
ws.row_dimensions[21].height  = 20
ws.row_dimensions[22].height  = 20
ws.row_dimensions[23].height  = 20
ws.row_dimensions[24].height  = 20
ws.row_dimensions[25].height  = 18
ws.row_dimensions[26].height  = 22
ws.row_dimensions[27].height  = 18
ws.row_dimensions[28].height  = 60
ws.row_dimensions[29].height  = 18
ws.row_dimensions[30].height  = 18
ws.row_dimensions[31].height  = 18
ws.row_dimensions[32].height  = 18
ws.row_dimensions[33].height  = 18
ws.row_dimensions[34].height  = 5
ws.row_dimensions[35].height  = 5

ms(ws, "B16:H16",
   "  STEP 2　　意向確認（重視事項）　　給与天引き・一般契約の方",
   GREEN, "FFFFFF", True, 11)

ms(ws, "B17:C17", "📋 スクリプト", "1E6644", "B8DEC9", True, 8, "center")
ms(ws, "D17:H17", "", "1E6644", "B8DEC9", False, 8)

script2a = (
    "「自動車保険でいちばん大切にしていることを教えていただけますか？\n"
    "いくつかお伺いしてもよいでしょうか？当てはまるものに○をつけてください。（複数回答可）」"
)
ms(ws, "D18:H18", script2a, "EDF7F2", NAVY, True, 10, "left", "center", True, 1)
ms(ws, "B18:C18", "📣 読み上げ", L_GRN, GREEN, True, 8, "center")

# ヘッダー行
ms(ws, "B19:C19", "重視項目", "1E6644", "B8DEC9", True, 8, "center")
ms(ws, "D19:E19", "お客様選択", "1E6644", "B8DEC9", True, 8, "center")
ms(ws, "F19:H19", "各社の強み（参考）", "1E6644", "B8DEC9", True, 8, "center")

priority_items = [
    ("保険料をできるだけ抑えたい",          "損保ジャパン（多様なプラン）／三井住友海上（ネット割引あり）"),
    ("補償をしっかり充実させたい",          "東京海上（総合型・特約充実）／損保ジャパン（幅広い特約）"),
    ("事故時の対応・サポートを重視したい",  "三井住友海上（示談交渉◎）／東京海上（専任担当）"),
    ("手続きが簡単・わかりやすいものがいい","三井住友海上（シンプル設計・見積り速い）"),
    ("担当者に相談しながら決めたい",        "3社すべて対応可。担当者によるサポートが手厚い"),
]
dv_chk = DataValidation(type="list", formula1='"○,−"',
                         allow_blank=True, showDropDown=False)
ws.add_data_validation(dv_chk)
chk_cells = []

for i, (item, note) in enumerate(priority_items):
    row = 20 + i
    ws.cell(row, 2).value = f"  {chr(9312+i)}"
    ws.cell(row, 2).fill  = F(GREEN)
    ws.cell(row, 2).font  = Fn("FFFFFF", True, 10)
    ws.cell(row, 2).alignment = Al("center")

    ws.merge_cells(f"C{row}:E{row}")
    ws.cell(row, 3).value = f"  {item}"
    ws.cell(row, 3).fill  = F(L_GRN)
    ws.cell(row, 3).font  = Fn(NAVY, False, 9)
    ws.cell(row, 3).alignment = Al("left")

    ws.merge_cells(f"F{row}:H{row}")
    ws.cell(row, 6).value = f"  {note}"
    ws.cell(row, 6).fill  = F("F8FFF9")
    ws.cell(row, 6).font  = Fn(DARK, False, 8)
    ws.cell(row, 6).alignment = Al("left")

    # 選択列（E列は merge済みのため D列はスキップ→別列使用不可 →Cに統合）
    # → 代わりに右端 (H列) にチェック列を設ける
    chk_cells.append(f"H{row}")

dv_chk.sqref = " ".join(chk_cells)
for cell in chk_cells:
    ws[cell].fill   = F(YELLOW)
    ws[cell].font   = Fn(GREEN, True, 11)
    ws[cell].alignment = Al("center")
    ws[cell].border = Bd(GREEN, "medium")

frame(ws, 16, 24, 2, 8)

# ─ 3社提案 ────────────────────────────────────────────────────
ms(ws, "B26:H26",
   "  STEP 2-2　　3社ご提案（意向確認結果をふまえて）",
   "1E6644", "FFFFFF", True, 11)

script2a2 = (
    "「ありがとうございます。いただいたご希望をもとに、損保ジャパン・三井住友海上・東京海上 "
    "の3社でお見積りをご用意します。\n"
    "─── 募集人ポイント ────────────────────────────────────────────────────────────\n"
    "三井住友海上はシンプル設計で見積り・手続きが速く、担当者の手間が少ないです。\n"
    "お客様には保険料もご提示しやすい選択肢です。必ず3社セットでお見せしましょう。\n"
    "────────────────────────────────────────────────────────────────────────────」"
)
ms(ws, "D27:H27", script2a2, "EDF7F2", NAVY, True, 9, "left", "center", True, 1)
ms(ws, "B27:C27", "📣 読み上げ\n+ ポイント", "1E6644", "B8DEC9", True, 8, "center")

# 3社比較
ms(ws, "B28:C28", "会　社", DARK, GRAY1, True, 8, "center")
ms(ws, "D28:E28", "主な強み・特徴", DARK, GRAY1, True, 8, "center")
ms(ws, "F28:G28", "MSI提案の一言", DARK, GRAY1, True, 8, "center")
ws.cell(28, 8).value = "提案"
ws.cell(28, 8).fill  = F(DARK)
ws.cell(28, 8).font  = Fn(GRAY1, True, 8)
ws.cell(28, 8).alignment = Al("center")

companies = [
    ("損保ジャパン",  RED,   L_RED,  "取引歴が長く慣れている。多彩なプラン・特約",       "慣れ親しんだ会社。実績・信頼で推せます"),
    ("三井住友海上",  GREEN, L_GRN,  "シンプル設計・見積り速い・ネット割引あり",          "手続きが楽で保険料も競争力あり。比較必須"),
    ("東京海上日動",  BLUE,  L_BLUE, "業界最大手。補償・サービスの充実度が高い",          "手厚い補償を重視するお客様に有効"),
]
dv_prop = DataValidation(type="list",
    formula1='"◎提案する,○提案する,△保留,×見送り"',
    allow_blank=True, showDropDown=False)
ws.add_data_validation(dv_prop)
prop_cells = []

for i, (name, hc, bc, feat, tip) in enumerate(companies):
    row = 29 + i
    ws.merge_cells(f"B{row}:C{row}")
    ws.cell(row, 2).value = f"  {name}"
    ws.cell(row, 2).fill  = F(hc)
    ws.cell(row, 2).font  = Fn("FFFFFF", True, 9)
    ws.cell(row, 2).alignment = Al("left")

    ws.merge_cells(f"D{row}:E{row}")
    ws.cell(row, 4).value = f"  {feat}"
    ws.cell(row, 4).fill  = F(bc)
    ws.cell(row, 4).font  = Fn(DARK, False, 8)
    ws.cell(row, 4).alignment = Al("left")

    ws.merge_cells(f"F{row}:G{row}")
    ws.cell(row, 6).value = f"  {tip}"
    ws.cell(row, 6).fill  = F("FEFEFE")
    ws.cell(row, 6).font  = Fn("2A3328", False, 8)
    ws.cell(row, 6).alignment = Al("left")

    ws.cell(row, 8).fill   = F(YELLOW)
    ws.cell(row, 8).font   = Fn(hc, True, 9)
    ws.cell(row, 8).alignment = Al("center")
    ws.cell(row, 8).border = Bd(hc, "medium")
    prop_cells.append(f"H{row}")

dv_prop.sqref = " ".join(prop_cells)
frame(ws, 26, 33, 2, 8)

# ── STEP2 ①② グループ設定（行16〜34 を折りたたみ） ──────────
for r in range(16, 35):
    ws.row_dimensions[r].outline_level = 1
    ws.row_dimensions[r].hidden = True

# ════════════════════════════════════════════════════════════════
#  STEP 2（③通販型）  ─  行36〜45  ← グループ折りたたみ
# ════════════════════════════════════════════════════════════════
ws.row_dimensions[36].height = 22
ws.row_dimensions[37].height = 18
ws.row_dimensions[38].height = 65
ws.row_dimensions[39].height = 65
ws.row_dimensions[40].height = 20
ws.row_dimensions[41].height = 18
ws.row_dimensions[42].height = 18
ws.row_dimensions[43].height = 5

ms(ws, "B36:H36",
   "  STEP 2　　ソニー損保ご案内　　通販型をご希望の方",
   RED, "FFFFFF", True, 11)

ms(ws, "B37:C37", "📋 スクリプト", "9B2335", "F5C0BB", True, 8, "center")
ms(ws, "D37:H37", "", "9B2335", "F5C0BB", False, 8)

script_b1 = (
    "「それではソニー損保をご案内しますので、お客様のご状況を確認させてください。\n"
    "ソニー損保はインターネットでお客様ご自身に直接ご契約いただく通販型です。"
    "手続きはお客様側のご対応となりますが、よろしいでしょうか？」"
)
ms(ws, "D38:H38", script_b1, "FEF5F4", NAVY, True, 9, "left", "center", True, 1)
ms(ws, "B38:C38", "📣 読み上げ①", L_RED, RED, True, 8, "center")

script_b2 = (
    "「保険料面ではメリットが出る場合もありますが、事故時のサポートはコールセンター対応が基本となります。\n"
    "当社担当者が直接サポートすることは難しくなりますが、それでもよろしいでしょうか？\n"
    "ご希望でしたら、ソニー損保のサイトをご一緒に確認しながら手続きをご案内します。」"
)
ms(ws, "D39:H39", script_b2, "FEF5F4", NAVY, True, 9, "left", "center", True, 1)
ms(ws, "B39:C39", "📣 読み上げ②\n（留意点）", L_RED, RED, True, 8, "center")

ms(ws, "B40:C40", "✏️ お客様の意向", "9B2335", "F5C0BB", True, 8, "center")
ws.merge_cells("D40:G40")
ws["D40"].value = "ソニー損保で進める"
ws["D40"].fill  = F(L_RED)
ws["D40"].font  = Fn(DARK, False, 9)
ws["D40"].alignment = Al("left")
ws["H40"].fill  = F(YELLOW)
ws["H40"].font  = Fn(RED, True, 9)
ws["H40"].alignment = Al("center")
ws["H40"].border = Bd(RED, "medium")

dv_b = DataValidation(type="list",
    formula1='"はい（取り次ぎ確定）,再検討（3社も比較）,見送り"',
    allow_blank=True, showDropDown=False)
dv_b.sqref = "H40"
ws.add_data_validation(dv_b)

for r in [41, 42]:
    ms(ws, f"B{r}:C{r}", "", "9B2335", "F5C0BB", False, 8)

frame(ws, 36, 42, 2, 8)

# ── STEP2 ③ グループ設定（行36〜44 を折りたたみ） ──────────
for r in range(36, 45):
    ws.row_dimensions[r].outline_level = 1
    ws.row_dimensions[r].hidden = True

# ════════════════════════════════════════════════════════════════
#  メモ欄
# ════════════════════════════════════════════════════════════════
ws.row_dimensions[46].height = 20
ws.row_dimensions[47].height = 80
ws.row_dimensions[48].height = 5
ws.row_dimensions[49].height = 20
ws.row_dimensions[50].height = 30
ws.row_dimensions[51].height = 5

ms(ws, "B46:H46", "  📝 面談メモ・お客様の声", DARK, "FFFFFF", True, 10)
ws.merge_cells("B47:H47")
ws["B47"].fill = F(YELLOW)
ws["B47"].font = Fn("000000", False, 10)
ws["B47"].alignment = Alignment(horizontal="left", vertical="top",
                                  wrap_text=True, indent=1)
ws["B47"].border = BdOuter()

ms(ws, "B49:H49", "  📌 次回アクション", DARK, "FFFFFF", True, 10)
ws.merge_cells("B50:H50")
ws["B50"].fill = F(YELLOW)
ws["B50"].font = Fn("000000", False, 10)
ws["B50"].alignment = Alignment(horizontal="left", vertical="top",
                                  wrap_text=True, indent=1)
ws["B50"].border = BdOuter()

frame(ws, 46, 50, 2, 8)

# ────── フッター ──────────────────────────────────────────────
ws.row_dimensions[52].height = 16
ms(ws, "B52:H52",
   "  ＊本シートは比較推奨規制対応の意向確認記録として活用してください。面談後は保存・アーカイブをお願いします。",
   NAVY, "93B8DC", False, 7)

# ════════════════════════════════════════════════════════════════
#  Sheet 2: 比較推奨チェックリスト
# ════════════════════════════════════════════════════════════════
ws2 = wb.create_sheet("比較推奨チェックリスト")

for r in range(1, 60):
    ws2.row_dimensions[r].height = 16
    for c in range(1, 8):
        ws2.cell(r, c).fill = F("F5F7F4")

for col, w in [("A",3),("B",4),("C",44),("D",22),("E",10),("F",10),("G",10)]:
    ws2.column_dimensions[col].width = w

ws2.row_dimensions[1].height = 34
ws2.merge_cells("A1:G1")
ws2["A1"].value = "  ■ 比較推奨チェックリスト（金融庁指針対応）"
ws2["A1"].fill  = F(NAVY)
ws2["A1"].font  = Fn("FFFFFF", True, 13)
ws2["A1"].alignment = Al("left", "center")

ws2.row_dimensions[2].height = 18
ws2.merge_cells("A2:G2")
ws2["A2"].value = "  面談前後に確認し、すべて「✅ 済」になっていることを確認してください。"
ws2["A2"].fill  = F("16304F")
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
    ("事前確認", GREEN, [
        "お客様の意向（重視事項）を確認した",
        "複数社（原則3社）の見積りを取得した",
        "各社の保険料・補償内容を比較説明した",
        "比較に用いた基準・理由を説明できる",
    ]),
    ("三井住友海上の提案", "1E6644", [
        "三井住友海上の見積りを必ず含めた",
        "損保ジャパンとの比較ポイントを説明した",
        "MSIを選ばない場合、理由を記録した",
    ]),
    ("推奨根拠の記録", BLUE, [
        "推奨する会社・商品とその理由を記録した",
        "お客様が選んだ会社・商品を記録した",
        "意向と選択が異なる場合、経緯を記録した",
    ]),
    ("コンプライアンス", RED, [
        "特定会社への誘導はない",
        "意向確認の同意を得た",
        "本シートを保管・アーカイブ予定",
    ]),
]

row = 4
for section, color, items in checklist:
    ws2.row_dimensions[row].height = 20
    ws2.merge_cells(f"B{row}:G{row}")
    ws2.cell(row, 2).value = f"  【 {section} 】"
    ws2.cell(row, 2).fill  = F(DARK)
    ws2.cell(row, 2).font  = Fn("FFFFFF", True, 9)
    ws2.cell(row, 2).alignment = Al("left")
    row += 1

    for item in items:
        ws2.row_dimensions[row].height = 20
        ws2.cell(row, 2).value = "▸"
        ws2.cell(row, 2).fill  = F(color)
        ws2.cell(row, 2).font  = Fn("FFFFFF", True, 9)
        ws2.cell(row, 2).alignment = Al("center")

        ws2.merge_cells(f"C{row}:D{row}")
        ws2.cell(row, 3).value = f"  {item}"
        ws2.cell(row, 3).fill  = F("FAFBFA")
        ws2.cell(row, 3).font  = Fn(NAVY, False, 9)
        ws2.cell(row, 3).alignment = Al("left")

        for c in [5, 6, 7]:
            ws2.cell(row, c).fill   = F(YELLOW)
            ws2.cell(row, c).font   = Fn("000000", True, 10)
            ws2.cell(row, c).alignment = Al("center")
            ws2.cell(row, c).border = Bd(GRAY2)
            c_cells.append(f"{get_column_letter(c)}{row}")

        ws2.cell(row, 5).border = Bd(color, "medium")
        row += 1

    ws2.row_dimensions[row].height = 4
    row += 1

dv_c.sqref = " ".join(c_cells)

# ─── 保存 ─────────────────────────────────────────────────────
out = "/home/user/Sunplaza-supermarket/intent_tool.xlsx"
wb.save(out)
print(f"Saved: {out}")
