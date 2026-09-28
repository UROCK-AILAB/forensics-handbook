---
title: "아이클라우드 드라이브"
parent: "아티팩트 · 클라우드·애플 앱"
nav_order: 1500
---

# 아이클라우드 드라이브 (iCloud Drive·CloudDocs)

iCloud Drive는 사용자 홈의 `CloudDocs` 폴더 아래 SQLite DB 두 개에 동기화하는 파일마다 이름·부모 항목·생성과 마지막 사용 시각·어느 기기에서 만든 판인지를 남겨서, 파일이 로컬에 없어도 어떤 파일이 iCloud Drive에 있었는지 알아낼 수 있습니다.

## 무엇을 기록하나 · 왜 생기나

iCloud Drive는 여러 기기가 같은 파일을 나눠 쓰도록 동기화하는 서비스라서, 맥은 동기화할 항목의 목록과 판(버전) 정보를 로컬 DB에 두고 관리합니다. 이 DB에는 기기 목록, 서버 쪽 항목, 클라이언트 쪽 항목, 앱 보관함 목록이 들어 있고, 공개 도구 mac_apt의 `iCloud.py` 플러그인으로 읽을 수 있습니다 [1].

계정 자체의 흔적과 iCloud 데이터 보호 방식 전반은 [아이클라우드 계정 (iCloud Account)](icloud-account.md)에서 다루고, 이 페이지는 iCloud Drive에만 해당하는 내용을 다룹니다.

## 위치와 버전별 차이

```
~/Library/Application Support/CloudDocs/session/db/server.db
~/Library/Application Support/CloudDocs/session/db/client.db
```

두 파일 모두 SQLite DB이고 사용자 홈 안에 있어서 사용자마다 따로 봅니다 [1]. 파일 이름으로 보면 `server.db` 는 서버 쪽 상태를, `client.db` 는 이 맥의 로컬 상태를 담는 것으로 보입니다.

ForensicArtifacts 정의(macos.yaml)에는 CloudDocs 항목이 없어서 [2], 이 정의만 쓰는 수집 도구로 자동 수집하면 두 DB가 빠질 수 있습니다. 수집 목록에 이 경로를 직접 넣었는지 확인합니다.

아래 표와 열은 mac_apt 플러그인이 읽는 이름이라서, macOS 10.15 Catalina 이후 기기를 분석할 때는 `.schema` 로 실제 열과 먼저 맞춰 봅니다. 10.15부터는 앱이 iCloud Drive 안 파일에 접근하려면 사용자 동의가 필요하고 [3], 그 동의 기록은 [개인 정보 보호 권한 (TCC)](../credentials/tcc/index.md)에서 봅니다.

## 구조

| 표 | mac_apt가 읽는 열 |
|---|---|
| `devices` | `key`, `name` |
| `server_items` | `item_id`, `item_filename`, `item_parent_id`, `item_birthtime`, `item_lastusedtime`, `version_device`, `version_name`, `version_size`, `version_mtime`, `item_type`, `item_sharing_options` |
| `client_items` | `rowid`, `item_id`, `item_filename`, `item_parent_id`, `item_birthtime`, `item_lastusedtime`, `version_device`, `app_library_rowid`, `version_name`, `version_size`, `version_mtime`, `item_type`, `item_sharing_options` |
| `app_libraries` | `rowid`, `app_library_name` |

두 DB에는 이 네 표가 있습니다 [1]. 표 이름으로 보면 `server_items` 는 `server.db` 에, `client_items` 와 `app_libraries` 는 `client.db` 에 있을 것으로 보이지만, 표마다 어느 파일에 있는지는 실제 파일에서 `.tables` 로 확인합니다.

항목 하나에는 자기 이름(`item_filename`)과 부모 항목 번호(`item_parent_id`)만 있고 전체 경로는 없습니다. 경로는 `item_parent_id` 를 따라 부모를 거슬러 오르는 재귀 쿼리로 조립하고, 가장 깊이 올라간 결과를 그 항목의 경로로 씁니다 [1]. `server_items` 와 `client_items` 모두 같은 방법으로 경로를 만듭니다 [1].

`version_device` 는 그 판을 만든 기기를 가리키는 값이고, `devices.key` 와 맞추면 기기 이름이 나옵니다(mac_apt 출력에서는 `version_device_name` 열) [1]. `client_items.app_library_rowid` 는 `app_libraries.rowid` 와 이어져서, 그 항목이 어느 앱 보관함에 속하는지 알려 줍니다 [1].

`item_type` 과 `item_sharing_options` 는 숫자로 남고, mac_apt 출력에서는 `item_type_str` 과 `item_is_shared` 로 바뀌어 나옵니다 [1]. 숫자값마다 무엇을 뜻하는지(파일·폴더 등)와 공유 옵션의 비트 뜻은 공개된 문서가 없어서, 도구가 붙인 글자를 그대로 보고서에 옮기기 전에 그 변환표의 근거를 확인합니다.

