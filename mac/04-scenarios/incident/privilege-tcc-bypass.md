---
title: "권한 상승과 TCC 우회 흔적"
parent: "시나리오 · 침해 사고"
nav_order: 2580
---

# 권한 상승과 TCC 우회 흔적 (Privilege·TCC Bypass)

## 조사 질문

악성 코드나 침입자가 관리자 권한을 얻었는지, 그리고 사용자가 알지 못하는 사이에 개인 정보 보호 권한 (Transparency, Consent, and Control, TCC) 을 얻었는지 묻습니다. 관리자 권한은 계정·그룹 변경과 로그에서, TCC 권한은 TCC 데이터베이스의 허용 기록에서 따로 찾아야 해서 두 갈래를 나눠 봅니다. 이 페이지는 TCC 데이터베이스에서 수상한 허용을 가려내는 순서를 중심으로 다루고, 데이터베이스 구조 전체는 [개인 정보 보호 권한](../../02-artifacts/credentials/tcc/index.md) 페이지로 넘깁니다.

## 먼저 확인할 것

OS 버전에 따라 TCC 데이터베이스의 `access` 표 구조가 다릅니다 [2]. 허용 여부를 담는 칸 이름과 값 체계가 모두 바뀌어서, 버전을 모르고 쿼리를 짜면 칸이 없다는 오류가 나거나 허용 값을 잘못 읽습니다.

| macOS 버전 | `access` 표에서 읽는 칸 | 허용 값 해석(mac_apt) |
|---|---|---|
| 10.15 Catalina 이하 | `last_modified`, `service`, `client`, `client_type`, `allowed`, `prompt_count`, `indirect_object_identifier` | `allowed` 0=거부, 1=허용 |
| 11 Big Sur 이상 | `last_modified`, `service`, `client`, `client_type`, `auth_value`, `auth_reason`, `indirect_object_identifier` | `auth_value` 0=거부, 2=허용 |

출처는 mac_apt TCC 플러그인입니다 [2]. `auth_value` 의 1 과 3, `auth_reason` 값마다의 뜻, `client_type` 값의 뜻은 이 출처로 확인하지 못해서 [개인 정보 보호 권한](../../02-artifacts/credentials/tcc/index.md) 페이지를 따릅니다.

TCC 데이터베이스는 사용자별 파일과 시스템 파일 두 가지라서 둘 다 수집합니다 [2].

```
~/Library/Application Support/com.apple.TCC/TCC.db
/Library/Application Support/com.apple.TCC/TCC.db
```

전체 디스크 접근 (Full Disk Access) 권한은 시스템 쪽 파일에만 기록됩니다 [1]. 기기 관리(MDM)로 내려준 권한은 mac_apt 가 읽지 않는 별도 파일에 있어서 [2], mac_apt 결과만으로는 조직이 준 권한이 빠집니다. 그 파일은 [개인 정보 보호 권한](../../02-artifacts/credentials/tcc/index.md) 페이지에서 다룹니다.

`last_modified` 는 유닉스 시각(초)입니다 [2]. 현지 시각으로 옮기는 기준은 [시간대와 시계 설정](../../02-artifacts/system-account/time-zone.md) 에 있습니다.

## 볼 아티팩트와 순서

| 순서 | 아티팩트 | 알려 주는 것 | 링크 |
|---|---|---|---|
| 1 | 시스템 TCC 데이터베이스 | 전체 디스크 접근처럼 시스템 쪽에 기록되는 권한 | [개인 정보 보호 권한](../../02-artifacts/credentials/tcc/index.md) |
| 2 | 사용자별 TCC 데이터베이스 | 사용자마다 허용·거부한 권한과 마지막으로 바뀐 시각 | [개인 정보 보호 권한](../../02-artifacts/credentials/tcc/index.md) |
| 3 | 권한을 받은 실행 파일 | 서명 여부와 번들 정보 | [앱 번들 정보](../../02-artifacts/embedded-metadata/app-bundle.md), [서명·공증·무결성 보호](../../01-foundations/protection/codesign-notarization-sip.md) |
| 4 | 사용자 계정과 관리자 그룹 | 관리자 계정이 늘었거나 그룹 구성이 바뀌었는지 | [사용자 계정](../../02-artifacts/system-account/user-accounts/index.md) |
| 5 | 통합 로그 | 권한 판정, 관리자 권한 사용 기록 | [통합 로그에서 찾을 것](../../02-artifacts/logs/unified-log-events/index.md) |
| 6 | 프로세스 실행 기록 | 암호를 받아 확인하는 동작 같은 권한 상승 앞 단계 | [통합 로그의 프로세스 실행 기록](../../02-artifacts/execution/unified-log-process.md) |

### TCC 데이터베이스를 읽는 쿼리

사본으로 연 데이터베이스에서 먼저 `PRAGMA table_info(access);` 로 칸 이름을 보고 버전 갈래를 정한 뒤, 11 이상 갈래라면 아래처럼 읽습니다. 10.15 이하 갈래는 `auth_value`, `auth_reason` 자리에 `allowed`, `prompt_count` 를 넣습니다.

```sql
SELECT datetime(last_modified, 'unixepoch') AS last_modified_utc,
       service,
       client,
       client_type,
       auth_value,
       auth_reason,
       indirect_object_identifier
FROM access
ORDER BY last_modified;
```

SQLite 를 여는 주의점은 [SQLite 데이터베이스](../../01-foundations/data-formats/sqlite/index.md) 페이지를 따릅니다.

