---
title: "저장 위치와 파일"
parent: "카카오톡"
grand_parent: "아티팩트 · 메신저"
nav_order: 800
---

# 저장 위치와 파일 (Paths·Files)

아이폰 카카오톡은 앱 데이터 컨테이너의 `Library/PrivateDocuments/` 아래에 메시지 DB `Message.sqlite` 와 채팅방·사용자 DB `Talk.sqlite` 를 두고, 받은 미디어는 같은 폴더의 `chat`·`chatVideo`·`chatAudio` 아래 채팅방별 폴더에 저장합니다.

## 무엇을 기록하나 · 왜 생기나

카카오톡의 번들 ID 는 `com.iwilab.KakaoTalk` 이고[3], 앱이 쓰는 파일은 이 앱의 데이터 컨테이너 안에 모입니다. 카카오톡 DB 파일은 모두 `Library/PrivateDocuments/` 아래에 있고[2][3], 메시지는 `Message.sqlite` 에, 채팅방·사용자·연락처는 `Talk.sqlite` 에 들어 있습니다[2][3]. 받은 사진·영상·음성은 DB 밖의 폴더에 파일로 남습니다[2].

각 파일의 안쪽은 하위 페이지에서 나눠 다룹니다. 표와 열, 암호화는 [대화 DB 구조와 암호화 (Chat DB)](chat-db.md)에, 미디어 폴더는 [받은 파일 (Received Files)](received-files.md)에, 사용자와 연락처 표는 [계정과 친구 목록 (Account·Friends)](account-friends.md)에 있습니다.

## 위치와 버전별 차이

### 기기 안의 위치

앱 데이터 컨테이너의 루트는 `.../Data/Application/<UUID>/` 이고[2], 파일은 그 아래 다음 경로에 있습니다[2].

```
*/Library/PrivateDocuments/Message.sqlite*
*/Library/PrivateDocuments/Talk.sqlite*
*/Library/PrivateDocuments/chat/*/*
*/Library/PrivateDocuments/chatVideo/*/*
*/Library/PrivateDocuments/chatAudio/*/*
```

`Message.sqlite*` 끝의 `*` 는 뒤에서 다룰 `-wal`·`-shm` 파일까지 함께 잡습니다. 컨테이너 폴더 이름의 UUID 는 기기마다 달라서, 경로를 적을 때는 "앱 데이터 컨테이너" 로 적고 실제 UUID 는 설치된 앱 목록과 맞춰 봅니다. 번들 ID 와 컨테이너의 관계는 [번들 ID와 앱 그룹 (Bundle ID·App Group)](../../../01-foundations/value-decoding/bundle-id-app-group.md)에서 다룹니다.

### 로컬 백업 안의 위치

아이튠즈(로컬) 백업에서 카카오톡 파일은 `AppDomain-com.iwilab.KakaoTalk` 도메인에 들어가고, 상대 경로는 기기와 같은 `Library/PrivateDocuments/Message.sqlite`, `Library/PrivateDocuments/Talk.sqlite` 입니다[3]. 백업의 `Manifest.db` 에는 `Files` 표(`fileID`, `domain`, `relativePath`, `flags`, `file`)가 있어서, 이 표에서 `domain` 과 `relativePath` 로 파일을 찾습니다[3]. 백업 파일 ID 를 구하는 방법과 백업 구조는 [로컬 백업 (Finder·Apple 기기 앱·iTunes Backup)](../../../01-foundations/backups/local-backup/index.md)에 있습니다.

로컬 백업만으로 DB 와 미디어 파일을 꺼내 분석할 수 있습니다[3]. 암호화 백업이어야 이 파일들이 들어가는지는 실제 백업으로 확인합니다.

### 버전별 차이

경로가 iOS 버전과 카카오톡 앱 버전에 따라 달라지는지는 실제 기기에서 확인합니다. 앱 버전에 따라 `Talk.sqlite` 의 열 구성이 다른 사례는 [계정과 친구 목록 (Account·Friends)](account-friends.md)에 있습니다.

## 구조

| 파일 | 위치(`Library/PrivateDocuments/` 기준) | 들어 있는 것 |
|---|---|---|
| `Message.sqlite` | 바로 아래 | 메시지 행(`Message` 표)[2][3] |
| `Message.sqlite-wal`, `Message.sqlite-shm` | 바로 아래 | 아직 DB 본체에 합쳐지지 않은 변경[2] |
| `Talk.sqlite` | 바로 아래 | 채팅방(`ZCHAT`), 사용자(`ZUSER`), 연락처(`ZCONTACT`), 채팅방 폴더(`ZCHATFOLDER`)[2] |
| 받은 사진·파일 | `chat/` 아래 채팅방별 폴더 | 확장자 없는 미디어 파일과 축소본[2] |
| 받은 영상 | `chatVideo/` 아래 채팅방별 폴더 | 영상 파일[2] |
| 받은 음성 | `chatAudio/` 아래 채팅방별 폴더 | 음성 파일[2] |

`Message.sqlite` 와 `Talk.sqlite` 는 흔한 이름이라 다른 앱의 파일과 헷갈릴 수 있습니다. `Message` 표에 `sentAt`·`chatId`·`serverLogId`·`clientMsgId` 열이 있는지, `Talk.sqlite` 에 `ZCHAT`·`ZUSER` 표가 있는지를 보면 카카오톡 파일인지 가려낼 수 있습니다[2]. 경로만 보고 고른 파일도 같은 방법으로 한 번 더 확인하는 편이 안전합니다.

