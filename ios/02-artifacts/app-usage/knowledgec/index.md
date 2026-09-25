---
title: "KnowledgeC"
parent: "아티팩트 · 앱 설치·사용 흔적"
nav_order: 330
has_children: true
has_toc: false
---

# KnowledgeC (knowledgeC.db)

knowledgeC.db 는 앱이 앞 화면에 있던 구간, 잠금과 화면 켜짐 같은 기기 상태를 시작·끝 시각이 있는 기록으로 모아 두는 SQLite 데이터베이스이고, iOS 16 부터는 이 기록 대부분을 바이옴 (Biome) 이 넘겨받았습니다.

## 왜 중요한가

폰을 언제 얼마나 썼는지 재구성할 때 knowledgeC 는 앱 이름(번들 ID)과 초 단위 구간을 한 표에서 함께 보여 주는 기록이라서, 앱 사용과 잠금 해제 흐름을 시간 축에 바로 올릴 수 있습니다 [1][2]. 다만 iOS 16 부터 기록 대부분이 바이옴으로 옮겨 가서 [2][3], 요즘 기기에서는 knowledgeC 만 보고 끝내지 않고 바이옴과 짝을 맞춰 봐야 합니다. 옛 버전 검체를 다루거나, 도구 결과에 knowledgeC 가 비어 나온 까닭을 설명할 때에도 이 파일의 구조와 버전별 변화를 알아야 합니다.

## 한눈에 보기

| 항목 | 내용 |
|---|---|
| 위치 | `/private/var/mobile/Library/CoreDuet/Knowledge/knowledgeC.db` [1][2] |
| 얻는 방법 | 전체 파일 시스템 수집이 있어야 하고, iCloud 백업과 iTunes 방식 백업에는 들어 있지 않습니다 [1][2] |
| 형식 | SQLite. 시각은 Mac 절대 시각 (Mac Absolute Time) |
| 보관 기간 | 약 4 주 [1], 대체로 한 달 정도 [2]. 정확한 삭제 규칙은 확인하지 못함 |
| 알려 주는 것 | 앞 화면에 있던 앱과 구간, 앱 사용 사건, 잠금 상태, 화면 켜짐, 충전기 연결, 기기 방향 등 |
| 버전 | iOS 16 부터 대부분 바이옴으로 옮겨 감 [2][3] |

knowledgeC 에 기록되는 종류, 곧 활성 스트림 (stream) 의 수는 버전을 따라 늘었다가 iOS 16 에서 크게 줄었습니다 [4].

| iOS | 활성 스트림 수 [4] | 비고 |
|---|---|---|
| 13 | 50 개 넘게 | |
| 14~15 | 65 개 넘게 | |
| 16 이후 | 약 20 개 | 일부는 knowledgeC 와 바이옴에 겹쳐 남고, 일부는 거의 전부 바이옴으로 옮겨 감 [4] |

iOS 16 에서 knowledgeC 에 보이지 않게 되었다고 보고된 것은 앱 포커스, Safari 기록, 설치 기록, 기기 방향, 충전기 연결 상태입니다 [3]. 앱과 기기 상태 스트림이 각각 어떻게 바뀌었는지는 아래 하위 페이지에서 다루고, 방문 기록은 [사파리](../../browsers/safari/index.md) 페이지에서 다룹니다.

이 핸드북의 기기 관찰에서는 로컬 백업 목록에 knowledgeC.db 가 없었고, HomeDomain 항목 1979 개 가운데 `Library/CoreDuet` 경로도 `Library/Biome` 경로도 없었습니다 (확인 범위: iPhone 13 mini, iOS 27.0). 같은 백업에서 CoreDuet·바이옴과 이름이 닿는 설정 plist 는 아래처럼 보였고, 값은 읽지 않았습니다 (확인 범위: iPhone 13 mini, iOS 27.0).

