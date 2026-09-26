---
title: "위챗"
parent: "아티팩트 · 메신저"
nav_order: 910
---

# 위챗 (WeChat)

## 한 줄 요약

iOS 위챗은 계정 폴더의 `DB` 폴더에 대화 DB 를 두고 대화 상대마다 `Chat_` + 상대 WeChat ID 의 MD5 라는 이름의 표를 따로 만들며, iOS 판 `MM.sqlite` 는 대개 암호화되어 있지 않습니다.

## 무엇을 기록하나 · 왜 생기나

위챗은 대화마다 메시지 표를 하나씩 만들고, 그 표에 메시지가 한 행씩 쌓입니다[2]. 연락처는 따로 `WCDB_Contact.sqlite` 의 `Friend` 표에 있어서[2], 메시지 표 이름의 MD5 를 `Friend` 표의 ID 와 맞춰야 대화 상대가 누구인지 알 수 있습니다. iOS 의 `MM.sqlite` 는 대개 암호화되어 있지 않고[1], iLEAPP 시험 기기에서도 본문이 평문이었습니다[2].

## 위치와 버전별 차이

대화 DB 의 경로를 백업 도메인 기준으로 쓰면 아래와 같습니다[1]. 백업 도메인 이름에서 번들 ID 가 `com.tencent.xin` 임을 알 수 있습니다.

```
AppDomain-com.tencent.xin\Documents\<32자리 16진 폴더>\DB\MM.sqlite
```

`Documents` 아래의 32자리 16진 이름 폴더가 계정 폴더이고 이름은 MD5 값이지만[2], 무엇의 MD5 인지는 공개 자료가 없습니다. 한 기기에서 여러 계정으로 로그인했다면 이런 폴더가 여럿일 수 있어서, 모든 계정 폴더를 확인합니다. 로컬 백업의 도메인과 파일 찾는 법은 [로컬 백업 (Finder·Apple 기기 앱·iTunes Backup)](../../01-foundations/backups/local-backup/index.md)에서 다룹니다.

| 파일 | 담긴 것 |
|---|---|
| `DB/MM.sqlite` | `Chat_` 표들이 들어 있습니다[1][2] |
| `DB/message_1.sqlite`, `DB/message_2.sqlite` … | `Chat_` 표들이 나뉘어 들어 있습니다[2] |
| `WCDB_Contact.sqlite` | 연락처 `Friend` 표가 있습니다[2] |

iLEAPP 의 iOS 위챗 지원은 Pull Request #2250 으로 2026-09-22 에 병합됐고, 필드 대응은 공개되지 않은 표본으로 확인했으며 시험한 앱·iOS 버전은 적혀 있지 않습니다[2]. 버전마다 무엇이 달라지는지는 공개 자료가 없어 검체에서 확인합니다.

## 구조

### `Chat_` 표

표 이름은 `Chat_` 뒤에 상대 WeChat ID 의 MD5 를 붙인 형태이고[2], 한 계정의 `Chat_` 표들은 `MM.sqlite` 와 `message_N.sqlite` 파일들에 나뉘어 있습니다[2]. 그래서 대화 하나를 다 보려면 `DB` 폴더의 모든 파일에서 같은 이름의 표를 찾습니다.

| 칸 | 읽는 법 |
|---|---|
| `CreateTime` | 보낸 시각이고 Unix 초입니다[2] |
| `Des` | 보낸 메시지인지 받은 메시지인지 방향을 나타냅니다[2] |
| `Type` | 메시지 종류를 나타내는 정수입니다[2] |

`Des` 의 어느 값이 보냄이고 어느 값이 받음인지, `Type` 의 각 값이 무슨 종류인지, 본문이 어느 칸에 있는지는 공개 자료가 없습니다. 이 칸들은 검체에서 사용자가 보낸 것이 분명한 메시지와 맞춰 보고 뜻을 정합니다.

### `Friend` 표 (`WCDB_Contact.sqlite`)

연락처는 `Friend` 표에 있고, 사용자가 붙인 별명은 `dbContactRemark` 칸의 protobuf blob 첫 필드에 들어 있습니다[2]. protobuf 를 읽는 법은 [프로토콜 버퍼 (Protocol Buffers)](../../01-foundations/data-formats/protobuf.md)에 있습니다. `Friend` 표의 WeChat ID 를 MD5 로 바꿔 `Chat_` 표 이름과 맞추면 대화 상대를 찾을 수 있고, 연락처에서 지운 상대와의 대화도 `Chat_` 표는 남아 있어 도구가 보고합니다[2].

## 증거로서 의미

**증명하는 것.** `Chat_` 표의 행은 이 계정의 위챗 DB 에 이 상대와의 메시지가 이 시각 값·방향·종류와 함께 남아 있다는 사실을 보여 줍니다. `Friend` 표에 짝이 없는 `Chat_` 표는 연락처에는 없지만 대화 기록은 남은 상대가 있다는 뜻이라서[2], 연락처를 정리한 흔적을 볼 때 단서가 됩니다.

**증명하지 못하는 것.** 표 이름은 MD5 라서 거꾸로 풀 수 없고, 상대 ID 를 알아야 맞출 수 있습니다. `Friend` 표에서 짝을 못 찾으면 상대는 MD5 값으로만 남습니다. 별명은 사용자가 붙인 이름이라서 실제 신원을 보여 주지 않습니다. 기기에 없는 메시지가 서버나 상대 기기에 있을 수 있어서, 행이 없다고 대화가 없었다고 볼 수 없습니다.

## 시각 해석

