---
title: "콘텐츠 검색"
parent: "기법 · 분석"
nav_order: 1390
---

# 콘텐츠 검색 (Content Search)

콘텐츠 검색 (Content Search)은 추출한 아이폰 데이터에서 이름·전화번호·주소·낱말 같은 검색어를 찾는 기법이고, 아이폰 데이터는 대부분 SQLite·plist·protobuf·압축 안에 들어 있어서 원시 바이트를 한 번 훑는 것으로 끝나지 않고 형식마다 풀어서 찾아야 합니다.

## 언제 쓰나

조사 질문이 "이 사람과 연락했나", "이 주소를 본 적이 있나", "이 낱말을 입력했나" 처럼 특정 문자열에서 출발할 때 씁니다. 어느 앱이 관련됐는지 모르는 상태에서 검색어로 먼저 훑고, 걸린 파일을 실마리 삼아 앱별 분석으로 넘어가는 흐름이 흔합니다. 스파이웨어 조사처럼 알려진 도메인·프로세스 이름·프로파일 UUID 같은 지표와 대조할 때도 같은 절차를 따르고, 이 경우는 공개 지표 목록을 검색어로 씁니다.

검색은 아티팩트 분석을 대신하지 못합니다. 검색은 "이 문자열이 이 파일의 이 위치에 있다" 는 사실만 알려 주고, 그 문자열이 보낸 메시지인지 받은 메시지인지, 언제 생겼는지는 걸린 레코드를 그 앱의 구조로 다시 읽어야 알 수 있습니다. 앱 구조를 읽는 순서는 [앱 데이터 분석](app-data-analysis/index.md) 에서 다룹니다.

## 버전에 따라 달라지는 점

| 달라지는 점 | 버전 | 검색에 주는 영향 |
|---|---|---|
| 백업 파일 목록 | iOS 9 이하는 Manifest.mbdb(이진 파일), iOS 10 부터 Manifest.db(SQLite) [1] | 경로로 파일을 찾는 방법이 다릅니다 |
| 백업 폴더 배치 | 2.4 형식(iOS 9 이하)은 한 폴더, 3.2 형식(iOS 10 이후)은 fileID 앞 두 글자 하위 폴더 [1] | 파일을 찾을 때 폴더 이름을 붙입니다 |
| 암호 건 백업의 Manifest.db | iOS 10.2 베타의 암호 건 백업에서 Manifest.db 전체가 암호화된 것이 보고됐습니다 [3] | 암호를 모르면 경로 목록조차 검색할 수 없습니다 |
| 바이옴 파일 형식 | SEGB v1 은 iOS 15–16, v2 는 iOS 17 이후 [12] | 레코드 경계를 가르는 방법이 다릅니다 |
| 메시지 본문 칸 | `attributedBody` 칸은 iOS 11~15 에도 있었고, iOS 16 부터 `text` 가 NULL 인 경우가 잦습니다 [18] | `text` 칸만 조회하면 본문을 놓칩니다 |
| 메일 Protected Index | iOS 12 는 `messages`·`message_data`, iOS 13 은 `Addresses`·`Subjects`·`Summaries` 표 [20] | 제목·본문 요약을 찾는 표 이름이 바뀝니다 |

## 절차

1. **질문과 검색어를 정합니다.** 검색어는 목록으로 적어 두고, 사람 이름이라면 별칭·영문 표기, 전화번호라면 국가 번호를 붙인 꼴과 하이픈을 뺀 꼴처럼 저장될 수 있는 모양을 함께 적습니다. 보고서에서 "무엇으로 찾았고 무엇이 안 나왔나" 를 밝히려면 이 목록이 그대로 남아 있어야 합니다. 한글 검색어는 인코딩마다 바이트가 달라서, 원시 바이트로 찾을 때는 UTF-8 과 UTF-16 두 꼴을 모두 준비합니다(6단계의 예시).

