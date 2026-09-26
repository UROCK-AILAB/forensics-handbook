---
title: "시그널"
parent: "아티팩트 · 메시지·메신저"
nav_order: 1470
---

# 시그널 (Signal)

시그널 데스크톱은 일렉트론 (Electron) 앱이라 데이터 폴더 아래 `sql/db.sqlite` 에 DB를 두고, DB 키는 사용자 설정 파일에 평문(`key`)이나 키체인에 묶인 암호문(`encryptedKey`)으로 두어서, 어느 필드가 남아 있는지로 키가 어떤 상태인지 가를 수 있습니다.

## 무엇을 기록하나 · 왜 생기나

시그널 데스크톱은 데이터 폴더를 일렉트론의 `app.getPath('userData')` 로 정하고 그 아래 `sql/db.sqlite` 에 DB를 둡니다 [3]. 짝 파일 `sql/db.sqlite-wal`, `sql/db.sqlite-shm` 도 같은 폴더에 생깁니다 [3]. 대화 기록은 이 DB에 들어 있는 것으로 보이고, 메시지 표 이름과 열은 실제 데이터로 확인합니다.

DB를 여는 키는 사용자 설정 파일(userConfig)에 두고 [3], 이 설정 파일은 데이터 폴더 아래 `config.json` 입니다 [2][6]. 키를 두는 방식은 두 가지이고, 앱이 옛 방식에서 새 방식으로 스스로 옮깁니다 [3].

일렉트론의 `safeStorage` 는 맥에서 암호화 키를 키체인 (Keychain) 에 두고, 이 키는 다른 앱이 사용자 허락 없이 불러올 수 없게 저장됩니다 [1]. 맥에서 `safeStorage` 가 제대로 동작하려면 앱이 코드 서명돼 있어야 하고 [1], 키 저장 백엔드를 고르는 `getSelectedStorageBackend()` 는 리눅스 전용이라 맥은 키체인, 윈도우는 DPAPI로 정해져 있습니다 [1]. `safeStorage` 가 만드는 키체인 항목의 이름(서비스·계정 이름)은 공식 문서에 나오지 않아서, 시그널의 항목 이름은 실제 키체인에서 확인합니다. 키체인의 구조는 [키체인 (Keychain)](../../01-foundations/protection/keychain/index.md)에서 다룹니다.

## 위치와 버전별 차이

| 기록 | 위치 |
|---|---|
| 데이터 폴더 | `app.getPath('userData')` 가 돌려주는 폴더 [3]. 일렉트론은 앱이 따로 바꾸지 않으면 맥에서 이 폴더를 `~/Library/Application Support/` 아래 앱 이름 폴더로 둡니다 [8]. 맥 실제 경로 후보는 `~/Library/Application Support/Signal/` 이고, 앱 이름 폴더가 `Signal` 인지는 실제 기기에서 확인합니다 |
| 메시지 DB | 데이터 폴더 아래 `sql/db.sqlite` [3] |
| DB 짝 파일 | 데이터 폴더 아래 `sql/db.sqlite-wal`, `sql/db.sqlite-shm` [3] |
| 사용자 설정 파일 | 데이터 폴더 아래 `config.json` [6] |
| 첨부 파일 폴더 | 데이터 폴더 아래 `attachments.noindex` [7]. `avatars.noindex`, `stickers.noindex`, `drafts.noindex`, `downloads.noindex` 폴더도 있습니다 [7] |

DB 키를 두는 방식은 시그널 데스크톱 버전에 따라 다르고, 새 방식이 들어온 버전은 공개 자료가 없습니다. macOS 10.15 Catalina 이후 맥 버전에 따라 경로가 바뀐다는 공개 자료도 없습니다.

