---
title: "계정 plist 구조"
parent: "사용자 계정"
grand_parent: "아티팩트 · 시스템·계정"
nav_order: 490
---

# 계정 plist 구조 (dslocal)

계정 plist 는 로컬 사용자마다 하나씩 `/private/var/db/dslocal/nodes/Default/users/` 폴더에 놓이는 속성 목록 파일이고, 이름·UID·UUID·홈 폴더와 함께 계정을 만든 시각, 로그인 실패 횟수와 시각, 암호를 마지막으로 설정한 시각까지 한 파일에서 읽을 수 있습니다 [1][3].

## 무엇을 기록하나 · 왜 생기나

macOS 는 로컬 사용자 계정 정보를 사용자마다 plist 하나로 나눠 저장하고, 파일 이름이 곧 사용자 이름입니다 [1]. 같은 파일 안에 암호 정책 값과 로그인 암호 해시도 함께 들어 있습니다 [1][3][5].

이 페이지는 파일의 위치와 키 구성, 시각 값을 다룹니다. 로그인 암호 해시는 [암호 해시 (ShadowHashData)](shadowhashdata.md)에서, 관리자 여부와 볼륨 소유자 구분은 [관리자와 그룹 소속 (admin·Groups)](admin-groups.md)에서, 이미 지워 파일이 없는 계정은 [지운 계정의 흔적 (Deleted Accounts)](deleted-accounts.md)에서 다룹니다.

## 위치와 버전별 차이

```
/private/var/db/dslocal/nodes/Default/users/<계정이름>.plist
```

`/var` 는 `/private/var` 로 이어지는 경로라서 자료에 따라 `/var/db/...` 로도 적습니다 [5]. 같은 `Default` 폴더에는 `sqlindex` 라는 디렉터리 서비스 (Directory Services) 로컬 노드 데이터베이스도 있고, 이 파일은 SQLite 데이터베이스입니다 [5]. `sqlindex` 가 계정 plist 의 색인인지 캐시인지, 안의 구조가 어떤지는 실제 데이터로 확인해야 합니다.

계정 plist 는 바이너리 plist 일 수도 XML plist 일 수도 있으니 실제 파일에서 형식부터 봅니다. 두 형식을 읽는 법은 [속성 목록 파일 (Property List)](../../../01-foundations/data-formats/plist/index.md)에 있습니다.

버전에 따라 암호 정책을 담는 키가 다릅니다 [1][3].

| macOS | 암호 정책 키 | 형태 | 출처 |
|---|---|---|---|
| 10.9 이전 | `passwordpolicyoptions` | XML 정책 구조 | [1] |
| 10.10 Yosemite 이후 (10.15 Catalina 이후 포함) | `accountPolicyData` | 데이터 안에 plist 가 한 번 더 들어 있음 | [3] |

경계는 mac_apt 코드가 `passwordpolicyoptions` 를 "Mavericks & earlier", `accountPolicyData` 를 "10.10 - Yosemite & higher" 로 나눠 읽는 데서 왔습니다 [3]. 도구 코드의 구분이고 Apple 이 밝힌 경계는 아닙니다. Catalina 이후 버전끼리도 키 구성이 다를 수 있어 실제 데이터로 확인합니다.

## 구조

### 계정 plist 의 키

아래 키는 plaso 와 mac_apt 가 실제로 읽는 키입니다. mac_apt 출력 열 이름을 함께 적어서 도구 결과와 원본 키를 짝지을 수 있게 했습니다 [1][2][3].

| 키 | 내용 | mac_apt 출력 열 | 출처 |
|---|---|---|---|
| `name` | 사용자 이름 | Username | [1][3] |
| `realname` | 전체 이름 | Realname | [1][3] |
| `home` | 홈 폴더 경로 | Homedir | [1][3] |
| `uid` | UID | UID | [1][3] |
| `gid` | GID | GID | [3] |
| `generateduid` | 계정 UUID | UUID | [2][3] |
| `hint` | 암호 힌트 | PasswordHint | [2][3] |
| `passwordpolicyoptions` | 옛 방식 암호 정책 | (시각 열들) | [1][3] |
| `accountPolicyData` | 10.10 이후 암호 정책 | CreationDate 등 | [3] |
| `ShadowHashData` | 로그인 암호 해시 | 없음 | [1][5] |

