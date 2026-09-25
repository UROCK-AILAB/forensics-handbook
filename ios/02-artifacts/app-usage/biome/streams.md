---
title: "저장 위치와 스트림"
parent: "바이옴"
grand_parent: "아티팩트 · 앱 설치·사용 흔적"
nav_order: 380
---

# 저장 위치와 스트림 (Streams)

## 한 줄 요약

바이옴은 기록 종류마다 스트림 폴더를 하나씩 두고 그 아래 `local`·`remote`·`tombstone` 폴더에 SEGB 파일을 쌓으며, 폴더 위치는 iOS 16 에서, 파일 형식은 iOS 17 에서 바뀌었습니다.

## 무엇을 기록하나 · 왜 생기나

바이옴 (Biome) 은 앱 사용과 기기 활동 기록을 스트림 (stream) 이라는 갈래로 나눠 쌓는 저장소이고, 스트림마다 폴더가 하나씩 있어서 그 안에 SEGB 라는 이진 파일이 들어갑니다[2][3][7]. 한 연구자는 스트림이 다루는 활동으로 앱 사용, Safari 활동, 방문 장소, 알림, 지갑 거래, Siri, 메시지 활동, Apple Intelligence 를 예로 들었습니다[2].

스트림 개수는 자료마다 다릅니다. 한 연구자는 최근 기기의 사용자 영역에 스트림 폴더가 300개가 넘고 그중 84개가 포렌식에 쓸모 있는 정보를 담는다고 정리했고[2], 다른 자료는 "130개가 넘는 스트림" 이라고 적었습니다[3]. 그래서 개수를 인용할 때는 출처와 조사한 버전을 함께 적습니다.

Apple 은 바이옴 구조를 공식 문서로 공개하지 않았습니다. 이 페이지의 경로와 형식은 모두 포렌식 연구자와 도구 자료에서 나온 내용이라서, 새 버전 검체에서는 폴더를 직접 열어 맞는지 확인하고 씁니다.

## 위치와 버전별 차이

바이옴 폴더는 사용자 영역의 `/private/var/mobile/Library/Biome` 와 시스템 영역의 `/private/var/db/biome` 두 곳에 있습니다[1][7]. iOS 16 조사에서는 이 아래 `streams` 폴더가 다시 `public` 또는 `restricted` 폴더로 나뉜다고 보고했습니다[1]. 한 연구자가 버전별로 정리한 위치는 아래와 같습니다[2].

| iOS | 위치 | 파일 형식 |
|---|---|---|
| 14–15 | `/private/var/mobile/Library/Biome/streams/public`, `/private/var/mobile/Library/Biome/streams/restricted`, `/private/var/mobile/Library/DuetExpertCenter/streams/` | SEGB v1 |
| 16 | `/private/var/db/biome/streams/restricted`(iOS 16 에서 새로 생김), `/private/var/mobile/Library/Biome/streams/restricted`, `/private/var/mobile/Library/DuetExpertCenter/streams/`(`userNotificationEvents` 포함) | SEGB v1 |
| 17–26 | iOS 16 과 같은 위치 | SEGB v2 |

SEGB 파일이 꾸준히 보이는 가장 이른 버전은 iOS 14 라고 한 연구자가 적었습니다[2]. v1 을 쓰는 버전 범위는 iOS 14–16 이라는 자료[3]와 iOS 15–16 이라는 자료[6]가 있고, iOS 17 에서 v2 로 바뀐 데는 세 자료가 모두 같습니다[2][3][6].

사용자 영역의 `public` 폴더를 두고는 자료가 엇갈립니다. 버전별로 정리한 자료는 iOS 16 부터 이 폴더가 사라졌다고 적었고[2], 버전을 밝히지 않은 다른 자료는 iOS 사용자 스트림 경로로 `/private/var/mobile/Library/Biome/streams/public/` 을 들었습니다[3]. 이 페이지는 버전별로 정리한 쪽을 따르지만, 실제 검체에서는 두 폴더를 모두 찾아봅니다. iOS 27 에서의 위치는 이번 자료로 확인하지 못했습니다.

맥에도 같은 구조가 `/private/var/db/biome/streams/` 에 있습니다[3].

### 수집 범위

