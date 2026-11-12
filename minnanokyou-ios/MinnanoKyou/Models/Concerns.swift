import Foundation

// 悩み30項目・機能・点数のしくみ。試作（ブラウザ版）と同じ規則。
// 点数の基準（2点以上・特に気になる＋3点）は仮。研究者の確認が必要。

enum ConcernCategory: String, CaseIterable, Codable, Identifiable {
    case memory, dayService, mood, home, family, medical, social, wellbeing
    var id: String { rawValue }
    var title: String {
        switch self {
        case .memory: "忘れる・見通し"
        case .dayService: "デイサービス・外出"
        case .mood: "気持ちや行動の変化"
        case .home: "家事・安全"
        case .family: "家族の負担"
        case .medical: "病院・手続き"
        case .social: "人とのつながり"
        case .wellbeing: "元気に過ごしてほしい"
        }
    }
    var symbol: String {
        switch self {
        case .memory: "clock"
        case .dayService: "bus"
        case .mood: "bubble.left"
        case .home: "house"
        case .family: "heart"
        case .medical: "cross.case"
        case .social: "person.2"
        case .wellbeing: "leaf"
        }
    }
}

enum AnswerScale: Codable { case frequency, degree
    var labels: [String] {
        switch self {
        case .frequency: ["ない", "たまに", "よく", "毎日"]
        case .degree: ["いいえ", "少し", "かなり", "とても"]
        }
    }
}

enum Feature: String, CaseIterable, Codable, Identifiable {
    case lockWidget, mealShow, medication, dateClock, reminder3, whereabouts, placeMemo
    case packList, dayMotivation, findMy, eveningCalm, voiceMessage
    case talkTips, episodeLog, smallRole, sleepRhythm
    case fireCheck, shopping, photoCards, water
    case outlookGuide, dutyTable, workGuide, caregiverCheck, shareScope
    case visitReport, procedures, socialPlans, lifestyle
    var id: String { rawValue }
    var title: String {
        switch self {
        case .lockWidget: "ロック画面の「今日のボード」"
        case .mealShow: "ごはん済みの表示"
        case .medication: "服薬チェック"
        case .dateClock: "日付と曜日の大きな表示"
        case .reminder3: "3段階のお知らせ"
        case .whereabouts: "みんなの予定"
        case .placeMemo: "しまった場所メモ"
        case .packList: "お迎え前の持ち物チェック"
        case .dayMotivation: "前日のお楽しみ通知"
        case .findMy: "「探す」の設定ガイド"
        case .eveningCalm: "夕方のやすらぎ時間"
        case .voiceMessage: "家族の声メッセージ"
        case .talkTips: "声かけのコツ"
        case .episodeLog: "できごと記録"
        case .smallRole: "小さな役割と気分の記録"
        case .sleepRhythm: "眠りのリズムづくり"
        case .fireCheck: "火の確認のお知らせ"
        case .shopping: "買い物メモの共有"
        case .photoCards: "手順の写真カード"
        case .water: "水分チェック"
        case .outlookGuide: "これからの見通しガイド"
        case .dutyTable: "家族の分担表"
        case .workGuide: "仕事との両立の案内"
        case .caregiverCheck: "家族の気分チェック"
        case .shareScope: "共有範囲の設定"
        case .visitReport: "受診メモの自動作成"
        case .procedures: "手続きチェックリスト"
        case .socialPlans: "つながりの予定"
        case .lifestyle: "生活習慣サポート"
        }
    }
    /// v1（無料版）ではまだ作っていない機能。画面では「準備中」と表示する。
    var isComingSoon: Bool {
        switch self {
        case .placeMemo, .photoCards, .voiceMessage, .visitReport, .shareScope: true
        default: false
        }
    }
}

struct Concern: Identifiable, Hashable {
    let id: String
    let category: ConcernCategory
    let label: String
    let features: [Feature]
    var scale: AnswerScale { Concern.degreeItems.contains(id) ? .degree : .frequency }

    static let degreeItems: Set<String> = ["B10","D18","D21","E22","E23","E24","E25","E26","F27","F28","G29","H30"]

