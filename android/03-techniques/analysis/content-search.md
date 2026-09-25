---
title: "콘텐츠 검색"
parent: "기법 · 분석"
nav_order: 1530
---

# 콘텐츠 검색 (Content Search)

## 한 줄 요약

수집한 파일과 이미지에서 이름·번호·낱말·URL 같은 검색어를 찾는 방법이고, 찾기 전에 파일을 풀고 인코딩별로 검색어를 만들고, 찾은 뒤에는 적중 위치를 파일 구조로 되짚어 그 바이트가 무엇인지 밝히는 데까지 다룹니다.

## 언제 쓰나

아티팩트 도구가 읽어 주는 표만으로는 답이 나오지 않을 때 씁니다. 전용 해석기가 없는 앱 폴더에서 장소 이름이나 검색어를 찾을 때, 스키마를 모르는 파일에서 URL 을 찾을 때, 지운 레코드나 옛 버전 페이지가 파일 어딘가에 남았는지 볼 때가 여기에 들어갑니다. 반대로 도구가 이미 칸 단위로 읽어 주는 기록(예: [크롬 (Chrome for Android)](../../02-artifacts/browsers/chrome/index.md) 의 방문·검색어 표)은 표를 먼저 보고, 콘텐츠 검색은 표에 없는 곳을 메우는 데 씁니다.

이 페이지는 검색 절차와 결과 해석을 다룹니다. 지운 레코드를 되살리는 방법은 [삭제 데이터 복구](data-recovery/index.md), 앱 폴더를 처음 살피는 순서는 [앱 데이터 분석](app-data-analysis/index.md), 적중한 기록을 시간 축에 올리는 방법은 [타임라인 작성](timeline/index.md) 페이지에 있습니다.

## 검색 결과에 영향을 주는 버전 차이

검색이 되느냐 마느냐는 먼저 저장 공간이 평문으로 보이느냐에 달렸습니다. 아래 표는 이 페이지의 출처로 확인한 범위만 적었고, 삼성 One UI 가 이 동작을 바꾸는지는 확인하지 못했습니다.

| 항목 | 내용 | 검색에 미치는 영향 |
|---|---|---|
| 파일 기반 암호화 (FBE) | Android 7.0 에서 지원을 시작했고, Android 10 이후 출시 기기는 의무입니다 [12] | 키 없이 뜬 `/data` 물리 이미지에서는 파일 내용이 암호문이라 검색어가 걸리지 않습니다 |
| 파일 이름 암호화 | 키가 없으면 디렉터리 목록의 이름이 base64url 모양으로 보이고, 긴 이름은 해시로 줄여 보입니다 [13] | 파일 이름으로 찾는 검색도 키 없는 이미지에서는 쓸 수 없습니다 |
| 메타데이터 암호화 | Android 9 에서 지원을 시작했고, Android 11 이후 출시 기기는 내부 저장소에서 의무입니다. 디렉터리 배치·파일 크기·권한·시각을 암호화합니다 [14] | 물리 이미지에서 파일 시스템 구조를 따라가며 찾는 방법도 막힙니다 |
| 앱 사용 기록 파일 형식 | 현행 AOSP 기본 버전 5 는 패키지 이름을 번호(토큰)로 바꿔 저장하고, 대응표는 `mappings` 파일에 따로 둡니다 [10] | 기록 파일에서 패키지 이름 문자열을 찾으면 걸리지 않습니다 |

그래서 실무에서 검색하는 대상은 대부분 논리 수집이나 파일 시스템 수집으로 얻은 평문 파일입니다. 암호화가 수집과 복구에 주는 제약은 [저장 공간 암호화](../../01-foundations/storage/encryption/index.md) 와 [모바일 증거 확보](../acquisition/mobile-acquisition/index.md) 페이지에 있습니다.

## 절차

