"""
意向確認シート v6 — xlsxwriter版（Excel完全互換）
"""
import xlsxwriter

out = "/home/user/Sunplaza-supermarket/intent_tool.xlsx"
wb = xlsxwriter.Workbook(out)
ws  = wb.add_worksheet("意向確認シート")
ws2 = wb.add_worksheet("比較推奨チェックリスト")

# ── カラー ──────────────────────────────────────────────────────
NAVY     = "#1C3557"; DNAVY   = "#16304F"; RED     = "#C0392B"
DRED     = "#9B2335"; BLUE    = "#1B5EB5"; DBLUE   = "#2146A0"
GREEN    = "#2E7D5B"; DGRN    = "#1E6644"; LBLUE   = "#DCE8F9"
LGRN     = "#E0F0E8"; LRED    = "#FDECEA"; BG      = "#F2F5F1"
WHITE    = "#FFFFFF"; YELLOW  = "#FFFDE7"; LYELLOW = "#FFF8E1"
GRAY1    = "#EAECE9"; GRAY2   = "#BFC5BB"; DARK    = "#404B3A"
ORANGE   = "#E67E22"; LORANGE = "#FEF0E3"; DORG    = "#D35400"

# ── フォーマット工場 ──────────────────────────────────────────
def fmt(bg=None, fg="#000000", bold=False, sz=10,
        ha="left", va="vcenter", wrap=True,
        border=0, border_color="#BFC5BB",
        top_c=None, bot_c=None, left_c=None, right_c=None,
        top_s=None, bot_s=None, left_s=None, right_s=None):
    d = {"font_name":"Meiryo UI","font_size":sz,
         "font_color":fg,"bold":bold,
         "align":ha,"valign":va,"text_wrap":wrap}
    if bg: d["bg_color"] = bg
    # uniform border
    if border:
        for side in ("top","bottom","left","right"):
            d[f"border"]   = border
        d["border_color"] = border_color
    # per-side overrides
    for side, col, sty in [
        ("top",   top_c,   top_s),
        ("bottom",bot_c,   bot_s),
        ("left",  left_c,  left_s),
        ("right", right_c, right_s),
    ]:
        if col: d[f"{side}_color"] = col
        if sty: d[f"{side}"] = sty
    return wb.add_format(d)

def hdr(bg, fg=WHITE, sz=10, bold=True, ha="left"):
    return fmt(bg=bg, fg=fg, sz=sz, bold=bold, ha=ha)

def inp(border_color=GREEN):
    return fmt(bg=YELLOW, fg=NAVY, bold=True, sz=11, ha="center", va="vcenter",
               wrap=False,
               top_c=border_color, bot_c=border_color,
               left_c=border_color, right_c=border_color,
               top_s=2, bot_s=2, left_s=2, right_s=2)

def body(bg, fg=DARK, sz=9, ha="left", bold=False):
    return fmt(bg=bg, fg=fg, sz=sz, ha=ha, bold=bold,
               top_s=1, bot_s=1, left_s=1, right_s=1,
               top_c=GRAY2, bot_c=GRAY2, left_c=GRAY2, right_c=GRAY2)

# ── 列幅 ─────────────────────────────────────────────────────
ws.set_column(0, 0, 2.5)   # A
ws.set_column(1, 1, 3)     # B
ws.set_column(2, 2, 9)     # C
ws.set_column(3, 3, 44)    # D
ws.set_column(4, 4, 18)    # E
ws.set_column(5, 5, 20)    # F
ws.set_column(6, 6, 20)    # G
ws.set_column(7, 7, 18)    # H

# ── 行グループ（折りたたみ: STEP2①②=16-49, ③=51-57） ─────────
for r in range(15, 49):   # rows 16-49 (0-indexed 15-48)
    ws.set_row(r, None, None, {"level":1, "hidden":True, "collapsed":False})
for r in range(50, 57):   # rows 51-57 (0-indexed 50-56)
    ws.set_row(r, None, None, {"level":1, "hidden":True, "collapsed":False})

# ── ヘッダー ─────────────────────────────────────────────────
ws.set_row(0, 36)
ws.merge_range("A1:H1",
    "  ■ 自動車保険　意向確認シート（トークスクリプト型）　改正保険業法対応版",
    hdr(NAVY, WHITE, 13))

