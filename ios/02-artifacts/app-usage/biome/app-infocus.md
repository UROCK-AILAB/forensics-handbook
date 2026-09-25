---
title: "앱 사용 스트림"
parent: "바이옴"
grand_parent: "아티팩트 · 앱 설치·사용 흔적"
nav_order: 390
---

# 앱 사용 스트림 (App.InFocus)

## 한 줄 요약

iOS 15 까지 KnowledgeC.db 에 있던 앱 전경 사용 기록(`/app/inFocus`)이 iOS 16 부터 바이옴의 `App.InFocus` 스트림으로 옮겨졌고, 어느 앱이 언제 화면 앞에 나오고 들어갔는지를 번들 ID 와 함께 SEGB 기록으로 남깁니다.

## 무엇을 기록하나 · 왜 생기나

iOS 15 까지 앱을 화면 앞에 띄워 쓴 기록은 KnowledgeC.db 의 `ZOBJECT` 표에서 `ZSTREAMNAME` 이 `/app/inFocus` 인 행이었습니다[1][3]. iOS 16 에서 이 기록이 바이옴 스트림으로 옮겨졌고[1][7], iOS 16 KnowledgeC.db 의 `ZSTREAMNAME` 칸에서 `app/inFocus` 값이 사라졌다는 보고가 있습니다[1]. KnowledgeC.db 파일 자체는 iOS 16 에도 남아 있어서[1][7], 파일이 있다고 앱 사용 기록까지 거기 있다고 보면 안 됩니다. 한 상용 도구 개발사는 "Application Focus" 기록을 바이옴에서 되살렸다고 소개했습니다[7].

스트림 폴더 구조와 SEGB 형식은 [저장 위치와 스트림 (Streams)](streams.md)에서 다루고, 이 페이지는 앱 사용 스트림의 위치와 기록 내용, 해석만 다룹니다.

## 위치와 버전별 차이

| iOS | 위치 | 형식 | 출처 |
|---|---|---|---|
| 15 까지 | KnowledgeC.db `ZOBJECT` 표, `ZSTREAMNAME` = `/app/inFocus` | SQLite | [1][3] |
| 16 | `/private/var/db/biome/streams/restricted/_DKEvent.App.InFocus` | SEGB v1 | [1][3][6] |
| 17–26 | iOS 16 과 같은 위치 | SEGB v2 | [2][6] |

iLEAPP 는 2026-09-03 에 고친 파서에서 `*/[Bb]iome/streams/restricted/App.InFocus/local/*` 와 `*/[Bb]iome/streams/restricted/App.InFocus/remote/*` 두 경로 규칙으로 이 스트림을 찾습니다[5]. `[Bb]` 로 대소문자를 모두 받아서 `/private/var/db/biome` 과 `/private/var/mobile/Library/Biome` 양쪽을 잡습니다. 스트림 이름이 `_DKEvent.App.InFocus` 인 경우와 `App.InFocus` 인 경우가 각각 어느 iOS 버전, 어느 영역에 해당하는지는 이번 자료로 정확히 가르지 못해서, 검체에서는 두 이름을 모두 찾아봅니다. iOS 27 에서의 위치도 확인하지 못했습니다.

관찰한 백업의 HomeDomain `Library/Preferences/com.apple.appstored.plist` 에는 `AppUsageBiomeStartDate` (datetime) 라는 키가 있지만, 이 키가 `App.InFocus` 와 관련이 있는지는 확인하지 못했고 `App.InFocus` SEGB 파일은 관찰 기록에 없습니다(확인 범위: iOS 27.0). 바이옴을 얻으려면 어떤 수집이 필요한지는 [저장 위치와 스트림 (Streams)](streams.md)의 수집 범위 절에 있습니다.

## 구조

기록 하나의 페이로드는 프로토콜 버퍼이고, 공개된 해석이 두 가지 있습니다. 두 해석의 필드 번호가 서로 달라서 다른 스트림(스키마)을 읽은 결과로 보이지만, 그 까닭은 이번 자료로 확인하지 못했습니다.

