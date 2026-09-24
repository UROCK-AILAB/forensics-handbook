---
title: "아이클라우드 계정"
parent: "아티팩트 · 클라우드·애플 앱"
nav_order: 1490
---

# 아이클라우드 계정 (iCloud Account)

맥에서 Apple 계정으로 iCloud에 로그인한 흔적은 사용자 홈 `Library` 아래의 계정 설정 plist와 계정 DB에 남고, 그 계정의 데이터가 기기 밖에서 어떻게 보호되는지는 표준 데이터 보호인지 고급 데이터 보호인지에 따라 달라집니다.

이 페이지는 계정 흔적이 있는 파일과, 그 흔적을 해석할 때 알아야 할 iCloud 보호 구조를 다룹니다. 파일 동기화 흔적은 [아이클라우드 드라이브 (iCloud Drive·CloudDocs)](icloud-drive.md)에서 다룹니다.

## 무엇을 기록하나 · 왜 생기나

사용자는 Apple 계정으로 로그인한 뒤 쓸 iCloud 서비스를 고르고, iCloud Drive나 iCloud 백업 (iCloud Backup) 같은 기능은 관리자가 기기 관리(MDM) 구성 프로파일로 끌 수 있습니다 [3]. 로그인하고 서비스를 고른 결과가 사용자 홈의 설정 파일과 계정 DB에 남아서, 이 맥의 어느 사용자 계정에서 iCloud를 설정했는지 따질 때 이 파일들을 먼저 봅니다.

공개 수집 정의인 ForensicArtifacts는 이 흔적을 세 항목으로 나눠 적어 두었습니다 [1]. `MacOSiCloudPreferences` 는 "iCloud user preferences", `MacOSiCloudAccounts` 는 "iCloud Accounts", `MacOSUserAccountsSQLiteDatabaseFile` 은 "User Accounts SQLite database files" 라는 설명이 붙어 있고, 마지막 항목의 별칭은 `MacOSUserSocialAccounts` 입니다 [1]. 별칭에 "SocialAccounts" 가 들어 있어서 계정 DB는 iCloud 전용이 아니라 이 사용자가 맥에 등록한 여러 인터넷 계정을 함께 담는 파일로 보이지만, 안에 어떤 계정이 들어가는지는 검체에서 확인합니다.

## 위치와 버전별 차이

```
~/Library/Preferences/MobileMeAccounts.plist
~/Library/Application Support/iCloud/Accounts/*
~/Library/Accounts/Accounts*.sqlite
~/Library/Accounts/Accounts*.sqlite-wal
```

세 위치 모두 사용자 홈 안에 있어서 사용자마다 따로 확인합니다 [1]. ForensicArtifacts 정의는 계정 DB에 대해 "Seen Accounts3.sqlite and Accounts4.sqlite" 라고 적어서, 파일 이름의 숫자가 다른 두 판이 실제로 보인다는 점까지는 확인할 수 있습니다 [1]. 어느 macOS 버전에서 `Accounts3` 에서 `Accounts4` 로 바뀌었는지는 연 자료로 확인하지 못해서, 검체에서는 `Accounts*.sqlite` 에 맞는 파일을 모두 모읍니다.

| 파일 | 이번 자료로 확인한 것 | 확인하지 못한 것 |
|---|---|---|
| `MobileMeAccounts.plist` | 위치와 "iCloud user preferences" 라는 설명 [1] | 안의 키 이름과 뜻 |
| `Application Support/iCloud/Accounts/` | 위치와 "iCloud Accounts" 라는 설명 [1] | 안의 파일 이름 규칙과 내용 |
| `Accounts*.sqlite` | 위치, `-wal` 파일, `Accounts3`·`Accounts4` 두 판 [1] | 표·칸 이름, 시각 기준, 판이 바뀐 버전 |

## 구조

`MobileMeAccounts.plist` 는 속성 목록 파일이라서 읽는 법은 [속성 목록 파일 (Property List)](../../01-foundations/data-formats/plist/index.md)을 따르고, 계정 DB는 SQLite 파일이라서 [SQLite 데이터베이스 (SQLite)](../../01-foundations/data-formats/sqlite/index.md)를 따릅니다. 두 파일 안의 키 이름과 표·칸 이름은 이번 자료로 확인하지 못해서 이 페이지에 적지 않았고, 검체에서 직접 열어 확인한 이름만 보고서에 씁니다.

계정 DB 옆에 `-wal` 파일이 있으면 아직 본 DB에 합쳐지지 않은 변경이 그 안에 있을 수 있어서, ForensicArtifacts도 두 파일을 함께 수집 대상으로 적어 둡니다 [1]. WAL을 합치는 순서와 주의점은 SQLite 페이지에서 다룹니다.