ws.set_row(1, 18)
ws.merge_range("A2:H2",
    "  ※ 太字部分はお客様へ読み上げます。黄色セルを入力・選択し、"
    "STEP2は選択後に左端の ＋ ボタンで該当グループを展開してください。"
    "【2026年6月施行 改正保険業法（比較推奨規制）対応】",
    fmt(bg=DNAVY, fg="#C8D8F0", sz=8))

# 基本情報
ws.set_row(2, 5)
ws.set_row(3, 20)
ws.set_row(4, 22)
ws.set_row(5, 5)

lbls = ["日　付","担当者名","お客様名","支　店"]
for i, lbl in enumerate(lbls):
    ws.write(3, 2+i, lbl, hdr(NAVY, WHITE, 8, ha="center"))
    ws.write(4, 2+i, "", inp(GRAY2))

# ════════════════════════════════════════════════════════════════
#  STEP 1（行7〜14）
# ════════════════════════════════════════════════════════════════
ws.set_row(6,  22)
ws.set_row(7,  55)
ws.set_row(8,  70)
ws.set_row(9,  26)
ws.set_row(10, 20)
ws.set_row(11, 20)
ws.set_row(12, 20)
ws.set_row(13, 5)

ws.merge_range("B7:H7",
    "  STEP 1　　はじめに・契約方法の確認", hdr(BLUE, WHITE, 11))

ws.merge_range("B8:C8",
    "📣 読み上げ①\n（開始前）", hdr(DBLUE, "#C5D8F5", 8, ha="center"))
opening = (
    "「本日は自動車保険のご案内をいたします。当社は複数の保険会社の商品を取り扱っており、"
    "お客様のご意向・ご状況に合った保険をご提案するために、まずいくつかお伺いします。\n"
    "ご確認いただいた内容は意向確認の記録として残させていただきます。よろしいですか？」\n"
    "※保険業法第294条の3および2026年6月施行の改正保険業法施行規則第227条の2に基づき実施"
)
ws.merge_range("D8:H8", opening,
    fmt(bg=LBLUE, fg=NAVY, sz=10, ha="left", va="vcenter"))

ws.merge_range("B9:C9",
    "📣 読み上げ②\n（契約方法）", hdr(DBLUE, "#C5D8F5", 8, ha="center"))
script1 = (
    "「当社では複数社の自動車保険を扱っています。"
    "給与天引き（団体割引）が使えるのは 損保ジャパン・三井住友海上・東京海上 の3社です。\n"
    "通販型のソニー損保へのお取り次ぎも可能で、クレカ・口振の一般契約もご案内できます。\n\n"
    "どのご契約方法をご希望ですか？」"
)
ws.merge_range("D9:H9", script1,
    fmt(bg="#EBF2FC", fg=NAVY, sz=10, ha="left", va="vcenter"))

ws.merge_range("B10:F10",
    "  ▶ お客様のご希望の契約方法（右の黄色セルで選択してください）",
    fmt(bg=LYELLOW, fg=RED, sz=9, bold=True))
ws.write("G10", "契約方法 →", hdr(RED, WHITE, 8, ha="center"))
ws.write("H10", "", inp(RED))
ws.data_validation("H10", {
    "validate":"list",
    "source":["①給与天引き（団体割引）","②一般契約（クレカ・口振）","③通販型（ソニー損保）"],
    "dropdown": True
})

choices = [
    (10, "①", "給与天引き（団体割引）",  "→ 下のグループ「①②」を展開", GREEN, LGRN),
    (11, "②", "一般契約（クレカ・口振）","→ 下のグループ「①②」を展開", BLUE,  LBLUE),
    (12, "③", "通販型（ソニー損保）",    "→ 下のグループ「③」を展開",  RED,   LRED),
]
for row, num, label, guide, hc, bc in choices:
    ws.write(row, 1, num, hdr(hc, WHITE, 9, ha="center"))
    ws.write(row, 2, label, fmt(bg=bc, fg=hc, sz=9, bold=True))
    ws.merge_range(row, 3, row, 7, guide, fmt(bg=bc, fg=DARK, sz=8))

# ── 分岐ガイド（行15） ─────────────────────────────────────────
ws.set_row(14, 24)
ws.merge_range("B15:E15",
    "  ▼  ①② 給与天引き・一般契約 ─── 下のグループ ＋ で展開",
    fmt(bg=LGRN, fg=GREEN, sz=9, bold=True))
