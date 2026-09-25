---
title: "여러 기록 엮기"
parent: "타임라인 작성"
grand_parent: "기법 · 분석"
nav_order: 1290
---

# 여러 기록 엮기 (Correlation)

정규화한 시각과 앱 이름 같은 공통 열쇠로 서로 다른 아이폰 기록을 한 흐름에 이어 붙여, 한 기록만으로는 보이지 않는 앞뒤 관계를 확인하는 방법입니다.

## 언제 쓰나

메시지 DB 하나, 사진 DB 하나만 보면 각 기록이 말하는 사실만 알 수 있지만, 같은 시간대의 네트워크 사용량이나 위치 기록을 나란히 놓으면 그 앞뒤에 기기에서 무슨 일이 있었는지 더 촘촘하게 볼 수 있습니다. 한 기록의 시각이 의심스러울 때 다른 기록과 맞춰 보는 데에도 씁니다. 엮기 전에 모든 시각을 [시각 정규화 (Time Normalization)](time-normalization.md)로 같은 기준에 맞춰 둡니다.

## 엮을 때 쓰는 열쇠

기록을 잇는 열쇠는 크게 세 가지입니다. 첫째는 정규화한 시각이고, 둘째는 앱을 가리키는 번들 이름이나 프로세스 이름이며, 셋째는 한 사건에 속한 로그를 묶는 식별자입니다. 시각만으로 엮으면 같은 분에 일어난 무관한 일까지 붙어 버리지만, 앱 이름이 같은 행끼리 먼저 묶고 시각을 맞추면 잘못 엮이는 경우가 줄어듭니다. 번들 ID 를 읽는 법은 [번들 ID와 앱 그룹 (Bundle ID·App Group)](../../../01-foundations/value-decoding/bundle-id-app-group.md)에 있습니다.

아래는 iOS 27.0 백업에서 시각 칸과 앱을 가리키는 칸이 한 행에 같이 있는 것을 이름으로 확인한 곳입니다(확인 범위: iPhone 13 mini, iOS 27.0). 값은 읽지 않았고, 각 시각 칸의 기준점은 확인하지 못했으므로 [시각 정규화](time-normalization.md)의 절차대로 값을 보고 판단합니다.

| 파일(도메인 :: 경로) | 표 | 시각 칸 | 앱을 가리키는 칸 | 함께 볼 페이지 |
|---|---|---|---|---|
| `WirelessDomain :: Library/Databases/DataUsage.sqlite` | `ZPROCESS` | `ZFIRSTTIMESTAMP`, `ZTIMESTAMP` | `ZBUNDLENAME`, `ZPROCNAME` | [앱별 데이터 사용량](../../../02-artifacts/network/data-usage.md) |
| 같은 파일 | `ZLIVEUSAGE` | `ZTIMESTAMP` | `ZBUNDLENAME`, `ZPROCNAME` | 같은 페이지 |
| 같은 파일 | `ZWIFIDATA` | `ZTIMESTAMP`, `ZTIMEAT`, `ZDHCPLEASETIME` | — | [와이파이 기록](../../../02-artifacts/network/wifi.md) |
| `RootDomain :: Library/Caches/locationd/consolidated.db` | `GeoFence` | `Timestamp` | `BundleId` | — |

같은 DataUsage.sqlite 의 `ZEVENT`, `ZPEER`, `ZCHECKUPEVENT`, `ZTSHOOTINGDATA`, `ZDEMOLIVEUSAGE` 표에도 `ZTIMESTAMP` 칸이 있습니다(확인 범위: iPhone 13 mini, iOS 27.0). 메시지와 사진처럼 앱이 정해진 기록은 [메시지 (iMessage·SMS)](../../../02-artifacts/communications/messages/index.md)와 [사진 보관함 (Photos Library)](../../../02-artifacts/media/photos/index.md)의 시각 칸을 그대로 쓰면 되고, 사진 쪽에는 사건마다 시간대 칸이 붙어 있어(칸 이름은 시각 정규화 페이지의 표) 현지 시각과 UTC 를 함께 맞출 후보가 됩니다. 다만 그 시간대 값의 쓰임새는 이 핸드북에서 확인하지 못했습니다.

통합 로그를 따로 확보했다면, 한 시각 변경 사건에 속한 로그들은 같은 ActivityID 를 공유합니다. 이 값은 터미널에서는 16진수로, Console 에서는 10진수로 보이므로 두 화면에서 뽑은 로그를 엮을 때는 진법을 맞춰야 같은 사건끼리 묶입니다 [1]. 통합 로그 형식은 [통합 로그 형식 (Unified Log·tracev3)](../../../01-foundations/data-formats/unified-log.md), 찾을 사건은 [통합 로그에서 찾을 것 (Unified Log Events)](../../../02-artifacts/logs/unified-log-events.md)에 있습니다.

## 절차

