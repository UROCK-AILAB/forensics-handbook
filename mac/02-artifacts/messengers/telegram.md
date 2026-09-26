---
title: "텔레그램"
parent: "아티팩트 · 메시지·메신저"
nav_order: 1400
---

# 텔레그램 (Telegram)

맥 텔레그램은 그룹 컨테이너 안에 계정마다 `account-` 폴더를 만들고 그 안의 `postbox/db/db_sqlite` 에 메시지를 암호화해 저장하며, 로컬 암호를 걸지 않은 계정은 키 파일 `.tempkeyEncrypted` 와 DB만 있으면 해독이 가능합니다 [1].

## 무엇을 기록하나 · 왜 생기나

텔레그램 앱은 대화를 서버에서 받아 보여 주면서 메시지와 미디어를 맥 안에 캐시해 두고, 이 로컬 저장소를 Postbox라고 부릅니다 [1]. DB 안에는 메시지 본문과 태그·플래그, 미디어 작업 종류, 전달 메시지 정보, 상대(peer) 사이의 관계가 들어 있습니다 [1]. 받은 사진과 파일 같은 미디어는 DB 밖의 `postbox/media/` 폴더에 따로 쌓입니다 [1].

텔레그램의 "비밀 대화" 와 일반 클라우드 대화가 맥에 어떻게 다르게 남는지는 공개된 분석 자료가 없어 검체로 확인해야 합니다. 서버에 있는 대화가 전부 맥에 내려와 있다는 보장도 없어서, DB에 없는 대화를 "없었다" 고 읽지 않습니다.

## 위치와 버전별 차이

데이터는 그룹 컨테이너 아래에 있고, 앱을 어디서 받았는지에 따라 하위 폴더가 다릅니다 [1].

| 받은 경로 | 데이터 폴더 |
|---|---|
| App Store | `~/Library/Group Containers/6N38VWS5BX.ru.keepcoder.Telegram/appstore/` |
| App Store 밖(직접 받은 것·Homebrew) | `~/Library/Group Containers/6N38VWS5BX.ru.keepcoder.Telegram/stable/` |

그 아래에 로그인한 계정마다 `account-` 뒤에 숫자 ID가 붙은 폴더가 생기고, 계정 폴더 안의 파일은 아래와 같습니다 [1].

```
account-<숫자 ID>/postbox/db/db_sqlite    메시지 DB
account-<숫자 ID>/postbox/media/          미디어 캐시
```

한 맥에 `appstore/` 와 `stable/` 이 함께 있을 수 있으니 두 곳을 모두 봅니다. 계정 폴더가 여러 개면 계정도 여러 개라서, 각 폴더를 따로 분석하고 결과를 섞지 않습니다. 그룹 컨테이너 이름 앞부분을 읽는 법은 [번들 ID와 팀 ID (Bundle ID·Team ID)](../../01-foundations/value-decoding/bundle-team-id.md)에 있습니다.

macOS 버전이나 텔레그램 버전에 따라 이 구조가 바뀌는지, 설정 plist(`ru.keepcoder.Telegram` 도메인)에 어떤 키가 있는지는 공개된 자료가 없어 검체에서 확인합니다.

## 구조

`db_sqlite` 는 SQLCipher로 암호화된 SQLite입니다 [1]. SQLCipher의 세부 설정값과 페이지 크기는 공개된 자료가 없어 검체에서 확인합니다.

맥에서 키와 관련된 파일은 64바이트짜리 `.tempkeyEncrypted` 입니다 [1]. iOS에서는 이름이 `.tempkey` 이고 암호화되지 않은 48바이트 파일이라서, 두 플랫폼의 설명을 섞지 않습니다 [1]. 이 파일이 계정 폴더 기준으로 정확히 어디에 있는지는 알려져 있지 않으니, 데이터 폴더 전체에서 파일 이름으로 찾습니다. 사용자가 앱 잠금용 로컬 암호를 걸지 않았으면 앱은 앱 안에 들어 있는 기본값으로 이 파일을 열고, 로컬 암호를 걸었으면 그 암호에서 PBKDF2로 키를 만들어 엽니다 [1]. 기본값 문자열은 이 핸드북에 적지 않습니다.