바이옴 SEGB 파일은 전체 파일시스템 추출에서 얻고, 로컬 백업(논리 추출)에는 드러나지 않는다고 두 자료가 적었습니다[3][7]. 관찰한 백업의 기록에도 `Library/Biome` 경로나 SEGB 파일은 없었지만, 그 기록은 DB 와 plist 만 목록으로 만들어서 백업에 바이옴이 없다고 관찰로 말할 수는 없습니다(확인 범위: iOS 27.0). 수집 방식에 따른 차이는 [모바일 증거 확보 (Acquisition)](../../../03-techniques/acquisition/mobile-acquisition/index.md)와 [로컬 백업 (Finder·Apple 기기 앱·iTunes Backup)](../../../01-foundations/backups/local-backup/index.md)에서 다룹니다.

### 백업에 보이는 바이옴 관련 설정

백업의 HomeDomain `Library/Preferences/` 에는 이름에 바이옴이 들어간 설정 파일과 키가 있습니다(확인 범위: iOS 27.0). 이 키들이 무엇의 시각이고 어떤 뜻인지는 이번 자료로 확인하지 못해서, "이런 이름의 키가 있다" 까지만 적습니다.

| 파일 | 키 이름(형식) |
|---|---|
| `com.apple.biomed.plist` | `LastCombinedBuild` (str) |
| `com.apple.biomesyncd.plist` | `CKPerBootTasks` (list), `CC_OncePerBootBackingData` (bytes), `CKStartupTime` (int) |
| `com.apple.appstored.plist` | `AppUsageBiomeStartDate` (datetime) |
| `com.apple.siriinferenced.plist` | `BiomeEventLastBackFill` (float), `SuggestionsBiomeEventLastBackFill` (float), `appIntentsBiomeBookmark` (bytes), `appIntentsTranscriptBiomeBookmark` (bytes) |
| `com.apple.siri.shortcuts.plist` | `WFInitialBiomeStreamWritesKey` (bool) |
| `com.apple.duetactivityscheduler.plist` | `widgetBiomeMigrationComplete` (bool), `widgetBiomeMigrationStartDate` (float) |
| `com.apple.lighthouse.dill.BiomeSELFIngestor.plist` | `bm_IntelligenceFlow.` 으로 시작하는 키 9개 (bytes) |
| `com.apple.das.fairscheduling.plist` | `priorityQueue` 안에 `com.apple.biomesyncd.deferredMerge` 라는 항목 이름 |

KnowledgeC 쪽 설정 파일인 `com.apple.CoreDuet.plist` 도 같은 폴더에 있습니다(확인 범위: iOS 27.0). plist 를 읽는 법은 [설정 값 (Preferences)](../../system-account/preferences.md)에 있습니다.

## 구조

### 스트림 폴더

스트림마다 폴더가 하나이고, 그 아래 `local` 에는 이 기기의 기록이, `remote` 에는 같은 Apple 계정을 쓰는 다른 iOS·macOS 기기에서 동기화된 기록이, `tombstone` 에는 기간이 지난 파일이 들어갑니다[1][3][7]. `remote` 아래는 다시 기기 식별자(GUID)별 폴더로 나뉩니다[1]. 아래 모양은 여러 자료의 경로를 합쳐 그린 예입니다.

```
/private/var/db/biome/streams/restricted/
└── App.InFocus/            스트림 폴더(이름은 버전에 따라 다름)
    ├── local/              이 기기의 SEGB 파일
    ├── remote/
    │   └── <기기 GUID>/    다른 기기에서 동기화된 SEGB 파일
    └── tombstone/          기간이 지난 파일
```

스트림 폴더에는 NSKeyedArchiver 형식의 메타데이터 plist 가 있고 여기에 `maxAge` 값이 들어 있으며, iOS 16 조사에서 이 값은 2,419,200초(28일)였습니다[1]. 스트림마다 값이 다른지는 확인하지 못했습니다. NSKeyedArchiver 를 푸는 법은 [속성 목록 파일 (plist·NSKeyedArchiver)](../../../01-foundations/data-formats/plist.md)에 있습니다.

스트림 이름은 버전에 따라 바뀝니다. iOS 16 조사에서는 `/private/var/db/biome/streams/restricted` 아래 `_DKEvent.App.InFocus` 가 보였고[1], iLEAPP 는 `App.InFocus` 라는 이름으로 찾습니다[5]. 앱 사용 스트림은 [앱 사용 스트림 (App.InFocus)](app-infocus.md)에서 자세히 다룹니다.

### 동기화 DB

