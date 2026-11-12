import SwiftUI
import CoreData

struct FamilyHomeView: View {
    @FetchRequest(sortDescriptors: [NSSortDescriptor(key: "createdAt", ascending: true)]) private var households: FetchedResults<Household>

    private var household: Household? {
        households.first { $0.objectID.persistentStore == PersistenceController.shared.sharedStore } ?? households.first
    }

    var body: some View {
        if let h = household {
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
            ContentUnavailableView {
                Label("家族グループを読み込んでいます", systemImage: "icloud.and.arrow.down")
            } description: {
                Text("招待コードで参加した直後は、iCloud から届くまで少し時間がかかります。届かないときは、iCloud にサインインしているか確かめてください。")
            }
        }
    }
}

struct TodayTab: View {
    @Environment(AppState.self) private var app
    @ObservedObject var household: Household
    @FetchRequest private var items: FetchedResults<DailyItem>
    @FetchRequest private var done: FetchedResults<DoneRecord>
    @FetchRequest private var pack: FetchedResults<PackItem>
    @State private var showPack = false
    private let pc = PersistenceController.shared

    init(household: Household) {
        self.household = household
        _items = FetchRequest(sortDescriptors: [NSSortDescriptor(key: "order", ascending: true)],
                              predicate: NSPredicate(format: "household == %@", household))
        _done = FetchRequest(sortDescriptors: [NSSortDescriptor(key: "at", ascending: true)],
                             predicate: NSPredicate(format: "household == %@ AND day == %@", household, Date().dayKey))
        _pack = FetchRequest(sortDescriptors: [NSSortDescriptor(key: "order", ascending: true)],
                             predicate: NSPredicate(format: "household == %@", household))
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
                    NavigationLink("家族を招待する") { InviteFamilyView(household: household) }
                    NavigationLink("お知らせの設定") { NotificationSettingsView() }
                    Button("ご本人の画面を見る") { app.route = .selfBoard }
                }
                Section { Disclaimer() }
            }
            .navigationTitle("きょう")
        }
    }

    private func pickupSection(now: Int) -> some View {
        let left = Int(household.pickupMinutes) - now
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
                        Button {
                            p.checkedDay = p.checkedDay == day ? "" : day; pc.save()
                        } label: {
                            Label(p.title ?? "", systemImage: p.checkedDay == day ? "checkmark.square.fill" : "square")
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
        let late = rec == nil && now > Int(it.minutes) + 30
        return HStack {
            VStack(alignment: .leading) {
                Text(it.title ?? "").bold()
                Group {
                    if let rec { Text("\(rec.by ?? "")・\((rec.at ?? Date()).minutesOfDay.hm)") }
                    else { Text("\(it.minutes.hm)ごろ") + (late ? Text("　まだです").foregroundColor(Theme.warm).bold() : Text("")) }
                }.font(.footnote).foregroundStyle(Theme.muted)
            }
            Spacer()
            Button(rec == nil ? "済みにする" : "済み") {
                if let rec { pc.viewContext.delete(rec); pc.save() }
                else { pc.markDone(it, in: household, by: app.memberName.isEmpty ? "家族" : app.memberName) }
                Task { await NotificationScheduler.shared.refresh(role: app.role) }
            }
            .buttonStyle(.borderedProminent).tint(rec == nil ? Theme.control : Theme.accentHex)
            .frame(minHeight: Theme.minTap)
        }
    }
}

struct LogTab: View {
    @ObservedObject var household: Household
    @FetchRequest private var done: FetchedResults<DoneRecord>
    init(household: Household) {
        self.household = household
        _done = FetchRequest(sortDescriptors: [NSSortDescriptor(key: "at", ascending: true)],
                             predicate: NSPredicate(format: "household == %@ AND day == %@", household, Date().dayKey))
    }
    var body: some View {
        List {
            if done.isEmpty {
                Text("まだ記録がありません。「済みにする」を押すと、ここに並びます。").foregroundStyle(Theme.muted)
            }
            ForEach(done) { r in
                HStack(spacing: 12) {
                    Text((r.at ?? Date()).minutesOfDay.hm).bold().monospacedDigit().foregroundStyle(Theme.accentHex)
                    Text("\(r.by ?? "")　\(household.itemList.first { $0.key == r.itemKey }?.title ?? (r.itemKey ?? "")) 済み")
                }
            }
            Text("ご家族みんなが同じ記録を見ています。").font(.footnote).foregroundStyle(Theme.muted)
        }
        .navigationTitle("きょうの記録")
    }
}

struct DutyTab: View {
    @Environment(AppState.self) private var app
    @ObservedObject var household: Household
    @FetchRequest private var duties: FetchedResults<Duty>
    @State private var newWhen = ""
    @State private var newTitle = ""
    private let pc = PersistenceController.shared
    init(household: Household) {
        self.household = household
        _duties = FetchRequest(sortDescriptors: [NSSortDescriptor(key: "when", ascending: true)],
                               predicate: NSPredicate(format: "household == %@", household))
    }
    var body: some View {
        List {
            ForEach(duties) { d in
                HStack {
                    Text(d.when ?? "").bold().foregroundStyle(Theme.accentHex).frame(minWidth: 44, alignment: .leading)
                    VStack(alignment: .leading) {
                        Text(d.title ?? "").bold()
                        if let detail = d.detail, !detail.isEmpty { Text(detail).font(.footnote).foregroundStyle(Theme.muted) }
                    }
                    Spacer()
                    if (d.assignee ?? "").isEmpty {
                        Button("引き受ける") { d.assignee = app.memberName; pc.save() }.buttonStyle(.bordered)
                    } else {
                        Text(d.assignee ?? "").bold()
                    }
                }
                .swipeActions { Button("担当を外す") { d.assignee = ""; pc.save() } }
            }
            .onDelete { idx in idx.map { duties[$0] }.forEach(pc.viewContext.delete); pc.save() }
            Section("予定を追加") {
                TextField("いつ（例：火、11/12、毎晩）", text: $newWhen)
                TextField("内容（例：通院の付きそい）", text: $newTitle)
                Button("追加する") {
                    let d = pc.insert(Duty.self, into: household); d.when = newWhen; d.title = newTitle
                    pc.save(); newWhen = ""; newTitle = ""
                }.disabled(newWhen.isEmpty || newTitle.isEmpty)
            }
        }
        .navigationTitle("家族の分担表")
    }
}