ws.merge_range("F15:H15",
    "  ▼  ③ 通販型 ─── 下のグループ ＋ で展開",
    fmt(bg=LRED, fg=RED, sz=9, bold=True))

# ════════════════════════════════════════════════════════════════
#  STEP 2①② 行16〜49（グループ level=1 hidden）
# ════════════════════════════════════════════════════════════════
ws.set_row(15, 22, None, {"level":1,"hidden":True})
ws.set_row(16, 18, None, {"level":1,"hidden":True})
ws.set_row(17, 55, None, {"level":1,"hidden":True})
ws.set_row(18, 18, None, {"level":1,"hidden":True})
for r in range(19, 24):
    ws.set_row(r, 20, None, {"level":1,"hidden":True})
ws.set_row(24, 5,  None, {"level":1,"hidden":True})
ws.set_row(25, 20, None, {"level":1,"hidden":True})
for r in range(26, 29):
    ws.set_row(r, 20, None, {"level":1,"hidden":True})
ws.set_row(29, 5,  None, {"level":1,"hidden":True})
ws.set_row(30, 20, None, {"level":1,"hidden":True})
ws.set_row(31, 18, None, {"level":1,"hidden":True})
for r in range(32, 36):
    ws.set_row(r, 20, None, {"level":1,"hidden":True})
ws.set_row(35, 5,  None, {"level":1,"hidden":True})
ws.set_row(36, 22, None, {"level":1,"hidden":True})
ws.set_row(37, 18, None, {"level":1,"hidden":True})
ws.set_row(38, 68, None, {"level":1,"hidden":True})
ws.set_row(39, 18, None, {"level":1,"hidden":True})
for r in range(40, 43):
    ws.set_row(r, 48, None, {"level":1,"hidden":True})
ws.set_row(43, 20, None, {"level":1,"hidden":True})
ws.set_row(44, 5,  None, {"level":1,"hidden":True})
ws.set_row(45, 24, None, {"level":1,"hidden":True})
ws.set_row(46, 30, None, {"level":1,"hidden":True})
ws.set_row(47, 5,  None, {"level":1,"hidden":True})
ws.set_row(48, 5,  None, {"level":1,"hidden":True})

ws.merge_range("B16:H16",
    "  STEP 2　　意向確認（重視事項・補償内容・リスク把握）　給与天引き・一般契約の方",
    hdr(GREEN, WHITE, 11))

ws.merge_range("B17:C17","📋 スクリプト", hdr(DGRN,"#B8DEC9",8,ha="center"))
ws.merge_range("D17:H17","", hdr(DGRN,"#B8DEC9",8))

script2a = (
    "「自動車保険でいちばん大切にしていることを教えていただけますか？"
    "いくつかお伺いしてもよいでしょうか？（複数回答可）」"
)
ws.merge_range("D18:H18", script2a,
    fmt(bg="#EDF7F2", fg=NAVY, sz=10, ha="left", va="vcenter"))
ws.merge_range("B18:C18","📣 読み上げ", fmt(bg=LGRN,fg=GREEN,sz=8,bold=True,ha="center"))

ws.merge_range("B19:C19","重視事項\n（複数可）", hdr(DGRN,"#B8DEC9",8,ha="center"))
ws.merge_range("D19:F19","お客様の重視事項",    hdr(DGRN,"#B8DEC9",8,ha="center"))
ws.merge_range("G19:H19","各社の強み（参考）",  hdr(DGRN,"#B8DEC9",8,ha="center"))

priority_items = [
    ("保険料をできるだけ抑えたい",         "損保ジャパン（多様なプラン）／三井住友海上（ネット割引）"),
    ("補償をしっかり充実させたい",         "東京海上（総合型・特約充実）／損保ジャパン（幅広い特約）"),
    ("事故時の対応・サポートを重視したい", "三井住友海上（示談交渉◎）／東京海上（専任担当）"),
    ("手続きが簡単・わかりやすいものがいい","三井住友海上（シンプル設計）"),
    ("担当者に相談しながら決めたい",       "3社すべて対応可。担当者サポートあり"),
]
prio_cells = []
for i, (item, note) in enumerate(priority_items):
    r = 19 + i
    ws.write(r, 1, f"  {chr(9312+i)}", hdr(GREEN, WHITE, 10, ha="center"))
    ws.merge_range(r, 2, r, 5, f"  {item}", fmt(bg=LGRN, fg=NAVY, sz=9))
    ws.write(r, 6, f"  {note}", fmt(bg="#F8FFF9", fg=DARK, sz=8))
    ws.write(r, 7, "", inp(GREEN))
    ws.data_validation(r, 7, r, 7, {"validate":"list","source":["○","−"],"dropdown":True})

