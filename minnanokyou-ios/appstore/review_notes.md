# 審査メモ（App Review への説明）

App Store Connect の「App Review に関する情報」→「メモ」に貼る。審査担当者向けに英語版も用意した。
更新：2026年11月12日（個人で申請する方針に合わせて改訂）

## 日本語
- 本アプリは、家族の予定と「ごはん・おくすり済み」の記録を、家族の間で共有するための生活支援アプリです。対象は、もの忘れが気になり始めた方（軽度認知症・MCI）とそのご家族です。
- **医療サービスではありません。** 診断・治療・予防・健康状態の判定の機能はありません。医療機関とのやり取りもありません。
- **計測をしません。** 血圧などの計測は行わず、HealthKit も使いません。
- **開発者はデータを預かりません。** データは利用者の iCloud（CloudKit）にだけ保存され、家族の間では iCloud の共有機能で共有されます。開発者のサーバーはありません。広告・解析ツールも入っていません。
- アプリ内とApp Storeの説明文に「診断や治療をするものではありません。健康や治療について判断するときは、医師にご相談ください。」と表示しています。
- 時間指定通知（Time Sensitive）は、デイサービスのお迎えの時刻とおくすりの時間を、集中モード中でも確実に知らせるために使います。
- 審査用の手順：
  1. 「家族として始める」から初回設定を終えると、家族のホームが開きます。
  2. 招待のテストには、2台目の端末（別の Apple ID）で「招待コードを入力する」に、1台目の「家族を招待する」で作った8けたのコードを入れてください。
  3. デモ用の家族グループの招待コード：[提出前に作成して記入。24時間で期限切れになるため、提出直前に作る]

## English
- Minna no Kyou is a daily-life app that lets family members share schedules and "meal / medicine done" check-offs with an older family member who has early memory concerns (mild cognitive impairment or mild dementia).
- **It is not a healthcare service.** It provides no diagnosis, treatment, prevention, or assessment features, and does not connect to any healthcare provider.
- **No measurements.** The app does not measure any health data and does not use HealthKit.
- **The developer does not collect or store user data.** All data is stored only in the user's own iCloud (CloudKit) and shared within the family through CloudKit sharing. There is no developer server, no advertising, and no analytics SDK.
- The app and the App Store description state that it does not diagnose or treat any condition and that users should consult a doctor for health decisions.
- Time Sensitive notifications are used only for the day-service pickup time and medicine times, so they reach the family even in a Focus mode.
- How to review:
  1. Tap "家族として始める" (Start as family) and finish the short setup to reach the family home.
  2. To test joining, on a second device with a different Apple ID, tap "招待コードを入力する" (Enter invite code) and enter the 8-digit code created from "家族を招待する" (Invite family) on the first device.
  3. Demo invite code: [create right before submission; codes expire after 24 hours]
