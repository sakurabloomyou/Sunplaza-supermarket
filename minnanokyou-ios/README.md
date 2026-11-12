# みんなのきょう（iOS）

もの忘れが気になり始めた方（軽度認知症・MCI）と、そのご家族のための予定共有アプリです。
ご家族が入れた予定を、ご本人の iPhone にもお知らせとボードで届けます。

- 対応：iPhone、iOS 17 以降
- 画面：SwiftUI　データ：Core Data＋CloudKit（家族の間で共有）
- ブラウザで動く試作：https://claude.ai/artifact/Bfc8nU9FkpNvNfcTuWDoFk
- チーム共有用まとめ：https://claude.ai/artifact/FQBxLJgPEjKJa93mcrh2Mv

## 状態（2026年11月12日）

| 項目 | 状態 |
|---|---|
| 画面のコード（起動・初回設定・家族のホーム・ご本人・招待コード・お知らせ設定） | 書いた。**ビルド未確認**（作成した環境に Xcode がないため） |
| 点数のしくみ・お知らせの計画のテスト | 書いた。**未実行** |
| 家族間のデータ共有（CloudKit の共有、8けたの招待コード、「済み」の連絡） | 書いた。**ビルド・実機テスト未実施**。`docs/ARCHITECTURE.md` |
| アイコン・説明画像・App Store の文言 | できている。`appstore/` |
| ローンチに必要な手続き | `docs/LAUNCH_CHECKLIST.md` |

## Mac での始め方

1. Xcode（最新版）と XcodeGen を入れる：`brew install xcodegen`
2. このフォルダで `xcodegen generate` を実行すると `MinnanoKyou.xcodeproj` ができる
3. `project.yml` の `DEVELOPMENT_TEAM` に Team ID を入れ、`jp.minnanokyou.app` を自分のバンドルIDに変える
4. Xcode で開いてビルド。テストは ⌘U

## フォルダ

- `MinnanoKyou/` アプリ本体
- `MinnanoKyouTests/` テスト
- `appstore/` App Store 用の文言・画像
- `docs/` 設計、ローンチ手順、プライバシーポリシー案、利用規約案、将来の有料化の検討（`PRICING_FUTURE.md`）

**v1 は無料版**です（2026年11月12日決定）。App 内課金はありません。
