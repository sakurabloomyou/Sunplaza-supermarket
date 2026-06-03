"""
意向確認シート（トークスクリプト型）Excelツール生成スクリプト
"""
import openpyxl
from openpyxl.styles import (
    PatternFill, Font, Alignment, Border, Side
)
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.datavalidation import DataValidation

wb = openpyxl.Workbook()
ws = wb.active
ws.title = "意向確認シート"

# ── カラーパレット ──────────────────────────────────────────────
NAVY   = "1C3557"
RED    = "C0392B"
BLUE   = "1B5EB5"
GREEN  = "2E7D5B"
ORANGE = "D35400"
L_BLUE = "DCE8F9"
L_GRN  = "E0F0E8"
L_RED  = "FDECEA"
L_ORG  = "FEF0E4"
BG     = "F2F5F1"
WHITE  = "FFFFFF"
YELLOW = "FFFDE7"
GRAY1  = "EAECE9"
GRAY2  = "BFC5BB"

# ── ヘルパー ───────────────────────────────────────────────────
def fill(color): return PatternFill("solid", fgColor=color)
def font(color=None, bold=False, size=10, name="Meiryo UI"):
    return Font(name=name, bold=bold, size=size,
                color=color if color else "000000")
def align(h="left", v="center", wrap=True):
    return Alignment(horizontal=h, vertical=v, wrap_text=wrap)
def border_box(top=True, bottom=True, left=True, right=True, color="BFC5BB", style="thin"):
    s = Side(style=style, color=color)
    return Border(
        top=s if top else None,
        bottom=s if bottom else None,
        left=s if left else None,
        right=s if right else None,
    )
def thick_border():
    s = Side(style="medium", color="7A8575")
    return Border(top=s, bottom=s, left=s, right=s)

def merge_set(ws, cell_range, text, bg, fg="FFFFFF", bold=True, size=10,
              halign="left", valign="center", wrap=True):
    ws.merge_cells(cell_range)
    c = ws[cell_range.split(":")[0]]
    c.value = text
    c.fill = fill(bg)
    c.font = font(fg, bold, size)
    c.alignment = align(halign, valign, wrap)

def row_set(ws, row, col_start, col_end, bg=None):
    for col in range(col_start, col_end + 1):
        c = ws.cell(row=row, column=col)
        if bg:
            c.fill = fill(bg)

def apply_border_range(ws, min_row, max_row, min_col, max_col,
                        outer_color="7A8575", inner_color="BFC5BB"):
    outer = Side(style="medium", color=outer_color)
    inner = Side(style="thin",   color=inner_color)
    for r in range(min_row, max_row + 1):
        for c_idx in range(min_col, max_col + 1):
            top    = outer if r == min_row    else inner
            bottom = outer if r == max_row    else inner
            left   = outer if c_idx == min_col  else inner
            right  = outer if c_idx == max_col  else inner
            ws.cell(r, c_idx).border = Border(
                top=top, bottom=bottom, left=left, right=right)

# ── 列幅・行高設定 ─────────────────────────────────────────────
col_widths = {
    "A": 2.5, "B": 3, "C": 8, "D": 52, "E": 22, "F": 22, "G": 22, "H": 16
}
for col, w in col_widths.items():
    ws.column_dimensions[col].width = w

# ── シート背景 ─────────────────────────────────────────────────
for r in range(1, 120):
    ws.row_dimensions[r].height = 16
    for c_idx in range(1, 9):
        ws.cell(r, c_idx).fill = fill(BG)

# ════════════════════════════════════════════════════════════════
# ヘッダー
# ════════════════════════════════════════════════════════════════
ws.row_dimensions[1].height = 36
merge_set(ws, "A1:H1",
          "  ■ 自動車保険　意向確認シート（トークスクリプト）",
          NAVY, "FFFFFF", True, 13, "left")

ws.row_dimensions[2].height = 22
merge_set(ws, "A2:H2",
          "  ※ 太字部分はお客様に読み上げてください。黄色セルに入力・選択してください。",
          "16304F", "C8D8F0", False, 8)

# 基本情報欄
ws.row_dimensions[3].height = 6
ws.row_dimensions[4].height = 20

