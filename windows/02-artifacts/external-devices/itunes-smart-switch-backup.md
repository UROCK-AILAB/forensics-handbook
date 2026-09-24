# 스마트폰 백업 파일 (iTunes·Smart Switch Backup)

## 한 줄 요약

iPhone·iPad 를 iTunes 나 Apple 기기 앱으로 백업하면 PC 의 사용자 프로필 아래에 백업 폴더가 생깁니다. 폴더 안 파일은 원래 이름 대신 40자 SHA-1 값을 이름으로 씁니다. 원래 경로는 `Manifest.db` 에서 찾습니다. Samsung Smart Switch 의 PC 백업은 이 글에서 확인한 자료가 없어 확인할 점만 적습니다.

## 무엇을 기록하나 · 왜 생기나

iPhone·iPad·iPod touch 는 컴퓨터에 백업을 만들 수 있고, Apple 은 백업을 찾고 관리하는 방법을 지원 문서(108809)로 안내합니다. 백업 폴더에는 기기 정보, 앱 목록, 백업 상태를 적은 파일이 있고, 메시지(`sms.db`)와 연락처(`AddressBook.sqlitedb`) 같은 SQLite 파일을 비롯한 기기 안 파일의 사본도 함께 들어갑니다. 그래서 스마트폰을 따로 압수하지 못해도 PC 에서 백업 시점의 메시지·연락처를 볼 수 있습니다.

Samsung 스마트폰은 PC 판 Smart Switch 로 백업할 수 있지만, 이 글에서는 그 형식을 확인하지 못했습니다.

## 위치와 버전별 차이

### iTunes·Apple 기기 앱

| 설치 방식 | 백업을 찾을 위치 | 근거 |
|---|---|---|
| Apple 기기 앱 (Apple Devices), Microsoft Store 판 iTunes | `%USERPROFILE%` 아래 | Apple |
| Apple 사이트에서 받은 iTunes | `%AppData%` 아래 | Apple |
| Mac (참고) | `~/Library/Application Support/MobileSync/Backup/` | Apple, Infante |

Windows 쪽은 그 아래 폴더 이름까지 확인하지 못했으므로, 두 위치 아래에서 Mac 과 같은 이름인 `MobileSync` 폴더를 찾아봅니다. 설치 방식이 바뀌었을 수 있으니 두 위치를 모두 봅니다. 기기마다 백업 폴더가 하나씩 생기고 폴더 이름이 기기 식별자(UDID)라는 설명이 있지만, 이 글에서는 확인하지 못했습니다.

### 백업 형식 판

| iOS | 백업 형식 | 파일 목록 | 파일 배치 |
|---|---|---|---|
| 9 | 2.4 | `Manifest.mbdb` (바이너리) | 한 폴더에 모두 둡니다. |
| 10·11 | 3.2 | `Manifest.db` (SQLite) | 파일 이름 앞 두 글자로 하위 폴더를 나눕니다. |

형식 설명은 2017년에 쓰고 2019년에 고친 글(Infante)에서 가져왔는데, 이 글은 iOS 10·11 까지만 다룹니다. iOS 12 이후에도 형식 3.2 와 같은 배치인지는 확인하지 못했습니다.

### Smart Switch

- 이 글에서는 Smart Switch PC 백업을 설명한 자료를 하나도 확인하지 못했습니다.
- 관찰한 PC 한 대(Windows 11 Home 25H2)에서 아래 네 곳을 찾아봤고, 모두 없었습니다. Smart Switch 설치 흔적도 없었습니다.
  - `%USERPROFILE%\Documents\Samsung`
  - `%APPDATA%\Samsung`
  - `%LOCALAPPDATA%\Samsung`
  - `C:\ProgramData\Samsung`
- 이 네 곳이 실제 백업 위치라는 뜻은 아닙니다. 검체에서 먼저 찾아볼 곳입니다.

## 구조

### 백업 폴더 맨 위 파일 (iTunes)

| 파일 | 형식 | 내용 |
|---|---|---|
| `Info.plist` | 평문 XML plist | 기기 정보, 앱 목록, 일련번호 등 |
| `Manifest.plist` | 바이너리 plist | 암호화 여부, 앱 목록, 키백 (KeyBag) |
| `Status.plist` | 바이너리 plist | 백업 버전, 상태, 완료 날짜 |
| `Manifest.db` | SQLite | 파일 목록. 형식 3.2(근거 글 기준 iOS 10·11) |
| `Manifest.mbdb` | 바이너리 | 파일 목록. 형식 2.4(iOS 9). `Manifest.db` 의 앞 형식 |