```
HomeDomain :: Library/Preferences/com.apple.coreduetd.plist
  ScreenTimeSyncDisabled (bool)
  _DKThrottledActivityLasthandshake:rapport:<UUID>ActivityDate (datetime)  여러 개
  kCDIntentDeletionContactStoreChangeHistoryToken (bytes)
  kCDIntentDeletionPendingDeletesQueued (bool)
HomeDomain :: Library/Preferences/com.apple.CoreDuet.plist
  CDPrivacyPreservingLocationHashDeviceSpecificSalt (bytes)
HomeDomain :: Library/Preferences/com.apple.biomed.plist
  LastCombinedBuild (str)
HomeDomain :: Library/Preferences/com.apple.ScreenTimeAgent.plist
  ScreenTimeEnabled (bool)
  UsageGenesisDate (datetime)
  LastViewedAllActivityDate (datetime)
  SyncEnabled (bool)
```

이 키들의 뜻은 공개 자료로 확인하지 못해서 이름만 적고, 사용 기록 자체로 해석하지 않습니다. 수집 방법별로 무엇을 얻는지는 [모바일 증거 확보](../../../03-techniques/acquisition/mobile-acquisition/index.md)와 [로컬 백업](../../../01-foundations/backups/local-backup/index.md) 페이지를 봅니다.

## 읽는 순서

1. [표와 스트림 구조 (ZOBJECT·Stream)](structure.md) — ZOBJECT·ZSTRUCTUREDMETADATA·ZSOURCE 표가 이어지는 방식, 칸의 뜻, 스트림 이름 읽는 법, Mac 절대 시각 변환을 다룹니다.
2. [앱 사용 기록 (App Usage)](app-usage.md) — /app/inFocus 와 /app/usage 로 어떤 앱이 언제 앞 화면에 있었는지 읽는 법과, iOS 16 이후 바이옴으로 옮겨 간 흐름을 다룹니다.
3. [화면·잠금 상태 (Display·Device Lock)](device-state.md) — /device/isLocked, /display/isBacklit 등으로 잠금 해제와 화면 켜짐 구간을 읽는 법을 다룹니다.

## 함께 볼 페이지

iOS 16 이후 기록은 [바이옴](../biome/index.md) 허브와 [SEGB 형식](../../../01-foundations/data-formats/segb.md) 페이지에서 이어서 봅니다. 파일 형식은 [SQLite 데이터베이스](../../../01-foundations/data-formats/sqlite/index.md), 시각 변환은 [시각 값](../../../01-foundations/value-decoding/time-values.md) 페이지에 있습니다. 앱별 사용량은 [화면 사용 시간](../screen-time.md)과 [전원 로그](../powerlog.md)로 교차 확인할 수 있고, 조사 흐름은 [어떤 앱을 언제 썼나](../../../04-scenarios/activity/app-usage.md)와 [폰 사용 시간 재구성](../../../04-scenarios/activity/usage-time.md) 시나리오를 따라갑니다.

## 참고 문헌

1. Sarah Edwards (mac4n6), "Knowledge is Power! Using the macOS/iOS knowledgeC.db Database to Determine Precise User and Application Usage" (2018-08) — https://www.mac4n6.com/blog/2018/8/5/knowledge-is-power-using-the-knowledgecdb-database-on-macos-and-ios-to-determine-precise-user-and-application-usage
2. Belkasoft, "KnowledgeC Database Forensics: A Comprehensive Guide" — https://belkasoft.com/knowledgec-database-forensics-with-belkasoft
3. D20 Forensics, "iOS 16 - Now You 'C' It, Now You Don't -- Breaking Down The Biomes Part 1" (2022-09-23) — https://blog.d204n6.com/2022/09/ios-16-now-you-c-it-now-you-dont.html
4. Mattia Epifani (digital-forensics.it), "84 Streams Later: Exploring the Evolution of Apple Biome in iOS" (2026-07-26) — https://blog.digital-forensics.it/2026/07/84-streams-later-exploring-evolution-of.html