2. **수집 범위와 암호 여부를 확인합니다.** 로컬 백업이라면 `Manifest.plist` 의 `IsEncrypted` 키로 암호 여부를 봅니다. 암호를 걸지 않은 백업에는 저장된 암호, Wi-Fi 설정, 웹사이트 방문 기록, 건강 데이터, 통화 기록이 들어가지 않으므로 [2], 이런 자료에서 나와야 할 검색어가 안 걸렸다면 "없다" 가 아니라 "수집 범위 밖" 으로 적습니다. Apple 보관 문서에 따르면 앱의 `Library/Caches` 폴더도 백업에 들어가지 않아서 [4], 앱 HTTP 캐시(`Cache.db`)는 보통 전체 파일 시스템 추출에서만 검색할 수 있습니다. 수집 방식별 범위는 [모바일 증거 확보](../acquisition/mobile-acquisition/index.md) 를 봅니다.

3. **경로와 이름으로 먼저 좁힙니다.** 로컬 백업 안의 파일 이름은 도메인과 상대 경로를 `-` 로 이은 문자열의 SHA-1 값(fileID)이라서 [1], 백업 폴더를 파일 이름으로 검색해서는 아무것도 알 수 없습니다. 대신 `Manifest.db` 의 `Files` 표(`fileID`, `domain`, `relativePath`, `flags`, `file`)를 조회하면 도메인과 원래 경로로 파일을 찾을 수 있고, 이 표에는 `relativePath` 와 `(domain, relativePath)` 색인이 걸려 있습니다. 찾은 fileID 는 3.2 형식에서 앞 두 글자 폴더 아래에 있습니다 [1]. 백업 구조는 [로컬 백업](../../01-foundations/backups/local-backup/index.md) 에서 자세히 다룹니다.

   ```sql
   -- 경로에 검색어(예: 앱 번들 ID 일부)가 든 파일 목록
   SELECT fileID, domain, relativePath
   FROM Files
   WHERE domain LIKE '%mobilesafari%' OR relativePath LIKE '%History%';
   -- 결과의 fileID 가 ad0009ec... 라면 백업 폴더의 ad/ad0009ec... 파일을 엽니다
   ```

   경로 이름 자체가 검색어가 되기도 합니다. 관찰한 백업의 도메인은 1428개였고, 그중 161개는 Apple 기본 영역이 아닌 설치 앱 등이었습니다. 앱 이름이나 회사 이름으로 도메인을 먼저 찾으면 그 앱의 파일만 골라 다음 단계로 넘길 수 있습니다.

4. **파일 형식을 머리 바이트로 가립니다.** DB 파일 확장자는 `.sqlite`, `.db`, `.sqlitedb` 로 제각각이라 확장자로는 형식을 가를 수 없고, 백업 안 파일은 이름이 fileID 라서 확장자조차 없습니다 [1]. 아래 머리 바이트로 가른 뒤 형식에 맞는 방법으로 넘깁니다.

   | 형식 | 머리 바이트 | 출처 |
   |---|---|---|
   | SQLite DB | 0번 오프셋 16바이트 `SQLite format 3\0` | [6] |
   | SQLite WAL | 0번 오프셋 4바이트 `0x377f0682` 또는 `0x377f0683` | [6] |
   | SQLite 롤백 저널 | `d9 d5 05 f9 20 a1 63 d7` | [6] |
   | 바이너리 plist | 앞 8바이트 `bplist00` | [9][10] |
   | SEGB v1 | 56바이트 헤더의 끝이 `SEGB`(파일 맨 앞이 아님) | [24] |
   | SEGB v2 | 파일 맨 앞 4바이트 `SEGB` | [12] |

