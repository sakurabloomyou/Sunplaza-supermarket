"""
サンプラザ ひだまり通信 — PowerPoint社内報ジェネレーター
創刊号 2026年6月
"""

from pptx import Presentation
from pptx.util import Cm, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.util import Inches
from pptx.enum.dml import MSO_THEME_COLOR
import copy

# ─── カラーパレット ─────────────────────────────────────────
CORAL      = RGBColor(0xFF, 0x6B, 0x6B)   # コーラルレッド（見出し）
YELLOW     = RGBColor(0xFF, 0xD9, 0x3D)   # サニーイエロー（帯）
GREEN      = RGBColor(0x6B, 0xCB, 0x77)   # フレッシュグリーン（レシピ）
ORANGE     = RGBColor(0xFF, 0x8E, 0x53)   # ウォームオレンジ（独り言）
CREAM      = RGBColor(0xFF, 0xF9, 0xF0)   # クリーム（背景）
DARK_BROWN = RGBColor(0x3D, 0x2C, 0x2C)   # ダークブラウン（本文）
MID_GRAY   = RGBColor(0x7A, 0x7A, 0x7A)   # グレー（サブテキスト）
WHITE      = RGBColor(0xFF, 0xFF, 0xFF)
LIGHT_YELLOW = RGBColor(0xFF, 0xF0, 0xB0)
LIGHT_GREEN  = RGBColor(0xD6, 0xF5, 0xDA)
LIGHT_CORAL  = RGBColor(0xFF, 0xE0, 0xE0)
LIGHT_ORANGE = RGBColor(0xFF, 0xED, 0xD5)
PURPLE     = RGBColor(0xC0, 0x83, 0xFF)
LIGHT_PURPLE = RGBColor(0xEE, 0xDD, 0xFF)

# ─── ヘルパー関数 ─────────────────────────────────────────

def set_bg(slide, color):
    """スライド背景色を設定"""
    fill = slide.background.fill
    fill.solid()
    fill.fore_color.rgb = color

def add_rect(slide, x, y, w, h, fill_color, line_color=None, line_width=Pt(0)):
    """塗りつぶし矩形を追加"""
    shape = slide.shapes.add_shape(1, x, y, w, h)  # MSO_SHAPE_TYPE.RECTANGLE=1
    shape.fill.solid()
    shape.fill.fore_color.rgb = fill_color
    if line_color:
        shape.line.color.rgb = line_color
        shape.line.width = line_width
    else:
        shape.line.fill.background()
    return shape

def add_rounded_rect(slide, x, y, w, h, fill_color, radius=Pt(8)):
    """角丸矩形を追加"""
    shape = slide.shapes.add_shape(5, x, y, w, h)  # 5=rounded rectangle
    shape.fill.solid()
    shape.fill.fore_color.rgb = fill_color
    shape.line.fill.background()
    shape.adjustments[0] = 0.05
    return shape

def add_textbox(slide, x, y, w, h, text, font_size=Pt(10), bold=False,
                color=DARK_BROWN, align=PP_ALIGN.LEFT, line_spacing=None):
    """テキストボックスを追加"""
    txBox = slide.shapes.add_textbox(x, y, w, h)
    tf = txBox.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = text
    p.alignment = align
    run = p.runs[0]
    run.font.size = font_size
    run.font.bold = bold
    run.font.color.rgb = color
    run.font.name = "メイリオ"
    if line_spacing:
        p.line_spacing = line_spacing
    return txBox

def add_multiline_textbox(slide, x, y, w, h, lines, font_size=Pt(10),
                          color=DARK_BROWN, bold_first=False, align=PP_ALIGN.LEFT):
    """複数行テキストボックス"""
    txBox = slide.shapes.add_textbox(x, y, w, h)
    tf = txBox.text_frame
    tf.word_wrap = True
    for i, line in enumerate(lines):
        if i == 0:
            p = tf.paragraphs[0]
        else:
            p = tf.add_paragraph()
        p.text = line
        p.alignment = align
        run = p.runs[0] if p.runs else p.add_run()
        run.text = line
        run.font.size = font_size
        run.font.bold = (bold_first and i == 0)
        run.font.color.rgb = color
        run.font.name = "メイリオ"
    return txBox

