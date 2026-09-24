---
title: "컴퓨터 이름과 하드웨어 정보"
parent: "아티팩트 · 시스템·계정"
nav_order: 460
---

# 컴퓨터 이름과 하드웨어 정보 (Computer Name·Hardware)

`/Library/Preferences/SystemConfiguration/preferences.plist` 에서 컴퓨터 이름·호스트 이름·하드웨어 모델을 읽고, 위치 서비스 캐시 데이터베이스에서 시리얼 번호를 찾아, 이미지 속 맥이 어느 기기이고 네트워크에 어떤 이름으로 보였는지를 적습니다.

## 무엇을 기록하나 · 왜 생기나

맥에는 이름이 여럿 있습니다. Apple 설명에 따르면 컴퓨터 이름 (Computer Name) 은 맥을 일반적으로 알아보는 이름이고, 로컬 호스트 이름 (Local Hostname) 은 로컬 네트워크 이름이라고도 하며 Bonjour 호환 서비스에 이 맥을 알리는 이름입니다. [3] 사용자는 컴퓨터 이름을 시스템 설정 → 일반 → 정보에서 바꾸고, 로컬 호스트 이름은 시스템 설정 → 일반 → 공유에서 "로컬 호스트 이름" 을 편집해 바꿉니다. [3]

이 설정은 시스템 구성 기본 설정 파일인 `/Library/Preferences/SystemConfiguration/preferences.plist` 에 들어 있습니다. [1][2] 공개 도구 mac_apt 는 이 파일에서 하드웨어 모델과 컴퓨터 이름, 호스트 이름을 읽어 기본 정보로 냅니다. [1]

조사에서 이 값이 필요한 곳은 두 가지입니다. 하나는 기기를 특정하는 일로, 압수한 기기와 이미지가 같은 기기인지, 보고서의 대상이 어느 맥인지를 컴퓨터 이름·모델·시리얼 번호로 적어 둡니다. 다른 하나는 네트워크 기록과 잇는 일로, 공유 폴더 접속, 원격 접속, 다른 기기의 연결 기록에는 흔히 상대 기기의 이름이 남아서 그 이름이 이 맥의 이름과 같은지 맞춰 볼 수 있습니다.

## 위치와 버전별 차이

| 기록 | 위치 | 알려 주는 것 |
|---|---|---|
| 시스템 구성 기본 설정 | `/Library/Preferences/SystemConfiguration/preferences.plist` | 하드웨어 모델, 컴퓨터 이름, 호스트 이름 [1][2] |
| 위치 서비스 캐시 데이터베이스 | `/private/var/folders/zz/zyxvpxvq6csfxvn_n00000sm00006d/C/` 아래 `consolidated.db`, `cache_encryptedA.db`, `lockCache_encryptedA.db` | 시리얼 번호 [1] |

mac_apt 는 시리얼 번호를 찾을 때 위 세 파일과 `locationd/` 아래의 같은 이름 파일 세 개, 모두 여섯 자리를 차례로 봅니다. [1] 폴더 이름 `zz/zyxvpxvq6csfxvn_n00000sm00006d` 가 모든 기기에서 같은지, 어느 macOS 버전부터 이 파일들이 있는지는 이번 자료로 확인하지 못했습니다. 이미지에서는 파일 이름으로 검색해 실제로 놓인 자리를 찾고, 보고서에도 찾은 경로를 그대로 적습니다.

설정 화면의 위치(시스템 설정 → 일반 → 정보, 일반 → 공유)는 최신 Apple 설명서 기준입니다. [3] `preferences.plist` 의 키 배치가 macOS 버전마다 달라지는지는 이번 자료로 확인하지 못했습니다.

## 구조

### preferences.plist

mac_apt 가 이 파일에서 읽는 키는 다음과 같습니다. [1] 파일 안의 계층은 사전 (dictionary) 안에 사전이 들어간 모양이라, 표의 화살표는 바깥 사전에서 안쪽 키로 들어가는 순서를 뜻합니다. plist 를 여는 법은 [속성 목록 파일](../../01-foundations/data-formats/plist/index.md) 페이지에 있습니다.

| 키 경로 | 뜻 |
|---|---|
| `Model` | 하드웨어 모델 |
| `System` → `System` → `ComputerName` | 컴퓨터 이름 |
| `System` → `System` → `HostName` | 호스트 이름 |
| `System` → `Network` → `HostNames` | 네트워크 호스트 이름들. mac_apt 는 이 사전의 키와 값을 모두 그대로 냄 |

mac_apt 는 `HostNames` 아래의 키를 이름을 정해 두지 않고 모두 읽어 내서 [1], 로컬 호스트 이름이 어떤 키 이름으로 들어가는지는 이 소스로 정해지지 않습니다. 검체에서 이 사전을 열어 실제 키와 값을 그대로 적습니다. 하드웨어 모델 식별자가 어떤 형식으로 적히는지, 인텔 칩과 Apple 칩을 어디서 구분하는지도 이번 자료 범위 밖이라, `Model` 값은 검체에서 나온 문자열 그대로 보고서에 옮깁니다.