5. **형식에 맞게 풀어서 찾습니다.** 같은 문자열이라도 담긴 형식에 따라 원시 바이트로는 보이지 않는 경우가 많아서, 형식마다 다음처럼 풀고 나서 찾습니다.

   - **SQLite**: 칸 단위로 조회하되 `-wal` 파일을 같은 폴더에 두고 엽니다. WAL 방식 DB 는 읽을 때 먼저 WAL 에 그 페이지가 있는지 보기 때문에, 본 파일만 열면 최신 내용이 빠질 수 있습니다 [7]. 헤더 56번 오프셋의 4바이트는 글자 인코딩(1=UTF-8, 2=UTF-16le, 3=UTF-16be)이라 [6], 원시 바이트로 찾을 때 어느 꼴을 쓸지 여기서 정합니다. 형식은 [SQLite 데이터베이스](../../01-foundations/data-formats/sqlite/index.md) 에서 다룹니다.
   - **본문이 BLOB 에 있는 표**: 메시지 DB 의 `message` 표에는 `text` 와 `attributedBody` 칸이 함께 있고, iLEAPP 는 `text` 가 비어 있으면 `attributedBody`(NSAttributedString, typedstream 형식)에서 본문을 꺼냅니다 [17]. `text LIKE '%검색어%'` 한 줄로는 이런 행을 놓칩니다. 칸 해석은 [메시지](../../02-artifacts/communications/messages/index.md) 를 봅니다.

     ```sql
     -- text 가 비어 본문이 attributedBody 에만 있을 수 있는 행
     SELECT ROWID, date, length(attributedBody) FROM message
     WHERE text IS NULL AND attributedBody IS NOT NULL;
     ```

   - **압축한 본문**: 메모 앱은 본문을 `ZICNOTEDATA` 표 `ZDATA` 칸에 gzip 으로 압축한 protobuf 로 저장합니다 [19]. 관찰한 백업에서도 `AppDomainGroup-group.com.apple.notes :: NoteStore.sqlite` 의 `ZICNOTEDATA` 에 `ZDATA` 칸이 있었습니다. 압축을 풀기 전에는 본문 글자가 바이트로 드러나지 않으니, 파서로 푼 결과에서 찾습니다. 자세한 내용은 [메모](../../02-artifacts/mail-cloud/notes.md) 에 있습니다.
   - **인코딩한 메일 본문**: 메일 본문(`.emlx`)은 Quoted-Printable 이나 Base64 로 인코딩되어 있어서 [20], 디코딩한 뒤에 찾습니다. Quoted-Printable 에서는 `=` 가 이스케이프 글자라 [20], UTF-8 한글이라면 `=EC=95=88` 같은 꼴이 되어 평문 검색어로는 걸리지 않습니다. iOS 13 의 Protected Index 에는 본문 앞 500바이트를 담은 `Summaries` 표가 있어서 [20], 본문 파일이 없을 때도 앞부분은 찾을 수 있습니다. 관찰한 백업에서는 Envelope Index·Protected Index·`.emlx` 파일을 찾지 못했습니다. [메일 앱](../../02-artifacts/mail-cloud/apple-mail.md) 을 함께 봅니다.
   - **plist**: 바이너리 plist 는 ASCII 문자열(마커 `0101`)과 유니코드 문자열(마커 `0110`)을 다른 형식으로 담고 [9], 객체끼리 오프셋 표로 이어져 있어서 풀어서 찾는 편이 확실합니다. plist 의 data 값 안에 NSKeyedArchiver 구조가 한 겹 더 들어 있는 경우가 흔하니 [10], 바이너리 plist 해석기와 NSKeyedArchiver 해석기를 함께 씁니다. 관찰한 백업의 plist 에서 값 형식이 bytes 인 키는 360개였고, 그 안이 어떤 형식인지는 값을 읽지 않아 모릅니다. 형식은 [속성 목록 파일](../../01-foundations/data-formats/plist.md) 에서 다룹니다.
   - **protobuf 와 바이옴**: protobuf 이진 데이터에는 필드 이름이 없고 필드 번호만 있으며, wire type 2(LEN)가 문자열·bytes·하위 메시지를 모두 싣기 때문에 [11] 스키마 없이 걸린 문자열은 어떤 필드인지 알 수 없습니다. 바이옴 SEGB 파일의 레코드 페이로드가 대개 protobuf 라서 [12], 바이옴에서 걸린 문자열은 SEGB 레코드 경계와 레코드 시각을 함께 읽어야 뜻이 생깁니다. [SEGB 형식](../../01-foundations/data-formats/segb.md), [프로토콜 버퍼](../../01-foundations/data-formats/protobuf.md), [바이옴](../../02-artifacts/app-usage/biome/index.md) 을 봅니다.
   - **통합 로그**: tracev3 파일은 메시지 문장의 위치와 인수만 담고 형식 문자열은 uuidtext·dsc 파일에 두며, 청크셋은 LZ4 로 압축되어 있습니다 [14]. 그래서 tracev3 를 원시 바이트로 훑어서는 문장을 찾을 수 없고, `log show --style json` 으로 바꾸거나 [15] 공개 파서 출력으로 바꾼 뒤에 찾습니다. 1.63GB 로그 묶음을 JSON 으로 바꾸니 29.19GB 가 된 예가 있으니 [15] 저장 공간을 미리 잡아 둡니다. 형식은 [통합 로그 형식](../../01-foundations/data-formats/unified-log.md), 찾을 사건은 [통합 로그에서 찾을 것](../../02-artifacts/logs/unified-log-events.md) 에 있습니다.
   - **HTTP 캐시**: 앱의 `Cache.db` 는 요청·응답 본문을 HTTP 압축을 푼 상태로 저장하고 헤더·메서드는 바이너리 plist 로 저장합니다 [5]. 본문은 원시 바이트 검색으로도 걸리지만, 헤더에서 찾으려면 plist 를 풀어야 합니다.