def add_section_header(slide, x, y, w, h, title, bg_color, text_color=WHITE, icon=""):
    """セクションヘッダーバー"""
    rect = add_rounded_rect(slide, x, y, w, h, bg_color)
    label = f"{icon}  {title}" if icon else title
    txBox = slide.shapes.add_textbox(x + Cm(0.3), y + Cm(0.05), w - Cm(0.6), h)
    tf = txBox.text_frame
    p = tf.paragraphs[0]
    p.text = label
    p.alignment = PP_ALIGN.LEFT
    run = p.runs[0]
    run.font.size = Pt(13)
    run.font.bold = True
    run.font.color.rgb = text_color
    run.font.name = "メイリオ"
    return rect

def add_photo_placeholder(slide, x, y, w, h, label="写真"):
    """写真プレースホルダー枠"""
    rect = slide.shapes.add_shape(1, x, y, w, h)
    rect.fill.solid()
    rect.fill.fore_color.rgb = RGBColor(0xF0, 0xF0, 0xF0)
    rect.line.color.rgb = RGBColor(0xCC, 0xCC, 0xCC)
    rect.line.width = Pt(1)
    rect.line.dash_style = 4  # dash
    txBox = slide.shapes.add_textbox(x, y + h/2 - Cm(0.5), w, Cm(1))
    tf = txBox.text_frame
    p = tf.paragraphs[0]
    p.text = f"📷 {label}"
    p.alignment = PP_ALIGN.CENTER
    run = p.runs[0]
    run.font.size = Pt(9)
    run.font.color.rgb = MID_GRAY
    run.font.name = "メイリオ"

def add_decorative_flowers(slide, positions, color=YELLOW, size=Pt(18)):
    """花飾り"""
    for (x, y) in positions:
        txBox = slide.shapes.add_textbox(x, y, Cm(1), Cm(1))
        tf = txBox.text_frame
        p = tf.paragraphs[0]
        p.text = "✿"
        run = p.runs[0]
        run.font.size = size
        run.font.color.rgb = color
        run.font.name = "メイリオ"


# ─── プレゼンテーション設定 ────────────────────────────────────

prs = Presentation()
# A4 縦 (210mm × 297mm)
prs.slide_width  = Cm(21.0)
prs.slide_height = Cm(29.7)

blank_layout = prs.slide_layouts[6]  # blank layout


# ════════════════════════════════════════════════════════════
# PAGE 1 — 表紙
# ════════════════════════════════════════════════════════════
slide1 = prs.slides.add_slide(blank_layout)
set_bg(slide1, CREAM)

# ── 最上部タイトルバナー（黄色）
add_rect(slide1, Cm(0), Cm(0), Cm(21), Cm(3.8), YELLOW)

# ── タイトル「サンプラザ」
txBox = slide1.shapes.add_textbox(Cm(0.5), Cm(0.1), Cm(20), Cm(1.5))
tf = txBox.text_frame
p = tf.paragraphs[0]
p.text = "スーパーサンプラザ"
p.alignment = PP_ALIGN.CENTER
r = p.runs[0]; r.font.size = Pt(16); r.font.bold = True
r.font.color.rgb = DARK_BROWN; r.font.name = "メイリオ"

# ── タイトル「ひだまり通信」
txBox2 = slide1.shapes.add_textbox(Cm(0.5), Cm(1.3), Cm(20), Cm(2.2))
tf2 = txBox2.text_frame
p2 = tf2.paragraphs[0]
p2.text = "ひだまり通信"
p2.alignment = PP_ALIGN.CENTER
r2 = p2.runs[0]; r2.font.size = Pt(38); r2.font.bold = True
r2.font.color.rgb = CORAL; r2.font.name = "メイリオ"

# ── 花飾り（タイトル両脇）
add_decorative_flowers(slide1, [(Cm(0.8), Cm(1.1)), (Cm(18.5), Cm(1.1))], CORAL, Pt(22))
add_decorative_flowers(slide1, [(Cm(1.8), Cm(0.5)), (Cm(17.5), Cm(0.5))], ORANGE, Pt(16))

# ── 号数・日付バッジ
add_rounded_rect(slide1, Cm(6.5), Cm(3.6), Cm(8), Cm(1.0), CORAL)
add_textbox(slide1, Cm(6.5), Cm(3.65), Cm(8), Cm(0.9),
            "創刊号  Vol.1  ✦  2026年6月号",
            font_size=Pt(12), bold=True, color=WHITE, align=PP_ALIGN.CENTER)

# ── サブタイトル
add_textbox(slide1, Cm(1), Cm(4.8), Cm(19), Cm(0.8),
            "～ 働くみんなの、笑顔をつなぐ社内報 ～",
            font_size=Pt(11), color=DARK_BROWN, align=PP_ALIGN.CENTER)

