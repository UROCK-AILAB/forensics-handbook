---
title: "휴대폰과 연결"
parent: "아티팩트 · 메신저"
nav_order: 2150
---

# 휴대폰과 연결 (Phone Link)

## 한 줄 요약

휴대폰과 연결 (Phone Link) 은 연결한 휴대폰의 문자·연락처·통화 기록·알림·사진을 PC 로 동기화하는 Windows 앱입니다. 동기화한 자료는 사용자 프로필의 앱 패키지 폴더 안 SQLite DB 에 남습니다[1][2]. 앱의 옛 이름은 Your Phone 이고 패키지 이름은 `Microsoft.YourPhone_8wekyb3d8bbwe` 입니다[1]. 관찰한 PC(패키지 1.26072.255.0)에서도 이름이 같았습니다.

## 무엇을 기록하나 · 왜 생기나

사용자가 휴대폰을 이 앱에 연결하면 앱이 휴대폰 자료를 받아 PC 쪽 DB 에 저장하므로, 휴대폰을 PC 에 선으로 꽂지 않아도 휴대폰 문자·통화 기록이 PC 에 남을 수 있습니다.

공개 수집 목록 작성자가 정리한 DB 별 내용입니다[1].

| DB | 들어 있는 것 |
|---|---|
| `phone.db` | 휴대폰의 문자 전부. RCS 대화, 대화방, 파일 전송, MMS 포함 |
| `contacts.db` | 연락처 이름·번호·주소·이메일 |
| `calling.db` | 통화 기록 |
| `notifications.db` | 휴대폰의 현재(활성) 알림 |
| `photos.db` | 사진 파일 이름과 blob |
| `settings.db` | 휴대폰에 설치된 앱 목록 |
| `deviceData.db` | 휴대폰에 지금 표시 중인 배경화면 |

(표는 [1])

이 목록 작성자는 안드로이드 휴대폰으로만 시험했고 아이폰은 확인하지 않았다고 적었습니다[1]. 2019년 연구 환경에서 본 DB 구성과 사진 폴더는 [스마트폰으로 옮겼나 (MTP·Phone Link)](../../04-scenarios/exfiltration/data-exfiltration/mtp-phone-link.md) 에 정리돼 있습니다.

## 위치와 버전별 차이

### 위치 (공개 자료 기준)

2019년 이후 공개 자료에 나온 DB 위치입니다[1].

```
C:\Users\<사용자>\AppData\Local\Packages\Microsoft.YourPhone_8wekyb3d8bbwe\LocalCache\Indexed\<GUID>\System\Database\
```

공개 수집 목록은 `...\LocalCache\Indexed` 아래를 통째로 모읍니다[1]. 패키지 폴더의 일반 구조는 [UWP 앱 데이터 구조](../../01-foundations/app-mail-data/packages-settings-dat.md) 에서 다룹니다. 앱 이름이 Your Phone 에서 Phone Link 로 바뀐 시점은 확인하지 못했습니다.

### 관찰한 PC

이 절은 Windows 11, 휴대폰과 연결 패키지 1.26072.255.0 기준입니다.

