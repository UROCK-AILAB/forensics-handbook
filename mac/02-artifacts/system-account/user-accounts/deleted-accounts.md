---
title: "지운 계정의 흔적"
parent: "사용자 계정"
grand_parent: "아티팩트 · 시스템·계정"
nav_order: 520
---

# 지운 계정의 흔적 (Deleted Accounts)

로컬 계정을 지우면 `/Library/Preferences/com.apple.preferences.accounts.plist` 의 `deletedUsers` 에 그 계정의 이름·전체 이름·UID·지운 시각이 남고, 지울 때 홈 폴더를 디스크 이미지로 저장하기로 했다면 `/Users/Deleted Users/` 에 그 이미지가 놓입니다 [1][2].

## 무엇을 기록하나 · 왜 생기나

계정을 지우면 계정 plist 가 사라지고, [계정 plist 구조 (dslocal)](dslocal-plist.md)에서 다룬 이름·UID·시각도 함께 없어집니다. 그 뒤에 계정이 있었다는 사실을 보여 주는 기록으로는 두 가지를 확인했습니다. 하나는 시스템 설정 파일의 `deletedUsers` 항목이고 [1], 다른 하나는 지울 때 고른 선택지에 따라 남는 홈 폴더입니다 [2].

시스템 설정에서 사용자를 지울 때는 홈 폴더를 어떻게 할지 세 가지 가운데 하나를 고릅니다 [2].

| 선택지 | 남는 것 | 출처 |
|---|---|---|
| 홈 폴더를 디스크 이미지로 저장 | `/Users/Deleted Users/` 에 디스크 이미지가 놓임 | [2] |
| 홈 폴더를 바꾸지 않음 | 사용자 문서와 정보를 보존해 나중에 복원할 수 있음 | [2] |
| 홈 폴더 삭제 | 홈 폴더를 지움 | [2] |

디스크 이미지의 파일 이름 규칙과, "바꾸지 않음" 을 골랐을 때 폴더 이름에 표시가 붙는지는 확인하지 못했습니다. 디스크 이미지를 여는 법은 [디스크 이미지 형식 (DMG·Sparsebundle)](../../../01-foundations/disk-volume/dmg-sparsebundle.md)에 있고, 지운 홈 폴더를 되살리는 일은 [삭제 데이터 복구 (Data Recovery)](../../../03-techniques/analysis/data-recovery/index.md)에서 다룹니다.

## 위치와 버전별 차이

```
/Library/Preferences/com.apple.preferences.accounts.plist   (deletedUsers)
/Users/Deleted Users/                                       (디스크 이미지로 남긴 홈 폴더)
```

`deletedUsers` 가 어느 macOS 버전부터 기록되는지, 시스템 설정으로 지울 때만 남는지 `sysadminctl`·`dscl` 같은 명령으로 지울 때도 남는지는 확인하지 못했습니다. 세 선택지를 설명한 Apple 지원 페이지는 최신 macOS 판(페이지를 열었을 때 기본으로 고른 버전)으로 확인했고, 옛 버전에서도 선택지가 같은지는 버전을 바꿔 보지 않았습니다 [2].

## 구조

`deletedUsers` 에는 지운 계정마다 항목이 하나씩 들어 있고, mac_apt USERS 플러그인은 항목마다 아래 키를 읽습니다 [1].

| 키 | 내용 |
|---|---|
| `name` | 사용자 이름 |
| `dsAttrTypeStandard:RealName` | 전체 이름 |
| `dsAttrTypeStandard:UniqueID` | UID |
| `date` | 지운 시각 (mac_apt 출력 칸 DeletedDate) |

mac_apt 는 `date` 값을 따로 바꾸지 않고 그대로 DeletedDate 에 넣습니다 [1]. 날짜 칸에 그대로 넣는다는 점은 plist 날짜형일 가능성을 보여 주지만, 저장 형태를 검체로 확인하지는 못했습니다.

## 증거로서 의미

**증명하는 것.** `deletedUsers` 에 항목이 있으면 그 이름과 UID 의 계정을 지운 기록이 이 Mac 에 있고, `date` 가 그 기록의 시각이라는 뜻입니다 [1]. `/Users/Deleted Users/` 에 디스크 이미지가 있으면 계정을 지우면서 홈 폴더를 이미지로 남기는 선택지를 골랐을 때 이미지가 놓이는 자리와 맞고, 이미지 안에서 그 계정의 파일을 볼 수 있습니다 [2].

**증명하지 못하는 것.** 이 기록에는 누가 지웠는지와 어떤 방법으로 지웠는지가 들어 있지 않습니다. 어떤 삭제 방법에서 기록이 남는지 확인하지 못했으니, `deletedUsers` 에 항목이 없다고 해서 지운 계정이 없었다고 볼 수 없습니다. 디스크 이미지가 `/Users/Deleted Users/` 에 있다는 사실만으로는 그 이미지를 계정 삭제 과정이 만들었는지, 누가 다른 방법으로 그 자리에 두었는지 가릴 수 없습니다.

보고서에는 "`deletedUsers` 에 이 이름과 UID 의 항목이 있고, `date` 값은 이 시각이다" 처럼 기록이 말하는 만큼만 쓰고, `date` 를 어떤 기준으로 풀었는지도 함께 적습니다.

## 시각 해석

`date` 의 저장 형태와 기준 시각을 확인하지 못했으니, 도구가 보여 주는 시각을 그대로 옮기기 전에 원본 값의 형태부터 봅니다. plist 날짜형이면 plist 도구가 날짜로 보여 주고, 숫자라면 유닉스 시각인지 맥 절대 시각인지 따져서 바꿔야 합니다. 기준별 계산은 [맥의 시각 값 (Mac Absolute Time·Unix·HFS)](../../../01-foundations/value-decoding/mac-time-values.md)에 있습니다.