# ── メインビジュアルエリア（コーラル枠）
add_rect(slide1, Cm(1.2), Cm(5.7), Cm(18.6), Cm(11.5), RGBColor(0xFF, 0xE8, 0xE8))
add_photo_placeholder(slide1, Cm(1.5), Cm(5.9), Cm(18), Cm(6.0),
                      "表紙メインビジュアル（従業員集合写真・ひまわり畑など）")

# ── ひまわりイラスト代替テキスト
txBox3 = slide1.shapes.add_textbox(Cm(1.5), Cm(12.1), Cm(18), Cm(2.5))
tf3 = txBox3.text_frame; tf3.word_wrap = True
for i, (txt, sz, clr) in enumerate([
    ("🌻  🌼  ☀  🌸  🌻  🌼  ☀  🌸  🌻", Pt(20), YELLOW),
    ("みんなで作る、みんなが主役の社内報です！", Pt(12), CORAL),
]):
    p3 = tf3.paragraphs[0] if i == 0 else tf3.add_paragraph()
    p3.text = txt; p3.alignment = PP_ALIGN.CENTER
    r3 = p3.runs[0] if p3.runs else p3.add_run(); r3.text = txt
    r3.font.size = sz; r3.font.color.rgb = clr; r3.font.name = "メイリオ"
    r3.font.bold = (i == 1)

# ── 特集ティーザー3点
teasers = [
    (CORAL,  "🏔  P.2",  "職場自慢！堺東駅前店、みんなで葛城山へ登山"),
    (GREEN,  "🍲  P.3",  "唐揚げde親子丼♪ アレンジレシピ＆郷土料理"),
    (ORANGE, "💡  P.4",  "得する生活の知恵 ＆ 今月のお誕生日スタッフ"),
]
for idx, (col, badge, text) in enumerate(teasers):
    ty = Cm(17.9) + idx * Cm(1.85)
    add_rounded_rect(slide1, Cm(1.2), ty, Cm(18.6), Cm(1.6), RGBColor(0xFF,0xFF,0xFF))
    # 左バッジ
    add_rounded_rect(slide1, Cm(1.4), ty + Cm(0.2), Cm(2.2), Cm(1.2), col)
    add_textbox(slide1, Cm(1.4), ty + Cm(0.25), Cm(2.2), Cm(0.9),
                badge, font_size=Pt(10), bold=True, color=WHITE, align=PP_ALIGN.CENTER)
    add_textbox(slide1, Cm(4.0), ty + Cm(0.3), Cm(15.2), Cm(0.9),
                text, font_size=Pt(11), color=DARK_BROWN, align=PP_ALIGN.LEFT)

# ── フッター
add_rect(slide1, Cm(0), Cm(27.8), Cm(21), Cm(1.9), DARK_BROWN)
add_textbox(slide1, Cm(0.5), Cm(27.9), Cm(20), Cm(0.8),
            "編集：サンプラザ 社内報編集部　　投稿・問い合わせ：総務部まで",
            font_size=Pt(9), color=WHITE, align=PP_ALIGN.CENTER)
add_textbox(slide1, Cm(0.5), Cm(28.7), Cm(20), Cm(0.7),
            "✿ 毎月1日発行 ✿  投稿大歓迎！ぜひ参加してください ✿",
            font_size=Pt(8), color=YELLOW, align=PP_ALIGN.CENTER)


# ════════════════════════════════════════════════════════════
# PAGE 2 — 中面左（職場自慢 ＋ わたしの独り言）
# ════════════════════════════════════════════════════════════
slide2 = prs.slides.add_slide(blank_layout)
set_bg(slide2, CREAM)

# ── ページヘッダーライン
add_rect(slide2, Cm(0), Cm(0), Cm(21), Cm(0.9), CORAL)
add_textbox(slide2, Cm(0.5), Cm(0.05), Cm(14), Cm(0.8),
            "サンプラザ ひだまり通信  創刊号 2026年6月",
            font_size=Pt(9), color=WHITE, align=PP_ALIGN.LEFT)
add_textbox(slide2, Cm(15), Cm(0.05), Cm(5.5), Cm(0.8),
            "P.2", font_size=Pt(10), bold=True, color=WHITE, align=PP_ALIGN.RIGHT)

# ══ コーナー1：〇〇店の職場自慢！ ══
add_section_header(slide2, Cm(0.8), Cm(1.1), Cm(19.4), Cm(1.0),
                   "〇〇店の職場自慢！", CORAL, WHITE, "🏆")

