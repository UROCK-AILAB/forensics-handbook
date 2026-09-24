---
title: "웹캐시 DB"
parent: "인터넷 익스플로러·옛 엣지"
grand_parent: "아티팩트 · 인터넷·브라우저"
nav_order: 1800
---

# 웹캐시 DB (WebCacheV01.dat)

## 한 줄 요약

IE 10 이후의 인터넷 익스플로러와 옛 엣지(EdgeHTML)는 방문 기록·캐시·쿠키·내려받기 기록을 `WebCacheV01.dat` 에 모읍니다. 이 파일은 사용자마다 하나씩 있는 ESE 데이터베이스입니다. 기록은 컨테이너 (Container) 단위로 나뉘어 표에 들어가고, 행마다 주소와 FILETIME 시각이 남습니다.

## 무엇을 기록하나 · 왜 생기나

IE 4~9 는 이 기록을 용도별 `index.dat` 파일에 나눠 두었고, 옛 형식은 [옛 기록 파일 (index.dat)](index-dat.md) 에서 다룹니다. IE 10 부터는 `WebCacheV*.dat` 파일 하나에 기록을 두며, 이 파일은 ESE (Extensible Storage Engine) 데이터베이스입니다. 페이지·B-트리·트랜잭션 로그 같은 저장 형식은 [ESE 데이터베이스](../../../01-foundations/database-log-formats/extensible-storage-engine/index.md) 에서 다룹니다.

옛 엣지도 캐시·방문 기록·내려받기 기록을 이 파일 안의 서로 다른 컨테이너에 두고, 새 버전은 쿠키도 이 파일에 둡니다. 컨테이너는 기록을 묶는 단위라서 컨테이너마다 표가 하나씩 따로 생깁니다.


- Windows 11 25H2 에서도 이 폴더와 파일이 있었습니다. 파일 크기는 약 51MB 였습니다. (확인 범위: Windows 11 25H2, 빌드 26200 PC 한 대)

## 위치와 버전별 차이

| 항목 | 내용 |
|---|---|
| 폴더 | `%LOCALAPPDATA%\Microsoft\Windows\WebCache\` |
| 풀어 쓴 경로 | `C:\Users\<사용자>\AppData\Local\Microsoft\Windows\WebCache\` |
| 파일 이름 | `WebCacheV01.dat`, `WebCacheV24.dat` 두 가지가 문서에 나옵니다 |
| 개수 | 사용자마다 하나 |

| 브라우저 | 기록을 두는 곳 |
|---|---|
| IE 4~9 | 용도별 `index.dat` |
| IE 10·11 | `WebCacheV*.dat` |
| 옛 엣지 | `WebCacheV01.dat` 안의 컨테이너(캐시·방문 기록·내려받기 기록·쿠키) |

- 어느 버전이 `V01` 을 쓰고 어느 버전이 `V24` 를 쓰는지는 이번에 연 자료에 나오지 않습니다.
- 수집할 때는 이름을 가리지 않고 `WebCacheV*.dat` 를 모두 가져옵니다.

### 폴더 안의 다른 파일

Windows 11 25H2 PC 의 WebCache 폴더에는 아래 파일이 있었습니다. (확인 범위: Windows 11 25H2, 빌드 26200 PC 한 대)

```
WebCacheV01.dat
WebCacheV01.jfm
V01.chk
V01.log
V0100296.log ~ V0100298.log
V01res00001.jrs
V01res00002.jrs
V01tmp.log
```

로그와 체크포인트 파일은 이름이 `V01` 로 시작하고 확장자가 `.log`·`.chk` 였으며, [윈도 검색 색인 DB](../../file-folder-usage/windows-search/index.md) 처럼 `.jtx`·`.jcp` 확장자를 쓰지 않았습니다. 비정상 종료 상태의 DB 를 JET API 로 열려면 이 로그가 필요합니다. 그래서 폴더를 통째로 수집합니다.

## 구조

아래 표 구성은 공개 분석 도구 plaso 의 WebCache 파서 코드를 기준으로 정리했습니다. 파서가 읽는 범위만 담았으므로 파일 안의 모든 표를 적은 것은 아닙니다.

### 표

| 표 이름 | 파서 기준 | 설명 |
|---|---|---|
| `Containers` | 꼭 있어야 함 | 컨테이너 목록입니다 |
| `LeakFiles` | 꼭 있어야 함 | plaso 가 Filename·CreationTime·LeakId 칸을 읽습니다 |
| `Partitions`, `PartitionsEx` | 있을 수도 있음 | 칸 구성은 아래에 적었습니다 |
| `Container_#` | 컨테이너마다 하나 | `#` 은 컨테이너 번호입니다 |
| `CookieEntryEx_#` | 컨테이너마다 하나 | 쿠키가 들어갑니다. `#` 은 컨테이너 번호입니다 |

