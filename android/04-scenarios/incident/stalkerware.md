---
title: "몰래 설치된 감시 앱"
parent: "시나리오 · 침해 사고"
nav_order: 1760
---

# 몰래 설치된 감시 앱 (Stalkerware)

## 조사 질문

"누군가 이 폰에 감시 앱을 깔아 두었나", "그 앱이 문자·알림·위치 같은 정보를 다른 사람에게 보낼 수 있는 상태였나", "언제 들어왔나" 같은 질문에 답하는 흐름입니다. 피해를 호소하는 사람의 폰을 보는 경우가 많고, 앱을 지우거나 설정을 바꾸기 전에 지금 상태를 먼저 확보합니다.

Google Play 보호 기능(Play Protect)의 악성 앱 분류에서 감시 앱(Stalkerware)은 기기에서 개인 정보나 민감한 사용자 데이터를 모아 감시 목적으로 제3자(기업이나 다른 개인)에게 보내는 코드입니다 [1]. 허용되는 감시 앱은 부모의 자녀 감시와 기업의 직원 감시뿐이고, 스파이·몰래 감시 도구로 내세우지 않을 것, 앱이 도는 동안 늘 떠 있는 알림(persistent notification)을 띄울 것, 스토어 설명에 감시 기능을 밝힐 것, 법을 지킬 것이 조건입니다. 배우자처럼 다른 사람을 추적하는 용도는 동의가 있어도 허용되지 않습니다 [1]. 이런 앱은 `isMonitoringTool` 메타데이터 표시를 쓰도록 되어 있습니다 [1]. 스파이웨어(Spyware)는 정책에 맞는 기능과 관계없는 사용자·기기 데이터를 모으거나 빼내거나 공유하는 앱·코드·동작이고, 오디오나 통화 녹음, 앱 데이터 탈취가 그 예입니다 [1].

기록은 어떤 앱이 접근성·알림 접근 같은 권한을 쥐고 있었는지, 계속 떠 있는 알림이 있었는지까지 알려 주지만, 누가 앱을 깔았는지나 그 앱이 실제로 무엇을 보냈는지는 이 기록만으로 알 수 없습니다.

## 먼저 확인할 것

- **OS 버전과 제조사** — 이 페이지의 설정 키와 알림 칸은 버전이나 제조사에 따라 없거나 이름이 다를 수 있으니 검체의 버전을 먼저 적어 둡니다. 사이드로드한 앱의 권한 제한처럼 버전마다 달라지는 보호 장치는 [악성 앱 흔적 분석](../../03-techniques/analysis/malicious-app-triage/index.md) 에서 이어 봅니다.
- **시간대** — `dumpsys notification` 은 `mCreationTimeMs`, `mUpdateTimeMs`, `mVisibleSinceMs` 를 숫자가 아니라 한글이 섞일 수 있는 날짜 문자열 뒤에 `+####` 모양의 시차를 붙여 찍습니다. 이 시차가 기기 시간대와 같은지는 [시간대와 시각 설정](../../02-artifacts/system-account/time-zone.md) 에서 확인합니다.
- **사용자와 프로필** — 알림 기록에는 줄마다 `uid=`, `userId=` 칸이 있습니다. 감시 앱이 업무 프로필이나 다른 사용자 공간에 숨어 있을 수 있어서 사용자 ID 별로 나눠 봅니다([보안 폴더와 작업 프로필](../../01-foundations/security-model/secure-folder-work-profile.md)).
- **수집 범위** — `dumpsys` 와 `settings` 출력은 adb 일반 셸 권한으로 받을 수 있습니다. `dumpsys notification` 은 받는 순간 떠 있는 알림 목록이라서 받기 전에 알림을 지우거나 앱을 끄지 않습니다. 앱 데이터까지 필요하면 확보 방식을 [모바일 증거 확보](../../03-techniques/acquisition/mobile-acquisition/index.md) 에서 정합니다.

## 볼 아티팩트와 순서

