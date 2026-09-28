---
title: "관리자와 그룹 소속"
parent: "사용자 계정"
grand_parent: "아티팩트 · 시스템·계정"
nav_order: 510
---

# 관리자와 그룹 소속 (admin·Groups)

계정의 권한을 따질 때는 관리자 그룹에 속했는지와 볼륨 소유자 (Volume Owner) 인지를 따로 확인합니다. 볼륨 소유자이면서 관리자가 아닌 계정도 있을 수 있습니다 [2].

## 무엇을 기록하나 · 왜 생기나

이 페이지는 두 질문을 다룹니다. 하나는 그 계정이 관리자 그룹에 속했는가이고, 다른 하나는 그 계정이 볼륨 소유자로서 보안 토큰 (Secure Token) 을 받았는가입니다. 두 번째 질문은 보안 토큰 기록으로 답할 수 있지만 [2], 첫 번째 질문에 쓸 그룹 기록의 경로와 멤버 키는 실제 데이터로 확인해야 합니다. mac_apt 의 `macinfo.py` 도 계정 plist 만 읽고 그룹 plist 는 읽지 않습니다 [1].

그룹 plist 의 경로, 멤버 목록 키, admin·staff 그룹의 GID 같은 구체값은 실제 데이터로 확인하고, 확인한 macOS 버전과 함께 보고서에 적습니다.

## 위치와 확인 범위

| 알고 싶은 것 | 볼 곳 | 알려진 것과 확인할 것 |
|---|---|---|
| 볼륨 소유자·보안 토큰 여부 | 계정의 `AuthenticationAuthority` 속성 ([계정 plist 구조 (dslocal)](dslocal-plist.md)), 켜진 시스템에서는 `diskutil apfs listUsers /` 출력 [2] | 보안 토큰을 막는 값은 `;DisabledTags;SecureToken` [2], 토큰이 있을 때의 값과 plist 키 이름은 실제 데이터로 확인 |
| 관리자 그룹 소속 | 로컬 그룹 기록 | 경로·키는 실제 데이터로 확인 [1] |
| 부트스트랩 토큰 사용 여부 | MDM 등록 상태 ([구성 프로파일 (Configuration Profiles·MDM)](../../persistence/configuration-profiles.md)) | 동작 설명 [2], 저장 위치는 실제 데이터로 확인 |

계정 plist 에는 `gid` 가 있지만 [1], 이 값으로 관리자 여부를 알 수 있다는 근거는 없습니다. `gid` 하나로 관리자라고 판단하지 않습니다.

## 관리자와 볼륨 소유자의 구분

macOS 는 관리자 여부와 볼륨 소유자 여부를 따로 다루고, 어떤 작업은 두 자격을 모두 확인합니다 [2]. 볼륨 소유자라야 할 수 있는 일은 시동 보안 정책을 바꾸는 일, macOS 소프트웨어 업데이트·업그레이드 설치를 승인하는 일, "모든 콘텐츠 및 설정 지우기" 를 시작하는 일입니다 [2]. 켜진 시스템에서는 `diskutil apfs listUsers /` 로 볼륨 소유자를 볼 수 있습니다 [2].

Apple silicon Mac 에서는 처음 설정한 사용자가 보안 토큰을 받고 첫 볼륨 소유자가 됩니다 [2]. 계정 기록의 `AuthenticationAuthority` 속성은 [계정 plist 구조 (dslocal)](dslocal-plist.md)에서 다룹니다.

부트스트랩 토큰 (Bootstrap Token) 은 플랫폼 SSO 계정이나 모바일 계정처럼 그때그때 만든 계정이 따로 인증하지 않고도 보안 토큰을 받게 합니다 [2]. macOS 26 이후에는 기기 관리 서비스가 지원하면 기기 관리 등록 단계에서 부트스트랩 토큰이 만들어집니다 [2]. 조직이 관리하는 Mac 이라면 나중에 생긴 계정이 사용자 암호 입력 없이 보안 토큰을 받았을 수 있다는 점을 염두에 둡니다.

| macOS | 달라진 점 | 출처 |
|---|---|---|
| macOS 26 이후 | 기기 관리 서비스가 지원하면 등록 때 부트스트랩 토큰이 만들어짐 | [2] |

## 증거로서 의미

