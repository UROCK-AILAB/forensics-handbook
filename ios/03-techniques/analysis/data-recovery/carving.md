---
title: "카빙"
parent: "삭제 데이터 복구"
grand_parent: "기법 · 분석"
nav_order: 1330
---

# 카빙 (Carving)

아이폰에서는 저장 공간 전체를 파일 시그니처로 훑는 전통 카빙이 거의 통하지 않고, 쓸모 있는 카빙은 이미 풀린 파일(SQLite DB·WAL·사용 기록 DB) 안쪽을 레코드 구조나 알려진 문자열로 훑는 작업입니다.

## 언제 쓰나

PC 에서는 지운 파일의 블록이 빈 공간에 남아 있어서, JPEG 머리 같은 시그니처로 원시 디스크를 훑으면 파일을 되살리기도 합니다. 아이폰은 데이터 볼륨에 파일을 만들 때마다 파일별 키를 새로 만들고, 하드웨어 AES 엔진이 플래시에 쓰는 순간 그 키로 암호화합니다 [2]. 그래서 원시 플래시나 볼륨을 시그니처로 훑으면 파일별 키 없이는 암호문만 보게 되고, 지운 사용자 파일을 되살리는 도구도 없습니다 [1]. 키가 어떻게 사라지는지는 [복구가 안 되는 이유](limits.md) 에 정리했습니다.

카빙이 실제로 쓸모 있는 곳은 수집 과정에서 이미 풀린 파일의 안쪽입니다. 대표적인 대상은 아래와 같습니다.

- SQLite 파일의 freelist 페이지, 페이지 안의 freeblock 과 빈 공간, WAL 프레임을 레코드 구조(varint·serial type)로 훑는 경우 [3]. 이 자리들이 무엇인지는 [SQLite 레코드 되살리기](sqlite-records.md) 에 있습니다.
- 검색 색인 DB. secure_delete 를 켜도 FTS3·FTS5 같은 가상 표의 그림자 표에는 흔적이 남을 수 있어서 [4], 본 표에서 지운 내용이 색인 쪽에 남아 있을 수 있습니다.
- 사용 기록 DB 와 스트림. iOS 16 기기 두 대로 한 시험에서, 보내기 취소한 메시지 본문이 KnowledgeC.db 에서 일반 파싱이 아닌 키워드 검색·카빙으로 나왔고 바이옴 AppIntent 스트림(`/private/var/mobile/Library/Biome/streams/public/AppIntent/local`)과 DuetExpertCenter 알림 이벤트 스트림(`/private/var/mobile/Library/DuetExpertCenter/streams/UserNotificationEvents/local/`)에서도 나왔습니다 [5]. 이 경로는 전체 파일 시스템 기준이고, 로컬 백업에 들어가는지는 검체에서 확인합니다.
- 사진 메타데이터. 미디어를 추출할 때 본 DB 에 합쳐지지 않은 WAL 파일도 함께 받으면 사진 메타데이터 일부를 되살릴 수 있다는 설명이 있습니다 [1].

## 절차

1. 수집 방식을 먼저 확인합니다. 로컬 백업은 파일 단위로 담기므로 빈 공간이 없고, 파일 안쪽만 카빙할 수 있습니다. 백업 구조는 [로컬 백업](../../../01-foundations/backups/local-backup/index.md), 파일 시스템 단위 수집은 [모바일 증거 확보](../../acquisition/mobile-acquisition/index.md) 를 봅니다.
2. 대상 파일을 고릅니다. 지운 항목이 있던 앱 DB 와 그 WAL, 같은 내용이 옮겨 가는 색인 DB, [KnowledgeC](../../../02-artifacts/app-usage/knowledgec/index.md) 와 [바이옴](../../../02-artifacts/app-usage/biome/index.md) 이 후보입니다.
3. SQLite 대상이면 살아 있는 스키마에서 표의 칸 수와 칸 종류를 읽어, 그 표의 레코드 머리가 어떤 바이트 모양이 될지 정합니다.
4. 파일을 바이트 단위로 훑으며 그 모양과 맞는 자리를 찾습니다. 레코드 머리 크기 varint 값은 머리 전체 길이(자기 자신 포함)와 같아야 하고, 정수 칸은 보통 serial type 1~6·8·9 또는 NULL(0), TEXT 칸은 13 이상의 홀수가 나옵니다. SQLite 는 칸 선언과 다른 종류의 값도 담을 수 있어서(정수 칸의 소수 값은 7) 모양을 너무 좁게 잡지 않습니다.
5. 맞는 자리마다 serial type 으로 값 길이를 계산해 값을 풀고, 값 길이의 합이 페이지 안에 들어가는지, TEXT 가 글자로 풀리는지 확인해 잘못 걸린 자리를 걸러 냅니다.
6. 풀어낸 행을 살아 있는 행과 WAL 의 판별 결과와 견줘 중복을 지우고, 파일 안 오프셋·페이지 번호를 함께 기록합니다.
7. SQLite 가 아닌 스트림이나 구조를 모르는 파일은 다른 증거로 알게 된 문자열(대화 일부, 파일 이름 등)로 검색하고, 찾은 자리 앞뒤를 헥스로 보며 구조를 짐작합니다. 바이옴 스트림을 읽는 법은 [바이옴](../../../02-artifacts/app-usage/biome/index.md), 문자열 검색은 [콘텐츠 검색](../content-search.md) 을 봅니다.

