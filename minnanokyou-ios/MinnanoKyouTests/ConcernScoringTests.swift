import XCTest
@testable import MinnanoKyou

/// 試作（ブラウザ版）の「例の回答」と同じ結果になることを確かめる。
final class ConcernScoringTests: XCTestCase {
    private func sample() -> ConcernAnswers {
        var a = ConcernAnswers()
        a.takesMedication = true; a.usesDayService = true
        a.categories = [.memory, .mood, .family, .wellbeing]
        a.levels = ["A1":3,"A2":2,"A3":3,"A4":1,"A5":2,"A6":1,"A7":2,"C12":2,"C13":1,"C14":1,"C15":2,"C16":0,"C17":2,
                    "E22":2,"E23":1,"E24":3,"E25":2,"E26":0,"H30":2]
        a.topThree = ["A3","E24","C12"]
        return a
    }

    func testRecommendedFeaturesAreTopThreeOnly() {
        let a = sample()
        let on = Feature.allCases.filter { a.isOn($0) }
        XCTAssertEqual(Set(on), [.medication, .workGuide, .talkTips, .placeMemo])
    }

    func testFeatureOrderByScore() {
        let fs = sample().featureScores()
        XCTAssertEqual(fs.first?.score, 6)
        XCTAssertTrue(fs.contains { $0.feature == .lifestyle && !$0.recommended })
        XCTAssertFalse(fs.contains { $0.feature == .dateClock })   // 1点はオンにならない
    }

    func testTopThreeLimitAndLowLevelRemovesTop() {
        var a = sample()
        a.toggleTop("A1")                    // 3つ選択済みなので追加されない
        XCTAssertEqual(a.topThree.count, 3)
        a.setLevel("A3", 1)                  // 2未満になったら外れる
        XCTAssertFalse(a.topThree.contains("A3"))
    }

    func testOverrideWins() {
        var a = sample()
        a.overrides[.medication] = false
        XCTAssertFalse(a.isOn(.medication))
    }

    func testDegreeScaleItems() {
        XCTAssertEqual(Concern.all.count, 30)
        XCTAssertEqual(Concern.all.filter { $0.scale == .degree }.count, 12)
    }
}

final class NotificationPlanTests: XCTestCase {
    let items: [(key: String, title: String, minutes: Int, isMedication: Bool)] =
        [("lu","おひるごはん",720,false),("m2","おくすり（昼）",750,true)]

    func testFamilyGetsLateNoticeNotMedication() {
        let p = NotificationPlanner.plan(role: .family, settings: .init(), selfName: "お母さん", pickup: 620, dutyName: "たろう", items: items)
        XCTAssertTrue(p.contains { $0.id == "late.lu" && $0.minutes == 750 })
        XCTAssertFalse(p.contains { $0.id.hasPrefix("med.") })
        XCTAssertEqual(p.first { $0.id == "pickup.at" }?.body, "お迎えの時間です。今日の送り出しは たろうさんです")
    }

    func testSelfGetsMedicationAndOffSwitchWorks() {
        var s = NotificationSettings(); s.hourBefore = false
        let p = NotificationPlanner.plan(role: .selfUser, settings: s, selfName: "お母さん", pickup: 620, dutyName: nil, items: items)
        XCTAssertTrue(p.contains { $0.id == "med.m2" })
        XCTAssertFalse(p.contains { $0.id == "pickup.h1" })
        XCTAssertEqual(p.first?.id, "pickup.prev")
    }
}
