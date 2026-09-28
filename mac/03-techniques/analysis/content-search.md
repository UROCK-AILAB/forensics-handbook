---
title: "콘텐츠 검색"
parent: "기법 · 분석"
nav_order: 2250
---

# 콘텐츠 검색 (Content Search)

정해 둔 낱말이나 패턴으로 증거 안의 문자열을 찾는 방법을 다룹니다. 라이브 시스템에서는 스포트라이트 색인을 조회하고 사본 이미지에서는 파일 내용과 원시 바이트를 직접 검사하는데, macOS 에서 검색이 놓치기 쉬운 자리(유니코드 정규화·투명 압축·상시 암호화·로그 가림)까지 함께 봅니다.

## 언제 쓰나

사람 이름, 계좌 번호, 프로젝트 코드명, 주민등록번호 같은 형식처럼 찾을 문자열이 정해져 있을 때 씁니다. 파일 이름만 찾으면 이름을 바꾼 파일이나 메일·메시지 데이터베이스 안의 기록을 놓칠 수 있어서, 검색 범위를 파일 내용과 앱 저장소까지 넓힙니다. 개인정보 파일이 어디 있는지 찾는 흐름은 [개인정보 파일이 어디 있고 밖으로 나갔나 (PII Exposure)](../../04-scenarios/exfiltration/pii-exposure.md) 에서, 악성 코드를 규칙으로 찾는 방법은 [악성 코드 흔적 분석 (Malware Triage)](malware-triage/index.md) 에서 다룹니다.

검색 방법은 대상과 범위에 따라 넷으로 나뉩니다.

| 방법 | 대상 | 잘 찾는 것 | 놓치는 것 |
|---|---|---|---|
| 스포트라이트 조회 (`mdfind`) | 라이브 시스템의 색인된 볼륨 | 속성·날짜·종류로 좁힌 파일 목록 | 색인이 꺼졌거나 제외된 곳 |
| 색인 저장소 읽기 (`store.db`) | 사본 이미지 | 색인에 남은 경로와 kMDItem 속성 | 색인에 들어가지 않은 파일 |
| 파일 단위 검색 | 읽기 전용으로 마운트한 사본 | 파일 본문, 정규식에 맞는 형식 | 압축·암호화된 내용, 앱 저장 형식 안의 값 |
| 원시 바이트 검색 | 볼륨 이미지 전체(빈 공간 포함) | 지운 파일의 조각 | 복호하지 않은 볼륨, 압축된 블록 |

## 절차

