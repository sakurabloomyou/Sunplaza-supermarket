"""
意向確認シート v7
・募集人が手元で使うスクリプト兼記録ツール
・お客様は見ない／お客様が書く欄は一切なし
・募集人がスクリプトを読み上げながら回答を記録する
"""
import xlsxwriter

out = "/home/user/Sunplaza-supermarket/intent_tool.xlsx"
wb  = xlsxwriter.Workbook(out)
ws  = wb.add_worksheet("意向確認シート")
ws2 = wb.add_worksheet("比較推奨チェックリスト")

# ── カラー ──────────────────────────────────────────────────────
NAVY="#1C3557"; DNAVY="#16304F"; RED="#C0392B"; DRED="#9B2335"
BLUE="#1B5EB5"; DBLUE="#2146A0"; GREEN="#2E7D5B"; DGRN="#1E6644"
LBLUE="#DCE8F9"; LGRN="#E0F0E8"; LRED="#FDECEA"; BG="#F2F5F1"
WHITE="#FFFFFF"; YELLOW="#FFFDE7"; LYELLOW="#FFF8E1"
GRAY1="#EAECE9"; GRAY2="#BFC5BB"; DARK="#404B3A"
ORANGE="#E67E22"; LORANGE="#FEF0E3"; DORG="#D35400"

# ── フォーマット ──────────────────────────────────────────────
def f(bg=None,fg="#000000",bold=False,sz=10,ha="left",va="vcenter",wrap=True,
      tc=None,bc=None,lc=None,rc=None,ts=None,bs=None,ls=None,rs=None):
    d={"font_name":"Meiryo UI","font_size":sz,"font_color":fg,"bold":bold,
       "align":ha,"valign":va,"text_wrap":wrap}
    if bg: d["bg_color"]=bg
    for side,col,sty in[("top",tc,ts),("bottom",bc,bs),("left",lc,ls),("right",rc,rs)]:
        if col: d[f"{side}_color"]=col
        if sty: d[f"{side}"]=sty
    return wb.add_format(d)

def hdr(bg,fg=WHITE,sz=10,bold=True,ha="left"):
    return f(bg=bg,fg=fg,sz=sz,bold=bold,ha=ha,wrap=True)

def script_fmt(bg=LBLUE):
    return f(bg=bg,fg=NAVY,sz=9,ha="left",va="vcenter",wrap=True,
             tc=GRAY2,bc=GRAY2,lc=GRAY2,rc=GRAY2,ts=1,bs=1,ls=1,rs=1)

def rec(border_color=GREEN):
    """募集人が記録する入力セル"""
    return f(bg=YELLOW,fg=NAVY,bold=True,sz=11,ha="center",va="vcenter",wrap=False,
             tc=border_color,bc=border_color,lc=border_color,rc=border_color,
             ts=2,bs=2,ls=2,rs=2)

def note_fmt(bg="#F8FFF9"):
    return f(bg=bg,fg=DARK,sz=7.5,ha="left",va="vcenter",wrap=True,
             tc=GRAY2,bc=GRAY2,lc=GRAY2,rc=GRAY2,ts=1,bs=1,ls=1,rs=1)

def body(bg,fg=DARK,sz=9):
    return f(bg=bg,fg=fg,sz=sz,ha="left",va="vcenter",wrap=True,
             tc=GRAY2,bc=GRAY2,lc=GRAY2,rc=GRAY2,ts=1,bs=1,ls=1,rs=1)

# ── 列幅 ──────────────────────────────────────────────────────
ws.set_column(0,0,2.5)  # A
ws.set_column(1,1,3)    # B
ws.set_column(2,2,10)   # C
ws.set_column(3,3,42)   # D
ws.set_column(4,4,18)   # E
ws.set_column(5,5,20)   # F
ws.set_column(6,6,20)   # G
ws.set_column(7,7,16)   # H

