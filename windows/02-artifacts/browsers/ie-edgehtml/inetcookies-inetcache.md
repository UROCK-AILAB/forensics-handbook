---
title: "쿠키·캐시 폴더"
parent: "인터넷 익스플로러·옛 엣지"
grand_parent: "아티팩트 · 인터넷·브라우저"
nav_order: 1840
---

# 쿠키·캐시 폴더 (INetCookies·INetCache)

## 한 줄 요약

IE 는 받은 웹 자원을 캐시 폴더(IE 4~9 는 `Content.IE5`, IE 10 이후는 `INetCache\IE`)에 파일로 저장합니다. 어느 주소가 어느 파일인지는 폴더가 아니라 기록 파일(index.dat 나 WebCacheV01.dat)이 잇습니다. IE 10 이후 쿠키는 WebCache DB 의 쿠키 표에 들어갑니다.

## 무엇을 기록하나 · 왜 생기나

캐시 (Cache) 는 브라우저가 받은 웹 자원의 사본이고, 캐시 폴더에는 이 사본이 파일로 남습니다. 쿠키 (Cookie) 는 웹사이트가 브라우저에 맡겨 두는 이름과 값의 쌍입니다.

IE 4~9 는 캐시 파일을 이름이 8글자인 하위 폴더에 나눠 두고, 어느 파일이 어느 주소에서 왔는지는 캐시 폴더의 `index.dat` 에 적습니다. 쿠키 기록도 `index.dat` 에 적습니다. IE 10 이후는 캐시 기록과 쿠키를 [웹캐시 DB (WebCacheV01.dat)](webcachev01-dat.md) 에 두고, 옛 엣지도 쿠키를 WebCacheV01.dat 에 둡니다.

## 위치와 버전별 차이

| 기록 | IE 4~9 | IE 10 이후 |
|---|---|---|
| 캐시 파일 | `%LOCALAPPDATA%\Microsoft\Windows\Temporary Internet Files\Content.IE5\*\*` | `%LOCALAPPDATA%\Microsoft\Windows\INetCache\IE\*\*` |
| 캐시 기록 | 캐시 폴더의 `index.dat` | WebCache DB 의 `Container_#` 표 |
| 쿠키 | `%APPDATA%\Microsoft\Windows\Cookies\index.dat` | WebCache DB 의 `CookieEntryEx_#` 표 |

- Windows XP 에서 쓰던 경로는 [옛 기록 파일 (index.dat)](index-dat.md) 에 정리했습니다.
- 옛 엣지의 쿠키 폴더로는 아래 두 곳이 알려져 있습니다.

```
C:\Users\<사용자>\AppData\Local\Packages\<패키지 이름>\AC\INetCookies
C:\Users\<사용자>\AppData\Local\Microsoft\Windows\INetCookies
```

### 한 PC 에서 본 폴더

Windows 11 25H2 PC 에서 본 모습입니다.

```
%LOCALAPPDATA%\Microsoft\Windows\
├─ Temporary Internet Files     → INetCache 로 가는 연결 폴더
├─ INetCache\
│  ├─ Content.IE5               → INetCache\IE 로 가는 연결 폴더 (숨김·시스템)
│  ├─ Content.MSO
│  ├─ Content.Word
│  ├─ IE\                       container.dat (0바이트)만 있음
│  ├─ Low
│  ├─ Virtualized
│  └─ WebTempDir
└─ INetCookies\
   ├─ DNTException
   ├─ ESE\                      container.dat (0바이트)만 있음
   ├─ Low\ESE
   ├─ PrivacIE
   ├─ container.dat             (0바이트)
   └─ deprecated.cookie         (91바이트)
```

`Temporary Internet Files` 는 `INetCache` 를 가리키는 연결 폴더 (Junction) 였고, `INetCache\Content.IE5` 는 `INetCache\IE` 를 가리키는 연결 폴더였으며 숨김·시스템 속성이 붙어 있었습니다. `INetCache\IE` 에는 8글자 캐시 하위 폴더가 없었고, `%APPDATA%\Microsoft\Windows\Cookies` 폴더도 없었습니다. 같은 PC 의 WebCacheV01.dat 사본에서는 `CookieEntryEx_#` 표 이름이 여럿 나왔습니다.

