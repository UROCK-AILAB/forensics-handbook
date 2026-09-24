---
title: "악성 코드는 어디서 들어왔나"
parent: "시나리오 · 침해 사고"
nav_order: 2540
---

# 악성 코드는 어디서 들어왔나 (Initial Access)

## 조사 질문

맥에서 악성 코드로 보이는 파일을 찾았을 때, 그 파일이 언제 어떤 길로 이 맥에 들어왔고 처음 열린 때가 언제인지 묻습니다. macOS 는 인터넷에서 받은 파일을 격리 (Quarantine) 대상으로 표시하고, 처음 열 때 게이트키퍼 (Gatekeeper) 와 XProtect 가 검사해서, 들어온 길이 여러 곳에 흔적으로 남습니다. 이 페이지는 침해 조사에서 그 흔적을 어떤 순서로 이어 보는지를 다루고, 각 아티팩트의 구조는 아티팩트 페이지로 넘깁니다. 악성 여부와 상관없이 파일 한 개의 출처를 묻는 조사는 [이 파일은 어디서 왔나](../activity/file-origin.md) 에 있습니다.

## 먼저 확인할 것

OS 버전부터 확인합니다. 게이트키퍼는 확인된 개발자의 소프트웨어인지, Apple 공증 (Notarization) 을 받아 알려진 악성 내용이 없는지, 변조되지 않았는지를 보고 [2], XProtect 는 버전에 따라 검사하는 때가 다릅니다.

| macOS 버전 | 달라지는 점 | 출처 |
|---|---|---|
| 10.15 Catalina 이후 | XProtect 가 앱을 실행할 때, 앱이 파일 시스템에서 바뀔 때, 서명이 갱신될 때 검사합니다 | [3] |
| 15 Sequoia | 격리된 앱이 공증되지 않았으면 게이트키퍼가 첫 실행을 거부하고, 오른쪽 클릭 "열기" 로 넘기는 길이 없어져 개인정보 보호 및 보안 설정에서 예외로 넣어야 실행됩니다 | [5] |
| 15 Sequoia | Endpoint Security API 가 늘어나, 사용자가 게이트키퍼를 우회한 사건과 XProtect 탐지 결과를 서드파티 보안 도구가 이벤트로 받을 수 있습니다 | [3] |
| 버전별 격리 속성 변화 | [격리 속성과 다운로드 기록](../../02-artifacts/filesystem/quarantine/index.md) 페이지에 정리합니다 | — |

게이트키퍼 정책은 App Store 만 허용, App Store 와 공증된 개발자 서명 허용(기본값), 기기 관리로 정책 덮어쓰기, 끄기 가운데 하나라서 [2], 조사 대상 맥이 어느 정책이었는지도 함께 적어 둡니다. 기기 관리를 받는 맥이면 조직의 정책부터 받아 둡니다.

시간대와 사용자도 먼저 정리합니다. 격리 이벤트 데이터베이스의 시각은 맥 절대 시각 (Mac Absolute Time) 이라서 [1] 변환이 필요하고, 변환 기준은 [맥의 시각 값](../../01-foundations/value-decoding/mac-time-values.md) 에, 현지 시각으로 옮기는 기준은 [시간대와 시계 설정](../../02-artifacts/system-account/time-zone.md) 에 있습니다. 격리 이벤트 데이터베이스는 사용자마다 따로 있어서 [1], 사용자 홈 폴더를 모두 수집했는지 확인합니다. 게이트키퍼가 마지막으로 거부한 항목은 `/private/var/db/` 아래에 있어서 [1], 사용자 폴더만 모은 수집본에는 빠집니다.

## 볼 아티팩트와 순서