1. **질문과 검색어 목록을 먼저 적습니다.** 사람 이름, 계정, 전화번호, URL, 파일 이름처럼 찾을 대상을 정하고, 같은 대상을 여러 표기로 적어 둡니다. 전화번호라면 하이픈이 들어간 형태와 국가 번호가 붙은 형태를, 이름이라면 줄임말과 영문 표기를 함께 넣습니다. 이 목록은 보고서에 그대로 붙일 수 있게 날짜와 함께 보관합니다.

2. **사본에서 작업하고, DB 는 부속 파일과 함께 옮깁니다.** SQLite DB 는 같은 폴더의 `-wal`, `-shm`, `-journal` 과 한 묶음이라서, 주 파일만 떼어 내면 WAL 에만 있던 커밋된 거래를 잃습니다 [2]. 검색 도구나 DB 브라우저로 원본을 열면 체크포인트가 일어나 WAL 내용이 주 파일로 합쳐질 수 있어서, 해시를 남긴 사본을 엽니다. 해시를 남기는 방법은 [모바일 증거 확보](../acquisition/mobile-acquisition/index.md) 페이지를 봅니다.

3. **풀 수 있는 것부터 풉니다.** 압축되거나 바이너리로 적힌 파일은 그대로 찾으면 검색어가 걸리지 않습니다. 아래 표의 파일은 먼저 풀어 텍스트나 원래 바이트로 바꾼 뒤 찾습니다.

   | 파일 | 풀어야 하는 까닭 | 자세한 곳 |
   |---|---|---|
   | 버그 리포트 zip | zip 안에 dumpsys·dumpstate·logcat 을 담은 본문 텍스트와, 기기 파일을 옮겨 담은 `FS/` 폴더가 들어 있습니다 [9] | [버그 리포트 (bugreport)](../../02-artifacts/logs/bugreport.md) |
   | DropBox 기록 | 압축한 항목은 파일 이름 끝에 `.gz` 가 붙습니다 [8] | [앱 오류·종료 기록](../../02-artifacts/app-usage/crash-records.md) |
   | ABX 파일 | 앞 4바이트가 `ABX` 와 버전 바이트 0 이고, 정수·실수를 글자가 아닌 원래 이진 형식으로 씁니다 [4] | [안드로이드 바이너리 XML (ABX)](../../01-foundations/data-formats/abx.md) |
   | 프로토콜 버퍼 | 숫자는 varint 로, 문자열은 varint 길이 뒤에 내용으로 적히고, 필드 이름은 파일 안에 없습니다 [5] | [프로토콜 버퍼 (Protocol Buffers)](../../01-foundations/data-formats/protobuf.md) |
   | LevelDB `.ldb` | 데이터가 Snappy 로 압축될 수 있어 풀지 않고 찾거나 카빙하면 잘 걸리지 않습니다 [6] | [LevelDB와 IndexedDB](../../01-foundations/data-formats/leveldb-indexeddb.md) |
   | 브라우저·웹뷰 HTTP 캐시 | 본문을 서버가 보낸 그대로(Content-Encoding 이 적용된 상태) 저장해서 압축돼 있을 수 있습니다 [7] | [크롬 (Chrome for Android)](../../02-artifacts/browsers/chrome/index.md) |

4. **인코딩별로 검색어를 바이트로 만듭니다.** 같은 낱말도 UTF-8 과 UTF-16 에서 바이트가 다릅니다. SQLite DB 는 파일 머리 오프셋 56 의 4바이트 값으로 글자 인코딩을 밝히고, 1 은 UTF-8, 2 는 UTF-16le, 3 은 UTF-16be 입니다 [1]. ABX 는 UTF-8 만 씁니다 [4]. 인코딩을 모르는 파일은 세 가지를 모두 찾습니다. 아래는 명세로 만든 예시입니다.

   | 인코딩 | "안녕" 의 바이트 |
   |---|---|
   | UTF-8 | `EC 95 88 EB 85 95` |
   | UTF-16LE | `48 C5 55 B1` |
   | UTF-16BE | `C5 48 B1 55` |

