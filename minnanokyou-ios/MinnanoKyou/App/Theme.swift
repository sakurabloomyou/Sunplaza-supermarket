import SwiftUI

/// 試作で WCAG のコントラスト比を確認した配色（明るい表示の値）。
/// 緑の文字 7.98:1、補足の文字 8.19:1、オレンジの文字 5.79:1、枠線 4.34:1（白背景に対して）。
/// 2026年11月15日：高齢者はグレーが見えにくい・白い物が白い地に溶けて認識されにくいとの資料を受け、
/// 枠線を緑みのある色に変え、選ぶ前のボタンにうすい緑の地（pickFill）を付けた。
enum Theme {
    static let accent = Color("AccentColor")
    static let accentHex = Color(red: 0x1F/255, green: 0x5A/255, blue: 0x4E/255)
    static let accentSoft = Color(red: 0xDC/255, green: 0xEB/255, blue: 0xE6/255)
    static let muted = Color(red: 0x44/255, green: 0x52/255, blue: 0x4E/255)
    static let control = Color(red: 0x5F/255, green: 0x80/255, blue: 0x77/255)
    /// 選ぶ前のボタンの地（白い画面に溶け込まないように）
    static let pickFill = Color(red: 0xE8/255, green: 0xF0/255, blue: 0xEC/255)
    static let warm = Color(red: 0x8A/255, green: 0x4B/255, blue: 0x00/255)
    static let warmSoft = Color(red: 0xFB/255, green: 0xEB/255, blue: 0xCF/255)
    static let sunk = Color(red: 0xF5/255, green: 0xF8/255, blue: 0xF6/255)

    static let cardRadius: CGFloat = 16
    static let controlRadius: CGFloat = 12
    /// Apple HIG の最小タップ領域
    static let minTap: CGFloat = 44
}

struct PrimaryButtonStyle: ButtonStyle {
    func makeBody(configuration: Configuration) -> some View {
        configuration.label
            .font(.title3.bold())
            .frame(maxWidth: .infinity, minHeight: 54)
            .foregroundStyle(.white)
            .background(Theme.accentHex.opacity(configuration.isPressed ? 0.8 : 1),
                        in: RoundedRectangle(cornerRadius: Theme.controlRadius))
    }
}