crush 자료는 `/app/inFocus` 기록을 SEGB v1·v2 공통으로 아래처럼 읽습니다[3]. 경로 표기는 `$` 가 페이로드 전체이고 점 뒤 숫자가 필드 번호입니다.

| 필드 경로 | 뜻 | 예 |
|---|---|---|
| `$.1.1` | 스트림 이름 | `/app/inFocus` |
| `$.2` | 전경 시작 시각 | |
| `$.3` | 전경 끝 시각 | |
| `$.4.3` | 번들 ID | `com.apple.Preferences` |
| `$.5` | 동작 GUID | |
| `$.7[0].2` | 전환 이유 | `com.apple.SpringBoard.transitionReason.homescreen` |
| `$.8` | 기록을 쓴 시각 | |

iLEAPP 는 `App.InFocus` 스트림을 아래처럼 읽습니다[5].

| 필드 | 형식 | iLEAPP 의 처리 |
|---|---|---|
| 3 | 정수 | 1 은 Foreground, 0 은 Background 로 표시하고 다른 값은 그대로 보고. iLEAPP 는 이 표시가 스트림 이름에서 끌어낸 해석이라고 밝힘 |
| 4 | double | 시작 시각. `webkit_timestampsconv` 함수로 변환 |
| 6 | 문자열 | 번들 ID |
| 2, 9, 10 | — | 읽기만 하고 출력하지 않음 |

iLEAPP 결과표의 칸은 `Timestamp`, `Start Time`, `SEGB State`, `Bundle ID`, `Action`, `Sync Origin`, `Filename`, `Offset` 입니다[5]. `SEGB State` 로 Written·Deleted 를, `Sync Origin` 으로 `local`·`remote` 를 가르고, `Filename` 과 `Offset` 으로 원본 파일의 기록 위치까지 되짚을 수 있습니다.

iLEAPP 해석대로라면 앱이 앞에 나올 때와 뒤로 갈 때마다 기록이 하나씩 생기고, 사용 구간은 Foreground 기록과 그 뒤의 Background 기록을 짝지어 만들게 됩니다. 이 짝짓기 방식은 출처에 적혀 있지 않아서, 구간을 계산했다면 보고서에 분석가가 짝지은 결과라고 밝힙니다.

## 증거로서 의미

**증명하는 것.** `local` 폴더의 기록은 이 기기에서 그 번들 ID 의 앱이 그 시각에 화면 앞에 나왔거나 뒤로 갔다는 기록이 있다는 사실을 보여 줍니다. crush 해석에서 전환 이유가 있으면 홈 화면에서 열었는지, 앱 전환기나 Spotlight 에서 열었는지까지 말할 수 있습니다[1][3]. Deleted 상태 기록은 번들 ID 가 없어도 시각과 파일 안 위치가 남아서[3][5], 그 시각에 기록이 있었다는 사실은 말할 수 있습니다.

**증명하지 못하는 것.** 앱이 화면 앞에 있었다는 기록만으로 사람이 그 앱을 들여다보며 조작했다거나 누가 썼다고 말할 수는 없습니다. `remote` 폴더의 기록은 같은 Apple 계정을 쓰는 다른 기기의 사건이라서 이 기기 사용으로 읽으면 안 됩니다[5][7]. 보존 기간 밖의 사용은 남지 않았을 수 있어서[1] 기록이 없다고 그 앱을 쓰지 않았다는 뜻도 아닙니다.

보고서에는 "이 기기의 앱 사용 스트림에 이 시각 이 번들 ID 의 전경 전환 기록이 있다" 처럼 쓰고, 계산한 사용 시간은 계산 방법과 함께 적습니다.

## 시각 해석