해독한 DB의 표는 `T7` 처럼 번호로 된 이름이라서 표 이름만으로는 무엇이 든 표인지 알 수 없습니다. 메시지는 `T7` 표에 들어 있습니다 [1]. 메시지 키는 이름공간(namespace)을 기준으로 정렬되어 있지만 [1], 키가 어떤 바이트로 짜여 있는지와 시각 칸의 형식은 공개된 분석 자료가 없어 검체로 확인해야 합니다.

## 증거로서 의미

**증명하는 것.** 그룹 컨테이너와 `account-` 폴더가 있으면 이 사용자 계정에서 텔레그램을 설치해 로그인한 적이 있고, 폴더 이름의 숫자 ID로 로그인한 계정을 구분할 수 있습니다 [1]. `appstore/` 와 `stable/` 중 어느 쪽에 데이터가 있는지로 앱을 받은 경로를 가를 수 있습니다 [1]. 해독한 DB에 메시지 행이 있으면 그 메시지가 이 맥의 로컬 저장소에 캐시되어 있었다는 사실을 보여 줍니다.

**증명하지 못하는 것.** 로컬 저장소는 서버의 대화 전체와 같지 않을 수 있어서, DB에 없는 메시지가 없었다고 말할 수 없습니다. 미디어 캐시에 파일이 있다는 사실만으로 사용자가 그 파일을 열어 보았다고 말할 수도 없습니다.

로컬 암호를 걸지 않은 계정은 `.tempkeyEncrypted` 와 DB 두 파일만으로 해독이 가능하다는 점 [1]을 방어 쪽에서 보면, 이 두 파일이 함께 다른 곳으로 복사된 흔적은 대화 내용이 넘어갔을 가능성과 이어서 봐야 합니다. 이런 흔적은 [정보 탈취 악성 코드 (Infostealer)](../../04-scenarios/incident/infostealer.md)와 [자료를 밖으로 빼돌렸나 (Data Exfiltration)](../../04-scenarios/exfiltration/data-exfiltration/index.md)의 흐름으로 확인합니다.

보고서에는 "`stable/account-○○` 폴더의 DB에 ○○ 행의 메시지가 캐시되어 있다" 처럼 기록이 말하는 만큼만 씁니다.

## 시각 해석

DB 안 메시지 시각의 형식은 공개된 분석 자료가 없습니다. 유닉스 시각으로 보이는 값이 나오더라도 기준점과 단위를 [맥의 시각 값 (Mac Absolute Time·Unix·HFS)](../../01-foundations/value-decoding/mac-time-values.md)의 방법으로 검증하고, 앱 화면이나 다른 기기의 대화와 몇 건을 맞춰 본 뒤에 씁니다.

계정 폴더와 `media/` 안 파일의 파일 시스템 시각은 캐시가 만들어지거나 바뀐 시각이지 메시지를 주고받은 시각이 아닙니다. 두 시각은 따로 적고, 폴더가 언제 생겼는지는 [파일 시스템 이벤트 (FSEvents)](../filesystem/fsevents/index.md)로 더 봅니다.

## 함정과 한계

DB를 해독하지 못하면 메시지 본문은 볼 수 없습니다. 로컬 암호를 걸어 둔 계정은 그 암호 없이 `.tempkeyEncrypted` 를 열 수 없으니 [1], 해독 가능성은 [암호화된 증거 다루기 (Encrypted Evidence)](../../03-techniques/analysis/encrypted-evidence/index.md)에서 검토합니다. 수집할 때 `.tempkeyEncrypted` 를 빠뜨리면 로컬 암호가 없던 계정도 나중에 해독할 수 없게 되니, DB와 키 파일을 같은 계정 폴더 단위로 함께 확보합니다.