| 순서 | 아티팩트 | 알려 주는 것 | 링크 |
|---|---|---|---|
| 1 | `~/Library/Preferences/com.apple.LaunchServices.QuarantineEventsV2` | 파일을 받은 시각, 받은 앱, 받은 주소와 출처 주소 | [격리 속성과 다운로드 기록](../../02-artifacts/filesystem/quarantine/index.md) |
| 2 | 파일의 `com.apple.quarantine` 확장 속성 | 이 파일이 격리 대상이었는지, 격리 데이터베이스의 어느 행과 이어지는지 | [격리 속성과 다운로드 기록](../../02-artifacts/filesystem/quarantine/index.md) |
| 3 | 다운로드 출처 속성 | 파일에 남은 다운로드 주소 | [다운로드 출처 속성](../../02-artifacts/filesystem/where-froms.md) |
| 4 | 브라우저 다운로드 기록, 메일 첨부 | 어느 브라우저나 메일로 받았는지 | [사파리](../../02-artifacts/browsers/safari/index.md), [크롬·엣지·웨일](../../02-artifacts/browsers/chromium/index.md), [애플 메일](../../02-artifacts/mail/apple-mail/index.md) |
| 5 | DMG 마운트, 파일 시스템 이벤트 | 디스크 이미지를 연 흔적과 파일이 생긴 시각 | [디스크 이미지 형식](../../01-foundations/disk-volume/dmg-sparsebundle.md), [파일 시스템 이벤트](../../02-artifacts/filesystem/fsevents/index.md) |
| 6 | `/private/var/db/.LastGKReject` | 게이트키퍼가 마지막으로 거부한 파일의 경로·시각·분류 | [실행 정책 평가 기록](../../02-artifacts/execution/execpolicy-gatekeeper.md) |
| 7 | XProtect 기록, 휴지통 | XProtect 가 탐지해 옮긴 파일 | [보안 도구 기록](../../02-artifacts/logs/xprotect.md), [휴지통](../../02-artifacts/file-folder-usage/trash.md) |
| 8 | 통합 로그, 실행 흔적 | 첫 실행 시각과 그 뒤 동작 | [통합 로그에서 찾을 것](../../02-artifacts/logs/unified-log-events/index.md), [KnowledgeC](../../02-artifacts/execution/knowledgec/index.md) |

### 격리 이벤트 데이터베이스에서 쓰는 칸

격리 이벤트 데이터베이스는 SQLite 파일이고 표 이름은 `LSQuarantineEvent` 입니다 [1]. mac_apt 가 읽는 칸은 `LSQuarantineEventIdentifier`, `LSQuarantineTimeStamp`, `LSQuarantineAgentBundleIdentifier`, `LSQuarantineAgentName`, `LSQuarantineDataURLString`, `LSQuarantineSenderName`, `LSQuarantineSenderAddress`, `LSQuarantineTypeNumber`, `LSQuarantineOriginTitle`, `LSQuarantineOriginURLString`, `LSQuarantineOriginAlias` 이고 [1], 칸마다의 뜻과 값은 [격리 속성과 다운로드 기록](../../02-artifacts/filesystem/quarantine/index.md) 페이지에 있습니다. 침해 조사에서는 시각, 받은 앱, 받은 주소 칸을 먼저 봅니다. `LSQuarantineTimeStamp` 는 2001-01-01 00:00:00 UTC 부터 센 초라서 [1], 유닉스 시각으로 바꿀 때 978307200 초를 더합니다.

```sql
SELECT LSQuarantineEventIdentifier,
       datetime(LSQuarantineTimeStamp + 978307200, 'unixepoch') AS time_utc,
       LSQuarantineAgentBundleIdentifier,
       LSQuarantineAgentName,
       LSQuarantineDataURLString,
       LSQuarantineOriginURLString,
       LSQuarantineSenderName,
       LSQuarantineSenderAddress,
       LSQuarantineTypeNumber
FROM LSQuarantineEvent
ORDER BY LSQuarantineTimeStamp;
```

### 게이트키퍼가 마지막으로 거부한 항목

`/private/var/db/.LastGKReject` 는 plist 이고, 키는 아래 세 가지입니다 [1].

