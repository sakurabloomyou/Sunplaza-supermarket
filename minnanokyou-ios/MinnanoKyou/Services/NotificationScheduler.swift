import Foundation
import UserNotifications

/// NotificationPlanner の結果を、iPhone のローカル通知として登録する。
@MainActor
final class NotificationScheduler {
    static let shared = NotificationScheduler()
    private let center = UNUserNotificationCenter.current()

    func requestAuthorization() async -> Bool {
        (try? await center.requestAuthorization(options: [.alert, .sound, .badge])) ?? false
    }

    /// 保存されている家族グループの内容から、今日と明日のお知らせを組み直す。
    /// アプリが前面に来たとき、「済み」にしたとき、ほかの家族の変更を受け取ったときに呼ぶ。
    func refresh(role: DeviceRole?) async {
        guard let role, let h = PersistenceController.shared.currentHousehold() else { return }
        let answers = h.answers
        let today = Date().dayKey
        let doneKeys = Set(((h.doneRecords as? Set<DoneRecord>) ?? []).filter { $0.day == today }.compactMap(\.itemKey))
        let weekdaySymbol = ["日","月","火","水","木","金","土"][Calendar.current.component(.weekday, from: Date()) - 1]
        let duty = h.dutyList.first { $0.when == weekdaySymbol && !($0.assignee ?? "").isEmpty }?.assignee
        let items = h.itemList.map { (key: $0.key ?? "", title: $0.title ?? "", minutes: Int($0.minutes), isMedication: $0.isMedication) }
        let plan = NotificationPlanner.plan(role: role, settings: RemoteChangeNotifier.loadSettings(), selfName: h.displaySelfName,
                                            pickup: answers.usesDayService ? Int(h.pickupMinutes) : nil, dutyName: duty, items: items)
        await reschedule(plan, doneKeys: doneKeys, pickupWeekdays: answers.dayServiceWeekdays)
    }

    /// 今日と明日の分を登録し直す。「済み」になった項目の「まだです」「おくすり」通知は外す。
    func reschedule(_ plan: [PlannedNotification], doneKeys: Set<String>, pickupWeekdays: Set<Int>) async {
        center.removeAllPendingNotificationRequests()
        let cal = Calendar.current
        let today = cal.startOfDay(for: Date())
        for dayOffset in 0...1 {
            guard let base = cal.date(byAdding: .day, value: dayOffset, to: today) else { continue }
            let weekday = cal.component(.weekday, from: base)
            for n in plan {
                if n.id.hasPrefix("pickup") {
                    // 前日のお知らせは「翌日がデイの日」かどうかで判断
                    let target = n.id == "pickup.prev" ? (weekday % 7) + 1 : weekday
                    if !pickupWeekdays.contains(target) { continue }
                }
                if dayOffset == 0, n.id.hasPrefix("late."), doneKeys.contains(String(n.id.dropFirst(5))) { continue }
                if dayOffset == 0, n.id.hasPrefix("med."), doneKeys.contains(String(n.id.dropFirst(4))) { continue }
                guard let fire = cal.date(byAdding: .minute, value: n.minutes, to: base), fire > Date() else { continue }
                let content = UNMutableNotificationContent()
                content.title = "みんなのきょう"
                content.body = n.body
                content.sound = .default
                content.interruptionLevel = n.timeSensitive ? .timeSensitive : .active
                let comps = cal.dateComponents([.year, .month, .day, .hour, .minute], from: fire)
                let req = UNNotificationRequest(identifier: "\(n.id).\(dayOffset)", content: content,
                                                trigger: UNCalendarNotificationTrigger(dateMatching: comps, repeats: false))
                try? await center.add(req)
            }
        }
    }
}