# ── 特集店舗名
add_rounded_rect(slide2, Cm(0.8), Cm(2.3), Cm(19.4), Cm(0.75), LIGHT_CORAL)
add_textbox(slide2, Cm(0.8), Cm(2.32), Cm(19.4), Cm(0.7),
            "今月の特集 ▶  堺東駅前店「全員で葛城山ハイキング！」",
            font_size=Pt(11), bold=True, color=CORAL, align=PP_ALIGN.LEFT)

# ── 写真プレースホルダー（2枚横並び）
add_photo_placeholder(slide2, Cm(0.8), Cm(3.2), Cm(9.2), Cm(5.5), "登山中の集合写真")
add_photo_placeholder(slide2, Cm(10.4), Cm(3.2), Cm(9.4), Cm(5.5), "山頂でのランチ風景")

# ── 本文
body1 = (
    "　先月の日曜日、堺東駅前店のスタッフ22名が大阪・奈良の県境にそびえる"
    "葛城山（標高959m）へ日帰りハイキングに出かけました！\n\n"
    "　早朝7時に近鉄・富田林駅に集合。ロープウェイを使わず登山道を徒歩で挑戦し、"
    "約2時間かけて山頂へ。途中、入社3年目のパートの荒木さん（67歳）が"
    "「山歩きは10年来の趣味！」と若手スタッフを次々と抜き去る場面に一同大爆笑！\n\n"
    "　山頂では各自が持ち寄ったお弁当でランチタイム。副店長の村田さんが"
    "「実はアウトドア料理が得意」と手作りのおにぎり20個を振る舞い、大好評でした。\n\n"
    "　下山後は富田林駅近くの居酒屋で打ち上げ。「次は金剛山に挑戦しよう！」と"
    "早くも次回の計画が持ち上がっています。店長・西川さん談：「普段話せない"
    "スタッフ同士が仲よくなれる最高の機会でした。来年も必ず行きます！」"
)
add_multiline_textbox(slide2, Cm(0.8), Cm(8.9), Cm(19.4), Cm(5.0),
                      body1.split("\n"), font_size=Pt(9.5), color=DARK_BROWN)

# ── 区切り線
add_rect(slide2, Cm(0.8), Cm(14.5), Cm(19.4), Cm(0.05), MID_GRAY)

# ══ コーナー2：わたしの独り言 ══
add_section_header(slide2, Cm(0.8), Cm(14.7), Cm(19.4), Cm(1.0),
                   "わたしの独り言", ORANGE, WHITE, "💬")

# ── 投稿者情報バッジ
add_rounded_rect(slide2, Cm(0.8), Cm(15.9), Cm(19.4), Cm(0.7), LIGHT_ORANGE)
add_textbox(slide2, Cm(0.8), Cm(15.92), Cm(19.4), Cm(0.65),
            "三日市駅前店  青山 恵子さん（パート歴11年）",
            font_size=Pt(10), bold=True, color=ORANGE, align=PP_ALIGN.LEFT)

# ── 写真プレースホルダー（右寄り）
add_photo_placeholder(slide2, Cm(14.5), Cm(16.8), Cm(5.7), Cm(4.5), "青山さんの写真")

# ── 本文（吹き出し風背景）
add_rounded_rect(slide2, Cm(0.8), Cm(16.8), Cm(13.3), Cm(5.5), RGBColor(0xFF,0xFF,0xF5))
body2 = (
    "　うちのお店に、もう10年以上毎朝いらっしゃる"
    "お客様がいます。いつも必ず「お茶漬けのり」と"
    "「わかめスープ」を買って帰られるんです。\n\n"
    "　先日、そのお客様が珍しそうにお惣菜コーナーを"
    "眺めていたので声をかけると、「今日は家内の誕生日"
    "なんや。何か喜ぶもんないかな」とはにかんで"
    "おられました。\n\n"
    "　一緒に選んで、プリンとちょっと豪華なお刺身を"
    "カゴに入れたら、「ラッピングしてもらえますか」と。"
    "そのひとことに、ジーンとしてしまいました。"
    "長年連れ添った奥様を大切にされている姿が、"
    "なんだかとっても素敵で……。\n\n"
    "　小さなお買い物の中にも、こんな温かい物語が"
    "あるんだなと、改めてこの仕事が好きになりました。"
)
add_multiline_textbox(slide2, Cm(1.0), Cm(17.0), Cm(13.0), Cm(5.2),
                      body2.split("\n"), font_size=Pt(9.5), color=DARK_BROWN)

