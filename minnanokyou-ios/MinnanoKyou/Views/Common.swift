import SwiftUI

struct SplashView: View {
    var body: some View {
        ZStack {
            LinearGradient(colors: [Theme.accentSoft, .white], startPoint: .top, endPoint: .bottom).ignoresSafeArea()
            VStack(spacing: 18) {
                Image("SplashMark").resizable().frame(width: 120, height: 120)
                    .clipShape(RoundedRectangle(cornerRadius: 27))
                    .accessibilityHidden(true)
                Text("みんなのきょう").font(.largeTitle.bold()).foregroundStyle(Theme.accentHex)
                Text("家族の予定を、ご本人にも。").foregroundStyle(Theme.muted)
            }
        }
    }
}

struct Card<Content: View>: View {
    var fill: Color = Theme.sunk
    @ViewBuilder var content: Content
    var body: some View {
        VStack(alignment: .leading, spacing: 6) { content }
            .padding(14).frame(maxWidth: .infinity, alignment: .leading)
            .background(fill, in: RoundedRectangle(cornerRadius: Theme.cardRadius))
    }
}

struct Disclaimer: View {
    var body: some View {
        Text("このアプリは診断や治療をするものではありません。健康や治療について判断するときは、医師にご相談ください。")
            .font(.footnote).foregroundStyle(Theme.muted)
    }
}

extension Date {
    var dayKey: String { AppState.dayKey(self) }
    var minutesOfDay: Int { let c = Calendar.current.dateComponents([.hour, .minute], from: self); return c.hour! * 60 + c.minute! }
}