| 키 | 담긴 것 |
|---|---|
| `BookmarkData` | 거부한 파일의 경로·생성일·볼륨 정보. 읽는 법은 [파일 참조 데이터](../../01-foundations/value-decoding/alias-bookmark.md) 에 있습니다 |
| `TimeStamp` | 거부한 시각 |
| `XProtectMalwareType` | 거부 분류. mac_apt 는 이 값을 unsigned, modified bundle, signed app, modified app 네 부류로 나눕니다 |

`XProtectMalwareType` 숫자마다의 뜻은 공개 자료로 확인하지 못했습니다.

## 분석 흐름

1. 악성으로 보이는 파일의 경로와 해시를 확보하고, OS 버전과 사용자 목록을 정리합니다.
2. 사용자마다 격리 이벤트 데이터베이스를 사본으로 열어 시각을 UTC 로 바꾸고, 파일이 디스크에 생긴 때보다 앞선 행을 추립니다. SQLite 를 여는 주의점은 [SQLite 데이터베이스](../../01-foundations/data-formats/sqlite/index.md) 페이지를 따릅니다.
3. 파일에 격리 확장 속성이 남아 있으면 그 속성과 데이터베이스 행을 이어 봅니다. 잇는 방법은 [격리 속성과 다운로드 기록](../../02-artifacts/filesystem/quarantine/index.md) 에 있습니다.
4. 받은 앱이 브라우저인지, 메일인지, 다른 앱인지로 들어온 길을 가르고, 해당 앱의 다운로드·첨부 기록에서 같은 주소와 시각을 찾습니다.
5. 받은 파일이 DMG 면 `/Volumes/` 아래 마운트 흔적과 파일 시스템 이벤트로 디스크 이미지 안의 앱이 어디로 복사되었는지 따라갑니다.
6. 첫 실행을 확인합니다. 게이트키퍼는 다운로드한 소프트웨어를 처음 열 때 사용자 승인을 받는데, 데이터 파일인 줄 알고 실행 코드를 여는 속임수를 막으려는 장치입니다 [2]. 승인·거부 흔적은 `.LastGKReject` 와 통합 로그에서 찾고, 로그에서 볼 내용은 [통합 로그에서 찾을 것](../../02-artifacts/logs/unified-log-events/index.md) 에 있습니다.
7. XProtect 가 악성 코드를 찾으면 실행을 막고 휴지통으로 옮긴 뒤 Finder 에서 알리기 때문에 [3], 휴지통과 XProtect 기록에 같은 파일이 있는지 봅니다.
8. 받은 시각, 파일이 생긴 시각, 첫 실행 시각을 [타임라인](../../03-techniques/analysis/timeline/index.md) 에 올리고, 그 뒤의 지속성은 [악성 코드 지속성 찾기](persistence.md) 로 이어 봅니다.

## 흔한 오판