# ── フッター
add_rect(slide2, Cm(0), Cm(29.0), Cm(21), Cm(0.7), YELLOW)
add_textbox(slide2, Cm(0.5), Cm(29.05), Cm(20), Cm(0.6),
            "✿  あなたのエピソードも投稿してください！編集部一同お待ちしています  ✿",
            font_size=Pt(8.5), color=DARK_BROWN, align=PP_ALIGN.CENTER)


# ════════════════════════════════════════════════════════════
# PAGE 3 — 中面右（アレンジレシピ ＋ 郷土料理）
# ════════════════════════════════════════════════════════════
slide3 = prs.slides.add_slide(blank_layout)
set_bg(slide3, CREAM)

# ── ページヘッダーライン
add_rect(slide3, Cm(0), Cm(0), Cm(21), Cm(0.9), GREEN)
add_textbox(slide3, Cm(0.5), Cm(0.05), Cm(14), Cm(0.8),
            "サンプラザ ひだまり通信  創刊号 2026年6月",
            font_size=Pt(9), color=WHITE, align=PP_ALIGN.LEFT)
add_textbox(slide3, Cm(15), Cm(0.05), Cm(5.5), Cm(0.8),
            "P.3", font_size=Pt(10), bold=True, color=WHITE, align=PP_ALIGN.RIGHT)

# ══ コーナー3：アレンジレシピ ══
add_section_header(slide3, Cm(0.8), Cm(1.1), Cm(19.4), Cm(1.0),
                   "サンプラザ商品でアレンジレシピ！", GREEN, WHITE, "🍳")

# ── 商品バッジ
add_rounded_rect(slide3, Cm(0.8), Cm(2.3), Cm(19.4), Cm(0.7), LIGHT_GREEN)
add_textbox(slide3, Cm(0.8), Cm(2.33), Cm(19.4), Cm(0.65),
            "使用商品 ▶  サンプラザ お惣菜「鶏の唐揚げ（にんにく醤油）」",
            font_size=Pt(10), bold=True, color=GREEN, align=PP_ALIGN.LEFT)

# ── レシピタイトル
add_textbox(slide3, Cm(0.8), Cm(3.2), Cm(19.4), Cm(0.9),
            "唐揚げで作る！ふわとろ親子丼",
            font_size=Pt(16), bold=True, color=DARK_BROWN, align=PP_ALIGN.LEFT)
add_textbox(slide3, Cm(0.8), Cm(3.9), Cm(19.4), Cm(0.6),
            "　〜 時短！買ってきた唐揚げがごちそう丼に変身 〜  （2人分・調理時間10分）",
            font_size=Pt(9.5), color=MID_GRAY, align=PP_ALIGN.LEFT)

# ── 写真
add_photo_placeholder(slide3, Cm(12.0), Cm(4.5), Cm(8.2), Cm(5.5), "完成写真")

# ── 材料リスト
add_rounded_rect(slide3, Cm(0.8), Cm(4.5), Cm(10.8), Cm(5.5), RGBColor(0xF0,0xFF,0xF4))
ingredients = [
    "【材料（2人分）】",
    "・唐揚げ（サンプラザ惣菜）  8個",
    "・卵                       3個",
    "・玉ねぎ（小）             1/2個",
    "・だし汁                   150ml",
    "・みりん                   大さじ2",
    "・醤油                     大さじ1.5",
    "・砂糖                     小さじ1",
    "・ご飯                     2膳分",
    "・三つ葉（お好みで）        少々",
]
add_multiline_textbox(slide3, Cm(1.1), Cm(4.7), Cm(10.2), Cm(5.2),
                      ingredients, font_size=Pt(9.5), color=DARK_BROWN,
                      bold_first=True)

# ── 作り方
steps = [
    "【作り方】",
    "① 玉ねぎを薄切りにする。だし汁・みりん・醤油・砂糖を合わせておく。",
    "② 小鍋に合わせ調味料と玉ねぎを入れて中火で2分煮る。玉ねぎが透き通ったら唐揚げを入れてさらに1分。",
    "③ 溶き卵を回し入れ、半熟になったら火を止めてふたをして30秒蒸らす。",
    "④ 丼にご飯をよそい、③をのせて完成！お好みで三つ葉を散らして。",
    "",
    "💡 コツ：卵は2回に分けて入れると、外はとろとろ・中はふんわり仕上がります。",
    "💡 唐揚げは電子レンジで軽く温めるとさらにジューシーに！",
]
add_multiline_textbox(slide3, Cm(0.8), Cm(10.2), Cm(19.4), Cm(4.0),
                      steps, font_size=Pt(9.5), color=DARK_BROWN, bold_first=True)

