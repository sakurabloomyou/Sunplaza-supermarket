"""
サンプラザ ひだまり通信 — リデザイン版（ブランドカラー準拠・主婦向けマガジンスタイル）
Sunplaza Brand Green テーマ × 女性誌風レイアウト
"""

from pptx import Presentation
from pptx.util import Cm, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
import math

# ─── サンプラザ ブランドカラー（公式サイト準拠：緑地に白字）────────
SP_GREEN       = RGBColor(0x1A, 0x7A, 0x3C)   # サンプラザ ブランドグリーン（メイン）
SP_GREEN_DARK  = RGBColor(0x0F, 0x52, 0x28)   # ダークグリーン（見出し・アクセント）
SP_GREEN_LIGHT = RGBColor(0xD8, 0xF0, 0xE3)   # ライトグリーン（背景帯）
SP_GREEN_MID   = RGBColor(0x4C, 0xAA, 0x6E)   # ミッドグリーン（装飾）

# ─── 主婦層向けアクセントカラー ────────────────────────────────────
SAKURA_PINK    = RGBColor(0xF4, 0x8F, 0xB1)   # 桜ピンク（柔らかい女性向け）
LIGHT_PINK     = RGBColor(0xFD, 0xE8, 0xF0)   # 淡ピンク（背景）
PEACH          = RGBColor(0xFF, 0xAB, 0x76)   # ピーチオレンジ（旧ブランド色ニュアンス）
LIGHT_PEACH    = RGBColor(0xFF, 0xED, 0xDE)   # 淡ピーチ（背景）
SUNNY_YELLOW   = RGBColor(0xFF, 0xE0, 0x52)   # サンシャインイエロー
LIGHT_YELLOW   = RGBColor(0xFF, 0xF8, 0xDC)   # 淡イエロー（背景）
LAVENDER       = RGBColor(0xB3, 0x9D, 0xDB)   # ラベンダー（知恵コーナー）
LIGHT_LAVENDER = RGBColor(0xEE, 0xE8, 0xF8)   # 淡ラベンダー（背景）

# ─── ベース・テキストカラー ────────────────────────────────────────
CREAM          = RGBColor(0xFF, 0xFA, 0xF3)   # クリーム背景
WHITE          = RGBColor(0xFF, 0xFF, 0xFF)
DARK_CHARCOAL  = RGBColor(0x2C, 0x2C, 0x2C)   # 本文テキスト
MID_GRAY       = RGBColor(0x88, 0x88, 0x88)   # サブテキスト
LIGHT_GRAY     = RGBColor(0xF0, 0xF0, 0xF0)   # プレースホルダー

# ─── ヘルパー ──────────────────────────────────────────────────────

def set_bg(slide, color):
    fill = slide.background.fill
    fill.solid()
    fill.fore_color.rgb = color

def rect(slide, x, y, w, h, fill, line=None, lw=Pt(0)):
    s = slide.shapes.add_shape(1, x, y, w, h)
    s.fill.solid(); s.fill.fore_color.rgb = fill
    if line:
        s.line.color.rgb = line; s.line.width = lw
    else:
        s.line.fill.background()
    return s

def rrect(slide, x, y, w, h, fill, adj=0.05):
    s = slide.shapes.add_shape(5, x, y, w, h)
    s.fill.solid(); s.fill.fore_color.rgb = fill
    s.line.fill.background()
    try: s.adjustments[0] = adj
    except: pass
    return s

def tb(slide, x, y, w, h, text, sz=Pt(10), bold=False,
        color=DARK_CHARCOAL, align=PP_ALIGN.LEFT, italic=False, font="メイリオ"):
    tx = slide.shapes.add_textbox(x, y, w, h)
    tf = tx.text_frame; tf.word_wrap = True
    p = tf.paragraphs[0]; p.alignment = align
    p.text = text
    r = p.runs[0]
    r.font.size = sz; r.font.bold = bold; r.font.italic = italic
    r.font.color.rgb = color; r.font.name = font
    return tx

