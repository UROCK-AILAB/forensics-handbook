---
title: "격리 이벤트 DB"
parent: "격리 속성과 다운로드 기록"
grand_parent: "아티팩트 · 파일 시스템"
nav_order: 990
---

# 격리 이벤트 DB (QuarantineEventsV2)

격리 이벤트 DB (QuarantineEventsV2)는 사용자마다 하나씩 있는 SQLite 파일이고, 격리 이벤트마다 받은 앱·받은 파일 URL·원래 페이지 URL·격리 이유·시각을 한 행씩 남겨서 확장 속성의 UUID로 파일과 다운로드 출처를 이을 수 있습니다.

## 무엇을 기록하나 · 왜 생기나

파일이 격리될 때 파일 쪽에는 [격리 확장 속성 (com.apple.quarantine)](quarantine-xattr.md)이 붙고, 같은 이벤트가 이 DB의 `LSQuarantineEvent` 표에 한 행으로 남습니다 [1][2]. 확장 속성에는 앱 이름과 시각까지만 들어 있고, 파일을 어느 URL에서 받았는지와 어떤 이유로 격리했는지는 이 DB에서 확인합니다.

파일 이름에 Launch Services가 들어 있고, 칸 이름도 Launch Services 공개 API의 격리 속성 키와 짝이 맞습니다 [3]. 칸의 뜻은 이 공개 API 설명을 기준으로 읽습니다.

## 위치와 버전별 차이

```
~/Library/Preferences/com.apple.LaunchServices.QuarantineEventsV2
```

사용자 홈 폴더마다 하나씩 있는 확장자 없는 SQLite 파일이고, 기록은 `LSQuarantineEvent` 표에 있습니다 [1][2]. 계정마다 따로 있으니 이미지에 있는 사용자 홈 폴더를 모두 확인합니다.

옛 이름 `QuarantineEvents`(V1) 파일이 언제까지 쓰였는지, macOS 10.15 Catalina 이후 버전마다 칸이 달라지는지는 확인하지 못했습니다. 아래 칸 목록은 mac_apt 격리 플러그인이 읽는 칸 기준입니다 [2].

## 구조

`LSQuarantineEvent` 표의 칸입니다. "공개 API 키" 는 공개 문서에서 짝이 맞는다고 확인한 것만 적었습니다 [3]. "mac_apt 출력" 은 공개 도구 결과를 읽을 때 쓰는 이름이고, mac_apt는 여기에 `User`·`Source` 칸을 더해 출력합니다 [2].

| 칸 | 공개 API 키 | 뜻 | mac_apt 출력 |
|---|---|---|---|
| `LSQuarantineEventIdentifier` | | 이벤트 UUID, 확장 속성 4칸과 같은 값 [1] | EventID |
| `LSQuarantineTimeStamp` | | 격리 시각, 맥 절대 시각 [2] | TimeStamp |
| `LSQuarantineAgentBundleIdentifier` | `kLSQuarantineAgentBundleIdentifierKey` | 파일을 받은 앱의 번들 ID | AgentBundleID |
| `LSQuarantineAgentName` | `kLSQuarantineAgentNameKey` | 파일을 받은 앱 이름 | AgentName |
| `LSQuarantineDataURLString` | `kLSQuarantineDataURLKey` | 실제로 받은 파일의 URL | DataUrl |
| `LSQuarantineSenderName` | | 확인 못 함(아래 참고) | SenderName |
| `LSQuarantineSenderAddress` | | 확인 못 함(아래 참고) | SenderAddress |
| `LSQuarantineTypeNumber` | `kLSQuarantineTypeKey` | 격리 이유 | TypeNumber |
| `LSQuarantineOriginTitle` | | 확인 못 함 | OriginTitle |
| `LSQuarantineOriginURLString` | `kLSQuarantineOriginURLKey` | 파일을 올려 둔 원래 페이지의 URL | OriginUrl |
| `LSQuarantineOriginAlias` | | 확인 못 함 | OriginAlias |

`LSQuarantineDataURLString` 과 `LSQuarantineOriginURLString` 은 다른 값입니다. 앞쪽은 실제로 받은 파일의 주소이고, 뒤쪽은 그 파일을 올려 둔 원래 페이지의 주소입니다 [3].

### 격리 이유

공개 API에는 격리 이유를 나타내는 상수가 아래처럼 정해져 있습니다 [3].