# ── 区切り線
add_rect(slide3, Cm(0.8), Cm(14.5), Cm(19.4), Cm(0.05), MID_GRAY)

# ══ コーナー4：郷土料理 ══
add_section_header(slide3, Cm(0.8), Cm(14.7), Cm(19.4), Cm(1.0),
                   "地方出身スタッフの郷土料理レシピ", PURPLE, WHITE, "🗾")

# ── 投稿者
add_rounded_rect(slide3, Cm(0.8), Cm(15.9), Cm(19.4), Cm(0.7), LIGHT_PURPLE)
add_textbox(slide3, Cm(0.8), Cm(15.92), Cm(19.4), Cm(0.65),
            "青森県弘前市ご出身  ▶  古市南店  佐藤 由紀さん（正社員・勤続8年）",
            font_size=Pt(10), bold=True, color=PURPLE, align=PP_ALIGN.LEFT)

# ── 郷土料理タイトル
add_textbox(slide3, Cm(0.8), Cm(16.8), Cm(19.4), Cm(0.85),
            "青森県の郷土料理「いちご煮」",
            font_size=Pt(15), bold=True, color=DARK_BROWN, align=PP_ALIGN.LEFT)
add_textbox(slide3, Cm(0.8), Cm(17.55), Cm(19.4), Cm(0.65),
            "　ウニとアワビが入った潮汁。名の由来は、ウニの黄色が野いちごに似ているから。",
            font_size=Pt(9), color=MID_GRAY, align=PP_ALIGN.LEFT)

# ── 2カラム（写真 + 材料）
add_photo_placeholder(slide3, Cm(0.8), Cm(18.3), Cm(6.8), Cm(4.8), "いちご煮の写真")

recipe2 = [
    "【材料（4人分）】",
    "・ウニ（塩水ウニ）  60g",
    "・アワビ           1個（薄切り）",
    "・昆布だし          600ml",
    "・酒               大さじ2",
    "・塩               小さじ3/4",
    "・薄口醤油         小さじ1/2",
    "",
    "【作り方】",
    "① アワビは塩でもみ洗いし薄切りに。",
    "② だし汁と酒を鍋で温め、アワビを入れて弱火で3分。",
    "③ 塩・醤油で味を調え、最後にウニを入れてひと煮立ち。",
    "④ 椀に盛り、三つ葉を添えて完成。",
]
add_multiline_textbox(slide3, Cm(8.0), Cm(18.3), Cm(12.2), Cm(4.8),
                      recipe2, font_size=Pt(9), color=DARK_BROWN, bold_first=True)

# ── 佐藤さんのひとこと
add_rounded_rect(slide3, Cm(0.8), Cm(23.3), Cm(19.4), Cm(1.3), LIGHT_PURPLE)
add_textbox(slide3, Cm(1.1), Cm(23.4), Cm(18.8), Cm(1.1),
            '佐藤さんのひとこと 💜  「お盆や年越しには必ずこれ！大阪に来てからも、ふるさとの味が恋しくて毎年作ります。'
            'ウニが苦手な方は少なめでも大丈夫。だしの香りだけで心が温まりますよ。」',
            font_size=Pt(9.5), color=DARK_BROWN, align=PP_ALIGN.LEFT)

# ── フッター
add_rect(slide3, Cm(0), Cm(29.0), Cm(21), Cm(0.7), GREEN)
add_textbox(slide3, Cm(0.5), Cm(29.05), Cm(20), Cm(0.6),
            "✿  あなたの故郷の味を教えてください！「郷土料理レシピ」随時募集中  ✿",
            font_size=Pt(8.5), color=WHITE, align=PP_ALIGN.CENTER)


# ════════════════════════════════════════════════════════════
# PAGE 4 — 裏表紙（生活の知恵 ＋ 誕生日 ＋ 投稿募集 ＋ 編集後記）
# ════════════════════════════════════════════════════════════
slide4 = prs.slides.add_slide(blank_layout)
set_bg(slide4, CREAM)

