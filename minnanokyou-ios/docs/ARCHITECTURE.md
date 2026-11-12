# 設計メモ

更新：2026年11月12日（家族間の共有を実装）

## データの置き場所
| データ | 置き場所 | 共有 |
|---|---|---|
| 家族グループ、メンバー、ごはん・おくすり、済みの記録、持ち物、分担 | Core Data＋CloudKit（`CoreDataModel.swift`、`PersistenceController.swift`） | 家族全員 |
| 招待コード → 共有リンクの対応（24時間） | CloudKit の公開データベース（レコード型 `Invite`） | コードを知っている人 |
| この端末の役割（家族／ご本人）、名前、お知らせの設定 | UserDefaults | しない |

開発者（私たち）のサーバーは使いません。データは家族グループを作った人の iCloud に保存され、参加した人の iCloud からは「共有」として見えます。

## 家族間の共有のしくみ
1. 家族グループを作った人の端末：`PersistenceController` の**非公開の保存先**に家族グループ（Household）を作る。ごはん・済みの記録などは、すべて Household との関係（relationship）でつながっている。
2. 「家族を招待する」→ `FamilySharing.makeInvite`
   - Household を `NSPersistentCloudKitContainer.share` で共有（CKShare）し、共有リンク（URL）を作る。`publicPermission = .readWrite`（リンクを知っている人が参加できる）。
   - 6けたのコードを作り、公開データベースに `Invite`（レコード名 `invite-123456`、`url`、`expires`＝24時間後）を保存。
3. 参加する人の端末：「招待コードを入力する」→ `FamilySharing.join`
   - `Invite` を読み、期限を確かめ、`CKContainer.shareMetadata(for:)` → `acceptShareInvitations(into: 共有の保存先)`。
   - iCloud から家族グループが届くまで「読み込んでいます」と表示。
4. 共有リンクを直接開いた場合は `SceneDelegate.windowScene(_:userDidAcceptCloudKitShareWith:)` で受け入れる。
5. 参加した人が追加する「済み」なども、`PersistenceController.insert(_:into:)` で家族グループと同じ保存先（共有）に入るので、家族全員に届く。

## お知らせ
- `NotificationPlanner`（純粋な関数）で「何時に・誰に・何を」を決め、`NotificationScheduler.refresh` がローカル通知として登録する。アプリが前面に来たとき、「済み」にしたとき、ほかの家族の変更を受け取ったときに組み直す。
- **「済み」の連絡**：`RemoteChangeNotifier` が CloudKit からの取り込み（`NSPersistentStoreRemoteChange`）を見て、ほかの人が作った `DoneRecord` があれば、家族の端末に「〇〇が『…済み』にしました」を出す。自分の操作（`transactionAuthor = "app"`）は除く。
- 集中モード中でも届く通知には、Time Sensitive Notifications の権限が必要。`project.yml` に追加済み。

## セキュリティ上の注意（法務・セキュリティの確認が必要）
- 6けたのコードは 100万通りなので、当てずっぽうに入れて当たる可能性はゼロではない。対策として、有効期限を24時間にし、使用中のコードと重ならないようにし、作成者が参加者を確認・削除できる画面（Apple 標準の `UICloudSharingController`）を用意した。
- より安全にするなら、コードを8けた以上にする、参加者を作成者が承認する（`publicPermission = .none` にして個別に招待する）などが考えられる。使いやすさとの兼ね合いで、当事者家族と相談して決める。
- 公開データベースの `Invite` には共有リンクと期限しか入れない（名前や健康情報は入れない）。

## CloudKit Console で行う作業（公開前）
- コンテナ `iCloud.jp.minnanokyou.app` を作成
- 開発環境で一度動かしてスキーマ（Household などと `Invite`）を作り、**本番環境に反映（Deploy Schema Changes）**
- `Invite` のセキュリティロール：作成者だけが書き換えられ、全員が読めること（既定）を確認

## 未実装・要確認
- ご本人の「声メッセージ」、受診メモ PDF、写真つきカード、しまった場所メモ、共有範囲の設定（`Feature.isComingSoon`、画面では「準備中」）
- ロック画面ウィジェット（WidgetKit）
- 使い終わった `Invite` の削除（今は期限切れで使えなくなるだけ）
- 家族グループの削除・共有の停止の画面（Apple 標準の管理画面から共有の停止は可能）
- Assistive Access での表示確認
- **すべて Xcode でのビルドと、2台の実機（別々の Apple ID）での共有テストが未実施**