동기화 상태는 `/private/var/mobile/Library/Biome/sync/sync.db` 에 남습니다. 이 DB 의 `DevicePeer` 표에는 동기화한 기기와 마지막 동기화 시각(Unix 시각)이 들어 있고, 동기화된 기록마다 GUID 가 붙습니다[1]. `remote` 아래 GUID 폴더가 어느 기기인지는 이 표와 맞춰 보고 판단합니다.

### SEGB 파일

SEGB 파일 이름은 큰 정수이고, Cocoa 기준(2001-01-01) 마이크로초 단위 시각이라서 이름만으로도 파일을 대략 언제 만들었는지 알 수 있다고 합니다[3]. 파일 안은 기록(v2 에서는 항목)을 차례로 이어 붙인 구조이고, v1 과 v2 는 아래처럼 다릅니다. 형식 전체는 [SEGB 형식 (SEGB)](../../../01-foundations/data-formats/segb.md)에서 다룹니다.

| | SEGB v1 | SEGB v2 (iOS 17 이후) |
|---|---|---|
| 파일 헤더 | 56바이트, 헤더 끝 쪽에 ASCII `SEGB`[1] | 32바이트, 맨 앞에 `SEGB`(4) + 항목 수(4, 리틀 엔디언) + 파일 생성 시각(8) + 내부용(12) + 채움(4)[6] |
| 기록 헤더 | 32바이트. 첫 4바이트가 protobuf 길이(리틀 엔디언), 오프셋 8 과 16 에 8바이트 double 시각 두 개[1][3] | 8바이트 항목 헤더[6] |
| 기록 사이 채움 | `0x00`, 다음 헤더는 8의 배수 오프셋에서 시작[1][6] | 4의 배수[6] |
| 상태·시각 | 기록 헤더 안 | 파일 끝 트레일러. 기록마다 16바이트로 항목 끝 오프셋(4, 리틀 엔디언) + 상태(4, 리틀 엔디언, 1 = Written, 3 = Deleted) + 항목 생성 시각(8)[6] |

v2 는 트레일러를 읽어야 파일을 제대로 해석할 수 있습니다[3][6]. crush 는 v1·v2 기록 모두에서 시스템이 적어 둔 CRC32 와 페이로드로 다시 계산한 값을 비교해 보여 줍니다[3]. v2 의 8바이트 항목 헤더가 어떤 칸으로 이뤄지는지는 이번 자료로 확인하지 못했습니다.

기록 상태는 Written(유효), Deleted(삭제 표시), Unknown(비었거나 알 수 없음) 세 가지로 나뉩니다[3]. Deleted 기록은 페이로드가 없어도 번호·오프셋·시각·상태가 남아 해석에 쓸 수 있고[3], iLEAPP 는 이런 기록을 페이로드 칸이 빈 행으로 보여 줍니다[5]. 페이로드는 거의 늘 프로토콜 버퍼 (Protocol Buffers) 이고 공개된 스키마가 없어서 필드 번호로 읽습니다[3][6]. 필드를 읽는 법은 [프로토콜 버퍼 (Protocol Buffers)](../../../01-foundations/data-formats/protobuf.md)에 있습니다.

## 증거로서 의미

**증명하는 것.** 스트림 폴더의 `local` 에 SEGB 기록이 있으면 이 기기가 그 종류의 사건을 그 시각에 기록했다는 사실을 보여 줍니다. `remote` 아래 GUID 폴더가 있으면 같은 Apple 계정의 다른 기기와 바이옴을 동기화했다는 사실을 보여 주고[1][7], `sync.db` 의 `DevicePeer` 표로 동기화한 기기와 마지막 동기화 시각까지 말할 수 있습니다[1]. Deleted 상태 기록은 내용이 비어도 그 자리에 기록이 있었다는 사실을 남깁니다[3].

**증명하지 못하는 것.** 기록이 없다고 그 활동이 없었다는 뜻은 아닙니다. iOS 16 조사에서 보존 기간 값은 28일이었고[1] 기간이 지난 파일은 `tombstone` 폴더에 따로 들어가서[1][3][7], `local` 만 보면 오래전 활동을 놓칠 수 있습니다. `remote` 기록은 다른 기기의 사건이라서 이 기기를 쓴 증거가 아닙니다[5][7]. 로컬 백업에 바이옴이 없다는 사실도 기기에 기록이 없었다는 뜻이 아닙니다[3][7].

