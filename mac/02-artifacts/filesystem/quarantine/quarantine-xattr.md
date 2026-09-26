---
title: "격리 확장 속성"
parent: "격리 속성과 다운로드 기록"
grand_parent: "아티팩트 · 파일 시스템"
nav_order: 980
---

# 격리 확장 속성 (com.apple.quarantine)

격리 확장 속성 (com.apple.quarantine)은 인터넷 등에서 받은 파일에 붙는 확장 속성이고, 플래그·격리 시각·받은 앱 이름·이벤트 UUID 네 필드가 들어 있어서 파일 하나만 보고도 어떤 앱을 거쳐 언제 들어왔는지 어림할 수 있습니다.

## 무엇을 기록하나 · 왜 생기나

Safari 같은 앱으로 인터넷에서 앱이나 파일을 받으면 그 파일에 `com.apple.quarantine` 확장 속성이 붙습니다. 이 속성은 잘 떨어지지 않고, 압축 파일을 풀면 안에서 나온 파일들에도 이어집니다 [1]. AirDrop으로 받은 앱에도 격리가 걸립니다 [2].

속성은 첫 실행 뒤에 지워지지 않고 플래그 값만 바뀐 채 남습니다 [2]. 한 번 열어 본 앱에서도 속성을 볼 수 있고, 플래그를 보면 그 앱이 첫 실행 확인을 거쳤는지 따져 볼 수 있습니다. Gatekeeper가 이 속성을 보고 첫 실행 때 무엇을 확인하는지는 [격리 속성과 다운로드 기록 (Quarantine)](index.md) 허브에 정리했습니다.

같은 다운로드는 사용자별 DB에도 한 행으로 남고, 속성의 마지막 필드인 UUID가 그 행을 찾는 열쇠입니다 [1]. 받은 파일 URL·원래 페이지 URL·격리 이유는 속성이 아니라 DB 쪽에 있어서 [격리 이벤트 DB (QuarantineEventsV2)](quarantine-events-db.md)에서 다룹니다.

## 위치와 버전별 차이

파일마다 붙는 확장 속성이라서 따로 정해진 파일 경로가 없고, 속성 이름 `com.apple.quarantine` 으로 찾습니다. 확장 속성이 볼륨에 어떻게 저장되는지는 [APFS 구조 (APFS)](../../../01-foundations/disk-volume/apfs/index.md)에서 다룹니다.

| macOS 버전 | 달라진 점 | 출처 |
|---|---|---|
| OS X El Capitan·macOS Sierra·High Sierra | 아래 네 필드 형식을 씀 | [1] |
| macOS 13 Ventura | 격리를 통과한 앱에 `com.apple.provenance` 확장 속성이 새로 붙음 | [2] |
| macOS 13.2.1 무렵 | Ventura 초기에는 앱 안의 모든 폴더·파일에 `com.apple.provenance` 가 붙었지만 이 무렵에는 `.app` 폴더에만 붙음. SIP가 이 속성을 지키는지는 관찰한 사람마다 다르게 보고함 | [2] |

macOS 13 Ventura의 플래그 예(아래 `0081` → `00c1`)를 보면 Catalina 이후에도 네 필드 형식이 그대로입니다 [2]. macOS 10.15 Catalina부터 12 Monterey 사이에서는 형식이 다를 수 있습니다.

## 구조

값은 세미콜론(`;`)으로 나눈 필드 네 개로 된 UTF-8 문자열입니다 [1].

| 필드 | 내용 | 형식 |
|---|---|---|
| 1 | 플래그 | 16진수 4자리 |
| 2 | 격리 시각 | 16진수로 적은 유닉스 시각(1970-01-01 기준 초) |
| 3 | 받은 앱 이름 | 문자열, 예: `Safari.app` |
| 4 | 이벤트 UUID | 격리 이벤트 DB의 `LSQuarantineEventIdentifier` 와 같은 값 |

### 플래그 비트

플래그 비트의 뜻은 Apple 공개 문서에 없습니다. 아래 이름은 WebKit 소스에 들어 있는 Apple 비공개 격리 API 선언(QuarantineSPI.h)의 이름입니다 [3].

| 비트 | 이름 |
|---|---|
| `0x0001` | `QTN_FLAG_DOWNLOAD` |
| `0x0002` | `QTN_FLAG_SANDBOX` |
| `0x0004` | `QTN_FLAG_HARD` |
| `0x0040` | `QTN_FLAG_USER_APPROVED` |
| `0x0080` | 이 헤더에 없음. 흔한 값 `0083`·`0081` 에 들어 있지만 뜻을 밝힌 공개 자료가 없음 [1][2] |

플래그는 앱을 연 뒤에 바뀝니다. Ventura에서 AirDrop으로 받은 앱은 처음에 `0081` 이고, 열어서 확인을 통과하면 `00c1` 이 되면서 `com.apple.provenance` 가 붙습니다 [2]. 늘어난 `0x0040` 은 헤더 이름으로 보면 사용자 승인 비트입니다 [3]. Gatekeeper 확인을 통과해 실행된 뒤 비트 두 개가 더해진다는 설명도 있지만, 그 설명의 비트 값은 예시 값과 맞지 않습니다 [1].

