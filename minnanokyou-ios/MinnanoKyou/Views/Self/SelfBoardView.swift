import SwiftUI
import CoreData

/// ご本人の画面。大きな文字で「いま」「つぎ」「きょうのみんな」。ボタンは1つだけ。
struct SelfBoardView: View {
    @Environment(AppState.self) private var app
    @FetchRequest(sortDescriptors: [NSSortDescriptor(key: "createdAt", ascending: true)]) private var households: FetchedResults<Household>
    private let pc = PersistenceController.shared

    var body: some View {
        if let h = households.first(where: { $0.objectID.persistentStore == pc.sharedStore }) ?? households.first {
            SelfBoardContent(household: h)
        } else {
            ContentUnavailableView("ご家族の予定を読み込んでいます", systemImage: "icloud.and.arrow.down",
                                   description: Text("少し待ってから、もう一度開いてください。"))
        }
    }
}

private struct SelfBoardContent: View {
    @Environment(AppState.self) private var app
    @ObservedObject var household: Household
    @FetchRequest private var done: FetchedResults<DoneRecord>
    private let pc = PersistenceController.shared

    init(household: Household) {
        self.household = household
        _done = FetchRequest(sortDescriptors: [], predicate: NSPredicate(format: "household == %@ AND day == %@", household, Date().dayKey))
    }

    var body: some View {
        TimelineView(.everyMinute) { tl in
            let now = tl.date.minutesOfDay
            let doneKeys = Set(done.compactMap(\.itemKey))
            let nowItem = household.itemList.first { !doneKeys.contains($0.key ?? "") && Int($0.minutes) <= now + 60 }
            ScrollView {
                VStack(alignment: .leading, spacing: 14) {
                    VStack(alignment: .leading) {
                        Text("きょうは").font(.headline).foregroundStyle(Theme.muted)
                        Text(tl.date.formatted(.dateTime.month().day().weekday(.wide).locale(Locale(identifier: "ja_JP"))))
                            .font(.largeTitle.bold())
                    }
                    Card(fill: Theme.accentSoft) {
                        Text("いま").font(.headline).foregroundStyle(Theme.muted)
                        Text(nowItem.map { "\($0.title ?? "")の時間です" } ?? "ゆっくり過ごしましょう").font(.title.bold())
                    }
                    if let nowItem {
                        Button("\(nowItem.title ?? "")を「済み」にする") {
                            pc.markDone(nowItem, in: household, by: household.displaySelfName)
                            Task { await NotificationScheduler.shared.refresh(role: app.role) }
                        }
                        .buttonStyle(PrimaryButtonStyle())
                    }
                    if household.answers.usesDayService {
                        let left = Int(household.pickupMinutes) - now
                        Card(fill: Theme.warmSoft) {
                            Text("つぎ").font(.headline).foregroundStyle(Theme.muted)
                            Text(left > 0 ? "\(household.pickupMinutes.hm)　デイサービスのお迎え\nあと\(left)分"
                                 : now < Int(household.returnMinutes) ? "\(household.returnMinutes.hm)　デイサービスから\nおうちに帰ります" : "ゆっくり休みましょう")
                                .font(.title.bold())
                        }
                    }
                    Card {
                        Text("きょうのみんな").font(.headline).foregroundStyle(Theme.muted)
                        ForEach(household.memberList.filter { !$0.isSelf }) { m in
                            HStack { Text(m.name ?? "").bold().foregroundStyle(Theme.accentHex); Spacer(); Text(m.returnTime ?? "") }.font(.title3)
                        }
                    }
                }
                .padding(20)
            }
            .dynamicTypeSize(.large ... .accessibility3)
        }
    }
}