- **게이트키퍼가 있으니 서명 없는 앱은 실행되지 않았다고 보는 경우.** 첫 실행에는 사용자 승인이 끼어들어서 [2], 사용자가 승인하면 실행됩니다. AMOS 사례에서도 서명 없는 표본을 사용자가 오른쪽 클릭 "열기" 로 실행하도록 유도했습니다 [4]. macOS 15 부터는 이 방법이 막히고 설정에서 예외로 넣어야 해서 [5], 사용자가 설정 화면에서 예외를 허용했는지도 함께 봅니다. 이 사례의 나머지 행동은 [정보 탈취 악성 코드](infostealer.md) 에 있습니다.
- **로그의 실행 경로를 파일이 놓인 경로로 읽는 경우.** 게이트키퍼는 앱을 무작위로 정한 읽기 전용 위치에서 여는데, 앱과 함께 배포된 플러그인이 자동으로 로드되지 않게 하려는 장치입니다 [2]. 필자 해석으로는 실행 기록에 남은 경로가 사용자가 연 파일의 경로와 다를 수 있습니다.
- **`.LastGKReject` 를 거부 이력 전체로 읽는 경우.** 이 파일은 마지막으로 거부한 항목만 담습니다 [1]. 앞선 거부는 통합 로그 같은 다른 기록에서 따로 찾아야 하는데, 어느 로그 항목에 남는지는 이 페이지의 출처로 확인하지 못했습니다.
- **`XProtectMalwareType` 을 악성 코드 이름으로 읽는 경우.** mac_apt 가 나누는 네 부류는 서명과 변조 상태의 분류입니다 [1].
- **XProtect 가 탐지하지 않았으니 정상 파일이라고 보는 경우.** XProtect 는 YARA 서명으로 검사하고 갱신 여부를 기본값으로 매일 확인합니다 [3]. 필자 해석으로는 서명이 나오기 전의 새 표본은 탐지되지 않을 수 있습니다. 공증 폐기 티켓은 XProtect 서명보다 훨씬 자주 확인한다는 점도 함께 적어 둡니다 [3].
- **격리 이벤트 데이터베이스에 행이 없으니 인터넷에서 오지 않았다고 보는 경우.** 데이터베이스는 사용자마다 따로 있어서 [1] 다른 계정이 받은 파일은 그 계정 쪽에 있습니다. 필자 해석으로는 행이 지워졌을 수도 있어서, 행이 없다는 사실만으로 들어온 길을 단정하지 않습니다.

## 보고서 문장 예

> 사용자 ○○의 격리 이벤트 데이터베이스(`com.apple.LaunchServices.QuarantineEventsV2`) `LSQuarantineEvent` 표에 `LSQuarantineAgentName` 이 "○○"이고 `LSQuarantineDataURLString` 이 "○○"인 행이 있으며, `LSQuarantineTimeStamp` 를 바꾼 시각은 ○○○○-○○-○○ ○○:○○:○○(UTC)입니다. 이 기록은 그 앱이 그 시각에 그 주소에서 파일을 받은 기록이 있다는 사실을 보여 주지만, 사용자가 받은 파일을 실행했는지는 이 행만으로 쓰지 않고 실행 흔적을 따로 확인해 적습니다.

## 함께 볼 페이지

- [격리 속성과 다운로드 기록 (Quarantine)](../../02-artifacts/filesystem/quarantine/index.md) — 격리 속성과 데이터베이스 구조 전체
- [실행 정책 평가 기록 (ExecPolicy·Gatekeeper)](../../02-artifacts/execution/execpolicy-gatekeeper.md) — 게이트키퍼 평가 기록
- [서명·공증·무결성 보호 (Code Signing·Notarization·SIP)](../../01-foundations/protection/codesign-notarization-sip.md) — 서명과 공증의 기초
- [악성 코드 흔적 분석 (Malware Triage)](../../03-techniques/analysis/malware-triage/index.md) — 찾은 파일을 살피는 절차
- [악성 코드 지속성 찾기 (Persistence)](persistence.md) — 들어온 뒤 자리를 잡았는지

## 참고 문헌

1. mac_apt, plugins/quarantine.py (Yogesh Khatri) — https://raw.githubusercontent.com/ydkhatri/mac_apt/master/plugins/quarantine.py
2. Apple Platform Security, "Gatekeeper and runtime protection in macOS" — https://support.apple.com/guide/security/gatekeeper-and-runtime-protection-sec5599b66df/web
3. Apple Platform Security, "Protecting against malware in macOS" — https://support.apple.com/guide/security/protecting-against-malware-sec469d47bd8/web
4. SentinelOne, "Atomic Stealer: Threat Actor Spawns Second Variant of macOS Malware Sold on Telegram" — https://www.sentinelone.com/blog/atomic-stealer-threat-actor-spawns-second-variant-of-macos-malware-sold-on-telegram/
5. Howard Oakley, "Gatekeeper and notarization in Sequoia" (The Eclectic Light Company, 2024-08-10) — https://eclecticlight.co/2024/08/10/gatekeeper-and-notarization-in-sequoia/