### com.apple.provenance (macOS 13 Ventura부터)

macOS 13 Ventura부터 앱이 격리를 통과할 때 `com.apple.provenance` 확장 속성이 붙고, 값은 보통 11바이트 바이너리입니다 [2]. 값 안에 있는 8바이트 리틀엔디언 정수가 `/var/db/SystemPolicyConfiguration/ExecPolicy` 데이터베이스 `provenance_tracking` 표의 기본 키이고, 그 표에서 번들 식별자·코드 서명 해시(cdhash) 같은 앱 정보를 찾을 수 있다는 해석이 있습니다 [2]. 한 사람이 찾아낸 연결이라 실제 데이터로 한 번 맞춰 본 뒤에 씁니다. 11바이트 안에서 이 정수의 위치는 실제 데이터로 확인해야 합니다. ExecPolicy 데이터베이스 자체는 [실행 정책 평가 기록 (ExecPolicy·Gatekeeper)](../../execution/execpolicy-gatekeeper.md)에서 다룹니다.

## 증거로서 의미

**증명하는 것.** 속성이 붙어 있으면 그 파일이 격리 대상으로 이 Mac에 들어왔고, 3번 필드의 앱을 거쳐 2번 필드의 시각에 격리됐다는 기록이 있다는 뜻입니다 [1]. 4번 필드의 UUID로 DB 행을 찾으면 같은 이벤트의 받은 파일 URL과 격리 이유까지 이을 수 있습니다. 앱 번들의 플래그에 `0x0040` 이 더해져 있거나 `com.apple.provenance` 가 붙어 있으면 그 앱이 격리 확인을 통과한 적이 있다고 볼 수 있습니다(macOS 13 Ventura 기준) [2].

**증명하지 못하는 것.** 속성에는 사용자 계정도 출처 URL도 들어 있지 않아서, 누가 받았는지와 어디서 받았는지는 DB나 다른 기록으로 확인해야 합니다. 속성에 들어 있는 시각은 격리 시각 하나뿐이라서 앱을 연 시각이나 실행한 횟수는 알 수 없습니다. 파일 하나에 속성이 있다고 해서 그 파일을 따로 받았다고 보지는 않고, 압축 파일에서 풀려 나오면서 속성이 이어진 파일일 수 있다는 점을 함께 따집니다 [1]. 반대로 속성이 없다고 해서 인터넷에서 받지 않았다고 단정하지도 않습니다(아래 함정 참고).

보고서에는 "이 파일에 `Safari.app` 이름과 이 시각이 적힌 격리 속성이 있고, 같은 UUID의 격리 이벤트 기록이 이 사용자의 DB에 있다" 처럼 기록으로 확인되는 만큼만 씁니다.

## 시각 해석

2번 필드는 16진수로 적은 유닉스 시각이라 UTC 기준 초이고, 현지 시각은 [시간대와 시계 설정 (Time Zone·NTP)](../../system-account/time-zone.md)을 보고 따로 바꿉니다. 격리 이벤트 DB의 시각은 2001-01-01 기준 맥 절대 시각이라서 기준이 다르고([격리 이벤트 DB](quarantine-events-db.md) 참고), 두 값을 그대로 비교하면 틀립니다. 시각 형식끼리 바꾸는 법은 [맥의 시각 값 (Mac Absolute Time·Unix·HFS)](../../../01-foundations/value-decoding/mac-time-values.md)에 있습니다.

아래 값은 명세로 만든 예시입니다. 2번 필드가 `65920080` 이면 10진수로 1704067200이고, 2024-01-01 00:00:00 UTC입니다. 같은 순간을 맥 절대 시각으로 적으면 725760000입니다.

플래그가 바뀔 때 2번 필드 시각도 함께 바뀌는지는 공개 자료가 없습니다. 2번 필드는 격리 시각으로만 읽고, 첫 실행 시각으로 읽지 않습니다.

## 함정과 한계

- **`0x0080` 비트.** 흔한 값 `0081`·`0083` 에 들어 있지만 뜻을 밝힌 공개 자료가 없습니다. 이 비트로 결론을 내리지 않습니다.
- **비공개 API 이름.** 플래그 이름은 Apple 비공개 헤더에서 왔고 [3], Apple이 공개 문서로 보장한 뜻이 아닙니다.
- **속성이 없는 경우.** 로컬에서 빌드해 ad hoc 서명한 앱은 격리되지 않습니다(허브 참고). curl 같은 명령줄 도구로 받은 파일에 속성이 붙는지, 확장 속성을 지원하지 않는 FAT·exFAT 볼륨으로 복사했다 돌아온 파일이 어떻게 되는지는 실제 데이터로 확인해야 합니다. 속성이 없으면 DB 쪽에서 파일 이름과 시각으로 행을 찾아봅니다.
- **지운 흔적.** 사용자가 속성을 지웠을 때 어디에 어떤 흔적이 남는지는 공개 자료가 없습니다. 속성은 없는데 DB에는 받은 기록이 있다면 그 차이를 기록한 그대로 보고합니다.
- **provenance 이상값.** macOS 오류로 보이는 이유로 `com.apple.provenance` 가 0으로 채운 4,096바이트가 된 사례가 있습니다 [2]. 이런 값에서는 기본 키를 읽을 수 없습니다.

