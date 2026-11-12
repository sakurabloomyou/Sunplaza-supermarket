import SwiftUI
import CloudKit
import UIKit

@main
struct MinnanoKyouApp: App {
    @UIApplicationDelegateAdaptor(AppDelegate.self) private var delegate
    @State private var appState = AppState()
    @Environment(\.scenePhase) private var phase
    private let pc = PersistenceController.shared

    var body: some Scene {
        WindowGroup {
            RootView()
                .environment(appState)
                .environment(\.managedObjectContext, pc.viewContext)
                .onAppear {
                    AppDelegate.appState = appState
                    RemoteChangeNotifier.shared.start { [appState] in appState.role }
                }
        }
        .onChange(of: phase) { _, p in
            if p == .active { Task { await NotificationScheduler.shared.refresh(role: appState.role) } }
        }
    }
}

/// 共有リンク（iCloud の招待URL）から開かれたときに、共有を受け入れる。
final class AppDelegate: NSObject, UIApplicationDelegate {
    static var appState: AppState?
    func application(_ application: UIApplication, configurationForConnecting s: UISceneSession,
                     options: UIScene.ConnectionOptions) -> UISceneConfiguration {
        let c = UISceneConfiguration(name: nil, sessionRole: s.role)
        c.delegateClass = SceneDelegate.self
        return c
    }
}

final class SceneDelegate: NSObject, UIWindowSceneDelegate {
    func windowScene(_ windowScene: UIWindowScene, userDidAcceptCloudKitShareWith metadata: CKShare.Metadata) {
        Task { @MainActor in
            try? await FamilySharing.shared.accept(metadata)
            if let app = AppDelegate.appState, app.role == nil { app.route = .invite }
        }
    }
}

/// 起動後の画面の振り分け。
struct RootView: View {
    @Environment(AppState.self) private var app
    @State private var showSplash = true

    var body: some View {
        ZStack {
            switch app.route {
            case .launch: LaunchView()
            case .onboarding: OnboardingFlow()
            case .invite: InviteCodeView()
            case .familyHome: FamilyHomeView()
            case .selfBoard: SelfBoardView()
            }
            if showSplash && app.isFirstLaunchToday {
                SplashView().transition(.opacity)
            }
        }
        .task {
            // その日の最初の起動だけ 2 秒表示（要・当事者家族の確認）。
            try? await Task.sleep(for: .seconds(2))
            withAnimation(.easeOut(duration: 0.3)) { showSplash = false }
            app.markLaunched()
        }
    }
}