6. **원시 바이트 검색으로 남은 곳을 훑습니다.** 5단계에서 풀어 읽은 결과는 살아 있는 레코드만 보여 줍니다. SQLite 는 freelist leaf 페이지를 읽지도 쓰지도 않아서 [6] 지운 행이 파일 안에 남을 수 있고, WAL 에는 같은 페이지의 옛 판이 여러 프레임으로 남을 수 있으며, `secure_delete` 를 켜도 FTS3·FTS5 가상 표의 그림자 표에는 흔적이 남을 수 있습니다 [8]. 이런 곳은 DB 파일과 `-wal` 파일 전체를 바이트 단위로 검색해야 걸립니다. 이때 1단계에서 준비한 인코딩 변형을 모두 씁니다. 아래는 유니코드 명세로 만든 예시이고, 특정 검체에서 나온 값이 아닙니다.

   ```text
   검색어 "안녕" (U+C548 U+B155)
   UTF-8     : EC 95 88 EB 85 95
   UTF-16LE  : 48 C5 55 B1
   UTF-16BE  : C5 48 B1 55
   QP 인코딩 : =EC=95=88=EB=85=95   (메일 본문 안)

   SQLite 헤더 (명세로 만든 예시)
   00000000  53 51 4C 69 74 65 20 66 6F 72 6D 61 74 20 33 00  SQLite format 3.
   00000038  00 00 00 01                                      56번 오프셋 = 1 → UTF-8
   ```

   걸린 위치가 살아 있는 레코드 밖이라면 그 바이트를 레코드 구조(varint·serial type)로 읽어 되살리는 작업으로 넘어가고, 이 과정은 [삭제 데이터 복구](data-recovery/index.md) 에서 다룹니다. 구조를 풀지 않은 파일에서 글자만 뽑는 방법도 있습니다. iLEAPP 는 키보드 동적 어휘 파일(`dynamic-lexicon.dat`)의 구조를 해석하지 않고, UTF-8 로 읽은 뒤 Python `string.printable`(ASCII 출력 글자)에 드는 글자가 3자 이상 이어진 문자열만 뽑습니다 [21]. 그래서 한글 같은 ASCII 밖 낱말은 이 출력에 나오지 않고, 뽑은 문자열에는 시각도 없어서 [21] 입력한 때를 말해 주지 못합니다. 자세한 해석은 [키보드 입력 기록](../../02-artifacts/input-assistant/keyboard.md) 에 있습니다.

