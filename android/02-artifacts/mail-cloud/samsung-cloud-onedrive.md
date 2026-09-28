---
title: "삼성 클라우드와 원드라이브"
parent: "아티팩트 · 메일·클라우드"
nav_order: 1110
---

# 삼성 클라우드와 원드라이브 (Samsung Cloud·OneDrive)

원드라이브 (OneDrive) 앱은 `QTMetadata.db` 의 `items` 표에 클라우드 파일과 폴더의 이름·크기·시각·SHA-1 을 담고 `stream_cache` 표에 기기에 캐시한 사본의 경로를 적어 두어서 [2] 파일 목록과 폴더 경로를 되살릴 수 있습니다. 삼성 클라우드 (Samsung Cloud) 는 앱 쪽 저장 위치를 실제 기기에서 확인해야 합니다.

## 무엇을 기록하나 · 왜 생기나

원드라이브 앱은 계정의 클라우드 저장 공간에 있는 파일과 폴더 목록을 기기에 받아 두고, 사용자가 연 파일은 기기에 사본을 캐시해 둡니다. 공개 도구 ALEAPP 의 Microsoft OneDrive 모듈은 이 목록과 캐시 경로를 읽어 폴더 경로가 붙은 파일 목록으로 보여 줍니다 [2].

삼성 클라우드는 갤럭시 기기의 동기화·백업 서비스이고, 앱 패키지 이름·DB·동기화 기록은 설치된 앱 기록과 앱 데이터 폴더에서 직접 찾아야 합니다. ALEAPP 에도 삼성 클라우드 전용 모듈은 없고 [1], 삼성 이름이 붙은 모듈은 SamsungNotes, SamsungTrash, Samsungwallet, SamsungGalleryHiddenAlbum, samsungMediaProvider, samsungSecureFolderHistoryLog, samsung_honeyboard_clipboard 같은 다른 앱의 것입니다 [1].

## 위치와 버전별 차이

### 원드라이브

패키지 이름은 `com.microsoft.skydrive` 이고, ALEAPP 가 찾는 경로 패턴은 아래와 같습니다 [2]. 패턴 끝의 `*` 는 `-wal` 같은 딸린 파일까지 함께 찾으려는 것입니다.

```
*/com.microsoft.skydrive/files/QTMetadata.db*
```

앱 데이터 폴더의 짜임은 [앱 데이터 폴더 구조](../../01-foundations/storage/app-data-layout.md), 다른 앱이나 셸이 이 폴더를 읽을 수 있는지는 [앱 샌드박스와 권한](../../01-foundations/security-model/sandbox-permissions.md) 페이지에서 다룹니다.

`items` 표에 `sha1Hash` 열이 없는 DB 도 있어서 [2], 질의 전에 열이 있는지 먼저 봅니다.

### 삼성 클라우드

앱 쪽 저장 위치는 실제 기기로 확인해야 합니다. 갤럭시 기기의 설정 값에는 이름에 `scloud` 나 클라우드 백업이 들어간 키가 아래처럼 있을 수 있습니다.

| 설정 표 | 키 |
|---|---|
| secure | `appprotection_permission_scloud_function_usage` |
| secure | `appprotection_permission_scloud_usage_user_decided` |
| secure | `wifi_ap_settings_cloud_backup_restoring` |
| global | `first_launch_samsung_account_menu` |

이 키가 있다는 것만으로 삼성 클라우드를 썼다고 볼 수는 없고, 설정 값을 읽는 법은 [설정 값 (Settings Global·Secure·System)](../system-account/settings.md) 페이지에서 다룹니다.

## 구조

### items 표

`QTMetadata.db` 는 SQLite 파일이고, 파일 형식은 [SQLite 데이터베이스](../../01-foundations/data-formats/sqlite/index.md) 페이지에서 다룹니다. `items` 표의 주요 열은 아래와 같습니다 [2].

| 열 | 담긴 것 |
|---|---|
| `_id` | 행 번호. `stream_cache.parentId` 가 이 값을 가리킴 |
| `resourceId`, `parentRid` | 항목 id 와 상위 폴더 id |
| `resourceIdAlias` | 뜻이 정해져 있지 않음. 값만 옮김 |
| `name`, `extension` | 이름과 확장자 |
| `itemType` | 종류 |
| `ownerName` | 주인 이름 |
| `size` | 크기 |
| `sha1Hash` | SHA-1 (없는 DB 도 있음) |
| `itemDate`, `creationDate`, `modifiedDateOnClient` | 시각 세 개 |