### 해석 배경: iCloud 데이터 보호

계정 흔적을 해석할 때는 그 계정의 데이터가 기기 밖에서 어떻게 보호되는지를 함께 알아야 합니다. 대부분의 iCloud 데이터는 기기에서 만든 iCloud 키로 먼저 암호화한 뒤 올라가고, 종단간 암호화 (End-to-End Encryption)가 아닌 데이터는 이 키를 Apple 데이터센터의 HSM에 올려 두어 Apple이 복구와 복호를 도울 수 있습니다 [3].

| 구분 | 표준 데이터 보호 | 고급 데이터 보호 (Advanced Data Protection) |
|---|---|---|
| 종단간 암호화 항목 수 | 15개(예: 암호와 키체인, Messages in iCloud) [2] | 지원 문서 기준 25개 [2], 보안 가이드 기준 23개 [3] |
| iCloud Drive·백업·사진·메모 | 전송 중과 서버에서 암호화하고 키는 Apple이 보관 [2] | 종단간 암호화에 들어감 [2] |
| 키 위치 | 종단간이 아닌 항목의 키는 Apple 보관 [2] | 신뢰하는 기기에 있음 [2] |

두 자료가 고급 데이터 보호의 항목 수를 다르게 적고 있어서, 숫자를 쓸 때는 출처를 함께 적습니다 [2][3]. 고급 데이터 보호를 켜도 Apple이 키를 쥔 메타데이터가 남고, iCloud 백업의 경우 기기 이름·모델·색·일련번호와 백업 스냅숏마다의 날짜·시각·크기가 여기에 들어갑니다 [2]. 서비스별로 남는 메타데이터는 각 서비스 페이지에서 다룹니다.

키체인 보호 등급 표에서 "iCloud token" 은 "After first unlock" 등급이라서, 맥을 켠 뒤 한 번 잠금을 푼 다음부터 쓸 수 있는 상태가 됩니다 [3]. 키체인 구조는 [키체인 (Keychain)](../../01-foundations/protection/keychain/index.md)에서 다룹니다.

## 증거로서 의미

**증명하는 것.** 사용자 홈에 이 파일들이 있으면 그 사용자 계정에서 iCloud 계정 설정이 만들어진 기록이 있다는 뜻이고, 계정 DB에 행이 있으면 그 사용자 홈에 계정 설정이 등록된 기록이 있다는 뜻이고, 그 행이 어떤 종류의 계정인지는 검체에서 칸을 확인한 뒤에 말합니다.

**증명하지 못하는 것.** 파일이 있다는 사실만으로 지금도 로그인해 있다거나 특정 시각에 로그인했다고 단정하지 않습니다. 로그인·로그아웃 시각이 남는 곳과 관련 통합 로그는 이번 자료로 확인하지 못했습니다. 그 계정을 실제로 쓴 사람이 누구인지도 이 파일만으로는 알 수 없어서 [그 시각에 맥을 쓴 사람이 누구인가 (User Attribution)](../../04-scenarios/activity/user-attribution.md)의 흐름으로 다른 흔적과 맞춰 봅니다.

서버에 올라간 데이터는 이 파일들에 담기지 않습니다. 표준 데이터 보호라면 Apple이 키를 보관하는 항목이 있고 고급 데이터 보호라면 키가 신뢰하는 기기에만 있어서 [2], 어느 쪽이든 맥 안에서 확인할 수 있는 흔적이 분석의 중심이 된다는 판단은 필자의 해석입니다.

보고서에는 "이 사용자 홈에 iCloud 계정 설정 파일이 있다", "계정 DB에 이 계정 이름의 행이 있다" 처럼 파일이 보여 주는 만큼만 쓰고, 칸의 뜻은 검체에서 확인한 경우에만 적습니다.

## 시각 해석

계정 DB 안 시각 칸의 이름과 기준은 확인하지 못했습니다. 검체에서 시각으로 보이는 칸을 찾으면 [맥의 시각 값 (Mac Absolute Time·Unix·HFS)](../../01-foundations/value-decoding/mac-time-values.md)의 기준을 차례로 대 보고, 알려진 다른 사건(설치 시각 등)과 맞는 기준을 고른 뒤 그 판단 근거를 보고서에 함께 적습니다.

파일 자체의 수정 시각은 이 파일이 마지막으로 바뀐 때를 알려 줄 뿐이고, 무엇이 바뀌어서 시각이 갱신됐는지는 알려 주지 않습니다. 파일 변경의 흐름은 [파일 시스템 이벤트 (FSEvents)](../filesystem/fsevents/index.md)와 함께 봅니다.