### 칸

| 표 | 칸 |
|---|---|
| `Containers` | ContainerId, Name, Directory, SetId, LastScavengeTime, LastAccessTime |
| `Container_#` | EntryId, Url, AccessCount, SyncCount, AccessedTime, CreationTime, ExpiryTime, ModifiedTime, PostCheckTime, SyncTime, ResponseHeaders, RequestHeaders, Filename, FileExtension, FileSize, CacheId, RedirectUrl |
| `CookieEntryEx_#` | ContainerId, EntryId, Name, Value, CookieHash, Flags, Expires, LastModified, RDomain |
| `LeakFiles` | LeakId, Filename, CreationTime (plaso 가 읽는 칸만) |
| `Partitions`, `PartitionsEx` | Directory, PartitionId, PartitionType, LastScavengeTime, TableId |

읽는 순서는 이렇습니다.

1. `Containers` 표에서 ContainerId 와 Name 을 짝지어 적습니다.
2. 이름을 보고 읽을 컨테이너를 고릅니다.
3. 그 번호가 붙은 `Container_#` 표를 엽니다.
4. 쿠키는 같은 번호가 붙은 `CookieEntryEx_#` 표에서 읽습니다.

`Container_#` 의 Filename·FileSize 칸과 캐시 폴더의 실제 파일을 잇는 방법은 [쿠키·캐시 폴더 (INetCookies·INetCache)](inetcookies-inetcache.md) 에서 다룹니다.

### 컨테이너 이름

| 컨테이너 이름 | plaso 가 하는 일 |
|---|---|
| BackgroundTransferApi, Content, Cookies, DOMStore, History, iedownload | 읽습니다 |
| 이름이 `MSHist` 로 시작하는 컨테이너 | 읽습니다 |
| MicrosoftEdge_DNTException, MicrosoftEdge_EmieSiteList, MicrosoftEdge_EmieUserList | 건너뜁니다 |
| wpnidm, iecompat, iecompatua, DNTException, DOMStore | 코드에 "아직 지원하지 않음" 으로 적혀 있습니다 |

- DOMStore 는 두 목록에 모두 나옵니다.
- `MSHist` 이름 규칙과 옛 index.dat 의 관계는 [옛 기록 파일 (index.dat)](index-dat.md) 에서 다룹니다.

### 한 PC 에서 찾은 표 이름

Windows 11 25H2 PC 의 WebCacheV01.dat 사본에서 표 이름 문자열을 찾으면 아래 이름이 나왔습니다. (확인 범위: Windows 11 25H2, 빌드 26200 PC 한 대)

- `Containers`, `LeakFiles`, `PartitionsEx`
- `Container_1` ~ `Container_69` (번호가 띄엄띄엄 있음)
- `CookieEntryEx_#`, `AppCacheEx_#`, `AppCacheEntryEx_#`, `HstsEntryEx_#`
- `MSysObjects`, `MSysObjids`, `MSysLocales`

`Partitions` 라는 이름만 따로 나오지는 않았습니다. `AppCacheEx_#`·`AppCacheEntryEx_#`·`HstsEntryEx_#` 의 뜻과 칸은 이번에 연 자료로 확인하지 못했습니다.

## 증거로서 의미

### 증명하는 것