- `Info.plist` 안의 칸 이름(기기 이름, 마지막 백업 날짜, 제품 종류 등)은 이 글에서 확인하지 못했습니다. 파일을 열어 칸 이름을 직접 봅니다.

### 파일 이름 규칙

백업된 파일은 원래 이름 대신 40자 SHA-1 값을 이름으로 쓰고, 이름은 `SHA-1(도메인 + "-" + 상대 경로)` 입니다.

- `HomeDomain` 의 `Library/SMS/sms.db` 는 `3d0d7e5fb2ce288813306e4d4636395e047a3d28` 입니다(Infante). 같은 규칙으로 직접 계산해 같은 값을 얻었습니다.
- `HomeDomain` 의 `Library/AddressBook/AddressBook.sqlitedb` 는 같은 규칙으로 계산하면 `31bb7ba8914766d4ba40d6dfb6113c8b614be442` 입니다.

형식 3.2 에서는 이름 앞 두 글자가 하위 폴더 이름이라서, 규칙대로라면 `sms.db` 는 `3d\3d0d7e5f…` 에 있습니다.

### Manifest.db

| 표 | 칸 | 내용 |
|---|---|---|
| `Files` | `fileID` TEXT PRIMARY KEY | 백업 폴더의 SHA-1 파일 이름과 맞춰 봅니다. |
| | `domain` TEXT | 도메인 |
| | `relativePath` TEXT | 도메인 안의 상대 경로 |
| | `flags` INTEGER | 문서로 공개되지 않았습니다. |
| | `file` BLOB | 바이너리 plist |
| `Properties` | `key` TEXT PRIMARY KEY, `value` BLOB | |

- 도메인 예: `HomeDomain`, `CameraRollDomain`, `AppDomain-*`, `MediaDomain`.
- 경로 예: `HomeDomain` 의 `Library/SMS/sms.db` 는 메시지, `Library/AddressBook/AddressBook.sqlitedb` 는 연락처입니다.
- `flags` 값의 뜻(파일·폴더·링크 구분)과 `file` BLOB 안의 칸 이름(크기, 수정 시각 등)은 확인하지 못했습니다.
- SQLite 파일을 읽는 법은 [SQLite 데이터베이스](../../01-foundations/database-log-formats/sqlite/index.md)를 봅니다.

### 암호화

- 백업이 암호화됐는지는 `Manifest.plist` 에 적힙니다. 칸 이름은 이 글에서 확인하지 못했습니다.
- 키를 유도하는 방법, 암호화 백업에만 들어가는 항목, `Manifest.db` 자체가 암호화되는 iOS 판도 확인하지 못했습니다.
- 암호화 백업을 다루는 일반 절차는 [암호화 증거 다루기](../../03-techniques/analysis/encrypted-evidence/index.md)를 봅니다.

### Smart Switch 백업에서 확인할 점

이 글에서 확인하지 못한 것들입니다. 검체나 시험 PC 에서 직접 확인한 뒤에 씁니다.

1. PC 판의 기본 백업 폴더, 그리고 설정에서 폴더를 바꿀 수 있는지
2. 백업 폴더 안 구조(항목별 폴더·파일, 확장자)와 기기 모델·백업 날짜를 적은 정보 파일
3. 항목별 암호화 여부와 복호에 필요한 값
4. 백업 기록을 남기는 설정 파일이나 레지스트리

## 증거로서 의미

### 증명하는 것

- 백업 폴더가 있으면 그 기기 데이터의 사본이 이 PC 에 있습니다.
- `Status.plist` 의 완료 날짜로 백업을 마친 때를 봅니다.
- `Info.plist` 의 기기 정보와 일련번호로 어느 기기의 백업인지 정합니다.
- `Manifest.db` 로 백업에 들어간 파일의 도메인과 경로를 모두 봅니다.
- 백업 안 메시지·연락처 DB 로 백업 시점의 대화와 연락처를 봅니다.

### 증명하지 못하는 것