labels = [("D4", "日　付"), ("E4", "担当者名"), ("F4", "お客様名"), ("G4", "支店")]
for cel, lbl in labels:
    ws[cel].value = lbl
    ws[cel].fill  = fill(NAVY)
    ws[cel].font  = font("FFFFFF", True, 8)
    ws[cel].alignment = align("center")

ws.row_dimensions[5].height = 22
input_cells = ["D5", "E5", "F5", "G5"]
for cel in input_cells:
    ws[cel].fill  = fill(YELLOW)
    ws[cel].font  = font("000000", False, 10)
    ws[cel].alignment = align("center")
    ws[cel].border = border_box(color=GRAY2)

ws["H4"].value = "契約形態選択 ↓"
ws["H4"].fill  = fill(RED)
ws["H4"].font  = font("FFFFFF", True, 8)
ws["H4"].alignment = align("center")
ws["H5"].fill  = fill(YELLOW)
ws["H5"].font  = font("000000", True, 10)
ws["H5"].alignment = align("center")
ws["H5"].border = border_box(color=RED, style="medium")

# ドロップダウン（STEP1 選択）
dv1 = DataValidation(
    type="list",
    formula1='"①給与天引き（団体割引）,②一般契約（クレカ・口振）,③通販型（ソニー損保）"',
    allow_blank=True, showDropDown=False
)
dv1.sqref = "H5"
ws.add_data_validation(dv1)

ws.row_dimensions[6].height = 5

# ════════════════════════════════════════════════════════════════
# STEP 1 ブロック
# ════════════════════════════════════════════════════════════════
ws.row_dimensions[7].height  = 20
ws.row_dimensions[8].height  = 18
ws.row_dimensions[9].height  = 72
ws.row_dimensions[10].height = 18
ws.row_dimensions[11].height = 20
ws.row_dimensions[12].height = 20
ws.row_dimensions[13].height = 20
ws.row_dimensions[14].height = 5

# STEP1 ヘッダー
merge_set(ws, "B7:H7",
          "  STEP 1　　契約形態の確認　　（まずこちらをお聞きします）",
          BLUE, "FFFFFF", True, 10)

merge_set(ws, "B8:C8", "📋 スクリプト", "2146A0", "C5D8F5", True, 8, "center")
merge_set(ws, "D8:H8", "", "2146A0", "C5D8F5", False, 8)

# スクリプト本文
script1 = (
    "「当社では●社の自動車保険を扱っています。\n"
    "そのうち 給与天引きで団体割引が使えるのは 損保ジャパン・三井住友海上・東京海上 の3社です。\n"
    "また 通販型のソニー損保 へのお取り次ぎも可能です。\n"
    "クレジットカード払いや口座振替をご希望の場合も、一般契約としてご案内できます。\n\n"
    "どのお支払い方法をご希望ですか？」"
)
merge_set(ws, "D9:H9", script1, "EBF2FC", NAVY, True, 10, "left")
ws["D9"].alignment = Alignment(horizontal="left", vertical="center",
                                wrap_text=True, indent=1)

merge_set(ws, "B9:C9", "📣 読み上げ", L_BLUE, BLUE, True, 8, "center")

# 選択肢説明
choices_data = [
    (10, "①", "給与天引き（団体割引）",   "損保ジャパン・三井住友海上・東京海上 から選択  →  STEP 2A へ", GREEN, L_GRN),
    (11, "②", "一般契約（クレカ・口振）", "同上3社 または その他会社  →  STEP 2A へ",                    BLUE,  L_BLUE),
    (12, "③", "通販型（ソニー損保）",     "ソニー損保へ取り次ぎ  →  STEP 2B へ",                         RED,   L_RED),
]
for row, num, label, note, hdr_col, bg_col in choices_data:
    ws.cell(row, 2).value = num
    ws.cell(row, 2).fill  = fill(hdr_col)
    ws.cell(row, 2).font  = font("FFFFFF", True, 9)
    ws.cell(row, 2).alignment = align("center")
    ws.cell(row, 3).value = label
    ws.cell(row, 3).fill  = fill(bg_col)
    ws.cell(row, 3).font  = font(hdr_col, True, 9)
    ws.cell(row, 3).alignment = align("left")
    ws.merge_cells(f"D{row}:G{row}")
    ws.cell(row, 4).value = note
    ws.cell(row, 4).fill  = fill(bg_col)
    ws.cell(row, 4).font  = font("404B3A", False, 8)
    ws.cell(row, 4).alignment = align("left")
    ws.cell(row, 8).value = "↑H5で選択"
    ws.cell(row, 8).font  = font("7A8575", False, 7)
    ws.cell(row, 8).alignment = align("center")
    if row == 10:
        ws.cell(row, 8).value = "← H5で選択"