SEGB 기록 헤더의 시각은 2001-01-01 00:00 UTC 부터 센 초를 double 로 적은 Mac 절대 시각이고[1][3], iLEAPP 는 기록 시각을 UTC 로 둡니다[5]. crush 자료는 페이로드 안의 시각도 Cocoa 시각으로 자동 변환된다고 적었습니다[3]. 헤더 시각과 페이로드 시각(crush 해석의 시작·끝·기록 시각, iLEAPP 해석의 필드 4)은 서로 다른 값이라서, 보고할 때는 어느 칸의 시각인지 밝힙니다. 현지 시각은 [시간대와 시각 설정 (Time Zone)](../../system-account/time-zone.md)에서 기기 시간대를 확인한 뒤 바꾸고, 단위 변환은 [시각 값 (Mac 절대 시각·Unix·기타)](../../../01-foundations/value-decoding/time-values.md)을 따릅니다.

iOS 16 에서 관찰된 전환 이유 값에는 `com.apple.SpringBoard.transitionReason.homescreen`, `com.apple.SpringBoard.transitionReason.externalrequest`, `com.apple.SpringBoard.transitionReason.appswitcher`, `com.apple.SpringBoard.transitionReason.spotlight` 가 있습니다[1]. 상용 도구 자료도 "SpringBoard 홈 화면에서 Safari 로 전환" 같은 정보를 보여 준다고 적었습니다[7].

보존 기간은 iOS 16 조사에서 스트림 메타데이터의 `maxAge` 가 2,419,200초(28일)였고[1], iOS 17 이후 값은 확인하지 못했습니다.

## 함정과 한계

도구 결과에서 `remote` 기록을 걸러내지 않으면 다른 기기의 사용이 이 기기의 사용처럼 타임라인에 섞입니다[5][7]. iLEAPP 는 `tombstone` 폴더 파일을 건너뛰고[5], `tombstone` 안 파일을 해석하는 방법은 이번 자료로 확인하지 못해서, 도구가 보여 주지 않는 기록이 폴더에 남아 있을 수 있습니다.

필드 3 의 Foreground·Background 표시는 iLEAPP 스스로 해석이라고 밝혔고[5], crush 와 iLEAPP 의 필드 번호도 다릅니다[3][5]. 그래서 도구 한 가지 결과만 옮기지 말고 필드 번호와 원본 값을 함께 기록합니다. 기록에는 번들 ID 만 남아서 앱 이름은 [설치된 앱 (Installed Apps·applicationState.db)](../installed-apps.md) 같은 다른 기록과 맞춰 바꾸는데, 이 절차는 이번 자료에 나온 방법이 아닙니다. 번들 ID 를 읽는 법은 [번들 ID와 앱 그룹 (Bundle ID·App Group)](../../../01-foundations/value-decoding/bundle-id-app-group.md)에 있습니다.

## 직접 분석해 보기

아래 헥스는 iLEAPP 의 필드 해석[5]과 프로토콜 버퍼 인코딩 규칙으로 만든 페이로드 예시이고 실제 검체에서 나온 값이 아닙니다. 필드 2·9·10 은 뺐고, 번들 ID 는 crush 자료의 예[3]를 썼습니다.

```
바이트                                              뜻
18 01                                               필드 3(varint) = 1 → Foreground
21 00 00 00 8C 21 F1 C5 41                          필드 4(64비트) = double 736248600.0 → 2024-05-01 09:30:00 UTC
32 15                                               필드 6(길이 있는 값), 길이 0x15 = 21바이트
63 6F 6D 2E 61 70 70 6C 65 2E 50 72                 "com.apple.Pr
65 66 65 72 65 6E 63 65 73                          eferences"
```

첫 바이트 `0x18` 은 필드 번호 3 을 왼쪽으로 세 칸 옮기고 형식 0(varint)을 더한 값이고, `0x21` 은 필드 4 와 형식 1(64비트), `0x32` 는 필드 6 과 형식 2(길이 있는 값)입니다. 필드 4 의 8바이트는 리틀 엔디언 double 로 읽어 2001-01-01 00:00 UTC 에 초를 더했습니다. 태그를 읽는 규칙은 [프로토콜 버퍼 (Protocol Buffers)](../../../01-foundations/data-formats/protobuf.md)에 있습니다.