mac_apt 출력 표 이름은 `iCloudDevices`, `iCloudServerItems`, `iCloudClientItems` 이고, `iCloudClientItems` 에서는 판 수정 시각 열이 원문 철자 그대로 `verion_mtime` 으로 나옵니다 [1]. 출력 열을 검색할 때 이 철자를 알아 둡니다.

## 증거로서 의미

**증명하는 것.** DB에 행이 있으면 이 이름의 항목이 이 사용자의 iCloud Drive 동기화 목록에 올라 있었다는 기록이 있다는 뜻입니다 [1]. `version_device` 가 가리키는 기기 이름은 그 판을 어느 기기에서 만들었는지 알려 주는 기록이고, 같은 계정에 묶인 다른 기기의 이름을 이 맥에서 확인하는 실마리가 됩니다 [1].

**증명하지 못하는 것.** DB에 행이 있다고 그 파일 내용이 이 맥 디스크에 있다고 단정하지 않습니다. 행의 존재만으로 이 맥의 사용자가 그 파일을 열었다고도 단정하지 않고, `item_lastusedtime` 은 어떤 동작에서 갱신되는지 시험 기기에서 재현해 보기 전에는 열람 시각으로 단정하지 않습니다. 파일 열람은 [이 파일을 누가 언제 열었나 (File Access)](../../04-scenarios/activity/file-access.md)의 흐름으로 다른 흔적과 맞춰 봅니다.

### 서버 쪽에 남는 것

표준 데이터 보호에서 iCloud Drive는 전송 중과 서버에서 암호화되고 키는 Apple이 보관하며, 고급 데이터 보호를 켜면 종단간 암호화로 바뀝니다 [4]. 표준 보호일 때 iCloud Drive처럼 인증 뒤에 쓸 수 있는 CloudKit 서비스 키는 Apple 데이터센터의 HSM에 있습니다 [3].

고급 데이터 보호를 켜도 iCloud Drive에서 Apple이 키를 쥔 메타데이터가 남고, 여기에는 파일 내용과 파일 이름의 원시 바이트 체크섬, 파일 종류, 만든 때·마지막으로 고친 때·마지막으로 연 때가 들어갑니다 [4]. 공유에도 예외가 있어서, 공유 폴더에서 Keynote·Numbers·Pages 문서를 열거나 함께 편집하면 그 문서의 암호화 키가 Apple 서버로 올라가고, "anyone with a link" 로 공유한 항목은 표준 보호가 됩니다 [3]. 공유마다 제목과 대표 섬네일이 표준 보호로 저장될 수도 있습니다 [3].

보고서에는 "`client.db` 에 이 이름의 항목이 이 앱 보관함 아래 있고, 이 판은 이 이름의 기기에서 만들어졌다는 기록이 있다" 처럼 DB가 보여 주는 만큼만 씁니다.

## 시각 해석

`item_birthtime`, `item_lastusedtime`, `version_mtime` 은 모두 유닉스 시각(초)이라서 [1], 1970-01-01 UTC 기준으로 바꾸고 현지 시각은 [시간대와 시계 설정 (Time Zone·NTP)](../system-account/time-zone.md)을 보고 따로 맞춥니다. 열 이름으로 보면 `item_birthtime` 은 항목이 생긴 때, `version_mtime` 은 그 판의 수정 시각, `item_lastusedtime` 은 마지막으로 쓴 때로 읽히지만, 각 값이 정확히 어떤 동작에서 바뀌는지는 공개된 문서가 없습니다. 이 열들을 타임라인에 넣을 때는 열 이름을 그대로 적고 "파일을 열었다" 같은 행위로 바꿔 쓰지 않습니다.

`version_mtime` 은 판을 만든 기기(`version_device`)에서 정한 시각일 수 있어서, 다른 기기의 시계가 틀렸다면 이 맥의 다른 기록과 어긋날 수 있다는 점도 함께 적어 둡니다.

## 함정과 한계

- **두 DB.** 서버 쪽 항목과 클라이언트 쪽 항목이 다른 DB에 있어서 [1], 한쪽만 보면 목록이 비어 보일 수 있습니다.
- **경로는 조립한 값.** 전체 경로는 DB에 없고 부모를 따라 조립한 결과입니다 [1]. 부모 행이 지워졌거나 끊겼으면 경로가 중간에서 멈추고, 이때는 조립이 멈춘 곳을 그대로 적습니다.
- **자동 수집에서 빠짐.** ForensicArtifacts 정의에 CloudDocs 항목이 없습니다 [2].
- **근거가 공개되지 않은 변환표.** `item_type`, `item_sharing_options` 의 숫자 뜻은 도구의 변환표에 기댑니다.
- **공유의 예외.** 고급 데이터 보호를 켜도 공유 폴더에서 열거나 함께 편집한 iWork 문서의 키는 Apple 서버로 올라가고, 링크 공유는 표준 보호가 됩니다 [3]. 서버 쪽 자료 요청 범위를 정할 때 이 예외를 함께 봅니다.
- **지운 행.** 동기화 목록에서 빠진 행은 SQLite 파일의 빈 공간을 살펴야 하고, 그 방법은 [SQLite 데이터베이스 (SQLite)](../../01-foundations/data-formats/sqlite/index.md)에서 다룹니다.

