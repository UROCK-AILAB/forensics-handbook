---
title: "연락처"
parent: "아티팩트 · 클라우드·애플 앱"
nav_order: 1580
---

# 연락처 (Contacts)

맥의 연락처는 전화번호와 이메일 주소를 사람 이름과 잇는 자료입니다. 공개 수집 정의에 경로가 나온 것은 메일 최근 연락처 파일과 아이클라우드 계정 폴더 같은 주변 파일이고 [1], 연락처 본체 DB의 경로와 표 구조는 실제 데이터로 확인해야 합니다.

아래에서 "실제 데이터로 확인" 으로 표시한 경로와 표 이름은 분석 대상에서 찾아볼 후보로만 쓰고, 보고서에는 실제 데이터로 직접 확인한 뒤에 적습니다.

## 무엇을 기록하나 · 왜 생기나

연락처는 누구와 아는 사이였는지를 보여 주는 자료라서, 메시지·메일·통화 기록에 나온 전화번호나 이메일 주소를 사람 이름과 이을 때 씁니다. 연락처 본체와 별도로 메일 앱의 최근 연락처 파일이 있고, 이 파일의 ForensicArtifacts 이름은 `MacOSMailRecentContacts` 입니다 [1]. 두 파일은 다른 파일이라서 나눠서 봅니다.

연락처는 아이클라우드나 다른 계정과 동기화되기도 해서, 계정마다 따로 저장될 수 있습니다. 계정 정보는 [아이클라우드 계정 (iCloud Account)](icloud-account.md)에서 다룹니다.

## 위치와 버전별 차이

### 수집 정의에 있는 경로

| ForensicArtifacts 이름 | 경로 | 비고 |
|---|---|---|
| `MacOSMailRecentContacts` | `%%users.homedir%%/Library/Application Support/AddressBook/MailRecents-v4.abcdmr` | 메일 최근 연락처 [1] |
| `MacOSiCloudAccounts` | `%%users.homedir%%/Library/Application Support/iCloud/Accounts/*` | 아이클라우드 계정 폴더 [1] |
| `MacOSAddressBookImagesSQLiteDatabaseFile` | `AddressBookImages.sqlitedb` | 경로가 Xcode 시뮬레이터 아래뿐이라 맥 본체 연락처가 아닙니다 [1] |

`%%users.homedir%%` 는 ForensicArtifacts 정의에서 사용자 홈 폴더를 가리키는 표기입니다. 맥 본체 연락처 DB(`AddressBook-v22.abcddb`) 항목은 이 정의에 없어서 [1], 이 정의만 쓰는 도구로 자동 수집하면 연락처 본체가 빠질 수 있습니다. `AddressBookImages.sqlitedb` 는 이름만 보면 연락처 사진 같지만 시뮬레이터 자료라서 [1], 맥 사용자의 연락처 증거로 적지 않습니다.

### 실제 데이터로 확인할 것

| 항목 | 상태 |
|---|---|
| 로컬 연락처 DB `~/Library/Application Support/AddressBook/AddressBook-v22.abcddb` | 실제 데이터로 확인 |
| 계정별(아이클라우드·Exchange 등) DB `~/Library/Application Support/AddressBook/Sources/<UUID>/AddressBook-v22.abcddb` | 실제 데이터로 확인 |
| 표 이름 `ZABCDRECORD`(사람·그룹), `ZABCDPHONENUMBER`, `ZABCDEMAILADDRESS`, `ZABCDPOSTALADDRESS`, `ZABCDNOTE` 등 | 실제 데이터로 확인 |
| 열 이름 `ZFIRSTNAME`, `ZLASTNAME`, `ZORGANIZATION`, `ZCREATIONDATE`, `ZMODIFICATIONDATE`, `ZOWNER` | 실제 데이터로 확인 |
| 시각 열이 맥 절대 시각인지 | 실제 데이터로 확인 |
| macOS 버전별 경로와 파일 이름 차이 | 실제 데이터로 확인 |

## 구조

표 구조를 설명한 공개 자료는 없습니다. 분석 대상에서 `.abcddb` 나 `.abcdmr` 파일을 찾으면 먼저 첫 바이트로 SQLite 파일인지 확인하고, 맞다면 표 목록과 열 목록을 뽑아 위 "실제 데이터로 확인할 것" 표의 이름과 비교합니다. SQLite 머리말과 표 목록을 읽는 법은 [SQLite 데이터베이스 (SQLite)](../../01-foundations/data-formats/sqlite/index.md)에서 다룹니다.

## 증거로서 의미

**증명하는 것.** `MailRecents-v4.abcdmr` 가 사용자 홈에 있으면 그 사용자 계정에서 메일 앱의 최근 연락처 파일이 만들어졌다는 기록이 있다는 뜻입니다 [1]. `iCloud/Accounts/` 아래 파일은 그 사용자 계정에 아이클라우드 계정 정보가 있었다는 기록이고 [1], 연락처가 어느 계정과 동기화됐을지 따질 출발점이 됩니다. 연락처 본체 DB를 분석 대상에서 찾아 구조를 직접 확인했다면, 그 DB에 든 이름과 주소는 그 사용자의 연락처에 그 항목이 있었다는 기록으로 씁니다.

