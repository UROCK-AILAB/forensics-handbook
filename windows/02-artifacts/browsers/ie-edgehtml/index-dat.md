---
title: "옛 기록 파일"
parent: "인터넷 익스플로러·옛 엣지"
grand_parent: "아티팩트 · 인터넷·브라우저"
nav_order: 1810
---

# 옛 기록 파일 (index.dat)

## 한 줄 요약

IE 4~9 는 방문 기록·캐시·쿠키·내려받기 기록을 같은 형식의 `index.dat` 파일에 용도별로 나눠 둡니다. 파일 머리글 뒤에 128바이트 블록 단위로 `URL `·`LEAK` 같은 레코드가 쌓이고, 레코드마다 시각 칸이 두 개 있습니다. 두 시각의 뜻은 파일 종류마다 다릅니다.

## 무엇을 기록하나 · 왜 생기나

이 형식의 이름은 MSIE 캐시 파일 (MSIE Cache File, MSIECF) 이고, 방문 기록·캐시·쿠키·내려받기 기록에 모두 쓰입니다. 기록 종류마다 폴더가 다르고 폴더마다 `index.dat` 가 하나씩 있으며, 파일 머리글의 서명 문자열에 판 번호가 들어갑니다.

| 판 번호 | 쓰는 IE |
|---|---|
| 4.7 | IE 4 |
| 5.2 | IE 5~9 |

- IE 3 은 `mm256.dat`, `mm1024.dat` 라는 다른 파일을 썼습니다.
- IE 10 부터는 이 기록을 ESE DB 하나에 둡니다. 새 형식은 [웹캐시 DB (WebCacheV01.dat)](webcachev01-dat.md) 에서 다룹니다.

## 위치와 버전별 차이

### Windows XP SP1~SP3, Windows 2003 (IE 6~8)

```
%USERPROFILE%\Local Settings\Temporary Internet Files\Content.IE5\index.dat
%USERPROFILE%\Local Settings\History\History.IE5\index.dat
%USERPROFILE%\Local Settings\History\History.IE5\MSHist01yyyymmddyyyymmdd\index.dat
%USERPROFILE%\Cookies\index.dat
%USERPROFILE%\UserData\index.dat
```

### Windows Vista·7 (IE 7~9)

```
%USERPROFILE%\AppData\Local\Microsoft\Windows\Temporary Internet Files\Content.IE5\index.dat
%USERPROFILE%\AppData\Local\Microsoft\Windows\Temporary Internet Files\Low\Content.IE5\index.dat
%USERPROFILE%\AppData\Local\Microsoft\Windows\History\History.IE5\index.dat
%USERPROFILE%\AppData\Local\Microsoft\Windows\History\History.IE5\MSHist01yyyymmddyyyymmdd\index.dat
%USERPROFILE%\AppData\Roaming\Microsoft\Windows\Cookies\index.dat
%USERPROFILE%\AppData\Roaming\Microsoft\Windows\IEDownloadHistory\index.dat
```

| 폴더 | 기록 종류 |
|---|---|
| `Content.IE5` | 캐시 (임시 인터넷 파일) |
| `History.IE5` | 방문 기록 |
| `History.IE5\MSHist01…` | 기간별 방문 기록 |
| `Cookies` | 쿠키 |
| `IEDownloadHistory` | 내려받기 기록 |

- `MSHist01` 뒤의 `yyyymmddyyyymmdd` 는 시작일과 끝일입니다. 폴더 이름에 이 기록이 덮는 기간이 적혀 있습니다.
- Vista·7 에는 `Temporary Internet Files\Low\Content.IE5` 아래에도 따로 `index.dat` 가 있습니다. 두 곳을 모두 수집합니다.
- 캐시 폴더 안의 파일과 기록을 잇는 방법은 [쿠키·캐시 폴더 (INetCookies·INetCache)](inetcookies-inetcache.md) 에서 다룹니다.

### 요즘 Windows 에 남은 폴더

Windows 11 25H2 기준입니다.

- `History\History.IE5` 폴더에 `index.dat` 는 없고, 크기가 0바이트인 `container.dat` 만 있습니다.
- `History.IE5` 아래에 `MSHist012026072920260730` 같은 폴더가 있고, 그 안에도 0바이트 `container.dat` 만 있습니다.
- IE 10 이후에도 `MSHist01` 폴더 이름 규칙은 남아 있고, WebCache DB 에도 이름이 `MSHist` 로 시작하는 컨테이너가 있습니다.

폴더가 있어도 `index.dat` 가 있다고 볼 수는 없습니다. 요즘 Windows 에서는 폴더 이름의 기간을 참고하되, 기록 자체는 WebCache DB 에서 읽습니다.

