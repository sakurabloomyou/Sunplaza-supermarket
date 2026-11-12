import SwiftUI
import SwiftData

/// 初回設定（基本情報 → カテゴリ → 具体的な悩み → 特に気になる3つ → 結果）。
struct OnboardingFlow: View {
    @Environment(AppState.self) private var app
    @Environment(\.modelContext) private var ctx
    @State private var step = 1
    @State private var answers = ConcernAnswers()
    @State private var categoryIndex = 0
    @State private var familyName = ""
    @State private var selfName = "お母さん"

    private var selectedCats: [ConcernCategory] { ConcernCategory.allCases.filter { answers.categories.contains($0) } }

    var body: some View {
        VStack(spacing: 0) {
            header
            ScrollView { content.padding(20) }
            footer
        }
    }

    private var header: some View {
        HStack {
            Button("‹ 戻る") { back() }.frame(minWidth: Theme.minTap, minHeight: Theme.minTap)
            VStack(alignment: .leading) {
                Text("\(step) / 5").font(.subheadline).foregroundStyle(Theme.muted)
                ProgressView(value: Double(step), total: 5).tint(Theme.accentHex)
            }
        }.padding(.horizontal, 16)
    }

    @ViewBuilder private var content: some View {
        switch step {
        case 1: basicInfo
        case 2: categories
        case 3: concerns
        case 4: topThree
        default: result
        }
    }

    private var basicInfo: some View {
        VStack(alignment: .leading, spacing: 16) {
            Text("まず、暮らしのことを教えてください").font(.title2.bold())
            TextField("あなたのお名前（例：さくら）", text: $familyName).textFieldStyle(.roundedBorder)
            TextField("ご本人の呼び名（例：お母さん）", text: $selfName).textFieldStyle(.roundedBorder)
            Toggle("毎日飲む薬がある", isOn: $answers.takesMedication)
            Toggle("デイサービスなどを利用している", isOn: $answers.usesDayService)
            if answers.usesDayService {
                HStack(spacing: 4) {
                    ForEach(Array(["日","月","火","水","木","金","土"].enumerated()), id: \.offset) { i, d in
                        let on = answers.dayServiceWeekdays.contains(i + 1)
                        Button(d) { if on { answers.dayServiceWeekdays.remove(i + 1) } else { answers.dayServiceWeekdays.insert(i + 1) } }
                            .frame(maxWidth: .infinity, minHeight: Theme.minTap)
                            .background(on ? Theme.accentHex : .clear, in: RoundedRectangle(cornerRadius: Theme.controlRadius))
                            .foregroundStyle(on ? .white : .primary)
                            .overlay(RoundedRectangle(cornerRadius: Theme.controlRadius).stroke(Theme.control))
                            .accessibilityAddTraits(on ? .isSelected : [])
                    }
                }
            }
        }
    }