apply_border_range(ws, 7, 13, 2, 8)

# ════════════════════════════════════════════════════════════════
# 分岐矢印
# ════════════════════════════════════════════════════════════════
ws.row_dimensions[15].height = 14
merge_set(ws, "B15:E15",
          "  ▼ ①② 給与天引き・一般契約 の場合 ─────────────────────── STEP 2A へ",
          L_GRN, GREEN, True, 8)
merge_set(ws, "F15:H15",
          "  ▼ ③ 通販型 の場合 ─── STEP 2B へ",
          L_RED, RED, True, 8)
ws.row_dimensions[16].height = 4

# ════════════════════════════════════════════════════════════════
# STEP 2A ブロック
# ════════════════════════════════════════════════════════════════
for r in range(17, 37):
    ws.row_dimensions[r].height = 18
ws.row_dimensions[17].height = 20
ws.row_dimensions[19].height = 60
ws.row_dimensions[21].height = 20
ws.row_dimensions[22].height = 20
ws.row_dimensions[23].height = 20
ws.row_dimensions[24].height = 20
ws.row_dimensions[25].height = 20
ws.row_dimensions[26].height = 20

merge_set(ws, "B17:E17",
          "  STEP 2A　　意向確認（重視事項の確認）　　①② 給与天引き・一般契約の方",
          GREEN, "FFFFFF", True, 10)
for c_idx in range(6, 9):
    ws.cell(17, c_idx).fill = fill(GREEN)

merge_set(ws, "B18:C18", "📋 スクリプト", "1E6644", "B8DEC9", True, 8, "center")
merge_set(ws, "D18:H18", "", "1E6644", "B8DEC9", False, 8)

script2a = (
    "「自動車保険でいちばん大切にしていることを教えていただけますか？\n"
    "いくつかお伺いしてもよいですか？　当てはまるものに○をつけてください。\n"
    "（複数回答可）」"
)
merge_set(ws, "D19:H19", script2a, "EDF7F2", NAVY, True, 10, "left")
ws["D19"].alignment = Alignment(horizontal="left", vertical="center",
                                 wrap_text=True, indent=1)
merge_set(ws, "B19:C19", "📣 読み上げ", L_GRN, GREEN, True, 8, "center")

merge_set(ws, "B20:C20", "✏️ 重視項目\n（複数可）", "1E6644", "B8DEC9", True, 8, "center")
merge_set(ws, "D20:E20", "お客様の選択", "1E6644", "B8DEC9", True, 8, "center")
merge_set(ws, "F20:H20", "各社の強み（参考）", "1E6644", "B8DEC9", True, 8, "center")

priority_items = [
    ("保険料をできるだけ抑えたい",          "損保ジャパン（多様なプラン）／三井住友海上（ネット割引）"),
    ("万一の補償をしっかり充実させたい",    "東京海上（総合型・特約充実）／損保ジャパン（幅広い特約）"),
    ("事故時の対応・サポートを重視したい",  "三井住友海上（示談交渉サービス）／東京海上（専任担当）"),
    ("手続きが簡単・わかりやすいものがいい","三井住友海上（シンプル設計・見積り◎）"),
    ("担当者に相談しながら決めたい",        "対面での丁寧なサポートが可能な3社すべて"),
]

dv_check = DataValidation(
    type="list", formula1='"○,−"',
    allow_blank=True, showDropDown=False
)
ws.add_data_validation(dv_check)