## 분석 흐름

1. OS 버전과 사용자 목록을 정리하고, 시스템 TCC 데이터베이스와 사용자마다의 TCC 데이터베이스를 모두 사본으로 확보합니다.
2. 칸 이름으로 버전 갈래를 정하고, 허용된 행만 추려 `last_modified` 순으로 정렬합니다.
3. 조사 시간대, 곧 [악성 코드는 어디서 들어왔나](initial-access.md) 에서 정한 유입 시각 이후에 바뀐 행을 먼저 봅니다.
4. 각 행의 `client` 가 번들 ID 모양인지 경로 모양인지 나눠 보고, 실행 파일을 찾아 서명과 번들 정보를 확인합니다. `client_type` 값의 뜻은 확인하지 못해서 이 단계의 기준으로 쓰지 않습니다.
5. 수상한 행을 가립니다. `client` 가 `/tmp` 나 `/Users/Shared` 같은 곳의 경로이거나, 서명 없는 도구에 `kTCCServiceSystemPolicyAllFiles` 가 허용된 행은 수상하게 봅니다(필자 판단).
6. 관리자 권한 쪽을 확인합니다. 관리자 그룹 구성과 새 계정은 [사용자 계정](../../02-artifacts/system-account/user-accounts/index.md) 에서, 관리자 권한 사용 기록은 [통합 로그에서 찾을 것](../../02-artifacts/logs/unified-log-events/index.md) 에서 봅니다.
7. 권한 상승 앞 단계로 사용자 암호를 받아 낸 흔적이 있는지 봅니다. 가짜 암호 창으로 받은 암호를 확인하는 동작은 [정보 탈취 악성 코드](infostealer.md) 에 정리했고, 필자 해석으로는 이 동작을 권한 상승 앞 단계로 봅니다.
8. TCC 행의 시각, 계정 변경, 실행 기록을 [타임라인](../../03-techniques/analysis/timeline/index.md) 에 올립니다.

## 흔한 오판

- **사용자 TCC 데이터베이스에 전체 디스크 접근 행이 없으니 그 권한이 없었다고 보는 경우.** 전체 디스크 접근은 시스템 쪽 파일에만 기록됩니다 [1].
- **`auth_value` 1 을 허용으로 읽는 경우.** 10.15 이하의 `allowed` 는 1 이 허용이지만, 11 이상의 `auth_value` 는 2 가 허용입니다 [2]. 두 칸의 값 체계가 달라서 칸 이름부터 확인합니다.
- **`last_modified` 를 권한을 처음 준 시각으로 쓰는 경우.** 필자 해석으로는 칸 이름대로 그 행이 마지막으로 바뀐 시각이라서, 처음 허용한 시각으로 단정하지 않습니다.
- **mac_apt 결과에 없으니 권한이 없었다고 보는 경우.** mac_apt 는 기기 관리로 내려준 권한 파일을 읽지 않습니다 [2].
- **수상한 경로의 허용 행을 곧바로 우회로 쓰는 경우.** 사용자가 직접 허용했을 수도 있어서, 같은 행의 `auth_reason` 값의 뜻을 [개인 정보 보호 권한](../../02-artifacts/credentials/tcc/index.md) 페이지에서 확인한 뒤에 씁니다. 5단계의 기준은 필자 판단이라 보고서에는 판단 근거와 함께 적습니다.
- **시스템 TCC 데이터베이스 경로를 폴더 없이 적는 경우.** 개요 글 가운데 `/Library/Application Support/com.apple.TCC.db` 처럼 폴더 이름이 빠진 표기가 있는데 [1], 도구가 실제로 읽는 경로는 `com.apple.TCC` 폴더 안의 `TCC.db` 입니다 [2].

## 보고서 문장 예

> 시스템 TCC 데이터베이스(`/Library/Application Support/com.apple.TCC/TCC.db`) `access` 표에 `service` 가 `kTCCServiceSystemPolicyAllFiles`, `client` 가 `/Users/Shared/○○` 이고 `auth_value` 가 2 인 행이 있으며, `last_modified` 는 ○○○○-○○-○○ ○○:○○:○○(UTC)입니다. 이 기록은 그 시각에 해당 실행 파일에 대한 권한 행이 허용 상태로 마지막으로 바뀌었다는 사실을 보여 주지만, 누가 어떤 방법으로 허용했는지는 `auth_reason` 과 그 시간대 기록을 확인한 뒤에 따로 적습니다.

## 함께 볼 페이지

- [개인 정보 보호 권한 (TCC)](../../02-artifacts/credentials/tcc/index.md) — 데이터베이스 구조와 값 해석 전체
- [사용자 계정 (Local Accounts)](../../02-artifacts/system-account/user-accounts/index.md) — 관리자 계정과 그룹
- [서명·공증·무결성 보호 (Code Signing·Notarization·SIP)](../../01-foundations/protection/codesign-notarization-sip.md) — 서명 확인과 SIP
- [정보 탈취 악성 코드 (Infostealer)](infostealer.md) — 가짜 암호 창과 암호 확인 흔적
- [원격 접속 침입 확인 (Remote Intrusion)](remote-intrusion.md) — 권한을 넓히기 전의 침입 경로

## 참고 문헌

1. Huntress, "Full Transparency: Controlling Apple's TCC" — https://www.huntress.com/blog/full-transparency-controlling-apples-tcc
2. mac_apt, plugins/tcc.py — https://raw.githubusercontent.com/ydkhatri/mac_apt/master/plugins/tcc.py