plaso 는 `home`, `name`, `passwordpolicyoptions`, `ShadowHashData`, `uid` 다섯 키가 함께 있는 plist 를 계정 plist 로 알아보고, 그 밖에 `realname` 도 읽습니다 [1]. UID·UUID 값을 읽는 법은 [식별자 읽기 (UUID·UID·GUID)](../../../01-foundations/value-decoding/uuid-uid.md)에 있습니다.

키 값은 배열 안에 들어 있고, 값은 배열의 첫 원소(`[0]`)에서 꺼냅니다 [3]. 모든 키가 배열로 저장된다는 일반 규칙은 알려져 있지 않으니, 키마다 값이 배열인지 먼저 봅니다.

### accountPolicyData 안의 값 (10.10 이후)

`accountPolicyData` 는 데이터 값이고, 그 안에 plist 가 한 번 더 들어 있습니다. 안쪽 plist 에는 아래 네 값이 있습니다 [3].

| 안쪽 키 | 뜻 (키·출력 열 이름으로 읽은 것) | mac_apt 출력 열 |
|---|---|---|
| `creationTime` | 계정을 만든 시각 | CreationDate |
| `failedLoginCount` | 로그인 실패 횟수 | FailedLoginCount |
| `failedLoginTimestamp` | 로그인에 실패한 시각 | FailedLoginTime |
| `passwordLastSetTime` | 암호를 마지막으로 설정한 시각 | PasswordLastSetTime |

mac_apt 출력에는 LastLoginTime 열도 있지만 [2], mac_apt 는 `lastLoginTimestamp` 를 옛 방식 `passwordpolicyoptions` 에서만 읽고 `accountPolicyData` 에서는 읽지 않습니다 [3]. 그래서 10.10 이후 이미지에서 이 열이 비어 나오는 것은 도구 동작 때문입니다. `accountPolicyData` 안에 마지막 로그인 시각이 따로 있는지는 실제 데이터로 확인해야 합니다.

### passwordpolicyoptions 안의 값 (옛 방식)

옛 방식에는 `lastLoginTimestamp`(마지막 인증), `failedLoginTimestamp`(마지막 실패), `passwordLastSetTime`(마지막 암호 변경) 세 시각이 있습니다 [1]. Catalina 이후 계정 plist 에 이 키가 남는지는 기기마다 다를 수 있고, 오래된 백업이나 옛 버전 이미지를 볼 때는 이 세 값을 찾습니다.

### Darwin 사용자 폴더와의 연결

`/private/var/folders` 아래에서 UID·GID 가 계정과 맞는 폴더가 그 계정의 Darwin 폴더이고, 그 아래 `/0` 이 DARWIN_USER_DIR, `/C` 가 캐시 폴더, `/T` 가 임시 폴더입니다 [3]. 계정 plist 에는 이 폴더 경로가 들어 있지 않고, UID·GID 를 맞춰 봐야 연결됩니다.

### 보안 토큰과 AuthenticationAuthority

보안 토큰 (Secure Token) 은 계정의 `AuthenticationAuthority` 속성과 이어집니다. 프로그램으로 만든 사용자가 보안 토큰을 받지 않게 하려면 암호를 정하기 전에 이 속성에 `;DisabledTags;SecureToken` 을 더합니다 [4]. 보안 토큰을 가진 계정에 이 속성이 어떤 값으로 적히는지와, 이 속성이 계정 plist 에서 어떤 키 이름으로 저장되는지는 실제 데이터로 확인해야 합니다. 보안 토큰은 사용자 암호로 보호되는 키 암호화 키 (KEK) 를 감싼 값이고, Apple silicon Mac 에서는 처음 설정한 사용자가 보안 토큰을 받고 첫 볼륨 소유자가 됩니다 [4]. `sysadminctl` 로 보안 토큰 상태를 바꿀 수 있어서 [4], 수집 시점의 속성 값이 처음부터 그 상태였다고 보지는 않습니다.

## 증거로서 의미

**증명하는 것.** 계정 plist 가 있으면 수집 시점에 그 이름·UID·UUID·홈 폴더를 쓰는 로컬 계정이 이 Mac 에 있었다는 뜻입니다 [1][3]. 10.10 이후라면 `accountPolicyData` 에서 계정을 만든 시각, 로그인 실패 횟수와 그 시각, 암호를 마지막으로 설정한 시각의 기록을 읽을 수 있습니다 [3].