# ────────────────────────────────────────────────────────────────
#  ヘッダー
# ────────────────────────────────────────────────────────────────
ws.set_row(0, 38)
ws.merge_range("A1:H1",
    "  ■ 自動車保険  意向確認シート（募集人スクリプト・記録用）  改正保険業法対応版",
    hdr(NAVY,WHITE,12))

ws.set_row(1, 18)
ws.merge_range("A2:H2",
    "  【使い方】太字スクリプトを読み上げ、お客様の回答を黄色セルに記録してください。"
    "　STEP2は契約方法選択後、左端の ＋ で展開。　【2026年6月施行 改正保険業法対応】",
    f(bg=DNAVY,fg="#C8D8F0",sz=8))

ws.set_row(2, 5)
ws.set_row(3, 20)
ws.set_row(4, 22)
ws.set_row(5, 5)

for i,lbl in enumerate(["日　付","担当者名","お客様名","支　店"]):
    ws.write(3,2+i, lbl, hdr(NAVY,WHITE,8,ha="center"))
    ws.write(4,2+i, "",  rec(GRAY2))

# ────────────────────────────────────────────────────────────────
#  STEP 1
# ────────────────────────────────────────────────────────────────
ws.set_row(6, 22)
ws.set_row(7, 60)
ws.set_row(8, 75)
ws.set_row(9, 28)
ws.set_row(10,20); ws.set_row(11,20); ws.set_row(12,20)
ws.set_row(13, 5)

ws.merge_range("B7:H7","  STEP 1　　はじめに・ご契約方法の確認", hdr(BLUE,WHITE,11))

ws.merge_range("B8:C8","■ 読み上げ①\n（開始前）", hdr(DBLUE,"#C5D8F5",8,ha="center"))
ws.merge_range("D8:H8",
    "「本日は自動車保険のご案内をいたします。当社では複数の保険会社の商品を取り扱っており、"
    "お客様のご意向・ご状況に合った保険をご提案するために、まずいくつかお伺いします。"
    "ご確認いただいた内容は意向確認の記録として残させていただきます。よろしいですか？」\n"
    "（根拠：保険業法第294条の3・2026年6月施行 改正保険業法施行規則第227条の2）",
    script_fmt(LBLUE))

ws.merge_range("B9:C9","■ 読み上げ②\n（契約方法）", hdr(DBLUE,"#C5D8F5",8,ha="center"))
ws.merge_range("D9:H9",
    "「当社では給与天引き（団体割引）が使える 損保ジャパン・三井住友海上・東京海上 の3社、"
    "通販型のソニー損保へのお取り次ぎ、クレカ・口振の一般契約もご案内できます。\n"
    "どのご契約方法をご希望ですか？」",
    script_fmt("#EBF2FC"))

# H10: 契約方法記録セル
ws.merge_range("B10:F10",
    "  ▶ 【記録】お客様のご希望の契約方法を選択してください",
    f(bg=LYELLOW,fg=RED,sz=9,bold=True,wrap=False))
ws.write("G10","記録 →", hdr(RED,WHITE,8,ha="center"))
ws.write("H10","", rec(RED))
ws.data_validation("H10",{
    "validate":"list",
    "source":["①給与天引き（団体割引）","②一般契約（クレカ・口振）","③通販型（ソニー損保）"],
    "dropdown":True
})

choices=[
    (10,"①","給与天引き（団体割引）", "→ STEP2グループ「①②」を展開して続けてください",GREEN,LGRN),
    (11,"②","一般契約（クレカ・口振）","→ STEP2グループ「①②」を展開して続けてください",BLUE, LBLUE),
    (12,"③","通販型（ソニー損保）",   "→ STEP2グループ「③」を展開して続けてください", RED,  LRED),
]
for row,num,label,guide,hc,bc in choices:
    ws.write(row,1, num,   hdr(hc,WHITE,9,ha="center"))
    ws.write(row,2, label, f(bg=bc,fg=hc,sz=9,bold=True))
    ws.merge_range(row,3,row,7, guide, f(bg=bc,fg=DARK,sz=8))

