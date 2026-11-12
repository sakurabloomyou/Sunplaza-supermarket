import SwiftUI
import SwiftData

struct FamilyHomeView: View {
    @Environment(AppState.self) private var app
    @Query private var households: [Household]
    var body: some View {
        if let h = households.first {
            TabView {
                NavigationStack { TodayTab(household: h) }
                    .tabItem { Label("きょう", systemImage: "calendar") }
                NavigationStack { LogTab(household: h) }
                    .tabItem { Label("記録", systemImage: "list.bullet") }
                NavigationStack { DutyTab(household: h) }
                    .tabItem { Label("分担", systemImage: "person.2") }
            }
            .tint(Theme.accentHex)
        } else {
            ContentUnavailableView("家族グループがまだありません", systemImage: "person.3",
                description: Text("最初の設定を終えるか、招待コードで参加してください。"))
        }
    }
}

struct TodayTab: View {
    @Environment(AppState.self) private var app
    @Environment(\.modelContext) private var ctx
    let household: Household
    @Query private var items: [DailyItem]
    @Query private var done: [DoneRecord]
    @Query private var pack: [PackItem]
    @State private var showPack = false

    init(household: Household) {
        self.household = household
        let id = household.id, day = Date().dayKey
        _items = Query(filter: #Predicate<DailyItem> { $0.householdID == id }, sort: \.order)
        _done = Query(filter: #Predicate<DoneRecord> { $0.householdID == id && $0.day == day })
        _pack = Query(filter: #Predicate<PackItem> { $0.householdID == id }, sort: \.order)
    }

    var body: some View {
        TimelineView(.everyMinute) { tl in
            let now = tl.date.minutesOfDay
            List {
                if household.answers.usesDayService { pickupSection(now: now) }
                Section("ごはん・おくすり") {
                    ForEach(items) { it in doneRow(it, now: now) }
                }
                let enabled = Feature.allCases.filter { household.answers.isOn($0) }
                if !enabled.isEmpty {
                    Section("ご家庭に合わせてオンにした機能") {
                        ForEach(enabled) { f in
                            HStack { Text(f.title); Spacer(); if f.isComingSoon { Text("準備中").font(.caption).foregroundStyle(Theme.muted) } }
                        }
                    }
                }
                Section {
                    NavigationLink("お知らせの設定") { NotificationSettingsView() }
                    Button("ご本人の画面を見る") { app.route = .selfBoard }
                    LabeledContent("招待コード", value: household.inviteCode)
                }
                Section { Disclaimer() }
            }
            .navigationTitle("きょう")
        }
    }

    private func pickupSection(now: Int) -> some View {
        let left = household.pickupMinutes - now
        let day = Date().dayKey
        return Section {
            VStack(alignment: .leading, spacing: 6) {
                Text("デイサービスのお迎えまで").font(.subheadline.bold()).foregroundStyle(Theme.muted)
                if left > 0 {
                    Text("あと\(left)分").font(.system(size: 40, weight: .bold, design: .rounded)).monospacedDigit()
                    Text("\(household.pickupMinutes.hm) にお迎えが来ます").bold()
                    ProgressView(value: max(0, min(1, 1 - Double(left) / 120))).tint(Theme.warm)
                } else {
                    Text("お迎えの時間です").font(.title.bold())
                }
                DisclosureGroup("お迎え前の持ち物（\(pack.filter { $0.checkedDay == day }.count) / \(pack.count)）", isExpanded: $showPack) {
                    ForEach(pack) { p in
                        Button { p.checkedDay = p.checkedDay == day ? "" : day } label: {
                            Label(p.title, systemImage: p.checkedDay == day ? "checkmark.square.fill" : "square")
                                .frame(minHeight: Theme.minTap, alignment: .leading)
                        }.foregroundStyle(.primary)
                    }
                }
            }
            .listRowBackground(Theme.warmSoft)
        }
    }

    private func doneRow(_ it: DailyItem, now: Int) -> some View {
        let rec = done.first { $0.itemKey == it.key }
        let late = rec == nil && now > it.minutes + 30
        return HStack {
            VStack(alignment: .leading) {
                Text(it.title).bold()
                Group {
                    if let rec { Text("\(rec.by)・\(rec.at.minutesOfDay.hm)") }
                    else { Text("\(it.minutes.hm)ごろ") + (late ? Text("　まだです").foregroundColor(Theme.warm).bold() : Text("")) }
                }.font(.footnote).foregroundStyle(Theme.muted)
            }
            Spacer()
            Button(rec == nil ? "済みにする" : "済み") { toggle(it, rec) }
                .buttonStyle(.borderedProminent).tint(rec == nil ? Theme.control : Theme.accentHex)
                .frame(minHeight: Theme.minTap)
        }
    }

    private func toggle(_ it: DailyItem, _ rec: DoneRecord?) {
        if let rec { ctx.delete(rec) }
        else { ctx.insert(DoneRecord(householdID: household.id, itemKey: it.key, day: Date().dayKey, by: app.memberName.isEmpty ? "家族" : app.memberName)) }
    }
}

struct LogTab: View {
    let household: Household
    @Query private var done: [DoneRecord]
    @Query private var items: [DailyItem]
    init(household: Household) {
        self.household = household
        let id = household.id, day = Date().dayKey
        _done = Query(filter: #Predicate<DoneRecord> { $0.householdID == id && $0.day == day }, sort: \.at)
        _items = Query(filter: #Predicate<DailyItem> { $0.householdID == id })
    }
    var body: some View {
        List {
            if done.isEmpty {
                Text("まだ記録がありません。「済みにする」を押すと、ここに並びます。").foregroundStyle(Theme.muted)
            }
            ForEach(done) { r in
                HStack(spacing: 12) {
                    Text(r.at.minutesOfDay.hm).bold().monospacedDigit().foregroundStyle(Theme.accentHex)
                    Text("\(r.by)　\(items.first { $0.key == r.itemKey }?.title ?? r.itemKey) 済み")
                }
            }
            Text("ご家族みんなが同じ記録を見ています。").font(.footnote).foregroundStyle(Theme.muted)
        }
        .navigationTitle("きょうの記録")
    }
}

struct DutyTab: View {
    @Environment(AppState.self) private var app
    @Environment(\.modelContext) private var ctx
    let household: Household
    @Query private var duties: [Duty]
    @State private var newWhen = ""
    @State private var newTitle = ""
    init(household: Household) {
        self.household = household
        let id = household.id
        _duties = Query(filter: #Predicate<Duty> { $0.householdID == id })
    }
    var body: some View {
        List {
            ForEach(duties) { d in
                HStack {
                    Text(d.when).bold().foregroundStyle(Theme.accentHex).frame(minWidth: 44, alignment: .leading)
                    VStack(alignment: .leading) { Text(d.title).bold(); if !d.detail.isEmpty { Text(d.detail).font(.footnote).foregroundStyle(Theme.muted) } }
                    Spacer()
                    if d.assignee.isEmpty {
                        Button("引き受ける") { d.assignee = app.memberName }.buttonStyle(.bordered)
                    } else {
                        Text(d.assignee).bold()
                    }
                }
                .swipeActions { Button("担当を外す") { d.assignee = "" } }
            }
            .onDelete { idx in idx.map { duties[$0] }.forEach(ctx.delete) }
            Section("予定を追加") {
                TextField("いつ（例：火、11/12、毎晩）", text: $newWhen)
                TextField("内容（例：通院の付きそい）", text: $newTitle)
                Button("追加する") {
                    ctx.insert(Duty(householdID: household.id, when: newWhen, title: newTitle, detail: ""))
                    newWhen = ""; newTitle = ""
                }.disabled(newWhen.isEmpty || newTitle.isEmpty)
            }
        }
        .navigationTitle("家族の分担表")
    }
}