ws.merge_range("B26:H26","  補償内容の確認（意向把握の必須事項）", hdr(DGRN,WHITE,9))

coverage_items = [
    ("車両保険の加入希望",  ["ご希望あり","検討中","不要"],
     "車両保険あり・なしで保険料が大きく変わります"),
    ("運転者の範囲",        ["本人のみ","家族限定","限定なし"],
     "限定なしは保険料が高くなる場合があります"),
    ("年間走行距離の目安",  ["5000km未満","〜10000km","10000km超"],
     "距離が多いほどリスクが高まる場合があります"),
]
for i, (label, choices_list, note) in enumerate(coverage_items):
    r = 26 + i
    ws.write(r, 1, f"  {chr(9317+i)}", hdr(DGRN, WHITE, 9, ha="center"))
    ws.merge_range(r, 2, r, 4, f"  {label}", fmt(bg=LGRN, fg=NAVY, sz=9))
    ws.merge_range(r, 5, r, 6, f"  {note}", fmt(bg="#F8FFF9", fg=DARK, sz=8))
    ws.write(r, 7, "", inp(DGRN))
    ws.data_validation(r, 7, r, 7,
        {"validate":"list","source":choices_list,"dropdown":True})

# ── 特定リスク把握（行31〜35） ─────────────────────────────────
ws.merge_range("B31:H31",
    "  特定リスク把握　　気になるリスク・トラブルはありますか？（複数可）",
    hdr(ORANGE, WHITE, 9))

ws.merge_range("B32:C32","リスク把握", hdr(DORG,"#FFE0C0",8,ha="center"))
ws.merge_range("D32:F32","リスク項目",       hdr(DORG,"#FFE0C0",8,ha="center"))
ws.merge_range("G32:H32","対応する補償・特約", hdr(DORG,"#FFE0C0",8,ha="center"))

risk_items = [
    ("自転車・歩行者との事故",   "対人賠償保険（無制限推奨）／個人賠償責任特約"),
    ("故障・レッカー手配",       "ロードサービス（搬送距離・回数）を各社比較"),
    ("あおり運転・危険運転被害", "弁護士費用特約（法的対応費用をカバー）"),
    ("当て逃げ・駐車場トラブル", "車両保険（エコノミー型で当て逃げ補償）"),
]
for i, (risk, coverage) in enumerate(risk_items):
    r = 32 + i
    ws.write(r, 1, f"  R{i+1}", hdr(ORANGE, WHITE, 9, ha="center"))
    ws.merge_range(r, 2, r, 5, f"  {risk}", fmt(bg=LORANGE, fg=NAVY, sz=9))
    ws.write(r, 6, f"  {coverage}", fmt(bg="#FFF8F0", fg=DARK, sz=8))
    ws.write(r, 7, "", inp(ORANGE))
    ws.data_validation(r, 7, r, 7,
        {"validate":"list","source":["○ 気になる","− 特になし"],"dropdown":True})

# ── STEP2-2: 3社提案（行37〜45） ─────────────────────────────
ws.merge_range("B37:H37",
    "  STEP 2-2　　3社ご提案（意向確認結果をふまえて）", hdr(DGRN,WHITE,11))

script2b = (
    "「ありがとうございます。いただいたご意向をもとに3社でお見積りをご用意します。\n"
    "── 募集人ポイント ──\n"
    "・保険料重視 → 三井住友海上のシンプルプラン\n"
    "・補償充実重視 → 東京海上の総合型／損保ジャパンの幅広い特約\n"
    "・事故対応重視 → 三井住友海上の示談交渉サービス／東京海上の専任担当\n"
    "必ず3社のお見積りをご提示し、推奨理由をご説明ください。」"
)
ws.merge_range("D38:H38", script2b,
    fmt(bg="#EDF7F2", fg=NAVY, sz=9, ha="left", va="vcenter"))