| 상수 | 뜻 |
|---|---|
| `kLSQuarantineTypeWebDownload` | 웹사이트에서 받은 파일 |
| `kLSQuarantineTypeOtherDownload` | 그 밖의 방법으로 받은 파일 |
| `kLSQuarantineTypeEmailAttachment` | 메일 첨부 |
| `kLSQuarantineTypeInstantMessageAttachment` | 메시지 첨부 |
| `kLSQuarantineTypeCalendarEventAttachment` | 캘린더 이벤트 첨부 |
| `kLSQuarantineTypeOtherAttachment` | 그 밖의 첨부 |

DB의 `LSQuarantineTypeNumber` 에는 숫자가 들어가는데, 숫자(0, 1, 2 …)와 위 상수가 어떻게 짝지어지는지는 확인하지 못했습니다. 숫자만 보고 격리 이유를 적지 않고, 같은 검체 안에서 URL·받은 앱과 함께 보며 판단합니다.

`LSQuarantineSenderName`·`LSQuarantineSenderAddress` 는 이름으로 보아 메일·메시지 첨부를 보낸 사람을 적는 칸으로 보이지만, 어떤 조건에서 채워지는지는 확인하지 못했습니다.

## 증거로서 의미

**증명하는 것.** 이 사용자 계정의 DB에 이 시각, 이 앱이 이 URL의 파일을 받아 격리한 기록이 있다는 점입니다. `LSQuarantineEventIdentifier` 가 파일의 격리 속성 UUID와 같으면 그 파일과 이 다운로드 기록이 같은 이벤트라고 이을 수 있습니다 [1][2]. `LSQuarantineOriginURLString` 이 채워져 있으면 그 파일을 올려 둔 원래 페이지도 알 수 있습니다 [3].

**증명하지 못하는 것.** 받은 파일이 지금도 디스크에 있는지, 사용자가 그 파일을 열거나 실행했는지는 이 DB로 알 수 없습니다. DB가 그 사용자 홈 폴더에 있다는 점은 계정을 알려 주지만, 그 시각에 키보드 앞에 있던 사람까지 알려 주지는 않습니다. 파일을 지웠을 때 행이 남는지, 브라우저 기록을 지울 때 이 DB도 함께 지워지는지는 확인하지 못해서, 행이 없다는 점만으로 받은 적이 없다고 보지 않습니다.

보고서에는 "이 사용자의 격리 이벤트 DB에 이 시각(UTC)에 이 앱이 이 URL의 파일을 받은 기록이 있고, 이 파일의 격리 속성과 UUID가 같다" 처럼 씁니다.

## 시각 해석

`LSQuarantineTimeStamp` 는 2001-01-01 00:00:00 UTC를 기준으로 센 초, 곧 맥 절대 시각이고, mac_apt는 이 값을 ReadMacAbsoluteTime으로 바꿔 보여 줍니다 [2]. 파일의 격리 속성 시각은 1970-01-01 기준 유닉스 시각이라서 [1] 두 값을 날것 그대로 견주면 안 되고, 한쪽 기준으로 바꾼 뒤 비교합니다. 두 기준의 차이와 바꾸는 법은 [맥의 시각 값 (Mac Absolute Time·Unix·HFS)](../../../01-foundations/value-decoding/mac-time-values.md)에 있습니다.

명세로 만든 예시로 보면, 맥 절대 시각 725760000은 2024-01-01 00:00:00 UTC이고, 격리 속성 쪽에서 같은 순간은 [격리 확장 속성](quarantine-xattr.md)의 풀이 예와 같습니다. 두 값 모두 UTC 기준이라 현지 시각은 [시간대와 시계 설정 (Time Zone·NTP)](../../system-account/time-zone.md)을 보고 따로 바꿉니다.

## 함정과 한계

- **격리 이유 숫자.** `LSQuarantineTypeNumber` 와 공개 상수의 대응표를 확인하지 못했습니다. 도구가 숫자를 글자로 바꿔 보여 주면 도구가 어떤 표를 썼는지 확인합니다.
- **사용자마다 따로.** DB가 홈 폴더마다 있어서 한 계정만 보면 다른 계정에서 받은 기록을 놓칩니다.
- **지운 기록.** 행 삭제와 파일 삭제가 어떻게 이어지는지 확인하지 못했습니다. 지운 행을 찾으려면 SQLite 파일의 빈 공간을 살펴야 하고, 그 방법은 [SQLite 데이터베이스 (SQLite)](../../../01-foundations/data-formats/sqlite/index.md)와 [삭제 데이터 복구 (Data Recovery)](../../../03-techniques/analysis/data-recovery/index.md)에서 다룹니다.
- **UUID 없이 찾기.** 파일의 격리 속성이 없어졌다면 `LSQuarantineDataURLString` 의 파일 이름과 시각으로 행을 찾을 수 있지만, 같은 이름의 파일을 여러 번 받았을 수 있어서 한 행으로 단정하지 않습니다.