- 이 PC 에 기기를 연결해 백업했다고 흔히 해석합니다. 이 글에서는 이 해석을 자료로 확인하지 못했습니다. 백업 폴더는 다른 PC 에서 복사해 올 수도 있습니다. 연결 흔적과 맞춰 봅니다.
- 백업 폴더가 있는 사용자 프로필은 알 수 있습니다. 그 계정으로 누가 백업했는지는 따로 정합니다([그 시각에 PC 를 쓴 사람이 누구인가](../../04-scenarios/activity/user-attribution.md)).
- 백업 뒤 기기에서 일어난 일은 알 수 없습니다.
- 백업에 없는 앱·파일이 기기에 없었다고 단정할 수 없습니다. 어떤 항목이 백업에서 빠지는지는 이 글에서 확인하지 못했습니다.

### 보고서 문장 예

- 쓰지 않을 문장: "사용자는 2026-05-01 에 아이폰을 PC 에 연결해 메시지를 옮겼다."
- 쓸 문장: "사용자 ○○ 의 프로필 아래에 iOS 기기 백업 폴더가 있다. `Status.plist` 의 완료 날짜는 ○○ 이고, `Info.plist` 의 일련번호는 ○○ 이다. 백업 안 `sms.db` 에 메시지 ○건이 있다. 이 기록은 해당 기기의 백업 사본이 이 PC 에 있음을 보여 준다. 백업을 이 PC 에서 만들었는지는 연결 흔적으로 따로 확인해야 한다."

## 시각 해석

| 시각 | 위치 | 기준 |
|---|---|---|
| 백업 완료 날짜 | `Status.plist` | UTC 인지 현지 시각인지 확인하지 못했습니다. |
| 파일별 시각 | `Manifest.db` `Files` 표의 `file` BLOB | 칸 이름과 기준을 확인하지 못했습니다. |
| 메시지·연락처 안의 시각 | `sms.db` 등 백업 안 DB | DB 마다 형식이 다릅니다. [시각 값 형식](../../01-foundations/value-decoding/filetime-unix-webkit-dos-ole.md)을 봅니다. |
| 백업 폴더·파일의 파일시스템 시각 | NTFS | UTC. [마스터 파일 테이블](../filesystem/mft.md)에서 다룹니다. |

백업 완료 날짜와 폴더의 파일시스템 시각을 나란히 적어 두고, 두 시각이 크게 떨어지면 폴더를 옮기거나 복사했을 가능성을 봅니다.

## 함정과 한계

1. **한 곳만 찾는 실수.** 설치 방식에 따라 `%USERPROFILE%` 아래와 `%AppData%` 아래로 위치가 나뉩니다. 사용자 프로필마다 두 곳을 모두 봅니다.
2. **SHA-1 이름에서 원래 경로를 거꾸로 구하려는 실수.** SHA-1 은 거꾸로 풀 수 없습니다. `Manifest.db` 로 경로를 찾거나, 알고 싶은 도메인과 경로로 SHA-1 을 계산해 파일을 찾습니다.
3. **입력 문자열이 한 글자만 달라도 값이 달라집니다.** 도메인과 경로 사이의 `-`, 경로 구분 `/`, 대소문자를 규칙 그대로 씁니다.
4. **형식 판.** iOS 9 백업은 `Manifest.mbdb` 를 쓰고 하위 폴더가 없습니다. `Manifest.db` 가 없다고 파일 목록이 없는 것이 아닙니다.
5. **오래된 근거.** 구조 설명의 근거 글은 2019년에 마지막으로 고쳤습니다. 최신 iOS 백업은 검체에서 다시 확인합니다.
6. **암호화 백업.** 암호화 여부부터 확인합니다. 복호 조건은 이 글에서 확인하지 못했습니다.
7. **SQLite 의 숨은 데이터.** 백업 안 메시지·연락처 DB 에도 WAL 파일과 지운 레코드가 남을 수 있습니다. [SQLite 데이터베이스](../../01-foundations/database-log-formats/sqlite/index.md)를 봅니다.
8. **Smart Switch.** 확인한 자료가 없습니다. 다른 글이나 도구 설명을 그대로 옮기지 말고 검체에서 직접 확인합니다.

## 직접 분석해 보기

### 헥스로 한 번

1. 백업 폴더를 통째로 사본으로 확보합니다.
2. 맨 위에 `Manifest.db` 가 있는지 `Manifest.mbdb` 가 있는지로 형식 판을 정합니다.
3. `Info.plist` 는 평문 XML 이라 텍스트 편집기로 읽힙니다. 기기 정보와 일련번호를 적습니다.
4. `Manifest.plist` 에서 암호화 여부를 확인합니다.
5. 찾을 파일의 도메인과 경로로 SHA-1 을 계산해 백업 폴더에서 그 이름을 찾습니다.
6. `Manifest.db` 의 `Files` 표에서 같은 값을 찾아 도메인과 경로가 맞는지 확인합니다.

