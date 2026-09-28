---
title: "알림 센터 DB"
parent: "아티팩트 · 메시지·메신저"
nav_order: 1485
---

# 알림 센터 DB (Notification Center)

맥은 앱이 띄운 알림을 사용자별 SQLite 파일 하나에 모아 두고, 알림마다 보낸 앱의 번들 ID, 전달 시각, 제목·부제목·본문을 한 행으로 남깁니다 [1][2]. 메신저 알림이면 메시지 내용이 평문으로 들어 있어서 [6], 메신저 DB를 열 수 없거나 대화가 지워졌을 때도 대화 일부가 여기에 남아 있을 가능성이 있습니다. 파일 위치는 macOS 버전마다 다르고, macOS 15 Sequoia 부터는 개인 정보 보호 권한 (TCC) 이 막는 그룹 컨테이너 (Group Containers) 안에 있습니다 [1][5][6].

## 무엇을 기록하나 · 왜 생기나

알림 센터 (Notification Center) 는 앱이 보낸 알림을 받아 화면에 띄우고 목록으로 보여 줍니다. 이 과정에서 알림 하나마다 DB에 행이 하나 생기고, 행에는 어느 앱이 보냈는지와 언제 전달됐는지, 알림에 적힌 글이 함께 들어갑니다 [1][2]. 메시지·슬랙·팀즈·X·페이스북처럼 알림을 보내는 앱이면 모두 이 DB에 기록이 남고, 내용은 암호화되지 않은 평문입니다 [6].

그래서 이 DB는 앱 하나의 기록이 아니라 알림을 보낸 모든 앱의 기록을 한곳에 모은 목록입니다. 메신저 DB가 암호화돼 있거나 사용자가 대화를 지웠을 때도 알림으로 전달된 제목과 본문은 이 DB에 따로 남아 있을 가능성이 있습니다.

## 위치와 버전별 차이

DB 위치는 macOS 버전에 따라 네 곳입니다 [1].

| macOS 버전 | 위치 |
|---|---|
| 10.9 Mavericks 까지 | `~/Library/Application Support/NotificationCenter/` 아래 UUID 이름의 `.db` 파일 [1][4] |
| 10.10 Yosemite ~ 10.12 Sierra | 사용자 Darwin 폴더 아래 `com.apple.notificationcenter/db/db` [1][4] |
| 10.13 High Sierra ~ 14 Sonoma | 사용자 Darwin 폴더 아래 `com.apple.notificationcenter/db2/db` [1][2][4] |
| 15 Sequoia 이후 | `~/Library/Group Containers/group.com.apple.usernoted/db2/db` [1][5][6] |

사용자 Darwin 폴더 (DARWIN_USER_DIR) 는 `/private/var/folders/` 아래 폴더 두 단계를 더 내려간 곳의 `0` 폴더입니다 [1][4]. 실행 중인 맥에서는 `getconf DARWIN_USER_DIR` 로 그 사용자의 폴더를 바로 찾을 수 있습니다 [6]. 폴더 이름에는 사용자 이름이 없어서, 어느 계정의 DB인지는 [사용자 계정 (Local Accounts)](../system-account/user-accounts/index.md)에서 UID로 이어 판단합니다.

```
(만든 예시)
/private/var/folders/zx/3kq9v1x52m7b0c4h8t6w0000gn/0/com.apple.notificationcenter/db2/db
/Users/minsu/Library/Group Containers/group.com.apple.usernoted/db2/db
```

High Sierra 로 올린 맥에는 `db/db` 와 `db2/db` 가 함께 남아 있을 수 있습니다 [1]. macOS 14 이전에는 이 DB가 `/private/var/folders/` 안에 있어서 TCC 허락 없이 읽을 수 있었고, macOS 15 에서 옮겨 간 그룹 컨테이너는 TCC 가 접근을 막습니다 [5][6]. Csaba Fitzl 은 2024년 7월 12일, 이 이동으로 메시지 내용을 알림 센터 DB에서 읽어 갈 수 없게 됐다고 밝혔습니다 [5].

## 구조