**증명하는 것.** 계정의 `AuthenticationAuthority` 에 `;DisabledTags;SecureToken` 이 있으면 그 계정이 보안 토큰을 받지 않도록 막아 둔 기록입니다 [2]. 이 값은 프로그램으로 계정을 만들 때 더하는 값이므로 [2], 누군가 계정을 만들면서 일부러 넣었을 가능성도 함께 따집니다. 관리자 그룹 소속은 그룹 기록을 직접 확인한 경우에만 증거로 씁니다.

**증명하지 못하는 것.** 보안 토큰이 있다고 해서 관리자라고 볼 수 없고, 관리자라고 해서 볼륨 소유자라고 볼 수도 없습니다 [2]. 수집 시점에 관리자였다는 기록만으로는 특정 시각에 그 계정이 관리자 권한을 썼는지, 사건 당시에도 관리자였는지 알 수 없습니다. `sysadminctl` 로 보안 토큰 상태를 바꿀 수 있어서 [2], 지금의 속성 값이 계정을 만들 때부터 그 상태였다고 보지 않습니다.

보고서에는 "수집 시점에 이 계정의 인증 속성에 이 값이 적혀 있다" 처럼 원래 값을 그대로 쓰고, 관리자 여부는 확인한 기록의 경로와 함께 따로 적습니다.

## 함정과 한계

- **도구 결과에 그룹이 없음.** mac_apt 사용자 정보는 그룹 plist 를 읽지 않아서 [1], 도구 표에 관리자 여부가 없다고 일반 사용자라고 판단하지 않습니다.
- **처음 만든 계정.** Apple silicon 에서는 처음 설정한 사용자가 첫 볼륨 소유자가 됩니다 [2]. 보안 토큰이 있는 계정이 여럿이면 어느 계정이 처음 설정한 계정인지 만든 시각(`creationTime`)으로 따져 봅니다.
- **권한이 바뀐 시점.** 관리자 권한이나 보안 토큰을 언제 주고 뺐는지는 [스냅숏과 백업 비교 (Snapshot·Time Machine Diff)](../../../03-techniques/analysis/snapshot-diff.md)로 이전 사본과 비교하고, [통합 로그에서 찾을 것 (Unified Log Events)](../../logs/unified-log-events/index.md)에서 같은 시간대 기록을 찾아 확인합니다.

## 교차 검증

| 함께 볼 아티팩트 | 맞춰 볼 것 |
|---|---|
| [계정 plist 구조 (dslocal)](dslocal-plist.md) | `AuthenticationAuthority` 값, 계정을 만든 시각 |
| [파일볼트 (FileVault)](../../../01-foundations/protection/filevault/index.md) | 보안 토큰이 있는 계정과 볼륨 잠금 해제 |
| [구성 프로파일 (Configuration Profiles·MDM)](../../persistence/configuration-profiles.md) | MDM 등록 여부와 부트스트랩 토큰 |
| [소프트웨어 업데이트 기록 (Software Update)](../software-update.md) | 볼륨 소유자 승인이 필요한 업데이트가 있었던 시각 |
| [권한 상승과 TCC 우회 흔적 (Privilege·TCC Bypass)](../../../04-scenarios/incident/privilege-tcc-bypass.md) | 권한이 바뀐 계정을 조사하는 흐름 |

## 실습

공개 시험 자료(NIST CFReDS 등)의 macOS 이미지로 풀어 봅니다.

1. 로컬 계정마다 `AuthenticationAuthority` 값을 표로 적고, `;DisabledTags;SecureToken` 이 있는 계정을 표시해 보세요.
2. 보안 토큰이 있는 계정 가운데 가장 먼저 만든 계정을 `creationTime` 으로 찾아 보세요.
3. 이미지의 그룹 기록을 찾아 관리자 그룹 멤버를 확인하고, 1번 표와 겹치지 않는 계정이 있는지 비교해 보세요. 찾은 경로와 macOS 버전도 함께 적습니다.

## 참고 문헌

1. mac_apt `macinfo.py` 헬퍼 소스 (`_GetUserInfo`) — https://raw.githubusercontent.com/ydkhatri/mac_apt/master/plugins/helpers/macinfo.py
2. Apple Platform Deployment, Use secure token, bootstrap token and volume ownership in deployments — https://support.apple.com/guide/deployment/use-secure-and-bootstrap-tokens-dep24dbdcf9e/web
