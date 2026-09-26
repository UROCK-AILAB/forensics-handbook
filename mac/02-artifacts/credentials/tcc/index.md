---
title: "개인 정보 보호 권한"
parent: "아티팩트 · 자격 증명·권한"
nav_order: 1810
has_children: true
has_toc: false
---

# 개인 정보 보호 권한 (TCC)

개인 정보 보호 권한 (TCC)은 앱이 카메라·마이크·화면·보호 폴더 같은 자료에 접근해도 되는지를 판단하는 macOS의 권한 체계이고, 어떤 앱이 어떤 자료 종류에 접근을 요청해 허용됐는지 거부됐는지가 사용자별·시스템 전체 `TCC.db` 두 SQLite 파일에 남습니다 [1][2].

## 왜 중요한가

TCC.db를 보면 화면 기록·입력 모니터링·손쉬운 사용·전체 디스크 접근 (Full Disk Access)처럼 남용되면 피해가 큰 권한을 어느 앱이 받았는지 한 표에서 확인할 수 있습니다. 공개 도구 Jamf Aftermath도 소스에서 이런 서비스들을 "critical"·"common"으로 따로 묶어 두고 있어서 [5], 침해 사고 조사에서 악성 코드나 원격 접속 도구가 권한을 얻었는지 가릴 때 먼저 여는 자료가 됩니다.

macOS 11부터는 권한 상태뿐 아니라 그 상태를 사용자·시스템·MDM 가운데 누가 정했는지도 남습니다 [2][5]. 기업 맥에서는 MDM이 사용자에게 묻지 않고 PPPC 프로파일로 권한을 미리 주기 때문에 [1][3], 사용자가 직접 허용한 권한과 조직이 내려준 권한을 나눠 읽어야 합니다.

Apple은 TCC.db 형식을 공개하지 않았고, 이 절의 페이지들은 공개 포렌식 도구 mac_apt·APOLLO·Aftermath의 소스와 Apple의 PPPC 프로파일 스키마를 근거로 씁니다. 도구가 읽지 않는 열과 값은 확인한 범위를 밝히고 다룹니다.

## 한눈에 보기

| 항목 | 내용 |
|---|---|
| 위치 (사용자별) | `~/Library/Application Support/com.apple.TCC/TCC.db` [2] |
| 위치 (시스템 전체) | `/Library/Application Support/com.apple.TCC/TCC.db`, 전체 디스크 접근처럼 모든 사용자에게 걸리는 권한이 남음 [1][2]. Huntress 글에 적힌 시스템 쪽 경로는 파일 이름이 빠진 형태라서 경로는 mac_apt 소스를 따름 |
| 형식 | 일반 SQLite, 핵심 표는 `access` [2][4][5] |
| macOS 버전 | 10.15 이하는 `allowed` 열, 11 이상은 `auth_value`·`auth_reason` 열 [2][4] |
| MDM 권한 | PPPC 프로파일 `com.apple.TCC.configuration-profile-policy`, macOS 10.14부터 [3] |
| 알려 주는 것 | 앱(client)과 자료 종류(service)별 권한 상태, 그 행이 마지막으로 바뀐 시각(유닉스 시각), 11 이상은 상태를 정한 사유 [2][4][5] |
| 알려 주지 않는 것 | 앱이 실제로 자료에 접근했는지, 권한의 지난 이력, 누가 알림창에 답했는지 |
| 공개 도구 | mac_apt `TCC` 플러그인 [2], APOLLO `tcc_db` 모듈 [4], Jamf Aftermath [5] |

TCC.db가 암호화돼 있다는 설명도 있지만 공개 도구들은 모두 일반 SQLite로 바로 열고, 이 차이는 [권한 DB 구조](tcc-db.md)에서 다룹니다.

## 읽는 순서

1. [권한 DB 구조 (TCC.db)](tcc-db.md) — 두 파일의 위치, `access` 표의 열 구성과 macOS 11 전후 구조를 열 이름으로 구분하는 법, 공개 도구와 SQL로 읽는 법을 다룹니다.
2. [권한 기록 해석 (Services·auth_value)](interpretation.md) — `auth_value`·`auth_reason` 숫자 값의 이름, `kTCCService` 서비스 이름과 PPPC 도입 버전, 도구 출력에서 값이 빠지는 함정을 다룹니다.
3. [권한 변경 흔적 (Changes)](changes.md) — `last_modified`로 권한이 바뀐 때를 읽는 법, MDM이 준 권한을 PPPC 프로파일과 대조하는 법, 사고 대응에서 먼저 볼 행을 다룹니다.

## 함께 볼 페이지

- [SQLite 데이터베이스 (SQLite)](../../../01-foundations/data-formats/sqlite/index.md) — TCC.db의 저장 형식
- [구성 프로파일 (Configuration Profiles·MDM)](../../persistence/configuration-profiles.md) — PPPC 프로파일이 설치된 흔적
- [서명·공증·무결성 보호 (Code Signing·Notarization·SIP)](../../../01-foundations/protection/codesign-notarization-sip.md) — 권한을 받은 앱의 서명을 확인할 때
- [원격 접속 (Remote Access)](../../network/remote-access/index.md)
- [권한 상승과 TCC 우회 흔적 (Privilege·TCC Bypass)](../../../04-scenarios/incident/privilege-tcc-bypass.md)
- [정보 탈취 악성 코드 (Infostealer)](../../../04-scenarios/incident/infostealer.md)

## 참고 문헌

1. Huntress, "Full Transparency: Controlling Apple's TCC" — https://www.huntress.com/blog/full-transparency-controlling-apples-tcc
2. mac_apt TCC 플러그인 소스 tcc.py (Minoru Kobayashi, 2022) — https://github.com/ydkhatri/mac_apt/blob/master/plugins/tcc.py
3. Apple device-management 저장소, PPPC 프로파일 스키마 com.apple.TCC.configuration-profile-policy.yaml — https://raw.githubusercontent.com/apple/device-management/release/mdm/profiles/com.apple.TCC.configuration-profile-policy.yaml
4. APOLLO 모듈 tcc_db.txt (Sarah Edwards, mac4n6) — https://github.com/mac4n6/APOLLO/blob/master/modules/tcc_db.txt
5. Jamf Aftermath 소스 analysis/DatabaseParser.swift — https://github.com/jamf/aftermath/blob/main/analysis/DatabaseParser.swift