`CreateTime` 은 1970-01-01 을 기준으로 한 Unix 초이고[2] UTC 입니다. 현지 시각은 바꾼 뒤에 시간대를 따로 적용합니다. 이 값이 기기 시계로 붙은 시각인지 서버가 붙인 시각인지는 공개 자료가 없어 검체에서 확인합니다. 시각 값 전반은 [시각 값 (Mac 절대 시각·Unix·기타)](../../01-foundations/value-decoding/time-values.md)에서 다룹니다.

## 함정과 한계

`MM.sqlite` 만 열면 `message_N.sqlite` 에 나뉜 표를 놓칩니다[2]. 파일마다 `-wal` 이 있으면 함께 가져와 열어야 최근 행이 빠지지 않습니다. 암호화되어 있지 않은 것은 "대개" 그렇다는 것이라서[1], 파일을 열 때 SQLite 머리글이 보이지 않으면 암호화된 DB 일 수 있다고 보고 그대로 기록합니다.

iLEAPP 의 위챗 지원은 2026-09-22 에 들어온 새 기능이고 공개 표본으로 검증한 기록이 없어서[2], 결과를 쓰기 전에 표 몇 개를 직접 열어 맞춰 봅니다. 사진·음성·영상 같은 미디어가 어느 폴더에 저장되는지는 공개 자료가 없어 검체에서 확인합니다. 지운 메시지를 SQLite 빈 공간이나 WAL 에서 찾는 일반적인 방법은 [삭제 데이터 복구 (Data Recovery)](../../03-techniques/analysis/data-recovery/index.md)와 [SQLite 데이터베이스 (SQLite)](../../01-foundations/data-formats/sqlite/index.md)에 있습니다.

## 직접 분석해 보기

### 헥스로 한 번

`dbContactRemark` 의 첫 필드가 문자열이라면 protobuf 규칙에 따라 필드 번호 1·길이 구분 형식을 뜻하는 `0A` 바이트 뒤에 길이 한 바이트, 그 뒤에 UTF-8 글자가 옵니다. 표 이름은 상대 ID 를 MD5 로 바꾼 값입니다. 아래는 명세로 만든 예시이고 실제 검체에서 나온 값이 아닙니다.

```
dbContactRemark 앞부분
0A 09 ED 99 8D EA B8 B8 EB 8F 99 ...
│  │  └ UTF-8 "홍길동" (9 바이트)
│  └ 길이 9
└ 필드 1, 길이 구분 형식

상대 ID (예시)       : wxid_example01
MD5                  : 1c6a66ee8b0caf7ad758cd20e283f47e
찾을 표 이름         : Chat_1c6a66ee8b0caf7ad758cd20e283f47e
```

### 질의로 한 번

```sql
-- DB 폴더의 파일마다 실행해 Chat_ 표 목록을 모은다
SELECT name FROM sqlite_master
WHERE type = 'table' AND name LIKE 'Chat\_%' ESCAPE '\';

-- 표 하나를 골라 시각·방향·종류를 본다
SELECT datetime(CreateTime, 'unixepoch') AS create_utc, Des, Type
FROM "Chat_1c6a66ee8b0caf7ad758cd20e283f47e"
ORDER BY CreateTime DESC
LIMIT 20;
```

SQLite 에는 MD5 함수가 없어서, `Friend` 표의 ID 목록을 꺼내 스크립트로 MD5 를 계산한 뒤 표 이름 목록과 맞춥니다.

### 공개 도구로 한 번

iLEAPP 의 위챗 분석기는 `Chat_` 표와 `Friend` 표를 이어 대화 상대 이름을 붙인 보고서를 만듭니다[2]. 위 질의로 모은 `Chat_` 표 수와 보고서의 대화 수를 맞춰 보고, 연락처에서 지운 상대의 대화가 보고서에 어떻게 표시되는지 확인합니다. 도구 결과를 검증하는 방법은 [도구 검증 (Tool Validation)](../../03-techniques/reporting/tool-validation.md)에 있습니다.

## 교차 검증

대화 시각에 위챗 알림이 떴는지는 [알림 기록 (Notifications)](../app-usage/notifications.md)에서, 그 시각에 앱을 쓰고 있었는지는 [KnowledgeC (knowledgeC.db)](../app-usage/knowledgec/index.md)와 [바이옴 (Biome)](../app-usage/biome/index.md)에서 봅니다. 위챗 연락처의 전화번호가 기기 연락처에도 있는지는 [연락처 (AddressBook)](../communications/contacts.md)에서 맞춰 보고, 다른 연락 수단과 시간순으로 합치는 방법은 [누구와 연락을 주고받았나 (Communication)](../../04-scenarios/activity/communication.md)에 있습니다.

## 실습

공개된 iOS 검체 가운데 위챗이 설치된 것으로 아래를 풀어 봅니다.

1. `Documents` 아래 32자리 16진 폴더가 몇 개인지 세고, 폴더마다 `DB` 안의 파일 목록을 적어 봅니다.
2. 모든 파일의 `Chat_` 표 이름을 모아 `Friend` 표의 ID MD5 와 맞춰 보고, 짝이 없는 표가 몇 개인지 세어 봅니다.
3. 사용자가 보낸 것이 분명한 메시지 하나를 골라 그 행의 `Des` 값을 보고 방향 값의 뜻을 정해 봅니다.

## 참고 문헌

1. Belkasoft, "WeChat. The Forensic Aspects Of and Uses For Evidence from a Super-App" — https://belkasoft.com/WeChat-forensics
2. abrignoni/iLEAPP, Pull Request #2250 "Add WeChat support for iOS" — https://github.com/abrignoni/iLEAPP/pull/2250
