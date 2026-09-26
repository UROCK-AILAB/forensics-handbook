---
title: "파일 형식 식별"
parent: "파일 내용 검색"
grand_parent: "기법 · 분석"
nav_order: 3470
---

# 파일 형식 식별 (File Signature)

파일 앞부분의 고정 바이트인 시그니처 (Signature) 를 읽어 파일 형식을 판단하고, 확장자와 시그니처가 다르면 그 차이를 바이트 그대로 기록합니다.

이 글은 [파일 내용 검색 (Content Search)](index.md) 묶음의 한 편입니다. 형식을 알아야 그 파일을 펼칠지, 본문을 어떻게 뽑을지 정할 수 있습니다.

## 언제 쓰나

- **확장자를 믿기 어려울 때** 씁니다. 확장자는 파일 이름의 일부라서 이름만 바꾸면 달라집니다.
- **내용 검색 전에 처리 방법을 고를 때** 씁니다. ZIP 이면 펼치고, 이미지면 글자 인식으로 보냅니다.
- **이름 없는 데이터 조각을 볼 때** 씁니다. 비할당 영역에서 파일을 되살리는 카빙도 시그니처와 파일 끝 표시를 씁니다. 카빙은 [삭제 데이터 복구](../data-recovery/index.md) 에서 다룹니다.

## 시그니처 표를 읽는 법