### 로컬 호스트 이름을 만드는 규칙

Apple 설명서가 밝힌 규칙은 다음과 같습니다. [3] 로컬 호스트 이름은 컴퓨터 이름 끝에 `.local` 을 붙이고 공백을 하이픈으로 바꿔 만들어서, 컴퓨터 이름이 "My Computer" 면 로컬 호스트 이름은 "My-Computer.local" 이 됩니다. 로컬 호스트 이름은 대소문자를 가리지 않고, 같은 이름의 맥이 네트워크에 있으면 이름 끝에 숫자가 붙습니다. 컴퓨터 이름을 Bonjour 가 알아보지 못하면 로컬 호스트 이름은 "Macintosh.local" 이 됩니다.

### 위치 서비스 캐시의 시리얼 번호

mac_apt 는 위 캐시 파일을 [SQLite 데이터베이스](../../01-foundations/data-formats/sqlite/index.md) 로 열고, `TableInfo` 테이블의 `SerialNumber` 칸을 읽습니다. [1]

```sql
SELECT SerialNumber FROM TableInfo
```

## 증거로서 의미

**증명하는 것.** `preferences.plist` 는 이미지를 뜬 시점에 이 맥에 설정된 컴퓨터 이름과 호스트 이름, 하드웨어 모델을 알려 줍니다. [1] 캐시 데이터베이스에 시리얼 번호가 있으면 압수 기록의 시리얼 번호와 맞춰 이미지와 기기를 이을 수 있습니다. 다른 기기나 로그에 남은 이름이 이 맥의 컴퓨터 이름이나 로컬 호스트 이름과 같으면, Apple 규칙에 따라 컴퓨터 이름에서 로컬 호스트 이름을 끌어내 두 기록을 같은 기기로 볼 근거가 생깁니다. [3]

**증명하지 못하는 것.** 컴퓨터 이름은 사용자가 설정 화면에서 언제든 바꿀 수 있어서 [3], 이름이 누구의 기기인지를 보여 주지 않고 과거에 어떤 이름을 썼는지도 이 파일만으로는 알 수 없습니다. 이름이 사람 이름처럼 보여도 그 사람이 이 맥을 썼다는 근거로 쓰지 않습니다. 다른 기기에 같은 이름이 남았더라도 이름만으로는 같은 기기라고 단정할 수 없어서, 시리얼 번호 같은 다른 식별자와 함께 봅니다.

로컬 호스트 이름 끝에 숫자가 붙어 있으면, 같은 이름의 다른 맥이 한 네트워크에 있었던 흔적일 수 있습니다(필자 판단). Apple 설명서는 숫자가 붙는 조건만 밝힐 뿐이라서 [3], 보고서에는 "숫자가 붙은 이름이 남아 있다" 까지만 쓰고 다른 맥이 있었다고 단정하지 않습니다.

보고서에는 "`preferences.plist` 의 `ComputerName` 값은 무엇이고, 위치 서비스 캐시의 `SerialNumber` 값은 압수 기록의 시리얼 번호와 같다" 처럼 기록이 말하는 만큼만 씁니다.

## 시각 해석

mac_apt 가 읽는 키에는 시각 값이 없습니다. [1] 이름이 언제 바뀌었는지 알고 싶어도 `preferences.plist` 의 파일 수정 시각을 그대로 쓸 수는 없는데, 이 파일에는 `System` 사전과 함께 `Network` 사전이 들어 있어서 [1] 이름이 아닌 다른 설정이 바뀌어도 파일은 다시 쓰일 수 있기 때문입니다. 파일 수정 시각은 "이 시각 이후로 이 파일이 바뀌지 않았다" 는 정도로만 쓰고, 이름을 바꾼 시각은 [통합 로그에서 찾을 것](../logs/unified-log-events/index.md) 이나 [스냅숏과 백업 비교](../../03-techniques/analysis/snapshot-diff.md) 로 따로 찾습니다.

## 함정과 한계

컴퓨터 이름과 로컬 호스트 이름, 호스트 이름은 서로 다른 값입니다. 사용자는 로컬 호스트 이름을 공유 설정에서 따로 바꿀 수 있어서 [3], 컴퓨터 이름에서 끌어낸 이름과 실제 로컬 호스트 이름이 다를 수 있습니다. 다른 기록과 맞춰 볼 때는 세 값을 모두 적어 두고 어느 값과 맞았는지 밝힙니다.

위치 서비스 캐시 파일은 폴더 이름과 macOS 버전 범위를 확인하지 못해서, 검체에 따라 파일이 없거나 테이블에 값이 없을 수 있습니다. 시리얼 번호를 못 찾았다고 해서 기기를 특정할 수 없다고 끝내지 말고, 압수 때 기록한 값과 다른 기록을 함께 봅니다.