## 구조

표의 오프셋은 파일이나 레코드의 첫 바이트에서 센 바이트 수입니다. 0x 를 붙이지 않은 숫자는 10진수입니다.

### 파일 머리글

| 오프셋 | 크기 | 내용 |
|---|---|---|
| 0~27 | 28 | 서명 `Client UrlCache MMF Ver #.#` 과 끝의 0x00. `#.#` 은 판 번호입니다 |
| 28~31 | 4 | 파일 크기 |
| 32~35 | 4 | 해시 표 첫 부분의 위치. 없으면 0 입니다. 128 의 배수이고 0x4000 이상입니다 |
| 36~39 | 4 | 전체 블록 수 |
| 40~43 | 4 | 할당된 블록 수 |
| 48~51 | 4 | 캐시 크기 한도 |
| 56~59 | 4 | 현재 캐시 크기 |
| 64~67 | 4 | 지울 수 없는 캐시 크기 |
| 72~ | 가변 | 캐시 폴더 표 ([쿠키·캐시 폴더](inetcookies-inetcache.md) 참고) |

### 블록과 할당 비트맵

- 블록 크기는 128바이트(0x80)입니다.
- 할당 비트맵 (Allocation Bitmap) 은 오프셋 0x250(592)부터 0x4000 앞까지입니다.
- 비트 하나가 0x4000 부터 시작하는 128바이트 블록 하나를 가리킵니다.
- 레코드는 블록 단위로 자리를 잡습니다.

### 레코드 종류

| 서명 | 뜻 | 크기 |
|---|---|---|
| `URL ` | 캐시 항목 | 128바이트 블록 단위로 달라집니다 |
| `HASH` | 해시 표 (Hash Table) | 4096바이트(128바이트 × 32) 고정 |
| `REDR` | 리디렉션 항목 | — |
| `LEAK` | 캐시의 유효 항목은 아니지만 지워지지 않은 URL 레코드 | — |

해시 표 칸에는 특수값이 있습니다.

- 해시 값 `0x0badf00d`, `0xdeadbeef` 는 초기화하지 않은 칸입니다.
- 해시 값 끝이 `0x01` 이면 잘못된 URL 레코드를 가리킵니다. 그래도 일부 오프셋은 맞을 수 있습니다.

### URL 레코드 — 4.7 판 (IE 4)

| 오프셋 | 크기 | 내용 |
|---|---|---|
| 0~3 | 4 | 서명 `URL ` |
| 4~7 | 4 | 블록 수 |
| 8~15 | 8 | 두 번째 시각 (FILETIME) |
| 16~23 | 8 | 첫 번째 시각 (FILETIME) |
| 24~31 | 8 | 만료 시각 (FILETIME) |
| 32~35 | 4 | 파일 크기 |
| 56~59 | 4 | 주소 (location) 위치. 보통 104 입니다 |
| 60 | — | 캐시 폴더 번호. 0 은 첫 폴더입니다 |
| 64~67 | 4 | 파일 이름 위치 |
| 68~71 | 4 | 플래그 |
| 72~75 | 4 | 데이터 위치 |
| 76~79 | 4 | 데이터 크기 |
| 84~87 | 4 | 마지막 확인 시각 (FAT 날짜·시각) |
| 88~91 | 4 | 접근 횟수 |

### URL 레코드 — 5.2 판 (IE 5~9) 에서 달라진 칸

| 오프셋 | 크기 | 내용 |
|---|---|---|
| 24~27 | 4 | 만료 시각. FILETIME 이 아니라 FAT 날짜·시각입니다 |
| 40~43 | 4 | 그룹 위치 |
| 44~47 | 4 | 지울 수 없는 기간 (초) |
| 52~55 | 4 | 주소 위치. 기본값은 0x68 입니다 |
| 56 | — | 캐시 폴더 번호. 0xfe·0xff 는 특수값입니다 |

5.2 판에서 마지막 확인 시각과 접근 횟수의 오프셋은 공개 자료에 나와 있지 않습니다.

## 증거로서 의미

### 증명하는 것

- 그 사용자 프로필의 기록 파일에 이 주소의 레코드가 있었습니다.
- 파일이 있는 폴더로 기록 종류(방문 기록·캐시·쿠키·내려받기)를 알 수 있습니다.
- `MSHist01` 폴더 이름으로 그 파일이 덮는 기간을 알 수 있습니다.
- `LEAK` 레코드는 더는 유효하지 않지만 지워지지 않은 항목입니다. 예전에 있던 항목의 흔적이 됩니다.

### 증명하지 못하는 것