ws.set_row(14, 24)
ws.merge_range("B15:E15","  ▼ ①② 給与天引き・一般契約 ─── ＋ で展開",
    f(bg=LGRN,fg=GREEN,sz=9,bold=True))
ws.merge_range("F15:H15","  ▼ ③ 通販型 ─── ＋ で展開",
    f(bg=LRED,fg=RED,sz=9,bold=True))

# ────────────────────────────────────────────────────────────────
#  STEP 2①②（行16〜46）level=1 hidden
# ────────────────────────────────────────────────────────────────
G1H = {"level":1,"hidden":True}

ws.set_row(15,22,None,G1H)
ws.set_row(16,18,None,G1H)
ws.set_row(17,60,None,G1H)
ws.set_row(18,20,None,G1H)
for r in range(19,24): ws.set_row(r,22,None,G1H)
ws.set_row(24, 5,None,G1H)
ws.set_row(25,20,None,G1H)
for r in range(26,29): ws.set_row(r,22,None,G1H)
ws.set_row(29, 5,None,G1H)
ws.set_row(30,20,None,G1H)
ws.set_row(31,18,None,G1H)
for r in range(32,36): ws.set_row(r,22,None,G1H)
ws.set_row(35, 5,None,G1H)
ws.set_row(36,22,None,G1H)
ws.set_row(37,20,None,G1H)
ws.set_row(38,70,None,G1H)
ws.set_row(39,20,None,G1H)
for r in range(40,43): ws.set_row(r,50,None,G1H)
ws.set_row(43,24,None,G1H)
ws.set_row(44, 5,None,G1H)
ws.set_row(45, 5,None,G1H)

ws.merge_range("B16:H16",
    "  STEP 2　　意向把握・補償確認・リスク把握　（給与天引き・一般契約）",
    hdr(GREEN,WHITE,11))

# スクリプト
ws.merge_range("B17:C17","■ 読み上げ③\n（意向把握）", hdr(DGRN,"#B8DEC9",8,ha="center"))
ws.merge_range("D17:H17","",hdr(DGRN,"#B8DEC9",8))

ws.merge_range("D18:H18",
    "「いくつかお伺いしてもよいでしょうか。自動車保険でいちばん大切にされていることを教えてください。"
    "重視される項目があれば、右の欄に記録させていただきます。」",
    script_fmt("#EDF7F2"))
ws.merge_range("B18:C18","■ 読み上げ", f(bg=LGRN,fg=DGRN,sz=8,bold=True,ha="center"))

# 重視事項ヘッダー
ws.merge_range("B19:C19","重視事項\n（担当者が記録）", hdr(DGRN,"#B8DEC9",8,ha="center"))
ws.merge_range("D19:F19","確認内容",           hdr(DGRN,"#B8DEC9",8,ha="center"))
ws.merge_range("G19:H19","各社の強み（参考）", hdr(DGRN,"#B8DEC9",8,ha="center"))

prio_items=[
    ("保険料をできるだけ抑えたい",         "損保ジャパン（多様なプラン）／三井住友海上（ネット割引）"),
    ("補償をしっかり充実させたい",         "東京海上（総合型・特約充実）／損保ジャパン（幅広い特約）"),
    ("事故時の対応・サポートを重視したい", "三井住友海上（示談交渉◎）／東京海上（専任担当）"),
    ("手続きが簡単・わかりやすいものがいい","三井住友海上（シンプル設計）"),
    ("担当者に相談しながら決めたい",       "3社すべて対応可"),
]
for i,(item,note) in enumerate(prio_items):
    r=19+i
    ws.write(r,1, f"  {chr(9312+i)}", hdr(GREEN,WHITE,10,ha="center"))
    ws.merge_range(r,2,r,5, f"  {item}", body(LGRN,NAVY,9))
    ws.write(r,6, f"  {note}", note_fmt())
    ws.write(r,7, "", rec(GREEN))
    ws.data_validation(r,7,r,7,{"validate":"list","source":["○","−"],"dropdown":True})

# 補償内容確認
ws.merge_range("B26:H26","  補償内容の確認（意向把握の必須事項）", hdr(DGRN,WHITE,9))