`itemType` 값의 뜻은 아래와 같습니다. 표에 없는 값은 ALEAPP 가 숫자 그대로 보여 줍니다 [2].

| `itemType` | 뜻 |
|---|---|
| 1 | File |
| 3 | Image |
| 32 | Folder |

폴더 경로는 한 항목의 `parentRid` 와 같은 `resourceId` 를 가진 행을 찾고, 그 행의 `parentRid` 를 다시 따라 올라가며 이름을 이어 붙여 만듭니다 [2]. `resourceId` 가 `search`, `Mru`, `SharedBy`, `SharedWithMe` 인 행은 실제 파일이 아니라 목록 화면용 특수 행이라서 셀 때 뺍니다 [2].

### stream_cache 표

`stream_cache` 의 `parentId` 는 `items._id` 를 가리키고, `stream_location` 에 기기에 캐시된 파일 사본의 경로가 적힙니다 [2]. 경로가 적혀 있어도 추출본에 그 캐시 파일이 없을 수 있습니다 [2].

## 증거로서 의미

**증명하는 것**

`items` 행은 그 이름·크기의 파일이나 폴더가 기기에 로그인한 원드라이브 계정의 목록에 있었다는 기록이고, 폴더 경로를 이어 붙이면 클라우드 안에서 어느 폴더에 있었는지까지 볼 수 있습니다 [2]. `stream_cache` 에 행이 있으면 그 파일을 기기로 받아 캐시한 적이 있다는 정황이 되고, 캐시 파일이 남아 있으면 내용을 직접 볼 수 있습니다. `sha1Hash` 는 다른 매체에서 찾은 파일과 내용이 같은지 맞춰 보는 데 쓸 수 있습니다.

**증명하지 못하는 것**

목록에 있다는 것만으로 이 기기에서 그 파일을 올렸다고 할 수 없고, 다른 기기나 웹에서 올린 파일이 동기화로 보였을 수도 있습니다. `ownerName` 이 기기 사용자와 다르면 공유받은 항목일 수 있지만, 공유를 누가 언제 했는지는 이 표만으로 알 수 없습니다. 삼성 클라우드 쪽은 설정 키 이름밖에 없어서 무엇을 동기화했는지 알 수 있는 기록이 없습니다.

## 시각 해석

`itemDate`, `creationDate`, `modifiedDateOnClient` 세 열은 유닉스 밀리초이고, 0 이하인 값은 빈 값으로 봅니다 [2]. 유닉스 시각은 UTC 기준이라 보고서에 현지 시각을 쓸 때는 기기 시간대를 따로 확인합니다. `modifiedDateOnClient` 는 이름으로 보면 클라이언트 쪽에서 고친 시각으로 짐작됩니다. `itemDate` 가 서버에 올라간 시각인지 목록에 들어온 시각인지는 실제 데이터로 확인합니다. 값을 바꾸는 법은 [시각 값](../../01-foundations/value-decoding/time-values.md), 시간대 확인은 [시간대와 시각 설정 (Time Zone)](../system-account/time-zone.md) 페이지에 있습니다.

## 함정과 한계

첫째, ALEAPP 모듈에는 시험 이미지 목록이 없고 [2], 앱 판이 바뀌면 이 구조가 달라질 수 있습니다. 열이 없다는 오류가 나거나 결과가 비면 표 정의부터 다시 읽습니다.

둘째, 폴더 경로를 이어 붙일 때 중간 폴더 행이 빠져 있으면 경로가 끊깁니다. 끊긴 경로를 보고서에 적을 때는 확인한 부분까지만 씁니다.

셋째, 특수 행(`search`, `Mru`, `SharedBy`, `SharedWithMe`)을 빼지 않고 세면 항목 수가 부풀려집니다 [2].

넷째, 파일을 지우면 `items` 에서 어떻게 빠지는지, 휴지통 항목이 따로 표시되는지는 실제 데이터로 확인해야 합니다. SQLite 에서 지운 행이 남을 수 있는 자리는 [삭제 데이터 복구 (Data Recovery)](../../03-techniques/analysis/data-recovery/index.md) 페이지에서 다룹니다. 계정 쪽 전체 목록과 변경 기록을 받는 절차는 [클라우드 데이터 (Google Takeout 등)](../../03-techniques/acquisition/cloud-data.md) 페이지에서 다룹니다.

다섯째, 삼성 클라우드는 시험 기기에 계정을 넣고 동기화를 켠 뒤 무엇이 생기는지 직접 봐서 확인합니다. 그 절차는 [앱 데이터 분석 (App Data Analysis)](../../03-techniques/analysis/app-data-analysis/index.md) 페이지에서 다룹니다.