## 구조

### IE 4~9: 캐시 폴더 표로 잇기

`index.dat` 머리글의 오프셋 72부터 캐시 폴더 표가 있습니다. 표는 4바이트 개수 뒤에 12바이트 항목이 이어지는 모양입니다. 머리글의 나머지 칸은 [옛 기록 파일 (index.dat)](index-dat.md) 에서 다룹니다.

| 오프셋 | 크기 | 내용 |
|---|---|---|
| 72 (0x48) | 4 | 캐시 폴더 개수 |
| 76 (0x4C) | 4 | 0번 폴더의 파일 수 |
| 80 (0x50) | 8 | 0번 폴더 이름. 끝에 0 이 없습니다 |
| 88 (0x58) | 4 | 1번 폴더의 파일 수 |
| 92 (0x5C) | 8 | 1번 폴더 이름 |
| … | | 폴더마다 12바이트씩 이어집니다 |

URL 레코드는 두 칸으로 캐시 파일을 가리킵니다.

- **캐시 폴더 번호** — 위 표에서 몇 번째 폴더인지 가리킵니다. 0 이 첫 폴더입니다. 4.7 판은 레코드 오프셋 60, 5.2 판은 오프셋 56 에 있습니다. 5.2 판에서 0xfe·0xff 는 특수값입니다.
- **파일 이름 위치** — 레코드 안에서 캐시 파일 이름을 찾는 칸입니다. 4.7 판은 오프셋 64~67 에 있습니다.

캐시 파일의 경로는 이렇게 조립합니다.

```
<캐시 폴더>\<폴더 표에서 찾은 8글자 이름>\<레코드의 파일 이름>
```

### IE 10 이후: WebCache 의 칸으로 잇기

- WebCache DB 의 `Container_#` 표에는 캐시 파일과 관련된 칸이 있습니다. Filename, FileExtension, FileSize, CacheId, ResponseHeaders, RequestHeaders 입니다.
- `Containers` 표에도 Directory 칸이 있습니다. 이 칸과 실제 캐시 폴더의 관계는 이번에 연 자료로 확인하지 못했습니다. Filename 칸 값으로 실제 폴더를 검색해 맞춰 봅니다.
- 쿠키는 `CookieEntryEx_#` 표의 Name, Value, RDomain, Expires, LastModified 같은 칸에 들어갑니다.
- 표와 칸 전체는 [웹캐시 DB (WebCacheV01.dat)](webcachev01-dat.md) 에서 다룹니다.

## 증거로서 의미

### 증명하는 것

- 캐시 폴더에 파일이 있으면, 그 내용이 이 사용자 프로필의 캐시에 저장된 적이 있습니다.
- 기록 파일과 이어지면 그 파일을 어느 주소에서 받았는지 알 수 있습니다.
- 캐시 파일을 열면 그때 받은 페이지나 이미지의 내용을 볼 수 있습니다.

### 증명하지 못하는 것

- 캐시 파일이 있다고 사용자가 그 내용을 화면에서 봤다고 단정하지 않습니다.
- 기록과 이어지지 않은 캐시 파일은 어느 주소에서 왔는지 말하지 못합니다.
- 캐시 폴더가 비어 있다고 IE 를 쓰지 않았다고 단정하지 않습니다. IE 10 이후 쿠키는 폴더가 아니라 DB 에 있고, 캐시는 지우거나 비울 수 있습니다.
- `INetCache` 아래 모든 폴더가 IE 흔적은 아닙니다. `Content.MSO`·`Content.Word` 를 어떤 프로그램이 쓰는지는 이번에 연 자료로 확인하지 못했습니다.

