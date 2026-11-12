import Foundation

/// お知らせの設定（端末ごと）。試作の「お知らせの設定」と同じ6種類＋時間指定。
struct NotificationSettings: Codable, Equatable {
    var dayBefore = true      // お迎えの前日 19:00
    var hourBefore = true     // お迎えの1時間前
    var atPickup = true       // お迎えの時刻
    var medication = true     // おくすりの時間（ご本人へ）
    var doneReport = true     // 「済み」の連絡（家族へ）
    var notDoneYet = true     // まだ済んでいないとき（家族へ、30分後）
    var timeSensitive = true  // 集中モード中でも届ける
}

struct PlannedNotification: Equatable, Identifiable {
    let id: String
    let minutes: Int          // その日の0時からの分（前日は負の値）
    let body: String
    let timeSensitive: Bool
}

/// どの端末に、何時に、どんな文面を出すかを決める（UI や通知 API に依存しない純粋な関数）。
enum NotificationPlanner {
    static func plan(role: DeviceRole, settings s: NotificationSettings, selfName: String,
                     pickup: Int?, dutyName: String?, items: [(key: String, title: String, minutes: Int, isMedication: Bool)]) -> [PlannedNotification] {
        var out: [PlannedNotification] = []
        let fam = role == .family
        if let p = pickup {
            if s.dayBefore {
                out.append(.init(id: "pickup.prev", minutes: 19*60 - 24*60,
                    body: fam ? "明日 \(p.hm) に、\(selfName)のデイサービスのお迎えがあります"
                              : "あしたは デイサービスの日です。\(p.hm) にお迎えが来ます", timeSensitive: false))
            }
            if s.hourBefore {
                out.append(.init(id: "pickup.h1", minutes: p - 60,
                    body: fam ? "お迎えまで、あと1時間です。持ち物を確かめましょう"
                              : "あと1時間で、デイサービスのお迎えです。持ち物をたしかめましょう", timeSensitive: s.timeSensitive))
            }
            if s.atPickup {
                let who = dutyName.map { "今日の送り出しは \($0)さんです" } ?? "送り出しの担当はまだ決まっていません"
                out.append(.init(id: "pickup.at", minutes: p,
                    body: fam ? "お迎えの時間です。\(who)" : "デイサービスのお迎えの時間です", timeSensitive: s.timeSensitive))
            }
        }
        if !fam && s.medication {
            for it in items where it.isMedication {
                out.append(.init(id: "med.\(it.key)", minutes: it.minutes,
                    body: "\(it.title)の時間です。のんだら「済み」をおしてください", timeSensitive: s.timeSensitive))
            }
        }
        if fam && s.notDoneYet {
            for it in items {
                out.append(.init(id: "late.\(it.key)", minutes: it.minutes + 30,
                    body: "「\(it.title)」が、まだ済みになっていません（\(it.minutes.hm)の予定）", timeSensitive: s.timeSensitive))
            }
        }
        return out.sorted { $0.minutes < $1.minutes }
    }

    /// 「済み」の連絡の文面（家族の端末に、ほかの人が済みにしたとき）
    static func doneBody(by: String, title: String) -> String { "\(by)が「\(title) 済み」にしました" }
}