| 방식 | 설정 파일의 필드 | 내용 [3] |
|---|---|---|
| 옛 방식 | `key` | 키를 평문으로 둡니다. 소스는 이 값을 `userConfig.get('key')` 로 읽고 "legacyKeyValue" 라고 부릅니다 |
| 새 방식 | `encryptedKey` | `safeStorage.encryptString(key).toString('hex')` 로 암호화한 키를 16진 문자열로 둡니다 |
| 새 방식으로 옮긴 뒤 | `key` 없음 | `userConfig.set('key', undefined)` 로 평문 필드를 지웁니다 |
| `safeStorage` 를 쓸 수 없을 때 | `key` | `userConfig.set('key', key)` 로 평문 키를 그대로 남깁니다 |

리눅스에서는 `safeStorageBackend` 필드에 백엔드 이름을 적고 백엔드가 `basic_text` 면 암호화를 쓰지 않지만 [3], 맥에는 해당하지 않습니다.

## 구조

데이터 폴더의 구조는 아래와 같습니다.

```
(app.getPath('userData') 가 돌려주는 폴더)
├── sql/
│   ├── db.sqlite        메시지 DB [3]
│   ├── db.sqlite-wal    짝 파일 [3]
│   └── db.sqlite-shm    짝 파일 [3]
├── attachments.noindex/ 첨부 파일 [7]
└── config.json          key 또는 encryptedKey 칸 [3][6]
```

`db.sqlite` 안의 표 구조는 실제 데이터로 확인합니다. `messages` 표와 `sent_at`, `received_at`, `conversationId`, `body`, `json`, `type` 같은 열이 있다는 설명과, 이 키로 DB를 여는 방식이 SQLCipher 라는 설명이 흔하지만, 표를 열어 실제 이름을 본 뒤에 씁니다. SQLite 파일과 WAL 의 일반 구조는 [SQLite 데이터베이스 (SQLite)](../../01-foundations/data-formats/sqlite/index.md)를 따릅니다.

> 그림 자리: 설정 파일의 `key`·`encryptedKey` 필드와 키체인, `sql/db.sqlite` 사이의 관계를 옛 방식·새 방식·`safeStorage` 를 못 쓴 경우 세 경우로 나눠 보여 주는 그림

## 증거로서 의미

**증명하는 것.** 데이터 폴더와 `sql/db.sqlite` 가 있으면 그 계정에서 시그널 데스크톱을 설치하고 실행한 정황이 됩니다. 설정 파일에 `encryptedKey` 만 있으면 DB 키가 `safeStorage` 로 암호화돼 그 사용자의 키체인에 묶여 있는 상태이고, 평문 `key` 가 남아 있으면 옛 버전을 쓰고 있었거나 `safeStorage` 를 쓰지 못한 경우입니다 [1][3]. 이 판단은 해석이라서, 보고서에는 "설정 파일에 이 필드가 있다" 는 관찰과 그 해석을 나눠 적습니다.

**증명하지 못하는 것.** DB를 열지 못하면 대화 상대·내용·시각은 말할 수 없고, `db.sqlite` 가 바뀐 시각은 앱이 DB에 쓴 때일 뿐 특정 메시지를 보낸 때가 아닙니다. 평문 `key` 가 있다는 사실만으로는 두 경우(옛 버전, `safeStorage` 를 못 씀) 가운데 어느 쪽인지 가를 수 없고, `encryptedKey` 가 있다고 해서 키체인 항목이 지금도 남아 있다는 뜻도 아닙니다. 보고서에는 "시그널로 대화했다" 보다 "이 계정에 시그널 데스크톱 DB가 있고, 설정 파일에는 DB 키가 `encryptedKey` 형태로 남아 있다" 처럼 기록으로 확인되는 만큼만 씁니다.

## 시각 해석

메시지 표의 시각 열은 유닉스 시각 밀리초를 쓴다는 설명이 흔하지만, 표를 열 수 있게 되면 시각으로 보이는 열의 자릿수를 보고 초·밀리초를 구분합니다. 13자리 안팎이면 밀리초, 10자리 안팎이면 초를 먼저 의심하고, 기준끼리의 관계는 [맥의 시각 값 (Mac Absolute Time·Unix·HFS)](../../01-foundations/value-decoding/mac-time-values.md)을 따릅니다. `sql/db.sqlite`·설정 파일의 파일 시스템 시각은 앱이 파일에 쓴 때를 보여 주므로, 메시지 시각과 섞지 않고 값마다 뜻을 적어 둡니다. 현지 시각으로 옮길 때는 [시간대와 시계 설정 (Time Zone·NTP)](../system-account/time-zone.md)에서 확인한 시간대를 적용합니다.

