import CoreData

// 家族で共有するデータの定義（Core Data）。
// CloudKit と同期・共有するため：
//  - すべての属性は「省略可」か「既定値あり」
//  - 一意制約は使わない
//  - 関係（relationship）はすべて省略可で、逆向きの関係を持つ
// 家族グループ（Household）を CKShare で共有すると、関係でつながった子データも一緒に共有される。

@objc(Household) final class Household: NSManagedObject, Identifiable {
    @NSManaged var id: String?
    @NSManaged var selfName: String?
    @NSManaged var answersData: Data?
    @NSManaged var pickupMinutes: Int64
    @NSManaged var returnMinutes: Int64
    @NSManaged var createdAt: Date?
    @NSManaged var members: NSSet?
    @NSManaged var items: NSSet?
    @NSManaged var doneRecords: NSSet?
    @NSManaged var packItems: NSSet?
    @NSManaged var duties: NSSet?

    var answers: ConcernAnswers {
        get { answersData.flatMap { try? JSONDecoder().decode(ConcernAnswers.self, from: $0) } ?? ConcernAnswers() }
        set { answersData = try? JSONEncoder().encode(newValue) }
    }
    var displaySelfName: String { selfName ?? "ご本人" }
    var itemList: [DailyItem] { ((items as? Set<DailyItem>) ?? []).sorted { $0.order < $1.order } }
    var memberList: [Member] { ((members as? Set<Member>) ?? []).sorted { ($0.name ?? "") < ($1.name ?? "") } }
    var dutyList: [Duty] { ((duties as? Set<Duty>) ?? []).sorted { ($0.when ?? "") < ($1.when ?? "") } }
}

@objc(Member) final class Member: NSManagedObject, Identifiable {
    @NSManaged var name: String?
    @NSManaged var isSelf: Bool
    @NSManaged var returnTime: String?
    @NSManaged var household: Household?
}

/// ごはん・おくすりの予定（毎日くり返し）。
@objc(DailyItem) final class DailyItem: NSManagedObject, Identifiable {
    @NSManaged var key: String?
    @NSManaged var title: String?
    @NSManaged var minutes: Int64
    @NSManaged var isMedication: Bool
    @NSManaged var order: Int64
    @NSManaged var household: Household?
}

/// 「済み」の記録。
@objc(DoneRecord) final class DoneRecord: NSManagedObject, Identifiable {
    @NSManaged var itemKey: String?
    @NSManaged var day: String?
    @NSManaged var by: String?
    @NSManaged var at: Date?
    @NSManaged var household: Household?
}

@objc(PackItem) final class PackItem: NSManagedObject, Identifiable {
    @NSManaged var title: String?
    @NSManaged var checkedDay: String?
    @NSManaged var order: Int64
    @NSManaged var household: Household?
}

@objc(Duty) final class Duty: NSManagedObject, Identifiable {
    @NSManaged var when: String?
    @NSManaged var title: String?
    @NSManaged var detail: String?
    @NSManaged var assignee: String?
    @NSManaged var household: Household?
}

enum CoreDataModel {
    static let model: NSManagedObjectModel = {
        func attr(_ n: String, _ t: NSAttributeType, _ def: Any? = nil) -> NSAttributeDescription {
            let a = NSAttributeDescription(); a.name = n; a.attributeType = t; a.isOptional = true; a.defaultValue = def; return a
        }
        func entity(_ cls: NSManagedObject.Type, _ attrs: [NSAttributeDescription]) -> NSEntityDescription {
            let e = NSEntityDescription(); e.name = NSStringFromClass(cls); e.managedObjectClassName = NSStringFromClass(cls)
            e.properties = attrs; return e
        }
        let household = entity(Household.self, [
            attr("id", .stringAttributeType), attr("selfName", .stringAttributeType, "お母さん"),
            attr("answersData", .binaryDataAttributeType), attr("pickupMinutes", .integer64AttributeType, 620),
            attr("returnMinutes", .integer64AttributeType, 990), attr("createdAt", .dateAttributeType)])
        let member = entity(Member.self, [attr("name", .stringAttributeType, ""), attr("isSelf", .booleanAttributeType, false),
                                          attr("returnTime", .stringAttributeType, "")])
        let item = entity(DailyItem.self, [attr("key", .stringAttributeType, ""), attr("title", .stringAttributeType, ""),
                                           attr("minutes", .integer64AttributeType, 0), attr("isMedication", .booleanAttributeType, false),
                                           attr("order", .integer64AttributeType, 0)])
        let done = entity(DoneRecord.self, [attr("itemKey", .stringAttributeType, ""), attr("day", .stringAttributeType, ""),
                                            attr("by", .stringAttributeType, ""), attr("at", .dateAttributeType)])
        let pack = entity(PackItem.self, [attr("title", .stringAttributeType, ""), attr("checkedDay", .stringAttributeType, ""),
                                          attr("order", .integer64AttributeType, 0)])
        let duty = entity(Duty.self, [attr("when", .stringAttributeType, ""), attr("title", .stringAttributeType, ""),
                                      attr("detail", .stringAttributeType, ""), attr("assignee", .stringAttributeType, "")])

        func link(_ childName: String, _ child: NSEntityDescription) {
            let toMany = NSRelationshipDescription()
            toMany.name = childName; toMany.destinationEntity = child; toMany.minCount = 0; toMany.maxCount = 0
            toMany.deleteRule = .cascadeDeleteRule; toMany.isOptional = true
            let toOne = NSRelationshipDescription()
            toOne.name = "household"; toOne.destinationEntity = household; toOne.minCount = 0; toOne.maxCount = 1
            toOne.deleteRule = .nullifyDeleteRule; toOne.isOptional = true
            toMany.inverseRelationship = toOne; toOne.inverseRelationship = toMany
            household.properties.append(toMany); child.properties.append(toOne)
        }
        link("members", member); link("items", item); link("doneRecords", done); link("packItems", pack); link("duties", duty)

        let m = NSManagedObjectModel(); m.entities = [household, member, item, done, pack, duty]; return m
    }()
}

extension Int64 { var hm: String { Int(self).hm } }
extension Int {
    /// 0時からの分 → "10:20"
    var hm: String { String(format: "%d:%02d", self / 60, self % 60) }
}