1. **수집 시각을 기준점으로 적습니다.** 로컬 백업에서는 `Manifest.plist` 의 `Date` 키와 `Info.plist` 의 `Last Backup Date` 키가 백업을 만든 시각을 담는 자리이고(키 이름은 확인 범위: iPhone 13 mini, iOS 27.0), 이 시각이 타임라인의 끝이 됩니다. 이보다 뒤에 찍힌 기록은 [시각 조작 흔적](time-manipulation.md)에서 다시 봅니다. 백업의 구조는 [로컬 백업 (Finder·Apple 기기 앱·iTunes Backup)](../../../01-foundations/backups/local-backup/index.md)에 있습니다.
2. **수집 범위에 무엇이 들어 있는지 확인합니다.** 암호화하지 않은 iOS 27.0 로컬 백업의 관찰 메모에는 `knowledgeC.db`, 바이옴(Biome) 스트림 파일, 통합 로그(tracev3·logarchive), powerlog DB 가 나오지 않았고, 통화 기록 DB 대신 `com.apple.CallHistorySyncHelper.plist` 만 보였습니다(확인 범위: iPhone 13 mini, iOS 27.0). 이런 백업 하나로는 이 기록들을 타임라인에 넣을 수 없으니, 빠진 기록이 무엇인지 타임라인 머리에 적어 둡니다. 수집 방법별 범위는 [모바일 증거 확보 (Acquisition)](../../acquisition/mobile-acquisition/index.md)에서 다룹니다.
3. **모든 시각을 정규화합니다.** 기록마다 원래 값, 단위, UTC 시각, 시간대를 한 표에 모읍니다.
4. **앱 이름으로 먼저 묶습니다.** 번들 이름이나 프로세스 이름이 같은 행끼리 모은 뒤, 그 안에서 시각 순서로 늘어놓습니다.
5. **시간 창을 정해 다른 기록을 붙입니다.** 관심 있는 사건 앞뒤로 창을 정하고, 그 안에 든 다른 기록의 행을 끼워 넣습니다. 창의 폭과 그렇게 정한 이유를 결과에 적어 둡니다.
6. **앞뒤가 맞는지 확인합니다.** 같은 사건을 두 기록이 서로 다른 순서로 보여 주거나 수집 시각보다 뒤에 있는 행이 나오면, 엮은 결과를 그대로 쓰지 말고 [시각 조작 흔적](time-manipulation.md)의 확인 순서로 넘어갑니다.

## 도구

공개 도구는 기록을 뽑아 주는 데까지 쓰고, 엮은 결과는 표로 직접 확인하는 편이 안전합니다. 예를 들어 MVT 의 `check-backup` 은 결과를 JSON 파일 몇 개로 내고, 탐지한 항목은 이름 끝에 `_detected` 가 붙은 파일에 따로 담습니다 [2]. iLEAPP 나 MVT 가 여러 기록을 한 타임라인 파일로 합치는지, 합친다면 어떤 형식인지는 이 핸드북에서 확인하지 못했으므로, 쓰는 버전의 문서와 출력으로 직접 확인합니다. 도구 출력을 믿기 전에 할 일은 [도구 검증 (Tool Validation)](../../reporting/tool-validation.md)에 있습니다.

## 함정과 한계

백업에 없는 기록은 엮을 수 없어서, 빈 시간대가 "기기를 쓰지 않았다" 는 뜻이 아니라 "이 수집 범위에 기록이 없다" 는 뜻일 수 있습니다. 바이옴 관련 plist 키(`com.apple.biome.sage.transcript.LastCollectionEndTime`, `AppUsageBiomeStartDate` 등)나 부팅 관련 키(`com.apple.cameracaptured.plist` 의 `boot-time`, `com.apple.contextsync.subscriptions.plist` 의 `lastBootUUID`, `com.apple.Accessibility.Assets.plist` 의 `StoreCurrentBootTime`)는 이름만 보이고(확인 범위: iPhone 13 mini, iOS 27.0) 뜻과 기준점을 확인하지 못했으므로, 엮는 열쇠로 쓰지 않습니다. `SysSharedContainerDomain-systemgroup.com.apple.mobiletimerd` 의 `Library/analytics.sqlite`, `Library/local.sqlite` 도 파일이 있는 것만 확인했습니다(확인 범위: iPhone 13 mini, iOS 27.0). 각 기록이 시각을 적는 때가 사건이 일어난 순간인지 저장하거나 집계한 순간인지는 기록마다 따로 확인해야 하고, 그것을 확인하지 못한 기록 사이의 몇 초에서 몇 분 차이로 앞뒤를 단정하지 않습니다.

## 결과를 어떻게 해석하나

두 기록이 같은 시간 창에 들어 있다는 것은 그 시간대에 두 일이 함께 있었다는 것까지만 보여 주고, 한쪽이 다른 쪽을 일으켰다는 것은 보여 주지 않습니다. 보고서에는 "14:02~14:05 UTC 사이에 이 번들 이름으로 데이터 사용량 기록이 있고, 같은 창에 메시지 발신 기록이 있다" 처럼 각 기록이 말하는 만큼을 나란히 적고, 쓴 시간 창과 빠진 기록을 함께 밝힙니다. 보고서 문장은 [포렌식 보고서 (Forensic Report)](../../reporting/forensic-report.md)를 참고합니다.

## 참고 문헌

1. Don't Trust the Clock: Timestamp Discrepancies in iOS Unified Logs (ios-unifiedlogs.com) — https://www.ios-unifiedlogs.com/post/ios-unified-logs-don-t-trust-the-clock-timestamp
2. Check an iTunes Backup (MVT 문서) — https://docs.mvt.re/en/latest/ios/backup/check/