보고서에는 "이 사용자 프로필의 캐시 폴더에 이 파일이 있고, WebCacheV01.dat 의 이 행이 이 주소와 이 파일을 잇는다" 처럼 파일과 기록을 함께 씁니다.

## 시각 해석

- 주소와 캐시 파일의 시각 칸은 기록 파일에 있습니다. [웹캐시 DB](webcachev01-dat.md) 와 [index.dat](index-dat.md) 의 시각 해석을 따릅니다.
- 캐시 파일 자체의 파일 시스템 시각은 [$MFT](../../filesystem/mft.md) 에서 봅니다.
- 두 시각이 크게 어긋나면 파일을 옮기거나 복사한 흔적인지 확인합니다. 파일 생성과 삭제 순서는 [$UsnJrnl](../../filesystem/usnjrnl.md) 로 확인합니다.

## 함정과 한계

- **연결 폴더를 따라가면 같은 파일을 두 번 셉니다.** `Temporary Internet Files` 와 `INetCache`, `Content.IE5` 와 `IE` 는 같은 곳을 가리킬 수 있습니다. 수집 도구가 연결 폴더를 따라가는지 확인합니다.
- **숨김·시스템 폴더를 놓치기 쉽습니다.** 탐색기 기본 설정으로는 `Content.IE5` 같은 폴더가 보이지 않을 수 있습니다. 연결 폴더는 재분석 지점 (Reparse Point) 이므로 [NTFS 구조](../../../01-foundations/disk-volume/ntfs/index.md) 의 속성으로 확인합니다.
- **`Low` 폴더를 빠뜨리기 쉽습니다.** `INetCache` 와 `INetCookies` 아래에 `Low` 폴더가 따로 있습니다.
- **폴더 이름만 보고 IE 버전을 정하지 않습니다.** `Content.IE5` 라는 이름은 IE 10 이후 PC 에도 연결 폴더로 남아 있었습니다. 기록 형식은 기록 파일에서 확인합니다.
- **폴더만 보고 쿠키를 찾으면 빠집니다.** IE 10 이후 쿠키는 WebCache DB 에 있습니다.
- **지운 캐시 파일이 남을 수 있습니다.** 캐시를 비워도 파일 내용이 할당 해제 영역에 남을 수 있습니다. 찾는 방법은 [삭제 데이터 복구](../../../03-techniques/analysis/data-recovery/index.md) 에서 다룹니다.

## 직접 분석해 보기

### 헥스로 한 번

아래 바이트는 명세로 만든 예시입니다. 폴더 이름 `ABCD1234` 는 지어낸 이름입니다.

```
오프셋 0x48  [4바이트]                  캐시 폴더 개수
오프셋 0x4C  [4바이트]                  0번 폴더의 파일 수
오프셋 0x50  41 42 43 44 31 32 33 34    "ABCD1234"  0번 폴더 이름
오프셋 0x58  [4바이트]                  1번 폴더의 파일 수
오프셋 0x5C  [8바이트]                  1번 폴더 이름
```

1. 캐시 폴더의 `index.dat` 사본을 헥스 편집기로 엽니다.
2. 오프셋 0x48 에서 폴더 개수를 읽습니다.
3. 0x50 부터 8바이트를 읽고, 12바이트씩 건너뛰며 폴더 이름을 모두 적습니다.
4. `URL ` 레코드 하나를 찾아 캐시 폴더 번호를 읽습니다. 5.2 판이면 레코드 오프셋 56 입니다.
5. 번호가 0 이면 0번 폴더(`ABCD1234`)입니다. 레코드의 파일 이름과 합쳐 경로를 만듭니다.
6. 그 경로에 파일이 실제로 있는지 봅니다.

### 공개 도구로 한 번