for i, (item, note) in enumerate(priority_items):
    row = 21 + i
    ws.cell(row, 2).value = f"  {chr(9312+i)}"
    ws.cell(row, 2).fill  = fill(L_GRN)
    ws.cell(row, 2).font  = font(GREEN, True, 10)
    ws.cell(row, 2).alignment = align("center")

    ws.merge_cells(f"C{row}:D{row}")
    ws.cell(row, 3).value = f"  {item}"
    ws.cell(row, 3).fill  = fill(L_GRN)
    ws.cell(row, 3).font  = font(NAVY, False, 9)
    ws.cell(row, 3).alignment = align("left")

    ws.cell(row, 5).fill   = fill(YELLOW)
    ws.cell(row, 5).font   = font(GREEN, True, 11)
    ws.cell(row, 5).alignment = align("center")
    ws.cell(row, 5).border = border_box(color=GREEN, style="medium")
    dv_check.sqref = f"E{row}" if i == 0 else f"{dv_check.sqref} E{row}"

    ws.merge_cells(f"F{row}:H{row}")
    ws.cell(row, 6).value = f"  {note}"
    ws.cell(row, 6).fill  = fill("F8FFF9")
    ws.cell(row, 6).font  = font("404B3A", False, 8)
    ws.cell(row, 6).alignment = align("left")

apply_border_range(ws, 17, 25, 2, 8)

# ─ STEP 2A フォローアップ ─────────────────────────────────────
ws.row_dimensions[27].height = 5
ws.row_dimensions[28].height = 20
ws.row_dimensions[29].height = 68
ws.row_dimensions[30].height = 20
ws.row_dimensions[31].height = 18
ws.row_dimensions[32].height = 18
ws.row_dimensions[33].height = 18
ws.row_dimensions[34].height = 5

merge_set(ws, "B28:H28",
          "  STEP 2A-2　　3社ご提案（意向確認の結果をふまえて）",
          "1E6644", "FFFFFF", True, 10)

script2a2 = (
    "「ありがとうございます。いただいたご希望をもとに、損保ジャパン・三井住友海上・東京海上\n"
    "の3社でお見積りをご用意します。\n"
    "─── ここがポイント ───────────────────────────────────────────────────\n"
    "三井住友海上は見積り・手続きがシンプルで、担当者の手間も少ないです。\n"
    "ご予算重視のお客様にもお伝えしやすい選択肢です。ぜひ一緒に比べてみましょう。\n"
    "────────────────────────────────────────────────────────────────」"
)
merge_set(ws, "D29:H29", script2a2, "EDF7F2", NAVY, True, 9, "left")
ws["D29"].alignment = Alignment(horizontal="left", vertical="center",
                                 wrap_text=True, indent=1)
merge_set(ws, "B29:C29", "📣 読み上げ\n+ポイント", "1E6644", "B8DEC9", True, 8, "center")

# 3社ヘッダー
merge_set(ws, "B30:C30", "会　社", "404B3A", "EAECE9", True, 8, "center")
merge_set(ws, "D30:E30", "主な強み・特徴", "404B3A", "EAECE9", True, 8, "center")
merge_set(ws, "F30:G30", "MSI提案時の一言", "404B3A", "EAECE9", True, 8, "center")
ws.cell(30, 8).value = "提案する"
ws.cell(30, 8).fill  = fill("404B3A")
ws.cell(30, 8).font  = font("EAECE9", True, 8)
ws.cell(30, 8).alignment = align("center")

companies = [
    ("損保ジャパン",    RED,   "SJ",  L_RED,  "取引歴が長く慣れている。多彩なプラン・特約",           "お客様のご状況を最もよく把握している1社"),
    ("三井住友海上",    GREEN, "MSI", L_GRN,  "シンプル設計・見積りが速い・ネット割引あり",           "手続きが楽で保険料も競争力あり。ぜひ比較を"),
    ("東京海上日動",    BLUE,  "TN",  L_BLUE, "業界最大手。補償・サービスの充実度が高い",             "手厚い補償を求めるお客様に刺さります"),
]

