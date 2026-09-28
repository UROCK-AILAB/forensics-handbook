---
title: "카카오톡 맥"
parent: "아티팩트 · 메시지·메신저"
nav_order: 1390
---

# 카카오톡 맥 (KakaoTalk)

맥 카카오톡의 저장 위치와 대화 DB 구조는 실제 데이터로 확인합니다. 이 페이지는 분석 대상에서 앱 데이터 폴더를 찾고 파일이 평문 SQLite인지 판별하는 방법을 다룹니다.

## 무엇을 기록하나 · 왜 생기나

메신저 앱은 대화를 이어 보여 주려고 대화 내용과 받은 파일, 로그인 상태 같은 설정을 사용자 폴더 안에 저장합니다. 맥 카카오톡이 어느 폴더에 어떤 이름의 파일로 이것들을 저장하는지, 대화 DB를 암호화하는지, 암호화한다면 어떤 방식인지는 실제 데이터로 확인해야 합니다. 받은 파일과 사진이 모이는 폴더, 로그인 계정이나 자동 로그인을 적는 설정 plist의 경로와 키도 마찬가지입니다.

윈도우판 카카오톡의 대화 파일(`.edb`)은 SQLCipher 계열로 알려져 있지만, 맥판이 같은 방식을 쓰는지는 파일 첫 16바이트부터 확인합니다. 윈도우판 이야기를 맥 데이터에 그대로 옮겨 "암호화되어 있다" 고 적지 않습니다.

## 위치와 버전별 차이

경로를 외워 두는 대신 분석 대상에서 찾습니다. 순서는 아래와 같습니다.

1. `/Applications` 아래에서 카카오톡 앱 번들을 찾고, 번들 안 `Contents/Info.plist` 의 `CFBundleIdentifier` 값으로 번들 ID를 확인합니다. 앱 번들의 구조는 [앱 번들 정보 (Info.plist·Code Signature)](../embedded-metadata/app-bundle.md), 번들 ID를 읽는 법은 [번들 ID와 팀 ID (Bundle ID·Team ID)](../../01-foundations/value-decoding/bundle-team-id.md)에 있습니다.
2. 사용자 폴더의 `~/Library/Containers/`, `~/Library/Group Containers/`, `~/Library/Application Support/`, `~/Library/Preferences/` 에서 그 번들 ID나 `kakao` 가 들어간 이름을 대소문자를 가리지 않고 찾습니다.
3. 찾은 폴더 아래 파일 목록을 크기·시각과 함께 떠 두고, 크기가 큰 파일과 자주 바뀐 파일부터 형식을 확인합니다.

앱 번들 ID로 흔히 `com.kakao.KakaoTalkMac` 이 알려져 있지만, 1번에서 실제 값을 직접 읽어 씁니다. 샌드박스 앱은 `~/Library/Containers/` 아래 번들 ID 이름의 폴더 안에 데이터를 두는 경우가 많지만, 카카오톡이 이 구조를 쓰는지는 실제 데이터로 확인합니다. 같은 앱이라도 받은 경로에 따라 저장 위치가 달라지는 예가 [슬랙 (Slack)](slack.md)과 [텔레그램 (Telegram)](telegram.md)에 있으니, 한 곳에서 못 찾았다고 멈추지 않습니다.

분석 대상의 macOS 버전은 [OS 버전과 설치 기록 (SystemVersion·InstallHistory)](../system-account/os-version-install-history.md)에서, 앱 버전은 1번의 `Info.plist` 에서 확인해 함께 적습니다.

## 구조

찾은 파일마다 형식부터 판별합니다. 평문 SQLite 파일은 첫 16바이트가 `SQLite format 3` 과 널 바이트 하나이고, 이 글자가 보이면 [SQLite 데이터베이스 (SQLite)](../../01-foundations/data-formats/sqlite/index.md)의 방법대로 표를 엽니다. 첫 16바이트가 이 글자가 아니면 평문 SQLite가 아니라는 사실만 확인한 것이라서, 그 파일이 암호화된 DB인지 다른 형식의 파일인지는 따로 판별해야 합니다.

plist로 보이는 파일은 [속성 목록 파일 (Property List)](../../01-foundations/data-formats/plist/index.md)에서 읽는 법을 보고, LevelDB로 보이는 폴더는 [LevelDB와 IndexedDB (LevelDB·IndexedDB)](../../01-foundations/data-formats/leveldb-indexeddb.md)를 봅니다.

## 증거로서 의미

**증명하는 것.** 앱 번들과 사용자 폴더 안의 카카오톡 데이터 폴더가 있으면, 이 맥에 앱이 설치되었고 그 사용자 계정으로 앱이 데이터를 남겼다는 사실을 보여 줍니다. 평문 SQLite로 열린 파일이 있으면 그 안의 표가 기록하는 만큼을 읽을 수 있습니다.