라이브 시스템에서 설정 화면이나 명령으로 이름을 확인할 때는, 조회 옵션만 쓰고 이름을 바꾸는 옵션은 쓰지 않습니다.

## 직접 분석해 보기

### 헥스로 한 번

바이너리 plist 는 키 이름을 문자열 객체로 저장해서, 헥스 편집기에서 `ComputerName` 이나 `HostNames` 를 검색하면 파일 안에 그 키가 있는지부터 확인할 수 있습니다. 키와 값을 잇는 오프셋 표를 따라가 문자열 값을 읽는 절차는 [속성 목록 파일](../../01-foundations/data-formats/plist/index.md) 페이지에 있습니다. 컴퓨터 이름에 한글이나 기호가 들어 있으면 문자열 인코딩과 정규화에 따라 바이트가 달라지니 [유니코드 정규화](../../01-foundations/value-decoding/unicode-normalization.md) 페이지도 함께 봅니다.

> 그림 자리: 헥스 편집기에서 `ComputerName` 키 문자열과 이어지는 값 문자열을 표시한 화면(명세로 만든 예시 파일 기준)

### 공개 도구로 한 번

mac_apt 의 `BASICINFO` 플러그인은 `preferences.plist` 의 모델·컴퓨터 이름·호스트 이름과 캐시 데이터베이스의 시리얼 번호를 한 번에 냅니다. [1] 캐시 데이터베이스를 직접 볼 때는 SQLite 도구로 파일 사본을 열고 위 `SELECT` 문을 실행합니다. 사본을 다루는 절차는 [SQLite 데이터베이스](../../01-foundations/data-formats/sqlite/index.md) 페이지를 따릅니다.

### 라이브 시스템에서

켜져 있는 맥에서는 `systemsetup` 명령으로 현재 값을 조회할 수 있고, 관리자 권한(sudo)이 필요합니다. [4]

| 옵션 | 돌려주는 값 |
|---|---|
| `systemsetup -getcomputername` | 컴퓨터 이름 |
| `systemsetup -getlocalsubnetname` | 로컬 서브넷 이름 |

조사 중에는 값을 돌려주는 `-get...` 옵션만 씁니다. 라이브 대응 전반의 순서는 [라이브 대응](../../03-techniques/process-acquisition/live-response/index.md) 페이지를 따르고, 명령 결과는 실행 시각과 함께 적어 둡니다.

## 교차 검증

| 함께 볼 기록 | 맞춰 볼 내용 |
|---|---|
| [네트워크 인터페이스와 설정](../network/network-interfaces.md) | 같은 파일의 `Network` 사전과 네트워크 구성 |
| [공유 폴더 연결 기록](../network/network-shares.md) | 다른 기기에 남은 이 맥의 이름 |
| [원격 접속](../network/remote-access/index.md) | 원격 접속 기록에 나오는 호스트 이름 |
| [아이폰·아이패드 연결](../external-devices/ios-devices/index.md) | 이 맥과 연결한 모바일 기기의 기록 |
| [OS 버전과 설치 기록](os-version-install-history.md) | 모델과 OS 버전이 서로 맞는지 |

## 실습

공개 검체(NIST CFReDS 등)의 맥 이미지로 다음 질문을 풀어 봅니다.

1. `preferences.plist` 에서 `Model`, `ComputerName`, `HostName` 과 `HostNames` 사전의 내용을 모두 적어 봅니다.
2. Apple 규칙대로 컴퓨터 이름에서 로컬 호스트 이름을 만들어 보고, `HostNames` 에 남은 값과 같은지 비교합니다. 다르다면 숫자가 붙었는지, 사용자가 따로 바꿨는지 가능한 설명을 적어 봅니다.
3. 이미지에서 `consolidated.db` 를 파일 이름으로 찾고, 사본을 열어 `TableInfo` 의 `SerialNumber` 를 읽어 봅니다. 파일이 놓인 폴더 이름도 함께 적습니다.
4. 공유 폴더 기록이나 원격 접속 기록에서 이 맥의 이름이 나오는 곳을 찾아, 세 이름 가운데 어느 값과 맞는지 확인합니다.

## 참고 문헌

1. mac_apt `BASICINFO` 플러그인 소스 (Yogesh Khatri) — https://raw.githubusercontent.com/ydkhatri/mac_apt/master/plugins/basicinfo.py
2. ForensicArtifacts `macos.yaml` (MacOSSystemConfigurationPreferencesPlistFile) — https://raw.githubusercontent.com/ForensicArtifacts/artifacts/main/artifacts/data/macos.yaml
3. Apple 지원, Mac 사용 설명서 — Change your computer's name or local hostname on Mac — https://support.apple.com/guide/mac-help/change-computers-local-hostname-mchlp2322/mac
4. SS64, systemsetup 명령 설명 — https://ss64.com/mac/systemsetup.html