1. **검색어 목록과 인코딩 변형을 정합니다.** HFS+ 는 파일 이름을 UTF-16 으로 완전 분해(NFD)해 저장하고 [1], APFS 는 파일 이름을 받은 형태 그대로 UTF-8 로 저장해서 [2][3] 같은 한글 이름이 NFC 로도 NFD 로도 남을 수 있습니다. 그래서 원시 바이트를 찾을 때는 한 낱말을 UTF-8 NFC, UTF-8 NFD, UTF-16 세 가지로 적어 둡니다. 정규화의 원리는 [유니코드 정규화 (NFD·NFC)](../../01-foundations/value-decoding/unicode-normalization.md) 에서 봅니다.
2. **라이브 시스템이면 색인 상태부터 확인합니다.** `mdutil -s` 로 볼륨의 색인 상태를 보고 [4], 색인이 꺼져 있거나 비어 있으면 `mdutil -i off`(색인 끄기)나 `mdutil -E`(로컬 저장소 지우기) [4] 를 누가 실행했는지를 확인할 거리로 적어 둡니다. 라이브 시스템에서 무엇을 먼저 수집할지는 [라이브 대응 (Live Response)](../process-acquisition/live-response/index.md) 을 따릅니다.
3. **스포트라이트로 후보를 좁힙니다.** `mdfind` 는 스포트라이트 메타데이터 값을 조회하고, `-onlyin` 으로 폴더를 제한하며 `-count` 로 개수만, `-0` 으로 결과마다 NUL 문자를 붙여 `xargs -0` 에 넘깁니다 [5]. 쿼리에는 `==`·`!=`·`<`·`>` 같은 비교와 `*` 와일드카드를 쓰고 값에 `c`(대소문자 무시)·`d`(발음 구별 부호 무시) 수식어를 붙일 수 있으며, `kMDItemContentType`·`kMDItemFSContentChangeDate` 같은 속성과 `kind:`·`date:` 필터로 좁힙니다 [5]. 본문 텍스트 속성 `kMDItemTextContent` 는 쿼리에는 쓸 수 있지만 값을 직접 읽지는 못해서 [6], 걸린 파일은 사본에서 다시 열어 문자열을 확인합니다.
4. **사본 이미지에서는 색인 저장소를 읽습니다.** 볼륨의 `.Spotlight-V100` 아래 `store.db` 를 공개 도구로 풀어 색인에 남은 경로와 속성 목록을 얻고, 저장소 위치와 구조는 [스포트라이트 (Spotlight)](../../02-artifacts/file-folder-usage/spotlight/index.md) 에서 봅니다. `store.db` 에는 zlib 이나 LZ4 로 압축한 페이지가 있어서 [7], 파일을 통째로 바이트 검색하면 속성 값이 걸리지 않을 수 있습니다.
5. **파일 단위로 검색합니다.** 사본을 읽기 전용으로 마운트한 뒤 정규식을 쓸 수 있는 도구로 파일 본문을 검사합니다. 공개 도구 YARA 를 예로 들면 규칙의 문자열을 텍스트(큰따옴표), 16진수(중괄호), 정규식(슬래시) 세 가지로 적고, `nocase`(대소문자 무시)·`wide`(두 바이트 문자)·`fullword`(낱말 단위 일치) 수식어를 붙입니다 [8]. 다만 `wide` 는 ASCII 문자 사이에 0 바이트를 끼워 넣을 뿐이고 영어가 아닌 문자의 UTF-16 은 지원하지 않아서 [8], 한글 검색어의 UTF-16 형태는 16진수 문자열로 직접 적습니다. 메일·메시지·메모처럼 SQLite 나 속성 목록 파일에 든 값은 걸린 위치를 형식에 맞게 다시 읽어야 해서 [SQLite 데이터베이스 (SQLite)](../../01-foundations/data-formats/sqlite/index.md) 와 [속성 목록 파일 (Property List)](../../01-foundations/data-formats/plist/index.md) 을 함께 봅니다.
6. **원시 바이트를 검색합니다.** 빈 공간까지 보려면 볼륨 이미지 전체를 검사하는데, Apple 실리콘·T2 Mac 의 내장 저장소는 FileVault 가 꺼져 있어도 볼륨이 암호화돼 있어서 [9] 복호한 볼륨 이미지를 대상으로 합니다. 복호 방법은 [암호화된 증거 다루기 (Encrypted Evidence)](encrypted-evidence/index.md) 에서 다룹니다. 지운 파일을 형식 시그니처로 꺼내는 일은 [삭제 데이터 복구 (Data Recovery)](data-recovery/index.md) 로 넘깁니다.
7. **통합 로그는 따로 검색합니다.** 통합 로그는 메시지 속 동적 문자열을 기본으로 가려 `<private>` 로 보여 주고 정수·실수·불리언 값은 가리지 않아서 [10], 파일 이름이나 계정 이름으로 로그를 찾으면 걸리지 않을 수 있습니다. 로그에서 찾을 사건과 조회 방법은 [통합 로그에서 찾을 것 (Unified Log Events)](../../02-artifacts/logs/unified-log-events/index.md) 에서 봅니다.
8. **결과를 기록합니다.** 걸린 것마다 파일 경로나 이미지 오프셋, 찾은 인코딩, 검색어, 도구와 버전을 적어 둡니다. 같은 파일이 스냅숏이나 백업에도 있으면 여러 번 걸리니 어느 시점의 사본인지도 적고, 시점을 비교하는 방법은 [스냅숏과 백업 비교 (Snapshot·Time Machine Diff)](snapshot-diff.md) 에서 봅니다.

## 도구

| 도구 | 쓰는 곳 | 하는 일 |
|---|---|---|
| `mdfind` | 라이브 시스템 | 스포트라이트 메타데이터 조회 [5] |
| `mdutil` | 라이브 시스템 | 색인 상태 표시·켜기·끄기·지우기 [4] |
| spotlight_parser | 사본 이미지 | `store.db` 를 풀어 텍스트로 출력 [11] |
| mac_apt SPOTLIGHT 플러그인 | 사본 이미지 | 사용자·볼륨 색인 읽기 [12] |
| YARA | 마운트한 사본, 이미지 | 텍스트·16진수·정규식 규칙으로 검사 [8] |

어느 도구든 투명 압축 파일을 풀어서 검사하는지, NFD 로 쪼개진 한글을 찾는지는 도구마다 다를 수 있어서, 알려진 문자열을 넣은 시험 파일로 먼저 확인합니다. 시험 방법은 [도구 검증 (Tool Validation)](../reporting/tool-validation.md) 을 따릅니다.

## 함정과 한계

가장 흔한 함정은 투명 압축입니다. HFS+ 와 APFS 는 파일 내용을 압축해 확장 속성 `com.apple.decmpfs` 나 리소스 포크에 담을 수 있고, 방식에는 zlib·LZVN·LZFSE 등이 있습니다 [13][14]. 이런 파일은 데이터 영역이 비어 있어서 도구가 압축을 풀지 않으면 본문 검색에 걸리지 않고, 원시 바이트 검색에서도 원문 대신 압축 블록 표시(LZFSE 의 `bvx2` 처럼 [15])만 보입니다. 압축 형식은 [압축 형식 (LZFSE·LZ4·zlib)](../../01-foundations/value-decoding/compression.md) 에서 다룹니다. 공개 도구 mac_apt 는 zlib·LZVN·LZFSE 압축 파일을 지원합니다 [16].