dv_propose = DataValidation(
    type="list", formula1='"◎提案する,○提案する,△保留,×見送り"',
    allow_blank=True, showDropDown=False
)
ws.add_data_validation(dv_propose)
propose_sqref = []

for i, (name, hdr_col, abbr, bg_col, feature, tip) in enumerate(companies):
    row = 31 + i
    ws.merge_cells(f"B{row}:C{row}")
    ws.cell(row, 2).value = f"  {name}"
    ws.cell(row, 2).fill  = fill(hdr_col)
    ws.cell(row, 2).font  = font("FFFFFF", True, 9)
    ws.cell(row, 2).alignment = align("left")

    ws.merge_cells(f"D{row}:E{row}")
    ws.cell(row, 4).value = f"  {feature}"
    ws.cell(row, 4).fill  = fill(bg_col)
    ws.cell(row, 4).font  = font("404B3A", False, 8)
    ws.cell(row, 4).alignment = align("left")

    ws.merge_cells(f"F{row}:G{row}")
    ws.cell(row, 6).value = f"  {tip}"
    ws.cell(row, 6).fill  = fill("FEFEFE")
    ws.cell(row, 6).font  = font("2A3328", False, 8)
    ws.cell(row, 6).alignment = align("left")

    ws.cell(row, 8).fill   = fill(YELLOW)
    ws.cell(row, 8).font   = font(hdr_col, True, 9)
    ws.cell(row, 8).alignment = align("center")
    ws.cell(row, 8).border = border_box(color=hdr_col, style="medium")
    propose_sqref.append(f"H{row}")

dv_propose.sqref = " ".join(propose_sqref)
apply_border_range(ws, 28, 33, 2, 8)

# ════════════════════════════════════════════════════════════════
# STEP 2B ブロック
# ════════════════════════════════════════════════════════════════
for r in range(35, 52):
    ws.row_dimensions[r].height = 18
ws.row_dimensions[35].height = 20
ws.row_dimensions[37].height = 65
ws.row_dimensions[39].height = 65
ws.row_dimensions[40].height = 20
ws.row_dimensions[41].height = 18
ws.row_dimensions[42].height = 18
ws.row_dimensions[43].height = 5

merge_set(ws, "B35:H35",
          "  STEP 2B　　ソニー損保ご案内　　③ 通販型をご希望の方",
          RED, "FFFFFF", True, 10)

merge_set(ws, "B36:C36", "📋 スクリプト", "9B2335", "F5C0BB", True, 8, "center")
merge_set(ws, "D36:H36", "", "9B2335", "F5C0BB", False, 8)

script2b_1 = (
    "「それではソニー損保をご案内しますので、お客様のご状況を確認させてください。\n"
    "ソニー損保はインターネットで直接ご契約いただく通販型です。\n"
    "お手続きはお客様ご自身にインターネットでしていただく形となりますが、よろしいでしょうか？」"
)
merge_set(ws, "D37:H37", script2b_1, "FEF5F4", NAVY, True, 9, "left")
ws["D37"].alignment = Alignment(horizontal="left", vertical="center",
                                 wrap_text=True, indent=1)
merge_set(ws, "B37:C37", "📣 読み上げ①", L_RED, RED, True, 8, "center")

script2b_2 = (
    "「保険料の面ではメリットが大きい場合もありますが、事故時のサポートはコールセンター対応が\n"
    "基本となります。当社担当者が直接サポートすることは難しくなる点もご了承ください。\n"
    "それでもよろしければ、ソニー損保のサイトをご一緒に確認しながら手続きをご案内します。」"
)
merge_set(ws, "D38:H38", script2b_2, "FEF5F4", NAVY, True, 9, "left")
ws["D38"].alignment = Alignment(horizontal="left", vertical="center",
                                 wrap_text=True, indent=1)
ws.row_dimensions[38].height = 65
merge_set(ws, "B38:C38", "📣 読み上げ②\n（留意点の説明）", L_RED, RED, True, 8, "center")

