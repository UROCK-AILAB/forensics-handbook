---
title: "클라우드로"
parent: "자료를 밖으로 빼돌렸나"
grand_parent: "시나리오 · 정보 유출"
nav_order: 2470
---

# 클라우드로 (Cloud)

## 조사 질문

이 맥에서 아이클라우드 드라이브 (iCloud Drive)나 드롭박스 같은 클라우드 저장소로 자료를 올렸는지 묻습니다. 아이클라우드 드라이브는 맥 안에 동기화 목록 데이터베이스를 남기고, 파일 버전마다 어느 기기와 이어지는지 적혀 있어 다른 경로보다 기록이 구체적인 편입니다. 제3자 클라우드는 앱마다 저장 방식이 달라서, 이 페이지는 공개 자료로 확인한 폴더 위치와 동작만 다루고 앱별 내용은 각 아티팩트 페이지로 넘깁니다. 경로마다 공통으로 쓰는 판단 원칙은 [자료를 밖으로 빼돌렸나](index.md) 허브에 있습니다.

## 먼저 확인할 것

사용자와 계정부터 확인합니다. 아이클라우드 사용자 환경 설정은 `~/Library/Preferences/MobileMeAccounts.plist`에 있고, 계정 정보는 `~/Library/Application Support/iCloud/Accounts/` 아래에 있습니다 [1]. 읽는 법은 [아이클라우드 계정](../../../02-artifacts/cloud-apps/icloud-account.md) 페이지에 있습니다.

OS 버전은 제3자 클라우드 폴더 위치와 이어집니다. 드롭박스의 파일 공급자 (File Provider)판은 macOS 12.5 이상이 필요하고, 이 판에서는 드롭박스 폴더가 `~/Library/CloudStorage/` 아래로 옮겨졌으며 파인더 사이드바에서 "즐겨찾기"가 아닌 "위치"에 나타납니다 [3]. 그보다 낮은 버전이나 예전 판을 쓴 맥은 폴더 위치가 다를 수 있어서, OS 버전을 [OS 버전과 설치 기록](../../../02-artifacts/system-account/os-version-install-history.md)에서 먼저 확인합니다.

| 항목 | 확인된 버전 조건 | 출처 |
|---|---|---|
| 드롭박스 파일 공급자판 | macOS 12.5 이상, 폴더는 `~/Library/CloudStorage/` 아래 | [3] |
| 아이클라우드 드라이브 데이터베이스 | 버전 경계는 공개 자료로 확인하지 못함 | — |

수집 범위도 따로 챙깁니다. ForensicArtifacts 정의에는 드롭박스·구글 드라이브·원드라이브·박스 항목이 없어서 [1], 이 정의만 쓰는 도구로 모으면 해당 폴더가 자동 수집에서 빠질 수 있습니다(필자 해석). `~/Library/CloudStorage/`와 `~/Library/Application Support/CloudDocs/`를 수집 목록에 직접 넣었는지 확인합니다.

## 볼 아티팩트와 순서

| 순서 | 아티팩트 | 알려 주는 것 | 링크 |
|---|---|---|---|
| 1 | `MobileMeAccounts.plist`, `iCloud/Accounts/` | 이 맥에 로그인한 아이클라우드 계정 | [아이클라우드 계정](../../../02-artifacts/cloud-apps/icloud-account.md) |
| 2 | `~/Library/Application Support/CloudDocs/session/db/client.db`·`server.db` | 아이클라우드 드라이브 항목의 이름·부모·시각·기기·공유 여부 | [아이클라우드 드라이브](../../../02-artifacts/cloud-apps/icloud-drive.md) |
| 3 | `~/Library/CloudStorage/` 아래 폴더 | 파일 공급자판 드롭박스 등의 동기화 폴더 | [파일 공급자](../../../02-artifacts/cloud-apps/file-provider.md), [드롭박스](../../../02-artifacts/cloud-apps/dropbox.md) |
| 4 | 최근 항목과 FSEvents | 동기화 폴더로 파일을 옮기거나 연 흔적 | [최근 항목](../../../02-artifacts/file-folder-usage/recent-items/index.md), [파일 시스템 이벤트](../../../02-artifacts/filesystem/fsevents/index.md) |