패키지 폴더에 `LocalCache\Indexed` 가 없었지만, 이 PC 에서 휴대폰을 연결해 쓴 적이 없는지는 모릅니다. `LocalCache` 에는 `DeviceMetadataStorage.json`, `PlatformEncryptedKeyStorage.json`, `YppCryptoTrustRelationships`, `Local\`, `Roaming\` 이 있었습니다. 패키지 폴더의 `Settings\` 에는 `settings.dat` 와 `settings.dat.LOG1`·`settings.dat.LOG2` 가 있었고, 이 파일의 형식은 [UWP 앱 데이터 구조](../../01-foundations/app-mail-data/packages-settings-dat.md) 에서 다룹니다.

같은 PC 에 `MicrosoftWindows.CrossDevice_cw5n1h2txyewy` 패키지(1.26072.116.0)도 있었습니다. 이 패키지의 `LocalCache` 에도 같은 이름의 `DeviceMetadataStorage.json`, `YppCryptoTrustRelationships` 가 있었고, `SystemAppData\Helium\User.dat`·`UserClasses.dat` 도 있었습니다.

### 판에 따른 차이

| 구분 | 공개 자료 기준 | 관찰한 PC |
|---|---|---|
| 패키지 이름 | `Microsoft.YourPhone_8wekyb3d8bbwe` [1] | 같음 (1.26072.255.0) |
| DB 위치 | `LocalCache\Indexed\<GUID>\System\Database\` [1] | `Indexed` 없음 |
| 함께 있던 패키지 | 언급 없음 | `MicrosoftWindows.CrossDevice_cw5n1h2txyewy` (1.26072.116.0) |
| 시험한 휴대폰 | 안드로이드만 [1] | 연결 흔적 없음 |

요즘 판에서도 휴대폰 자료가 `Indexed\<GUID>\System\Database` 에 쌓이는지, 일부 자료가 CrossDevice 패키지로 옮겨 갔는지는 확인하지 못했습니다. 그래서 검체에서는 두 패키지 폴더를 통째로 확보한 다음 `Database` 폴더가 어디 있는지 찾습니다.

## 구조

### Database 폴더의 파일

공개 수집 목록 작성자 PC 의 `Database\` 폴더에 있던 파일입니다[1].

```
calling.db        calling.db-shm        calling.db-wal
contacts.db       contacts.db-shm       contacts.db-wal
                  deviceData.db-shm     deviceData.db-wal