# 対応選択
merge_set(ws, "B39:C39", "✏️ お客様の意向", "9B2335", "F5C0BB", True, 8, "center")
ws.merge_cells("D39:E39")
ws.cell(39, 4).value = "ソニー損保で進める"
ws.cell(39, 4).fill  = fill(L_RED)
ws.cell(39, 4).font  = font("404B3A", False, 9)
ws.cell(39, 4).alignment = align("left")
ws.cell(39, 6).fill  = fill(YELLOW)
ws.cell(39, 6).font  = font(RED, True, 9)
ws.cell(39, 6).alignment = align("center")
ws.cell(39, 6).border = border_box(color=RED, style="medium")

dv_b = DataValidation(type="list", formula1='"はい（取り次ぎ確定）,再検討（給与天引きも比較）,見送り"',
                      allow_blank=True, showDropDown=False)
dv_b.sqref = "F39"
ws.add_data_validation(dv_b)

ws.merge_cells("G39:H39")
ws.cell(39, 7).value = "← 選択してください"
ws.cell(39, 7).fill  = fill(L_RED)
ws.cell(39, 7).font  = font("9B2335", False, 8)
ws.cell(39, 7).alignment = align("left")

apply_border_range(ws, 35, 39, 2, 8)

# ════════════════════════════════════════════════════════════════
# メモ・フォローアップ欄
# ════════════════════════════════════════════════════════════════
ws.row_dimensions[44].height = 20
ws.row_dimensions[45].height = 80
ws.row_dimensions[46].height = 5
ws.row_dimensions[47].height = 20
ws.row_dimensions[48].height = 30
ws.row_dimensions[49].height = 5

merge_set(ws, "B44:H44",
          "  📝 面談メモ・次回アクション",
          "404B3A", "FFFFFF", True, 10)

ws.merge_cells("B45:H45")
ws["B45"].value = ""
ws["B45"].fill  = fill(YELLOW)
ws["B45"].font  = font("000000", False, 10)
ws["B45"].alignment = Alignment(horizontal="left", vertical="top",
                                 wrap_text=True, indent=1)
ws["B45"].border = border_box(color="7A8575", style="medium")

merge_set(ws, "B47:H47",
          "  📌 次回アクション",
          "404B3A", "FFFFFF", True, 10)

ws.merge_cells("B48:H48")
ws["B48"].value = ""
ws["B48"].fill  = fill(YELLOW)
ws["B48"].font  = font("000000", False, 10)
ws["B48"].alignment = Alignment(horizontal="left", vertical="top",
                                 wrap_text=True, indent=1)
ws["B48"].border = border_box(color="7A8575", style="medium")

apply_border_range(ws, 44, 48, 2, 8)

# ════════════════════════════════════════════════════════════════
# フッター
# ════════════════════════════════════════════════════════════════
ws.row_dimensions[50].height = 16
merge_set(ws, "B50:H50",
          "  ＊本シートは比較推奨規制対応の意向確認記録としてご活用ください。"
          "　面談後にファイルを保存・アーカイブしてください。",
          NAVY, "93B8DC", False, 7)

# ════════════════════════════════════════════════════════════════
# Sheet2: 比較推奨チェックリスト（規制対応確認用）
# ════════════════════════════════════════════════════════════════
ws2 = wb.create_sheet("比較推奨チェックリスト")
for r in range(1, 50):
    ws2.row_dimensions[r].height = 16
    for c_idx in range(1, 8):
        ws2.cell(r, c_idx).fill = fill("F5F7F4")

for col, w in [("A",3),("B",4),("C",42),("D",25),("E",12),("F",12),("G",12)]:
    ws2.column_dimensions[col].width = w

ws2.row_dimensions[1].height = 34
ws2.merge_cells("A1:G1")
ws2["A1"].value = "  ■ 比較推奨チェックリスト（金融庁指針対応）"
ws2["A1"].fill  = fill(NAVY)
ws2["A1"].font  = font("FFFFFF", True, 13)
ws2["A1"].alignment = align("left", "center")

ws2.row_dimensions[2].height = 18
ws2.merge_cells("A2:G2")
ws2["A2"].value = "  面談前後に確認し、すべて「済」になっていることを確認してください。"
ws2["A2"].fill  = fill("16304F")
ws2["A2"].font  = font("C8D8F0", False, 8)
ws2["A2"].alignment = align("left", "center")