- 그 사용자 프로필의 DB 에 이 주소의 행이 남아 있었습니다.
- 행이 어느 컨테이너에 들어 있었는지 알 수 있습니다.
- 쿠키 표의 행으로 어느 도메인(RDomain)이 어떤 이름의 쿠키를 남겼는지 알 수 있습니다.
- 행의 시각 칸으로 그 기록을 만들거나 고친 때를 좁힐 수 있습니다.

### 증명하지 못하는 것

- 사용자가 주소를 직접 열었는지, 페이지가 알아서 불러온 자원인지는 행 하나만으로 가르지 못합니다.
- IE 와 옛 엣지가 같은 파일을 쓰므로 행이 어느 브라우저에서 왔는지는 파일만으로 단정하지 않습니다.
- 컨테이너 이름에서 용도를 짐작할 수 있지만 용도를 적은 문서는 이번에 확인하지 못했습니다. 컨테이너의 뜻은 행의 Url 모양과 함께 판단합니다.
- 행이 없다고 방문하지 않았다고 단정하지 않습니다. 기록은 지우거나 정리할 수 있습니다.

보고서에는 "이 사용자 프로필의 WebCacheV01.dat History 컨테이너에 이 주소의 행이 있고, 시각 칸 값은 이렇다" 처럼 기록이 말하는 만큼만 씁니다.

## 시각 해석

- 시각 칸은 모두 FILETIME 입니다. 변환 방법은 [시각 값 형식](../../../01-foundations/value-decoding/filetime-unix-webkit-dos-ole.md) 에서 다룹니다.
- 값이 `0x7FFFFFFFFFFFFFFF` 이면 plaso 는 "기한 없음" 으로 처리합니다.
- 값이 1 인 FILETIME 같은 특수값은 plaso 도 아직 처리하지 않는다고 적어 두었습니다. 변환 결과가 1601년 1월 1일로 나오면 특수값을 먼저 의심합니다.

plaso 는 각 시각 칸에 아래 설명을 붙입니다.

| 표 | 칸 | plaso 가 붙인 뜻 |
|---|---|---|
| `Container_#` | AccessedTime | 마지막 접근 |
| `Container_#` | CreationTime | 만든 시각 |
| `Container_#` | ExpiryTime | 만료 |
| `Container_#` | ModifiedTime | 수정 |
| `Container_#` | PostCheckTime | 사후 확인 |
| `Container_#` | SyncTime | 동기화 |
| `Containers` | LastAccessTime | 마지막 접근 |
| `Containers`, `Partitions` | LastScavengeTime | 마지막 정리 (scavenge) |
| `CookieEntryEx_#` | Expires | 만료 |
| `CookieEntryEx_#` | LastModified | 수정 |

History 컨테이너에서 어느 칸이 "방문 시각" 인지, 그 칸이 UTC 인지 현지 시각인지는 이번에 연 자료로 확인하지 못했습니다. 그래서 시각을 아는 방문 하나를 골라 칸 값과 맞춰 본 뒤 해석합니다. 같은 버전의 Windows 에서 시험 방문을 만들어 비교해도 됩니다.

## 함정과 한계