# ── ページヘッダーライン
add_rect(slide4, Cm(0), Cm(0), Cm(21), Cm(0.9), ORANGE)
add_textbox(slide4, Cm(0.5), Cm(0.05), Cm(14), Cm(0.8),
            "サンプラザ ひだまり通信  創刊号 2026年6月",
            font_size=Pt(9), color=WHITE, align=PP_ALIGN.LEFT)
add_textbox(slide4, Cm(15), Cm(0.05), Cm(5.5), Cm(0.8),
            "P.4", font_size=Pt(10), bold=True, color=WHITE, align=PP_ALIGN.RIGHT)

# ══ コーナー5：ちょこっと得する生活の知恵 ══
add_section_header(slide4, Cm(0.8), Cm(1.1), Cm(19.4), Cm(1.0),
                   "ちょこっと得する生活の知恵", ORANGE, WHITE, "💡")

tips = [
    ("🥒 きゅうりのあく抜き", "きゅうりのヘタを切り口に当て、クルクル回すと白い泡が出てきます。これが苦みの原因！1分ほど続けると苦みが取れてよりおいしくなります。"),
    ("🍌 バナナで即席アイス", "熟したバナナを輪切りにして冷凍庫へ。凍ったままミキサーにかけるだけでクリーミーなアイスの完成！砂糖ゼロでヘルシー♪"),
    ("🌿 お米のとぎ汁を活用", "お米のとぎ汁は植物への水やりに最適！栄養豊富で植物が元気に育ちます。観葉植物や家庭菜園にどうぞ。"),
]
for i, (title, body) in enumerate(tips):
    tx = Cm(0.8) + i * Cm(6.5)
    add_rounded_rect(slide4, tx, Cm(2.3), Cm(6.1), Cm(4.2), LIGHT_ORANGE)
    add_textbox(slide4, tx + Cm(0.2), Cm(2.4), Cm(5.7), Cm(0.8),
                title, font_size=Pt(10), bold=True, color=ORANGE, align=PP_ALIGN.LEFT)
    add_multiline_textbox(slide4, tx + Cm(0.2), Cm(3.2), Cm(5.7), Cm(3.0),
                          [body], font_size=Pt(9), color=DARK_BROWN)

# ── 区切り線
add_rect(slide4, Cm(0.8), Cm(6.8), Cm(19.4), Cm(0.05), MID_GRAY)

# ══ コーナー6：今月のお誕生日スタッフ ══
add_section_header(slide4, Cm(0.8), Cm(7.0), Cm(19.4), Cm(1.0),
                   "今月のお誕生日スタッフ 🎂", YELLOW, DARK_BROWN, "")

birthday_staff = [
    ("堺東駅前店", "山田 花子さん"),
    ("古市南店",   "田中 美穂さん"),
    ("三日市駅前店", "中村 幸恵さん"),
    ("羽曳が丘店", "鈴木 由美さん"),
    ("北野田店",   "林 久美子さん"),
    ("さつき野店", "松本 玲子さん"),
]
for i, (store, name) in enumerate(birthday_staff):
    col = i % 3
    row = i // 3
    bx = Cm(0.8) + col * Cm(6.5)
    by = Cm(8.2) + row * Cm(1.6)
    add_rounded_rect(slide4, bx, by, Cm(6.1), Cm(1.4), RGBColor(0xFF,0xF5,0xD0))
    add_textbox(slide4, bx + Cm(0.2), by + Cm(0.05), Cm(5.7), Cm(0.55),
                f"🎂  {name}", font_size=Pt(10), bold=True, color=DARK_BROWN, align=PP_ALIGN.LEFT)
    add_textbox(slide4, bx + Cm(0.2), by + Cm(0.6), Cm(5.7), Cm(0.55),
                store, font_size=Pt(8.5), color=MID_GRAY, align=PP_ALIGN.LEFT)

# ── 区切り線
add_rect(slide4, Cm(0.8), Cm(11.7), Cm(19.4), Cm(0.05), MID_GRAY)

# ══ コーナー7：投稿募集 ══
add_section_header(slide4, Cm(0.8), Cm(11.9), Cm(19.4), Cm(1.0),
                   "投稿募集コーナー & 読者プレゼント", CORAL, WHITE, "📮")

