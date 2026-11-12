import SwiftUI
import SwiftData

/// ご本人の画面。大きな文字で「いま」「つぎ」「きょうのみんな」。ボタンは1つだけ。
struct SelfBoardView: View {
    @Environment(\.modelContext) private var ctx
    @Query private var households: [Household]
    @Query private var items: [DailyItem]
    @Query private var done: [DoneRecord]
    @Query private var members: [Member]

    var body: some View {
        TimelineView(.everyMinute) { tl in
            let now = tl.date.minutesOfDay
            let h = households.first
            let today = tl.date.dayKey
            let doneToday = Set(done.filter { $0.day == today }.map(\.itemKey))
            let nowItem = items.sorted { $0.order < $1.order }.first { !doneToday.contains($0.key) && $0.minutes <= now + 60 }
            ScrollView {
                VStack(alignment: .leading, spacing: 14) {
                    VStack(alignment: .leading) {
                        Text("きょうは").font(.headline).foregroundStyle(Theme.muted)
                        Text(tl.date.formatted(.dateTime.month().day().weekday(.wide).locale(Locale(identifier: "ja_JP"))))
                            .font(.largeTitle.bold())
                    }
                    Card(fill: Theme.accentSoft) {
                        Text("いま").font(.headline).foregroundStyle(Theme.muted)
                        Text(nowItem.map { "\($0.title)の時間です" } ?? "ゆっくり過ごしましょう").font(.title.bold())
                    }
                    if let nowItem, let h {
                        Button("\(nowItem.title)を「済み」にする") {
                            ctx.insert(DoneRecord(householdID: h.id, itemKey: nowItem.key, day: today, by: h.selfName))
                        }
                        .buttonStyle(PrimaryButtonStyle())
                        .font(.title2.bold())
                    }
                    if let h, h.answers.usesDayService {
                        let left = h.pickupMinutes - now
                        Card(fill: Theme.warmSoft) {
                            Text("つぎ").font(.headline).foregroundStyle(Theme.muted)
                            Text(left > 0 ? "\(h.pickupMinutes.hm)　デイサービスのお迎え\nあと\(left)分"
                                 : now < h.returnMinutes ? "\(h.returnMinutes.hm)　デイサービスから\nおうちに帰ります" : "ゆっくり休みましょう")
                                .font(.title.bold())
                        }
                    }
                    Card {
                        Text("きょうのみんな").font(.headline).foregroundStyle(Theme.muted)
                        ForEach(members.filter { !$0.isSelf }) { m in
                            HStack { Text(m.name).bold().foregroundStyle(Theme.accentHex); Spacer(); Text(m.returnTime) }.font(.title3)
                        }
                    }
                }
                .padding(20)
            }
            .dynamicTypeSize(.large ... .accessibility3)
        }
    }
}