**증명하지 못하는 것.** 폴더가 있다는 사실만으로 대화를 주고받았다거나 특정 상대와 연락했다고 말할 수 없습니다. 파일이 열리지 않을 때 그 이유를 "암호화" 로 단정하지 않고, 풀지 못한 파일은 풀지 못했다고 적습니다. 암호화 여부와 키 위치가 확인되지 않은 상태에서 대화가 없었다고 쓰지도 않습니다.

보고서에는 "`○○` 경로에 크기 ○○바이트의 파일이 있고, 첫 16바이트가 SQLite 평문 서명과 다르다" 처럼 확인한 만큼만 씁니다.

## 시각 해석

대화 DB 안의 시각 열은 평문 SQLite로 열린 파일에서 `.schema` 로 표 구조를 보고 확인합니다. 그 밖에 확인할 수 있는 시각은 데이터 폴더와 파일의 파일 시스템 시각이고, 읽는 법은 [APFS 구조 (APFS)](../../01-foundations/disk-volume/apfs/index.md)에 있습니다. 폴더와 파일이 언제 만들어지고 바뀌었는지는 [파일 시스템 이벤트 (FSEvents)](../filesystem/fsevents/index.md)로 더 볼 수 있고, 앱을 언제 실행했는지는 [어떤 앱을 언제 썼나 (App Usage)](../../04-scenarios/activity/app-usage.md)의 흐름으로 봅니다. 파일 시각이 곧 대화 시각은 아니라서 둘을 섞지 않고 따로 적습니다.

## 함정과 한계

구조가 공개되지 않은 앱이라서, 다른 앱이나 윈도우판에서 알려진 내용을 그대로 옮기는 일이 가장 흔한 실수입니다. 확장자나 파일 이름만 보고 "암호화된 DB" 라고 판단하지 말고, 먼저 첫 16바이트를 확인합니다. 같은 이름의 파일이라도 파일마다 평문과 암호문이 섞여 있을 수 있어서, 표본 하나만 보고 폴더 전체를 판단하지 않습니다.

대화 DB가 평문이 아니고 키도 찾지 못했다면, 억지로 풀려 하기 전에 [암호화된 증거 다루기 (Encrypted Evidence)](../../03-techniques/analysis/encrypted-evidence/index.md)에서 다른 경로를 고르고, 앱이 실행 중인 맥이라면 [라이브 대응 (Live Response)](../../03-techniques/process-acquisition/live-response/index.md)에서 전원을 끄기 전에 확보할 것을 먼저 봅니다.

## 직접 분석해 보기

**헥스로 한 번.** 아래는 SQLite 파일 형식 명세로 만든 평문 SQLite 헤더 예시이고, 실제 데이터에서 나온 값이 아닙니다.

```
00000000  53 51 4c 69 74 65 20 66 6f 72 6d 61 74 20 33 00  |SQLite format 3.|
```

찾은 폴더 안 파일마다 첫 16바이트를 찍어 이 예시와 같은지 봅니다.

```sh
find "<데이터 폴더>" -type f -size +0 -exec sh -c 'printf "%s  " "$1"; xxd -p -l 16 "$1"' _ {} \;
```

**공개 도구로 한 번.** `file` 명령으로 같은 파일들의 형식을 다시 확인하고, 헥스로 가린 결과와 맞춰 봅니다. 평문 SQLite로 나온 파일은 사본을 sqlite3로 열어 `.tables` 와 `.schema` 로 표 목록부터 적습니다.

```sh
file "<데이터 폴더>"/*
sqlite3 copy.db '.tables'
```

## 교차 검증

| 함께 볼 자료 | 확인할 것 |
|---|---|
| [설치한 앱과 영수증 (Applications·Receipts)](../system-account/installed-apps-receipts.md) | 앱이 언제 어떤 경로로 설치되었는지 |
| [어떤 앱을 언제 썼나 (App Usage)](../../04-scenarios/activity/app-usage.md) | 앱을 실행한 시각 |
| [격리 속성과 다운로드 기록 (Quarantine)](../filesystem/quarantine/index.md) | 메신저로 받은 파일에 붙은 속성 |
| [앱별 네트워크 사용량 (netusage)](../network/netusage.md) | 앱이 주고받은 데이터 양 |
| [누구와 연락을 주고받았나 (Communication)](../../04-scenarios/activity/communication.md) | 여러 통신 기록을 묶어 보는 조사 흐름 |

## 실습

카카오톡 맥을 설치한 시험용 맥 또는 공개 시험 이미지(NIST CFReDS 등)에서 아래 질문을 풀어 봅니다.

1. 앱 번들의 `CFBundleIdentifier` 값은 무엇이고, 그 값이 들어간 폴더는 사용자 `Library` 아래 어디에 있는가?
2. 그 폴더 안에서 첫 16바이트가 SQLite 평문 서명인 파일과 아닌 파일은 각각 몇 개인가?
3. 평문 SQLite로 열린 파일에는 어떤 표가 있는가?
4. 데이터 폴더가 처음 만들어진 시각은 앱 설치 기록의 시각과 어떻게 이어지는가?

## 참고 문헌

이 페이지에서 인용한 문헌은 없습니다.
