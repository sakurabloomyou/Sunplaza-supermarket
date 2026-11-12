import CoreData
import CloudKit

/// 家族グループの共有と、8けたの招待コード。
///
/// しくみ：
/// 1. 家族グループ（Household）を CKShare で共有し、共有リンク（URL）を作る
/// 2. 8けたのコード → 共有リンク の対応を、CloudKit の「公開」データベースに 24 時間だけ置く
/// 3. 参加する人はコードを入れる → 共有リンクを取り出す → 共有を受け入れる
///
/// 注意（法務・セキュリティの確認が必要）：
/// - 共有リンクを知っている iCloud ユーザーは誰でも参加できる設定（publicPermission = .readWrite）にしている。
///   8けた（1億通り）でも当てずっぽうで当たる可能性はゼロではないため、有効期限（24時間）を短くし、
///   家族グループの作成者が参加者を確認・削除できる画面（CloudSharingView）を用意している。
@MainActor
final class FamilySharing {
    static let shared = FamilySharing()
    static let inviteLifetime: TimeInterval = 24 * 60 * 60
    static let codeLength = 8

    struct Invite: Equatable { let code: String; let expires: Date; let url: URL }
    enum JoinError: LocalizedError {
        case notFound, expired, noICloud
        var errorDescription: String? {
            switch self {
            case .notFound: "このコードは見つかりませんでした。数字をもう一度確かめてください。"
            case .expired: "このコードは有効期限（24時間）が切れています。ご家族に新しいコードを作ってもらってください。"
            case .noICloud: "iCloud にサインインしてください。iPhone の「設定」の一番上から行えます。"
            }
        }
    }

    private let pc: PersistenceController
    private let ck: CKContainer
    init(pc: PersistenceController = .shared) {
        self.pc = pc
        self.ck = CKContainer(identifier: PersistenceController.containerID)
    }

    func existingShare(for h: Household) -> CKShare? {
        (try? pc.container.fetchShares(matching: [h.objectID]))?[h.objectID]
    }

    /// 自分が作った家族グループか（招待されて参加したものではないか）。
    func isOwner(of h: Household) -> Bool { h.objectID.persistentStore == pc.privateStore }

    /// 招待コードを作る（共有がまだなければ作る）。
    func makeInvite(for h: Household) async throws -> Invite {
        guard try await ck.accountStatus() == .available else { throw JoinError.noICloud }
        var share = existingShare(for: h)
        if share == nil {
            let (_, s, _) = try await pc.container.share([h], to: nil)
            share = s
        }
        guard var s = share else { throw JoinError.notFound }
        if s.publicPermission != .readWrite || s[CKShare.SystemFieldKey.title] == nil {
            s[CKShare.SystemFieldKey.title] = "みんなのきょう" as CKRecordValue
            s.publicPermission = .readWrite
            s = try await pc.container.persistUpdatedShare(s, in: pc.privateStore)
        }
        guard let url = s.url else { throw JoinError.notFound }

        let db = ck.publicCloudDatabase
        let expires = Date().addingTimeInterval(Self.inviteLifetime)
        for _ in 0..<5 {
            let code = String(format: "%08d", Int.random(in: 0...99_999_999))
            let id = CKRecord.ID(recordName: "invite-\(code)")
            if let old = try? await db.record(for: id),
               let exp = old["expires"] as? Date, exp > Date() { continue }   // 使用中のコードは避ける
            let rec = CKRecord(recordType: "Invite", recordID: id)
            rec["url"] = url.absoluteString as CKRecordValue
            rec["expires"] = expires as CKRecordValue
            _ = try await db.modifyRecords(saving: [rec], deleting: [], savePolicy: .allKeys)
            return Invite(code: code, expires: expires, url: url)
        }
        throw JoinError.notFound
    }

    /// 招待コードで参加する。
    func join(code: String) async throws {
        guard try await ck.accountStatus() == .available else { throw JoinError.noICloud }
        let id = CKRecord.ID(recordName: "invite-\(code)")
        guard let rec = try? await ck.publicCloudDatabase.record(for: id),
              let s = rec["url"] as? String, let url = URL(string: s) else { throw JoinError.notFound }
        if let exp = rec["expires"] as? Date, exp < Date() { throw JoinError.expired }
        let metadata = try await ck.shareMetadata(for: url)
        try await accept(metadata)
    }

    /// 共有リンクから開かれたとき（SceneDelegate）にも使う。
    func accept(_ metadata: CKShare.Metadata) async throws {
        _ = try await pc.container.acceptShareInvitations(from: [metadata], into: pc.sharedStore)
    }

    /// 参加している人の名前（iCloud のアカウント名）。
    func participantNames(for h: Household) -> [String] {
        guard let share = existingShare(for: h) else { return [] }
        return share.participants.compactMap { p in
            p.userIdentity.nameComponents.map { PersonNameComponentsFormatter().string(from: $0) }
        }
    }
}
