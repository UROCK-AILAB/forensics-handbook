---
title: "권한 DB 구조"
parent: "개인 정보 보호 권한"
grand_parent: "아티팩트 · 자격 증명·권한"
nav_order: 1820
---

# 권한 DB 구조 (TCC.db)

TCC.db는 앱이 어떤 개인 정보 자료에 접근해도 되는지를 적어 두는 SQLite 파일이고, 핵심 기록은 `access` 표에 있으며, macOS 11부터 이 표의 열 구성이 바뀌어서 파일을 연 뒤 열 이름부터 보고 버전에 맞게 읽어야 합니다 [2][3][4].

## 무엇을 기록하나 · 왜 생기나

앱이 카메라·마이크·보호 폴더 같은 자료에 접근하려 하면 개인 정보 보호 권한 (TCC)이 허용 여부를 판단하고, 그 결과가 TCC.db에 남습니다. 파일에는 어떤 앱(client)이 어떤 자료 종류(service)에 접근을 요청했고 허용됐는지 거부됐는지가 행마다 적혀 있습니다 [1][2]. 사용자가 알림창에 답하거나 설정에서 직접 바꾼 결과뿐 아니라 시스템이나 MDM이 정한 결과도 같은 표에 들어가고, 누가 정했는지는 [권한 기록 해석](interpretation.md)에서 다룹니다.

Apple은 TCC.db 형식을 공개하지 않았습니다. 아래 구조는 공개 포렌식 도구 mac_apt·APOLLO·Aftermath의 소스가 읽는 방식에서 나온 것이라서, 도구가 읽지 않는 열과 표는 뜻이 알려져 있지 않습니다.

## 위치와 버전별 차이

TCC.db는 두 곳에 있습니다 [2][4].

| 구분 | 경로 | 비고 |
|---|---|---|
| 사용자별 | `~/Library/Application Support/com.apple.TCC/TCC.db` | 사용자 홈마다 하나씩 있고, 그 사용자에게 적용되는 권한이 남습니다 |
| 시스템 전체 | `/Library/Application Support/com.apple.TCC/TCC.db` | mac_apt는 이 파일의 기록에 사용자 이름을 "System"으로 붙입니다 [2] |

전체 디스크 접근 (Full Disk Access)처럼 모든 사용자에게 걸리는 권한은 시스템 쪽 TCC.db에 남습니다 [1]. 그래서 한 앱의 권한을 확인할 때는 사용자별 파일과 시스템 파일을 모두 열어 봅니다. mac_apt는 크기가 0인 TCC.db를 건너뛰고 [2] 결과에 아무것도 남기지 않으므로, 도구 출력에 행이 없으면 파일이 없었는지 비어 있었는지를 원본에서 확인해 기록해 둡니다.

`access` 표 구조는 macOS 11을 기준으로 두 가지로 나뉩니다. macOS 10.15 이하에는 `allowed` 열이, macOS 11 이상에는 `auth_value` 열이 있습니다. mac_apt는 `PRAGMA table_info("access")`로 열 이름을 읽어 구조를 판별하고 [2], APOLLO는 macOS 10.14·10.15(iOS 12·13)에는 `allowed`를 읽는 쿼리를, macOS 10.16(=11)·iOS 14에는 `auth_value`를 읽는 쿼리를 씁니다 [3].

| macOS | 권한 값 열 | 함께 읽는 열 | 판별 기준 |
|---|---|---|---|
| 10.15 이하 (APOLLO 쿼리는 10.14·10.15 대상) | `allowed` | `prompt_count` | `allowed` 열이 있음 |
| 11 이상 | `auth_value` | `auth_reason` | `auth_value` 열이 있음 |

### macOS 27 Golden Gate 에서 바뀐 점

macOS 27 Golden Gate 부터는 앱이 로컬 TCC 데이터베이스에 직접 접근할 수 없습니다 [6]. SUMURI 지침서는 여기에 더해 TCC.db 가 `~/Library` 밖의 보호된 시스템 위치로 옮겨졌다고 보고, 그래서 어느 앱이 어떤 권한을 받았는지는 실행 중인 맥에서 파일을 복사해 읽지 말고 디스크 이미지나 `tccutil` 로 확인하라고 합니다 [5].
macOS 27 이미지에서 앞의 두 경로에 TCC.db 가 없어도 권한 기록이 없다고 판단하지 않습니다. 이미지 안에서 `TCC.db` 이름으로 파일을 찾고, 찾은 파일도 `PRAGMA table_info("access")` 로 열 구성을 다시 확인한 뒤 읽습니다. 실행 중인 맥이 기관이 관리하는 기기라면 macOS 27 에 새로 생긴 `tccutil list` 로 지정한 서비스나 앱의 현재 권한을 볼 수 있습니다 [6]. 결정을 지우는 `tccutil reset` 은 쓰지 않습니다. `tccutil` 설명은 [전체 디스크 접근 권한](../../../03-techniques/process-acquisition/live-response/full-disk-access.md) 의 도구 절에 있습니다.