cov_items=[
    ("車両保険の加入希望",  ["ご希望あり","検討中","不要"],
     "車両保険あり・なしで保険料が大きく変わります"),
    ("運転者の範囲",        ["本人のみ","家族限定","限定なし"],
     "限定なしは保険料が高くなる場合があります"),
    ("年間走行距離の目安",  ["5000km未満","〜10000km","10000km超"],
     "距離が多いほどリスクが高まる場合があります"),
]
for i,(label,src,note) in enumerate(cov_items):
    r=26+i
    ws.write(r,1, f"  {chr(9317+i)}", hdr(DGRN,WHITE,9,ha="center"))
    ws.merge_range(r,2,r,4, f"  {label}", body(LGRN,NAVY,9))
    ws.merge_range(r,5,r,6, f"  {note}",  note_fmt())
    ws.write(r,7, "", rec(DGRN))
    ws.data_validation(r,7,r,7,{"validate":"list","source":src,"dropdown":True})

# 特定リスク把握
ws.set_row(30,20,None,G1H)
ws.merge_range("B31:H31",
    "  特定リスク把握　　お客様が気にされているリスクを確認・記録してください（LP Step4対応）",
    hdr(ORANGE,WHITE,9))

ws.merge_range("B32:C32","確認項目", hdr(DORG,"#FFE0C0",8,ha="center"))
ws.merge_range("D32:F32","リスク内容",           hdr(DORG,"#FFE0C0",8,ha="center"))
ws.merge_range("G32:H32","対応する補償・特約",   hdr(DORG,"#FFE0C0",8,ha="center"))

risk_items=[
    ("R1 自転車・歩行者との事故",   "対人賠償保険（無制限推奨）／個人賠償責任特約"),
    ("R2 故障・レッカー手配",       "ロードサービス（搬送距離・回数を各社比較）"),
    ("R3 あおり運転・危険運転被害", "弁護士費用特約（法的対応費用をカバー）"),
    ("R4 当て逃げ・駐車場トラブル", "車両保険エコノミー型（当て逃げ補償）"),
]
for i,(risk,cov) in enumerate(risk_items):
    r=32+i
    ws.write(r,1, f"  {risk[:2]}", hdr(ORANGE,WHITE,9,ha="center"))
    ws.merge_range(r,2,r,5, f"  {risk[3:]}", body(LORANGE,NAVY,9))
    ws.write(r,6, f"  {cov}", note_fmt("#FFF8F0"))
    ws.write(r,7, "", rec(ORANGE))
    ws.data_validation(r,7,r,7,{"validate":"list",
        "source":["○ 気になる","− 特になし"],"dropdown":True})

# 3社比較
ws.merge_range("B37:H37",
    "  STEP 2-2　　3社ご提案　（意向把握結果をふまえてお見積りをご提示）",
    hdr(DGRN,WHITE,11))

ws.merge_range("B38:C38","■ 読み上げ④\n＋募集人メモ", hdr(DGRN,"#B8DEC9",8,ha="center"))
ws.merge_range("D38:H38",
    "「ありがとうございます。いただいたご意向をもとに3社でお見積りをご用意します。\n"
    "─── 募集人確認メモ ───────────────────────────────\n"
    "・保険料重視 → 三井住友海上のシンプルプラン／損保ジャパンのネット割引\n"
    "・補償充実重視 → 東京海上の総合型／損保ジャパンの特約構成\n"
    "・事故対応重視 → 三井住友海上の示談交渉サービス／東京海上の専任担当制度\n"
    "必ず3社のお見積りをご提示のうえ、推奨理由をご説明ください。」",
    script_fmt("#EDF7F2"))

ws.merge_range("B39:C39","会社・商品名",         hdr(DARK,GRAY1,8,ha="center"))
ws.merge_range("D39:E39","主な強み・固有特約",    hdr(DARK,GRAY1,8,ha="center"))
ws.merge_range("F39:G39","顧客への説明ポイント",  hdr(DARK,GRAY1,8,ha="center"))
ws.write("H39","提案記録", hdr(DARK,GRAY1,7,ha="center"))

