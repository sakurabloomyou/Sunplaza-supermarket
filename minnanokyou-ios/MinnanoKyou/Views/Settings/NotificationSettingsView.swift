import SwiftUI

struct NotificationSettingsView: View {
    @AppStorage("notificationSettings") private var raw: Data = (try? JSONEncoder().encode(NotificationSettings())) ?? Data()
    private var settings: Binding<NotificationSettings> {
        Binding(get: { (try? JSONDecoder().decode(NotificationSettings.self, from: raw)) ?? NotificationSettings() },
                set: { raw = (try? JSONEncoder().encode($0)) ?? Data() })
    }
    var body: some View {
        Form {
            Section {
                Toggle(isOn: settings.dayBefore) { row("お迎えの前日", "19:00 に、明日のお迎えをお知らせ", "ご本人・家族") }
                Toggle(isOn: settings.hourBefore) { row("お迎えの1時間前", "持ち物の確認もいっしょに", "ご本人・家族") }
                Toggle(isOn: settings.atPickup) { row("お迎えの時刻", "ご本人には大きくお知らせ", "ご本人・家族") }
                Toggle(isOn: settings.medication) { row("おくすりの時間", "済みになっていなければお知らせ", "ご本人") }
                Toggle(isOn: settings.doneReport) { row("「済み」の連絡", "ほかの家族が済みにしたとき", "家族") }
                Toggle(isOn: settings.notDoneYet) { row("まだ済んでいないとき", "予定の30分後にお知らせ", "家族") }
            } footer: { Text("オフにしたお知らせは、ロック画面にも出ません。") }
            Section("大事なお知らせの届け方") {
                Toggle(isOn: settings.timeSensitive) {
                    row("集中モード中でも届ける", "お迎えの1時間前・時刻、おくすり、まだ済んでいないときが対象です", nil)
                }
                Text("マナーモードでも音を鳴らす「緊急通知」は、Appleの審査で認められたアプリしか使えません。").font(.footnote).foregroundStyle(Theme.muted)
            }
        }
        .navigationTitle("お知らせの設定")
    }
    private func row(_ t: String, _ d: String, _ to: String?) -> some View {
        VStack(alignment: .leading, spacing: 2) {
            if let to { Text("\(to)へ").font(.caption.bold()).foregroundStyle(Theme.accentHex) }
            Text(t).bold(); Text(d).font(.footnote).foregroundStyle(Theme.muted)
        }
    }
}