### 헥스로 한 번 따라가기

아래는 SQLite 명세로 만든 예시이고 실제 검체에서 나온 바이트가 아닙니다. 표는 `CREATE TABLE t (n INTEGER, body TEXT)` 로, 칸이 두 개라 레코드 머리는 머리 크기 1바이트와 serial type 두 개를 더해 3바이트가 됩니다. 그래서 훑을 모양은 "`03` 다음에 정수 serial type 한 바이트, 그다음에 13 이상의 홀수 한 바이트" 입니다.

```
freelist 잎 페이지 안 어딘가
.. 00 00 09 07 03 01 17 2A 68 65 6C 6C 6F 00 00 ..
            │  │  │  │  └ n = 0x2A(42), body = "hello"(5바이트)
            │  │  │  └ 0x17 = 23 → TEXT (23-13)/2 = 5바이트
            │  │  └ 0x01 → 1바이트 정수
            │  └ 머리 크기 3 → 모양과 맞음
            └ 앞의 09 07 은 페이로드 길이 9 와 rowid 7 로 읽힘
```

`03 01 17` 에서 레코드가 시작한다고 보면 값 길이는 1 + 5 = 6바이트이고, 머리 3바이트를 더한 9 가 바로 앞 바이트 `09`(페이로드 길이)와 맞아서 셀 머리까지 온전하다고 판단할 수 있습니다. varint 한 바이트에는 127 까지만 들어가므로, TEXT 가 58자 이상이면 serial type 이 2바이트가 되고 머리 크기도 한 바이트 늘어납니다. 모양을 하나로만 잡으면 긴 값의 행을 놓치게 되니 이 경우까지 함께 훑습니다.

## 도구

헥스 편집기와 정규식 검색을 지원하는 공개 도구로 바이트 모양을 직접 찾을 수 있고, 지운 SQLite 레코드를 찾아 주는 공개 도구도 있습니다. 어떤 도구든 SQLite 명세로 만든 시험 파일에서 먼저 결과를 견줘 보고 씁니다([도구 검증](../../reporting/tool-validation.md)).

## 함정과 한계

- 짧은 바이트 모양은 아무 데이터에서나 우연히 걸립니다. 값 길이와 페이지 경계, 글자 풀림을 확인하지 않은 결과는 보고서에 쓰지 않습니다.
- freeblock 안의 옛 셀은 앞 4바이트가 덮여 레코드 머리가 온전하지 않을 수 있어서, 머리 모양으로 훑으면 놓칩니다. 이때는 값 쪽(알려진 문자열)으로 찾습니다.
- 카빙한 조각에는 어느 표의 행인지, 언제 쓰였는지가 붙어 있지 않습니다. 찾은 자리(파일·페이지·오프셋)를 남겨야 나중에 다시 확인할 수 있습니다.
- 파일 시스템 단위로 수집해도 지운 파일이 차지하던 블록은 파일별 키 없이는 풀리지 않습니다([데이터 보호](../../../01-foundations/storage/data-protection/index.md)).

## 결과를 어떻게 해석하나

카빙으로 찾은 조각은 "이 파일의 이 오프셋에 이런 바이트가 있었다" 까지만 증명합니다. 그 내용을 사용자가 입력했는지, 받았는지, 언제 지웠는지는 조각만으로 정할 수 없어서, 조각이 나온 파일의 성격(예: 알림 이벤트 스트림인지 메시지 DB 인지)과 다른 기록의 시각을 맞춰 봐야 합니다. 보고서에는 "KnowledgeC.db 사본의 오프셋 ○○ 에서 이 문자열을 찾았고, 일반 파싱 결과에는 나오지 않았다" 처럼 찾은 방법과 자리를 함께 적습니다.

## 참고 문헌

1. The Five Ways to Recover iPhone Deleted Data — ElcomSoft blog (2021-11) — https://blog.elcomsoft.com/2021/11/the-five-ways-to-recover-iphone-deleted-data/
2. Data Protection overview — Apple Platform Security — https://support.apple.com/guide/security/data-protection-overview-secf6276da8a/web
3. Database File Format — SQLite — https://www.sqlite.org/fileformat2.html
4. Pragma statements supported by SQLite — https://www.sqlite.org/pragma.html
5. iOS 16 - "Paul unsent a message." ... OR DID HE?! — D20 Forensics blog (2022-09) — https://blog.d204n6.com/2022/09/ios-16-paul-unsent-message-or-did-he.html