companies=[
    (RED,  LRED,
     "損保ジャパン\n「THEクルマの保険」",
     "・つながるドラレコ（安全運転スコア割引 最大20%）\n・故障運搬時車両損害特約（最大30万円）\n・代車費用特約（30日型）",
     "取引歴が長く特約の選択肢が豊富。ドラレコ割引で保険料を抑えたい方に。"),
    (GREEN,LGRN,
     "三井住友海上\n「GKクルマの保険」",
     "・プレミアムドラレコ（360°全方位・AI事故状況分析）\n・雹災緊急アラート（業界唯一）\n・LINE連携で手続き完結",
     "シンプル設計で手続き楽々。保険料重視・手続き簡便を求める方に。"),
    (BLUE, LBLUE,
     "東京海上日動\n「トータルアシスト」",
     "・DAP（ドライブエージェントパーソナル）\n・入院時選べるアシスト特約（自動付帯）\n・エコノミー型（当て逃げ補償あり）",
     "業界最大手の手厚い補償。事故後サポート・補償充実を重視する方に。"),
]
dv_prop=["◎提案する","○提案する","△保留","×見送り"]
for i,(hc,bc,nm,feat,tip) in enumerate(companies):
    r=40+i
    ws.merge_range(r,1,r,2, nm,
        f(bg=hc,fg=WHITE,sz=9,bold=True,ha="center",va="vcenter",wrap=True,
          tc=hc,bc=hc,lc=hc,rc=hc,ts=1,bs=1,ls=1,rs=1))
    ws.merge_range(r,3,r,4, feat,
        f(bg=bc,fg=DARK,sz=8,ha="left",va="top",wrap=True,
          tc=GRAY2,bc=GRAY2,lc=GRAY2,rc=GRAY2,ts=1,bs=1,ls=1,rs=1))
    ws.merge_range(r,5,r,6, tip,
        f(bg=WHITE,fg="#2A3328",sz=8,ha="left",va="top",wrap=True,
          tc=GRAY2,bc=GRAY2,lc=GRAY2,rc=GRAY2,ts=1,bs=1,ls=1,rs=1))
    ws.write(r,7,"", rec(hc))
    ws.data_validation(r,7,r,7,{"validate":"list","source":dv_prop,"dropdown":True})

# 推奨根拠記録（募集人が記録）
ws.merge_range("B44:D44","  📝 推奨根拠の記録（比較推奨規制・必須）", hdr(DNAVY,WHITE,9))
ws.merge_range("E44:F44","上記ご意向（              ）に照らし、",
    f(bg=LBLUE,fg=NAVY,sz=9,wrap=False))
ws.write("G44","推奨会社 →", hdr(NAVY,WHITE,8,ha="center"))
ws.write("H44","", rec(NAVY))
ws.data_validation("H44",{"validate":"list",
    "source":["損保ジャパン","三井住友海上","東京海上日動","お客様意向で選択"],
    "dropdown":True})

# ────────────────────────────────────────────────────────────────
#  STEP 2③（行50〜56）level=1 hidden
# ────────────────────────────────────────────────────────────────
G1H2={"level":1,"hidden":True}
ws.set_row(49,22,None,G1H2); ws.set_row(50,18,None,G1H2)
ws.set_row(51,60,None,G1H2); ws.set_row(52,60,None,G1H2)
ws.set_row(53,22,None,G1H2); ws.set_row(54,22,None,G1H2)
ws.set_row(55, 5,None,G1H2)

ws.merge_range("B50:H50","  STEP 2　　ソニー損保ご案内　（通販型をご希望の方）",
    hdr(RED,WHITE,11))
ws.merge_range("B51:C51","■ 読み上げ③\n（通販型）", hdr(DRED,"#F5C0BB",8,ha="center"))
ws.merge_range("D51:H51","",hdr(DRED,"#F5C0BB",8))