DB 안의 표 구성은 두 세대로 나뉩니다. `dbinfo` 표에서 키가 `compatibleVersion` 인 행의 값이 17 이상이면 High Sierra 이후 구조입니다 [1].

**High Sierra 이후 구조 (`db2/db`, 그룹 컨테이너의 `db2/db`).** 알림 한 건이 `record` 표의 한 행이고, `app` 표와 `app_id` 로 이어집니다 [1][2].

| 표 · 열 | 뜻 |
|---|---|
| `record.rec_id` | 행 번호 [2] |
| `record.app_id` | 보낸 앱. `app.app_id` 와 이어집니다 [1][2] |
| `app.identifier` | 앱 번들 ID [1][2] |
| `app.badge` | 앱 배지 값. macOS 10.14 이후 쿼리에만 있습니다 [2] |
| `record.delivered_date` | 전달 시각 [1][2] |
| `record.presented` | 알림을 화면에 띄웠는지를 나타내는 값. mac_apt 는 이 열을 `Shown` 으로 내보냅니다 [1] |
| `record.style` | 알림 표시 방식 [2] |
| `record.snooze_fire_date`, `record.request_date`, `record.request_last_date` | 다시 알림 시각, 요청 시각, 마지막 요청 시각 [2] |
| `record.uuid` | 알림 UUID. 16바이트 BLOB 입니다 [1][2] |
| `record.data` | 알림 내용을 담은 plist BLOB [1][2] |
| `categories.categories` | 앱별 알림 분류 BLOB. macOS 10.14 이후 쿼리에만 있습니다 [2] |

`record.data` 는 plist 이고, 최상위 `app` 키에 번들 ID가, `req` 딕셔너리에 알림 글이 들어 있습니다 [1]. `req` 안에서 `titl` 은 제목, `subt` 는 부제목, `body` 는 본문, `iden` 은 알림 식별자입니다 [1]. macOS 10.15 에서는 이 값이 문자열이 아니라 목록으로 들어 있는 경우도 있습니다 [1]. plist 를 읽는 방법은 [속성 목록 파일 (Property List)](../../01-foundations/data-formats/plist/index.md)에 있습니다.

**Sierra 까지의 구조 (`NotificationCenter/*.db`, `db/db`).** 알림 한 건이 `presented_notifications` 표의 한 행입니다 [1]. 이 표의 `date_presented` 가 표시 시각, `actually_presented` 가 실제로 띄웠는지를 나타내는 값이고, `app_id` 로 `app_info.bundleid`(번들 ID)와 `app_loc.last_known_path`(앱 경로)를, `note_id` 로 `notifications.uuid` 와 `notifications.encoded_data` 를 찾습니다 [1]. `encoded_data` 는 NSKeyedArchiver 로 저장한 plist 라서, 두 번째 객체의 `NSTitle`·`NSSubtitle`·`NSInformativetext` 값이 가리키는 `$objects` 번호를 따라가 제목·부제목·본문을 읽습니다 [1]. 푸는 방법은 [NSKeyedArchiver 풀기 (NSKeyedArchiver)](../../01-foundations/data-formats/plist/nskeyedarchiver.md)에 있습니다. `uuid` 열은 macOS 10.12 Sierra 에서 16진 문자열 대신 BLOB 로 바뀌었습니다 [1].

SQLite 파일과 WAL 의 일반 구조는 [SQLite 데이터베이스 (SQLite)](../../01-foundations/data-formats/sqlite/index.md)를 따릅니다.

> 그림 자리: `app` 표와 `record` 표가 `app_id` 로 이어지고, `record.data` 의 plist 안 `req` 딕셔너리에 `titl`·`subt`·`body`·`iden` 이 들어 있는 관계

## 증거로서 의미

