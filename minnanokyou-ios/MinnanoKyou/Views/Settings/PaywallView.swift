import SwiftUI
import StoreKit

/// 有料プランの説明と購入（docs/PRICING.md の案）。
/// 基本機能（予定共有・済みチェック・お知らせ・ご本人の画面）は無料のまま。
struct PaywallView: View {
    @Environment(SubscriptionStore.self) private var store
    @State private var error: String?
    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 16) {
                Text("みんなのきょう プラス").font(.largeTitle.bold())
                Text("毎日の見守りに必要な機能は、ずっと無料です。プラスでは、記録や共有をもっと便利にできます。").foregroundStyle(Theme.muted)
                Card {
                    ForEach(["家族を5人以上招待（最大10人）","ご本人を2人まで（ご両親など）","記録を期間の制限なく保存","受診メモをPDFで作成","写真つきの持ち物・手順カード","家族の声メッセージ","しまった場所メモ","ケアマネ・デイサービスとの共有範囲の設定"], id: \.self) {
                        Label($0, systemImage: "checkmark.circle.fill").foregroundStyle(Theme.accentHex)
                    }
                }
                if store.isPlus {
                    Text("プラスをご利用中です。").bold()
                } else {
                    ForEach(store.products, id: \.id) { p in
                        Button("\(p.displayName)　\(p.displayPrice)") { Task { do { try await store.buy(p) } catch { self.error = "購入できませんでした。時間をおいて、もう一度お試しください。" } } }
                            .buttonStyle(PrimaryButtonStyle())
                    }
                    if store.products.isEmpty { Text("料金を読み込めませんでした。通信できる場所でもう一度開いてください。").foregroundStyle(Theme.muted) }
                }
                Button("購入を復元する") { Task { await store.restore() } }.frame(minHeight: Theme.minTap)
                if let error { Text(error).foregroundStyle(Theme.warm) }
                Text("サブスクリプションは期間終了の24時間前までに解約しない限り、自動で更新されます。解約は iPhone の「設定」>「Apple ID」>「サブスクリプション」から行えます。")
                    .font(.footnote).foregroundStyle(Theme.muted)
                HStack { Link("利用規約", destination: URL(string: "https://example.com/terms")!); Link("プライバシーポリシー", destination: URL(string: "https://example.com/privacy")!) }
                    .font(.footnote)
            }.padding(20)
        }
    }
}