아래는 Infante 의 예와 이름 규칙으로 만든 예시입니다. 검체에서 나온 값이 아닙니다.

```
입력 문자열    HomeDomain-Library/SMS/sms.db
입력 바이트    48 6F 6D 65 44 6F 6D 61 69 6E 2D 4C 69 62 72 61
               72 79 2F 53 4D 53 2F 73 6D 73 2E 64 62
SHA-1          3d0d7e5fb2ce288813306e4d4636395e047a3d28
파일 위치      3d\3d0d7e5fb2ce288813306e4d4636395e047a3d28   (형식 3.2, 규칙대로 만든 경로)
```

- 공개 도구인 Python 으로는 `hashlib.sha1(b"HomeDomain-Library/SMS/sms.db").hexdigest()` 로 같은 값을 얻습니다.

### 공개 도구로 한 번

- sqlite3 명령줄 도구로 `Manifest.db` 사본을 엽니다. 아래 질의로 메시지 DB 의 백업 파일 이름을 찾습니다.

```sql
SELECT fileID, domain, relativePath
FROM Files
WHERE relativePath LIKE '%sms.db';
```

- 바이너리 plist(`Manifest.plist`, `Status.plist`, `file` BLOB)는 Python 표준 라이브러리 `plistlib` 로 읽을 수 있습니다.
- 도구가 보여 준 경로와 직접 계산한 SHA-1 이 맞는지 한 파일 이상 확인합니다.

## 교차 검증

| 아티팩트 | 맞춰 볼 것 | 링크 |
|---|---|---|
| USB 연결 흔적 | 백업 무렵 기기를 PC 에 연결했나 | [USB 저장장치 흔적](usb-storage-artifacts/index.md) |
| 외부 장치 연결 이벤트 | 연결 시각 | [외부 장치 연결 이벤트](../event-logs/partition-diagnostic-kernel-pnp-driverframeworks.md) |
| 설치 프로그램 | iTunes·Smart Switch 를 설치했나 | [설치 프로그램](../system-account/uninstall.md) |
| 스토어 앱 설치 목록 | Apple 기기 앱, Store 판 iTunes | [스토어 앱 설치 목록](../system-account/appx-staterepository.md) |
| 휴대폰과 연결 | 백업 말고 다른 경로로 휴대폰과 주고받은 흔적 | [휴대폰과 연결](../messengers/phone-link.md) |
| 아이클라우드 | PC 쪽 Apple 클라우드 흔적 | [아이클라우드](../cloud-notes/icloud-for-windows.md) |

- 백업 안 메시지·연락처로 대화 상대를 정리하는 흐름은 [누구와 연락을 주고받았나](../../04-scenarios/activity/communication-reconstruction.md)를 봅니다.
- 스마트폰으로 자료를 옮겼는지 묻는 흐름은 [자료를 밖으로 빼돌렸나](../../04-scenarios/exfiltration/data-exfiltration/index.md)에서 다룹니다.

## 실습

iOS 기기 백업이 들어 있는 공개 검체를 고르거나, 시험용 기기를 시험 PC 에 백업해 풀어 봅니다.

1. 사용자 프로필마다 백업 폴더를 찾습니다. 어느 설치 방식의 위치입니까?
2. `Manifest.db` 와 `Manifest.mbdb` 가운데 무엇이 있습니까? 백업 형식 판은 무엇입니까?
3. `HomeDomain-Library/SMS/sms.db` 의 SHA-1 을 직접 계산해 파일을 찾습니다. `Manifest.db` 의 결과와 같습니까?
4. `Status.plist` 의 완료 날짜, 폴더의 파일시스템 시각, USB 연결 흔적의 시각을 나란히 적습니다. 서로 맞습니까?
5. 암호화 백업입니까? 무엇을 근거로 판단했습니까?

## 참고 문헌

1. Apple 지원, "Locate and manage backups of your iPhone, iPad, and iPod touch" (108809). https://support.apple.com/en-us/HT204215
2. Rich Infante, "Reverse Engineering the iOS Backup" (2017-03-17 작성, 2019-12-17 갱신). https://www.richinfante.com/2017/3/16/reverse-engineering-the-ios-backup