ws2.row_dimensions[3].height = 5

checklist = [
    ("事前確認", [
        ("お客様の意向（重視事項）を確認した",                       GREEN),
        ("複数社（原則3社以上）の見積りを取得した",                   GREEN),
        ("各社の保険料・補償内容を比較説明した",                      GREEN),
        ("比較に用いた基準・理由を説明できる状態にある",              GREEN),
    ]),
    ("三井住友海上の提案", [
        ("三井住友海上の見積りを必ず含めた",                          "1E6644"),
        ("損保ジャパンとの比較ポイントをお客様に説明した",            "1E6644"),
        ("お客様が三井住友海上を選ばない理由を記録した（選ばない場合）","1E6644"),
    ]),
    ("推奨根拠の記録", [
        ("推奨する商品・会社とその理由を記録した",                    BLUE),
        ("お客様が最終的に選んだ商品・会社を記録した",                BLUE),
        ("意向と選択が異なる場合、その経緯を記録した",                BLUE),
    ]),
    ("コンプライアンス", [
        ("特定の会社を誘導した事実はない",                            RED),
        ("お客様から意向確認の同意を得た",                            RED),
        ("本シートを保管・アーカイブ予定",                            RED),
    ]),
]

dv_chk = DataValidation(
    type="list", formula1='"✅ 済,⬜ 未,N/A"',
    allow_blank=True, showDropDown=False
)
ws2.add_data_validation(dv_chk)
chk_sqref = []

row = 4
for section, items in checklist:
    ws2.row_dimensions[row].height = 20
    ws2.merge_cells(f"B{row}:G{row}")
    ws2.cell(row, 2).value = f"  【 {section} 】"
    ws2.cell(row, 2).fill  = fill("404B3A")
    ws2.cell(row, 2).font  = font("FFFFFF", True, 9)
    ws2.cell(row, 2).alignment = align("left")
    row += 1

    for item_text, color in items:
        ws2.row_dimensions[row].height = 20
        ws2.cell(row, 2).value = "▸"
        ws2.cell(row, 2).fill  = fill(color)
        ws2.cell(row, 2).font  = font("FFFFFF", True, 9)
        ws2.cell(row, 2).alignment = align("center")

        ws2.merge_cells(f"C{row}:D{row}")
        ws2.cell(row, 3).value = f"  {item_text}"
        ws2.cell(row, 3).fill  = fill("FAFBFA")
        ws2.cell(row, 3).font  = font(NAVY, False, 9)
        ws2.cell(row, 3).alignment = align("left")

        for col_idx in [5, 6, 7]:
            ws2.cell(row, col_idx).fill = fill(YELLOW)
            ws2.cell(row, col_idx).font = font("000000", True, 10)
            ws2.cell(row, col_idx).alignment = align("center")
            ws2.cell(row, col_idx).border = border_box(color=GRAY2)
            chk_sqref.append(f"{get_column_letter(col_idx)}{row}")

        ws2.cell(row, 5).border = border_box(color=color, style="medium")
        chk_sqref_unique = list(dict.fromkeys(chk_sqref))
        row += 1

    ws2.row_dimensions[row].height = 4
    row += 1

dv_chk.sqref = " ".join(chk_sqref_unique)

# ヘッダー行の追加
ws2.row_dimensions[3].height = 16
ws2.merge_cells("C3:D3")
ws2.cell(3, 3).value = "  確認項目"
ws2.cell(3, 3).fill  = fill("404B3A")
ws2.cell(3, 3).font  = font("EAECE9", True, 8)
ws2.cell(3, 3).alignment = align("left")
for i, lbl in enumerate(["SJ", "MSI", "TN"], start=5):
    ws2.cell(3, i).value = lbl
    ws2.cell(3, i).fill  = fill("404B3A")
    ws2.cell(3, i).font  = font("EAECE9", True, 8)
    ws2.cell(3, i).alignment = align("center")

# ── 保存 ─────────────────────────────────────────────────────
out = "/home/user/Sunplaza-supermarket/intent_tool.xlsx"
wb.save(out)
print(f"Saved: {out}")