| 순서 | 아티팩트 | 알려 주는 것 | 링크 |
|---|---|---|---|
| 1 | settings secure 의 접근성 키 (`enabled_accessibility_services`, `accessibility_enabled`) | 접근성 서비스로 등록된 앱이 있는지 | [기기 관리자와 접근성 권한](../../02-artifacts/credentials-security/device-admin-accessibility.md) |
| 2 | settings secure 의 알림 접근 키 (`enabled_notification_listeners`) | 다른 앱의 알림을 읽는 앱이 있는지 | [설정 값](../../02-artifacts/system-account/settings.md) |
| 3 | settings secure 의 입력·자동 완성 키 (`default_input_method`, `autofill_service`, `credential_service`) | 입력 방법, 자동 완성, 자격 증명 서비스로 지정된 앱 | [설정 값](../../02-artifacts/system-account/settings.md) |
| 4 | 기기 관리자 목록 | 기기 관리자 권한을 받은 앱 | [기기 관리자와 접근성 권한](../../02-artifacts/credentials-security/device-admin-accessibility.md) |
| 5 | `dumpsys notification` 의 알림 기록 | 계속 떠 있는 알림과 그 알림을 띄운 앱 | [알림 기록](../../02-artifacts/app-usage/notification-history.md) |
| 6 | 설치 기록 | 1~5에서 찾은 앱이 언제, 어떤 경로로 들어왔는지 | [악성 앱은 어디서 들어왔나](initial-access.md) |
| 7 | 앱 사용·배터리·데이터 사용량 | 그 앱이 뒤에서 돌았는지, 얼마나 송신했는지 | [앱 사용 기록](../../02-artifacts/app-usage/usagestats/index.md), [배터리 사용 기록](../../02-artifacts/app-usage/batterystats.md), [데이터 사용량](../../02-artifacts/network/netstats.md) |

## 분석 흐름

1. **감시에 쓰이는 권한을 쥔 앱부터 모읍니다.** 감시 앱은 접근성 서비스, 알림 리스너, 기기 관리자 같은 기능을 많이 씁니다. settings secure 키 가운데 이와 이어지는 것은 `enabled_accessibility_services`, `accessibility_enabled`, `enabled_notification_listeners`, `autofill_service`, `credential_service`, `default_input_method` 입니다. 검체에서 값을 읽어 들어 있는 앱을 적고, 값을 읽는 법은 [설정 값](../../02-artifacts/system-account/settings.md) 페이지를 따릅니다. 기본 제공 앱이 아닌 이름이 나오면 그 앱을 다음 단계의 대상으로 삼습니다.

2. **기기 관리자 목록을 따로 확인합니다.** settings 키 목록에는 `device_admin` 류 키가 없을 수 있습니다. 설정 키가 없다고 기기 관리자 앱이 없다고 보지 않고, 저장 위치와 읽는 법은 [기기 관리자와 접근성 권한](../../02-artifacts/credentials-security/device-admin-accessibility.md) 에서 봅니다. 삼성 자동 차단(Auto Blocker)의 최대 제한은 기기 관리자 앱과 업무 프로필을 막습니다. 이 기능들로 폰에 접근하거나 폰을 원격으로 조종하는 공격을 막기 위해서입니다 [2]. 자동 차단 전체 설명은 [악성 앱은 어디서 들어왔나](initial-access.md) 에 있습니다.

3. **계속 떠 있는 알림을 찾습니다.** 계속 떠 있는 알림은 감시 앱이 허용되는 조건 가운데 하나이므로 [1], 알림 목록에서 대상 앱의 알림이 보이는지 봅니다. `dumpsys notification` 의 NotificationRecord 한 건에는 `pkg=`, `uid=`, `userId=`, `opPkg=`, `flags=`, `importance=`, `mImportance=`, `mCreationTimeMs=`, `mUpdateTimeMs=`, `mVisibleSinceMs=` 가 찍히고, `extras` 안에 `android.title` 과 `android.text` 가 있습니다. 1단계에서 모은 앱의 `pkg=` 줄을 찾아 알림 제목·내용과 처음 만들어진 시각을 적습니다. `flags=` 에서 진행 중(ongoing) 알림을 가리키는 비트 값은 [알림 기록](../../02-artifacts/app-usage/notification-history.md) 페이지에서 봅니다. `mImportance=MIN` 처럼 중요도가 찍힌 줄도 있으니 이 값도 함께 적어 둡니다.

4. **들어온 경로와 시각을 세웁니다.** 대상 앱의 설치자, 설치를 요청한 패키지, 첫 설치 시각을 [악성 앱은 어디서 들어왔나](initial-access.md) 의 흐름대로 읽습니다. 설치 시각이 피해자가 폰을 다른 사람에게 맡긴 시간대와 겹치는지 보는 문제는 [그 시각에 폰을 쓴 사람이 누구인가](../activity/user-attribution.md) 에서 이어 갑니다.

5. **돌았는지와 보냈는지를 봅니다.** 같은 앱이 뒤에서 실행된 흔적은 [앱 사용 기록](../../02-artifacts/app-usage/usagestats/index.md) 과 [배터리 사용 기록](../../02-artifacts/app-usage/batterystats.md) 에서, 송신량은 [데이터 사용량](../../02-artifacts/network/netstats.md) 에서 봅니다. 무엇을 밖으로 보냈는지 따지는 흐름은 [자료를 밖으로 보냈나](../exfiltration/data-exfiltration/index.md) 에 있습니다.