# 投稿募集（左）
add_rounded_rect(slide4, Cm(0.8), Cm(13.1), Cm(11.0), Cm(5.2), LIGHT_CORAL)
recruit_text = [
    "📝 投稿募集中！毎号、みなさんの投稿で作る社内報です。",
    "",
    "【募集コーナー】",
    " ・〇〇店の職場自慢！（エピソード＋写真）",
    " ・わたしの独り言（お客様とのほっこり話）",
    " ・アレンジレシピ（サンプラザ商品使用）",
    " ・郷土料理レシピ（出身地の味を教えて！）",
    " ・生活の知恵（ちょっと得するTipsなど）",
    "",
    "【締め切り】毎月15日",
    "【提出先】各店舗リーダー経由 or 総務部へメール",
]
add_multiline_textbox(slide4, Cm(1.1), Cm(13.2), Cm(10.4), Cm(5.0),
                      recruit_text, font_size=Pt(9.5), color=DARK_BROWN)

# プレゼント（右）
add_rounded_rect(slide4, Cm(12.2), Cm(13.1), Cm(8.0), Cm(5.2), RGBColor(0xFF,0xF0,0xFF))
prize_text = [
    "🎁 読者プレゼント！",
    "",
    "投稿が採用されたスタッフに",
    "サンプラザ商品券（500円分）を",
    "プレゼント！",
    "",
    "💌 創刊号投稿採用者には",
    "特別に1,000円分贈呈！",
    "",
    "たくさんのご投稿、",
    "お待ちしています♪",
]
add_multiline_textbox(slide4, Cm(12.5), Cm(13.2), Cm(7.4), Cm(5.0),
                      prize_text, font_size=Pt(9.5), color=DARK_BROWN)

# ── 区切り線
add_rect(slide4, Cm(0.8), Cm(18.6), Cm(19.4), Cm(0.05), MID_GRAY)

# ══ 編集後記 ══
add_section_header(slide4, Cm(0.8), Cm(18.8), Cm(19.4), Cm(0.9),
                   "編集後記", DARK_BROWN, WHITE, "✏️")

add_rounded_rect(slide4, Cm(0.8), Cm(19.9), Cm(14.5), Cm(3.5), RGBColor(0xF5,0xF5,0xF0))
koki_text = (
    "　ついに「ひだまり通信」創刊号が完成しました！\n\n"
    "　このお知らせを読んでいるあなたも、きっと誰かのエピソードや笑顔に"
    "元気をもらっているはず。社内報を通じて、南大阪の各店舗に散らばる"
    "仲間たちとの「つながり」を感じてほしいと思っています。\n\n"
    "　次号も、みなさんの投稿でにぎやかに作りましょう！\n\n"
    "                        （編集部　担当：総務部 河野・中嶋）"
)
add_multiline_textbox(slide4, Cm(1.1), Cm(20.0), Cm(13.9), Cm(3.3),
                      koki_text.split("\n"), font_size=Pt(9.5), color=DARK_BROWN)

# ── QRコード
add_rect(slide4, Cm(15.7), Cm(19.9), Cm(4.5), Cm(3.5), RGBColor(0xF0,0xF0,0xF0))
add_photo_placeholder(slide4, Cm(15.7), Cm(19.9), Cm(4.5), Cm(2.8), "QRコード\n（投稿フォーム）")
add_textbox(slide4, Cm(15.7), Cm(22.8), Cm(4.5), Cm(0.6),
            "投稿はこちらから", font_size=Pt(8.5), color=MID_GRAY, align=PP_ALIGN.CENTER)

# ── フッター
add_rect(slide4, Cm(0), Cm(27.8), Cm(21), Cm(1.9), DARK_BROWN)
add_textbox(slide4, Cm(0.5), Cm(27.9), Cm(20), Cm(0.9),
            "サンプラザ ひだまり通信  創刊号  発行日：2026年6月1日",
            font_size=Pt(10), bold=True, color=WHITE, align=PP_ALIGN.CENTER)
add_textbox(slide4, Cm(0.5), Cm(28.8), Cm(20), Cm(0.7),
            "発行：株式会社サンプラザ 総務部　〒（本社住所）　TEL：（代表番号）",
            font_size=Pt(8), color=YELLOW, align=PP_ALIGN.CENTER)

# ── 最終花飾り
add_decorative_flowers(slide4,
    [(Cm(0.3), Cm(27.5)), (Cm(3.0), Cm(27.3)), (Cm(18.0), Cm(27.3)), (Cm(19.5), Cm(27.5))],
    YELLOW, Pt(14))

# ─── 保存 ─────────────────────────────────────────────────
output_path = "/home/user/Sunplaza-supermarket/sunplaza_newsletter_vol1.pptx"
prs.save(output_path)
print(f"✅ PowerPoint保存完了: {output_path}")
