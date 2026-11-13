# 本番制作ツール調査メモ

> 調査日: 2026-11-13 ／ 方法: Web検索の結果の要約（各記事の本文までは開けず）
> ⚠️ 出典の多くは個人・企業ブログで、評価は書き手の主観です。料金・商用利用の条件は、契約前に各社の公式規約で必ず確認すること

## 結論
- 1本のツールで全部はできない。**①映像（参照画像→動画）②声（関西弁）③口パク④編集** を分けて作るのが現実的
- 映像は、参照画像からキャラを保てる Runway／Kling／Seedance が候補
- 関西弁の声は、AIの音声合成だと抑揚が不安定という検証結果がある → **ご本人が声を当てる案**も検討

## ① 映像（参照画像からキャラを保つ）
| ツール | 調査で出てきた評価 | 出典 |
|---|---|---|
| Runway | 参照画像でキャラの見た目を保つ機能が強いと複数記事が評価 | geekvibesnation／neural4d |
| Kling 3.0 | 1回の生成で最大6カットを、キャラを保ったまま作れる「Director Mode」 | presenc.ai ほか |
| Seedance 2.0／2.5 | 複数の参照画像に強い。1本20〜30秒程度。日本語を含む8言語以上で口の動きを合わせられる | seeddance.io／hinakira.com |
| Veo 3.1 | セリフ・音声つきの生成が強み。ただし参照画像を使うと1本8秒まで | meltflexsolutions ほか |
| Sora 2 | キャラの一貫性の評価が記事によって割れている | teachaitools ほか |

- 共通の注意: 場面を続けて作ったり、衣装や髪型を変えたりすると崩れやすい → 1カットずつ作って編集でつなぐ（gai.workstyle-evolution.co.jp、2026-04-26）
- 商用利用: Kling は規約上、書面での許可が必要とする記事あり（ai-revolution.co.jp、2026年10月）→ 要公式確認

## ② 声（関西弁）
| 候補 | 調査で出てきた内容 | 出典 |
|---|---|---|
| Gemini TTS（Google） | 関西弁を指示すると関西らしさは上がるが、同じ条件でも4語に1語は東京式と関西式の抑揚が入れ替わる（2026年9月の検証） | zenn.dev（acntechjp） |
| ElevenLabs v3 | 日本語対応・感情表現あり。関西弁の演出も可能とされる（2025年のアルファ版の記事） | dis-media.com |
| AITalk6（エーアイ） | 関西弁の話者に対応と公式に案内（掲載日は不明） | ai-j.jp |
| VOICEROID2 ついなちゃん | 「標準語」「関西弁」の話し方を切り替えられる（声は既存キャラクターの声） | ah-soft.com |
| Fish Audio | 関西弁の声モデルを個人が共有。品質はそれぞれ確認が必要 | fish.audio |
| ご本人の声を収録 | 関西弁の自然さは最も確実（※ご本人の話し方による） | — |

## ③ 口パク（リップシンク）
- 日本語の「つ」「ん」などで口が合いにくい海外ツールがある（hinakira.com）
- アニメ調の口パクの独自採点（1記事のみ）: DomoAI 86点、Dreamina 81点、HeyGen 78点、Kling 77点（fragments.co.jp）

## 次にやること（提案）
1. 一番の見せ場「旅行行ってたんか！」（約7秒）の1カットだけで、映像ツール2〜3個を無料枠で試す
2. 同じセリフを、関西弁の音声合成とご本人の声で録って聞き比べる
3. 気に入った組み合わせで、第1回を作る

## 出典
- https://geekvibesnation.com/ai-video-generators-consistent-characters-2026
- https://blog.neural4d.com/comparisons/best-ai-video-generator-for-consistent-characters/
- https://presenc.ai/research/ai-video-generation-models-compared-2026
- https://www.seeddance.io/blog/best-ai-video-generators-2026
- https://meltflexsolutions.com/blog/ai-video-generators
- https://teachaitools.blog/blog/best-ai-video-generation-tools-2026
- https://gai.workstyle-evolution.co.jp/2026/04/26/ai-video-character-consistency/
- https://ai-revolution.co.jp/media/best-ai-video-tools/
- https://zenn.dev/acntechjp/articles/zenn-gemini-tts-kansai-accent
- https://dis-media.com/20250825_1931.html
- https://www.ai-j.jp/about/
- https://www.ah-soft.com/voiceroid/tsuina/
- https://fish.audio/m/c6d50e23946b42659e4cf5870750863f/
- https://hinakira.com/blog/how-to-make-lip-sync-videos/
- https://fragments.co.jp/blog/speak-ai/
