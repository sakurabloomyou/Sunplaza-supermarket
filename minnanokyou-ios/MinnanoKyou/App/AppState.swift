import Foundation
import Observation

enum Route: Equatable { case launch, onboarding, invite, familyHome, selfBoard }
enum DeviceRole: String, Codable { case family, selfUser }

/// 端末ごとの状態（どの画面から始めるか、この端末を誰が使うか）。
/// 家族で共有するデータは Core Data＋CloudKit（PersistenceController）に置く。
@Observable
final class AppState {
    var route: Route
    var role: DeviceRole? {
        didSet { defaults.set(role?.rawValue, forKey: Keys.role) }
    }
    var memberName: String {
        didSet { defaults.set(memberName, forKey: Keys.memberName) }
    }

    private let defaults: UserDefaults
    private enum Keys {
        static let role = "deviceRole", memberName = "memberName", lastLaunch = "lastLaunchDay"
    }

    init(defaults: UserDefaults = .standard) {
        self.defaults = defaults
        let saved = defaults.string(forKey: Keys.role).flatMap(DeviceRole.init(rawValue:))
        self.role = saved
        self.memberName = defaults.string(forKey: Keys.memberName) ?? ""
        switch saved {
        case .family: route = .familyHome
        case .selfUser: route = .selfBoard
        case nil: route = .launch
        }
    }

    var isFirstLaunchToday: Bool {
        defaults.string(forKey: Keys.lastLaunch) != Self.dayKey(Date())
    }
    func markLaunched() { defaults.set(Self.dayKey(Date()), forKey: Keys.lastLaunch) }
    static func dayKey(_ d: Date) -> String {
        let c = Calendar.current.dateComponents([.year, .month, .day], from: d)
        return "\(c.year!)-\(c.month!)-\(c.day!)"
    }
}