- **파일이 잠겨 있습니다.** 로그인한 상태에서는 다른 프로세스가 파일을 잡고 있어 일반 복사가 "being used by another process" 로 실패했습니다. 관리자 권한으로 `esentutl` 의 `/y` 복사에 `/vss` 를 붙여 볼륨 섀도 복사본 (Volume Shadow Copy) 에서 복사하면 됐습니다. (확인 범위: Windows 11 25H2, 빌드 26200 PC 한 대)
- **사본은 비정상 종료 상태입니다.** 사용 중인 DB 를 복사한 사본은 머리글 상태가 Dirty Shutdown 이었습니다. (확인 범위: 같은 PC)
- **압수 이미지에서 꺼낸 파일도 대부분 비정상 종료 (dirty shutdown) 상태입니다.** JET API 로 열려면 같은 폴더의 트랜잭션 로그로 먼저 복구해야 합니다. 로그 사슬이 끊겨 복구가 안 되는 경우가 있습니다. 페이지를 직접 해석하는 방식은 로그 없이 읽습니다. (확인 범위: 현장 검체 분석 관찰)
- **원본을 열지 않습니다.** 원본을 열면 내용이 바뀔 수 있습니다. 항상 사본에서 작업합니다. (확인 범위: 현장 검체 분석 관찰)
- **도구마다 행 수가 다를 수 있습니다.** 손상된 ESE DB 는 읽는 방식에 따라 결과 행 수가 달라집니다. B-트리를 끝까지 따라가지 못한 쪽이 적게 냅니다. 두 가지 이상 방식으로 열어 비교합니다. 비교 방법은 [도구 결과 교차 검증](../../../03-techniques/reporting/tool-validation.md) 에서 다룹니다. (확인 범위: 현장 검체 분석 관찰)
- **긴 값이 조용히 망가질 수 있습니다.** ESE 의 긴 값 (Long Value) 은 조각으로 나뉘어 저장됩니다. 조각 경계를 잘못 계산하면 오류 없이 값이 망가집니다. 긴 값이 들어가는 칸은 길이가 그럴듯한지 확인합니다. (확인 범위: 현장 검체 분석 관찰)
- **값이 압축돼 있을 수 있습니다.** ESE 값 압축에는 7비트 ASCII·7비트 유니코드·XPRESS·XPRESS9·XPRESS10·LZ4 가 있습니다. 압축 형식은 [윈도 압축 형식](../../../01-foundations/value-decoding/lznt1-xpress-xpress-huffman.md) 에서 다룹니다. (확인 범위: 현장 검체 분석 관찰)
- **문자열 검색 결과는 표 목록이 아닙니다.** 파일 바이트에서 찾은 표 이름에는 지운 표의 잔재가 섞일 수 있습니다. 표 목록은 카탈로그 (Catalog) 를 해석해서 얻습니다.

## 직접 분석해 보기

### 헥스로 한 번

1. 섀도 복사본에서 뜬 사본을 헥스 편집기로 엽니다.
2. `Container_` 문자열을 찾습니다. 번호가 붙은 표 이름이 여러 개 나옵니다.
3. `CookieEntryEx_` 문자열을 찾습니다. 쿠키 표 이름이 나옵니다.
4. 찾은 번호를 적어 두고, 뒤에서 공개 도구로 연 `Containers` 표의 ContainerId 와 맞춰 봅니다.

이 방법으로 얻는 것은 표 이름 후보뿐입니다. 표 목록은 카탈로그를 해석해야 확정됩니다. 카탈로그와 페이지 구조는 [ESE 데이터베이스](../../../01-foundations/database-log-formats/extensible-storage-engine/index.md) 에서 다룹니다.

### 공개 도구로 한 번

1. 관리자 권한으로 `esentutl` 의 `/y` 복사에 `/vss` 를 붙여 WebCacheV01.dat 사본을 뜹니다. 같은 폴더의 로그 파일도 함께 가져옵니다.
2. `esentutl /mh` 로 사본의 머리글을 봅니다. 아래는 Windows 11 25H2 PC 에서 본 값입니다. (확인 범위: Windows 11 25H2, 빌드 26200 PC 한 대)

   | 머리글 항목 | 본 값 |
   |---|---|
   | Engine ulMagic | 0x89abcdef |
   | Format ulVersion | 0x620,300,620 |
   | cbDbPage | 32768 (페이지 32KB) |
   | State | Dirty Shutdown |
   | Log Required | 665-665 (0x299) |

3. State 가 Dirty Shutdown 이면 JET API 기반 도구로 열기 전에 사본 폴더에서 로그로 복구합니다. 로그가 끊겨 복구가 안 되면 페이지를 직접 해석하는 도구로 엽니다.
4. plaso 의 WebCache 파서처럼 이 파일을 읽는 공개 도구로 타임라인을 뽑습니다.
5. 다른 방식의 도구로 한 번 더 열어 컨테이너별 행 수를 비교합니다.

