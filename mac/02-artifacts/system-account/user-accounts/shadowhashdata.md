---
title: "암호 해시"
parent: "사용자 계정"
grand_parent: "아티팩트 · 시스템·계정"
nav_order: 500
---

# 암호 해시 (ShadowHashData)

암호 해시 (ShadowHashData) 는 계정 plist 의 `ShadowHashData` 키에 들어 있는 로그인 암호 해시이고, 공개 도구는 그 안의 반복 횟수·솔트·entropy 를 꺼내 한 줄로 보여 주며, 암호 자체가 아니라 암호를 어떤 방식으로 저장했는지와 그 값이 언제 바뀌었는지를 따질 때 씁니다 [1][4].

## 무엇을 기록하나 · 왜 생기나

로컬 계정의 로그인 암호는 평문이 아니라 해시로 계정 plist 에 들어가고, 그 키 이름이 `ShadowHashData` 입니다 [1][4]. OS X 10.9 에서 이 값은 사용자 로그인 암호의 솔트 SHA-512 해시 값입니다 [5]. 이 안에는 `SALTED-SHA512-PBKDF2` 방식의 값이 있고, `entropy`, `salt`, `iterations` 가 들어 있습니다 [1].

이 핸드북은 사고 대응과 탐지를 위한 자료라서 해시에서 암호를 알아내는 절차는 다루지 않습니다. 이 페이지는 해시가 어디에 어떤 모양으로 남고, 증거로서 무엇을 말해 주는지만 다룹니다. 계정 plist 의 위치와 다른 키는 [계정 plist 구조 (dslocal)](dslocal-plist.md)에 있습니다.

## 위치와 버전별 차이

해시는 따로 파일이 있지 않고 계정 plist 안의 키 하나로 들어 있습니다 [1][4]. 그래서 계정 plist 가 곧 사용자 암호 해시 plist 파일입니다 [4].

| 자료 | 다루는 버전 | 적힌 방식 | 출처 |
|---|---|---|---|
| Forensics Wiki, Mac OS X 10.9 흔적 위치 | OS X 10.9 | 솔트 SHA-512 해시 | [5] |
| plaso `macos_user` 플러그인 | 버전 표시 없음 | `SALTED-SHA512-PBKDF2` | [1] |

macOS 버전마다 해시 방식이 어떻게 바뀌었는지, 10.15 Catalina 이후에 `SALTED-SHA512-PBKDF2` 말고 다른 방식의 키(예: `SRP-RFC5054-4096-SHA512-PBKDF2`)가 함께 들어가는지와 어느 버전부터인지는 공개 자료로 정리돼 있지 않습니다. 검체에서 `ShadowHashData` 를 열면 어떤 방식 이름이 들어 있는지부터 적어 둡니다.

## 구조

`ShadowHashData` 의 `SALTED-SHA512-PBKDF2` 항목은 딕셔너리이고, 아래 세 값이 들어 있습니다 [1].

| 값 | 내용 | plaso 가 다루는 방식 |
|---|---|---|
| `iterations` | PBKDF2 반복 횟수 | 숫자 그대로 씀 |
| `salt` | 솔트 | 바이트열을 16진 문자열로 바꿈 |
| `entropy` | entropy 값 (plaso 출력의 마지막 칸) | 바이트열을 16진 문자열로 바꿈 |

plaso 는 세 값을 아래 모양의 한 줄로 이어 냅니다 [1].

```
$ml$<iterations>$<salt>$<entropy>
```

`ShadowHashData` 값 안에는 바이너리 plist 가 한 번 더 들어 있어서 [1], 손으로 읽을 때도 이 데이터를 plist 로 다시 엽니다. 반복 횟수와 솔트·entropy 길이는 검체에서 읽어 적습니다.

## 증거로서 의미

**증명하는 것.** 계정 plist 에 `ShadowHashData` 가 있으면 수집 시점에 그 계정에 로그인 암호가 해시로 저장돼 있었다는 뜻이고, 방식 이름과 반복 횟수를 보면 어떤 방식으로 저장됐는지 알 수 있습니다 [1]. 같은 계정의 두 시점 사본(예: 백업과 현재 디스크)에서 값이 다르면 그 사이에 저장된 해시가 바뀌었다는 기록입니다.

**증명하지 못하는 것.** 해시에는 암호가 무엇인지도, 누가 그 암호를 알았는지도, 언제 로그인했는지도 들어 있지 않습니다. 해시가 있다고 해서 그 계정으로 로그인한 적이 있다고 볼 수 없습니다. 파일볼트 (FileVault) 잠금 해제와 보안 토큰 쪽 키는 로그인 해시와 별개로 사용자 암호로 감싼 키 암호화 키 (KEK) 라서 [3], 이 해시만으로 볼륨 잠금 해제 권한을 판단하지 않습니다. 보안 토큰 관련 속성은 [계정 plist 구조 (dslocal)](dslocal-plist.md)에서, 볼륨 쪽은 [파일볼트 (FileVault)](../../../01-foundations/protection/filevault/index.md)에서 다룹니다.