7. **지표와 대조합니다.** 알려진 악성 도메인·프로세스 이름 같은 지표를 찾을 때는 검색어를 손으로 적기보다 공개 지표 파일을 씁니다. MVT 는 STIX2 형식 지표 파일(`.stix2` 또는 `.json`)을 `--iocs` 로 여러 개 받고, `mvt download-iocs` 로 공개 지표를 내려받습니다 [22]. MVT 는 백업 `Manifest.db` 의 파일 상대 경로에 지표 도메인이 들어 있는지 대조하고, 메시지 DB 에서는 메시지 속 HTTP 링크를 뽑아 대조합니다 [23]. 이어지는 판단은 [악성 코드·스파이웨어 흔적](spyware-triage/index.md) 에서 다룹니다.

8. **적중마다 위치를 적고 원래 레코드로 되돌아갑니다.** 적중 하나마다 도메인과 상대 경로(또는 기기 경로), 파일 해시, 표와 행 번호(SQLite) 또는 바이트 오프셋(원시 검색), 어느 단계에서 걸렸는지를 기록합니다. 그다음 걸린 레코드의 시각 칸과 보낸 쪽·받은 쪽 같은 칸을 그 앱 구조로 읽어 뜻을 정하고, 시각은 [시각 값](../../01-foundations/value-decoding/time-values.md) 에 따라 UTC 로 바꿔 [타임라인 작성](timeline/index.md) 에 넣습니다.

## 도구

도구 하나로 모든 형식을 풀 수 없어서, 형식마다 공개 도구를 골라 쓰고 결과를 서로 맞춰 봅니다. 아래는 예시이고, 특정 제품을 권하는 목록이 아닙니다.

| 대상 | 공개 도구 예 | 하는 일 |
|---|---|---|
| SQLite | `sqlite3` 명령줄 | 칸 단위 조회. `-wal` 을 같은 폴더에 두고 열어야 최신 내용을 봅니다 [7] |
| 바이너리 plist·NSKeyedArchiver | ccl_bplist | 바이너리 plist 를 읽고 NSKeyedArchiver 를 풉니다 [10] |
| 바이옴 SEGB | ccl-segb | 헤더를 보고 v1·v2 를 가려 레코드를 꺼냅니다 [13] |
| 통합 로그 | `log show --style json`, mandiant macos-UnifiedLogs | JSON·JSONL·CSV 로 바꿔 문장을 검색할 수 있게 합니다 [15][16] |
| 메모 | Apple Cloud Notes Parser | gzip 을 풀고 protobuf 를 읽어 본문을 꺼냅니다 [19] |
| 여러 앱 한꺼번에 | iLEAPP | 앱마다 정해진 경로·표를 읽어 보고서로 냅니다 [17][21] |
| 지표 대조 | MVT(mvt-ios) | STIX2 지표를 백업·파일 시스템 추출과 대조합니다 [22][23] |

원시 바이트 검색에는 16진수 편집기나 `grep -a` 처럼 바이트열을 찾는 일반 도구를 씁니다. 도구마다 지원하는 iOS 버전과 표가 다르니, 결과를 보고서에 쓰기 전에 [도구 검증](../reporting/tool-validation.md) 방식으로 한 번 맞춰 봅니다. mandiant 파서는 지원하지 않는 객체를 base64 로 출력하므로 [16], 그 출력에서 평문 검색어가 안 걸려도 로그에 없다고 볼 수 없습니다.

