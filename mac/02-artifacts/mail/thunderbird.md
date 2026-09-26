---
title: "썬더버드"
parent: "아티팩트 · 메일"
nav_order: 1330
---

# 썬더버드 (Thunderbird)

썬더버드는 메일함마다 요약 파일 `.msf` 를 Mork 형식으로 두고, 예전 버전은 주소록 `.mab` 도 같은 Mork 형식으로 저장했습니다 [1]. 맥에서의 프로필 위치와 메일 파일 구성은 널리 알려진 후보 값이라 실제 데이터로 확인해야 합니다.

## 무엇을 기록하나 · 왜 생기나

`.msf` 는 메일함 하나의 요약(색인) 파일이고 Mork 형식으로 쓰여 있습니다 [1]. Mork 는 David McCusker 가 Netscape·Mozilla 용으로 만든 형식이고, 텍스트처럼 보이지만 사람이 읽기 어렵고 파싱이 까다롭다는 비판을 받았습니다 [1]. 주소록 `.mab` 파일도 Mork 형식이었지만, 썬더버드 78 부터는 주소록을 SQLite DB 로 저장하고 기존 `.mab` 주소록은 변환합니다 [2].

썬더버드 3.0 때 Mork 를 SQLite(MozStorage)로 바꾸려는 계획이 있었지만, 2025년 기준으로도 Mork 형식은 계속 쓰이고 있었고, 썬더버드에서는 메일함 요약 `.msf` 가 그 예입니다 [1]. 같은 Mozilla 계열인 파이어폭스는 버전 7(2011)에서 Mork 를 완전히 없앴는데 [1], 썬더버드 프로필에는 Mork 파일이 계속 남아 있어서 SQLite 만 읽는 도구로는 메일함 요약 파일을 읽지 못합니다. 파이어폭스 쪽 구조는 [파이어폭스 (Firefox)](../browsers/firefox.md)에서 다룹니다.

## 위치와 버전별 차이

아래는 널리 알려진 후보 위치입니다. 분석 대상에 실제로 있는지 먼저 보고, 확인한 것만 보고서에 씁니다.

```
~/Library/Thunderbird/profiles.ini
~/Library/Thunderbird/installs.ini
~/Library/Thunderbird/Profiles/<무작위8자>.<이름>/
~/Library/Caches/Thunderbird/Profiles/<프로필>/
```

| 후보 | 알려진 내용 | 확인 |
|---|---|---|
| `profiles.ini` | 프로필 목록. `IsRelative=0` 과 `Path=` 가 있으면 프로필이 다른 경로에 있다는 뜻 | 확인 필요 |
| `Profiles/` 아래 폴더 | `xxxxxxxx.default` 나 `.default-release` 같은 이름의 프로필 폴더 | 확인 필요 |
| `Caches/Thunderbird/` | 프로필과 따로 있는 캐시 | 확인 필요 |

`profiles.ini` 는 프로필이 어디 있는지 알려 주는 파일로 알려져 있어서, 후보 폴더에 프로필이 없으면 이 파일의 `Path=` 값을 따라가 휴대용 프로필이나 다른 경로의 프로필이 있는지 봅니다.

macOS 버전에 따라 저장 구조가 달라지는지는 공개 자료에 없습니다. 썬더버드 버전에 따른 차이로 알려진 것은 주소록 형식입니다.

| 썬더버드 버전 | 주소록 형식 | 출처 |
|---|---|---|
| 78 이전 | `.mab` (Mork) | [1] |
| 78 이후 | SQLite (기존 `.mab` 는 변환) | [2] |

변환 뒤에 예전 `.mab` 파일이 프로필에 남는지는 실제 데이터로 확인합니다. 분석할 때는 macOS 버전과 함께 썬더버드 버전을 먼저 적어 둡니다.

## 구조

### 메일함과 요약 파일

프로필 안의 메일 파일은 아래처럼 놓인다고 알려져 있고, 모두 실제 데이터로 확인할 후보입니다.

| 후보 | 알려진 내용 |
|---|---|
| `Mail/` | 로컬 폴더와 POP 메일 |
| `ImapMail/<서버 이름>/` | IMAP 메일 |
| 확장자 없는 파일 (예: `Inbox`, `Sent`) | 메일함 하나의 mbox 파일. 같은 이름의 `.msf` 가 짝 |
| `<이름>.sbd/` | 하위 메일함을 담는 폴더 |

