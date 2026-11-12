import SwiftUI

/// 招待コードの入力。コードから共有リンクを取り出し、家族グループの共有を受け入れる（FamilySharing）。
struct InviteCodeView: View {
    @Environment(AppState.self) private var app
    @State private var code = ""
    @State private var role: DeviceRole?
    @State private var name = ""
    @State private var error: String?
    @State private var busy = false
    @FocusState private var focused: Bool

    var body: some View {
        VStack(alignment: .leading, spacing: 16) {
            Button("‹ 戻る") { app.route = .launch }.frame(minHeight: Theme.minTap)
            Text("招待コードを入力してください").font(.title2.bold())
            Text("ご家族から届いた8けたの数字です。").foregroundStyle(Theme.muted)
            TextField("8けたの数字", text: $code)
                .keyboardType(.numberPad).textContentType(.oneTimeCode)
                .font(.title.monospacedDigit().bold()).multilineTextAlignment(.center)
                .frame(minHeight: 56).background(.white, in: RoundedRectangle(cornerRadius: Theme.controlRadius))
                .overlay(RoundedRectangle(cornerRadius: Theme.controlRadius).stroke(Theme.control, lineWidth: 1.5))
                .focused($focused)
                .onChange(of: code) { _, v in code = String(v.filter(\.isNumber).prefix(FamilySharing.codeLength)) }
            Text("どちらで使いますか").bold()
            HStack {
                roleButton("ご本人として", .selfUser)
                roleButton("家族として", .family)
            }
            if role == .family { TextField("あなたのお名前", text: $name).textFieldStyle(.roundedBorder) }
            if let error { Text(error).foregroundStyle(Theme.warm).bold() }
            Spacer()
            if busy { ProgressView("参加しています…").frame(maxWidth: .infinity) }
            Button("参加する") { Task { await join() } }.buttonStyle(PrimaryButtonStyle()).disabled(busy)
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

    private func join() async {
        guard code.count == FamilySharing.codeLength else { error = "8けたの数字をすべて入れてください。"; return }
        guard let role else { error = "「ご本人として」か「家族として」を選んでください。"; return }
        if role == .family && name.trimmingCharacters(in: .whitespaces).isEmpty { error = "あなたのお名前を入れてください。"; return }
        busy = true; error = nil
        defer { busy = false }
        do { try await FamilySharing.shared.join(code: code) }
        catch { self.error = (error as? LocalizedError)?.errorDescription ?? "参加できませんでした。通信できる場所で、もう一度お試しください。"; return }
        app.role = role
        if role == .family { app.memberName = name }
        app.route = role == .family ? .familyHome : .selfBoard
        _ = await NotificationScheduler.shared.requestAuthorization()
        await NotificationScheduler.shared.refresh(role: role)
    }
}