ws.merge_range("D52:H52",
    "「ソニー損保はお客様ご自身がインターネットで直接ご契約いただく通販型です。"
    "当社（代理店）が契約を代理するものではなく、申込・告知内容はお客様ご自身でご入力・ご確認いただきます。"
    "手続きはお客様側のご対応となりますが、よろしいでしょうか？」",
    script_fmt("#FEF5F4"))
ws.merge_range("B52:C52","■ 読み上げ③\n（案内）",
    f(bg=LRED,fg=RED,sz=8,bold=True,ha="center"))

ws.merge_range("D53:H53",
    "「事故時のサポートはソニー損保のコールセンター対応が基本となり、"
    "当社担当者が直接サポートすることは難しくなります。"
    "この点をご了解いただいたうえでご希望ですか？」",
    script_fmt("#FEF5F4"))
ws.merge_range("B53:C53","■ 読み上げ④\n（留意事項）",
    f(bg=LRED,fg=RED,sz=8,bold=True,ha="center"))

ws.merge_range("B54:C54","【記録】意向確認", hdr(DRED,"#F5C0BB",8,ha="center"))
ws.merge_range("D54:F54","通販型の特性（直接契約・コールセンター）をご説明済み。お客様の意向：",
    f(bg=LRED,fg=DARK,sz=8,wrap=True))
ws.write("G54","意向記録 →", hdr(DRED,WHITE,7,ha="center"))
ws.write("H54","", rec(RED))
ws.data_validation("H54",{"validate":"list",
    "source":["ソニー損保を希望","3社比較に戻る","見送り"],"dropdown":True})

# ────────────────────────────────────────────────────────────────
#  常時表示（行58〜）
# ────────────────────────────────────────────────────────────────
ws.set_row(57,22); ws.set_row(58,45); ws.set_row(59,5)

ws.merge_range("B58:H58",
    "  ■ 意向と最終選択の確認（契約前に必ず実施・記録）", hdr(NAVY,WHITE,10))
ws.merge_range("B59:C59","■ 読み上げ⑤\n（最終確認）",
    f(bg=NAVY,fg="#93B8DC",sz=8,bold=True,ha="center"))
ws.merge_range("D59:G59",
    "「本日ご提案した○○（会社名）の○○プランは、先ほどお伺いしたご意向（○○を重視）"
    "に沿ったものです。ご確認いただけますか？」\n"
    "→ 意向と異なる商品を選択された場合は、右欄にその理由を記録してください。",
    script_fmt(LBLUE))
ws.write("H59","",
    f(bg=YELLOW,fg=DARK,sz=9,ha="left",va="top",wrap=True,
      tc=NAVY,bc=NAVY,lc=NAVY,rc=NAVY,ts=2,bs=2,ls=2,rs=2))

ws.set_row(60,5)
ws.set_row(61,20); ws.set_row(62,75); ws.set_row(63,5)
ws.set_row(64,20); ws.set_row(65,32); ws.set_row(66,5)
ws.set_row(67,18)

ws.merge_range("B62:H62","  📝 面談メモ・お客様の声（担当者メモ欄）", hdr(DARK,WHITE,10))
ws.merge_range("B63:H63","",
    f(bg=YELLOW,ha="left",va="top",wrap=True,
      tc="#7A8575",bc="#7A8575",lc="#7A8575",rc="#7A8575",ts=2,bs=2,ls=2,rs=2))

ws.merge_range("B65:H65","  📌 次回アクション（担当者メモ欄）", hdr(DARK,WHITE,10))
ws.merge_range("B66:H66","",
    f(bg=YELLOW,ha="left",va="top",wrap=True,
      tc="#7A8575",bc="#7A8575",lc="#7A8575",rc="#7A8575",ts=2,bs=2,ls=2,rs=2))

ws.merge_range("B68:H68",
    "  ＊本シートは2026年6月施行の改正保険業法（比較推奨規制・施行規則第227条の2）に基づく"
    "意向確認記録です。面談後は必ず保存・アーカイブをお願いします。",
    f(bg=NAVY,fg="#93B8DC",sz=7))