## 구조

권한 기록의 핵심 표는 `access`이고 [2][3][4], 도구들이 읽는 열은 아래와 같습니다 [2][3][4]. 열의 값을 어떻게 읽는지는 [권한 기록 해석](interpretation.md)에 있습니다.

| 열 | 10.15 이하 | 11 이상 | 담긴 내용 |
|---|---|---|---|
| `last_modified` | 읽음 | 읽음 | 그 행이 마지막으로 바뀐 시각, 유닉스 시각(1970-01-01 기준 초) |
| `service` | 읽음 | 읽음 | 자료 종류, `kTCCService`로 시작하는 문자열 |
| `client` | 읽음 | 읽음 | 권한을 받은 앱 |
| `client_type` | 읽음 | 읽음 | `client` 값의 종류 |
| `allowed` | 읽음 | 없음 | 허용 여부 |
| `prompt_count` | 읽음 | 읽지 않음 | 도구 출력 이름 Prompt_Count |
| `auth_value` | 없음 | 읽음 | 허용·거부 같은 권한 상태 |
| `auth_reason` | 없음 | 읽음 | 그 상태가 된 사유 |
| `indirect_object_identifier` | 읽음 | 읽음 | 권한에 딸린 다른 대상으로 보이는 값(뜻은 해석 페이지) |

`last_modified`는 2001년 기준인 맥 절대 시각이 아니라 유닉스 시각이고, mac_apt와 APOLLO도 `DATETIME(last_modified, 'UNIXEPOCH')`로 바꿔 읽습니다 [2][3][4]. 이 시각을 타임라인에서 어떻게 쓰는지는 [권한 변경 흔적](changes.md)에서 다룹니다.

macOS 11 이상에서 `prompt_count` 열이 아예 없어졌는지, 도구가 읽지 않을 뿐인지는 실제 파일의 열 목록으로 확인합니다. `access` 표에는 도구들이 읽지 않는 열이 더 있고 `access` 말고 다른 표도 있다고 알려져 있으니, 실제 파일에서 `.schema` 로 표와 열 이름을 확인하고, 뜻을 알 수 없는 열은 값만 옮깁니다.

## 증거로서 의미

TCC.db 한 행은 수집 시점에 어느 범위(한 사용자 또는 시스템 전체)에서 어떤 앱이 어떤 자료 종류에 대해 어떤 권한 상태였는지를 보여 줍니다. 사용자별 파일에 있는 행이면 그 홈 폴더의 사용자에게 걸린 권한이고, 시스템 파일에 있는 행이면 모든 사용자에게 걸린 권한입니다.

행이 있다고 해서 앱이 실제로 그 자료에 접근했다는 뜻은 아니고, 권한 상태가 기록됐다는 뜻까지만 말할 수 있습니다. 권한이 언제부터 그 상태였는지, 그 전에는 어땠는지도 이 파일 하나로는 알기 어렵고, 자세한 내용은 [권한 변경 흔적](changes.md)에 있습니다.

## 함정과 한계

Huntress 글은 TCC DB가 암호화돼 있다고 쓰지만 [1], mac_apt·APOLLO·Aftermath는 모두 TCC.db를 일반 SQLite로 바로 엽니다 [2][3][4]. 따라서 TCC.db는 일반 SQLite로 열어 읽으면 됩니다.

macOS 버전만 보고 쿼리를 고르면 어긋날 수 있어서, mac_apt처럼 열 이름으로 구조를 먼저 판별합니다. 도구마다 출력하는 열도 다른데, mac_apt는 10.15 이하에서 Prompt_Count를, 11 이상에서 Auth_Reason을 내보내고, 11 이상에서도 출력 열 이름은 Allowed이지만 그 값은 `auth_value`에서 0과 2만 풀어 낸 것입니다 [2]. Aftermath는 `client`·`auth_value`·`auth_reason`·`service`·`last_modified`만 읽습니다 [4]. 도구 출력만 보고 열이 없다고 판단하지 말고 원본 파일에서 열 목록을 확인합니다.