메일당 파일 하나로 저장하는 Maildir 방식도 고를 수 있고 기본값은 mbox 라고 알려져 있습니다. 분석 대상의 메일함 폴더 안에 파일이 메일 수만큼 있으면 Maildir 방식으로 보고 읽습니다.

`.msf` 는 mbox 에서 다시 만들 수 있는 색인이라 지우면 썬더버드가 다시 만든다고 알려져 있습니다. 그렇다면 `.msf` 에 메일이 없다는 사실로 mbox 에도 메일이 없다고 말할 수 없어서, 메일 여부는 mbox 쪽을 직접 열어 판단합니다.

### 프로필의 다른 파일

| 후보 파일 | 알려진 내용 |
|---|---|
| `global-messages-db.sqlite` | 전체 검색 색인(Gloda). 본문 일부·보낸 사람·주소 |
| `abook.sqlite`·`history.sqlite` | 개인 주소록과 수집된 주소 (78 이후 SQLite 주소록 [2], 파일 이름은 실제 데이터로 확인) |
| `prefs.js` | 계정·서버·사용자 이름·메일 주소 설정 |
| `logins.json`·`key4.db` | 저장된 비밀번호(암호화) |
| `places.sqlite`·`cookies.sqlite` | 메일 안 링크 방문 기록 등, 쿠키 |
| `calendar-data/local.sqlite` | 내장 일정 |
| `msgFilterRules.dat` | 서버 폴더별 메일 규칙 |

모두 실제 데이터로 확인할 후보이고, 표 이름과 열 이름은 분석 대상에서 `.schema` 로 뽑은 것만 씁니다. SQLite 파일을 여는 순서는 [SQLite 데이터베이스 (SQLite)](../../01-foundations/data-formats/sqlite/index.md)에 있습니다. 저장된 비밀번호 파일은 이 핸드북에서 존재 여부와 어떤 계정이 있는지 확인하는 데까지만 다루고, 암호 저장 방식은 [저장된 암호 (Passwords·iCloud Keychain)](../credentials/saved-passwords.md)와 [암호화된 증거 다루기 (Encrypted Evidence)](../../03-techniques/analysis/encrypted-evidence/index.md)를 봅니다.

## 증거로서 의미

**증명하는 것.** `.msf` 가 있으면 그 이름의 메일함 요약이 프로필에 만들어져 있었다는 기록이 됩니다 [1]. mbox 파일이 남아 있으면 그 안의 메일 헤더와 본문으로 누가 누구에게 언제 보냈다고 적힌 메일인지 볼 수 있지만, mbox 의 위치와 구성은 실제 데이터로 확인한 뒤에 씁니다.

**증명하지 못하는 것.** `.msf` 는 요약 파일이라 [1], 이 파일만으로 메일 본문이나 메일이 지금도 있는지를 말할 수 없습니다. Mork 는 파싱이 까다로운 형식이라 [1] 도구마다 읽어 내는 값이 다를 수 있고, 도구가 보여 주는 필드의 뜻은 원문 텍스트와 맞춰 본 것만 씁니다. 메일을 읽었는지, 지웠는지를 나타내는 `X-Mozilla-Status`·`X-Mozilla-Status2` 헤더의 비트 뜻은 시험 계정으로 확인하기 전에는 이 값으로 사용자 행위를 말하지 않습니다.

보고서에는 "이 프로필의 `Inbox.msf` 에 이 제목의 요약 항목이 있다" 처럼 파일과 항목을 그대로 적고, 확인한 썬더버드 버전을 함께 밝힙니다.

## 시각 해석

아래 시각 기준은 알려진 후보라서 실제 데이터로 맞춰 봅니다.

| 위치 | 알려진 기준 |
|---|---|
| Gloda·places 같은 Mozilla SQLite | PRTime (유닉스 시각 기준 마이크로초) |
| `.msf` 안의 날짜 | 16진수로 적은 유닉스 초 |
| mbox 의 `From ` 구분 줄과 `Date:` 헤더 | 보낸 쪽 시간대가 섞임 |