## 교차 검증

| 아티팩트 | 알려 주는 것 | 링크 |
|---|---|---|
| 옛 기록 파일 | 같은 PC 에서 IE 9 이전에 남긴 기록을 봅니다 | [옛 기록 파일 (index.dat)](index-dat.md) |
| 주소창 입력 주소 | History 행의 주소를 사용자가 직접 입력했는지 봅니다 | [주소창 입력 주소](typedurls-typedurlstime.md) |
| 쿠키·캐시 폴더 | Filename 칸이 가리키는 캐시 파일이 실제로 있는지 봅니다 | [쿠키·캐시 폴더](inetcookies-inetcache.md) |
| 저장 비밀번호 | History 에 남은 주소로 저장 비밀번호 값을 풉니다 | [저장 비밀번호 (IntelliForms)](intelliforms.md) |
| 다운로드 출처 표시 | iedownload 행의 파일에 다운로드 출처 표시가 남았는지 봅니다 | [다운로드 출처 표시](../../filesystem/zone-identifier.md) |
| $MFT·$UsnJrnl | WebCacheV01.dat 와 로그 파일이 언제 만들어지고 바뀌었는지 봅니다 | [$MFT](../../filesystem/mft.md), [$UsnJrnl](../../filesystem/usnjrnl.md) |
| 섀도 복사본 | 이전 시점의 DB 를 꺼내 지운 행을 찾습니다 | [섀도 복사본 활용](../../../03-techniques/analysis/volume-shadow-copy-analysis.md) |
| 시간대 설정 | 시각 칸을 현지 시각으로 바꿀 때 기준을 봅니다 | [시간대 설정](../../system-account/time-zone.md) |
| 다른 브라우저 | 같은 사이트를 다른 브라우저로 썼는지 봅니다 | [크롬 계열 브라우저](../chrome-edge-whale/index.md), [파이어폭스](../firefox/index.md) |

웹 사용 전체를 재구성하는 흐름은 [웹 사용 행위 재구성](../../../04-scenarios/activity/web-activity.md) 에 있습니다.

## 실습

IE 10 이후의 IE 나 옛 엣지를 쓴 공개 검체(NIST CFReDS 등)에서 사용자 프로필 폴더를 꺼내 아래 질문을 풀어 봅니다.

1. WebCache 폴더에 어떤 파일이 있습니까? `WebCacheV01.dat` 와 `WebCacheV24.dat` 가운데 어느 것입니까?
2. `esentutl /mh` 로 본 State 는 무엇입니까? 로그로 복구가 됩니까?
3. `Containers` 표에 컨테이너가 몇 개 있습니까? 이름과 번호를 짝지어 적어 봅니다.
4. History 컨테이너에서 시각을 아는 방문 하나를 고릅니다. 어느 칸이 그 시각과 맞습니까? UTC 로 맞습니까, 현지 시각으로 맞습니까?
5. 두 가지 도구로 같은 사본을 열었을 때 컨테이너별 행 수가 같습니까?
6. iedownload 컨테이너의 행이 가리키는 파일이 디스크에 아직 있습니까?

## 참고 문헌

1. ForensicArtifacts, *artifacts/data/webbrowser.yaml* (WebCacheV*.dat 위치). https://raw.githubusercontent.com/ForensicArtifacts/artifacts/main/artifacts/data/webbrowser.yaml
2. Forensics Wiki, *Internet Explorer* (IE 10 이후 형식, 파일 이름, 경로). https://forensics.wiki/internet_explorer
3. log2timeline/plaso, *plaso/parsers/esedb_plugins/msie_webcache.py* (표·칸·컨테이너 이름, 시각 칸 처리). https://raw.githubusercontent.com/log2timeline/plaso/main/plaso/parsers/esedb_plugins/msie_webcache.py
4. Forensafe 블로그, 옛 엣지(EdgeHTML) 아티팩트 설명 글 (옛 엣지가 쓰는 컨테이너와 쿠키). https://www.forensafe.com/blogs/microsoftedge.html