## 함정과 한계

- **WAL 파일을 빼먹는 경우.** DB 옆에 `-wal`·`-shm` 짝 파일이 있어서 [3], `db.sqlite` 만 복사하면 최근 메시지가 빠질 수 있습니다. WAL 동작은 [SQLite 데이터베이스 (SQLite)](../../01-foundations/data-formats/sqlite/index.md)에서 다룹니다.
- **설정 파일을 빼먹는 경우.** DB 키가 DB가 아니라 설정 파일에 있어서 [3], `sql/` 폴더만 수집하면 키 상태를 판단할 근거가 사라집니다. 데이터 폴더를 통째로 수집합니다.
- **키체인을 빼먹는 경우.** `encryptedKey` 만 있는 기기에서는 키가 사용자 키체인에 묶여 있어서 [1][3], 키체인을 수집 범위에 넣었는지가 뒤의 분석 범위를 정합니다. 수집 방법은 [맥 증거 확보 (Acquisition)](../../03-techniques/process-acquisition/evidence-acquisition/index.md)를 봅니다.
- **맥 경로를 확정된 것처럼 쓰는 경우.** 데이터 폴더를 정하는 방식은 소스에 있지만 맥의 실제 경로는 후보라서, 보고서에는 실제 기기에서 찾은 경로를 씁니다.
- **수집 정의만 믿는 경우.** ForensicArtifacts 메신저 정의 파일은 시그널을 다루지만, 맥(Darwin) 정의로 알려진 것은 스카이프뿐이라 시그널 항목이 맥에도 쓰이는지는 정의 파일에서 직접 봅니다 [4].
- **지우기와 조작.** 앱을 지웠거나 데이터 폴더를 비운 정황은 [증거를 없애려 했나 (Anti-Forensics)](../../04-scenarios/activity/anti-forensics/index.md)의 방법으로 판단합니다.

## 직접 분석해 보기

원본을 바로 열지 않고 데이터 폴더 전체를 작업 폴더로 복사한 뒤 사본에서 봅니다.

### 헥스로 한 번

`config.json` 을 헥스 편집기나 텍스트 보기로 열어 `key` 와 `encryptedKey` 가운데 어느 필드가 있는지 봅니다. `encryptedKey` 값은 `safeStorage` 가 만든 암호문 바이트를 `toString('hex')` 로 적은 16진 문자열이라서 [3], 글자 두 개가 한 바이트입니다. 아래 값은 명세에 맞춰 만든 예시이고, 실제 데이터에서 나온 값이 아닙니다.

```
encryptedKey 칸의 16진 문자열 (예시, 앞부분만)
"a1b2c3d4e5f6..."

글자 두 개씩 끊어 바이트로 읽으면
a1 b2 c3 d4 e5 f6 ...
```

문자열 길이를 2로 나누면 암호문 바이트 수가 나오고, 그 바이트의 내부 구조는 공식 문서에 나오지 않습니다. 이어서 `sql/db.sqlite` 의 첫 줄을 열어 SQLite 파일 머리 모양인지 봅니다. 머리 모양은 [SQLite 데이터베이스 (SQLite)](../../01-foundations/data-formats/sqlite/index.md)에 있고, 그 모양이 보이지 않으면 파일 전체가 암호화된 정황으로 적어 두되 암호 방식은 확인되지 않았다고 함께 씁니다.

### 공개 도구로 한 번

공개 도구 sigtop 은 시그널 데스크톱 데이터를 내보내는 도구이고, 맥에는 Homebrew 로 설치합니다 [5]. 맥에서 데이터 폴더를 찾고 키를 다루는 방식은 README 가 아닌 설명서(`sigtop.1`)에 있습니다 [5]. 도구 결과를 보고서에 쓰기 전에 [도구 검증 (Tool Validation)](../../03-techniques/reporting/tool-validation.md)의 방법으로 같은 데이터로 결과를 확인하고, 설정 파일의 필드 상태와 파일 시각은 도구 없이 직접 본 값으로 적습니다.