**증명하는 것.** 행이 있으면 그 번들 ID의 앱이 그 시각에 이 사용자 계정의 알림 센터로 알림을 보냈고, 알림에 그 제목과 본문이 적혀 있었다는 사실을 보여 줍니다. 메신저 알림이면 보낸 사람 이름이나 대화방 이름, 메시지 본문의 일부가 제목과 본문에 들어 있을 수 있어서, 메신저 DB가 없거나 열리지 않을 때 대화 내용을 확인하는 다른 경로가 됩니다 [6]. 앱 설치 기록이 사라졌더라도 번들 ID가 남아 있으면 그 앱이 한때 이 계정에서 알림을 보낼 만큼 동작했다는 정황이 됩니다.

**증명하지 못하는 것.** 알림이 전달됐다고 사용자가 읽었다는 뜻은 아닙니다. `presented` 값도 알림을 띄웠는지를 나타낼 뿐, 누가 화면 앞에 있었는지는 알 수 없습니다. 알림 글은 앱이 알림용으로 정한 글이라서 원래 메시지보다 짧거나 다른 문장일 가능성이 있고, 대화 전체가 아니라 알림으로 전달된 것만 남습니다. 사용자가 그 앱의 알림을 껐거나 앱이 알림에 내용을 넣지 않았을 수도 있어서, 알림 행이 없다고 메시지가 오지 않았다고 볼 수는 없습니다.

보고서에는 "메시지를 받았다" 보다 "`record` 표 `rec_id` ○○ 행에 UTC ○○시 ○○분, 번들 ID ○○ 앱이 보낸 제목 ○○·본문 ○○ 알림이 전달된 기록이 있다" 처럼 기록으로 확인되는 만큼만 씁니다.

## 시각 해석

`delivered_date` 는 2001-01-01 00:00:00 UTC 부터 센 초, 곧 맥 절대 시각입니다 [1][2]. 유닉스 시각으로 바꾸려면 978307200 을 더하고, SQL 로는 `DATETIME(delivered_date+978307200,'unixepoch')` 로 UTC 시각을 얻습니다 [2]. 이 값은 알림이 알림 센터로 전달된 때라서, 앱이 메시지를 받은 때나 상대가 보낸 때와 차이가 날 수 있습니다. 옛 구조의 `date_presented` 도 같은 맥 절대 시각입니다 [1].

`request_date`·`request_last_date`·`snooze_fire_date` 는 APOLLO 가 바꾸지 않고 그대로 내보내는 열입니다 [2]. 같은 맥 절대 시각일 가능성이 있으니, 값의 자릿수와 `delivered_date` 와의 차이를 보고 기준을 확인한 뒤 바꿉니다. 기준점과 단위는 [맥의 시각 값 (Mac Absolute Time·Unix·HFS)](../../01-foundations/value-decoding/mac-time-values.md)을, 현지 시각으로 옮길 때는 [시간대와 시계 설정 (Time Zone·NTP)](../system-account/time-zone.md)을 봅니다.

## 함정과 한계