5. **숫자는 글자로만 찾지 않습니다.** SQLite 레코드의 정수는 빅엔디언 이진값이고 [1], 프로토콜 버퍼는 varint 로 [5], ABX 는 원래 이진 형식으로 [4] 숫자를 씁니다. 그래서 시각이나 번호를 10진 글자로 찾으면 이런 파일 안의 값은 걸리지 않습니다. 숫자는 파일을 해석기로 풀어 칸 단위로 찾거나, 형식에 맞는 이진 표현으로 바꿔 찾습니다.

6. **정규식은 모양이 정해진 대상에 씁니다.** 파일 이름·URL·계정처럼 모양이 정해진 대상은 정규식이 낱말 목록보다 빠뜨림이 적습니다. 예를 들어 MediaProvider 는 휴지통에 넣은 파일과 저장 중인 파일의 이름을 아래 정규식으로 알아봅니다 [11]. 이 모양의 이름이 무엇을 뜻하는지는 [미디어 저장소 (MediaStore)](../../02-artifacts/media/mediastore/index.md) 페이지에 있습니다.

   ```
   (?i)^\.(pending|trashed)-(\d+)-([^/]+)$
   ```

7. **적중 위치를 파일 구조로 되짚습니다.** 적중한 오프셋만 적고 끝내지 말고, 그 바이트가 살아 있는 레코드인지, 지워진 뒤 남은 빈 공간인지, WAL 의 옛 프레임인지 가립니다. 아래 "직접 되짚어 보기" 에 SQLite 파일에서 되짚는 계산이 있습니다.

8. **적중마다 근거를 한 줄로 남깁니다.** 파일 경로, 오프셋, 인코딩, 쓴 검색어, 풀기 단계(압축 해제·ABX 변환 등), 도구와 버전을 함께 적어 두면 다른 사람이 같은 결과를 다시 낼 수 있습니다.

## 직접 되짚어 보기

### SQLite 레코드에서 글자와 숫자가 적히는 모양

SQLite 레코드는 머리 길이(varint), 칸마다 직렬 타입(serial type) varint, 그리고 본문 순서로 적힙니다. 13 이상 홀수 직렬 타입 N 은 (N−13)/2 바이트짜리 문자열이고 끝에 NUL 이 없으며, 2 는 2바이트 부호 있는 정수입니다 [1]. 칸이 "안녕"(UTF-8)과 1000 두 개인 레코드를 명세대로 만들면 아래와 같습니다(명세로 만든 예시).

```
03          머리 길이 3바이트(자기 자신 포함)
19          직렬 타입 25 → (25−13)/2 = 6바이트 문자열
02          직렬 타입 2  → 2바이트 정수
EC 95 88 EB 85 95   "안녕" (UTF-8)
03 E8               1000 (빅엔디언)
```

문자열은 본문에 그대로 들어가서 UTF-8 검색어 `EC 95 88 EB 85 95` 로 걸리지만, 1000 은 `03 E8` 두 바이트라서 글자 "1000" 으로는 걸리지 않습니다. 같은 DB 가 UTF-16le 라면 "안녕" 은 4바이트 `48 C5 55 B1` 이고 직렬 타입은 21(`15`)이 됩니다.

### 적중 오프셋에서 페이지 찾기

SQLite 파일은 같은 크기의 페이지로 나뉘고, 페이지 크기는 파일 머리 오프셋 16 의 2바이트(빅엔디언)에 있습니다 [1]. 주 DB 파일에서 오프셋 X 에 적중했다면 그 바이트는 페이지 번호 X ÷ 페이지 크기(몫) + 1 에 있습니다. 그 페이지 머리(1번 페이지만 오프셋 100 부터)의 첫 바이트가 13 이면 표 잎 페이지이고, 적중 위치가 셀 포인터가 가리키는 셀 안인지, 첫 freeblock 부터 이어지는 빈 조각 안인지를 보면 살아 있는 레코드인지 지워진 뒤 남은 바이트인지 가를 수 있습니다 [1]. 페이지 안 구조와 되살리는 방법은 [SQLite 데이터베이스](../../01-foundations/data-formats/sqlite/index.md) 와 [삭제 데이터 복구](data-recovery/index.md) 페이지에 있습니다.