1. 사용자 프로필의 `INetCache`·`INetCookies`·WebCache 폴더를 사본으로 뜹니다. 연결 폴더는 따라가지 않고 원래 폴더만 가져옵니다.
2. IE 9 이전이면 libmsiecf 같은 공개 라이브러리로 캐시 `index.dat` 를 열어 주소·폴더 번호·파일 이름 목록을 뽑습니다.
3. IE 10 이후면 plaso 의 WebCache 파서 같은 공개 도구로 `Container_#` 행을 뽑습니다.
4. 뽑은 파일 이름 목록과 실제 폴더의 파일 목록을 맞춰 봅니다. 기록은 있는데 파일이 없는 항목과, 파일은 있는데 기록이 없는 항목을 따로 적습니다.

## 교차 검증

| 아티팩트 | 알려 주는 것 | 링크 |
|---|---|---|
| 웹캐시 DB | IE 10 이후 캐시 파일과 주소, 쿠키 행을 봅니다 | [웹캐시 DB (WebCacheV01.dat)](webcachev01-dat.md) |
| 옛 기록 파일 | IE 9 이전 캐시 레코드와 폴더 표를 봅니다 | [옛 기록 파일 (index.dat)](index-dat.md) |
| $MFT·$UsnJrnl | 캐시 파일을 만들고 지운 시각을 봅니다 | [$MFT](../../filesystem/mft.md), [$UsnJrnl](../../filesystem/usnjrnl.md) |
| 다운로드 출처 표시 | 캐시를 거쳐 저장한 파일에 출처 표시가 남았는지 봅니다 | [다운로드 출처 표시](../../filesystem/zone-identifier.md) |
| 섀도 복사본 | 캐시를 비우기 전의 파일을 찾습니다 | [섀도 복사본 활용](../../../03-techniques/analysis/volume-shadow-copy-analysis.md) |
| 다른 브라우저 | 같은 사이트의 캐시·쿠키가 다른 브라우저에도 있는지 봅니다 | [크롬 계열 브라우저](../chrome-edge-whale/index.md), [파이어폭스](../firefox/index.md) |

파일이 어디서 왔는지 따지는 흐름은 [이 파일은 어디서 왔나](../../../04-scenarios/activity/file-origin.md) 에 있습니다.

## 실습

IE 를 쓴 공개 검체(NIST CFReDS 등)에서 사용자 프로필 폴더를 꺼내 아래 질문을 풀어 봅니다.

1. 캐시 폴더는 `Content.IE5` 입니까, `INetCache\IE` 입니까? 연결 폴더가 있습니까?
2. IE 9 이전 검체라면 캐시 `index.dat` 의 폴더 표에 폴더가 몇 개 있습니까? 실제 하위 폴더 수와 같습니까?
3. 폴더 표의 파일 수와 실제 하위 폴더의 파일 수가 맞습니까?
4. 기록에는 있는데 폴더에 없는 캐시 파일이 몇 개입니까? 그 파일은 할당 해제 영역에서 찾을 수 있습니까?
5. IE 10 이후 검체라면 `CookieEntryEx_#` 표에 쿠키가 몇 개 있습니까? `INetCookies` 폴더에는 무엇이 남아 있습니까?

## 참고 문헌

1. ForensicArtifacts, *artifacts/data/webbrowser.yaml* (IE 버전별 캐시·쿠키 경로). https://raw.githubusercontent.com/ForensicArtifacts/artifacts/main/artifacts/data/webbrowser.yaml
2. libyal/libmsiecf, *MSIE Cache File (index.dat) format* (캐시 폴더 표, URL 레코드의 폴더 번호와 파일 이름 칸). https://raw.githubusercontent.com/libyal/libmsiecf/main/documentation/MSIE%20Cache%20File%20(index.dat)%20format.asciidoc
3. log2timeline/plaso, *plaso/parsers/esedb_plugins/msie_webcache.py* (WebCache 의 캐시·쿠키 칸). https://raw.githubusercontent.com/log2timeline/plaso/main/plaso/parsers/esedb_plugins/msie_webcache.py
4. Forensafe 블로그, 옛 엣지(EdgeHTML) 아티팩트 설명 글 (옛 엣지 쿠키 폴더와 WebCacheV01.dat). https://www.forensafe.com/blogs/microsoftedge.html