보고서에는 "이 계정의 `ShadowHashData` 에 `SALTED-SHA512-PBKDF2` 항목이 있고, 백업 사본과 비교하면 값이 다르다" 처럼 기록이 말하는 만큼만 씁니다. 해시 값은 자격 증명 자료라서 보고서 본문에 그대로 옮기지 않고, 필요하면 앞 몇 글자만 적거나 따로 보관한 사본을 가리킵니다.

## 시각 해석

이 항목의 값은 반복 횟수·솔트·entropy 세 가지이고, 시각은 없습니다 [1]. 해시가 언제 바뀌었는지는 같은 계정 plist 의 `passwordLastSetTime` 에서 찾습니다. 10.10 이후에는 이 값이 `accountPolicyData` 안에 유닉스 시각으로 들어 있습니다 [2]. 두 시점 사본의 해시가 다르면 `passwordLastSetTime` 이 그 사이에 있는지 맞춰 봅니다. 시각을 읽는 법은 [계정 plist 구조 (dslocal)](dslocal-plist.md)의 시각 해석 절에 있습니다.

## 함정과 한계

- **버전별 방식.** macOS 버전마다 쓰는 해시 방식은 공개 자료로 정리돼 있지 않습니다. 한 버전에서 본 방식을 다른 버전 검체에 그대로 적용하지 않습니다.
- **도구가 보여 주는 방식이 전부가 아닐 수 있음.** plaso 는 `SALTED-SHA512-PBKDF2` 항목만 꺼냅니다 [1]. 도구 결과에 이 항목만 보인다고 해서 다른 방식의 키가 없다고 단정하지 말고, 원본 값의 키 목록을 직접 봅니다.
- **10.9 자료의 설명.** "솔트 SHA-512" 라는 설명은 10.9 을 다룬 자료에서 왔습니다 [5]. Catalina 이후 검체를 설명할 때 이 문장을 근거로 인용하지 않습니다.
- **자격 증명 취급.** 해시는 암호를 되찾는 데 쓰일 수 있는 자료입니다. 수집·보관·공유 범위를 사건 절차에 맞춰 제한합니다.

## 직접 분석해 보기

아래는 값의 모양을 확인하고 두 시점을 비교하는 순서입니다.

1. [계정 plist 구조 (dslocal)](dslocal-plist.md)의 순서대로 계정 plist 를 엽니다.
2. `ShadowHashData` 데이터를 plist 로 다시 열고 [1], 안에 어떤 방식 이름의 키가 있는지 모두 적습니다.
3. `SALTED-SHA512-PBKDF2` 항목에서 `iterations`, `salt`, `entropy` 가 있는지 확인합니다 [1].
4. plaso `macos_user` 플러그인으로 같은 파일을 읽어 `$ml$...` 줄이 나오는지, 손으로 읽은 값과 같은지 봅니다 [1].
5. 백업이나 스냅숏에 같은 계정의 이전 사본이 있으면 `salt`·`entropy` 가 같은지 비교하고, 다르면 두 사본의 `passwordLastSetTime` 을 함께 적습니다. 이전 사본을 찾는 법은 [스냅숏과 백업 비교 (Snapshot·Time Machine Diff)](../../../03-techniques/analysis/snapshot-diff.md)에 있습니다.

## 교차 검증

| 함께 볼 아티팩트 | 맞춰 볼 것 |
|---|---|
| [계정 plist 구조 (dslocal)](dslocal-plist.md) | `passwordLastSetTime` 과 해시가 바뀐 시점 |
| [파일볼트 (FileVault)](../../../01-foundations/protection/filevault/index.md) | 로그인 해시와 따로 움직이는 볼륨 쪽 키 |
| [타임 머신 (Time Machine)](../../filesystem/time-machine/index.md) | 이전 시점의 계정 plist 사본 |

## 실습

공개 검체(NIST CFReDS 등)의 macOS 이미지로 풀어 봅니다.

1. 각 로컬 계정의 `ShadowHashData` 에 들어 있는 방식 이름을 모두 적고, 계정마다 같은지 비교해 보세요.
2. plaso 출력의 `$ml$` 줄에서 반복 횟수를 읽고, 계정마다 같은지 확인해 보세요.
3. 같은 검체에 이전 시점 사본이 있다면 해시가 바뀐 계정을 찾고, `passwordLastSetTime` 과 맞는지 확인해 보세요.

## 참고 문헌

1. plaso `macos_user` plist 플러그인 소스 — https://raw.githubusercontent.com/log2timeline/plaso/main/plaso/parsers/plist_plugins/macos_user.py
2. mac_apt `macinfo.py` 헬퍼 소스 (`_GetUserInfo`) — https://raw.githubusercontent.com/ydkhatri/mac_apt/master/plugins/helpers/macinfo.py
3. Apple Platform Deployment, Use secure token, bootstrap token and volume ownership in deployments — https://support.apple.com/guide/deployment/use-secure-and-bootstrap-tokens-dep24dbdcf9e/web
4. ForensicArtifacts `macos.yaml` (MacOSUserPasswordHashesPlistFile) — https://raw.githubusercontent.com/ForensicArtifacts/artifacts/main/artifacts/data/macos.yaml
5. Forensics Wiki, Mac OS X 10.9 artifacts location — https://forensics.wiki/mac_os_x_10.9_artifacts_location/
