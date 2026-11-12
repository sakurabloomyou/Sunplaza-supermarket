import SwiftUI
import SwiftData

/// 招待コードの入力。家族グループへの参加は CloudKit の共有（CKShare）で行う想定。
/// v1 では「コード → 共有URL」の対応表が必要（docs/ARCHITECTURE.md）。
struct InviteCodeView: View {
    @Environment(AppState.self) private var app
    @State private var code = ""
    @State private var role: DeviceRole?
    @State private var name = ""
    @State private var error: String?
    @FocusState private var focused: Bool

    var body: some View {
        VStack(alignment: .leading, spacing: 16) {
            Button("‹ 戻る") { app.route = .launch }.frame(minHeight: Theme.minTap)
            Text("招待コードを入力してください").font(.title2.bold())
            Text("ご家族から届いた6けたの数字です。").foregroundStyle(Theme.muted)
            TextField("6けたの数字", text: $code)
                .keyboardType(.numberPad).textContentType(.oneTimeCode)
                .font(.title.monospacedDigit().bold()).multilineTextAlignment(.center)
                .frame(minHeight: 56).background(.white, in: RoundedRectangle(cornerRadius: Theme.controlRadius))
                .overlay(RoundedRectangle(cornerRadius: Theme.controlRadius).stroke(Theme.control, lineWidth: 1.5))
                .focused($focused)
                .onChange(of: code) { _, v in code = String(v.filter(\.isNumber).prefix(6)) }
            Text("どちらで使いますか").bold()
            HStack {
                roleButton("ご本人として", .selfUser)
                roleButton("家族として", .family)
            }
            if role == .family { TextField("あなたのお名前", text: $name).textFieldStyle(.roundedBorder) }
            if let error { Text(error).foregroundStyle(Theme.warm).bold() }
            Spacer()
            Button("参加する") { join() }.buttonStyle(PrimaryButtonStyle())
        }
        .padding(20)
        .onAppear { focused = true }
    }

    private func roleButton(_ title: String, _ r: DeviceRole) -> some View {
        Button(title) { role = r }
            .frame(maxWidth: .infinity, minHeight: Theme.minTap)
            .background(role == r ? Theme.accentHex : .clear, in: RoundedRectangle(cornerRadius: Theme.controlRadius))
            .foregroundStyle(role == r ? .white : .primary)
            .overlay(RoundedRectangle(cornerRadius: Theme.controlRadius).stroke(Theme.control, lineWidth: 1.5))
    }

    private func join() {
        guard code.count == 6 else { error = "6けたの数字をすべて入れてください。"; return }
        guard let role else { error = "「ご本人として」か「家族として」を選んでください。"; return }
        // TODO(v1): HouseholdSync.join(code:) で共有を受け入れる。
        app.role = role
        if role == .family { app.memberName = name }
        app.route = role == .family ? .familyHome : .selfBoard
        Task { _ = await NotificationScheduler.shared.requestAuthorization() }
    }
}