실제 데이터로 정할 때는 같은 메일의 `Date:` 헤더를 기준으로 삼아, 각 파일의 값을 후보 기준으로 풀었을 때 헤더와 맞는지 봅니다. `Date:` 헤더 값은 UTC 로 바꾼 뒤에 비교합니다. 시각 값 변환은 [맥의 시각 값 (Mac Absolute Time·Unix·HFS)](../../01-foundations/value-decoding/mac-time-values.md)에 있습니다.

## 함정과 한계

위치·파일 이름·시각 기준 가운데 후보로 적은 것은 실제 데이터로 직접 확인하기 전에는 보고서에 쓰지 않습니다.

mbox 에서 지운 메일은 "압축(Compact)" 전까지 파일에 남아 있고 `X-Mozilla-Status` 헤더의 삭제 플래그만 바뀐다고 알려져 있습니다. 이 점은 시험 계정에서 메일을 지운 뒤 압축 전과 후의 mbox 를 비교해 확인합니다. 지운 데이터를 찾는 일반 방법은 [삭제 데이터 복구 (Data Recovery)](../../03-techniques/analysis/data-recovery/index.md)에 있습니다.

mbox 파일에는 확장자가 없어서 확장자로 파일을 거르는 도구는 메일함을 빠뜨릴 수 있습니다. `.msf` 와 이름이 같은 짝 파일을 찾는 식으로 메일함을 모읍니다.

## 직접 분석해 보기

### 헥스로 확인하기

`.msf` 를 헥스 편집기나 텍스트 편집기로 열어 보면 텍스트처럼 보이지만 읽기 어려운 Mork 내용이 나옵니다 [1]. 같은 메일함의 mbox 에서 제목 하나를 골라 `.msf` 안에서 그 글자를 찾아보고, 요약 파일에 어떤 값이 함께 들어 있는지 사건 기록에 적습니다.

mbox 후보 파일은 텍스트로 열어 메일 헤더가 이어지는지 보고, 메일 사이의 경계 줄과 `X-Mozilla-Status` 헤더가 있는지 확인합니다.

### 공개 도구로 읽기

SQLite 후보 파일은 증거 사본을 `sqlite3` 명령 줄 도구로 읽기 전용으로 열고, 표 목록과 스키마를 먼저 뽑습니다.

```sql
.tables
.schema
```

mbox 는 일반 메일 도구나 텍스트 도구로 열 수 있고, Mork 파일은 도구마다 결과가 다를 수 있어서 두 도구 이상으로 읽어 결과를 맞춰 봅니다. Mork 를 읽는 도구를 고를 때는 [도구 검증 (Tool Validation)](../../03-techniques/reporting/tool-validation.md)의 절차로 먼저 시험합니다.

## 교차 검증

`Message-ID` 로 같은 메일이 [애플 메일 (Apple Mail)](apple-mail/index.md)이나 [아웃룩 (Outlook for Mac)](outlook.md)에도 있는지 맞춰 보고, 주소는 [연락처 (Contacts)](../cloud-apps/contacts.md)와 맞춰 사람을 짚습니다. 메일 본문에서 키워드를 찾을 때는 [콘텐츠 검색 (Content Search)](../../03-techniques/analysis/content-search.md)을 따르고, 연락 상대 분석은 [누구와 연락을 주고받았나 (Communication)](../../04-scenarios/activity/communication.md)로 묶습니다.

## 실습

썬더버드에 시험 계정을 연결한 맥이나 공개 시험 이미지로 아래 질문을 풀어 봅니다.

1. 이 페이지의 후보 위치에 `profiles.ini` 와 프로필 폴더가 실제로 있는가? `profiles.ini` 의 `Path=` 는 어디를 가리키는가?
2. 메일함 폴더에서 확장자 없는 파일과 `.msf` 파일이 짝으로 있는지 확인한다. 짝이 없는 `.msf` 가 있는가?
3. mbox 에서 메일 하나를 골라 제목을 `.msf` 안에서 찾고, 그 주변에 어떤 값이 있는지 적는다.
4. 시험 계정에서 메일 하나를 지운 뒤, 압축 전과 후의 mbox 에 그 메일이 남아 있는지 비교한다.

## 참고 문헌

1. Mork (file format) — Wikipedia — https://en.wikipedia.org/wiki/Mork_(file_format)
2. Thunderbird 78.0 Release Notes — https://www.thunderbird.net/en-US/thunderbird/78.0/releasenotes/