## 교차 검증

- [키체인 (Keychain)](../../01-foundations/protection/keychain/index.md) — `encryptedKey` 를 쓰는 기기에서 키가 묶인 사용자 키체인을 확인합니다.
- [서명·공증·무결성 보호 (Code Signing·Notarization·SIP)](../../01-foundations/protection/codesign-notarization-sip.md), [앱 번들 정보 (Info.plist·Code Signature)](../embedded-metadata/app-bundle.md) — `safeStorage` 가 기대하는 코드 서명과 설치된 앱의 버전을 봅니다.
- [설치한 앱과 영수증 (Applications·Receipts)](../system-account/installed-apps-receipts.md) — 시그널이 언제 설치됐는지 봅니다.
- [KnowledgeC (knowledgeC.db)](../execution/knowledgec/index.md), [바이옴 (Biome)](../execution/biome/index.md) — 앱을 쓴 시간대를 봅니다.
- [파일 시스템 이벤트 (FSEvents)](../filesystem/fsevents/index.md) — `sql/db.sqlite` 와 설정 파일이 언제 바뀌었는지 봅니다.
- [정보 탈취 악성 코드 (Infostealer)](../../04-scenarios/incident/infostealer.md) — 메신저 데이터 폴더와 키체인에 다른 프로그램이 손댄 흔적을 볼 때 씁니다.
- [누구와 연락을 주고받았나 (Communication)](../../04-scenarios/activity/communication.md) — 이 기록을 쓰는 조사 흐름입니다.

## 실습

NIST CFReDS 같은 공개 시험 이미지 가운데 시그널 데스크톱을 쓴 맥 이미지를 골라 아래 질문을 풀어 봅니다.

1. 이미지에서 시그널 데이터 폴더는 어디에 있나요? 이 페이지의 후보 경로와 같나요?
2. `sql/` 폴더에 `db.sqlite`, `db.sqlite-wal`, `db.sqlite-shm` 가 모두 있나요? 각 파일의 크기와 마지막 수정 시각은 어떤가요?
3. `config.json` 에 `key` 와 `encryptedKey` 가운데 어느 필드가 있나요? 그 상태로 보아 옛 방식, 새 방식, `safeStorage` 를 못 쓴 경우 가운데 어디에 해당하나요?
4. `encryptedKey` 가 있다면 16진 문자열의 길이로 암호문이 몇 바이트인지 계산해 보세요.
5. `sql/db.sqlite` 의 첫 줄이 SQLite 파일 머리 모양인가요? 판단 근거를 적어 보세요.

## 참고 문헌

1. Electron 문서, safeStorage — https://www.electronjs.org/docs/latest/api/safe-storage
2. signalapp/Signal-Desktop, `app` 폴더 목록 — https://github.com/signalapp/Signal-Desktop/tree/main/app
3. signalapp/Signal-Desktop, `app/main.main.ts` — https://raw.githubusercontent.com/signalapp/Signal-Desktop/main/app/main.main.ts
4. ForensicArtifacts, instant_messaging.yaml — https://raw.githubusercontent.com/ForensicArtifacts/artifacts/main/artifacts/data/instant_messaging.yaml
5. tbvdm/sigtop 저장소 첫 화면 — https://github.com/tbvdm/sigtop
6. signalapp/Signal-Desktop, `app/user_config.main.ts` — https://raw.githubusercontent.com/signalapp/Signal-Desktop/main/app/user_config.main.ts
7. signalapp/Signal-Desktop, `app/attachments.node.ts` — https://github.com/signalapp/Signal-Desktop/blob/main/app/attachments.node.ts
8. Electron 문서, app (`getPath` 의 `appData`·`userData`) — https://www.electronjs.org/docs/latest/api/app