def mtb(slide, x, y, w, h, lines, sz=Pt(9.5), color=DARK_CHARCOAL,
        align=PP_ALIGN.LEFT, bold_first=False, spacing=None):
    tx = slide.shapes.add_textbox(x, y, w, h)
    tf = tx.text_frame; tf.word_wrap = True
    for i, line in enumerate(lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        r = p.add_run(); r.text = line
        r.font.size = sz; r.font.color.rgb = color; r.font.name = "メイリオ"
        r.font.bold = (bold_first and i == 0)
        if spacing and i > 0:
            p.space_before = spacing
    return tx

def photo_box(slide, x, y, w, h, caption="写真", icon="📷"):
    rect(slide, x, y, w, h, LIGHT_GRAY, MID_GRAY, Pt(1))
    tb(slide, x, y + h/2 - Cm(0.6), w, Cm(1.2),
       f"{icon}\n{caption}", sz=Pt(8.5), color=MID_GRAY,
       align=PP_ALIGN.CENTER)

def section_banner(slide, x, y, w, h, text, icon,
                   bg=SP_GREEN, fg=WHITE, sub=None):
    """マガジン風セクションバナー（左にアイコン丸）"""
    # 背景バー
    rrect(slide, x, y, w, h, bg, adj=0.04)
    # アイコン丸
    circle = slide.shapes.add_shape(9, x + Cm(0.25), y + Cm(0.1),
                                     h - Cm(0.2), h - Cm(0.2))
    circle.fill.solid(); circle.fill.fore_color.rgb = WHITE
    circle.line.fill.background()
    tb(slide, x + Cm(0.2), y + Cm(0.05),
       h, h - Cm(0.1), icon, sz=Pt(14), align=PP_ALIGN.CENTER)
    # タイトル
    tb(slide, x + h + Cm(0.3), y + Cm(0.1),
       w - h - Cm(0.5), h - Cm(0.2),
       text, sz=Pt(13), bold=True, color=fg)
    if sub:
        tb(slide, x + h + Cm(0.3), y + h * 0.55,
           w - h - Cm(0.5), h * 0.5,
           sub, sz=Pt(8.5), color=fg, italic=True)

def leaf_deco(slide, positions, color=SP_GREEN_MID, sz=Pt(16)):
    for (x, y) in positions:
        tb(slide, x, y, Cm(1), Cm(1), "🌿", sz=sz,
           color=color, align=PP_ALIGN.CENTER)

def diamond_divider(slide, y, color=SP_GREEN_LIGHT):
    rect(slide, Cm(0.8), y, Cm(19.4), Cm(0.06), color)
    # 小ダイヤモンド中央
    tb(slide, Cm(9.5), y - Cm(0.25), Cm(2), Cm(0.5),
       "✦", sz=Pt(10), color=SP_GREEN, align=PP_ALIGN.CENTER)

# ─── プレゼンテーション ────────────────────────────────────────────

prs = Presentation()
prs.slide_width  = Cm(21.0)
prs.slide_height = Cm(29.7)
blank = prs.slide_layouts[6]


# ════════════════════════════════════════════════════════
# PAGE 1 — 表紙  （ブランドグリーン × 桜ピンク × クリーム）
# ════════════════════════════════════════════════════════
s1 = prs.slides.add_slide(blank)
set_bg(s1, CREAM)

# ── 上部ブランドグリーン帯（ロゴエリア）
rect(s1, Cm(0), Cm(0), Cm(21), Cm(4.5), SP_GREEN)

# ── ロゴエリア：「スーパーサンプラザ」
tb(s1, Cm(0.8), Cm(0.2), Cm(19.4), Cm(1.2),
   "スーパーサンプラザ", sz=Pt(14), bold=False, color=RGBColor(0xC8,0xFF,0xD4))

# ── 大タイトル「ひだまり通信」
tb(s1, Cm(0.5), Cm(0.9), Cm(20), Cm(2.5),
   "ひだまり通信", sz=Pt(44), bold=True, color=WHITE,
   align=PP_ALIGN.CENTER, font="メイリオ")

# ── 緑帯内タグライン
tb(s1, Cm(0.5), Cm(3.35), Cm(20), Cm(0.8),
   "〜 働くみんなの笑顔をつなぐ社内報 〜",
   sz=Pt(10.5), color=SP_GREEN_LIGHT, align=PP_ALIGN.CENTER, italic=True)

# ── 号数リボン（グリーン帯の下縁に重なる）
rrect(s1, Cm(5.5), Cm(4.0), Cm(10), Cm(1.1), SUNNY_YELLOW)
tb(s1, Cm(5.5), Cm(4.05), Cm(10), Cm(1.0),
   "創刊号  Vol.1  ✦  2026年6月号",
   sz=Pt(13), bold=True, color=SP_GREEN_DARK, align=PP_ALIGN.CENTER)

# ── 葉っぱデコ（タイトル周辺）
leaf_deco(s1, [(Cm(1.0), Cm(1.2)), (Cm(18.0), Cm(1.2)),
               (Cm(2.0), Cm(3.0)), (Cm(17.0), Cm(3.0))],
          RGBColor(0xA8,0xFF,0xC0), sz=Pt(20))

# ── メインビジュアルエリア（白カード）
rrect(s1, Cm(1.0), Cm(5.4), Cm(19.0), Cm(9.8), WHITE)
photo_box(s1, Cm(1.3), Cm(5.7), Cm(18.4), Cm(6.2),
          "表紙メインビジュアル\n（従業員笑顔の集合写真 / ひまわり × 野菜モチーフなど）",
          "🌻")

# ── ミニイラストライン
tb(s1, Cm(1.3), Cm(12.1), Cm(18.4), Cm(0.9),
   "🌿  🌸  ☀️  🌿  🌼  🌿  ☀️  🌸  🌿",
   sz=Pt(16), color=SP_GREEN, align=PP_ALIGN.CENTER)

# ── キャッチコピー
rrect(s1, Cm(1.3), Cm(13.1), Cm(18.4), Cm(1.9), SP_GREEN_LIGHT)
tb(s1, Cm(1.5), Cm(13.15), Cm(18.0), Cm(1.8),
   "みんなで作る、みんなが主役の社内報です！\n"
   "投稿・エピソード随時大募集中  ✉️  総務部まで",
   sz=Pt(10.5), color=SP_GREEN_DARK, align=PP_ALIGN.CENTER)

# ── ティーザー3点（カード型）
teasers = [
    (SP_GREEN,     "🏔",  "P.2",  "堺東駅前店の\n職場自慢！"),
    (PEACH,        "🍳",  "P.3",  "唐揚げで\n親子丼レシピ"),
    (SAKURA_PINK,  "💬",  "P.4",  "わたしの独り言 &\nお誕生日スタッフ"),
]
for i, (col, icon, page, txt) in enumerate(teasers):
    tx = Cm(1.0) + i * Cm(6.5)
    rrect(s1, tx, Cm(15.3), Cm(6.0), Cm(4.5), col, adj=0.07)
    tb(s1, tx, Cm(15.5), Cm(6.0), Cm(1.2), icon,
       sz=Pt(22), color=WHITE, align=PP_ALIGN.CENTER)
    tb(s1, tx + Cm(0.2), Cm(16.7), Cm(5.6), Cm(0.7), page,
       sz=Pt(10), bold=True, color=WHITE, align=PP_ALIGN.CENTER)
    tb(s1, tx + Cm(0.2), Cm(17.4), Cm(5.6), Cm(2.0), txt,
       sz=Pt(11.5), bold=True, color=WHITE, align=PP_ALIGN.CENTER)

# ── フッター（グリーン）
rect(s1, Cm(0), Cm(28.0), Cm(21), Cm(1.7), SP_GREEN_DARK)
tb(s1, Cm(0.5), Cm(28.15), Cm(20), Cm(0.75),
   "発行：株式会社サンプラザ 総務部　　毎月1日発行",
   sz=Pt(9), color=WHITE, align=PP_ALIGN.CENTER)
tb(s1, Cm(0.5), Cm(28.85), Cm(20), Cm(0.7),
   "🌿  投稿はいつでも歓迎！みなさんの笑顔と声がこの社内報を作っています  🌿",
   sz=Pt(8.5), color=SP_GREEN_LIGHT, align=PP_ALIGN.CENTER)


# ════════════════════════════════════════════════════════
# PAGE 2 — 中面左（職場自慢 ＋ わたしの独り言）
# ════════════════════════════════════════════════════════
s2 = prs.slides.add_slide(blank)
set_bg(s2, CREAM)

# ── ページヘッダー
rect(s2, Cm(0), Cm(0), Cm(21), Cm(0.85), SP_GREEN)
tb(s2, Cm(0.7), Cm(0.07), Cm(15), Cm(0.72),
   "🌿  サンプラザ ひだまり通信  創刊号  2026年6月",
   sz=Pt(9), color=WHITE)
tb(s2, Cm(16.5), Cm(0.07), Cm(4.0), Cm(0.72),
   "P.2", sz=Pt(10), bold=True, color=WHITE, align=PP_ALIGN.RIGHT)

# ══ コーナー1：〇〇店の職場自慢！ ══════════════════════
section_banner(s2, Cm(0.7), Cm(1.1), Cm(19.6), Cm(1.15),
               "〇〇店の職場自慢！", "🏆", SP_GREEN)

# 特集ラベル
rrect(s2, Cm(0.7), Cm(2.45), Cm(19.6), Cm(0.75), SP_GREEN_LIGHT)
tb(s2, Cm(1.0), Cm(2.48), Cm(19.0), Cm(0.68),
   "今月の店 ▶  堺東駅前店  「みんなで葛城山ハイキング！」",
   sz=Pt(10.5), bold=True, color=SP_GREEN_DARK)

# 写真2枚（横並び）
photo_box(s2, Cm(0.7), Cm(3.35), Cm(9.3), Cm(5.2), "登山道でのスタッフ集合写真")
photo_box(s2, Cm(10.4), Cm(3.35), Cm(9.6), Cm(5.2), "山頂でのランチタイム風景")

# 本文
body1 = [
    "　先月の日曜日、堺東駅前店のスタッフ22名が葛城山（標高959m）への",
    "日帰りハイキングを敢行しました！",
    "",
    "　早朝7時、近鉄・富田林駅に集合。ロープウェイは使わず、登山道を",
    "徒歩でひたすら登ること2時間。途中、「山歩きが10年来の趣味！」と",
    "いうパートの荒木さん（67歳）が若手スタッフをスイスイ追い抜く場面",
    "に一同大爆笑！",
    "",
    "　山頂では副店長の村田さんが手作りのおにぎり20個を振る舞い、大好",
    "評。下山後は富田林の居酒屋で打ち上げ。「次は金剛山に挑戦しよう！」",
    "と早くも次回の計画が持ち上がっています。",
    "",
    '店長・西川さん談：「普段なかなか話せないスタッフ同士が仲よくなれ',
    'る最高の機会でした。来年も必ず行きます！」',
]
mtb(s2, Cm(0.7), Cm(8.7), Cm(19.6), Cm(5.0), body1, sz=Pt(9.5))

# ── 区切り
diamond_divider(s2, Cm(14.3))

# ══ コーナー2：わたしの独り言 ══════════════════════════
section_banner(s2, Cm(0.7), Cm(14.55), Cm(19.6), Cm(1.15),
               "わたしの独り言", "💬", SAKURA_PINK, WHITE,
               sub="三日市駅前店  青山 恵子さん（パート歴11年）")

# 写真（右）
photo_box(s2, Cm(14.5), Cm(15.9), Cm(5.8), Cm(4.5), "青山さん")

# 吹き出し風テキストエリア
rrect(s2, Cm(0.7), Cm(15.9), Cm(13.4), Cm(4.5), LIGHT_PINK, adj=0.06)
body2 = [
    "　うちのお店に、もう10年以上毎朝いらっしゃるお客様がいます。",
    "いつも必ず「お茶漬けのり」と「わかめスープ」を買って帰られます。",
    "",
    "　先日、そのお客様が珍しそうにお惣菜コーナーをながめておら",
    "れたので声をかけると、「今日は家内の誕生日なんや。何か喜ぶ",
    "もんないかな」とはにかんでおられました。",
    "",
    "　一緒にプリンとお刺身を選んで「ラッピングしてもらえますか」",
    "と。そのひとことにジーンとしてしまいました。長年連れ添った",
    "奥様を大切にされている姿が、なんとも素敵で……。",
    "この仕事が好きになった瞬間でした。",
]
mtb(s2, Cm(1.0), Cm(16.1), Cm(12.8), Cm(4.2), body2, sz=Pt(9.5))

# フッター
rect(s2, Cm(0), Cm(29.0), Cm(21), Cm(0.7), SP_GREEN_LIGHT)
tb(s2, Cm(0.5), Cm(29.05), Cm(20), Cm(0.62),
   "🌿  あなたの「ほっこりエピソード」もぜひ投稿してください！  🌿",
   sz=Pt(8.5), color=SP_GREEN_DARK, align=PP_ALIGN.CENTER)


# ════════════════════════════════════════════════════════
# PAGE 3 — 中面右（アレンジレシピ ＋ 郷土料理）
# ════════════════════════════════════════════════════════
s3 = prs.slides.add_slide(blank)
set_bg(s3, CREAM)

# ── ページヘッダー
rect(s3, Cm(0), Cm(0), Cm(21), Cm(0.85), SP_GREEN)
tb(s3, Cm(0.7), Cm(0.07), Cm(15), Cm(0.72),
   "🌿  サンプラザ ひだまり通信  創刊号  2026年6月",
   sz=Pt(9), color=WHITE)
tb(s3, Cm(16.5), Cm(0.07), Cm(4.0), Cm(0.72),
   "P.3", sz=Pt(10), bold=True, color=WHITE, align=PP_ALIGN.RIGHT)

# ══ コーナー3：アレンジレシピ ══════════════════════════
section_banner(s3, Cm(0.7), Cm(1.1), Cm(19.6), Cm(1.15),
               "サンプラザ商品でアレンジレシピ！", "🍳", PEACH, WHITE)

# 商品ラベル
rrect(s3, Cm(0.7), Cm(2.45), Cm(19.6), Cm(0.75), LIGHT_PEACH)
tb(s3, Cm(1.0), Cm(2.48), Cm(19.0), Cm(0.68),
   "使用商品 ▶  お惣菜「鶏の唐揚げ（にんにく醤油）」",
   sz=Pt(10.5), bold=True, color=PEACH)

# レシピタイトル
tb(s3, Cm(0.7), Cm(3.35), Cm(19.6), Cm(1.0),
   "唐揚げで作る！ふわとろ親子丼", sz=Pt(17), bold=True, color=SP_GREEN_DARK)
tb(s3, Cm(0.7), Cm(4.25), Cm(19.6), Cm(0.65),
   "時短10分  ✦  2人分  ✦  サンプラザの唐揚げがごちそう丼に早変わり！",
   sz=Pt(9), color=MID_GRAY, italic=True)

# 写真 + 材料（2カラム）
photo_box(s3, Cm(11.7), Cm(4.9), Cm(8.6), Cm(5.3), "完成写真", "🍲")

rrect(s3, Cm(0.7), Cm(4.9), Cm(10.6), Cm(5.3), WHITE, adj=0.04)
rect(s3, Cm(0.7), Cm(4.9), Cm(10.6), Cm(0.6), LIGHT_PEACH)
tb(s3, Cm(0.9), Cm(4.9), Cm(10.2), Cm(0.6),
   "材料（2人分）", sz=Pt(9.5), bold=True, color=PEACH)
ingr = [
    "・唐揚げ（サンプラザ惣菜）  8個",
    "・卵  3個       ・玉ねぎ（小）  1/2個",
    "・だし汁  150ml  ・みりん  大さじ2",
    "・醤油  大さじ1.5  ・砂糖  小さじ1",
    "・ご飯  2膳分   ・三つ葉  少々",
]
mtb(s3, Cm(0.9), Cm(5.55), Cm(10.2), Cm(4.3), ingr, sz=Pt(9.5))

# 作り方（グリーン左ライン）
rect(s3, Cm(0.7), Cm(10.3), Cm(0.3), Cm(4.2), SP_GREEN_MID)
steps = [
    "【作り方】",
    "① 玉ねぎを薄切りに。だし汁・みりん・醤油・砂糖を混ぜておく。",
    "② 小鍋に調味料と玉ねぎを入れて中火で2分。唐揚げを加えて1分。",
    "③ 溶き卵を回し入れ、半熟になったら火を止め30秒蒸らす。",
    "④ ご飯に盛りつけ、三つ葉を散らして完成！",
    "",
    "💡 卵は2回に分けて入れるとふんわり仕上がります。",
    "💡 唐揚げは電子レンジで温めておくとよりジューシー。",
]
mtb(s3, Cm(1.2), Cm(10.3), Cm(19.1), Cm(4.2), steps,
    sz=Pt(9.5), bold_first=True)

# ── 区切り
diamond_divider(s3, Cm(14.6))

# ══ コーナー4：郷土料理 ════════════════════════════════
section_banner(s3, Cm(0.7), Cm(14.85), Cm(19.6), Cm(1.15),
               "地方出身スタッフの郷土料理", "🗾", SP_GREEN_DARK, WHITE,
               sub="古市南店  佐藤 由紀さん（青森県弘前市ご出身・勤続8年）")

# 料理名
tb(s3, Cm(0.7), Cm(16.2), Cm(19.6), Cm(0.9),
   "青森の郷土料理 「いちご煮」", sz=Pt(15), bold=True, color=SP_GREEN_DARK)
tb(s3, Cm(0.7), Cm(17.0), Cm(19.6), Cm(0.65),
   "ウニとアワビの潮汁。野いちごに似た黄金色のウニが名前の由来です。",
   sz=Pt(9), color=MID_GRAY, italic=True)

# 写真 + 材料
photo_box(s3, Cm(0.7), Cm(17.75), Cm(6.8), Cm(4.8), "いちご煮")

recipe2 = [
    "【材料（4人分）】",
    "・ウニ（塩水ウニ） 60g",
    "・アワビ  1個（薄切り）",
    "・昆布だし  600ml",
    "・酒  大さじ2",
    "・塩  小さじ3/4",
    "・薄口醤油  小さじ1/2",
    "",
    "【作り方】",
    "① アワビを塩でもみ洗いし薄切りに。",
    "② だし汁と酒を温めアワビを弱火で3分。",
    "③ 塩・醤油で調味し、ウニを加えてひと煮立ち。",
    "④ 器に盛り、三つ葉を添えて完成。",
]
mtb(s3, Cm(7.9), Cm(17.75), Cm(12.4), Cm(4.8), recipe2,
    sz=Pt(9), bold_first=True)

# 佐藤さんひとこと
rrect(s3, Cm(0.7), Cm(22.75), Cm(19.6), Cm(1.4), SP_GREEN_LIGHT, adj=0.05)
tb(s3, Cm(1.0), Cm(22.85), Cm(19.0), Cm(1.2),
   '佐藤さんより 🌿  「お盆や年越しには必ずこれ！大阪に来てからも'
   'ふるさとの味が恋しくて毎年作ります。'
   'だしの香りだけで心が温まりますよ。お試しください！」',
   sz=Pt(9.5), color=SP_GREEN_DARK)

# フッター
rect(s3, Cm(0), Cm(29.0), Cm(21), Cm(0.7), SP_GREEN_LIGHT)
tb(s3, Cm(0.5), Cm(29.05), Cm(20), Cm(0.62),
   "🗾  あなたの故郷の味を教えてください！郷土料理レシピ随時募集中  🗾",
   sz=Pt(8.5), color=SP_GREEN_DARK, align=PP_ALIGN.CENTER)


# ════════════════════════════════════════════════════════
# PAGE 4 — 裏表紙（生活の知恵 ＋ 誕生日 ＋ 投稿募集 ＋ 編集後記）
# ════════════════════════════════════════════════════════
s4 = prs.slides.add_slide(blank)
set_bg(s4, CREAM)

# ── ページヘッダー
rect(s4, Cm(0), Cm(0), Cm(21), Cm(0.85), SP_GREEN)
tb(s4, Cm(0.7), Cm(0.07), Cm(15), Cm(0.72),
   "🌿  サンプラザ ひだまり通信  創刊号  2026年6月",
   sz=Pt(9), color=WHITE)
tb(s4, Cm(16.5), Cm(0.07), Cm(4.0), Cm(0.72),
   "P.4", sz=Pt(10), bold=True, color=WHITE, align=PP_ALIGN.RIGHT)

# ══ コーナー5：生活の知恵 ══════════════════════════════
section_banner(s4, Cm(0.7), Cm(1.1), Cm(19.6), Cm(1.15),
               "ちょこっと得する生活の知恵", "💡", LAVENDER, WHITE)

tips = [
    ("🥒", "きゅうりの苦み取り",
     "ヘタを切った断面同士をくるくると擦り合わせると白い泡が出てきます。これが苦みの素！1分ほど続けるとおいしさUP。"),
    ("🍌", "バナナ即席アイス",
     "熟したバナナを輪切りにして冷凍。凍ったままミキサーにかけるだけでクリーミーなアイスに！砂糖ゼロでヘルシー♪"),
    ("🌱", "お米のとぎ汁活用",
     "栄養豊富なとぎ汁は観葉植物や家庭菜園への水やりに最適。植物が元気に育ちます。捨てずに活用！"),
]
for i, (icon, title, body) in enumerate(tips):
    tx = Cm(0.7) + i * Cm(6.55)
    rrect(s4, tx, Cm(2.45), Cm(6.2), Cm(5.0), LIGHT_LAVENDER, adj=0.06)
    tb(s4, tx + Cm(0.1), Cm(2.55), Cm(6.0), Cm(0.9),
       icon, sz=Pt(22), color=LAVENDER, align=PP_ALIGN.CENTER)
    tb(s4, tx + Cm(0.2), Cm(3.5), Cm(5.8), Cm(0.75),
       title, sz=Pt(10.5), bold=True, color=SP_GREEN_DARK)
    mtb(s4, tx + Cm(0.2), Cm(4.3), Cm(5.8), Cm(2.9), [body], sz=Pt(9.5))

# ── 区切り
diamond_divider(s4, Cm(7.7))

# ══ コーナー6：お誕生日スタッフ ════════════════════════
section_banner(s4, Cm(0.7), Cm(7.9), Cm(19.6), Cm(1.15),
               "今月のお誕生日スタッフ 🎂", "🎉", SUNNY_YELLOW, DARK_CHARCOAL)

staff = [
    ("堺東駅前店", "山田 花子さん"),
    ("古市南店",   "田中 美穂さん"),
    ("三日市駅前店", "中村 幸恵さん"),
    ("羽曳が丘店", "鈴木 由美さん"),
    ("北野田店",   "林 久美子さん"),
    ("さつき野店", "松本 玲子さん"),
]
for i, (store, name) in enumerate(staff):
    col = i % 3; row = i // 3
    bx = Cm(0.7) + col * Cm(6.55)
    by = Cm(9.25) + row * Cm(1.65)
    rrect(s4, bx, by, Cm(6.2), Cm(1.5), LIGHT_YELLOW, adj=0.07)
    tb(s4, bx + Cm(0.3), by + Cm(0.05), Cm(5.6), Cm(0.7),
       f"🎂  {name}", sz=Pt(10.5), bold=True, color=SP_GREEN_DARK)
    tb(s4, bx + Cm(0.3), by + Cm(0.75), Cm(5.6), Cm(0.6),
       store, sz=Pt(8.5), color=MID_GRAY)

# ── 区切り
diamond_divider(s4, Cm(12.8))

# ══ コーナー7：投稿募集 ════════════════════════════════
section_banner(s4, Cm(0.7), Cm(13.0), Cm(19.6), Cm(1.15),
               "投稿募集 & 読者プレゼント", "📮", SAKURA_PINK, WHITE)

# 左：投稿募集
rrect(s4, Cm(0.7), Cm(14.35), Cm(11.2), Cm(5.3), LIGHT_PINK, adj=0.05)
recruit = [
    "📝 投稿募集中！みなさんの声で作る社内報です",
    "",
    " ■ 〇〇店の職場自慢！（エピソード＋写真）",
    " ■ わたしの独り言（お客様とのほっこり話）",
    " ■ アレンジレシピ（サンプラザ商品を使ったもの）",
    " ■ 郷土料理レシピ（故郷の味を教えてください！）",
    " ■ 生活の知恵（得するTipsなど）",
    "",
    "締め切り：毎月15日",
    "提出先：各店舗リーダー経由 or 総務部へメール",
]
mtb(s4, Cm(1.0), Cm(14.55), Cm(10.6), Cm(5.0), recruit, sz=Pt(9.5),
    bold_first=True)

# 右：プレゼント
rrect(s4, Cm(12.3), Cm(14.35), Cm(8.0), Cm(5.3), SP_GREEN_LIGHT, adj=0.05)
rect(s4, Cm(12.3), Cm(14.35), Cm(8.0), Cm(0.7), SP_GREEN_MID)
tb(s4, Cm(12.5), Cm(14.37), Cm(7.6), Cm(0.65),
   "🎁  読者プレゼント", sz=Pt(11), bold=True, color=WHITE)
prize = [
    "採用された投稿者に",
    "サンプラザ商品券",
    "（500円分）をプレゼント！",
    "",
    "💚 創刊号採用者には",
    "    特別に1,000円分贈呈！",
    "",
    "たくさんのご投稿",
    "お待ちしています♪",
]
mtb(s4, Cm(12.5), Cm(15.2), Cm(7.6), Cm(4.2), prize, sz=Pt(10))

# ── 区切り
diamond_divider(s4, Cm(19.9))

# ══ 編集後記 ════════════════════════════════════════════
section_banner(s4, Cm(0.7), Cm(20.1), Cm(19.6), Cm(1.0),
               "編集後記", "✏️", SP_GREEN_DARK, WHITE)

rrect(s4, Cm(0.7), Cm(21.3), Cm(14.8), Cm(3.3), WHITE, adj=0.04)
koki = [
    "　「ひだまり通信」、ついに創刊です！",
    "",
    "　南大阪のあちこちの店舗で、毎日いきいきと働くみなさんの",
    "声とエピソードをつなげる場所を作りたいという想いから生まれ",
    "ました。毎号、みなさんの投稿でにぎやかに作っていきましょう！",
    "",
    "                     編集部：総務部 河野・中嶋",
]
mtb(s4, Cm(1.0), Cm(21.45), Cm(14.2), Cm(3.0), koki, sz=Pt(9.5))

# QRコード
rrect(s4, Cm(16.0), Cm(21.3), Cm(4.3), Cm(3.3), SP_GREEN_LIGHT, adj=0.04)
photo_box(s4, Cm(16.1), Cm(21.4), Cm(4.1), Cm(2.3), "QRコード\n（投稿フォーム）", "📱")
tb(s4, Cm(16.0), Cm(23.8), Cm(4.3), Cm(0.7),
   "投稿はこちらから", sz=Pt(8.5), color=SP_GREEN_DARK, align=PP_ALIGN.CENTER)

# ── フッター（ダークグリーン）
rect(s4, Cm(0), Cm(27.7), Cm(21), Cm(2.0), SP_GREEN_DARK)
tb(s4, Cm(0.5), Cm(27.85), Cm(20), Cm(0.85),
   "サンプラザ ひだまり通信  創刊号  発行日：2026年6月1日",
   sz=Pt(11), bold=True, color=WHITE, align=PP_ALIGN.CENTER)
tb(s4, Cm(0.5), Cm(28.7), Cm(20), Cm(0.7),
   "発行：株式会社サンプラザ 総務部　〒大阪府羽曳野市誉田（本社）",
   sz=Pt(8), color=SP_GREEN_LIGHT, align=PP_ALIGN.CENTER)

# 葉っぱデコ（フッター周辺）
leaf_deco(s4,
    [(Cm(0.5), Cm(27.3)), (Cm(2.5), Cm(27.1)),
     (Cm(17.0), Cm(27.1)), (Cm(19.0), Cm(27.3))],
    RGBColor(0xA8,0xFF,0xC0), sz=Pt(14))

# ─── 保存 ──────────────────────────────────────────────
out = "/home/user/Sunplaza-supermarket/sunplaza_newsletter_vol1_redesign.pptx"
prs.save(out)
print(f"✅ リデザイン版 PowerPoint 保存完了: {out}")