공개 목록으로 Gary Kessler 의 파일 시그니처 표 (GCK's File Signatures Table) 가 있습니다[1]. 2002년부터 이어 온 목록이며, 지금은 SEARCH 로 넘어가서 옛 주소 페이지가 SEARCH 사이트(https://filesig.search.org/)로 안내합니다[2].

표를 읽을 때는 네 가지를 지킵니다.

- **한 방향으로만 읽습니다.** 매직 넘버 (Magic Number) 가 맞으면 대개 그 형식이지만, 그 형식의 파일이 늘 그 매직 넘버로 시작하지는 않습니다[1].
- **오프셋을 확인합니다.** 오프셋 0 이 아닌 곳에 시그니처가 있는 형식도 많고, 표에는 "[X byte offset]" 으로 적혀 있습니다.
- **겹치는 값이 있습니다.** 여러 형식이 같은 시그니처를 쓰기도 합니다.
- **끝도 봅니다.** 일부 형식은 파일 끝 표시인 트레일러 (Trailer) 도 표에 있습니다.

## 자주 보는 시그니처

아래 값은 모두 오프셋 0 에서 시작합니다[1].

| 형식 | 시작 바이트 | 글자로 보면 | 트레일러 | 같은 값을 쓰는 확장자 |
|---|---|---|---|---|
| PDF | 25 50 44 46 | %PDF | 0A 25 25 45 4F 46 (.%%EOF) | PDF·FDF·AI |
| JPEG | FF D8 (JFIF 는 FF D8 FF E0, Exif 는 FF D8 FF E1) | | FF D9 | |
| PNG | 89 50 4E 47 0D 0A 1A 0A | | 49 45 4E 44 AE 42 60 82 | |
| GIF | 47 49 46 38 37 61 / 47 49 46 38 39 61 | GIF87a / GIF89a | 00 3B | |
| ZIP | 50 4B 03 04 | PK | | DOCX·XLSX·PPTX·JAR·ODT·APK·EPUB 등 |
| ZIP (빈 압축 파일) | 50 4B 05 06 | PK | | |
| ZIP (여러 권으로 나눈 압축 파일) | 50 4B 07 08 | PK | | |
| OLE 복합 파일 (CFB) | D0 CF 11 E0 A1 B1 1A E1 | | | DOC·DOT·XLS·XLA·PPT·PPS·WIZ 등 |
| RAR 4.x 이하 | 52 61 72 21 1A 07 00 | Rar! | | |
| RAR 5.0 | 52 61 72 21 1A 07 01 00 | Rar! | | |
| 7-Zip | 37 7A BC AF 27 1C | 7z | | |
| GZIP | 1F 8B 08 | | | GZ·TGZ |
| BZIP2 | 42 5A 68 | BZh | | |
| XZ | FD 37 7A 58 5A 00 | 7zXZ | | |
| CAB | 4D 53 43 46 | MSCF | | |
| DOS·Windows 실행 파일 | 4D 5A | MZ | | EXE·DLL·SYS·SCR·CPL·OCX 등 |
| TIFF (인텔 바이트 순서) | 49 49 2A 00 | II* | | |
| TIFF (모토로라 바이트 순서) | 4D 4D 00 2A | MM | | |
| BMP | 42 4D | BM | | |
| SQLite | 53 51 4C 69 74 65 20 66 6F 72 6D 61 74 20 33 00 | SQLite format 3 | | |
| EVTX | 45 6C 66 46 69 6C 65 00 | ElfFile | | |
| 레지스트리 하이브 | 72 65 67 66 | regf | | |
| 바로가기 (LNK) | 4C 00 00 00 01 14 02 00 | | | |

PDF 안에는 파일 끝 표시가 여러 개 있을 수 있어서, 카빙할 때는 마지막 것을 잡습니다[1].

뒤쪽 네 형식의 안쪽 구조는 각 기반 페이지에 있습니다. [SQLite 데이터베이스](../../../01-foundations/database-log-formats/sqlite/index.md), [이벤트 로그 형식](../../../01-foundations/database-log-formats/evtx-evt-etl/index.md), [레지스트리 하이브 구조](../../../01-foundations/database-log-formats/registry-hive/index.md), [바로가기 형식](../../../01-foundations/shell-document-formats/shell-link-lnk.md) 을 봅니다.

HWP·ALZ·EGG 처럼 국내에서 많이 쓰는 형식은 위 공개 표에 없으므로 헥스 편집기로 직접 확인합니다. HWP 문서의 구조는 [문서 메타데이터](../../../02-artifacts/embedded-metadata/document-metadata/index.md) 에서 다룹니다.

## 시그니처 하나에 형식이 여럿일 때

### ZIP 계열

ZIP 을 바탕으로 한 형식에는 DOCX·PPTX·XLSX·JAR·ODT·ODP·OTT·APK·KMZ·XPI·XPS·EPUB 등이 있습니다[1]. OOXML(DOCX·PPTX·XLSX) 시그니처는 `50 4B 03 04 14 00 06 00` 입니다[1]. 뒤 4바이트는 ZIP 로컬 파일 헤더의 "추출에 필요한 버전"(0x04) 필드와 "일반 목적 비트 플래그"(0x06) 필드입니다[4].

OOXML 에는 따로 부헤더 (Sub-header) 가 없고 확장자를 .ZIP 으로 바꾸면 ZIP 으로 열리므로, 시그니처만으로는 OOXML 과 일반 ZIP 을 가르기 어렵습니다. 안쪽 항목을 펼쳐 봐야 하며, 방법은 [압축·복합 파일 펼치기](archive-expansion.md) 에 있습니다.

### OLE 복합 파일 계열

DOC·XLS·PPT 를 비롯한 여러 확장자가 같은 8바이트 `D0 CF 11 E0 A1 B1 1A E1` 을 쓰기 때문에 시그니처만으로는 이 확장자들을 가를 수 없습니다. 안쪽 구조는 [OLE 복합 파일](../../../01-foundations/shell-document-formats/compound-file-binary.md) 에서 다룹니다.

CFB 는 시그니처 뒤의 필드까지 보면 한 번 더 확인할 수 있습니다. 복합 파일 헤더는 반드시 파일 맨 앞(오프셋 0)에 있으며[3], 확인에 쓰는 필드는 다음과 같습니다.

| 오프셋 | 크기 | 필드 | 명세 값 |
|---|---|---|---|
| 0x00 | 8 | 헤더 시그니처 | D0 CF 11 E0 A1 B1 1A E1 |
| 0x08 | 16 | 헤더 CLSID | 쓰지 않으며 모두 0 |
| 0x18 | 2 | 부 버전 | 주 버전이 3 이나 4 이면 0x003E |
| 0x1A | 2 | 주 버전 | 0x0003 또는 0x0004 |
| 0x1C | 2 | 바이트 순서 | 0xFFFE. 모든 정수가 리틀 엔디언이라는 표시 |
| 0x1E | 2 | 섹터 시프트 | 버전 3 은 0x0009(512바이트), 버전 4 는 0x000C(4,096바이트) |
| 0x20 | 2 | 미니 섹터 시프트 | 0x0006(64바이트) |

오프셋은 명세의 필드 크기를 차례로 더해 얻은 값입니다.

아래는 명세 값으로 만든 버전 3 헤더의 첫 34바이트이며, 특정 파일에서 뽑은 바이트가 아닙니다.

```
오프셋    00 01 02 03 04 05 06 07  08 09 0A 0B 0C 0D 0E 0F
00000000  D0 CF 11 E0 A1 B1 1A E1  00 00 00 00 00 00 00 00
00000010  00 00 00 00 00 00 00 00  3E 00 03 00 FE FF 09 00
00000020  06 00
```

- 0x00~0x07 은 시그니처입니다.
- 0x08~0x17 의 16바이트는 CLSID 이고 모두 0 입니다.
- 0x18 의 `3E 00` 은 부 버전 0x003E 입니다.
- 0x1A 의 `03 00` 은 주 버전 3 입니다.
- 0x1C 의 `FE FF` 는 바이트 순서 0xFFFE 입니다.
- 0x1E 의 `09 00` 은 섹터 시프트 9 입니다. 2⁹ = 512바이트 섹터입니다.
- 0x20 의 `06 00` 은 미니 섹터 시프트 6 입니다. 2⁶ = 64바이트입니다.

버전 4 라면 0x1A 가 `04 00`, 0x1E 가 `0C 00` 이고, 512바이트 헤더 뒤 섹터의 나머지 3,584바이트를 0 으로 채웁니다.

시그니처 8바이트가 맞아도 이 필드들이 명세 값과 다르면 온전한 CFB 헤더로 보기 어렵고, 우연히 같은 바이트로 시작한 조각이거나 손상된 헤더일 수 있습니다.

### 실행 파일

EXE·DLL·SYS·SCR·CPL·OCX 는 모두 `4D 5A`(MZ)로 시작합니다. 실행 파일의 종류와 정보는 [실행 파일 메타데이터](../../../02-artifacts/embedded-metadata/pe-header-version-info-digital-signature.md) 에서 봅니다.

## 절차

1. 파일 앞부분을 읽습니다. 트레일러가 있는 형식이면 끝부분도 읽습니다.
2. 시그니처 표와 맞춰 봅니다. 오프셋 0 이 아닌 곳에 시그니처가 있는 형식을 빠뜨리지 않습니다.
3. 겹치는 시그니처면 뒤 필드를 더 봅니다. CFB 라면 위의 헤더 필드를 확인합니다.
4. ZIP·CFB 처럼 다른 파일을 담는 형식이면 여기서 멈추지 않습니다. [압축·복합 파일 펼치기](archive-expansion.md) 로 넘깁니다.
5. 확장자와 비교해 "일치", "불일치", "판단 못 함" 셋으로 나눕니다.
6. 판단 근거를 적습니다. 근거는 오프셋과 바이트 값입니다.

## 확장자와 내용이 다를 때

Windows Search 의 필터는 파일 이름 확장자·MIME 형식·CLSID 로 파일 종류와 연결됩니다. 필터 하나가 여러 형식을 처리할 수 있지만 한 형식에는 필터가 하나만 붙습니다[5].

그래서 확장자를 바꾼 파일은 바뀐 확장자의 필터로 처리될 가능성이 크고, 그러면 그 파일의 본문은 색인에 들어가지 않을 수 있습니다. 필터를 찾는 순서는 [본문 추출과 글자 인식](text-extraction-ocr.md) 에, 색인 자체는 [윈도 검색 색인 DB](../../../02-artifacts/file-folder-usage/windows-search/index.md) 에 있습니다.

## 도구

- **헥스 편집기**: 첫 바이트를 직접 봅니다. 판단이 갈리면 늘 여기로 돌아옵니다.
- **시그니처 표**: Kessler 표와 이를 넘겨받은 SEARCH 사이트를 봅니다.
- **시그니처 데이터베이스로 형식을 추정하는 공개 도구**: 유닉스 계열의 `file` 명령이 예입니다. 도구마다 데이터베이스가 다르므로 결과가 갈리면 헥스로 확인합니다.

## 함정과 한계

- **시그니처가 맞다고 그 형식이 확정되지 않습니다.** 표는 한 방향으로만 읽습니다. 여러 형식이 같은 값을 쓰기도 합니다.
- **고정 바이트가 없는 형식이 있습니다.** 일반 글 파일처럼 앞부분이 정해지지 않은 형식은 이 방법으로 판단하지 못합니다.
- **컨테이너 시그니처는 겉만 알려 줍니다.** ZIP 이라는 판단만으로는 DOCX 인지 APK 인지 알 수 없습니다.
- **PDF 트레일러는 하나가 아닐 수 있습니다.** 카빙에서 첫 번째 `%%EOF` 에서 끊으면 파일 뒷부분을 잃습니다.
- **앞부분이 덮어써진 파일은 시그니처가 없습니다.** "형식을 모른다" 는 "형식이 없다" 와 다릅니다.
- **암호를 건 파일은 겉 형식만 보입니다.** 이런 파일은 [암호화 증거 다루기](../encrypted-evidence/index.md) 로 넘깁니다.

## 결과를 어떻게 해석하나

결과는 바이트로 적습니다. 예를 들어 "확장자는 .jpg 이고, 오프셋 0 의 4바이트는 `25 50 44 46`(%PDF)이다" 처럼 씁니다. "PDF 를 그림 파일로 위장했다" 는 의도를 판단한 문장이라 시그니처만으로는 쓸 수 없습니다.

시그니처는 이름을 언제 누가 바꿨는지 알려 주지 않는데, 그 시점은 파일 시스템 기록에서 따로 찾아봅니다. [마스터 파일 테이블](../../../02-artifacts/filesystem/mft.md), [USN 변경 저널](../../../02-artifacts/filesystem/usnjrnl.md), [이 파일은 어디서 왔나](../../../04-scenarios/activity/file-origin.md) 를 함께 봅니다.

## 참고 문헌

- Gary Kessler, "GCK's File Signatures Table" (최종판) — https://www.garykessler.net/library/file_sigs_GCK_latest.html
- Gary Kessler, "GCK's File Signatures Table" 옛 주소 안내 페이지, 2025-04-26 — https://www.garykessler.net/library/file_sigs.html
- Microsoft Learn, "[MS-CFB]: Compound File Header" — https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-cfb/05060311-bfce-4b12-874d-71fd4ce63aea
- PKWARE, ".ZIP File Format Specification" (APPNOTE.TXT) 버전 6.3.10, 2022-11-01 — https://pkware.cachefly.net/webdocs/casestudies/APPNOTE.TXT
- Microsoft Learn, "Understanding filter handlers in Windows Search" — https://learn.microsoft.com/en-us/windows/win32/search/-search-ifilter-about