- **옛 위치만 수집하는 경우.** ForensicArtifacts 의 `MacOSNotificationCenterSQLiteDatabaseFile` 정의에는 `NotificationCenter/*.db` 와 `/private/var/folders/` 아래 `db/db`·`db2/db` 경로만 있고 그룹 컨테이너 경로가 없습니다 [4]. 이 정의로 수집 목록을 만들면 macOS 15 이후 DB가 빠집니다.
- **새 위치만 보는 경우.** mac_apt 는 macOS 15 이후 이미지에서 그룹 컨테이너의 DB만 읽습니다 [1]. 14 이전에서 올린 맥이라면 `/private/var/folders/` 에 옛 DB가 남아 있을 가능성이 있으니 두 위치를 함께 찾습니다.
- **실행 중인 맥에서 TCC 에 막히는 경우.** macOS 15 이후 DB는 TCC 가 지키는 그룹 컨테이너에 있어서 [5][6], 실행 중인 맥에서 파일을 복사하는 수집 도구가 권한을 받지 못하면 파일을 읽지 못합니다. 수집 도구의 권한과 수집 결과를 [맥 증거 확보 (Acquisition)](../../03-techniques/process-acquisition/evidence-acquisition/index.md)의 방법으로 확인하고, 권한 기록은 [개인 정보 보호 권한 (TCC)](../credentials/tcc/index.md)에서 봅니다.
- **WAL 파일을 빼먹는 경우.** 최근 알림이 아직 `-wal` 파일에만 있을 수 있어서, `db` 와 같은 폴더의 `db-wal`·`db-shm` 을 함께 수집합니다. WAL 동작은 [SQLite 데이터베이스 (SQLite)](../../01-foundations/data-formats/sqlite/index.md)에 있습니다.
- **화면 사용 시간 알림.** 번들 ID `com.apple.ScreenTimeNotifications` 알림은 `titl`·`subt`·`body` 에 글 대신 세 항목짜리 목록이 들어 있고, 첫 항목은 문장을 찾는 키, 세 번째 항목은 문장에 채워 넣을 값 목록입니다 [1]. 글로 풀려면 `/System/Library/UserNotifications/Bundles/com.apple.ScreenTimeNotifications.bundle/Contents/Resources/` 아래 `en.lproj/Localizable.strings`·`en.lproj/InfoPlist.strings` 나 `Localizable.loctable`·`InfoPlist.loctable` 에서 키에 맞는 문장을 찾아 값을 채워 넣습니다 [1].
- **지우기와 조작.** 사용자가 알림을 지웠을 때 행이 어떻게 되는지는 버전마다 실제 데이터로 확인합니다. SQLite 빈 페이지와 WAL 에 남은 옛 행을 찾는 방법은 [삭제 데이터 복구 (Data Recovery)](../../03-techniques/analysis/data-recovery/index.md)에, 지우려 한 정황을 판단하는 흐름은 [증거를 없애려 했나 (Anti-Forensics)](../../04-scenarios/activity/anti-forensics/index.md)에 있습니다.

## 직접 분석해 보기

원본을 바로 열지 않고 `db`·`db-wal`·`db-shm` 을 작업 폴더로 함께 복사한 뒤 사본에서 봅니다.

### 헥스로 한 번

`db` 의 첫 16바이트가 `SQLite format 3` 과 널 바이트 하나인지 봅니다. 이어서 `record.data` 한 행을 16진으로 뽑아, 앞 8바이트가 바이너리 plist 머리 `bplist00` 인지 확인합니다. 아래 값은 두 형식의 명세로 만든 예시이고, 실제 기기에서 나온 값이 아닙니다.

```
(만든 예시) db 파일 머리
00000000  53 51 4c 69 74 65 20 66 6f 72 6d 61 74 20 33 00  |SQLite format 3.|

(만든 예시) record.data 앞부분
00000000  62 70 6c 69 73 74 30 30                          |bplist00|
```

```sh
xxd -l 16 db
sqlite3 db "SELECT hex(data) FROM record WHERE rec_id = 1;" | xxd -r -p - | xxd -l 8
```

### sqlite3 로 한 번

1. 구조 세대를 확인합니다.

   ```sql
   SELECT value FROM dbinfo WHERE key = 'compatibleVersion';
   ```

2. 17 이상이면 APOLLO `notifications_db` 모듈의 쿼리를 따라 알림 목록을 뽑습니다 [2].

   ```sql
   SELECT record.rec_id,
          DATETIME(record.delivered_date + 978307200, 'unixepoch') AS delivered_utc,
          app.identifier AS bundle_id,
          record.presented, record.style,
          HEX(record.uuid) AS uuid_hex
   FROM record
   LEFT JOIN app ON app.app_id = record.app_id
   ORDER BY record.delivered_date;
   ```

3. 한 행의 `data` 를 plist 로 풀어 `req` 안의 `titl`·`subt`·`body` 를 읽습니다. 맥에서는 아래처럼 `plutil` 로 볼 수 있습니다 [6].

   ```sh
   sqlite3 db "SELECT hex(data) FROM record WHERE rec_id = 1;" | xxd -r -p - | plutil -p -
   ```