## 직접 분석해 보기

### 값으로 한 번

아래는 위 구조로 만든 예시 행이고, id 모양까지 지어낸 값이라 실제 데이터의 값과 다릅니다. 파일 행의 `parentRid` 가 `R2` 이면 `resourceId` 가 `R2` 인 행을 찾고, 그 행의 `parentRid` 로 다시 올라갑니다.

```
_id  resourceId  parentRid  name        itemType  itemDate
1    R1          (없음)     root        32        0
2    R2          R1         보고서      32        1767232800000
3    R3          R2         결산.xlsx   1         1767261600000

경로   root/보고서/결산.xlsx
시각   1767261600000 ms → 1767261600 s → 2026-01-01 10:00:00 UTC (한국 시각 19:00)
```

DB 사본에서는 아래처럼 재귀 질의로 경로를 이어 붙일 수 있습니다. 위 구조 표로 만든 예시입니다.

```sql
WITH RECURSIVE path(id, rid, parent, full_path) AS (
  SELECT _id, resourceId, parentRid, name FROM items
  UNION ALL
  SELECT p.id, p.rid, i.parentRid, i.name || '/' || p.full_path
  FROM path p JOIN items i ON i.resourceId = p.parent
)
SELECT i._id, i.itemType, i.size,
       datetime(NULLIF(i.itemDate, 0) / 1000, 'unixepoch') AS item_utc,
       (SELECT full_path FROM path WHERE id = i._id
        ORDER BY length(full_path) DESC LIMIT 1) AS full_path,
       s.stream_location
FROM items i
LEFT JOIN stream_cache s ON s.parentId = i._id
WHERE i.resourceId NOT IN ('search', 'Mru', 'SharedBy', 'SharedWithMe');
```

### 공개 도구로 한 번

ALEAPP 의 Microsoft OneDrive 모듈이 `QTMetadata.db` 를 읽어 경로가 붙은 파일 목록과 캐시 경로를 보여 줍니다 [2]. 도구가 낸 경로 몇 개를 위 질의 결과와 맞춰 보고, 캐시 경로가 가리키는 파일이 추출본에 실제로 있는지 확인합니다. 그 방법은 [도구 검증 (Tool Validation)](../../03-techniques/reporting/tool-validation.md) 페이지에 있습니다.

## 교차 검증

| 함께 볼 기록 | 맞춰 볼 것 |
|---|---|
| [계정 (Accounts)](../system-account/accounts/index.md) | 원드라이브·삼성 계정을 기기에 넣고 뺀 기록 |
| [설치된 앱 (packages.xml)](../app-usage/packages/index.md) | 원드라이브 앱과 삼성 클라우드 관련 앱의 설치·업데이트 시점 |
| [앱 사용 기록 (usagestats)](../app-usage/usagestats/index.md) | 파일 시각 앞뒤로 앱을 앞에 띄운 기록 |
| [데이터 사용량 (netstats)](../network/netstats.md) | 그 시간대에 앱이 주고받은 데이터 양 |
| [삼성 갤러리 (Samsung Gallery)](../media/samsung-gallery.md) | 갤러리 사진과 클라우드 목록의 이름·크기가 맞는지 |

클라우드로 자료를 내보냈는지 따지는 흐름은 [자료를 밖으로 보냈나 (Data Exfiltration)](../../04-scenarios/exfiltration/data-exfiltration/index.md) 에 있습니다.

## 실습

NIST CFReDS 같은 공개 안드로이드 시험 이미지에 `com.microsoft.skydrive` 앱 데이터가 들어 있으면 아래 질문을 풀어 봅니다.

1. `items` 에서 `itemType` 값별 행 수는 어떻게 되고, 표에 없는 값이 있습니까?
2. 특수 행을 뺀 파일 하나를 골라 폴더 경로를 끝까지 이어 붙일 수 있습니까?
3. `stream_cache` 의 경로 가운데 추출본에 실제 파일이 있는 것은 몇 개입니까?
4. `sha1Hash` 열이 있습니까? 있다면 캐시 파일의 SHA-1 을 직접 계산해 맞춰 봅니다.

## 참고 문헌

1. ALEAPP 저장소 파일 목록 (GitHub API, git trees, recursive) — https://api.github.com/repos/abrignoni/ALEAPP/git/trees/main?recursive=1
2. ALEAPP — scripts/artifacts/microsoft_onedrive.py (Microsoft OneDrive 모듈) — https://raw.githubusercontent.com/abrignoni/ALEAPP/main/scripts/artifacts/microsoft_onedrive.py