**증명하지 못하는 것.** 계정이 있다는 기록만으로는 그 계정을 누가 썼는지 알 수 없습니다. 로그인 실패 기록에는 횟수와 시각만 있어서 어디서 어떤 방법으로 실패했는지는 다른 기록으로 확인해야 합니다. 10.10 이후 계정 plist 에서 마지막 로그인 시각을 읽는 방법은 알려져 있지 않으니 [3], 이 파일을 마지막 로그인의 근거로 쓰지 않습니다. 파일이 없다고 해서 그 계정이 없었다고 볼 수도 없고, 이런 경우는 [지운 계정의 흔적 (Deleted Accounts)](deleted-accounts.md)을 봅니다.

보고서에는 "`/private/var/db/dslocal/nodes/Default/users/` 에 이 이름의 계정 plist 가 있고, `accountPolicyData` 의 `creationTime` 값은 이 시각(UTC)이다" 처럼 기록으로 확인되는 만큼만 씁니다.

## 시각 해석

`accountPolicyData` 안의 시각은 1970-01-01 기준 초인 유닉스 시각입니다 [3]. 유닉스 시각이라서 UTC 기준이고, 현지 시각은 [시간대와 시계 설정 (Time Zone·NTP)](../time-zone.md)을 보고 따로 바꿉니다. 값은 정수일 수도 소수점 아래까지 있는 실수일 수도 있으니 실제 데이터로 확인합니다.

옛 방식 `passwordpolicyoptions` 에서는 값이 0 으로 초기화돼 있으면 라이브러리가 2001-01-01 00:00:00(Cocoa 기준 시각 0)으로 읽는데, 이 값은 "없음" 을 뜻합니다 [1]. 다른 도구가 이 날짜를 보여 주면 실제 사건 시각이 아니라 빈 값일 수 있습니다. 두 기준 시각을 바꾸는 법은 [맥의 시각 값 (Mac Absolute Time·Unix·HFS)](../../../01-foundations/value-decoding/mac-time-values.md)에 있습니다.

각 시각이 어떤 동작에서 갱신되는지는 공개된 설명이 없고, 위의 뜻은 키 이름과 도구 출력 열 이름에 따른 것입니다.

## 함정과 한계

- **시스템 계정.** mac_apt 는 이름이 `_` 로 시작하는 plist 를 홈 폴더 없는 시스템 사용자일 가능성이 크다고 보고 건너뛰고 [3], USERS 플러그인은 UUID 가 `FFFFEEEE` 로 시작하면 시스템 계정으로 봅니다 [2]. 두 기준 모두 도구의 판단이라서 Apple 문서로 확인한 규칙으로 인용하지 않습니다.
- **배열로 싼 값.** mac_apt 는 배열의 첫 원소만 꺼내 쓰지만 [3], 배열에 원소가 둘 이상 들어 있을 수도 있습니다. 손으로 읽을 때는 배열 전체를 보고 원소 개수도 적어 둡니다.
- **마지막 로그인 시각.** mac_apt 의 LastLoginTime 열은 옛 방식 `passwordpolicyoptions` 의 `lastLoginTimestamp` 에서만 채워집니다 [3]. 10.10 이후 이미지에서 이 열이 비어 있다고 로그인한 적이 없다고 보지 않고, 채워져 있으면 어느 원본 키에서 왔는지 확인합니다.
- **sqlindex 와 어긋날 때.** `sqlindex` 와 계정 plist 의 관계는 알려져 있지 않으니, 두 곳의 내용이 다르면 어느 쪽이 맞다고 판단하지 말고 둘 다 기록합니다.
- **파일을 고친 흔적.** 계정 plist 를 직접 고치면 어디에 어떤 흔적이 남는지는 공개 자료로 정리돼 있지 않습니다. [파일 시스템 이벤트 (FSEvents)](../../filesystem/fsevents/index.md)의 해당 경로 기록과 [스냅숏과 백업 비교 (Snapshot·Time Machine Diff)](../../../03-techniques/analysis/snapshot-diff.md)로 이전 사본과 비교해 봅니다.

## 직접 분석해 보기

### 값으로 한 번

계정 plist 는 바이너리일 수도 XML 일 수도 있어서, 여기서는 값을 손으로 풀어 보는 순서를 적습니다. 아래 숫자는 명세로 만든 예시이고, 실제 데이터에서 나온 값이 아닙니다.