TCC.db가 무결성 보호 (SIP)로 보호되는지, 실행 중인 맥에서 읽으려면 전체 디스크 접근 권한이 필요한지는 분석하는 맥에서 복사해 보며 확인합니다. 실행 중인 시스템에서 파일을 복사할 때는 [라이브 대응](../../../03-techniques/process-acquisition/live-response/index.md)의 절차를 따르고, 복사가 실패하면 그 사실과 오류를 함께 적어 둡니다.

## 직접 분석해 보기

SQLite 파일을 헥스로 따라가며 레코드를 읽는 방법은 [SQLite 데이터베이스](../../../01-foundations/data-formats/sqlite/index.md)에 있어서 여기서는 되풀이하지 않고, 이 페이지는 SQL로 구조를 확인하는 데까지 다룹니다. 원본이 아니라 사본을 엽니다.

먼저 열 이름으로 구조를 판별합니다 [2].

```sh
sqlite3 TCC.db 'PRAGMA table_info("access");'
```

`auth_value`가 보이면 macOS 11 이상 구조라서 아래처럼 읽습니다. 열 목록은 도구들이 읽는 열을 모았고, 시각 변환은 mac_apt·APOLLO와 같습니다 [2][3][4].

```sql
SELECT DATETIME(last_modified, 'UNIXEPOCH') AS last_modified_utc,
       service, client, client_type, auth_value, auth_reason,
       indirect_object_identifier
FROM access
ORDER BY last_modified DESC;
```

`allowed`가 보이면 macOS 10.15 이하 구조라서 `auth_value, auth_reason` 자리에 `allowed, prompt_count`를 넣습니다 [2][3].

공개 도구로는 아래 셋이 이 파일을 읽습니다.

| 도구 | 읽는 방식 | 출력 |
|---|---|---|
| mac_apt `TCC` 플러그인 (Minoru Kobayashi, 2022) | 사용자별·시스템 파일을 모두 읽고 열 이름으로 구조 판별 | Last_Modified·Service·Client·Client_Type·Allowed·Auth_Reason(10.15 이하는 Prompt_Count)·Indirect_Object_Identifier·User·Source [2] |
| APOLLO `tcc_db` 모듈 (Sarah Edwards) | 버전별 쿼리 두 개 | 기준 시각은 LAST MODIFIED [3] |
| Jamf Aftermath `parseTCC()` | `select client, auth_value, auth_reason, service, last_modified from access order by last_modified desc` | `tcc.csv` [4] |

## 교차 검증

- [권한 기록 해석 (Services·auth_value)](interpretation.md) — 각 열 값의 뜻
- [권한 변경 흔적 (Changes)](changes.md) — `last_modified`로 권한이 바뀐 때를 읽을 때
- [사용자 계정 (Local Accounts)](../../system-account/user-accounts/index.md) — 사용자별 TCC.db가 어느 계정의 것인지 확인할 때
- [OS 버전과 설치 기록 (SystemVersion·InstallHistory)](../../system-account/os-version-install-history.md) — 열 구성과 macOS 버전이 맞는지 볼 때
- [맥의 시각 값 (Mac Absolute Time·Unix·HFS)](../../../01-foundations/value-decoding/mac-time-values.md)

## 실습

공개 데이터셋이나 직접 준비한 시험용 맥 이미지에서 아래 질문을 풀어 봅니다.

1. 이미지 안에 TCC.db가 몇 개 있고, 각각 어느 사용자의 것인지 또는 시스템 전체의 것인지 구분해 봅니다.
2. `PRAGMA table_info("access")` 결과로 이 파일이 10.15 이하 구조인지 11 이상 구조인지 판별하고, 이미지의 macOS 버전과 맞는지 확인합니다.
3. 같은 파일을 mac_apt와 SQL로 각각 읽어 행 수와 열이 같은지 비교합니다.

## 참고 문헌

1. Huntress, "Full Transparency: Controlling Apple's TCC" — https://www.huntress.com/blog/full-transparency-controlling-apples-tcc
2. mac_apt TCC 플러그인 소스 tcc.py (Minoru Kobayashi, 2022) — https://github.com/ydkhatri/mac_apt/blob/master/plugins/tcc.py
3. APOLLO 모듈 tcc_db.txt (Sarah Edwards, mac4n6) — https://github.com/mac4n6/APOLLO/blob/master/modules/tcc_db.txt
4. Jamf Aftermath 소스 analysis/DatabaseParser.swift — https://github.com/jamf/aftermath/blob/main/analysis/DatabaseParser.swift
5. SUMURI, Mac Forensics Best Practices Guide, 2026 Edition (2026-09) — https://sumuri.com/
6. Apple Support, "What's new for enterprise in macOS Golden Gate 27" (2026-09-14) — https://support.apple.com/en-us/148830