## 직접 분석해 보기

### 헥스로 한 번

명세로 만든 예시로, `item_birthtime` 열이 4바이트 정수로 저장됐다고 가정하면 레코드 안에서 아래처럼 보입니다.

```
5E 0B E1 00
= 1577836800 (정수)
= 2020-01-01 00:00:00 UTC (유닉스 시각, 초)
```

이 값을 정수로 읽어 1970-01-01 UTC부터 센 초로 바꾸면 날짜가 나옵니다 [1]. 열이 실제로 몇 바이트로 저장됐는지와 레코드 안에서 열 값을 찾아가는 법은 [SQLite 데이터베이스 (SQLite)](../../01-foundations/data-formats/sqlite/index.md)에서 다룹니다.

### SQL로 한 번

사본을 `sqlite3` 로 열고, mac_apt와 같은 방식으로 부모를 거슬러 올라 경로를 만듭니다. 아래는 `client.db` 의 예이고, `server.db` 는 표 이름을 `server_items` 로 바꿔 같은 방식으로 씁니다.

```sql
WITH RECURSIVE up(start_id, cur_parent, path, depth) AS (
  SELECT item_id, item_parent_id, item_filename, 0 FROM client_items
  UNION ALL
  SELECT up.start_id, p.item_parent_id, p.item_filename || '/' || up.path, up.depth + 1
  FROM up JOIN client_items p ON p.item_id = up.cur_parent
)
SELECT c.item_filename, u.path,
       datetime(c.item_birthtime, 'unixepoch')     AS birth_utc,
       datetime(c.item_lastusedtime, 'unixepoch')  AS lastused_utc,
       datetime(c.version_mtime, 'unixepoch')      AS version_mtime_utc,
       c.version_size, c.version_device, a.app_library_name
FROM client_items c
JOIN up u ON u.start_id = c.item_id
LEFT JOIN app_libraries a ON a.rowid = c.app_library_rowid
WHERE u.depth = (SELECT max(depth) FROM up WHERE start_id = c.item_id);
```

`version_device` 는 `devices` 표의 `key` 와 맞춰 기기 이름으로 바꿉니다 [1]. 같은 결과를 mac_apt의 `iCloud` 플러그인으로 뽑아 두 결과가 맞는지 보면 도구 검증도 함께 할 수 있습니다.

## 교차 검증

| 함께 볼 아티팩트 | 맞춰 볼 것 |
|---|---|
| [아이클라우드 계정 (iCloud Account)](icloud-account.md) | 이 사용자 홈에 iCloud 계정 설정이 있는지와 데이터 보호 방식 |
| [파일 공급자 (File Provider)](file-provider.md) | 동기화 폴더의 파일 내용이 로컬에 없을 수 있는 구조 |
| [파일 시스템 이벤트 (FSEvents)](../filesystem/fsevents/index.md) | 같은 이름의 파일이 로컬에서 만들어지고 바뀐 시각 |
| [개인 정보 보호 권한 (TCC)](../credentials/tcc/index.md) | 어떤 앱이 iCloud Drive 파일 접근 동의를 받았는지 |
| [자료를 밖으로 빼돌렸나 (Data Exfiltration)](../../04-scenarios/exfiltration/data-exfiltration/index.md) | 클라우드 동기화 폴더가 유출 경로가 될 때 볼 순서 |

## 실습

공개 시험 데이터(NIST CFReDS 등)의 macOS 이미지로 풀어 봅니다.

1. 사용자 홈마다 `CloudDocs/session/db/` 아래 `server.db` 와 `client.db` 가 있는지 확인해 보세요.
2. `devices` 표에서 이 계정에 묶인 기기 이름을 모두 적고, 그중 이 맥이 어느 것인지 가려내 보세요.
3. 위 SQL로 `client_items` 의 경로를 조립하고, 경로가 끝까지 조립되지 않은 행이 있는지 찾아보세요.
4. `server_items` 에는 있고 `client_items` 에는 없는 파일 이름을 찾아, 그 차이를 어떻게 해석할지 적어 보세요.

## 참고 문헌

1. mac_apt, plugins/iCloud.py — https://raw.githubusercontent.com/ydkhatri/mac_apt/master/plugins/iCloud.py
2. ForensicArtifacts, artifacts/data/macos.yaml — https://raw.githubusercontent.com/ForensicArtifacts/artifacts/main/artifacts/data/macos.yaml
3. Apple Platform Security Guide (2026년 8월 판) — https://help.apple.com/pdf/security/en_US/apple-platform-security-guide.pdf
4. Apple Support, "iCloud data security overview" (2026-01-05) — https://support.apple.com/en-us/102651