보고서에는 "이 기기의 `App.InFocus` 스트림 `local` 폴더에 이 시간대의 기록이 있다" 처럼 폴더와 상태를 함께 밝혀 씁니다.

## 시각 해석

바이옴에는 시각이 여러 겹으로 남습니다. SEGB 파일 이름은 Cocoa 기준 마이크로초[3], v1 기록 헤더의 두 시각은 2001-01-01 00:00 UTC 부터 센 초를 double 로 적은 Mac 절대 시각이고[1][3], ccl_segb 는 이 둘을 `timestamp1`·`timestamp2` 로 부릅니다[4]. v2 에는 파일 헤더의 파일 생성 시각과 트레일러의 항목 생성 시각이 있고[6], ccl_segb 는 v2 의 시각을 `creation` 으로 부릅니다[4]. `sync.db` 의 동기화 시각은 Unix 시각입니다[1].

기준점이 UTC 라서 기록 자체에는 시간대가 없고, 현지 시각으로 바꿀 때는 [시간대와 시각 설정 (Time Zone)](../../system-account/time-zone.md)에서 기기 시간대를 확인합니다. `timestamp1` 과 `timestamp2` 가 각각 어떤 순간(사건 시작, 기록을 쓴 때 등)에 바뀌는지는 이번 자료로 확인하지 못해서, 두 값을 모두 보고하고 한쪽만 골라 쓰지 않습니다. 단위 변환은 [시각 값 (Mac 절대 시각·Unix·기타)](../../../01-foundations/value-decoding/time-values.md)을 따릅니다.

## 함정과 한계

도구가 바이옴을 한 폴더에서만 찾으면 시스템 영역이나 사용자 영역의 기록을 놓칠 수 있어서, `/private/var/db/biome` 과 `/private/var/mobile/Library/Biome` 두 곳을 모두 확인합니다. 스트림 이름과 폴더(`public`·`restricted`)가 버전마다 바뀌었다는 점[1][2][3]도 같은 이유로 조심합니다.

v1 과 v2 는 헤더 크기, 채움 단위, 상태를 적는 위치가 모두 달라서[1][6] 한 형식용 파서로 다른 형식을 읽으면 오프셋이 어긋납니다. `tombstone` 안 파일을 어떻게 해석하는지는 이번 자료로 확인하지 못했고, 기록을 지웠을 때 바이옴에 무엇이 남는지는 Deleted 상태 기록[3] 말고는 확인한 자료가 없습니다. 조작 흔적을 찾는 흐름은 [증거를 없애려 했나 (Anti-Forensics)](../../../04-scenarios/activity/anti-forensics/index.md)에서 이어집니다.

## 직접 분석해 보기

아래 헥스는 SEGB v1 명세[1][3]로 만든 예시이고 실제 검체에서 나온 값이 아닙니다. 56바이트 파일 헤더 바로 뒤, 첫 기록 헤더가 오프셋 `0x38` 에서 시작한다고 두었습니다.

```
오프셋  바이트                                              뜻
0x38    2A 00 00 00                                         protobuf 길이 = 0x2A = 42바이트(리틀 엔디언)
0x3C    ?? ?? ?? ??                                         (이번 자료로 뜻을 확인하지 못한 칸)
0x40    00 00 00 8C 21 F1 C5 41                             시각 1 = 736248600.0 → 2024-05-01 09:30:00 UTC
0x48    00 00 20 92 21 F1 C5 41                             시각 2 = 736248612.25 → 2024-05-01 09:30:12.25 UTC
0x50    ?? ?? ?? ?? ?? ?? ?? ??                             (이번 자료로 뜻을 확인하지 못한 칸)
0x58    (protobuf 42바이트)
0x82    00 00 00 00 00 00                                   채움
0x88    (다음 기록 헤더)
```

기록 헤더 32바이트 뒤 `0x58` 에서 페이로드 42바이트가 끝나면 `0x82` 가 되고, 다음 헤더는 8의 배수 오프셋에서 시작하므로[1][6] `0x88` 로 건너뜁니다. 시각 두 값은 8바이트를 리틀 엔디언 double 로 읽은 뒤 2001-01-01 00:00 UTC 에 초를 더해 바꿉니다.

v2 파일도 명세[6]로만 만든 예시를 들면 다음과 같습니다.