- 캐시 레코드 하나만으로 사용자가 그 주소를 직접 열었는지 가르지 못합니다.
- 방문 기록 레코드는 방문 사실을 적을 뿐, 사용자가 그 페이지를 읽었는지는 말하지 않습니다.
- 레코드가 없다고 방문하지 않았다고 단정하지 않습니다. 기록은 지울 수 있습니다.

보고서에는 "이 사용자 프로필의 주간 방문 기록 index.dat 에 이 주소의 레코드가 있고, 마지막 방문 시각은 현지 시각으로 이렇다" 처럼 파일 종류와 시각 기준을 함께 씁니다.

## 시각 해석

URL 레코드의 두 시각은 파일 종류마다 뜻이 다릅니다.

| 파일 종류 | 첫 번째 시각 | 두 번째 시각 |
|---|---|---|
| 임시 인터넷 파일 (캐시) | 이 PC 가 마지막으로 접근한 시각 (UTC) | 서버의 수정 시각 (UTC) |
| 방문 기록 (전체) | 마지막 방문 (UTC) | 마지막 방문 (UTC) |
| 방문 기록 (주간) | 이 index.dat 를 만든 날 (UTC) | 마지막 방문 (현지 시각) |
| 방문 기록 (일간) | 마지막 방문 (UTC) | 마지막 방문 (현지 시각) |
| 쿠키 | 마지막 접근 (UTC) | 수정 시각 (UTC) |
| 내려받기 기록 | 내려받은 파일을 만든 시각 (UTC) | 비어 있음 |

- 첫 번째 시각은 오프셋 16~23, 두 번째 시각은 오프셋 8~15 입니다. 순서가 뒤집혀 있으니 주의합니다.
- 일간·주간 방문 기록의 두 번째 시각은 현지 시각입니다. UTC 로 바꾸려면 [시간대 설정](../../system-account/time-zone.md) 을 확인합니다.
- 주간 기록의 첫 번째 시각은 방문 시각이 아닙니다. 그 index.dat 를 만든 날입니다.
- 만료 시각은 4.7 판에서 FILETIME 이고, 5.2 판에서 FAT 날짜·시각입니다.
- FILETIME 과 FAT 날짜·시각을 바꾸는 방법은 [시각 값 형식](../../../01-foundations/value-decoding/filetime-unix-webkit-dos-ole.md) 에서 다룹니다.

## 함정과 한계

- **판마다 오프셋이 다릅니다.** 주소 위치 칸은 4.7 판에서 56~59, 5.2 판에서 52~55 입니다. 머리글의 판 번호를 먼저 읽습니다.
- **일간·주간 기록을 섞어 해석하면 틀립니다.** 파일이 일간 기록인지 주간 기록인지 먼저 정한 뒤 시각을 읽습니다. 여러 레코드의 첫 번째 시각이 모두 같은 날이면 주간 기록을 의심합니다. 주간 기록의 첫 번째 시각은 파일을 만든 날이기 때문입니다.
- **해시 표 특수값을 레코드 위치로 읽지 않습니다.** `0x0badf00d`·`0xdeadbeef` 는 빈 칸입니다.
- **폴더만 남은 경우가 있습니다.** 요즘 Windows 에서는 `History.IE5` 아래 폴더에 0바이트 `container.dat` 만 있을 수 있습니다.
- **`Low` 폴더를 빠뜨리기 쉽습니다.** Vista·7 에서는 `Low\Content.IE5` 에도 따로 기록 파일이 있습니다.
- **지운 레코드가 남을 수 있습니다.** `LEAK` 레코드와 비트맵에서 비어 있다고 표시된 블록에 옛 레코드가 남을 수 있습니다. 비어 있는 블록을 서명으로 훑는 방법은 [삭제 데이터 복구](../../../03-techniques/analysis/data-recovery/index.md) 에서 다룹니다.

## 직접 분석해 보기

### 헥스로 한 번

아래 바이트는 명세로 만든 예시입니다. 특정 검체에서 꺼낸 값이 아닙니다.

**파일 머리글 서명.** 5.2 판 파일의 첫 28바이트는 이렇게 생겼습니다.

```
오프셋 0x00  43 6C 69 65 6E 74 20 55 72 6C 43 61 63 68 65 20   Client UrlCache 
오프셋 0x10  4D 4D 46 20 56 65 72 20 35 2E 32 00               MMF Ver 5.2.
```

4.7 판이면 `35 2E 32` 자리가 `34 2E 37` 입니다.

**레코드 서명.** 블록 머리에서 아래 4바이트를 찾으면 레코드 종류를 알 수 있습니다.

```
55 52 4C 20   "URL "
48 41 53 48   "HASH"
52 45 44 52   "REDR"
4C 45 41 4B   "LEAK"
```

**비트맵에서 블록 찾기.** 오프셋 0x5000 에 레코드가 있다고 합시다.