    private var categories: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("気になることを選んでください").font(.title2.bold())
            Text("いくつ選んでもかまいません。").foregroundStyle(Theme.muted)
            LazyVGrid(columns: [GridItem(.flexible()), GridItem(.flexible())], spacing: 8) {
                ForEach(ConcernCategory.allCases) { c in
                    let on = answers.categories.contains(c)
                    Button { if on { answers.categories.remove(c) } else { answers.categories.insert(c) } } label: {
                        VStack(alignment: .leading, spacing: 6) {
                            HStack { Image(systemName: c.symbol); Spacer(); Image(systemName: on ? "checkmark.circle.fill" : "circle") }
                            Text(c.title).multilineTextAlignment(.leading).bold(on)
                        }
                        .padding(12).frame(maxWidth: .infinity, minHeight: 88, alignment: .topLeading)
                        .background(on ? Theme.accentSoft : .white, in: RoundedRectangle(cornerRadius: Theme.controlRadius))
                        .overlay(RoundedRectangle(cornerRadius: Theme.controlRadius).stroke(on ? Theme.accentHex : Theme.control, lineWidth: 1.5))
                    }
                    .foregroundStyle(.primary)
                    .accessibilityAddTraits(on ? .isSelected : [])
                }
            }
        }
    }

    private var concerns: some View {
        let cat = selectedCats[min(categoryIndex, max(selectedCats.count - 1, 0))]
        return VStack(alignment: .leading, spacing: 16) {
            Label("\(cat.title)（\(categoryIndex + 1) / \(selectedCats.count)）", systemImage: cat.symbol)
                .foregroundStyle(Theme.accentHex).bold()
            Text("あてはまるものを選んでください").font(.title2.bold())
            ForEach(Concern.all.filter { $0.category == cat }) { c in
                VStack(alignment: .leading, spacing: 8) {
                    Text(c.label).bold()
                    Picker(c.label, selection: Binding(get: { answers.levels[c.id] ?? -1 }, set: { answers.setLevel(c.id, $0) })) {
                        ForEach(Array(c.scale.labels.enumerated()), id: \.offset) { i, l in Text(l).tag(i) }
                    }.pickerStyle(.segmented)
                }
                Divider()
            }
        }
    }

    private var topThree: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("特に気になるものを、3つまで選んでください").font(.title2.bold())
            Text("\(answers.topThree.count) / 3 選択中").foregroundStyle(Theme.muted)
            if answers.topThree.count >= 3 {
                Text("3つ選びました。選び直すときは、選んだものをもう一度押して外してください。")
                    .padding(10).background(Theme.sunk, in: RoundedRectangle(cornerRadius: Theme.cardRadius))
            }
            if answers.topCandidates.isEmpty {
                Text("「よく」「毎日」「かなり」「とても」を選んだ悩みがないので、この画面はとばせます。").foregroundStyle(Theme.muted)
            }
            ForEach(answers.topCandidates) { c in
                let rank = answers.topThree.firstIndex(of: c.id)
                let dim = answers.topThree.count >= 3 && rank == nil
                Button { answers.toggleTop(c.id) } label: {
                    HStack {
                        Text(rank.map { "\($0 + 1)" } ?? " ").frame(width: 30, height: 30)
                            .background(rank == nil ? Theme.sunk : Theme.warm, in: Circle()).foregroundStyle(.white)
                        Text(c.label).multilineTextAlignment(.leading)
                        Spacer()
                        Text(c.scale.labels[answers.levels[c.id] ?? 0]).font(.footnote).foregroundStyle(Theme.muted)
                    }
                    .padding(12).frame(minHeight: 58)
                    .background(rank == nil ? .white : Theme.warmSoft, in: RoundedRectangle(cornerRadius: Theme.controlRadius))
                    .overlay(RoundedRectangle(cornerRadius: Theme.controlRadius).stroke(rank == nil ? Theme.control : Theme.warm, lineWidth: 1.5))
                }
                .foregroundStyle(.primary).opacity(dim ? 0.45 : 1)
            }
        }
    }

    private var result: some View {
        let fs = answers.featureScores()
        let onCount = fs.filter { answers.isOn($0.feature) }.count
        return VStack(alignment: .leading, spacing: 12) {
            Text(onCount > 0 ? "ご家庭に合わせて、\(onCount)つの機能をオンにしました" : "ご家庭に合わせた機能は、まだオフです").font(.title2.bold())
            Text("ほかの機能も、必要になったらここでオンにできます。").foregroundStyle(Theme.muted)
            ForEach(fs) { item in
                let on = answers.isOn(item.feature)
                Toggle(isOn: Binding(get: { on }, set: { answers.overrides[item.feature] = $0 })) {
                    VStack(alignment: .leading, spacing: 2) {
                        Text(on ? "★ オン" : "オフ").font(.caption.bold()).foregroundStyle(on ? Theme.warm : Theme.muted)
                        Text(item.feature.title).bold()
                        if item.feature.isComingSoon { Text("準備中").font(.caption).foregroundStyle(Theme.muted) }
                    }
                }
                .padding(12).background(on ? Theme.warmSoft : Theme.sunk, in: RoundedRectangle(cornerRadius: Theme.cardRadius))
            }
            Text("みなさん共通の基本機能（今日のボード・済みチェック\(answers.usesDayService ? "・お迎えカウントダウン" : "")）はオンです。")
                .font(.footnote).foregroundStyle(Theme.muted)
        }
    }

    private var footer: some View {
        VStack(spacing: 8) {
            Button(step == 5 ? "はじめる" : "次へ") { next() }.buttonStyle(PrimaryButtonStyle())
                .disabled(step == 1 && familyName.trimmingCharacters(in: .whitespaces).isEmpty)
        }.padding(20)
    }

    private func next() {
        switch step {
        case 2 where answers.categories.isEmpty: step = 5
        case 3 where categoryIndex < selectedCats.count - 1: categoryIndex += 1
        case 5: finish()
        default: step += 1
        }
    }
    private func back() {
        if step == 1 { app.route = .launch }
        else if step == 3 && categoryIndex > 0 { categoryIndex -= 1 }
        else if step == 5 && answers.categories.isEmpty { step = 2 }
        else { step -= 1 }
    }
    private func finish() {
        let h = HouseholdStore.createHousehold(in: ctx, answers: answers, familyName: familyName, selfName: selfName)
        _ = h
        app.memberName = familyName
        app.role = .family
        app.route = .familyHome
        Task { _ = await NotificationScheduler.shared.requestAuthorization() }
    }
}