    static let all: [Concern] = [
        .init(id: "A1", category: .memory, label: "同じことを何度も聞く", features: [.lockWidget]),
        .init(id: "A2", category: .memory, label: "ご飯を食べたか忘れる", features: [.mealShow]),
        .init(id: "A3", category: .memory, label: "薬を飲んだか忘れる・二重に飲む", features: [.medication]),
        .init(id: "A4", category: .memory, label: "日付や曜日がわからなくなる", features: [.dateClock]),
        .init(id: "A5", category: .memory, label: "約束や通院を忘れる", features: [.reminder3]),
        .init(id: "A6", category: .memory, label: "家族がどこにいるか不安がる", features: [.whereabouts]),
        .init(id: "A7", category: .memory, label: "物をなくす・しまった場所を忘れる", features: [.placeMemo]),
        .init(id: "B8", category: .dayService, label: "お迎えの時間に準備が間に合わない", features: [.packList]),
        .init(id: "B9", category: .dayService, label: "デイサービスに行きたがらない", features: [.dayMotivation]),
        .init(id: "B10", category: .dayService, label: "ひとりで出かけて道に迷わないか心配", features: [.findMy]),
        .init(id: "B11", category: .dayService, label: "夕方になると「帰る」と言い出す", features: [.eveningCalm, .voiceMessage]),
        .init(id: "C12", category: .mood, label: "物を盗られたと言う", features: [.talkTips, .placeMemo]),
        .init(id: "C13", category: .mood, label: "怒りっぽい・強い言葉や手が出る", features: [.episodeLog]),
        .init(id: "C14", category: .mood, label: "落ち込む・やる気が出ない", features: [.smallRole]),
        .init(id: "C15", category: .mood, label: "不安そう・そわそわする", features: [.voiceMessage]),
        .init(id: "C16", category: .mood, label: "夜に眠らない・昼夜が逆になる", features: [.sleepRhythm]),
        .init(id: "C17", category: .mood, label: "声のかけ方で傷つけてしまう", features: [.talkTips]),
        .init(id: "D18", category: .home, label: "火の消し忘れが心配", features: [.fireCheck]),
        .init(id: "D19", category: .home, label: "同じ物を何度も買う・お金の管理", features: [.shopping]),
        .init(id: "D20", category: .home, label: "お風呂や着替えを嫌がる", features: [.photoCards]),
        .init(id: "D21", category: .home, label: "水分をあまりとらない", features: [.water]),
        .init(id: "E22", category: .family, label: "この先どうなるか見通せない", features: [.outlookGuide]),
        .init(id: "E23", category: .family, label: "家族の中で負担がかたよっている", features: [.dutyTable]),
        .init(id: "E24", category: .family, label: "仕事と両立できるか不安", features: [.workGuide]),
        .init(id: "E25", category: .family, label: "自分の心と体が限界に近い", features: [.caregiverCheck]),
        .init(id: "E26", category: .family, label: "誰とどこまで情報を共有するか迷う", features: [.shareScope]),
        .init(id: "F27", category: .medical, label: "受診のとき様子をうまく伝えられない", features: [.visitReport]),
        .init(id: "F28", category: .medical, label: "介護保険などの手続きがむずかしい", features: [.procedures]),
        .init(id: "G29", category: .social, label: "外に出ず、人と会わなくなった", features: [.socialPlans]),
        .init(id: "H30", category: .wellbeing, label: "物忘れの進み方を少しでもゆるやかにしたい", features: [.lifestyle]),
    ]
}

struct FeatureScore: Identifiable, Equatable {
    let feature: Feature
    let score: Int
    /// 「特に気になる3つ」または「薬あり」から来たもの（最初からオン）
    let recommended: Bool
    var id: Feature { feature }
}

/// 初回設定の回答。
struct ConcernAnswers: Codable, Equatable {
    var categories: Set<ConcernCategory> = []
    var levels: [String: Int] = [:]          // concernID → 0...3
    var topThree: [String] = []              // 特に気になる（最大3）
    var takesMedication = false
    var usesDayService = false
    var dayServiceWeekdays: Set<Int> = []    // 1=日 … 7=土
    var overrides: [Feature: Bool] = [:]     // 結果画面で家族が切り替えたもの

    static let onThreshold = 2
    static let topBonus = 3
    static let maxTop = 3

    func score(_ c: Concern) -> Int { (levels[c.id] ?? 0) + (topThree.contains(c.id) ? Self.topBonus : 0) }

    /// 2点以上の悩みに対応する機能と、その最高点。
    func featureScores() -> [FeatureScore] {
        var best: [Feature: (Int, Bool)] = [:]
        for c in Concern.all {
            let s = score(c); guard s > 0 else { continue }
            for f in c.features {
                let rec = topThree.contains(c.id)
                let cur = best[f] ?? (0, false)
                best[f] = (max(cur.0, s), cur.1 || rec)
            }
        }
        if takesMedication {
            let cur = best[.medication] ?? (0, false)
            best[.medication] = (max(cur.0, Self.onThreshold), true)
        }
        return best.filter { $0.value.0 >= Self.onThreshold }
            .map { FeatureScore(feature: $0.key, score: $0.value.0, recommended: $0.value.1) }
            .sorted { $0.score != $1.score ? $0.score > $1.score : $0.feature.rawValue < $1.feature.rawValue }
    }

    /// 最初からオンにするのは「特に気になる3つ」に対応する機能と、薬ありのときの服薬チェックだけ。
    func isOn(_ f: Feature) -> Bool {
        if let o = overrides[f] { return o }
        return featureScores().first { $0.feature == f }?.recommended ?? false
    }

    var topCandidates: [Concern] { Concern.all.filter { (levels[$0.id] ?? 0) >= 2 } }

    mutating func toggleTop(_ id: String) {
        if let i = topThree.firstIndex(of: id) { topThree.remove(at: i) }
        else if topThree.count < Self.maxTop { topThree.append(id) }
    }

    mutating func setLevel(_ id: String, _ v: Int) {
        levels[id] = v
        if v < 2 { topThree.removeAll { $0 == id } }
    }
}