notifications.db  notifications.db-shm  notifications.db-wal
phone.db          phone.db-shm          phone.db-wal
photos.db         photos.db-shm         photos.db-wal
settings.db       settings.db-shm       settings.db-wal
```

`deviceData.db` 는 목록에 `-shm`·`-wal` 만 적혀 있었습니다[1]. DB 마다 `-wal`·`-shm` 짝 파일이 있는데[1], 선행 기록 로그 (Write-Ahead Log, WAL) 방식이라 최근 기록이 아직 `.db` 로 옮겨지지 않고 `-wal` 에만 있을 수 있습니다. 그래서 세 파일을 함께 수집합니다. WAL 을 읽는 법은 [WAL과 롤백 저널](../../01-foundations/database-log-formats/sqlite/wal-journal-shm.md) 에서 다룹니다.

### phone.db 를 알아보는 기준

`message`, `mms`, `rcs_chat`, `sync`, `subscription` 다섯 표가 모두 있으면 `phone.db` 로 봅니다[2]. 파일 이름이 바뀌었거나 복구한 파일이라도 이 기준으로 알아볼 수 있습니다.

### message 표 — 문자

공개 SQL 질의가 읽는 칸입니다[2].

| 칸 | 뜻 |
|---|---|
| `message_id` | 메시지 번호 (칸 이름으로 본 뜻) |
| `thread_id` | 대화방 |
| `timestamp` | 시각 (아래 "시각 해석") |
| `from_address` | 보낸 번호 |
| `type` | 1 = 받은 문자, 2 = 보낸 문자, 그 밖 = 알 수 없음 |
| `body` | 본문 |

(표는 [2])

### subscription 표 — 유심과 통신사

유심·통신사 정보가 든 표입니다[2]. 공개 SQL 질의가 읽는 칸은 다음과 같습니다[2]. `name`·`number` 의 뜻은 [2] 에 나온 것이고, 나머지 뜻은 칸 이름으로 본 것입니다.

| 칸 | 뜻 |
|---|---|
| `subscription_id` | 가입 정보 번호 |
| `sim_slot_index` | 유심 슬롯 |
| `country_iso` | 나라 코드 |
| `name` | 통신사 이름 |
| `is_roaming` | 로밍 중인지 |
| `number` | 휴대폰 번호 |
| `is_mms_enabled`, `is_rcs_supported` | MMS·RCS 를 쓸 수 있는지 |
| `is_default_sms_subscription`, `is_default_voice_subscription` | 문자·통화 기본 유심인지 |
| `max_message_size`, `max_rcs_file_size` | 메시지·RCS 파일 최대 크기 |

(표는 [2])

- `number` 로 연결된 휴대폰의 번호를 알 수 있습니다[2].

### 확인하지 못한 표

`mms`, `rcs_chat`, `sync` 표의 칸과 `calling.db`, `contacts.db`, `photos.db`, `notifications.db`, `settings.db` 의 표와 칸은 확인하지 못했습니다. 검체에서는 `.schema` 로 표와 칸을 직접 확인합니다.

> 그림 자리: `phone.db` 의 `message` 표와 `subscription` 표 — 두 표의 칸을 나란히 놓고, `number`·`from_address`·`type` 이 무엇을 알려 주는지 표시

## 증거로서 의미

### 증명하는 것

- 이 PC 의 그 사용자 프로필에 휴대폰이 연결된 적이 있습니다. 문자·연락처·통화 기록 등이 이 PC 로 동기화됐습니다[1].
- `subscription` 표로 연결된 휴대폰의 번호와 통신사를 알 수 있습니다[2].
- `message` 표로 문자 본문, 상대 번호, 받음·보냄 구분, 시각을 알 수 있습니다[2].

### 증명하지 못하는 것

- PC 앞의 사람이 문자를 읽었는지: DB 에 문자가 있다는 것은 동기화된 기록입니다. 누가 PC 화면에서 그 문자를 봤다는 뜻은 아닙니다.
- 보낸 곳: `type=2`(보낸 문자)만으로는 PC 에서 입력해 보냈는지 휴대폰에서 보냈는지 가리지 못합니다. 이를 가리는 칸이 따로 있는지는 확인하지 못했습니다.
- 휴대폰에서 지운 문자: PC DB 에 남는지 확인하지 못했습니다.
- 사진 전체: `photos.db` 에 대해 공개 목록은 "파일 이름과 blob" 만 적었습니다[1]. 휴대폰 사진 전체가 들어 있는지는 확인하지 못했습니다.
- 알림 이력 전체: `notifications.db` 는 "현재(활성) 알림" 이라고 적혀 있습니다[1]. 지난 알림 이력 전체가 아닐 수 있습니다.
- PC 에서 휴대폰으로 파일을 보냈는지: 이 페이지의 DB 는 휴대폰에서 PC 로 온 자료입니다.

### 보고서 문장

- 쓸 수 있는 문장: "`<사용자>` 프로필의 Phone Link 패키지 폴더에 있는 `phone.db` 의 `subscription` 표에 휴대폰 번호 `<번호>` 가 있습니다. 같은 DB 의 `message` 표에는 `<시각> (UTC)` 에 `<상대 번호>` 에게서 받은 문자(`type`=1)가 있습니다."
- 피할 문장: "사용자는 PC 로 이 문자를 읽었다." DB 는 동기화까지만 말해 줍니다.

## 시각 해석

`message.timestamp` 는 FILETIME 과 같은 방식으로 1601-01-01 부터 센 100나노초 단위 값입니다[2]. 공개 SQL 질의는 `(timestamp / 10000000) - 11644473600` 으로 Unix 초로 바꾼 다음 `datetime(..., 'unixepoch')` 으로 읽으며[2], 결과는 UTC 입니다. SQLite 에서 정수끼리 나누면 소수점 아래를 버리므로 이 식은 1초 미만을 버립니다.

이 시각이 휴대폰에서 문자가 오간 시각인지, PC 로 동기화된 시각인지는 확인하지 못했습니다. 공개 질의는 이 칸을 문자 시각으로 씁니다. 다른 DB 의 시각 칸 형식도 확인하지 못했으므로 자릿수로 형식부터 가립니다. 형식별 읽는 법은 [시각 값 형식](../../01-foundations/value-decoding/filetime-unix-webkit-dos-ole.md) 에서 다룹니다.

## 함정과 한계

- 패키지 이름(`YourPhone`)과 앱 표시 이름(휴대폰과 연결·Phone Link)이 다릅니다[1]. 표시 이름으로 폴더를 찾으면 찾지 못합니다.
- 앱이 설치돼 있어도 `Indexed` 가 없을 수 있습니다. 관찰 PC 가 그랬습니다(관찰).
- `*.db` 만 모으고 `-wal` 을 빼면 최근 문자가 빠질 수 있습니다.
- 아이폰 연결은 공개 수집 목록에서 시험하지 않았습니다[1].
- 관찰 PC 에 `PlatformEncryptedKeyStorage.json` 처럼 암호와 관련된 이름의 파일이 있었습니다(관찰). 이 파일이 DB 를 암호화하는 데 쓰이는지는 확인하지 못했습니다.
- 공개 수집 목록은 DB 를 일반 SQLite 뷰어로 바로 연다고 적었습니다[1]. 검체에서도 첫 16바이트로 평문인지 먼저 확인합니다.
- 원본 말고 사본에서 작업합니다. `.db`·`-wal`·`-shm` 세 파일을 함께 복사한 사본을 엽니다. WAL 이 붙은 DB 를 열고 닫을 때 파일이 어떻게 바뀌는지는 [WAL과 롤백 저널](../../01-foundations/database-log-formats/sqlite/wal-journal-shm.md) 에서 다룹니다.

### 지운 기록

앱이 DB 에서 행을 지우면 빈 공간에 흔적이 남을 수 있습니다. 찾는 법은 [파일 안에 남은 지운 레코드](../../01-foundations/database-log-formats/sqlite/freelist-freeblock.md) 에서 다룹니다. Phone Link DB 에서 지운 문자가 실제로 남는지, 사용자가 앱과 휴대폰의 연결을 끊으면 PC 쪽 DB 가 어떻게 되는지는 확인하지 못했습니다. 섀도 복사본에 옛 DB 가 남아 있는지 찾아봅니다([섀도 복사본 활용](../../03-techniques/analysis/volume-shadow-copy-analysis.md)).

## 직접 분석해 보기

### 헥스로 한 번

아래 예시는 SQLite 명세와 FILETIME 정의로 만든 예시입니다. 실제 검체에서 뽑은 값이 아닙니다.

**1. 평문 SQLite 인지 가리기**

```
오프셋  00 01 02 03 04 05 06 07 08 09 0A 0B 0C 0D 0E 0F
0x00    53 51 4C 69 74 65 20 66 6F 72 6D 61 74 20 33 00   SQLite format 3.
```

1. `Database\` 아래 `.db` 파일마다 첫 16바이트를 봅니다.
2. 위와 같으면 평문 SQLite 입니다. 사본을 일반 SQLite 도구로 엽니다.
3. 다르면 암호화됐거나 손상된 파일입니다. 이때는 일반 SQLite 도구로 읽히지 않습니다.

**2. timestamp 를 손으로 풀기**

`message.timestamp` 값이 `133485408000000000` 이라고 합시다.

4. 10,000,000 으로 나눕니다. 13,348,540,800 입니다. 1601-01-01 부터 센 초입니다.
5. 11,644,473,600 을 뺍니다. 1,704,067,200 입니다. 1970-01-01 부터 센 Unix 초입니다.
6. UTC 로 읽으면 2024-01-01 00:00:00 입니다.

SQLite 레코드 안에 정수가 어떤 바이트로 들어가는지는 [SQLite 데이터베이스](../../01-foundations/database-log-formats/sqlite/index.md) 에서 다룹니다.

### 공개 도구로 한 번

sqlite3 명령줄 도구 같은 공개 SQLite 도구로 사본을 엽니다. 먼저 `.tables` 로 다섯 표가 모두 있는지 봅니다.

문자는 다음처럼 읽습니다. 공개 SQL 질의[2]와 같은 방식으로 쓴 예시입니다. 공개 질의는 대화방(`thread_id`)별로 먼저 묶고 그 안에서 시각 순으로 늘어놓습니다[2].

```sql
SELECT message_id,
       thread_id,
       datetime((timestamp / 10000000) - 11644473600, 'unixepoch') AS time_utc,
       from_address,
       CASE type WHEN 1 THEN '받음' WHEN 2 THEN '보냄' ELSE '알 수 없음' END AS direction,
       body
