import Foundation
import StoreKit
import Observation

/// 有料プラン「みんなのきょう プラス」（docs/PRICING.md）。StoreKit 2 を使う。
/// 商品IDは App Store Connect で作る自動更新サブスクリプションと一致させること。
@Observable
@MainActor
final class SubscriptionStore {
    static let productIDs = ["jp.minnanokyou.plus.monthly", "jp.minnanokyou.plus.yearly"]
    private(set) var products: [Product] = []
    private(set) var isPlus = false
    private var updates: Task<Void, Never>?

    func start() async {
        updates = Task { for await r in Transaction.updates { await self.handle(r) } }
        products = (try? await Product.products(for: Self.productIDs))?.sorted { $0.price < $1.price } ?? []
        await refresh()
    }

    func refresh() async {
        var plus = false
        for await r in Transaction.currentEntitlements {
            if case .verified(let t) = r, Self.productIDs.contains(t.productID), t.revocationDate == nil { plus = true }
        }
        isPlus = plus
    }

    func buy(_ p: Product) async throws {
        let result = try await p.purchase()
        if case .success(let v) = result { await handle(v) }
    }

    func restore() async { try? await AppStore.sync(); await refresh() }

    private func handle(_ r: VerificationResult<Transaction>) async {
        if case .verified(let t) = r { await t.finish() }
        await refresh()
    }
}