이 시각은 [파일 시스템 이벤트 (FSEvents)](../../filesystem/fsevents/index.md)에서 계정 plist 가 지워진 기록과 `/Users/Deleted Users/` 에 이미지가 생긴 기록을 찾아 맞춰 봅니다. 두 기록의 시각이 가까우면 `date` 를 어떤 기준으로 풀었는지 판단하는 근거로도 쓸 수 있습니다.

## 함정과 한계

- **기록 조건을 모름.** 버전과 삭제 방법에 따라 `deletedUsers` 가 남는지 확인하지 못했습니다. 항목이 없으면 아래 다른 자리를 함께 찾아봅니다.
- **다른 흔적 후보.** 계정 plist 가 지워진 뒤에도 흔적이 있을 법한 자리로는 `/private/var/folders` 의 Darwin 폴더(mac_apt 가 UID 로 계정과 잇는 폴더 [3]), 같은 노드 폴더의 `sqlindex` [4], 지우지 않은 홈 폴더, 통합 로그가 있습니다. 이 자리들에 지운 계정의 흔적이 실제로 남는지는 하나씩 확인하지 못했습니다.
- **같은 UID.** Darwin 폴더는 UID·GID 로 계정과 이어집니다 [3]. 지운 계정과 UID 가 같은 계정이 지금 있는지 먼저 확인해야 폴더 주인을 잘못 짚지 않습니다.
- **설정 파일을 고친 경우.** `com.apple.preferences.accounts.plist` 를 누가 직접 고치거나 지우면 어떤 흔적이 남는지는 확인하지 못했습니다. [스냅숏과 백업 비교 (Snapshot·Time Machine Diff)](../../../03-techniques/analysis/snapshot-diff.md)로 이전 사본의 `deletedUsers` 와 계정 plist 를 비교합니다.

## 직접 분석해 보기

`date` 의 저장 형태를 확인하지 못해서 헥스 예시는 싣지 않고, 확인 순서만 적습니다.

1. `/Library/Preferences/com.apple.preferences.accounts.plist` 를 plist 도구로 열고 `deletedUsers` 항목을 모두 적습니다 [1].
2. 각 항목의 `date` 가 날짜형인지 숫자인지 적고, 숫자라면 기준을 따져 UTC 로 바꿉니다.
3. `dsAttrTypeStandard:UniqueID` 를 지금 있는 계정 plist 의 `uid` 와 비교해 같은 UID 가 있는지 봅니다.
4. `/Users/Deleted Users/` 에 디스크 이미지가 있는지 보고, 있으면 쓰기 막힌 상태로 열어 안의 홈 폴더를 확인합니다 [2].
5. `/private/var/folders` 아래에서 그 UID 의 폴더를 찾습니다 [3].

mac_apt USERS 플러그인은 1번의 항목을 DeletedDate 칸이 채워진 행으로 내고, 이때 `date` 를 따로 바꾸지 않고 그대로 옮깁니다 [1]. 손으로 읽은 `date` 와 DeletedDate 가 다르게 보이면 도구가 값을 바꾼 것이 아니라 표시하는 시간대가 다른 것인지 먼저 봅니다.

## 교차 검증

| 함께 볼 아티팩트 | 맞춰 볼 것 |
|---|---|
| [계정 plist 구조 (dslocal)](dslocal-plist.md) | 지금 있는 계정과 UID·이름이 겹치는지 |
| [파일 시스템 이벤트 (FSEvents)](../../filesystem/fsevents/index.md) | 계정 plist 삭제·디스크 이미지 생성 시각 |
| [타임 머신 (Time Machine)](../../filesystem/time-machine/index.md) | 지우기 전 계정 plist 와 홈 폴더 사본 |
| [통합 로그에서 찾을 것 (Unified Log Events)](../../logs/unified-log-events/index.md) | `date` 와 같은 시간대의 기록 |
| [증거를 없애려 했나 (Anti-Forensics)](../../../04-scenarios/activity/anti-forensics/index.md) | 계정 삭제가 흔적 지우기의 일부인지 따지는 흐름 |

## 실습

공개 검체(NIST CFReDS 등)의 macOS 이미지로 풀어 봅니다.

1. `deletedUsers` 에 항목이 있는지 보고, 있다면 이름·UID·`date` 를 적은 뒤 `date` 의 저장 형태를 확인해 보세요.
2. `/Users/Deleted Users/` 에 디스크 이미지가 있는지, 있다면 안의 홈 폴더가 어느 계정 것인지 확인해 보세요.
3. 지운 계정의 UID 로 `/private/var/folders` 에서 폴더를 찾고, 지금 같은 UID 를 쓰는 계정이 없는지 확인해 보세요.

## 참고 문헌

1. mac_apt `USERS` 플러그인 소스 (Yogesh Khatri) — https://raw.githubusercontent.com/ydkhatri/mac_apt/master/plugins/users.py
2. Apple 지원, Mac 사용 설명서 — Delete a user or group on Mac — https://support.apple.com/guide/mac-help/delete-a-user-or-group-mchlp1557/mac
3. mac_apt `macinfo.py` 헬퍼 소스 (`_GetUserInfo`) — https://raw.githubusercontent.com/ydkhatri/mac_apt/master/plugins/helpers/macinfo.py
4. ForensicArtifacts `macos.yaml` (MacOSDirectoryServicesLocalNodesSQLiteDatabaseFile) — https://raw.githubusercontent.com/ForensicArtifacts/artifacts/main/artifacts/data/macos.yaml