구글 드라이브와 원드라이브의 데이터베이스·로그 위치는 이 페이지에서 확인하지 못해서 [구글 드라이브](../../../02-artifacts/cloud-apps/google-drive.md)와 [원드라이브](../../../02-artifacts/cloud-apps/onedrive.md) 페이지로 넘깁니다.

### 아이클라우드 드라이브 데이터베이스에서 쓰는 칸

두 파일은 SQLite 데이터베이스이고, mac_apt는 여기서 `server_items`, `client_items`, `app_libraries`(rowid, app_library_name), `devices`(key, name) 표를 읽습니다. mac_apt는 `devices` 표를 `server.db`에서 읽고, 여기서 얻은 기기 목록을 두 파일의 항목에 함께 씁니다 [2]. 표 전체 구조는 [아이클라우드 드라이브](../../../02-artifacts/cloud-apps/icloud-drive.md) 페이지에 있고, 유출 조사에 쓰는 칸만 추리면 아래와 같습니다.

| 칸 | 쓰임 |
|---|---|
| `item_filename` | 파일 이름 |
| `item_id`, `item_parent_id` | 부모 항목의 `item_id`를 따라 올라가 폴더 경로를 다시 만듭니다 |
| `item_birthtime`, `item_lastusedtime`, `version_mtime` | 시각. mac_apt는 유닉스 시각(1970 기준)으로 읽습니다 |
| `version_device` | `devices.key`와 이어져 기기 이름(`devices.name`)을 얻습니다 |
| `version_name`, `version_size` | 버전 정보 |
| `item_sharing_options` | mac_apt는 값이 0이면 공유하지 않은 것으로, 0이 아니면 공유한 것으로 봅니다(`item_is_shared`). 0이 아닌 값의 비트 뜻은 확인하지 못했습니다 |
| `item_type` | 항목 종류. mac_apt는 0을 폴더, 1을 파일, 그 밖의 값을 알 수 없음으로 읽습니다 |

`client_items`에는 이 밖에 `app_library_rowid`가 있습니다 [2].

## 분석 흐름

1. 이 맥에 로그인한 아이클라우드 계정과 설치된 클라우드 앱을 정리합니다([설치한 앱과 영수증](../../../02-artifacts/system-account/installed-apps-receipts.md)).
2. `client.db`와 `server.db`를 사본으로 열고, 어느 파일에 어느 표가 있는지 표 목록(`.tables`)으로 먼저 확인합니다. mac_apt는 `server_items`와 `devices`를 `server.db`에서, `client_items`와 `app_libraries`를 `client.db`에서 읽습니다 [2]. SQLite를 여는 주의점은 [SQLite 데이터베이스](../../../01-foundations/data-formats/sqlite/index.md) 페이지를 따릅니다.
3. 조사 대상 파일 이름으로 `server_items`·`client_items`를 찾고, `version_device`를 `devices` 표와 이어 기기 이름을 붙입니다. `server.db`를 열었을 때의 예입니다.

   ```sql
   SELECT s.item_id,
          s.item_filename,
          s.item_parent_id,
          datetime(s.version_mtime, 'unixepoch')   AS version_mtime_utc,
          datetime(s.item_birthtime, 'unixepoch')  AS birthtime_utc,
          s.version_size,
          d.name                                   AS version_device_name,
          s.item_sharing_options
   FROM server_items s
   LEFT JOIN devices d ON d.key = s.version_device
   WHERE s.item_filename LIKE '%대상파일이름%';
   ```