카카오톡 설정 plist 가 있는지, 앱 그룹 컨테이너를 쓰는지, 카카오 서버로 올리는 대화 백업 기능이 기기에 파일을 남기는지는 실제 기기로 확인해야 합니다.

## 증거로서 의미

**증명하는 것.** 앱 데이터 컨테이너나 `AppDomain-com.iwilab.KakaoTalk` 도메인에 위 파일이 있으면, 수집 시점에 이 기기(또는 백업)에 카카오톡 데이터가 남아 있었다는 사실을 보여 줍니다. 파일 안의 표 구성으로 카카오톡 DB 인지도 확인할 수 있습니다.

**증명하지 못하는 것.** 파일이 있다는 것만으로는 사용자가 언제 앱을 썼는지, 누구와 대화했는지를 말할 수 없고, 그 내용은 DB 를 열어 봐야 합니다. 반대로 파일이 없을 때 앱을 쓰지 않았다고 볼 수도 없는데, 앱을 지웠거나 백업에 앱 데이터가 들어가지 않았을 수 있기 때문입니다.

## 함정과 한계

WAL 파일을 빠뜨리면 메시지가 크게 빠집니다. `Message.sqlite` 는 행 내용 대부분이 DB 본체가 아니라 `-wal` 파일에 있는 경우가 있습니다[2]. DB 본체만 복사해 열면 메시지가 거의 없는 것처럼 보일 수 있어서, `-wal`·`-shm` 을 같은 폴더에 함께 두고 엽니다. WAL 이 합쳐지는 방식은 [SQLite 데이터베이스 (SQLite)](../../../01-foundations/data-formats/sqlite/index.md)에서 다룹니다.

원본 파일을 바로 SQLite 도구로 열면 WAL 이 본체에 합쳐져 원본이 바뀔 수 있습니다. 먼저 세 파일을 함께 사본으로 떠 놓고 사본을 엽니다.

## 직접 분석해 보기

### 헥스로 한 번

SQLite 파일은 첫 16바이트가 정해진 문자열이라서, 확장자나 이름과 상관없이 DB 파일인지 가려낼 수 있습니다. 아래는 SQLite 파일 형식 명세로 만든 예시이고 실제 기기에서 나온 값이 아닙니다.

```
00000000  53 51 4C 69 74 65 20 66 6F 72 6D 61 74 20 33 00  SQLite format 3.
```

`Message.sqlite` 와 `Talk.sqlite` 첫머리에 이 문자열이 있는지 확인한 뒤, 표 이름으로 카카오톡 DB 인지 확인합니다.

### 백업에서 파일 찾기

```sql
SELECT fileID, relativePath
FROM Files
WHERE domain = 'AppDomain-com.iwilab.KakaoTalk'
  AND relativePath LIKE 'Library/PrivateDocuments/%'
ORDER BY relativePath;
```

찾은 DB 가 카카오톡 것인지는 아래 질의로 확인합니다. 첫 줄은 `Message.sqlite` 에서, 둘째 줄은 `Talk.sqlite` 에서 실행합니다.

```sql
SELECT name FROM pragma_table_info('Message')
 WHERE name IN ('sentAt','chatId','serverLogId','clientMsgId');
SELECT name FROM sqlite_master WHERE type='table' AND name IN ('ZCHAT','ZUSER');
```

### 공개 도구로 한 번

iLEAPP 의 카카오톡 분석기(`scripts/artifacts/kakaoTalk.py`)는 위 경로 패턴으로 파일을 모아 메시지·채팅방·사용자·주소록 대응·채팅 미디어 다섯 가지 보고서를 만듭니다[1][2]. 도구가 모은 파일 목록과 직접 찾은 목록을 맞춰 보면 `-wal` 이 빠졌는지 바로 드러납니다.

## 교차 검증

카카오톡이 설치되어 있었는지와 컨테이너 UUID 는 [설치된 앱 (Installed Apps·applicationState.db)](../../app-usage/installed-apps.md)에서, 앱을 언제 썼는지는 [KnowledgeC (knowledgeC.db)](../../app-usage/knowledgec/index.md)와 [바이옴 (Biome)](../../app-usage/biome/index.md)에서 확인합니다.

## 실습

공개된 iOS 시험 이미지 가운데 카카오톡이 설치된 것으로 아래를 풀어 봅니다.

1. 백업이나 파일 시스템 추출본에서 `Library/PrivateDocuments/` 아래 파일 목록을 뽑아 `-wal` 파일이 있는지 확인해 봅니다.
2. `Message.sqlite` 를 `-wal` 없이 연 결과와 함께 연 결과의 `Message` 행 수를 비교해 봅니다.
3. `chat`·`chatVideo`·`chatAudio` 아래 채팅방 폴더 수를 세어 봅니다.

## 참고 문헌

1. abrignoni/iLEAPP, Pull Request #2249 "Add KakaoTalk support for iOS" (2026-09-22 병합) — https://github.com/abrignoni/iLEAPP/pull/2249
2. abrignoni/iLEAPP, `scripts/artifacts/kakaoTalk.py` — https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/kakaoTalk.py
3. kim-do-hyeon/iOS-Forensic, `artifact_analyzer/messenger/kakaotalk/kakaotalk_analyzer.py` — https://github.com/kim-do-hyeon/iOS-Forensic/blob/main/artifact_analyzer/messenger/kakaotalk/kakaotalk_analyzer.py