## 함정과 한계

- **판이 다른 계정 DB.** `Accounts3.sqlite` 와 `Accounts4.sqlite` 가 둘 다 보인다고 알려져 있습니다 [1]. 한 파일만 열면 다른 판에 남은 기록을 놓칩니다.
- **WAL 파일.** `-wal` 을 빼고 DB만 복사하면 최근 변경이 빠질 수 있습니다 [1].
- **관리자가 끈 기능.** iCloud Drive나 iCloud 백업은 구성 프로파일로 꺼질 수 있어서 [3], 서비스 흔적이 없을 때는 [구성 프로파일 (Configuration Profiles·MDM)](../persistence/configuration-profiles.md)에서 제한이 걸려 있었는지 먼저 봅니다.
- **항목 수가 다른 두 자료.** 고급 데이터 보호의 종단간 항목 수는 지원 문서와 보안 가이드가 다르게 적습니다 [2][3].
- **확인하지 못한 키와 칸.** 도구가 plist 키나 DB 칸에 뜻을 붙여 보여 주면, 그 뜻이 어디서 나왔는지 확인한 뒤에 씁니다.

## 직접 분석해 보기

### 헥스로 한 번

`MobileMeAccounts.plist` 를 헥스 편집기로 열어 첫 바이트가 바이너리 plist 머리말인지 XML 텍스트인지 먼저 확인합니다. 머리말을 가려내는 법과 바이너리 plist의 오프셋 표를 따라가는 법은 [속성 목록 파일 (Property List)](../../01-foundations/data-formats/plist/index.md)에서 다루고, 이 파일에 고유한 바이트 구조는 확인한 자료가 없어서 예시를 싣지 않습니다.

### 공개 도구로 한 번

사본을 만든 뒤 plist는 macOS의 `plutil` 로, 계정 DB는 `sqlite3` 로 엽니다.

```
plutil -p "MobileMeAccounts.plist"

sqlite3 "Accounts4.sqlite"
.tables
.schema
```

`.tables` 와 `.schema` 로 실제 표와 칸을 확인한 다음, 계정 이름과 계정 종류로 보이는 칸을 골라 행을 뽑습니다. `Accounts3.sqlite` 가 있으면 같은 순서로 따로 엽니다.

## 교차 검증

| 함께 볼 아티팩트 | 맞춰 볼 것 |
|---|---|
| [아이클라우드 드라이브 (iCloud Drive·CloudDocs)](icloud-drive.md) | 이 계정으로 동기화한 파일과 기기 목록 |
| [연속성과 유니버설 클립보드 (Continuity·Handoff)](continuity.md) | 같은 Apple 계정에 묶인 다른 기기와 주고받은 흔적 |
| [저장된 암호 (Passwords·iCloud Keychain)](../credentials/saved-passwords.md) | iCloud 키체인으로 동기화된 암호 |
| [사용자 계정 (Local Accounts)](../system-account/user-accounts/index.md) | iCloud 설정 파일이 어느 로컬 사용자 홈에 있는지 |
| [구성 프로파일 (Configuration Profiles·MDM)](../persistence/configuration-profiles.md) | iCloud 기능을 끄는 제한이 있었는지 |

## 실습

공개 검체(NIST CFReDS 등)의 macOS 이미지로 풀어 봅니다.

1. 사용자 홈마다 `MobileMeAccounts.plist` 가 있는지 확인하고, 있는 사용자를 적어 보세요.
2. `~/Library/Accounts/` 에 어느 판의 `Accounts*.sqlite` 가 있는지, `-wal` 파일이 함께 있는지 확인해 보세요.
3. 계정 DB의 `.schema` 를 뽑아 계정 이름과 계정 종류를 담은 것으로 보이는 칸을 찾고, 그렇게 판단한 근거를 적어 보세요.
4. 계정 DB에서 시각으로 보이는 칸 하나를 골라 유닉스 시각과 맥 절대 시각으로 각각 바꿔 보고, 어느 쪽이 검체의 다른 기록과 맞는지 따져 보세요.

## 참고 문헌

1. ForensicArtifacts, artifacts/data/macos.yaml — https://raw.githubusercontent.com/ForensicArtifacts/artifacts/main/artifacts/data/macos.yaml
2. Apple Support, "iCloud data security overview" (2026-01-05) — https://support.apple.com/en-us/102651
3. Apple Platform Security Guide (2026년 8월 판) — https://help.apple.com/pdf/security/en_US/apple-platform-security-guide.pdf