FROM message
ORDER BY timestamp;
```

연결된 휴대폰의 번호와 통신사는 다음처럼 읽습니다.

```sql
SELECT sim_slot_index, name, number, country_iso, is_roaming
FROM subscription;
```

- `time_utc` 는 UTC 입니다. 보고서에 현지 시각을 함께 적을 때는 검체의 시간대 설정을 확인합니다([시간대 설정](../system-account/time-zone.md)).
- 결과 가운데 한두 건은 위 헥스 절처럼 손으로 다시 계산해 맞춰 봅니다. 방법은 [도구 결과 교차 검증](../../03-techniques/reporting/tool-validation.md) 을 봅니다.

## 교차 검증

| 함께 볼 아티팩트 | 무엇을 맞춰 보나 |
|---|---|
| [스마트폰으로 옮겼나 (MTP·Phone Link)](../../04-scenarios/exfiltration/data-exfiltration/mtp-phone-link.md) | USB·MTP 연결 기록과 Phone Link 를 함께 읽는 순서 |
| [휴대용 장치·볼륨 이름 기록](../external-devices/usb-storage-artifacts/wpd-emdmgmt.md) | 같은 휴대폰을 USB·MTP 로도 연결했는지 |
| [블루투스 장치](../external-devices/bthport.md) | 휴대폰과 블루투스로 짝지은 기록. Phone Link 가 블루투스를 쓰는지는 확인하지 못했습니다 |
| [스토어 앱 설치 목록](../system-account/appx-staterepository.md) | Phone Link 패키지를 설치한 기록과 판 |
| [UWP 앱 데이터 구조](../../01-foundations/app-mail-data/packages-settings-dat.md) | 패키지 폴더의 `settings.dat` |
| [윈도 알림 기록](../execution/wpndatabase-db.md) | PC 쪽 윈도 알림에 휴대폰 알림이 남는지. 확인하지 못했습니다 |
| [SQLite 데이터베이스](../../01-foundations/database-log-formats/sqlite/index.md) | DB 형식과 WAL·빈 공간 |
| [시각 값 형식](../../01-foundations/value-decoding/filetime-unix-webkit-dos-ole.md) | `timestamp` 의 FILETIME 방식 |

문자·통화 기록을 다른 연락 흔적과 합쳐 읽는 순서는 [누구와 연락을 주고받았나](../../04-scenarios/activity/communication-reconstruction.md) 에서 다룹니다.

## 실습

NIST CFReDS 같은 공개 검체 가운데 Phone Link 를 쓴 Windows 이미지를 고릅니다. 없으면 실험용 가상 머신에 안드로이드 휴대폰을 연결해 씁니다.

1. 사용자마다 `Microsoft.YourPhone_8wekyb3d8bbwe` 폴더가 있습니까? 그 안에 `LocalCache\Indexed` 가 있습니까?
2. `Database\` 폴더의 파일 목록을 적습니다. DB 마다 `-wal` 이 있고 크기가 0 보다 큽니까?
3. `phone.db` 에 다섯 표(`message`, `mms`, `rcs_chat`, `sync`, `subscription`)가 모두 있습니까?
4. `subscription` 표의 휴대폰 번호와 통신사는 무엇입니까?
5. `message` 표에서 가장 이른 문자와 가장 늦은 문자의 UTC 시각을 구합니다. 한 건은 손으로 계산해 맞춰 봅니다.
6. `-wal` 을 넣고 연 사본과 뺀 사본에서 `message` 행 수를 비교합니다. 차이가 있습니까?
7. `MicrosoftWindows.CrossDevice_cw5n1h2txyewy` 패키지가 있으면, 그 폴더에 휴대폰 자료로 보이는 파일이 있는지 찾아봅니다. 결과에는 Windows 버전과 두 패키지의 판을 함께 적습니다.

## 참고 문헌

1. Andrew Rathbun, KapeFiles 수집 목록 "WindowsYourPhone.tkape" (v1.0) — https://raw.githubusercontent.com/EricZimmerman/KapeFiles/master/Targets/Apps/WindowsYourPhone.tkape
2. Andrew Rathbun, SQLECmd SQL 맵 "Windows_YourPhone_PhoneDB-SMSMessages.smap" (v1.1) — https://raw.githubusercontent.com/EricZimmerman/SQLECmd/master/SQLMap/Maps/Windows_YourPhone_PhoneDB-SMSMessages.smap