## 함정과 한계

**검색어가 안 걸려도 없다고 단정할 수 없습니다.** 검색어가 걸리지 않았을 때 가능한 원인은 여러 가지입니다. 수집 범위 밖일 수 있고(암호 없는 백업, 백업에서 빠지는 Caches 폴더), 본문이 압축·인코딩·BLOB 안에 있어 5단계 없이 원시 검색만 했을 수 있고, 검색어의 저장 모양(인코딩, 전화번호 표기, 대소문자)이 달랐을 수도 있습니다. 보고서에는 "이 목록의 검색어를 이 범위에서 이 방법으로 찾았을 때 걸리지 않았다" 까지만 씁니다.

**암호로 보호된 내용은 검색되지 않습니다.** 암호 건 백업은 iOS 10.2 이후 `Manifest.db` 까지 암호화되어 [3], 암호를 모르면 파일 경로 목록조차 검색할 수 없습니다. 잠근 메모는 Apple Cloud Notes Parser 도 암호가 있어야 풀 수 있고, 기기 암호로 잠근 메모(iOS 16 이후)는 아직 처리하지 못합니다 [19]. 이런 본문은 풀기 전까지 검색 대상에서 빠진다는 점을 보고서에 밝힙니다.

**한 번 걸린 문자열이 여러 곳에서 다시 걸립니다.** 보내기 취소한 메시지 본문이 바이옴 AppIntent 스트림, 알림 이벤트 스트림, KnowledgeC 에서 찾아졌다는 보고처럼 [25], 같은 본문이 여러 저장소에 따로 남을 수 있어서 적중 수를 그대로 "몇 번 주고받았다" 로 읽으면 안 됩니다. 적중을 원래 레코드로 되돌려 같은 사건인지 먼저 묶습니다.

**원시 검색의 적중은 문맥이 없습니다.** freelist 나 WAL 에서 걸린 바이트는 어느 표의 어느 칸이었는지, 언제 지워졌는지 바로 알려 주지 않습니다. protobuf 안에서 걸린 문자열도 스키마 없이는 어떤 필드인지 알 수 없습니다 [11]. 이런 적중은 레코드 구조를 풀어 표와 칸을 밝힌 뒤에 보고서에 씁니다.

## 결과를 어떻게 해석하나

검색 결과는 "이 문자열이 이 파일의 이 위치에 있다" 는 사실을 보여 줄 뿐, 누가 언제 왜 남겼는지는 증명하지 못합니다. 예를 들어 메시지 DB 에서 걸린 전화번호는 그 번호가 대화 상대였을 수도 있고 본문에 적힌 번호였을 수도 있어서, 걸린 칸이 `handle` 표인지 본문인지부터 가립니다. 키보드 어휘에서 걸린 낱말은 그 기기에서 입력된 적이 있다는 정황이지만 시각이 없어서 [21] 사건 시각과 잇지 못합니다.

보고서 문장은 기록이 말하는 만큼만 씁니다. "용의자가 '○○' 라고 보냈다" 가 아니라 "`HomeDomain :: Library/SMS/sms.db` 의 `message` 표 한 행(보낸 메시지 표시, 기록 시각 UTC 기준)에 검색어 '○○' 가 든 본문이 있다" 처럼 위치·칸·시각의 기준을 함께 적습니다. 지운 영역에서 걸린 적중은 "살아 있는 레코드가 아니라 파일 안 빈 공간에서 찾은 조각" 이라고 밝히고, 원시 검색으로 찾은 것과 파서로 풀어 찾은 것을 구분해 적습니다. 검색어 목록과 도구 이름·판, 검색 범위는 [포렌식 보고서](../reporting/forensic-report.md) 의 방법 절에 남겨, 다른 분석가가 같은 결과를 다시 얻을 수 있게 합니다.

## 참고 문헌