`-wal` 파일에서 적중했다면 계산이 다릅니다. WAL 은 32바이트 머리 뒤에 "24바이트 프레임 머리 + 페이지 한 장" 이 이어지므로 [1], 오프셋 X 는 (X − 32) ÷ (24 + 페이지 크기)(몫) + 1 번째 프레임에 있습니다. 그 프레임 머리의 처음 4바이트가 DB 페이지 번호이고, 프레임의 salt 두 값이 WAL 머리와 같고 누적 체크섬이 맞아야 유효한 프레임입니다 [1]. 체크포인트 뒤 WAL 을 처음부터 다시 쓸 때 salt 가 바뀌므로, salt 가 맞지 않는 프레임은 그 전에 쓴 옛 프레임이라서 거기서 적중한 내용은 지금 DB 에 없는 옛 버전일 수 있습니다.

한 번은 이렇게 손으로 되짚고, 그다음에는 사본을 SQL 로 열어 같은 값을 찾아 맞춰 봅니다. 칸 이름을 모를 때는 스키마 표(`sqlite_schema`)[1] 로 표와 칸 이름을 먼저 확인한 뒤 `WHERE 칸 LIKE '%검색어%'` 처럼 칸마다 찾습니다. 바이트 검색에는 걸렸는데 SQL 결과에 없다면, 그 적중은 빈 공간이나 WAL 옛 프레임·저널에만 남은 내용일 수 있습니다.

## 도구

어느 한 도구에 기대지 말고 성격이 다른 도구를 섞어 서로 맞춰 봅니다.

| 도구 종류 | 쓰임 | 주의 |
|---|---|---|
| 아티팩트 해석 도구(예: ALEAPP) | 알려진 기록을 칸 단위로 풀어 보여 주고, 풀어 낸 결과에서 찾기 쉽습니다 | 도구가 모르는 파일과 빈 공간은 다루지 않습니다. ALEAPP 에는 WAL 문자열을 다루는 모듈(`walStrings.py`)이 따로 있지만 [15], 이 페이지에서는 이름만 확인했습니다 |
| SQLite 명령줄 도구·DB 브라우저 | 사본을 열어 표·칸 단위로 찾습니다 | 원본을 열면 WAL 이 합쳐질 수 있어 사본만 엽니다 [2] |
| 헥스 편집기·바이너리 검색 도구 | 바이트 열로 찾고, 적중 오프셋을 구조로 되짚습니다 | 인코딩마다 검색어를 따로 넣어야 합니다 |
| 형식별 변환 도구(ABX 변환, 프로토콜 버퍼 원시 해독, 압축 해제) | 이진 파일을 텍스트로 바꾼 뒤 찾습니다 | 프로토콜 버퍼는 `.proto` 없이 풀면 필드 번호와 형식만 보입니다 [5] |

도구 결과를 믿기 전에 확인하는 방법은 [도구 검증](../reporting/tool-validation.md) 페이지에 있습니다.

## 함정과 한계

**암호화한 DB 와 암호화한 칸에서는 걸리지 않습니다.** SQLCipher 로 암호화한 DB 는 파일 첫 16바이트에 난수 salt 가 들어가 `SQLite format 3` 매직부터 보이지 않고, 파일 전체가 무작위 데이터처럼 보이며, 롤백 저널과 WAL 의 페이지도 같은 키로 암호화합니다 [3]. 파일은 평범한 SQLite 로 열리지만 특정 칸 값만 암호문(Base64 문자열)으로 넣는 앱도 있어서, 공개 도구 kakaodecrypt 는 카카오톡 `chat_logs` 의 `message`·`attachment` 칸을 이런 칸으로 다룹니다 [16]. 이런 칸은 원문 검색어로도, 검색어를 Base64 로 바꾼 값으로도 걸리지 않고, 칸의 의미는 [카카오톡 (KakaoTalk)](../../02-artifacts/messengers/kakaotalk/index.md) 페이지에 있습니다.