```
(0x5000 − 0x4000) ÷ 0x80 = 0x20   → 0부터 센 블록 번호 32
32 ÷ 8 = 4                        → 비트맵 첫 바이트에서 4바이트 뒤
0x250 + 4 = 0x254                 → 이 블록의 비트가 들어 있는 바이트
```

비트맵에서 비어 있다고 표시된 블록에 `URL ` 서명이 있으면, 할당이 풀린 뒤 남은 옛 레코드일 수 있습니다.

### 공개 도구로 한 번

1. 기록 파일은 폴더째 사본을 뜹니다. 폴더 이름(`MSHist01…`)이 기간 정보이므로 경로를 함께 보존합니다.
2. libmsiecf 같은 공개 라이브러리로 파일을 열어 레코드 목록을 뽑습니다.
3. 도구가 보여 주는 두 시각이 위 표의 어느 뜻인지, 파일 종류에 맞춰 다시 붙입니다.
4. 도구 결과에서 한두 레코드를 골라 헥스로 오프셋을 따라가 봅니다. 시각 두 개의 순서가 맞는지 확인합니다.

## 교차 검증

| 아티팩트 | 알려 주는 것 | 링크 |
|---|---|---|
| 웹캐시 DB | 같은 PC 가 IE 10 이후로 바뀐 뒤의 기록을 봅니다 | [웹캐시 DB (WebCacheV01.dat)](webcachev01-dat.md) |
| 쿠키·캐시 폴더 | URL 레코드가 가리키는 캐시 파일이 실제로 있는지 봅니다 | [쿠키·캐시 폴더](inetcookies-inetcache.md) |
| 주소창 입력 주소 | 방문 기록의 주소를 직접 입력했는지 봅니다 | [주소창 입력 주소](typedurls-typedurlstime.md) |
| 저장 비밀번호 | 방문 기록에 남은 주소로 저장 비밀번호 값을 풉니다 | [저장 비밀번호 (IntelliForms)](intelliforms.md) |
| 시간대 설정 | 현지 시각으로 적힌 두 번째 시각을 UTC 로 바꿉니다 | [시간대 설정](../../system-account/time-zone.md) |
| $MFT | index.dat 와 `MSHist01…` 폴더를 만든 시각을 봅니다 | [$MFT](../../filesystem/mft.md) |
| 섀도 복사본 | 이전 시점의 index.dat 에서 지금은 없는 레코드를 찾습니다 | [섀도 복사본 활용](../../../03-techniques/analysis/volume-shadow-copy-analysis.md) |

웹 사용 전체를 재구성하는 흐름은 [웹 사용 행위 재구성](../../../04-scenarios/activity/web-activity.md) 에 있습니다.

## 실습

Windows XP 나 Windows 7 에서 IE 를 쓴 공개 검체(NIST CFReDS 등)에서 사용자 프로필 폴더를 꺼내 아래 질문을 풀어 봅니다.

1. 프로필 안에 `index.dat` 가 몇 개 있습니까? 폴더별로 어떤 기록 종류입니까?
2. 머리글 서명의 판 번호는 몇입니까?
3. `MSHist01…` 폴더 이름의 기간을 모두 적어 봅니다. 하루짜리와 여러 날짜짜리가 섞여 있습니까?
4. 주간 기록 파일에서 한 레코드를 골라 두 시각을 읽습니다. 첫 번째 시각이 파일을 만든 날과 맞습니까?
5. 같은 주소가 방문 기록과 캐시에 모두 있습니까? 두 파일의 시각은 몇 초 차이 납니까?
6. `LEAK` 레코드가 있습니까? 그 주소는 지금 방문 기록에도 남아 있습니까?

## 참고 문헌

1. ForensicArtifacts, *artifacts/data/webbrowser.yaml* (index.dat 위치 목록). https://raw.githubusercontent.com/ForensicArtifacts/artifacts/main/artifacts/data/webbrowser.yaml
2. Forensics Wiki, *Internet Explorer* (IE 4~9 가 index.dat 를 쓰는 점). https://forensics.wiki/internet_explorer
3. libyal/libmsiecf, *MSIE Cache File (index.dat) format* (판 번호, 위치, 머리글, 레코드 구조, 시각의 뜻). https://raw.githubusercontent.com/libyal/libmsiecf/main/documentation/MSIE%20Cache%20File%20(index.dat)%20format.asciidoc
4. log2timeline/plaso, *plaso/parsers/esedb_plugins/msie_webcache.py* (WebCache 의 `MSHist` 컨테이너). https://raw.githubusercontent.com/log2timeline/plaso/main/plaso/parsers/esedb_plugins/msie_webcache.py