해독한 뒤에도 표 이름이 번호라서 [1], 표 이름으로 짐작하지 말고 공개된 분석 자료나 해독 도구가 설명하는 표의 뜻을 버전과 함께 확인합니다.

## 직접 분석해 보기

**헥스로 한 번.** 평문 SQLite 파일이라면 첫 16바이트가 `SQLite format 3` 과 널 바이트 하나입니다. 아래는 SQLite 파일 형식 명세로 만든 예시이고, 검체에서 나온 값이 아닙니다.

```
00000000  53 51 4c 69 74 65 20 66 6f 72 6d 61 74 20 33 00  |SQLite format 3.|
```

`db_sqlite` 의 첫 16바이트를 찍어 이 글자가 없는지 보고, `.tempkeyEncrypted` 의 크기가 64바이트인지 확인합니다 [1].

```sh
xxd -l 16 db_sqlite
find . -name .tempkeyEncrypted -exec stat -f '%z %N' {} \;
```

**공개 도구로 한 번.**

1. `appstore/` 와 `stable/` 아래 `account-` 폴더를 통째로 수집하고 사본에서 작업합니다.
2. 계정 폴더마다 `postbox/db/` 의 파일 목록과 `postbox/media/` 의 파일 수·크기를 적습니다.
3. `file` 명령으로 미디어 캐시 파일의 형식을 가리고, 사진 파일은 [사진 메타데이터 (EXIF·HEIC)](../embedded-metadata/exif-heic.md)의 방법으로 안의 정보를 봅니다.
4. 해독이 필요하면 SQLCipher를 지원하는 공개 도구를 쓰되, 적법한 권한 안에서 사본으로만 작업하고 쓴 도구와 버전을 보고서에 남깁니다. 도구의 결과는 [도구 검증 (Tool Validation)](../../03-techniques/reporting/tool-validation.md)의 방법으로 확인합니다.

## 교차 검증

| 함께 볼 자료 | 확인할 것 |
|---|---|
| [설치한 앱과 영수증 (Applications·Receipts)](../system-account/installed-apps-receipts.md) | App Store판인지 직접 받은 판인지 |
| [어떤 앱을 언제 썼나 (App Usage)](../../04-scenarios/activity/app-usage.md) | 앱을 실행한 시각 |
| [파일 시스템 이벤트 (FSEvents)](../filesystem/fsevents/index.md) | 계정 폴더와 미디어 캐시가 바뀐 시각 |
| [격리 속성과 다운로드 기록 (Quarantine)](../filesystem/quarantine/index.md) | 텔레그램으로 받아 저장한 파일에 붙은 속성 |
| [앱별 네트워크 사용량 (netusage)](../network/netusage.md) | 앱이 주고받은 데이터 양 |
| [정보 탈취 악성 코드 (Infostealer)](../../04-scenarios/incident/infostealer.md) | DB와 키 파일이 함께 복사된 흔적 |

## 실습

텔레그램을 설치한 시험용 맥 또는 공개 검체(NIST CFReDS 등)에서 아래 질문을 풀어 봅니다.

1. 데이터가 `appstore/` 와 `stable/` 중 어디에 있고, `account-` 폴더는 몇 개인가?
2. `db_sqlite` 의 첫 16바이트는 SQLite 평문 서명과 같은가?
3. `.tempkeyEncrypted` 는 어느 경로에 있고 크기는 몇 바이트인가?
4. `postbox/media/` 에서 가장 먼저 만들어진 파일과 가장 늦게 만들어진 파일의 시각은 언제인가?

## 참고 문헌

1. stek29, Telegram macOS/iOS Postbox DB 관련 gist (GitHub Gist) — https://gist.github.com/stek29/8a7ac0e673818917525ec4031d77a713