**증명하지 못하는 것.** 연락처에 이름이 있다는 사실만으로 두 사람이 실제로 연락했는지는 알 수 없고, 동기화로 다른 기기에서 넘어온 항목일 수 있어서 이 맥에서 입력했다고 쓰지 않습니다. 메일 최근 연락처에 주소가 있어도 그 주소를 사용자가 연락처에 저장했다는 뜻은 아닙니다. 본체 DB의 경로와 구조는 공개 자료가 없어서, 도구가 연락처 항목에 만든 시각·수정 시각을 붙여 보여 주면 그 열이 무엇인지 실제 데이터로 확인한 뒤에 씁니다.

보고서에는 "이 사용자의 연락처 DB에 이 이름으로 이 전화번호가 저장돼 있다" 처럼 쓰고, 연락을 주고받은 사실은 메시지·메일·통화 기록으로 따로 적습니다.

## 시각 해석

연락처 파일의 시각 열과 그 기준을 설명한 공개 자료는 없습니다. 실제 데이터에서 시각으로 보이는 열을 찾으면 값의 크기로 맥 절대 시각인지 유닉스 시각인지 구분하고, 구분하는 법은 [맥의 시각 값 (Mac Absolute Time·Unix·HFS)](../../01-foundations/value-decoding/mac-time-values.md)을 따릅니다. 구분한 기준은 보고서에 "(macOS 버전 기준)" 처럼 분석 대상의 macOS 버전을 붙여 적습니다.

## 함정과 한계

- **수집 정의에 없는 본체 DB.** ForensicArtifacts 정의에는 `AddressBook-v22.abcddb` 항목이 없어서 [1], 수집 목록에 `~/Library/Application Support/AddressBook/` 폴더 전체가 들어갔는지 확인합니다.
- **이름이 헷갈리는 시뮬레이터 파일.** `AddressBookImages.sqlitedb` 는 Xcode 시뮬레이터 아래 파일입니다 [1]. 개발 도구를 쓰는 맥에서 나와도 사용자 연락처로 적지 않습니다.
- **최근 연락처와 연락처 본체.** 메일 최근 연락처는 연락처 본체와 다른 파일입니다 [1]. 두 파일의 항목을 섞어 "저장한 연락처" 로 적지 않습니다.
- **권한 흔적.** 다른 앱이 연락처에 접근했는지는 [개인 정보 보호 권한 (TCC)](../credentials/tcc/index.md)에서 확인합니다.
- **에어드롭과 연락처.** 에어드롭의 "연락처만" 모드가 연락처를 어떻게 쓰는지는 [에어드롭 (AirDrop)](../external-devices/airdrop.md)에서 다룹니다.

## 직접 분석해 보기

### 헥스로 한 번

`MailRecents-v4.abcdmr` 사본을 헥스 편집기로 열어 첫 바이트가 SQLite 머리말인지 확인합니다. 머리말을 읽는 법은 [SQLite 데이터베이스 (SQLite)](../../01-foundations/data-formats/sqlite/index.md)에서 다루고, 이 파일의 형식은 실제 데이터로 확인해야 합니다.

### 공개 도구로 한 번

사본을 만든 뒤, 파일이 SQLite라면 `sqlite3` 으로 표 목록과 구조를 먼저 뽑습니다.

```
ls -la "Library/Application Support/AddressBook/"
ls -laR "Library/Application Support/AddressBook/Sources/"
sqlite3 "MailRecents-v4.abcdmr" ".tables"
sqlite3 "AddressBook-v22.abcddb" ".schema"
```

뽑은 표 이름을 위 "실제 데이터로 확인할 것" 표와 비교하고, 맞는 이름과 다른 이름을 분석 대상의 macOS 버전과 함께 적습니다.

## 교차 검증

| 함께 볼 아티팩트 | 맞춰 볼 것 |
|---|---|
| [아이클라우드 계정 (iCloud Account)](icloud-account.md) | 연락처가 묶였을 계정 |
| [메시지 (iMessage·SMS)](../messengers/imessage/index.md) | 대화 상대 전화번호·주소와 연락처 이름 |
| [페이스타임과 통화 기록 (FaceTime·CallHistory)](../messengers/facetime-callhistory.md) | 통화 상대와 연락처 이름 |
| [애플 메일 (Apple Mail)](../mail/apple-mail/index.md) | 메일 주소와 최근 연락처 |
| [미리 알림과 캘린더 (Reminders·Calendar)](reminders-calendar.md) | 일정 참석자 이메일 주소 |
| [에어드롭 (AirDrop)](../external-devices/airdrop.md) | "연락처만" 모드와 주고받은 상대 |
| [누구와 연락을 주고받았나 (Communication)](../../04-scenarios/activity/communication.md) | 연락처를 연락 관계 재구성에 쓰는 흐름 |

## 실습

공개 시험 자료(NIST CFReDS 등)의 macOS 이미지로 풀어 봅니다.

1. 사용자 홈의 `Library/Application Support/AddressBook/` 아래 파일과 폴더를 모두 적어 보세요.
2. `MailRecents-v4.abcdmr` 가 있으면 SQLite 파일인지 확인하고 표 목록을 적어 보세요.
3. `.abcddb` 파일을 찾으면 표 목록을 뽑아 이 페이지의 "실제 데이터로 확인할 것" 표와 맞는 이름, 다른 이름을 나눠 보세요.
4. 연락처에서 찾은 전화번호 하나로 메시지나 통화 기록에 같은 번호가 있는지 찾아보세요.

## 참고 문헌

1. ForensicArtifacts, macos.yaml — https://raw.githubusercontent.com/ForensicArtifacts/artifacts/main/artifacts/data/macos.yaml