**압축과 이진 표기는 빠뜨림을 만듭니다.** 절차 3·5 에서 본 것처럼 Snappy·gzip·HTTP 압축과 varint·이진 정수는 단순 검색을 비껴갑니다. 앱 사용 기록의 버전 5 파일은 이름을 토큰 번호로 바꿔 두어서, `mappings` 파일을 빼고 뽑으면 이름 대신 번호만 남습니다 [10]. 기록 해석은 [앱 사용 기록 (usagestats)](../../02-artifacts/app-usage/usagestats/index.md) 페이지를 봅니다.

**긴 값은 페이지를 넘어 나뉩니다.** 한 페이지에 다 들어가지 않는 레코드는 뒷부분을 넘침(overflow) 페이지에 두고, 넘침 페이지는 앞 4바이트에 다음 넘침 페이지 번호를 적습니다 [1]. 구조로 보면 긴 글이 나뉘는 자리에 검색어가 걸쳐 있으면 바이트 검색으로는 걸리지 않을 수 있어서, 긴 본문은 SQL 로 칸 값을 꺼내 다시 찾습니다.

**없다는 결과는 없었다는 뜻이 아닙니다.** 현행 AOSP 의 플랫폼 SQLite 는 `SQLITE_SECURE_DELETE` 와 `SQLITE_DEFAULT_AUTOVACUUM=1` 로 빌드해서 지운 내용을 0 으로 덮고 빈 페이지를 커밋마다 잘라 내므로 [17], 지운 레코드가 빈 공간에 남지 않는 경우가 많습니다. 다만 SQLite 를 직접 넣어 쓰는 앱이나 DB 를 만들 때 설정을 바꾼 앱은 이 기본값을 따르지 않을 수 있습니다. 이 제약과 WAL·저널이 그나마 남기는 흔적은 [삭제 데이터 복구](data-recovery/index.md) 페이지에 정리돼 있습니다. 캐시도 같아서, ALEAPP 의 HTTP 캐시 모듈 설명은 캐시에 URL 이 없다고 해서 그 URL 을 받은 적이 없다는 증거는 아니라고 적습니다 [7].

**날짜 문자열은 형식이 제각각입니다.** 관찰한 폰의 logcat 기본 형식 줄은 `##-## ##:##:##.###` 모양으로 연도가 없었고, `dumpsys usagestats` 의 `time="..."` 값에는 한글이 섞여 있었습니다 (확인 범위: SM-S937N, Android 16, One UI 8.5). 그래서 날짜를 글자로 찾을 때는 파일마다 실제 표기를 먼저 확인하고 그 모양에 맞춰 검색어를 만듭니다. 표기별 변환은 [타임라인 작성](timeline/index.md) 과 [시각 값](../../01-foundations/value-decoding/time-values.md) 페이지에 있습니다.

**적중 수가 많다고 중요한 것은 아닙니다.** 흔한 낱말이나 짧은 숫자는 로그·캐시·라이브러리 파일에서 무더기로 걸립니다. 적중을 파일 종류별로 묶고, 사람이 만든 내용이 들어가는 파일(메시지 DB, 문서, 알림 기록 등)부터 봅니다.

## 결과를 어떻게 해석하나

적중이 알려 주는 사실은 "수집한 시점에 이 파일의 이 위치에 이 바이트가 있었다" 까지입니다. 그 바이트를 누가 입력했는지, 화면에 보였는지, 보냈는지는 적중만으로 알 수 없고, 적중 위치를 레코드와 칸으로 되짚은 뒤 그 기록의 의미를 해당 아티팩트 페이지로 따져야 합니다. 예를 들어 HTTP 캐시 항목은 그 URL 을 응답 시각에 받거나 다시 확인했다는 기록일 뿐, 페이지가 화면에 표시됐다는 뜻은 아니고 방문 기록도 아닙니다 [7].

