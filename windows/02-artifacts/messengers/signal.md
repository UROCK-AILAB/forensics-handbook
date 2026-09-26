---
title: "시그널"
parent: "아티팩트 · 메신저"
nav_order: 2110
---

# 시그널 (Signal)

> 위치: 아티팩트 사전 > 메신저

시그널 데스크톱은 Electron 앱이고, 사용자 데이터를 `C:\Users\<사용자>\AppData\Roaming\Signal\` 에 둡니다.
대화방·메시지·첨부 파일 정보는 `sql\db.sqlite` 에 있고, 이 DB 는 SQLCipher 로 암호화돼 있습니다. DB 키는 같은 폴더의 `config.json` 에 있습니다. 옛 방식은 키를 평문 `key` 필드에 적었고, 지금 소스는 키를 암호화해 `encryptedKey` 필드에 적습니다. Windows 에서 이 암호화의 키는 DPAPI 로 만들기 때문에, `encryptedKey` 만 있는 이미지에서는 그 사용자의 DPAPI 를 풀어야 DB 키를 얻습니다.

## 무엇을 기록하나 · 왜 생기나

시그널 데스크톱은 대화를 PC 의 로컬 DB 인 `sql\db.sqlite` 에 저장하고, 이 DB 를 SQLCipher 로 암호화합니다. SQLCipher 형식은 [SQLite 데이터베이스](../../01-foundations/database-log-formats/sqlite/index.md) 에서 다룹니다. DB 를 여는 키는 `config.json` 에 두고, 연락처와 대화 상대의 프로필 사진, 첨부 파일은 `attachments.noindex\` 에, 앱 로그는 `logs\` 에 둡니다.

시그널 데스크톱은 Electron 의 `safeStorage` 를 불러 쓰며, Electron 앱이라서 Chromium 공통 폴더도 생깁니다. 공통 폴더는 [Electron·WebView2 앱 데이터 위치](../../01-foundations/app-mail-data/chromium-electron-webview2/teams-discord-slack.md) 에서 다룹니다.

## 위치와 버전별 차이

### 폴더 위치

| 항목 | 위치 | 근거 |
|---|---|---|
| 사용자 데이터 폴더 | `C:\Users\<사용자>\AppData\Roaming\Signal\` | 수집 정의 파일 |
| 프로그램 설치 폴더 | 알려진 바로는 `%LOCALAPPDATA%\Programs\signal-desktop\` (버전마다 확인 필요) | 공개 자료 없음 |

`%APPDATA%` 는 사용자마다 따로 있으므로 사용자 프로필마다 봅니다.

### 폴더·파일별 내용

| 파일·폴더 | 내용 | 근거 |
|---|---|---|
| `sql\db.sqlite` | 첨부 파일 정보·대화방·메시지 등이 든 DB. SQLCipher 로 암호화 | 수집 정의 파일 |
| `sql\db.sqlite-wal`, `sql\db.sqlite-shm` | WAL 짝 파일. 앱이 `config.json` 과 함께 파일 권한을 챙기는 목록에 들어 있습니다 | 소스 코드 |
| `config.json` | DB 키 | 수집 정의 파일, 소스 코드 |
| `attachments.noindex\` | 연락처·대화 상대의 프로필 사진. 첨부 파일이 있을 수 있음 | 수집 정의 파일 |
| `logs\` | 시그널 로그. 가장 최근 것은 확장자 `.log`, 예전 것은 `.log.0`, `.log.1` … | 수집 정의 파일 |

### 버전별 차이 — 키를 적는 필드

| 방식 | `config.json` 의 키 필드 |
|---|---|
| 옛 방식 | `key` 에 평문 키 |
| 새 방식 | `encryptedKey` 에 암호화한 키 |

옛 수집 정의 파일에는 "`config.json` 에 `db.sqlite` 의 SQLCipher 원시 키 (Raw Key) 가 있다" 고 나오는데, 이 설명은 평문 `key` 시절 기준입니다. 그래서 옛 자료만 보고 `config.json` 에서 평문 키를 기대하면 틀릴 수 있습니다.

## 구조

### config.json 의 키 필드 (소스 코드 기준)

아래 동작은 Signal-Desktop 소스의 `getSQLKey` 함수 기준입니다.

앱이 읽는 키 필드는 옛 방식 `key` 와 새 방식 `encryptedKey` 두 개입니다. `encryptedKey` 는 키를 `safeStorage.encryptString` 으로 암호화한 결과를 16진수 문자열로 적은 값입니다.

앱은 시작할 때 아래 순서로 키를 정합니다.

| `config.json` 상태 | 앱이 하는 일 |
|---|---|
| `encryptedKey` 가 있음 | `safeStorage.decryptString` 으로 풀어 씁니다. 암호화를 쓸 수 없는 환경이면 키를 풀 수 없다는 오류를 냅니다 |
| `key` 만 있고 암호화를 쓸 수 있음 | `encryptedKey` 를 새로 쓰고 `key` 를 지웁니다 |
| `key` 만 있고 Flatpak(리눅스) 환경 | `encryptedKey` 를 쓰고 `key` 도 남깁니다 |
| 두 필드가 모두 있고 푼 값이 같음 | `key` 를 지웁니다 |
| 암호화를 쓸 수 없음 | 평문 `key` 로 저장합니다 |

`safeStorageBackend` 필드는 리눅스에서만 쓰는데, 같은 Windows PC 라도 이미지를 뜬 시점에 따라 `config.json` 에 평문 `key` 가 있을 수도, `encryptedKey` 만 있을 수도 있습니다(해석).

### Windows 의 safeStorage

Windows 에서 safeStorage 의 암호화 키는 DPAPI 로 만듭니다. 이렇게 암호화한 값은 대개 같은 로그온 자격 증명으로 로그온한 사용자만 풀 수 있습니다. 그래서 같은 PC 의 다른 사용자로부터는 보호되지만, 같은 사용자 공간에서 도는 다른 앱으로부터는 보호되지 않습니다. Windows 에서 `isEncryptionAvailable()` 은 앱이 `ready` 이벤트를 낸 뒤 true 를 돌려줍니다.

safeStorage 가 값마다 DPAPI 를 직접 쓰는지, Chromium 처럼 `Local State` 파일에 둔 키를 DPAPI 로 감싸는지는 공개 문서에 나오지 않으므로 실제 데이터로 확인합니다(아래 "헥스로 한 번"). 사용자 DPAPI 의 마스터 키와 푸는 조건은 [DPAPI 구조](../../01-foundations/protection/data-protection-api/index.md) 에서 다룹니다.

### DB 파일

`db.sqlite` 는 SQLCipher 로 암호화한 SQLite 파일입니다. 여는 설정은 키를 원시 키로 넣고, 나머지는 SQLCipher 4 기본값으로 둡니다. SQLCipher 의 페이지 배치와 버전별 기본값은 [SQLite 데이터베이스](../../01-foundations/database-log-formats/sqlite/index.md) 에서 다룹니다.

`-wal`·`-shm` 짝 파일이 함께 생기며, 본 파일에 아직 옮겨지지 않은 페이지가 WAL 에 있을 수 있으므로 세 파일을 함께 수집합니다. 알려진 바로는 DB 안에 `messages`, `conversations` 같은 표가 있습니다(버전마다 확인 필요).

### 첨부 파일

`attachments.noindex\` 에는 프로필 사진과 첨부 파일이 있을 수 있습니다. 첨부 파일을 디스크에 암호화해 저장하는지는 버전마다 다를 수 있으므로, 파일 앞머리로 평문 이미지·문서인지 먼저 봅니다.

### 디스크 이미지만으로 풀리나

| `config.json` 상태 | DB 를 열려면 |
|---|---|
| 평문 `key` 가 있음 | 키가 파일에 그대로 있습니다. 원시 키로 넣고 SQLCipher 4 기본값으로 엽니다 |
| `encryptedKey` 만 있음 | 그 사용자의 DPAPI 를 풀어야 키를 얻습니다. 푸는 데 필요한 재료는 [DPAPI 구조](../../01-foundations/protection/data-protection-api/index.md) 에서 다룹니다 |
| 두 필드가 모두 있음 | 평문 `key` 로 먼저 열어 봅니다 |
| `config.json` 이 없음 | 디스크에서 DB 키를 얻을 자리가 없습니다(해석). 섀도 복사본과 지운 파일에서 예전 `config.json` 을 찾습니다 |

## 증거로서 의미

| 증명하는 것 | 증명하지 못하는 것 |
|---|---|
| 사용자 프로필에 `Signal` 폴더가 있으면, 그 Windows 계정에서 시그널 데스크톱이 실행된 적이 있습니다 | 누가 그 계정으로 앱을 조작했는지 |
| DB 를 열면, 이 PC 의 앱에 저장된 대화방·메시지·첨부 파일 정보가 보입니다 | 이 PC 에 남지 않은 대화. 다른 기기에서만 주고받은 대화가 있을 수 있습니다 |
| `attachments.noindex\` 에 파일이 있으면 그 파일이 이 PC 에 있었습니다 | DB 를 열지 못했을 때, 그 파일이 어느 대화의 것인지 |
| `config.json` 의 키 필드는 이미지 시점의 키 저장 방식을 보여 줍니다 | 키 필드만으로 앱 버전 |
| `logs\` 에는 앱 동작 기록이 남습니다 | DB 를 못 열었을 때 대화가 없었다는 것 |

### 보고서 문장

아래 사용자 이름과 개수는 설명을 위해 만든 예입니다.

- 쓸 수 있는 문장: "사용자 A 프로필의 시그널 `config.json` 에는 `encryptedKey` 필드만 있습니다. 사용자 A 의 DPAPI 를 풀지 못해 `db.sqlite` 의 내용은 확인하지 못했습니다. `attachments.noindex\` 에는 파일 42개가 있습니다."
- 쓰면 안 되는 문장: "사용자 A 는 시그널로 파일 42개를 주고받았습니다."

## 시각 해석

| 시각 | 자리 | 무엇이 바뀔 때 바뀌나 | 기준 |
|---|---|---|---|
| 메시지 시각 | DB 안의 시각 열 | 공개 자료 없음 | 알려진 바로는 밀리초 단위 유닉스 시각(버전마다 확인 필요) |
| `config.json` 수정 시각 | 파일 시스템 | 앱이 파일을 다시 쓸 때 | UTC |
| `db.sqlite`·`-wal` 수정 시각 | 파일 시스템 | 앱이 DB 에 쓸 때 | UTC |
| 로그 파일 시각 | 파일 시스템, 로그 줄 | 앱이 로그를 쓸 때 | 로그 줄의 형식은 실제 데이터로 확인 |

유닉스 시각은 UTC 기준입니다. 밀리초 단위 값을 푸는 법은 [시각 값 형식](../../01-foundations/value-decoding/filetime-unix-webkit-dos-ole.md) 에 있습니다.

앱은 `key` 를 `encryptedKey` 로 옮길 때 `config.json` 을 다시 쓰므로, `config.json` 의 수정 시각은 옮긴 때이거나 그 뒤 다른 이유로 다시 쓴 때입니다(해석). 가장 최근 로그는 `.log`, 예전 로그는 `.log.0`, `.log.1` … 입니다. 로그 파일마다 파일 시스템 시각을 적어 두면 로그가 넘어간 시점을 추정할 수 있습니다.

## 함정과 한계

- **옛 자료대로 평문 키를 기대합니다.** 지금 소스는 암호화를 쓸 수 있으면 평문 `key` 를 지웁니다.
- **`db.sqlite` 만 수집합니다.** `-wal`·`-shm`·`config.json` 을 함께 수집합니다. 로그의 `.log.0`, `.log.1` 도 함께 수집합니다.
- **다른 사용자의 DPAPI 로 풀려고 합니다.** safeStorage 는 같은 로그온 자격 증명으로 로그온한 사용자만 대개 풀 수 있습니다. `Signal` 폴더가 있는 그 사용자의 DPAPI 를 풉니다. SID 와 사용자는 [사용자 프로필 목록](../system-account/profilelist.md) 에서 맞춥니다.
- **`Local State` 를 거친다고 단정합니다.** safeStorage 가 Windows 에서 키를 어떻게 보관하는지는 공개 문서에 나오지 않습니다. 아래 "헥스로 한 번" 처럼 값을 직접 봅니다.
- **safeStorage 를 강한 보호로 봅니다.** 같은 사용자 공간에서 도는 다른 앱으로부터는 보호되지 않습니다. 사용자 권한으로 도는 악성 프로그램도 키를 풀 수 있다는 뜻입니다(해석).
- **암호문에서 지운 레코드를 찾습니다.** 페이지가 암호화돼 있어서 풀기 전에는 지운 레코드를 찾을 수 없습니다. DB 를 푼 뒤 [SQLite 데이터베이스](../../01-foundations/database-log-formats/sqlite/index.md) 의 방법으로 찾습니다.
- **첨부 파일을 모두 평문으로 봅니다.** 첨부 파일을 디스크에 암호화하는지는 버전마다 확인합니다.
- **폴더를 지웠다고 끝으로 봅니다.** 예전 `config.json` 이 [볼륨 섀도 복사본](../../03-techniques/analysis/volume-shadow-copy-analysis.md) 이나 지운 파일 영역에 남았을 수 있습니다(해석). 지운 파일은 [삭제 데이터 복구](../../03-techniques/analysis/data-recovery/index.md) 방법으로 찾습니다.

## 직접 분석해 보기

### 텍스트로 한 번 — config.json

`config.json` 은 텍스트 파일입니다. 헥스 대신 텍스트로 봅니다.
아래는 소스 코드의 필드 이름으로 만든 예시입니다. 값은 자리표시이고 실제 데이터에서 나온 값이 아닙니다. 실제 파일에는 다른 필드가 더 있을 수 있습니다.

옛 방식:

```json
{
  "key": "<평문 키>"
}
```

새 방식:

```json
{
  "encryptedKey": "<safeStorage 로 암호화한 값을 16진수로 적은 문자열>"
}
```

1. `config.json` 을 텍스트 편집기로 엽니다.
2. `key` 와 `encryptedKey` 중 어느 필드가 있는지 적습니다.
3. `key` 가 있으면 그 값이 DB 키입니다.
4. `encryptedKey` 만 있으면 16진수 문자열을 바이트로 바꿉니다.

### 헥스로 한 번 — 암호문과 DB

1. 4번에서 바꾼 바이트를 헥스 편집기로 봅니다.
2. 이 바이트가 DPAPI 블롭 모양인지 [DPAPI 구조](../../01-foundations/protection/data-protection-api/index.md) 의 블롭 구조와 맞춰 봅니다.
3. DPAPI 블롭 모양이면 값마다 DPAPI 를 직접 쓴 것으로 봅니다. 아니면 다른 키를 거친 것으로 보고 `Signal` 폴더의 `Local State` 를 봅니다.
4. `sql\db.sqlite` 의 앞 16바이트를 봅니다. SQLite 헤더 문자열이 없고 무작위 바이트로 보이면 SQLCipher 로 암호화된 상태입니다.
5. `-wal` 파일 크기가 0 보다 크면 본 DB 에 아직 옮겨지지 않은 페이지가 있을 수 있습니다. 함께 엽니다.

### 공개 도구로 한 번

아래 도구는 예로만 듭니다.

| 도구 | 쓰임 |
|---|---|
| 텍스트 편집기, JSON 조회 도구(jq 등) | `config.json` 의 키 필드를 봅니다 |
| 오프라인 DPAPI 복호 도구 | 그 사용자의 DPAPI 를 풀어 `encryptedKey` 를 풉니다 |
| SQLCipher 를 지원하는 SQLite 도구 | 원시 키와 SQLCipher 4 기본값으로 `db.sqlite` 를 엽니다 |

DB 를 연 뒤에는 도구가 보여 주는 메시지 수와 표의 행 수를 맞춰 봅니다.
방법은 [도구 결과 교차 검증](../../03-techniques/reporting/tool-validation.md) 에서 다룹니다.

## 교차 검증 — 함께 볼 아티팩트

| 아티팩트 | 맞춰 볼 점 |
|---|---|
| [DPAPI 구조](../../01-foundations/protection/data-protection-api/index.md) | 그 사용자의 마스터 키 파일이 이미지에 있는지 |
| [사용자 프로필 목록](../system-account/profilelist.md) | `Signal` 폴더가 있는 프로필의 SID |
| [크롬 계열 앱 공통 구조](../../01-foundations/app-mail-data/chromium-electron-webview2/index.md) | `Signal` 폴더의 `Local State` 에 암호화 키 필드가 있는지 |
| [프리페치](../execution/prefetch/index.md) · [AmCache](../execution/amcache-hve/index.md) | 시그널 실행 파일의 경로와 실행 시각 |
| [SRUM](../execution/system-resource-usage-monitor/index.md) | 시그널 앱의 네트워크 사용량 기록이 있는지 |
| [윈도 알림 기록](../execution/wpndatabase-db.md) | 시그널 알림이 남았는지 |
| [볼륨 섀도 복사본 구조](../../01-foundations/disk-volume/volume-shadow-copy.md) | 예전 시점의 `config.json` 에 평문 `key` 가 남았는지 |

- 대화 DB 를 암호화하는 다른 메신저는 [텔레그램](telegram.md), [왓츠앱 데스크톱](whatsapp-desktop.md), [카카오톡 PC](kakaotalk-pc/index.md) 페이지를 봅니다.
- 암호화된 증거를 다루는 순서는 [암호화 증거 다루기](../../03-techniques/analysis/encrypted-evidence/index.md) 에서 다룹니다.
- 조사 전체 흐름은 [누구와 연락을 주고받았나](../../04-scenarios/activity/communication-reconstruction.md) 에서 다룹니다.

## 실습

시그널 데스크톱이 든 공개 시험 이미지는 알려진 것이 없습니다. Windows 가상 머신에 시그널 데스크톱을 설치해 직접 시험하고, 시험 전에 앱 버전과 Windows 버전을 적어 둡니다.

1. 새로 설치하고 처음 실행한 뒤 `config.json` 에 어떤 키 필드가 있습니까?
2. `sql\db.sqlite` 의 앞 16바이트는 평문 SQLite 헤더입니까?
3. `encryptedKey` 값을 바이트로 바꾸면 DPAPI 블롭 모양입니까? 아니면 다른 모양입니까?
4. 다른 Windows 사용자로 로그온해 같은 `config.json` 을 풀려고 하면 어떻게 됩니까?
5. 시험 메시지를 보낸 시각을 적어 두고, DB 를 연 뒤 그 메시지의 시각 열과 맞춥니다. 단위는 무엇입니까?
6. 사진을 받은 뒤 `attachments.noindex\` 에 생긴 파일의 앞머리는 평문 이미지입니까?
7. 섀도 복사본을 만든 뒤 앱을 업데이트합니다. 섀도 복사본의 `config.json` 과 지금의 `config.json` 이 다릅니까?

## 참고 문헌

- KapeFiles, *Targets/Apps/Signal.tkape* (작성 Matt Dawson, 버전 1.0) — https://raw.githubusercontent.com/EricZimmerman/KapeFiles/master/Targets/Apps/Signal.tkape
- Signal-Desktop 소스, *app/main.main.ts* (main 브랜치, 2026-09-23 받음. `getSQLKey` 함수와 파일 권한 목록) — https://raw.githubusercontent.com/signalapp/Signal-Desktop/main/app/main.main.ts
- Electron docs, *safeStorage* — https://www.electronjs.org/docs/latest/api/safe-storage