1. 수집한 사본에서 `users` 폴더의 plist 를 plist 도구로 엽니다. 파일 이름과 `name` 값이 같은지 먼저 봅니다 [1].
2. `uid`, `generateduid`, `home` 을 읽습니다. 값이 배열이면 첫 원소를 꺼냅니다 [3].
3. `accountPolicyData` 의 첫 원소를 꺼내면 데이터 값이고, 이 데이터를 plist 로 한 번 더 엽니다 [3].
4. 안쪽 plist 에서 `passwordLastSetTime` 이 1704067200 이라면 유닉스 시각으로 2024-01-01 00:00:00 UTC 입니다.
5. `/private/var/folders` 아래에서 같은 UID·GID 의 폴더를 찾아 `/0`, `/C`, `/T` 를 이 계정과 잇습니다 [3].

### 공개 도구로 한 번

mac_apt USERS 플러그인은 로컬·도메인 사용자의 이름, UID, UUID, GID, 홈 폴더, Darwin 폴더, 자동 로그인 저장 암호, 지운 사용자 정보를 한 표로 냅니다 [2]. plaso 의 `macos_user` plist 플러그인은 계정 plist 를 알아보고 옛 방식 정책의 세 시각을 사건으로 냅니다 [1]. 두 도구가 읽는 키가 다르니, 같은 계정의 같은 시각이 두 도구에서 어떻게 나오는지 나란히 놓고 봅니다.

## 교차 검증

| 함께 볼 아티팩트 | 맞춰 볼 것 |
|---|---|
| [암호 해시 (ShadowHashData)](shadowhashdata.md) | 해시가 바뀐 시점과 `passwordLastSetTime` |
| [관리자와 그룹 소속 (admin·Groups)](admin-groups.md) | `AuthenticationAuthority` 값과 볼륨 소유자·관리자 여부 |
| [지운 계정의 흔적 (Deleted Accounts)](deleted-accounts.md) | 지금 없는 UID·이름이 지운 계정 기록에 있는지 |
| [로그인 창 설정 (loginwindow)](../loginwindow.md) | 자동 로그인 계정·마지막 로그인 사용자와 계정 이름 |
| [파일볼트 (FileVault)](../../../01-foundations/protection/filevault/index.md) | 보안 토큰이 있는 계정과 볼륨 잠금 해제 |
| [파일 시스템 이벤트 (FSEvents)](../../filesystem/fsevents/index.md) | 계정 plist 와 홈 폴더가 생긴 시각 |

## 실습

공개 시험 자료(NIST CFReDS 등)의 macOS 이미지로 풀어 봅니다.

1. `users` 폴더에서 이름이 `_` 로 시작하지 않는 plist 를 모두 찾고, 각 계정의 UID·UUID·홈 폴더를 표로 적어 보세요.
2. 한 계정의 `accountPolicyData` 를 손으로 풀어 네 값을 UTC 와 현지 시각으로 적고, mac_apt 결과와 비교해 보세요.
3. `creationTime` 과 홈 폴더가 생긴 시각을 나란히 놓고 차이가 있는지 확인해 보세요.
4. `/private/var/folders` 에서 각 계정의 Darwin 폴더를 UID·GID 로 찾아 보세요.

## 참고 문헌

1. plaso `macos_user` plist 플러그인 소스 — https://raw.githubusercontent.com/log2timeline/plaso/main/plaso/parsers/plist_plugins/macos_user.py
2. mac_apt `USERS` 플러그인 소스 (Yogesh Khatri) — https://raw.githubusercontent.com/ydkhatri/mac_apt/master/plugins/users.py
3. mac_apt `macinfo.py` 헬퍼 소스 (`_GetUserInfo`) — https://raw.githubusercontent.com/ydkhatri/mac_apt/master/plugins/helpers/macinfo.py
4. Apple Platform Deployment, Use secure token, bootstrap token and volume ownership in deployments — https://support.apple.com/guide/deployment/use-secure-and-bootstrap-tokens-dep24dbdcf9e/web
5. ForensicArtifacts `macos.yaml` (MacOSUserPasswordHashesPlistFile, MacOSDirectoryServicesLocalNodesSQLiteDatabaseFile) — https://raw.githubusercontent.com/ForensicArtifacts/artifacts/main/artifacts/data/macos.yaml
