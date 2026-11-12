import SwiftUI
import SwiftData

@main
struct MinnanoKyouApp: App {
    @State private var appState = AppState()

    var body: some Scene {
        WindowGroup {
            RootView()
                .environment(appState)
        }
        .modelContainer(HouseholdStore.container)
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
            // 初回（その日の最初）だけ 2 秒表示。2 回目以降は表示しない（要・当事者家族の確認）。
            try? await Task.sleep(for: .seconds(2))
            withAnimation(.easeOut(duration: 0.3)) { showSplash = false }
            app.markLaunched()
        }
    }
}
