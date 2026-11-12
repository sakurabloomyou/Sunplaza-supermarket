import Foundation
import SwiftData

// 家族で共有するデータ。CloudKit と同期するため、すべてのプロパティに既定値を持たせ、
// 一意制約（@Attribute(.unique)）は使わない（CloudKit の制約）。

@Model final class Household {
    var id: String = UUID().uuidString
    var selfName: String = "お母さん"           // ご本人の呼び名
    var inviteCode: String = Household.makeCode()
    var answersData: Data = Data()             // ConcernAnswers を JSON で保存
    var pickupMinutes: Int = 620                // お迎え時刻（0時からの分）10:20
    var returnMinutes: Int = 990                // 帰宅 16:30
    var createdAt: Date = Date()
    init() {}

    var answers: ConcernAnswers {
        get { (try? JSONDecoder().decode(ConcernAnswers.self, from: answersData)) ?? ConcernAnswers() }
        set { answersData = (try? JSONEncoder().encode(newValue)) ?? Data() }
    }
    static func makeCode() -> String { String(format: "%06d", Int.random(in: 0...999_999)) }
}

@Model final class Member {
    var householdID: String = ""
    var name: String = ""
    var isSelf: Bool = false
    var colorHex: String = "#1F5A4E"
    var returnTime: String = ""               // 例: 「18:00に帰ります」
    init(householdID: String, name: String, isSelf: Bool = false) {
        self.householdID = householdID; self.name = name; self.isSelf = isSelf
    }
}

/// ごはん・おくすりの予定（毎日くり返し）。
@Model final class DailyItem {
    var householdID: String = ""
    var key: String = ""                      // bf, m1, lu, m2, di, m3
    var title: String = ""
    var minutes: Int = 0
    var isMedication: Bool = false
    var order: Int = 0
    init(householdID: String, key: String, title: String, minutes: Int, isMedication: Bool, order: Int) {
        self.householdID = householdID; self.key = key; self.title = title
        self.minutes = minutes; self.isMedication = isMedication; self.order = order
    }
}

/// 「済み」の記録。
@Model final class DoneRecord {
    var householdID: String = ""
    var itemKey: String = ""
    var day: String = ""                      // yyyy-M-d
    var by: String = ""
    var at: Date = Date()
    init(householdID: String, itemKey: String, day: String, by: String, at: Date = Date()) {
        self.householdID = householdID; self.itemKey = itemKey; self.day = day; self.by = by; self.at = at
    }
}

@Model final class PackItem {
    var householdID: String = ""
    var title: String = ""
    var checkedDay: String = ""               // その日にチェックされたら日付が入る
    var order: Int = 0
    init(householdID: String, title: String, order: Int) {
        self.householdID = householdID; self.title = title; self.order = order
    }
}

@Model final class Duty {
    var householdID: String = ""
    var when: String = ""                     // 「火」「11/12」「毎晩」
    var title: String = ""
    var detail: String = ""
    var assignee: String = ""                 // 空なら未定
    init(householdID: String, when: String, title: String, detail: String, assignee: String = "") {
        self.householdID = householdID; self.when = when; self.title = title
        self.detail = detail; self.assignee = assignee
    }
}

enum HouseholdStore {
    /// iCloud の非公開データベースと同期する。家族間の共有（CKShare）は docs/ARCHITECTURE.md 参照。
    static let container: ModelContainer = {
        let schema = Schema([Household.self, Member.self, DailyItem.self, DoneRecord.self, PackItem.self, Duty.self])
        let config = ModelConfiguration(schema: schema, cloudKitDatabase: .private("iCloud.jp.minnanokyou.app"))
        do { return try ModelContainer(for: schema, configurations: config) }
        catch {
            // iCloud にサインインしていない等で失敗したら端末内だけで動かす
            let local = ModelConfiguration(schema: schema, cloudKitDatabase: .none)
            return try! ModelContainer(for: schema, configurations: local)
        }
    }()

    /// 新しい家族グループを作り、既定のごはん・おくすり・持ち物・分担を入れる。
    @MainActor
    static func createHousehold(in ctx: ModelContext, answers: ConcernAnswers, familyName: String, selfName: String) -> Household {
        let h = Household(); h.selfName = selfName; h.answers = answers
        ctx.insert(h)
        ctx.insert(Member(householdID: h.id, name: selfName, isSelf: true))
        ctx.insert(Member(householdID: h.id, name: familyName))
        let items: [(String, String, Int, Bool)] = [
            ("bf","あさごはん",480,false),("m1","おくすり（朝）",510,true),
            ("lu","おひるごはん",720,false),("m2","おくすり（昼）",750,true),
            ("di","ばんごはん",1080,false),("m3","おくすり（夜）",1110,true)]
        for (i, it) in items.enumerated() where answers.takesMedication || !it.3 {
            ctx.insert(DailyItem(householdID: h.id, key: it.0, title: it.1, minutes: it.2, isMedication: it.3, order: i))
        }
        for (i, t) in ["連絡帳","着がえ","タオル","おくすり","上ばき"].enumerated() {
            ctx.insert(PackItem(householdID: h.id, title: t, order: i))
        }
        return h
    }
}

extension Int {
    /// 0時からの分 → "10:20"
    var hm: String { String(format: "%d:%02d", self / 60, self % 60) }
}
