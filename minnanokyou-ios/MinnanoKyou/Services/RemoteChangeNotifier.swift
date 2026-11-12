import CoreData
import UserNotifications

/// ほかの家族の端末からの変更（CloudKit からの取り込み）を見て、
/// 「〇〇が『おくすり（朝） 済み』にしました」をこの端末に知らせる。お知らせの予定も組み直す。
final class RemoteChangeNotifier {
    static let shared = RemoteChangeNotifier()
    private let pc = PersistenceController.shared
    private let tokenKey = "historyToken"
    private var observer: NSObjectProtocol?
    private lazy var bg: NSManagedObjectContext = pc.container.newBackgroundContext()

    func start(roleProvider: @escaping () -> DeviceRole?) {
        guard observer == nil else { return }
        observer = NotificationCenter.default.addObserver(forName: .NSPersistentStoreRemoteChange,
                                                          object: pc.container.persistentStoreCoordinator, queue: nil) { [weak self] _ in
            self?.process(role: roleProvider())
        }
    }

    private var lastToken: NSPersistentHistoryToken? {
        get {
            guard let d = UserDefaults.standard.data(forKey: tokenKey) else { return nil }
            return try? NSKeyedUnarchiver.unarchivedObject(ofClass: NSPersistentHistoryToken.self, from: d)
        }
        set {
            let d = newValue.flatMap { try? NSKeyedArchiver.archivedData(withRootObject: $0, requiringSecureCoding: true) }
            UserDefaults.standard.set(d, forKey: tokenKey)
        }
    }

    private func process(role: DeviceRole?) {
        bg.perform {
            let req = NSPersistentHistoryChangeRequest.fetchHistory(after: self.lastToken)
            guard let res = try? self.bg.execute(req) as? NSPersistentHistoryResult,
                  let txs = res.result as? [NSPersistentHistoryTransaction] else { return }
            let settings = Self.loadSettings()
            let today = Date().dayKey
            for tx in txs {
                defer { self.lastToken = tx.token }
                guard tx.author != PersistenceController.localAuthor else { continue }   // 自分の操作は知らせない
                for ch in tx.changes ?? [] where ch.changeType == .insert && ch.changedObjectID.entity.name == "DoneRecord" {
                    guard role == .family, settings.doneReport,
                          let r = try? self.bg.existingObject(with: ch.changedObjectID) as? DoneRecord,
                          r.day == today, let key = r.itemKey else { continue }
                    let title = r.household?.itemList.first { $0.key == key }?.title ?? key
                    Self.post(NotificationPlanner.doneBody(by: r.by ?? "家族", title: title))
                }
            }
            Task { @MainActor in await NotificationScheduler.shared.refresh(role: role) }
        }
    }

    static func loadSettings() -> NotificationSettings {
        UserDefaults.standard.data(forKey: "notificationSettings")
            .flatMap { try? JSONDecoder().decode(NotificationSettings.self, from: $0) } ?? NotificationSettings()
    }

    private static func post(_ body: String) {
        let c = UNMutableNotificationContent(); c.title = "みんなのきょう"; c.body = body; c.sound = .default
        UNUserNotificationCenter.current().add(UNNotificationRequest(identifier: UUID().uuidString, content: c, trigger: nil))
    }
}