1. Rich Infante, "Reverse Engineering the iOS Backup" (2017-03-16) — https://www.richinfante.com/2017/3/16/reverse-engineering-the-ios-backup
2. Apple Support, "About encrypted backups on your iPhone, iPad, or iPod touch" (108353) — https://support.apple.com/en-us/108353
3. GitHub horrorho/InflatableDonkey Issue #41, "iOS 10.2 beta new manifest encryption" (2016-11-08) — https://github.com/horrorho/InflatableDonkey/issues/41
4. Apple Developer, File System Programming Guide — File System Basics (보관 문서) — https://developer.apple.com/library/archive/documentation/FileManagement/Conceptual/FileSystemProgrammingGuide/FileSystemOverview/FileSystemOverview.html
5. Silent Signal Techblog, "iOS HTTP cache analysis for abusing APIs and forensics" (2016-05-06) — https://blog.silentsignal.eu/2016/05/06/ios-http-cache-analysis-for-abusing-apis-and-forensics/
6. SQLite, "Database File Format" — https://www.sqlite.org/fileformat2.html
7. SQLite, "Write-Ahead Logging" — https://www.sqlite.org/wal.html
8. SQLite, "Pragma statements supported by SQLite" — https://www.sqlite.org/pragma.html
9. Apple 공개 소스 CF, CFBinaryPList.c (형식 설명 주석) — https://raw.githubusercontent.com/apple-oss-distributions/CF/main/CFBinaryPList.c
10. CCL Group, ccl-bplist (GitHub README) — https://github.com/cclgroupltd/ccl-bplist
11. Protocol Buffers 공식 문서, "Encoding" — https://protobuf.dev/programming-guides/encoding/
12. Cellebrite, "Understanding and Decoding the Newest iOS SEGB Format" — https://cellebrite.com/en/blog/understanding-and-decoding-the-newest-ios-segb-format/
13. CCL Group, ccl-segb (GitHub README) — https://github.com/cclgroupltd/ccl-segb
14. libyal dtformats, "Apple Unified Logging and Activity Tracing formats" — https://github.com/libyal/dtformats/blob/main/documentation/Apple%20Unified%20Logging%20and%20Activity%20Tracing%20formats.asciidoc
15. Alexis Brignoni, "Extraction, Processing, & Querying Apple Unified Logs from an iOS Device" (2025-05) — https://abrignoni.blogspot.com/2025/05/extraction-processing-querying-apple.html
16. Mandiant, macos-UnifiedLogs (GitHub README) — https://github.com/mandiant/macos-UnifiedLogs
17. iLEAPP, scripts/artifacts/sms.py — https://raw.githubusercontent.com/abrignoni/iLEAPP/main/scripts/artifacts/sms.py
18. ChatExport, ChatExportKnowledge README — https://github.com/ChatExport/ChatExportKnowledge
19. threeplanetssoftware, Apple Cloud Notes Parser (GitHub README) — https://github.com/threeplanetssoftware/apple_cloud_notes_parser
20. DoubleBlak (Ian Whiffin), "iOS Mail" — https://www.doubleblak.com/blogPost.php?k=iosmail
21. iLEAPP, scripts/artifacts/keyboard.py — https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/keyboard.py
22. Mobile Verification Toolkit, "Indicators of Compromise" — https://docs.mvt.re/en/latest/iocs/
23. Mobile Verification Toolkit, "Records extracted by mvt-ios" — https://docs.mvt.re/en/latest/ios/records/
24. D20 Forensics, "iOS 16 - Now You 'C' It, Now You Don't -- Breaking Down The Biomes Part 1" (2022-09) — https://blog.d204n6.com/2022/09/ios-16-now-you-c-it-now-you-dont.html
25. D20 Forensics, "iOS 16 - 'Paul unsent a message.' ... OR DID HE?!" (2022-09) — https://blog.d204n6.com/2022/09/ios-16-paul-unsent-message-or-did-he.html
