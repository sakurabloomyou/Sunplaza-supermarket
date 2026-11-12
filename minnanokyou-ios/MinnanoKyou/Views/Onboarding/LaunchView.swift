import SwiftUI

struct LaunchView: View {
    @Environment(AppState.self) private var app
    var body: some View {
        VStack(alignment: .leading, spacing: 16) {
            HStack(spacing: 12) {
                Image("SplashMark").resizable().frame(width: 52, height: 52).clipShape(RoundedRectangle(cornerRadius: 12))
                Text("みんなのきょう").font(.headline).foregroundStyle(Theme.accentHex)
            }
            VStack(alignment: .leading, spacing: 6) {
                Text("もの忘れが気になり始めた方（軽度認知症・MCI）と、そのご家族のためのアプリ").bold().foregroundStyle(Theme.accentHex)
                Divider()
                LabeledContent("ご家族", value: "予定を入れて、離れていても様子を確認")
                LabeledContent("ご本人", value: "お知らせとボードで、今日のことがわかる")
            }
            .font(.subheadline).padding(12)
            .background(.white, in: RoundedRectangle(cornerRadius: Theme.cardRadius))
            Text("家族の予定を、\nご本人のiPhoneにも。").font(.title.bold())
            Spacer()
            Disclaimer()
            Text("約3分の質問で、ご家庭に合う機能を選びます").font(.footnote).foregroundStyle(Theme.muted)
                .frame(maxWidth: .infinity)
            Button("家族として始める") { app.route = .onboarding }.buttonStyle(PrimaryButtonStyle())
            Button("招待コードを入力する") { app.route = .invite }
                .frame(maxWidth: .infinity, minHeight: Theme.minTap).bold()
        }
        .padding(20)
        .background(LinearGradient(colors: [Theme.accentSoft, .white], startPoint: .top, endPoint: .center))
    }
}
