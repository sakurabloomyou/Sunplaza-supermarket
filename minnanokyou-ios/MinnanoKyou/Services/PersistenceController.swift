import CoreData
import CloudKit

/// iCloud（CloudKit）の「非公開」と「共有」の2つの保存先を持つ Core Data。
/// - 自分が作った家族グループ → 非公開の保存先（private）
/// - 招待されて参加した家族グループ → 共有の保存先（shared）
final class PersistenceController {
    static let containerID = "iCloud.jp.minnanokyou.app"
    static let shared = PersistenceController()
    static let localAuthor = "app"

    let container: NSPersistentCloudKitContainer
    private(set) var privateStore: NSPersistentStore!
    private(set) var sharedStore: NSPersistentStore!
    var viewContext: NSManagedObjectContext { container.viewContext }

    init(inMemory: Bool = false) {
        container = NSPersistentCloudKitContainer(name: "MinnanoKyou", managedObjectModel: CoreDataModel.model)
        let dir = NSPersistentContainer.defaultDirectoryURL()

        let priv = NSPersistentStoreDescription(url: inMemory ? URL(fileURLWithPath: "/dev/null") : dir.appendingPathComponent("private.sqlite"))
        let privOpts = NSPersistentCloudKitContainerOptions(containerIdentifier: Self.containerID)
        privOpts.databaseScope = .private
        priv.cloudKitContainerOptions = inMemory ? nil : privOpts

        let shr = NSPersistentStoreDescription(url: inMemory ? URL(fileURLWithPath: "/dev/null") : dir.appendingPathComponent("shared.sqlite"))
        let shrOpts = NSPersistentCloudKitContainerOptions(containerIdentifier: Self.containerID)
        shrOpts.databaseScope = .shared
        shr.cloudKitContainerOptions = inMemory ? nil : shrOpts

        for d in [priv, shr] {
            d.setOption(true as NSNumber, forKey: NSPersistentHistoryTrackingKey)
            d.setOption(true as NSNumber, forKey: NSPersistentStoreRemoteChangeNotificationPostOptionKey)
        }
        container.persistentStoreDescriptions = inMemory ? [priv] : [priv, shr]

        container.loadPersistentStores { desc, error in
            if let error { assertionFailure("保存先を開けませんでした: \(error)"); return }
            guard let scope = desc.cloudKitContainerOptions?.databaseScope else { return }
            let store = self.container.persistentStoreCoordinator.persistentStore(for: desc.url!)
            if scope == .private { self.privateStore = store } else if scope == .shared { self.sharedStore = store }
        }
        if inMemory { privateStore = container.persistentStoreCoordinator.persistentStores.first; sharedStore = privateStore }

        viewContext.automaticallyMergesChangesFromParent = true
        viewContext.mergePolicy = NSMergeByPropertyObjectTrumpMergePolicy
        viewContext.transactionAuthor = Self.localAuthor
    }

    // MARK: 読み書き

    /// この端末で使う家族グループ（参加したものを優先）。
    func currentHousehold() -> Household? {
        let req = NSFetchRequest<Household>(entityName: "Household")
        req.sortDescriptors = [NSSortDescriptor(key: "createdAt", ascending: true)]
        let all = (try? viewContext.fetch(req)) ?? []
        return all.first { $0.objectID.persistentStore == sharedStore } ?? all.first
    }

    /// 家族グループと同じ保存先（非公開／共有）に子データを作る。
    /// 共有された家族グループに参加している人が追加したデータも、家族全員に届くようにするため。
    func insert<T: NSManagedObject>(_ type: T.Type, into h: Household) -> T {
        let obj = T(context: viewContext)
        if let store = h.objectID.persistentStore { viewContext.assign(obj, to: store) }
        obj.setValue(h, forKey: "household")
        return obj
    }

    func save() {
        guard viewContext.hasChanges else { return }
        do { try viewContext.save() } catch { viewContext.rollback() }
    }

    /// 新しい家族グループを作り、既定のごはん・おくすり・持ち物を入れる。
    @discardableResult
    func createHousehold(answers: ConcernAnswers, familyName: String, selfName: String) -> Household {
        let h = Household(context: viewContext)
        if let privateStore { viewContext.assign(h, to: privateStore) }
        h.id = UUID().uuidString; h.createdAt = Date(); h.selfName = selfName; h.answers = answers
        h.pickupMinutes = 620; h.returnMinutes = 990

        let me = insert(Member.self, into: h); me.name = selfName; me.isSelf = true
        let fam = insert(Member.self, into: h); fam.name = familyName
        let defaults: [(String, String, Int64, Bool)] = [
            ("bf","あさごはん",480,false),("m1","おくすり（朝）",510,true),
            ("lu","おひるごはん",720,false),("m2","おくすり（昼）",750,true),
            ("di","ばんごはん",1080,false),("m3","おくすり（夜）",1110,true)]
        for (i, d) in defaults.enumerated() where answers.takesMedication || !d.3 {
            let it = insert(DailyItem.self, into: h)
            it.key = d.0; it.title = d.1; it.minutes = d.2; it.isMedication = d.3; it.order = Int64(i)
        }
        for (i, t) in ["連絡帳","着がえ","タオル","おくすり","上ばき"].enumerated() {
            let p = insert(PackItem.self, into: h); p.title = t; p.order = Int64(i)
        }
        save()
        return h
    }

    func markDone(_ item: DailyItem, in h: Household, by: String) {
        let r = insert(DoneRecord.self, into: h)
        r.itemKey = item.key; r.day = Date().dayKey; r.by = by; r.at = Date()
        save()
    }
}