6. **알려진 지표와 맞춰 봅니다.** 공개된 감시 앱 지표 목록이나 점검 도구와 대조하는 법은 [악성 앱 흔적 분석](../../03-techniques/analysis/malicious-app-triage/index.md) 에서 다룹니다.

> 그림 자리: 가운데에 의심 앱 하나를 두고, 둘레에 "접근성 키", "알림 접근 키", "기기 관리자", "계속 떠 있는 알림", "설치 기록", "송신량" 을 선으로 잇고 각 선에 근거 기록 이름을 적은 그림

## 흔한 오판

**접근성이나 알림 접근 권한만 보고 감시 앱으로 단정하는 오판**이 흔합니다. 감시 앱인지는 데이터를 모아 감시 목적으로 제3자에게 보내는지로 가리므로 [1], 권한은 대상을 좁히는 단서로 쓰고 송신 흔적과 함께 판단합니다.

**부모 보호 앱이나 회사 관리 앱을 바로 불법 감시 앱으로 적는 것**도 조심합니다. 조건을 지킨 자녀 감시와 직원 감시는 허용됩니다 [1]. 다만 조건을 지켰는지는 알림과 스토어 설명 같은 다른 근거로 따로 봅니다.

**settings 키 목록에 없으니 그 기능을 쓰지 않았다고 보는 것**은 근거가 없습니다. 기기 관리자처럼 settings 키 목록에 `device_admin` 류 키가 없어도 쓰일 수 있는 기능이 있습니다.

**`dumpsys notification` 에 알림이 없으니 앱이 알림을 띄운 적이 없다고 읽는 것**도 지나칩니다. 이 출력은 받는 순간의 상태이고, 지난 알림은 [알림 기록](../../02-artifacts/app-usage/notification-history.md) 쪽에서 따로 찾습니다.

## 보고서 문장 예

| 쓰지 않을 문장 | 쓸 문장 |
|---|---|
| 가해자가 피해자 폰에 스파이 앱을 깔아 감시했다. | 기기의 설정 값 `enabled_accessibility_services` 와 `enabled_notification_listeners` 에 ○○ 앱이 들어 있습니다. 이 앱의 첫 설치 시각은 ○○일 ○○:○○(UTC ○○:○○)이고 설치자(`installer`)는 ○○입니다. 누가 설치했는지는 이 기록에 담겨 있지 않습니다. |
| 이 앱이 피해자의 메시지를 빼돌렸다. | ○○ 앱은 다른 앱의 알림을 읽을 수 있는 상태였고, ○○일부터 ○○일까지 이 앱의 데이터 송신량은 ○○로 기록되어 있습니다. 송신한 내용은 확보한 기록으로 확인되지 않습니다. |
| 이 앱은 몰래 동작했다. | 자료 확보 시점의 알림 목록(`dumpsys notification`)에서 ○○ 앱이 띄운 알림은 찾지 못했습니다. |

보고서 전체의 틀은 [포렌식 보고서](../../03-techniques/reporting/forensic-report.md) 에 있습니다.

## 함께 볼 페이지

- 아티팩트 본문: [기기 관리자와 접근성 권한](../../02-artifacts/credentials-security/device-admin-accessibility.md), [설정 값](../../02-artifacts/system-account/settings.md), [알림 기록](../../02-artifacts/app-usage/notification-history.md), [설치된 앱](../../02-artifacts/app-usage/packages/index.md), [데이터 사용량](../../02-artifacts/network/netstats.md), [dumpsys 출력](../../02-artifacts/logs/dumpsys.md)
- 보안 구조: [앱 샌드박스와 권한](../../01-foundations/security-model/sandbox-permissions.md), [보안 폴더와 작업 프로필](../../01-foundations/security-model/secure-folder-work-profile.md)
- 이어지는 시나리오: [악성 앱은 어디서 들어왔나](initial-access.md), [계정 탈취 흔적](account-takeover.md), [자료를 밖으로 보냈나](../exfiltration/data-exfiltration/index.md), [그 시각에 폰을 쓴 사람이 누구인가](../activity/user-attribution.md)
- 기법: [악성 앱 흔적 분석](../../03-techniques/analysis/malicious-app-triage/index.md)

## 참고 문헌

1. Malware categories — Play Protect (Google for Developers) — https://developers.google.com/android/play-protect/phacategories
2. Samsung Auto Blocker — Samsung Knox Documentation (2025-03-07 수정) — https://docs.samsungknox.com/admin/fundamentals/whitepaper/samsung-knox-mobile-security/system-security/samsung-auto-blocker/