ws.merge_range("B38:C38","📣 読み上げ\n+ポイント", hdr(DGRN,"#B8DEC9",8,ha="center"))

ws.merge_range("B39:C39","会社・商品名",     hdr(DARK,GRAY1,8,ha="center"))
ws.merge_range("D39:E39","主な強み・固有特約", hdr(DARK,GRAY1,8,ha="center"))
ws.merge_range("F39:G39","顧客への一言",     hdr(DARK,GRAY1,8,ha="center"))
ws.write("H39","提案",hdr(DARK,GRAY1,8,ha="center"))

companies = [
    (RED,  LRED,
     "損保ジャパン\n「THEクルマの保険」",
     "・つながるドラレコ（安全運転スコア割引 最大20%）\n"
     "・故障運搬時車両損害特約（最大30万円）\n"
     "・代車費用特約（30日型）",
     "取引歴が長く特約の選択肢が豊富。\nドラレコ割引で保険料を抑えたい方に。"),
    (GREEN,LGRN,
     "三井住友海上\n「GKクルマの保険」",
     "・プレミアムドラレコ（360°全方位・AI事故状況分析）\n"
     "・雹災緊急アラート（業界唯一）\n"
     "・LINE連携で手続き完結",
     "シンプル設計で手続き楽々。\n保険料重視・手続き簡便を求める方に。"),
    (BLUE, LBLUE,
     "東京海上日動\n「トータルアシスト」",
     "・DAP（ドライブエージェントパーソナル）\n"
     "・入院時選べるアシスト特約（自動付帯）\n"
     "・エコノミー型（当て逃げ補償あり）",
     "業界最大手の手厚い補償。\n事故後サポート重視の方に。"),
]
for i, (hc, bc, name, feat, tip) in enumerate(companies):
    r = 40 + i
    ws.merge_range(r, 1, r, 2, name,
        fmt(bg=hc, fg=WHITE, sz=9, bold=True, ha="center", va="vcenter"))
    ws.merge_range(r, 3, r, 4, feat,
        fmt(bg=bc, fg=DARK, sz=8, ha="left", va="top"))
    ws.merge_range(r, 5, r, 6, tip,
        fmt(bg=WHITE, fg="#2A3328", sz=8, ha="left", va="top"))
    ws.write(r, 7, "", inp(hc))
    ws.data_validation(r, 7, r, 7, {
        "validate":"list",
        "source":["◎提案する","○提案する","△保留","×見送り"],
        "dropdown":True
    })

# 推奨根拠記録欄（行44）
ws.merge_range("B44:D44","  📝 推奨根拠記録（比較推奨規制必須）",
    hdr(DNAVY,WHITE,9))
ws.merge_range("E44:F44","上記のご意向（           ）に照らし、",
    fmt(bg=LBLUE, fg=NAVY, sz=9))
ws.write("G44","推奨会社 →", hdr(NAVY,WHITE,8,ha="center"))
ws.write("H44","", inp(NAVY))
ws.data_validation("H44",{
    "validate":"list",
    "source":["損保ジャパン","三井住友海上","東京海上日動","お客様選択"],
    "dropdown":True
})

# お客様確認サイン欄（行46〜47）
ws.merge_range("B46:H46",
    "  ✍ お客様確認サイン（比較推奨規制・同意記録）",
    hdr(DNAVY,WHITE,10))
ws.merge_range("B47:E47",
    "  「上記の比較内容・推奨根拠を確認しました。内容は私の意向と合致しています。」",
    fmt(bg=LBLUE, fg=NAVY, sz=9))
ws.write("F47","確認日 →", hdr(DNAVY,WHITE,8,ha="center"))
ws.write("G47","", inp(DNAVY))
ws.write("H47","サイン", fmt(bg=YELLOW, fg=DARK, sz=9, ha="center",
    top_c=DNAVY, bot_c=DNAVY, left_c=DNAVY, right_c=DNAVY,
    top_s=2, bot_s=2, left_s=2, right_s=2))

