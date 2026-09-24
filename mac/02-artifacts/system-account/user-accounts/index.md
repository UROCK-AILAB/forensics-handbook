---
title: "사용자 계정"
parent: "아티팩트 · 시스템·계정"
nav_order: 480
has_children: true
has_toc: false
---

# 사용자 계정 (Local Accounts)

macOS 의 로컬 사용자 계정 정보는 사용자마다 plist 하나로 `/private/var/db/dslocal/nodes/Default/users/` 에 들어 있고, 이 파일과 몇몇 설정 파일에서 계정의 이름·UID·만든 시각·암호 해시와 지운 계정의 기록을 찾습니다 [1][3][6].

## 왜 중요한가

사용자별 흔적은 대부분 홈 폴더(`/Users/*`) 아래에 쌓이고 [7], `/private/var/folders` 의 Darwin 폴더처럼 이름 대신 UID 로만 계정과 이어지는 기록도 있습니다 [3]. 그래서 조사 초반에 계정 목록을 만들어 이름·UID·UUID·홈 폴더를 짝지어 두면, 뒤에서 만나는 흔적마다 어느 계정의 것인지 바로 이을 수 있습니다. 계정 plist 에는 계정을 만든 시각과 암호를 마지막으로 설정한 시각, 로그인 실패 기록도 들어 있어서 [3] 계정이 언제 생기고 어떻게 쓰였는지 따지는 출발점이 됩니다.

지금은 없는 계정도 조사 대상입니다. 계정을 지운 기록과 지울 때 남긴 홈 폴더가 따로 남을 수 있고 [2][5], 볼륨 소유자 (Volume Owner) 인지 관리자인지는 따로 정해져서 [4] 계정 권한을 판단할 때 둘 다 확인합니다.

공개 도구로는 plaso 의 `macos_user` plist 플러그인 [1] 과 mac_apt 의 `USERS` 플러그인 [2] 이 있습니다. mac_apt 는 로컬·도메인 사용자의 이름, UID, UUID, GID, 홈 폴더, Darwin 폴더, 자동 로그인 저장 암호, 지운 사용자 정보를 한 표로 냅니다 [2].

## 한눈에 보기

| 위치 | macOS 버전 | 알려 주는 것 |
|---|---|---|
| `/private/var/db/dslocal/nodes/Default/users/*.plist` | 암호 정책 키가 10.10 Yosemite 이후 `accountPolicyData`, 그 전 `passwordpolicyoptions` [1][3] | 이름·UID·UUID·홈 폴더·만든 시각·로그인 실패·암호 설정 시각·로그인 암호 해시 [1][3][6] |
| `/private/var/db/dslocal/nodes/Default/sqlindex` | 확인 못 함 | 디렉터리 서비스 (Directory Services) 로컬 노드 데이터베이스, 계정 plist 와의 관계는 확인 못 함 [6] |
| `/Library/Preferences/com.apple.preferences.accounts.plist` | 기록되기 시작한 버전 확인 못 함 | `deletedUsers` 에 지운 계정의 이름·UID·지운 시각 [2] |
| `/Users/Deleted Users/` | 최신 macOS 지원 문서로 확인 [5] | 계정을 지울 때 디스크 이미지로 남긴 홈 폴더 [5] |
| `/Library/Preferences/com.apple.loginwindow.plist` | 마지막 로그인 사용자는 10.9 자료로 확인 [7] | 자동 로그인 계정 `autoLoginUser` [2], 마지막 로그인 사용자 [7] |
| `/private/etc/kcpassword` | 확인 못 함 | 자동 로그인 암호를 되돌릴 수 있는 형태로 가려 저장한 파일 [2] |
| `/private/var/folders/` | 확인 못 함 | UID·GID 로 계정과 이어지는 Darwin 사용자 폴더 [3] |

`/private/var/...` 경로는 자료에 따라 `/var/...` 로도 적습니다 [6][7]. 로그인 창 설정과 자동 로그인 파일은 [로그인 창 설정 (loginwindow)](../loginwindow.md)에서 다룹니다.

## 읽는 순서

1. [계정 plist 구조 (dslocal)](dslocal-plist.md) — 계정 plist 의 위치와 키, `accountPolicyData` 안의 시각 값, Darwin 폴더와 보안 토큰 관련 속성을 읽는 법을 다룹니다.
2. [암호 해시 (ShadowHashData)](shadowhashdata.md) — 로그인 암호 해시가 남는 모양과, 해시가 바뀐 시점을 암호 설정 시각과 맞춰 보는 법을 다룹니다.
3. [관리자와 그룹 소속 (admin·Groups)](admin-groups.md) — 관리자 여부와 볼륨 소유자·보안 토큰 여부를 나눠 확인하는 법과 부트스트랩 토큰을 다룹니다.
4. [지운 계정의 흔적 (Deleted Accounts)](deleted-accounts.md) — `deletedUsers` 기록과 `/Users/Deleted Users/` 의 디스크 이미지, 계정 plist 가 사라진 뒤 찾아볼 자리를 다룹니다.

## 함께 볼 페이지

- [로그인 창 설정 (loginwindow)](../loginwindow.md) — 자동 로그인 계정과 마지막 로그인 사용자
- [속성 목록 파일 (Property List)](../../../01-foundations/data-formats/plist/index.md) — 계정 plist 를 여는 법
- [식별자 읽기 (UUID·UID·GUID)](../../../01-foundations/value-decoding/uuid-uid.md) — UID·UUID 로 계정을 잇는 법
- [맥의 시각 값 (Mac Absolute Time·Unix·HFS)](../../../01-foundations/value-decoding/mac-time-values.md) — 계정 시각 값을 풀 때
- [파일볼트 (FileVault)](../../../01-foundations/protection/filevault/index.md) — 보안 토큰과 볼륨 잠금 해제
- [그 시각에 맥을 쓴 사람이 누구인가 (User Attribution)](../../../04-scenarios/activity/user-attribution.md)
- [권한 상승과 TCC 우회 흔적 (Privilege·TCC Bypass)](../../../04-scenarios/incident/privilege-tcc-bypass.md)

## 참고 문헌

1. plaso `macos_user` plist 플러그인 소스 — https://raw.githubusercontent.com/log2timeline/plaso/main/plaso/parsers/plist_plugins/macos_user.py
2. mac_apt `USERS` 플러그인 소스 (Yogesh Khatri) — https://raw.githubusercontent.com/ydkhatri/mac_apt/master/plugins/users.py
3. mac_apt `macinfo.py` 헬퍼 소스 (`_GetUserInfo`) — https://raw.githubusercontent.com/ydkhatri/mac_apt/master/plugins/helpers/macinfo.py
4. Apple Platform Deployment, Use secure token, bootstrap token and volume ownership in deployments — https://support.apple.com/guide/deployment/use-secure-and-bootstrap-tokens-dep24dbdcf9e/web
5. Apple 지원, Mac 사용 설명서 — Delete a user or group on Mac — https://support.apple.com/guide/mac-help/delete-a-user-or-group-mchlp1557/mac
6. ForensicArtifacts `macos.yaml` (MacOSUserPasswordHashesPlistFile, MacOSDirectoryServicesLocalNodesSQLiteDatabaseFile, MacOSLoginWindowPlistFile) — https://raw.githubusercontent.com/ForensicArtifacts/artifacts/main/artifacts/data/macos.yaml
7. Forensics Wiki, Mac OS X 10.9 artifacts location — https://forensics.wiki/mac_os_x_10.9_artifacts_location/