4. 같은 사본을 공개 도구로 읽어 결과를 맞춰 봅니다. mac_apt 의 `NOTIFICATIONS` 플러그인은 이미지 전체에서 버전에 맞는 위치를 찾아 제목·부제목·본문을 풀어 주고, DB 파일 하나만 넣어 돌릴 수도 있습니다 [1]. APOLLO `notifications_db` 모듈은 `data` 를 16진 그대로 내보냅니다 [2]. 행 수와 시각이 SQL 결과와 같은지 [도구 검증 (Tool Validation)](../../03-techniques/reporting/tool-validation.md)의 방법으로 확인합니다.

## 교차 검증

| 함께 볼 자료 | 확인할 것 |
|---|---|
| [메시지 (iMessage·SMS)](imessage/index.md), [카카오톡 맥 (KakaoTalk)](kakaotalk.md), [슬랙 (Slack)](slack.md) | 알림 본문과 같은 메시지가 앱 DB에 남아 있는지, 지워졌는지 |
| [KnowledgeC (knowledgeC.db)](../execution/knowledgec/index.md) | `/notification/usage` 스트림의 번들 ID와 시각. APOLLO 는 macOS 10.15·10.16 에서 이 스트림을 읽습니다 [3] |
| [화면 사용 시간 (Screen Time)](../execution/screen-time.md) | `com.apple.ScreenTimeNotifications` 알림과 같은 시간대의 사용 기록 |
| [번들 ID와 팀 ID (Bundle ID·Team ID)](../../01-foundations/value-decoding/bundle-team-id.md), [설치한 앱과 영수증 (Applications·Receipts)](../system-account/installed-apps-receipts.md) | 번들 ID가 어떤 앱이고 언제 설치됐는지 |
| [개인 정보 보호 권한 (TCC)](../credentials/tcc/index.md) | macOS 15 이후 그룹 컨테이너에 접근한 앱의 권한 기록 |
| [누구와 연락을 주고받았나 (Communication)](../../04-scenarios/activity/communication.md) | 여러 통신 기록을 묶어 보는 조사 흐름 |

## 실습

NIST CFReDS 같은 공개 시험 이미지 가운데 맥 사용자 폴더와 `/private/var/folders/` 가 들어 있는 이미지를 골라 아래 질문을 풀어 봅니다.

1. 이미지의 macOS 버전은 무엇이고, 위 표에 따르면 알림 센터 DB는 어느 위치에 있어야 하나요? 실제로 그 위치에 있나요?
2. `dbinfo` 의 `compatibleVersion` 값은 얼마이고, 어느 구조 세대에 해당하나요?
3. `app` 표에 번들 ID가 몇 개 있고, 알림이 가장 많은 앱은 무엇인가요?
4. 메신저 번들 ID의 알림 가운데 하나를 골라 `data` 를 풀고, `titl`·`body` 값을 그 메신저 DB의 메시지와 맞춰 보세요.
5. 가장 이른 `delivered_date` 와 가장 늦은 값을 UTC 로 바꾸면 언제인가요?

## 참고 문헌

1. ydkhatri/mac_apt `plugins/notifications.py` (GitHub) — https://github.com/ydkhatri/mac_apt/blob/master/plugins/notifications.py
2. mac4n6/APOLLO `modules/notifications_db.txt` (GitHub) — https://github.com/mac4n6/APOLLO/blob/master/modules/notifications_db.txt
3. mac4n6/APOLLO `modules/knowledge_notification_usage.txt` (GitHub) — https://github.com/mac4n6/APOLLO/blob/master/modules/knowledge_notification_usage.txt
4. ForensicArtifacts `artifacts/data/macos.yaml` (`MacOSNotificationCenterSQLiteDatabaseFile`, 별칭 `MacOSNotificationCenter`) — https://github.com/ForensicArtifacts/artifacts/blob/main/artifacts/data/macos.yaml
5. Csaba Fitzl (@theevilbit), X 게시글, 2024-07-12 — https://x.com/theevilbit/status/1811758367045537990
6. Arin Waichulis, "Security Bite: Apple addresses privacy concerns around Notification Center database in macOS Sequoia", 9to5Mac, 2024-09-01 — https://9to5mac.com/2024/09/01/security-bite-apple-addresses-privacy-concerns-around-notification-center-database-in-macos-sequoia/