## 직접 분석해 보기

### 헥스로 한 번

확장자가 없어도 SQLite 파일이라서 SQLite 헤더와 페이지 구조를 그대로 따라가면 되고, 레코드를 헥스로 읽는 방법은 [SQLite 데이터베이스 (SQLite)](../../../01-foundations/data-formats/sqlite/index.md)에서 다룹니다. 원본을 건드리지 않도록 사본을 열어 봅니다.

### SQL로 한 번

SQLite를 여는 도구라면 어느 것이든 아래처럼 읽을 수 있습니다. `978307200` 은 1970-01-01과 2001-01-01 사이의 초이고, 맥 절대 시각에 더하면 유닉스 시각이 됩니다.

```sql
SELECT LSQuarantineEventIdentifier,
       datetime(LSQuarantineTimeStamp + 978307200, 'unixepoch') AS time_utc,
       LSQuarantineAgentBundleIdentifier,
       LSQuarantineAgentName,
       LSQuarantineDataURLString,
       LSQuarantineOriginURLString,
       LSQuarantineTypeNumber
FROM LSQuarantineEvent
ORDER BY LSQuarantineTimeStamp;
```

파일 하나의 출처를 찾을 때는 그 파일 격리 속성의 4칸 UUID를 `WHERE LSQuarantineEventIdentifier = '<UUID>'` 로 넣습니다.

### 공개 도구로 한 번

mac_apt의 격리 플러그인(quarantine)은 이 DB를 읽고, 시각을 바꿔서 위 구조 표의 "mac_apt 출력" 이름으로 내보냅니다 [2]. 도구 결과와 SQL 결과의 시각이 같은지 한 번 맞춰 보면 시각 변환이 맞는지 확인할 수 있습니다.

## 교차 검증

| 함께 볼 아티팩트 | 맞춰 볼 것 |
|---|---|
| [격리 확장 속성 (com.apple.quarantine)](quarantine-xattr.md) | UUID로 행과 파일을 잇고, 기준을 맞춘 시각을 비교합니다 |
| [다운로드 출처 속성 (kMDItemWhereFroms)](../where-froms.md) | 파일에 남은 출처와 `LSQuarantineDataURLString`·`LSQuarantineOriginURLString` 을 맞춰 봅니다 |
| [사파리 (Safari)](../../browsers/safari/index.md), [크롬·엣지·웨일 (Chromium 계열)](../../browsers/chromium/index.md), [파이어폭스 (Firefox)](../../browsers/firefox.md) | 받은 앱의 방문·다운로드 기록에서 같은 URL과 시각을 찾습니다 |
| [애플 메일 (Apple Mail)](../../mail/apple-mail/index.md), [메시지 (iMessage·SMS)](../../messengers/imessage/index.md) | 받은 앱이 메일·메시지 앱이면 첨부가 들어 있던 메시지를 찾습니다 |
| [타임라인 작성 (Timeline)](../../../03-techniques/analysis/timeline/index.md) | 다운로드 시각을 실행·파일 사용 기록과 한 시간축에 놓습니다 |

## 실습

공개 검체(NIST CFReDS 등)의 macOS 이미지로 풀어 봅니다.

1. 이미지에 있는 사용자마다 이 DB가 있는지 확인하고, 사용자별 행 수를 세어 보세요.
2. 위 SQL로 가장 최근 다운로드 다섯 건을 뽑고, 받은 앱·받은 파일 URL·원래 페이지 URL을 적어 보세요.
3. 한 행의 UUID를 골라 같은 UUID의 격리 속성이 붙은 파일이 아직 디스크에 있는지 찾아보세요.
4. mac_apt 결과의 시각과 SQL로 바꾼 시각이 같은지 비교해 보세요.

## 참고 문헌

1. Howard Oakley, "xattr: com.apple.quarantine, the quarantine flag" (The Eclectic Light Company, 2017-12-11) — https://eclecticlight.co/2017/12/11/xattr-com-apple-quarantine-the-quarantine-flag/
2. mac_apt 격리 플러그인 소스 quarantine.py (Yogesh Khatri) — https://raw.githubusercontent.com/ydkhatri/mac_apt/master/plugins/quarantine.py
3. Apple Developer Documentation, Launch Services (격리 속성 키·격리 이유 상수) — https://developer.apple.com/tutorials/data/documentation/coreservices/launch_services.json