## 직접 분석해 보기

### 헥스로 한 번

아래는 명세로 만든 예시 값의 앞부분이고, 실제 기기에서 나온 값이 아닙니다. 값이 UTF-8 문자열이라서 헥스와 글자가 한 글자씩 짝이 맞습니다.

```
30 30 38 31 3B 36 35 39 32 30 30 38 30 3B 53 61   0081;65920080;Sa
66 61 72 69 2E 61 70 70 3B ...                    fari.app;<UUID>
```

1. `3B`(`;`)를 기준으로 네 필드로 나눕니다.
2. 1번 필드 `0081` 은 `0x0080`(뜻이 공개되지 않음)과 `0x0001`(`QTN_FLAG_DOWNLOAD`)을 더한 값이고, `0x0040` 이 없으니 아직 사용자 승인 비트가 서지 않은 상태입니다.
3. 2번 필드 `65920080` 을 10진수로 바꾸면 1704067200이고, 유닉스 시각으로 2024-01-01 00:00:00 UTC입니다.
4. 3번 필드 `Safari.app` 이 받은 앱 이름입니다.
5. 4번 필드 UUID로 격리 이벤트 DB에서 `LSQuarantineEventIdentifier` 가 같은 행을 찾습니다.

### 공개 도구로 한 번

값이 글자라서 확장 속성을 글자로 보여 주는 도구라면 어느 것이든 그대로 읽을 수 있고, 풀이 순서는 위와 같습니다. DB 쪽은 mac_apt 격리 플러그인으로 읽는 방법을 [격리 이벤트 DB (QuarantineEventsV2)](quarantine-events-db.md)에 적었습니다. `com.apple.provenance` 는 바이너리라서 헥스로 보고, 기본 키로 ExecPolicy의 `provenance_tracking` 행을 찾습니다.

## 교차 검증

| 함께 볼 아티팩트 | 맞춰 볼 것 |
|---|---|
| [격리 이벤트 DB (QuarantineEventsV2)](quarantine-events-db.md) | 4번 필드 UUID로 행을 찾아 받은 파일 URL·원래 페이지 URL·격리 이유를 잇습니다 |
| [다운로드 출처 속성 (kMDItemWhereFroms)](../where-froms.md) | 같은 파일에 붙은 다른 확장 속성으로 출처를 한 번 더 확인합니다 |
| [실행 정책 평가 기록 (ExecPolicy·Gatekeeper)](../../execution/execpolicy-gatekeeper.md) | provenance의 기본 키로 번들 식별자·cdhash를 찾습니다 |
| [사파리 (Safari)](../../browsers/safari/index.md), [크롬·엣지·웨일 (Chromium 계열)](../../browsers/chromium/index.md) | 3번 필드 앱의 다운로드 기록과 시각을 맞춰 봅니다 |
| [에어드롭 (AirDrop)](../../external-devices/airdrop.md) | AirDrop으로 받은 앱이면 받은 기록과 맞춰 봅니다 |
| [서명·공증·무결성 보호 (Code Signing·Notarization·SIP)](../../../01-foundations/protection/codesign-notarization-sip.md) | 격리된 앱의 서명·공증 상태를 확인합니다 |

## 실습

공개 시험 자료(NIST CFReDS 등)의 macOS 이미지로 풀어 봅니다.

1. 사용자가 받은 파일 하나를 골라 격리 속성의 네 필드를 풀고, 2번 필드 시각을 UTC와 현지 시각으로 적어 보세요.
2. 같은 UUID의 행을 격리 이벤트 DB에서 찾고, 두 기록의 시각을 기준을 맞춘 뒤 비교해 보세요.
3. 설치된 앱 번들의 플래그에 `0x0040` 이 있는지, macOS 13 이후 이미지라면 `com.apple.provenance` 가 있는지 확인해 보세요.
4. 압축 파일과 거기서 풀려 나온 파일의 격리 속성을 나란히 놓고 어떤 필드가 같은지 비교해 보세요.

## 참고 문헌

1. Howard Oakley, "xattr: com.apple.quarantine, the quarantine flag" (The Eclectic Light Company, 2017-12-11) — https://eclecticlight.co/2017/12/11/xattr-com-apple-quarantine-the-quarantine-flag/
2. Howard Oakley, "Ventura has changed app quarantine with a new xattr" (The Eclectic Light Company, 2023-03-13) — https://eclecticlight.co/2023/03/13/ventura-has-changed-app-quarantine-with-a-new-xattr/
3. WebKit 소스 QuarantineSPI.h (Apple 비공개 격리 API 선언) — https://raw.githubusercontent.com/WebKit/WebKit/main/Source/WebCore/PAL/pal/spi/mac/QuarantineSPI.h