공개 도구로는 iLEAPP 의 `biomeInfocus` 파서가 이 스트림을 표로 뽑고[5], ccl_segb 로 SEGB 파일에서 기록을 꺼낸 뒤[4] 페이로드를 프로토콜 버퍼 디코더로 풀어 볼 수 있습니다. crush 는 `/app/inFocus` 기록을 위 필드 경로대로 풀어 줍니다[3]. iLEAPP 결과의 `Filename`·`Offset` 으로 원본 기록을 찾아 위 순서대로 한 건을 직접 읽어 보면 도구 해석을 검증할 수 있습니다.

## 교차 검증

iOS 15 이하나 버전을 올린 기기는 [KnowledgeC (knowledgeC.db)](../knowledgec/index.md)의 `/app/inFocus` 기록과 이어서 봅니다. 앱별 사용 시간 합계는 [화면 사용 시간 (Screen Time)](../screen-time.md)과, 같은 시각의 알림은 [알림 기록 (Notifications)](../notifications.md)과, 화면 켜짐과 전원 상태는 [전원 로그 (PowerLog)](../powerlog.md)와 맞춰 봅니다. 조사 흐름은 [어떤 앱을 언제 썼나 (App Usage)](../../../04-scenarios/activity/app-usage.md), [폰 사용 시간 재구성 (Usage Time)](../../../04-scenarios/activity/usage-time.md), [그 시각에 폰을 쓴 사람이 누구인가 (User Attribution)](../../../04-scenarios/activity/user-attribution.md)에서 이어집니다.

## 실습

NIST CFReDS 같은 곳에 공개된 iOS 16 이후 전체 파일시스템 검체로 아래를 풀어 봅니다.

1. `_DKEvent.App.InFocus` 와 `App.InFocus` 가운데 어느 이름의 스트림 폴더가 있고, 시스템 영역과 사용자 영역 가운데 어디에 있는지 찾아봅니다.
2. 같은 번들 ID 의 Foreground 기록과 바로 뒤 Background 기록을 짝지어 사용 구간을 만들고, 짝이 맞지 않는 기록이 있는지 봅니다.
3. crush 해석의 전환 이유 필드가 있는 기록을 골라 어떤 값들이 나오는지 세어 봅니다.
4. `remote` 기록이 있다면 `Sync Origin` 으로 걸러낸 뒤와 전과 타임라인이 어떻게 달라지는지 비교해 봅니다.
5. 같은 검체의 KnowledgeC.db 에 `/app/inFocus` 행이 남아 있는지 확인합니다.

## 참고 문헌

1. D20 Forensics, "iOS 16 - Now You 'C' It, Now You Don't -- Breaking Down The Biomes Part 1" (2022-09) — https://blog.d204n6.com/2022/09/ios-16-now-you-c-it-now-you-dont.html
2. digital-forensics.it, "84 Streams Later: Exploring the Evolution of Apple Biome in iOS" (2026-07) — https://blog.digital-forensics.it/2026/07/84-streams-later-exploring-evolution-of.html
3. Be-binary 4n6, "Beyond the C — SEGB and Biome Forensics with crush" (2026-05) — https://bebinary4n6.blogspot.com/2026/05/beyond-c-segb-and-biome-forensics-with.html
4. CCL Group, ccl-segb README — https://github.com/cclgroupltd/ccl-segb
5. iLEAPP, `scripts/artifacts/biomeInfocus.py` (마지막 갱신 2026-09-03) — https://raw.githubusercontent.com/abrignoni/iLEAPP/main/scripts/artifacts/biomeInfocus.py
6. Cellebrite, "Understanding and Decoding the Newest iOS SEGB Format" — https://cellebrite.com/en/blog/understanding-and-decoding-the-newest-ios-segb-format/
7. Magnet Forensics, "Bringing it Back With Biome Data" — https://www.magnetforensics.com/blog/bringing-it-back-with-biome-data/