# ────────────────────────────────────────────────────────────────
#  Sheet2: 比較推奨チェックリスト
# ────────────────────────────────────────────────────────────────
ws2.set_column(0,0,3); ws2.set_column(1,1,4)
ws2.set_column(2,3,34); ws2.set_column(4,6,10)

ws2.set_row(0,34)
ws2.merge_range("A1:G1",
    "  ■ 比較推奨チェックリスト（改正保険業法対応・金融庁指針準拠）",
    hdr(NAVY,WHITE,13))
ws2.set_row(1,18)
ws2.merge_range("A2:G2",
    "  面談後に全項目を確認し、すべて「✅ 済」になっていることを確認してください。"
    "【根拠：2026年6月施行 改正保険業法施行規則第227条の2】",
    f(bg=DNAVY,fg="#C8D8F0",sz=8))

ws2.set_row(2,18)
ws2.merge_range("C3:D3","  確認項目", hdr(DARK,GRAY1,8))
for i,lbl in enumerate(["SJ","MSI","TN"]):
    ws2.write(2,4+i, lbl, hdr(DARK,GRAY1,8,ha="center"))

checklist=[
    ("① 事前確認（意向把握）",GREEN,[
        "お客様の意向（重視事項）を確認・記録した",
        "補償内容の希望（車両保険・運転者範囲等）を確認・記録した",
        "特定リスク把握（自転車事故・レッカー・あおり・当て逃げ）を確認した",
        "複数社（3社）の見積りを取得した",
        "各社の保険料・補償内容を比較説明した",
    ]),
    ("② 比較推奨の実施",DGRN,[
        "お客様の意向に照らして比較対象3社を選定し、選定理由を説明できる",
        "各社の特徴・強みをお客様の意向と紐づけて説明した",
        "商品名・固有特約レベルで3社の違いを説明した",
    ]),
    ("③ 推奨根拠の記録",BLUE,[
        "推奨する会社・商品とその理由を本シートに記録した",
        "お客様が選んだ会社・商品を記録した",
        "意向と異なる商品を選択した場合、その理由を確認・記録した",
    ]),
    ("④ コンプライアンス確認",RED,[
        "特定会社への一方的な誘導はなく、公平な比較を実施した",
        "3社のお見積りをすべてお客様にご提示した",
        "推奨内容がお客様の意向に沿うことを口頭で確認した",
        "本シートを保管・アーカイブ予定（施行規則第227条の2）",
    ]),
]

row=3
for section,color,items in checklist:
    ws2.set_row(row,20)
    ws2.merge_range(row,1,row,6,f"  【 {section} 】",hdr(DARK,WHITE,9))
    row+=1
    for item in items:
        ws2.set_row(row,20)
        ws2.write(row,1,"▸",hdr(color,WHITE,9,ha="center"))
        ws2.merge_range(row,2,row,3,f"  {item}",
            f(bg="#FAFBFA",fg=NAVY,sz=9,tc=GRAY2,bc=GRAY2,lc=GRAY2,rc=GRAY2,
              ts=1,bs=1,ls=1,rs=1))
        for c in range(4,7):
            ws2.write(row,c,"",
                f(bg=YELLOW,fg="#000000",bold=True,sz=11,ha="center",
                  tc=color,bc=color,lc=color,rc=color,ts=2,bs=2,ls=2,rs=2))
            ws2.data_validation(row,c,row,c,
                {"validate":"list","source":["✅ 済","⬜ 未","N/A"],"dropdown":True})
        row+=1
    ws2.set_row(row,4); row+=1

ws2.set_row(row,18)
ws2.merge_range(row,1,row,6,
    "  ＊推奨根拠は必ず「顧客の意向との対応関係」で記録してください"
    "（2026年6月施行 改正保険業法施行規則第227条の2）。",
    f(bg=NAVY,fg="#93B8DC",sz=7))

wb.close()
print(f"Saved: {out}")