적중이 살아 있는 레코드에 있는지, 빈 공간·WAL 옛 프레임·저널에 있는지도 해석을 바꿉니다. 살아 있는 레코드는 앱이 수집 시점에 쓰던 내용이고, 빈 공간이나 옛 프레임의 내용은 한때 있었다가 바뀌거나 지워진 내용일 수 있지만 언제 바뀌었는지는 따로 확인해야 합니다. 찾지 못한 경우에는 검색한 범위(파일 목록, 풀기 단계, 인코딩)를 함께 적어서, 어디까지 찾았는지를 결과로 남깁니다.

보고서에는 기록이 말하는 만큼만 씁니다.

> 사본으로 뜬 (앱) 의 메시지 DB 에서 검색어 "(검색어)" 를 UTF-8 로 찾았고, 주 DB 파일의 (페이지 번호) 번 페이지 살아 있는 레코드 1건과, `-wal` 파일에서 salt 가 WAL 머리와 맞지 않는 프레임 1건에 같은 문자열이 있었습니다. 뒤의 1건은 수집 시점의 DB 에는 없는 옛 버전 페이지의 내용입니다. 검색 범위는 (파일 목록) 이고, 압축·암호화된 파일은 범위에 들지 않았습니다.

보고서 전체의 틀은 [포렌식 보고서](../reporting/forensic-report.md), 지운 대화를 찾는 흐름은 [지운 대화와 사진 찾기](../../04-scenarios/activity/deleted-content.md) 페이지에 있습니다.

## 참고 문헌

1. Database File Format — SQLite, https://www.sqlite.org/fileformat2.html
2. Write-Ahead Logging — SQLite, https://www.sqlite.org/wal.html
3. SQLCipher Design — Zetetic, https://www.zetetic.net/sqlcipher/design/
4. BinaryXmlSerializer.java — AOSP frameworks/libs/modules-utils (main), https://android.googlesource.com/platform/frameworks/libs/modules-utils/+/refs/heads/main/java/com/android/modules/utils/BinaryXmlSerializer.java
5. Encoding — Protocol Buffers Documentation, https://protobuf.dev/programming-guides/encoding/
6. Hang on! That's not SQLite! Chrome, Electron, and LevelDB — CCL Solutions Group, https://www.cclsolutionsgroup.com/post/hang-on-thats-not-sqlite-chrome-electron-and-leveldb
7. ALEAPP chromiumHttpCache.py — abrignoni/ALEAPP, https://raw.githubusercontent.com/abrignoni/ALEAPP/main/scripts/artifacts/chromiumHttpCache.py
8. DropBoxManagerService.java — AOSP frameworks/base (GitHub 미러, main), https://raw.githubusercontent.com/aosp-mirror/platform_frameworks_base/main/services/core/java/com/android/server/DropBoxManagerService.java
9. Capture and read bug reports — Android Developers, https://developer.android.com/studio/debug/bug-report
10. UsageStatsDatabase.java — AOSP frameworks/base (GitHub 미러, main), https://raw.githubusercontent.com/aosp-mirror/platform_frameworks_base/main/services/usage/java/com/android/server/usage/UsageStatsDatabase.java
11. FileUtils.java — AOSP packages/providers/MediaProvider (main), https://android.googlesource.com/platform/packages/providers/MediaProvider/+/refs/heads/main/src/com/android/providers/media/util/FileUtils.java
12. File-based encryption — Android Open Source Project, https://source.android.com/docs/security/features/encryption/file-based
13. Filesystem-level encryption (fscrypt) — docs.kernel.org, https://docs.kernel.org/filesystems/fscrypt.html
14. Metadata encryption — Android Open Source Project, https://source.android.com/docs/security/features/encryption/metadata
15. ALEAPP scripts/artifacts 폴더 목록 — abrignoni/ALEAPP (GitHub API), https://api.github.com/repos/abrignoni/ALEAPP/contents/scripts/artifacts
16. kakaodecrypt.py — jiru/kakaodecrypt, https://github.com/jiru/kakaodecrypt/blob/HEAD/kakaodecrypt.py
17. dist/Android.bp — AOSP external/sqlite (main), https://android.googlesource.com/platform/external/sqlite/+/refs/heads/main/dist/Android.bp