```
오프셋  바이트                                  뜻
0x00    53 45 47 42                             매직 "SEGB"
0x04    02 00 00 00                             항목 수 = 2
0x08    xx xx xx xx xx xx xx xx                 파일 생성 시각(8바이트)
0x10    (12바이트)                              내부용
0x1C    (4바이트)                               채움
...
트레일러의 기록 하나(16바이트)
        30 00 00 00                             항목 끝 오프셋 = 0x30
        03 00 00 00                             상태 = 3(Deleted)
        xx xx xx xx xx xx xx xx                 항목 생성 시각(8바이트)
```

오프셋을 어디서부터 세는지는 이번 자료로 확인하지 못해서 예시에서도 밝히지 않았습니다. v2 에서는 파일 앞부터 항목을 읽지 말고, 트레일러에서 항목 끝 오프셋과 상태를 먼저 읽은 뒤 그 범위의 항목을 찾아갑니다[3][6].

공개 도구로는 파이썬 모듈 ccl_segb 가 있고, 함수 하나로 SEGB v1 파일과 v2 파일을 모두 읽습니다[4]. crush 도 SEGB 와 바이옴을 해석하고, 소개 자료는 기록을 Written·Deleted·Unknown 상태로 나눠 설명합니다[3]. iLEAPP 는 스트림별 파서를 두고 `local` 과 `remote` 기록을 나눠 보고합니다[2][5]. 도구마다 결과가 다르면 위 헥스 순서대로 한 기록을 직접 읽어 어느 쪽이 맞는지 가립니다.

## 교차 검증

iOS 15 까지 같은 종류의 기록은 [KnowledgeC (knowledgeC.db)](../knowledgec/index.md)에 있었고 파일은 iOS 16 에도 남아 있어서[1][7], 버전이 걸친 사건은 두 곳을 함께 봅니다. 알림 스트림은 [알림 기록 (Notifications)](../notifications.md)과, 동기화한 기기는 [애플 계정 (Apple Account)](../../system-account/apple-account.md)과 맞춰 봅니다. 여러 스트림의 시각을 한 줄로 세우는 법은 [타임라인 작성 (Timeline)](../../../03-techniques/analysis/timeline/index.md)에 있습니다.

## 실습

NIST CFReDS 같은 곳에 공개된 전체 파일시스템 검체로 아래를 풀어 봅니다.

1. `/private/var/db/biome/streams` 와 `/private/var/mobile/Library/Biome/streams` 아래 `public`·`restricted` 폴더가 각각 있는지, 스트림 폴더가 몇 개인지 세어 봅니다.
2. 스트림 폴더 하나를 골라 SEGB 파일의 헤더를 보고 v1 인지 v2 인지 가려 봅니다.
3. SEGB 파일 이름을 Cocoa 기준 마이크로초로 바꾼 값과 파일 안 첫 기록의 시각을 비교해 봅니다.
4. `remote` 아래 GUID 폴더가 있다면 `sync.db` 의 `DevicePeer` 표에서 같은 기기를 찾아봅니다.
5. Deleted 상태 기록이 몇 개인지 세고, 그 시각이 스트림의 다른 기록과 어떻게 이어지는지 봅니다.

## 참고 문헌

1. D20 Forensics, "iOS 16 - Now You 'C' It, Now You Don't -- Breaking Down The Biomes Part 1" (2022-09) — https://blog.d204n6.com/2022/09/ios-16-now-you-c-it-now-you-dont.html
2. digital-forensics.it, "84 Streams Later: Exploring the Evolution of Apple Biome in iOS" (2026-07) — https://blog.digital-forensics.it/2026/07/84-streams-later-exploring-evolution-of.html
3. Be-binary 4n6, "Beyond the C — SEGB and Biome Forensics with crush" (2026-05) — https://bebinary4n6.blogspot.com/2026/05/beyond-c-segb-and-biome-forensics-with.html
4. CCL Group, ccl-segb README — https://github.com/cclgroupltd/ccl-segb
5. iLEAPP, `scripts/artifacts/biomeInfocus.py` (마지막 갱신 2026-09-03) — https://raw.githubusercontent.com/abrignoni/iLEAPP/main/scripts/artifacts/biomeInfocus.py
6. Cellebrite, "Understanding and Decoding the Newest iOS SEGB Format" — https://cellebrite.com/en/blog/understanding-and-decoding-the-newest-ios-segb-format/
7. Magnet Forensics, "Bringing it Back With Biome Data" — https://www.magnetforensics.com/blog/bringing-it-back-with-biome-data/