# ════════════════════════════════════════════════════════════════
#  STEP 2③（行51〜57）
# ════════════════════════════════════════════════════════════════
ws.set_row(50, 22, None, {"level":1,"hidden":True})
ws.set_row(51, 18, None, {"level":1,"hidden":True})
ws.set_row(52, 60, None, {"level":1,"hidden":True})
ws.set_row(53, 60, None, {"level":1,"hidden":True})
ws.set_row(54, 22, None, {"level":1,"hidden":True})
ws.set_row(55, 20, None, {"level":1,"hidden":True})
ws.set_row(56, 5,  None, {"level":1,"hidden":True})

ws.merge_range("B51:H51",
    "  STEP 2　　ソニー損保ご案内　　通販型をご希望の方",
    hdr(RED,WHITE,11))
ws.merge_range("B52:C52","📋 スクリプト", hdr(DRED,"#F5C0BB",8,ha="center"))
ws.merge_range("D52:H52","", hdr(DRED,"#F5C0BB",8))

sb1 = (
    "「ソニー損保はインターネットでお客様ご自身に直接ご契約いただく通販型です。"
    "当社（代理店）が契約を代理するものではなく、申込・告知内容はお客様ご自身でご入力・確認いただきます。"
    "手続きはお客様側のご対応となりますが、よろしいでしょうか？」"
)
ws.merge_range("D53:H53", sb1,
    fmt(bg="#FEF5F4", fg=NAVY, sz=9, ha="left", va="vcenter"))
ws.merge_range("B53:C53","📣 読み上げ①", fmt(bg=LRED,fg=RED,sz=8,bold=True,ha="center"))

sb2 = (
    "「事故時のサポートはソニー損保のコールセンター対応が基本となり、"
    "当社担当者が直接サポートすることは難しくなります。この点をご了解いただいたうえでご希望ですか？」"
)
ws.merge_range("D54:H54", sb2,
    fmt(bg="#FEF5F4", fg=NAVY, sz=9, ha="left", va="vcenter"))
ws.merge_range("B54:C54","📣 読み上げ②\n（留意事項）",
    fmt(bg=LRED,fg=RED,sz=8,bold=True,ha="center"))

ws.merge_range("B55:C55","✏️ お客様確認", hdr(DRED,"#F5C0BB",8,ha="center"))
ws.merge_range("D55:E55","通販型の特性を理解の上、ソニー損保を希望する",
    fmt(bg=LRED, fg=DARK, sz=8))
ws.merge_range("F55:G55","← お客様の意向を選択",
    fmt(bg=LRED, fg=DRED, sz=8))
ws.write("H55","", inp(RED))
ws.data_validation("H55",{
    "validate":"list",
    "source":["はい（取り次ぎ確定）","再検討（3社比較に戻る）","見送り"],
    "dropdown":True
})

# ════════════════════════════════════════════════════════════════
#  意向と最終確認（行59〜61）
# ════════════════════════════════════════════════════════════════
ws.set_row(58, 22)
ws.set_row(59, 40)
ws.set_row(60, 5)

ws.merge_range("B59:H59",
    "  ■ 意向と最終選択の確認（契約前に必ず実施）",
    hdr(NAVY,WHITE,10))
final = (
    "「本日ご提案した○○（会社名）の○○プランは、先ほどお伺いしたご意向（○○を重視）に沿ったものです。"
    "ご確認いただけますか？」\n→ 異なる商品をご選択の場合は、右の欄にその理由を記録してください。"
)
ws.merge_range("D60:G60", final,
    fmt(bg=LBLUE, fg=NAVY, sz=9, ha="left", va="vcenter"))
ws.merge_range("B60:C60","📣 確認・記録",
    fmt(bg=NAVY, fg="#93B8DC", sz=8, bold=True, ha="center"))
ws.write("H60","", fmt(bg=YELLOW, fg=DARK, sz=9,
    top_c=NAVY, bot_c=NAVY, left_c=NAVY, right_c=NAVY,
    top_s=2, bot_s=2, left_s=2, right_s=2))

# ════════════════════════════════════════════════════════════════
#  メモ欄（行62〜68）
# ════════════════════════════════════════════════════════════════
ws.set_row(61, 20); ws.set_row(62, 75); ws.set_row(63, 5)
ws.set_row(64, 20); ws.set_row(65, 30); ws.set_row(66, 5)
ws.set_row(67, 18)