`mdfind` 가 파일 본문까지 찾는지는 본문에만 든 낱말로 시험 파일을 만들어 검색해 보고 확인합니다. 주민등록번호처럼 형식으로 찾는 검색은 `mdfind` 에 맡기지 않고 사본에서 정규식을 쓰는 도구로 하며, 스포트라이트 결과는 후보 목록으로만 씁니다. 스포트라이트는 색인된 볼륨과 파일만 찾아서, 색인에서 뺀 폴더나 색인이 꺼진 볼륨은 결과에 나오지 않습니다.

APFS 는 고친 객체를 제자리에 덮어쓰지 않고 새 위치에 써서 [2], 빈 공간에서 걸린 문자열이 지운 파일이 아니라 지금도 남아 있는 파일의 옛 사본일 수 있습니다. 원시 검색에서 걸린 조각을 지운 파일로 보고하기 전에 같은 내용이 현재 파일 시스템에 있는지 확인합니다.

## 결과를 어떻게 해석하나

검색 결과는 "이 위치에 이 인코딩으로 이 문자열이 있었다" 까지만 말해 줍니다. 누가 그 문자열을 썼는지, 언제 파일에 들어갔는지, 사용자가 그 파일을 열어 봤는지는 알려 주지 않아서 파일 시스템 시각과 사용 흔적으로 따로 확인하고, 그 흐름은 [이 파일을 누가 언제 열었나 (File Access)](../../04-scenarios/activity/file-access.md) 와 [타임라인 작성 (Timeline)](timeline/index.md) 에서 봅니다.

걸린 것이 없다는 결과는 문자열이 없었다는 증거가 되지 못합니다. 색인 꺼짐, 투명 압축, 암호화, 정규화 차이, 로그 가림 가운데 무엇을 배제했는지를 함께 적어야 결과의 범위가 드러납니다.

보고서에는 "복호한 데이터 볼륨 사본을 UTF-8 NFC·NFD 와 UTF-16 으로 검색했고, 이 경로의 문서 본문에서 검색어가 나온다. 투명 압축 파일은 도구가 풀어서 검사했다" 처럼 검색 범위, 인코딩, 걸린 위치를 함께 적습니다.

## 참고 문헌

1. Apple, Technical Note TN1150: HFS Plus Volume Format — https://developer.apple.com/library/archive/technotes/tn/tn1150.html
2. Apple, Apple File System Reference (2020-06-22) — https://developer.apple.com/support/downloads/Apple-File-System-Reference.pdf
3. Apple, Apple File System Guide — Frequently Asked Questions (2018-06-04) — https://developer.apple.com/library/archive/documentation/FileManagement/Conceptual/APFS_Guide/FAQ/FAQ.html
4. SS64, mdutil — https://ss64.com/mac/mdutil.html
5. SS64, mdfind — https://ss64.com/mac/mdfind.html
6. Apple, Spotlight Metadata Attributes Reference — Common Attributes (2014-07-15) — https://developer.apple.com/library/archive/documentation/CoreServices/Reference/MetadataAttributesRef/Reference/CommonAttrs.html
7. Joachim Metz, Apple Spotlight store database file format (libyal/dtformats, 0.0.3, 2024-01) — https://raw.githubusercontent.com/libyal/dtformats/main/documentation/Apple%20Spotlight%20store%20database%20file%20format.asciidoc
8. YARA 문서, Writing YARA rules — https://yara.readthedocs.io/en/stable/writingrules.html
9. Apple, Apple Platform Security (2026년 8월) — https://help.apple.com/pdf/security/en_US/apple-platform-security-guide.pdf
10. Apple Developer Documentation, Generating log messages from your code — https://developer.apple.com/tutorials/data/documentation/os/generating-log-messages-from-your-code.json
11. Yogesh Khatri, spotlight_parser README — https://github.com/ydkhatri/spotlight_parser
12. Yogesh Khatri, mac_apt 플러그인 spotlight.py — https://raw.githubusercontent.com/ydkhatri/mac_apt/master/plugins/spotlight.py
13. Apple xnu, bsd/sys/decmpfs.h — https://raw.githubusercontent.com/apple-oss-distributions/xnu/main/bsd/sys/decmpfs.h
14. Joachim Metz, libfsapfs — Apple File System (APFS) 형식 문서 (개정 0.0.18) — https://raw.githubusercontent.com/libyal/libfsapfs/main/documentation/Apple%20File%20System%20(APFS).asciidoc
15. LZFSE 참조 구현, src/lzfse_internal.h — https://raw.githubusercontent.com/lzfse/lzfse/master/src/lzfse_internal.h
16. Yogesh Khatri, mac_apt README (v1.33.2) — https://raw.githubusercontent.com/ydkhatri/mac_apt/master/README.md