4. `item_parent_id`를 부모의 `item_id`로 따라 올라가 폴더 경로를 다시 만듭니다. mac_apt는 `length(item_parent_id) < 16`인 행을 최상위로 봅니다 [2].
5. 제3자 클라우드는 `~/Library/CloudStorage/` 아래 동기화 폴더에서 대상 파일을 찾고, 그 파일이 폴더로 들어온 흔적을 FSEvents와 최근 항목에서 찾습니다.
6. 계정·데이터베이스 시각·파일 접근 시각을 한 기준으로 바꿔 [타임라인](../../../03-techniques/analysis/timeline/index.md)에 올립니다. 시각 기준은 [맥의 시각 값](../../../01-foundations/value-decoding/mac-time-values.md)을 참고합니다.

## 흔한 오판

- **동기화 폴더에 파일이 있으니 이 맥이 올렸다고 보는 경우.** 같은 계정의 다른 기기가 올린 파일도 동기화로 내려오기 때문에, 아이클라우드 드라이브라면 `version_device`가 어느 기기와 이어지는지 먼저 봅니다(필자 해석).
- **로컬 폴더에 내용이 없으니 파일이 없었다고 보는 경우.** 드롭박스 파일 공급자판에서 "오프라인에서 사용 가능"으로 지정하지 않은 파일은 디스크 공간이 모자라면 자동으로 온라인 전용이 될 수 있습니다 [3]. 필자 해석으로는 로컬 폴더에 파일 자리만 있고 내용은 없을 수 있습니다.
- **`~/Library/CloudStorage/` 아래에 없으니 드롭박스를 쓰지 않았다고 보는 경우.** 드롭박스 폴더를 외장 드라이브로 옮기는 기능이 일부 사용자에게 배포되고 있습니다(2025년 3월 기준) [3].
- **자동 수집 결과에 클라우드 폴더가 없으니 쓰지 않았다고 보는 경우.** ForensicArtifacts 정의에 제3자 클라우드 항목이 없습니다 [1].
- **`item_sharing_options` 값으로 공유 대상까지 말하는 경우.** mac_apt는 이 값이 0인지 아닌지로 공유 여부만 판단하고 [2], 0이 아닌 값의 비트 뜻은 확인하지 못했습니다.

## 보고서 문장 예

> 사용자 ○○의 아이클라우드 드라이브 데이터베이스(`server.db`) `server_items` 표에 "○○.docx" 항목이 있고, 이 항목의 `version_device`는 `devices` 표에서 이름이 "○○"인 기기와 이어지며, `version_mtime`은 ○○○○-○○-○○ ○○:○○:○○(UTC)입니다. 이 기록은 해당 버전이 그 기기와 이어져 있다는 사실을 보여 주지만, `item_sharing_options` 값이 0이 아니어도 누구와 공유했는지는 이 기록으로 쓰지 않습니다.

## 함께 볼 페이지

- [아이클라우드 드라이브 (iCloud Drive·CloudDocs)](../../../02-artifacts/cloud-apps/icloud-drive.md) — 데이터베이스 구조 전체
- [파일 공급자 (File Provider)](../../../02-artifacts/cloud-apps/file-provider.md) — `~/Library/CloudStorage/` 아래 동기화 폴더
- [웹 업로드로 (Web Upload)](web-upload.md) — 브라우저로 클라우드 사이트에 올린 경우
- [이 파일을 누가 언제 열었나 (File Access)](../../activity/file-access.md) — 올리기 전 파일 접근 흔적

## 참고 문헌

1. ForensicArtifacts, "artifacts/data/macos.yaml" — https://raw.githubusercontent.com/ForensicArtifacts/artifacts/main/artifacts/data/macos.yaml
2. mac_apt, plugins/iCloud.py — https://raw.githubusercontent.com/ydkhatri/mac_apt/master/plugins/iCloud.py
3. Dropbox Help Center, "Expected changes with Dropbox for macOS on File Provider" — https://help.dropbox.com/installs/macos-support-for-expected-changes
