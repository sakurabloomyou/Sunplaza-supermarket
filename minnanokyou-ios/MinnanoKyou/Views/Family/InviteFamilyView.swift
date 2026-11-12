import SwiftUI
import CloudKit
import UIKit

/// 家族を招待する画面。8けたのコード（24時間有効）を作り、参加している人を確認できる。
struct InviteFamilyView: View {
    @ObservedObject var household: Household
    @State private var invite: FamilySharing.Invite?
    @State private var busy = false
    @State private var error: String?
    @State private var showManage = false

    var body: some View {
        List {
            Section {
                if let invite {
                    VStack(spacing: 8) {
                        // 読み間違えないよう 4けたずつ区切って表示（入力は8けた続けて）
                        Text("\(invite.code.prefix(4)) \(invite.code.suffix(4))").font(.system(size: 40, weight: .bold, design: .rounded)).monospacedDigit()
                            .accessibilityLabel(invite.code.map(String.init).joined(separator: " "))
                        Text("\(invite.expires.formatted(date: .abbreviated, time: .shortened)) まで使えます").font(.footnote).foregroundStyle(Theme.muted)
                    }.frame(maxWidth: .infinity).padding(.vertical, 8)
                    ShareLink(item: "「みんなのきょう」の招待コード：\(invite.code)（24時間有効）\nアプリを開いて「招待コードを入力する」に入れてください。") {
                        Label("コードを送る", systemImage: "square.and.arrow.up")
                    }
                } else {
                    Text("ご家族やご本人のiPhoneで入力する、8けたのコードを作ります。コードは24時間だけ使えます。")
                }
                Button(invite == nil ? "招待コードを作る" : "新しいコードを作る") { Task { await make() } }
                    .disabled(busy)
                if busy { ProgressView() }
                if let error { Text(error).foregroundStyle(Theme.warm) }
            }
            Section("参加している人") {
                let names = FamilySharing.shared.participantNames(for: household)
                if names.isEmpty { Text("まだ誰も参加していません").foregroundStyle(Theme.muted) }
                ForEach(names, id: \.self) { Text($0) }
                if FamilySharing.shared.isOwner(of: household), FamilySharing.shared.existingShare(for: household) != nil {
                    Button("参加している人を管理する") { showManage = true }
                }
            }
            Section {
                Text("コードを知っている人は、iCloud にサインインしていれば参加できます。コードは家族だけに送ってください。知らない人が参加していたら、「参加している人を管理する」から外せます。")
                    .font(.footnote).foregroundStyle(Theme.muted)
            }
        }
        .navigationTitle("家族を招待する")
        .sheet(isPresented: $showManage) {
            if let share = FamilySharing.shared.existingShare(for: household) {
                CloudSharingView(share: share, container: CKContainer(identifier: PersistenceController.containerID))
            }
        }
    }

    private func make() async {
        busy = true; error = nil
        defer { busy = false }
        do { invite = try await FamilySharing.shared.makeInvite(for: household) }
        catch { self.error = (error as? LocalizedError)?.errorDescription ?? "招待コードを作れませんでした。通信できる場所で、もう一度お試しください。" }
    }
}

/// Apple 標準の「共有の管理」画面（参加者の確認・削除、共有の停止）。
struct CloudSharingView: UIViewControllerRepresentable {
    let share: CKShare
    let container: CKContainer
    func makeUIViewController(context: Context) -> UICloudSharingController {
        let c = UICloudSharingController(share: share, container: container)
        c.availablePermissions = [.allowReadWrite, .allowPrivate]
        return c
    }
    func updateUIViewController(_ vc: UICloudSharingController, context: Context) {}
}
