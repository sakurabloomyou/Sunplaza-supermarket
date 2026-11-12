# ローンチまでの手順（チェックリスト）

作成：2026年11月12日。☑ はこちらで用意済み、☐ はこれから。担当は README のチーム表の役割。

## A. 先に決めること（ここで止まると申請できない）
- ☐ **申請する主体を法人にする**（法務）
  App Review Guidelines 5.1.1(ix)：医療（healthcare）などの規制の多い分野や、機微な個人情報を扱うアプリは、個人の開発者ではなく、サービスを提供する法人が提出するべきとされています。出典：https://developer.apple.com/app-store/review/guidelines/
- ☐ Apple Developer Program に法人で登録（年会費 99米ドル。円での金額は Apple の購入画面で確認）。法人登録には D-U-N-S 番号が必要（Apple の登録ページで要確認）。
- ☐ 医療機器に当たらないことの確認（法務）。不安が残る場合は厚労省・PMDA の一元化窓口に相談。出典：プログラムの医療機器該当性に関するガイドライン（2021年3月31日）https://www.pmda.go.jp/files/000240364.pdf
- ☐ 商標「みんなのきょう」の調査（J-PlatPat）と出願の判断（法務）
- ☐ 家族間の共有の方式を決めて実装（iOS。`docs/ARCHITECTURE.md`）

## B. アプリを仕上げる
- ☑ 画面のコード一式（ビルド未確認）
- ☐ Mac で `xcodegen generate` → ビルドエラーを直す（iOS）
- ☐ テスト（⌘U）を通す（iOS）
- ☐ 家族間の共有、「済み」の連絡通知（iOS）
- ☐ 実機で通知（前日・1時間前・時刻・おくすり・まだです）を確認（iOS）
- ☐ 高齢のモニター（白内障の方を含む）での見え方・使いやすさテスト（UX）
- ☐ 研究者・当事者家族・ご本人による文言の確認（研究者・当事者家族・ご本人）
- ☐ StoreKit の課金テスト（サンドボックス）（iOS）

## C. App Store Connect の準備
- ☐ アプリを登録（名前：みんなのきょう 認知症の家族向け）
- ☐ サブタイトル・キーワード・説明文：`appstore/metadata_ja.md` を貼る
- ☑ 説明画像 5枚（2868×1320px）：`appstore/screenshots/`
- ☑ アイコン（通常・ダーク・色合い）：`Assets.xcassets/AppIcon.appiconset`
- ☐ プライバシーポリシーの URL（`docs/PRIVACY_POLICY.md` を法務確認後に公開）
- ☐ サポート URL（問い合わせ先のページ）
- ☐ App のプライバシー（栄養成分ラベル）：開発者がデータを集めない設計なら「データの収集なし」。共有方式で変わる（法務・iOS）
- ☑ プライバシーマニフェスト（`PrivacyInfo.xcprivacy`）。使っているAPIが増えたら更新
- ☐ 年齢区分の質問に回答
- ☐ 自動更新サブスクリプションの商品を作成：`jp.minnanokyou.plus.monthly` / `.yearly`（`docs/PRICING.md`）
- ☐ App Store Small Business Program に申し込む（手数料15%）
- ☐ 審査メモ：`appstore/review_notes.md`（審査用のデモ用家族グループの入り方を書く）

## D. 公開前
- ☐ TestFlight で家族数組（例：3〜5家庭）に2週間使ってもらう
- ☐ 問い合わせ・不具合の受け付け方法を決める
- ☐ 審査に提出 → 公開