ws.merge_range("B62:H62","  📝 面談メモ・お客様の声", hdr(DARK,WHITE,10))
ws.merge_range("B63:H63","",
    fmt(bg=YELLOW, ha="left", va="top",
        top_c="#7A8575", bot_c="#7A8575", left_c="#7A8575", right_c="#7A8575",
        top_s=2, bot_s=2, left_s=2, right_s=2))
ws.merge_range("B65:H65","  📌 次回アクション", hdr(DARK,WHITE,10))
ws.merge_range("B66:H66","",
    fmt(bg=YELLOW, ha="left", va="top",
        top_c="#7A8575", bot_c="#7A8575", left_c="#7A8575", right_c="#7A8575",
        top_s=2, bot_s=2, left_s=2, right_s=2))
ws.merge_range("B68:H68",
    "  ＊本シートは2026年6月施行の改正保険業法（比較推奨規制、施行規則第227条の2）に基づく"
    "意向確認記録として活用してください。面談後は必ず保存・アーカイブをお願いします。",
    fmt(bg=NAVY, fg="#93B8DC", sz=7))

# ════════════════════════════════════════════════════════════════
#  Sheet2: 比較推奨チェックリスト
# ════════════════════════════════════════════════════════════════
ws2.set_column(0, 0, 3)
ws2.set_column(1, 1, 4)
ws2.set_column(2, 3, 33)
ws2.set_column(4, 6, 10)

ws2.set_row(0, 34)
ws2.merge_range("A1:G1",
    "  ■ 比較推奨チェックリスト（改正保険業法対応・金融庁指針準拠）",
    hdr(NAVY,WHITE,13))

ws2.set_row(1, 18)
ws2.merge_range("A2:G2",
    "  面談後に全項目を確認し、すべて「✅ 済」になっていることを確認してください。"
    "【根拠：2026年6月施行 改正保険業法施行規則第227条の2】",
    fmt(bg=DNAVY, fg="#C8D8F0", sz=8))

ws2.set_row(2, 18)
ws2.merge_range("C3:D3","  確認項目", hdr(DARK,GRAY1,8))
for i, lbl in enumerate(["SJ","MSI","TN"]):
    ws2.write(2, 4+i, lbl, hdr(DARK,GRAY1,8,ha="center"))

checklist = [
    ("① 事前確認（意向把握）", GREEN, [
        "お客様の意向（重視事項）を確認した",
        "補償内容の希望（車両保険・運転者範囲等）を確認した",
        "特定リスク把握（自転車事故・レッカー・あおり・当て逃げ）を確認した",
        "複数社（3社）の見積りを取得した",
        "各社の保険料・補償内容を比較説明した",
    ]),
    ("② 比較推奨の実施", DGRN, [
        "お客様の意向に照らして比較対象3社を選定し、選定理由を説明できる",
        "各社の特徴・強みをお客様の意向と紐づけて説明した",
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

row = 3
for section, color, items in checklist:
    ws2.set_row(row, 20)
    ws2.merge_range(row, 1, row, 6, f"  【 {section} 】",
        hdr(DARK,WHITE,9))
    row += 1
    for item in items:
        ws2.set_row(row, 20)
        ws2.write(row, 1, "▸", hdr(color,WHITE,9,ha="center"))
        ws2.merge_range(row, 2, row, 3, f"  {item}",
            fmt(bg="#FAFBFA", fg=NAVY, sz=9))
        for c in range(4, 7):
            ws2.write(row, c, "",
                fmt(bg=YELLOW, fg="#000000", bold=True, sz=11, ha="center",
                    top_c=color, bot_c=color, left_c=color, right_c=color,
                    top_s=2, bot_s=2, left_s=2, right_s=2))
            ws2.data_validation(row, c, row, c,
                {"validate":"list","source":["✅ 済","⬜ 未","N/A"],"dropdown":True})
        row += 1
    ws2.set_row(row, 4)
    row += 1

ws2.set_row(row, 18)
ws2.merge_range(row, 1, row, 6,
    "  ＊推奨根拠は必ず「顧客の意向との対応関係」で記録してください"
    "（2026年6月施行 改正保険業法施行規則第227条の2）。",
    fmt(bg=NAVY, fg="#93B8DC", sz=7))

wb.close()
print(f"Saved: {out}")
