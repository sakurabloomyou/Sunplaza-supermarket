# 無料の Apple ID で試作アプリを作る手順

作成：2026年11月15日。Mac を持っている人向け。**この手順は、まだ実機で通しで確かめていません**（作成した環境に Mac がないため）。つまずいたら、画面の写真かエラー文を共有してください。

## この試作版でできること・できないこと
| | 試作版（無料の Apple ID） | 通常版（Apple Developer Program 登録後） |
|---|---|---|
| 初回設定（悩みを選ぶ）、家族のホーム、ご本人の画面、済みチェック、分担表 | ○（その iPhone の中だけ） | ○ |
| iPhone へのお知らせ（前日・1時間前・お迎え・おくすり・まだです） | ○（集中モード中は届かない） | ○（集中モード中も届く） |
| 家族の招待・家族の間での共有 | **×** | ○ |
| 使える期間 | **7日**（過ぎたら Mac からもう一度入れ直す） | 最長1年（開発用） |
| 入れられる iPhone | 自分の端末（3台まで） | 登録した端末 |

家族の共有を試せないため、試作版では「1台の iPhone で、家族の画面とご本人の画面を切り替えて」試します（家族のホームの「ご本人の画面を見る」）。

## 用意するもの
- MacBook（新しめの macOS）
- iPhone と、Mac につなぐケーブル
- Apple ID（ふだん使っているもので可）
- インターネット（Xcode のダウンロードは大きく、時間がかかります）

---

## 1. Xcode を入れる（30分〜数時間）
1. Mac の「App Store」で **Xcode** を検索して入手（無料）。
2. Xcode を起動。追加の部品を聞かれたら「Install」。
3. 起動画面で iOS のプラットフォーム（シミュレーター）を入れるよう聞かれたら入れる。後からでも Xcode のメニュー「Xcode」→「Settings…」→「Components」で入れられる。

## 2. Xcode に Apple ID を登録する
1. Xcode のメニュー「Xcode」→「Settings…」→「Accounts」。
2. 左下の「＋」→「Apple ID」→ サインイン。
3. 一覧に「（あなたの名前）(Personal Team)」が出れば OK。

## 3. XcodeGen を入れる（5〜10分）
「ターミナル」（アプリケーション → ユーティリティ）を開き、1行ずつ貼り付けて Enter。

Homebrew が入っていなければ、先に入れる（https://brew.sh/ の方法）：
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```
終わりに表示される「Next steps」の2行（`echo ... >> ~/.zprofile` など）も、表示どおりに実行する。

XcodeGen を入れる：
```bash
brew install xcodegen
```

## 4. コードを取ってくる
ブラウザで次を開き、緑の「Code」→「Download ZIP」：
https://github.com/sakurabloomyou/Sunplaza-supermarket/tree/claude/fervent-carson-qe1vli

ダウンロードした ZIP をダブルクリックで開く。中の **`minnanokyou-ios`** フォルダを使う。
（リポジトリが非公開の場合は、GitHub にサインインして見られる人がダウンロードし、ZIP を渡してください）

## 5. 試作版のプロジェクトを作る
ターミナルで `cd ` と入力し（cd の後にスペース1つ）、`minnanokyou-ios` フォルダをターミナルの画面にドラッグして Enter。続けて：
```bash
xcodegen generate --spec project-free.yml
```
`MinnanoKyou.xcodeproj` ができたら：
```bash
open MinnanoKyou.xcodeproj
```
**注意**：`--spec project-free.yml` を付け忘れると通常版になり、無料の Apple ID では署名で止まります。

## 6. 署名を設定する
1. Xcode 左の一覧の一番上「MinnanoKyou」（青いアイコン）をクリック。
2. 中央の「TARGETS」で「MinnanoKyou」を選び、「Signing & Capabilities」タブ。
3. 「Automatically manage signing」にチェック。
4. 「Team」で「（あなたの名前）(Personal Team)」を選ぶ。
5. 「Bundle Identifier」を、ほかと重ならない名前に変える。例：`jp.yamada.minnanokyou`（英数字と「.」だけ）。
6. 赤いエラーが消えれば OK。
7. 「MinnanoKyouTests」というターゲットにも同じく Team を設定する（テストを動かす場合）。

## 7. まずシミュレーターで動かす（おすすめ）
1. Xcode 上部の端末の選択欄で「iPhone 16」など、シミュレーターを選ぶ。
2. **⌘B**（command＋B）でビルド。成功すると上に「Build Succeeded」。
3. **⌘R** で起動。仮想の iPhone に、スプラッシュ → 起動画面が出る。
4. **⌘U** でテスト。左の◇のアイコンの一覧で、緑なら成功。

## 8. 自分の iPhone に入れる
1. iPhone をケーブルで Mac につなぐ。iPhone に「このコンピュータを信頼しますか？」が出たら「信頼」。
2. iPhone の「設定」→「プライバシーとセキュリティ」→ 一番下の「**デベロッパモード**」をオン → 再起動 → 再起動後の確認で「オンにする」。
   （出てこない場合は、一度 Xcode で iPhone を選んでビルドすると表示されます。Apple の説明：https://developer.apple.com/documentation/xcode/enabling-developer-mode-on-a-device ）
3. Xcode 上部の端末の選択欄で、自分の iPhone を選ぶ。
4. **⌘R**。初回は iPhone 側で「信頼されていないデベロッパ」と出ることがある。そのときは iPhone の「設定」→「一般」→「VPNとデバイス管理」→ 自分の Apple ID →「信頼」。
5. もう一度 ⌘R。iPhone にアプリが入り、起動する。
6. お知らせの許可を聞かれたら「許可」。

**7日たつと起動できなくなります。** そのときは、Mac につないで手順8の3〜5（⌘R）をもう一度行えば、また7日使えます（データは残ります）。

## 9. 試してほしいこと（チェック表）
- ☐ 起動画面 →「家族として始める」→ 初回設定を最後まで進められるか（約3分）
- ☐ 結果画面で、選んだ悩みに合った機能が「★ オン」になっているか
- ☐ 家族のホームで「済みにする」を押すと、記録タブに出るか
- ☐ 「ご本人の画面を見る」で、大きな文字が読みやすいか。ボタンで「済み」にできるか
- ☐ 分担表に予定を追加し、「引き受ける」を押せるか
- ☐ お知らせ：おくすりの時刻などの少し前にアプリを開いておき、時刻に通知が届くか
- ☐ 文字の大きさ（iPhone の「設定」→「画面表示と明るさ」→「テキストサイズを変更」）を大きくしても崩れないか

## 10. エラーが出たら
- ビルドで止まったら、Xcode 左側の **赤い×のメッセージを全部コピー**（またはスクリーンショット）して共有してください。直したコードをブランチに送ります。
- 直したコードを使うときは、手順4（ZIP を取り直す）→ 手順5 → 手順6（Team と Bundle Identifier の設定し直し）→ ⌘R。
