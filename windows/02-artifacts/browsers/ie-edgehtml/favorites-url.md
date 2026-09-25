---
title: "즐겨찾기 (Favorites .url)"
parent: "인터넷 익스플로러·옛 엣지"
grand_parent: "아티팩트 · 인터넷·브라우저"
nav_order: 1850
---

# 즐겨찾기 (Favorites .url)

## 한 줄 요약

IE 는 즐겨찾기를 사용자 즐겨찾기 폴더 (Favorites) 안의 `.url` 파일로 둡니다. `.url` 은 INI 형식의 글자 파일이고, `URL=` 줄에 즐겨찾기가 가리키는 주소가 있습니다. 한 PC 에서 본 `.url` 에는 시각을 적은 줄이 없었습니다. 그래서 시각은 파일 시스템에서 읽습니다. 옛 엣지 (EdgeHTML) 의 새 버전은 즐겨찾기를 ESE 데이터베이스인 `spartan.edb` 에 둡니다.

## 무엇을 기록하나 · 왜 생기나

즐겨찾기는 사용자가 다시 찾아가려고 저장해 둔 웹 주소입니다. IE 의 즐겨찾기 하나는 즐겨찾기 폴더 안의 `.url` 파일 하나이고, 이 파일은 인터넷 바로가기 (Internet Shortcut) 로서 안의 `[InternetShortcut]` 절에 주소가 있습니다. 즐겨찾기를 추가하면 폴더에 파일이 생기고 지우면 파일이 없어지므로, 즐겨찾기는 파일 시스템 기록과 함께 읽습니다.

Forensafe 글은 옛 엣지의 새 버전이 즐겨찾기를 `spartan.edb` 에 둔다고 적었습니다.

이 페이지는 즐겨찾기 파일과 그 위치만 다룹니다. 즐겨찾기 주소에 실제로 방문했는지는 [웹캐시 DB (WebCacheV01.dat)](webcachev01-dat.md) 와 [옛 기록 파일 (index.dat)](index-dat.md) 에서 봅니다.

## 위치와 버전별 차이

### IE 즐겨찾기 폴더

Windows 11 25H2 PC 에서 본 모습입니다.

| 항목 | 이 PC 에서 본 것 |
|---|---|
| 폴더 | `%USERPROFILE%\Favorites` |
| 폴더 위치를 적은 값 | `HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\User Shell Folders` 의 `Favorites` 값 (REG_EXPAND_SZ), 값은 `%USERPROFILE%\Favorites` |
| 폴더 안 | `Links` 하위 폴더, `desktop.ini`, `.url` 파일 |
| 함께 있던 키 | `HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\MenuOrder\Favorites` |

- `User Shell Folders` 값은 사용자 하이브 (NTUSER.DAT) 에 있습니다. 검체에서는 그 사용자의 NTUSER.DAT 에서 읽습니다. 하이브 구조는 [레지스트리 하이브 구조](../../../01-foundations/database-log-formats/registry-hive/index.md) 에서 다룹니다.
- 기본 위치에 폴더가 없으면 이 값을 먼저 확인합니다.
- 다른 Windows 버전의 기본 위치는 이번에 연 자료로 확인하지 못했습니다.
- `desktop.ini` 는 폴더 표시 설정 파일입니다. 즐겨찾기가 아닙니다.
- `MenuOrder\Favorites` 키 값의 형식과 뜻은 이번에 연 자료로 확인하지 못했습니다. 이 키로 즐겨찾기 순서나 시각을 해석하지 않습니다.

### 옛 엣지 즐겨찾기

| 항목 | 내용 | 출처 |
|---|---|---|
| 저장 형식 | 새 버전은 `spartan.edb` (ESE 데이터베이스), 옛 버전은 `Favorites` 폴더 안의 `.url` 파일 | Forensafe |
| 즐겨찾기 폴더 | `C:\Users\<사용자>\AppData\Local\Packages\<패키지 이름>\AC\MicrosoftEdge\User\<프로필 이름>\Favorites` | Forensafe |
| 같은 곳의 다른 폴더 | `…\User\<프로필 이름>\Recovery`, `…\User\<프로필 이름>\Datastore` | Forensafe |
| 수집 범위 예 | 공개 수집 정의 `Edge.tkape` 는 `…\AppData\Local\Packages\Microsoft.MicrosoftEdge_8wekyb3d8bbwe\` 아래를 모두 모읍니다 | KapeFiles |

- `spartan.edb` 의 정확한 전체 경로와 표 이름·칸 이름은 이번에 연 자료로 확인하지 못했습니다.
- 어느 버전부터 `spartan.edb` 를 썼는지는 확인하지 못했습니다. 출처 글도 "새 버전"·"옛 버전"으로만 나눕니다.
- 그래서 경로 하나만 찾지 않고 패키지 폴더를 통째로 모읍니다.
- `spartan.edb` 의 저장 형식은 [ESE 데이터베이스](../../../01-foundations/database-log-formats/extensible-storage-engine/index.md) 에서, 패키지 폴더의 짜임은 [UWP 앱 데이터 구조](../../../01-foundations/app-mail-data/packages-settings-dat.md) 에서 다룹니다.
- Windows 11 25H2 PC 에는 옛 엣지 패키지 폴더가 없었습니다.
- 옛 엣지의 지원 종료 시점은 [인터넷 익스플로러·옛 엣지 (IE·EdgeHTML)](index.md) 에서 다룹니다.

## 구조

### .url 파일

아래는 Windows 11 25H2 PC 의 즐겨찾기 폴더에서 본 `Bing.url` (208바이트) 의 내용입니다.

```
[{000214A0-0000-0000-C000-000000000046}]
Prop3=19,2
[InternetShortcut]
IDList=
URL=http://go.microsoft.com/fwlink/p/?LinkId=255142
IconIndex=0
IconFile=%ProgramFiles%\Internet Explorer\Images\bing.ico
```

바이너리가 아니라 INI 형식의 글자 파일이며, `[InternetShortcut]` 이 아니라 `[{` (0x5B 0x7B) 로 시작했습니다. 위 일곱 줄의 글자 수를 모두 더하면 194이고, 줄마다 줄 끝 두 바이트 (CR LF) 를 더하면 208로 파일 크기와 같습니다. 그래서 이 파일은 한 글자를 한 바이트로 적고 줄 끝에 CR LF 를 붙인 것으로 보입니다.

| 줄 | 이 파일의 값 | 읽는 법 |
|---|---|---|
| `[{000214A0-0000-0000-C000-000000000046}]` | 절 이름 | 이 절의 뜻은 이번에 연 자료로 확인하지 못했습니다 |
| `Prop3=` | `19,2` | 뜻을 확인하지 못했습니다 |
| `[InternetShortcut]` | 절 이름 | 아래 줄들이 이 절에 듭니다 |
| `IDList=` | 비어 있음 | 이 파일에서는 값이 없었습니다 |
| `URL=` | `http://go.microsoft.com/fwlink/p/?LinkId=255142` | 즐겨찾기가 가리키는 주소입니다 |
| `IconIndex=` | `0` | 아이콘에 관한 값입니다 |
| `IconFile=` | `%ProgramFiles%\Internet Explorer\Images\bing.ico` | 아이콘 파일 경로입니다 |

- 이 파일에는 시각을 적은 줄이 없었습니다.
- 다른 `.url` 파일에 `Modified=` 같은 시각 줄이 들어가는지는 이번에 연 자료로 확인하지 못했습니다. 이런 줄이 보이면 뜻을 따로 확인한 뒤에 씁니다.
- `.url` 은 `.lnk` 바로가기와 형식이 다릅니다. `.lnk` 형식은 [바로가기 형식](../../../01-foundations/shell-document-formats/shell-link-lnk.md) 에서 다룹니다.

## 증거로서 의미

### 증명하는 것

- 이 사용자 프로필의 즐겨찾기 폴더에 이 주소를 가리키는 `.url` 파일이 있었습니다.
- 파일 시스템 시각으로 그 파일이 이 볼륨에 생긴 때와 바뀐 때를 볼 수 있습니다.
- 즐겨찾기 폴더는 사용자 프로필 폴더 아래 있습니다. 그래서 어느 Windows 계정의 즐겨찾기인지 알 수 있습니다. 폴더와 계정을 잇는 법은 [사용자 프로필 목록](../../system-account/profilelist.md) 에서 다룹니다.

### 증명하지 못하는 것

- 그 주소에 방문했는지는 알 수 없습니다. 즐겨찾기는 저장해 둔 주소일 뿐입니다.
- 사용자가 직접 추가했는지는 알 수 없습니다. 처음부터 들어 있던 항목이나 다른 곳에서 복사해 온 파일일 수 있습니다.
- `.url` 은 글자 파일입니다. 어느 프로그램으로든, 손으로든 만들고 고칠 수 있습니다. 파일만 보고 IE 가 만들었다고 단정하지 않습니다.
- 그 시각에 누가 키보드 앞에 있었는지는 알 수 없습니다. 사람을 좁히는 법은 [그 시각에 PC 를 쓴 사람이 누구인가](../../../04-scenarios/activity/user-attribution.md) 에서 다룹니다.
- 즐겨찾기가 없다고 추가한 적이 없었던 것은 아닙니다. 지운 파일은 아래 "함정과 한계" 의 자리에서 찾습니다.

보고서에는 "이 계정의 즐겨찾기 폴더에 이 주소를 가리키는 `.url` 파일이 있고, 이 파일의 NTFS 만든 시각은 이 시각이다" 처럼 씁니다. "이 사용자가 이 시각에 즐겨찾기를 추가했다" 로 쓰지 않습니다.

## 시각 해석

- 한 PC 에서 본 `.url` 에는 시각 줄이 없었습니다. 시각은 파일 시스템에서 읽습니다.
- NTFS 는 파일 시각을 UTC 로 적습니다. 현지 시각으로 바꿀 때는 [시간대 설정](../../system-account/time-zone.md) 을 확인합니다.
- 파일 시스템 시각의 종류와 바뀌는 조건은 [마스터 파일 테이블](../../filesystem/mft.md) 에서 다룹니다.
- 만든 시각을 즐겨찾기를 추가한 시각으로 단정하지 않습니다. 다른 곳에서 복사해 온 파일이면 만든 시각은 복사한 때를 가리킬 수 있습니다.
- 파일 내용을 고치면 수정 시각이 바뀝니다. 즐겨찾기 주소를 바꾼 흔적일 수 있습니다.
- 옛 엣지 `spartan.edb` 안에 어떤 시각 칸이 있는지는 이번에 연 자료로 확인하지 못했습니다.

## 함정과 한계

- **처음부터 들어 있던 항목이 섞입니다.** 한 PC 의 `Bing.url` 은 주소가 `go.microsoft.com` 의 안내 링크였고, 아이콘은 Internet Explorer 설치 폴더의 그림이었습니다. 이런 항목을 사용자가 추가했다고 단정하지 않습니다.
- **파일 첫머리만 보면 놓칩니다.** 한 PC 의 `.url` 은 `[InternetShortcut]` 이 아니라 `[{000214A0-…}]` 절로 시작했습니다. 지운 `.url` 을 내용으로 찾을 때는 `[InternetShortcut]` 과 `URL=` 문자열을 파일 어디서든 찾습니다. 검색 방법은 [파일 내용 검색](../../../03-techniques/analysis/content-search/index.md) 에서 다룹니다.
- **지운 즐겨찾기는 파일 시스템에서 찾습니다.** 휴지통, 지운 MFT 레코드, USN 저널, 폴더 인덱스 슬랙을 차례로 봅니다. 크기가 작은 파일은 내용이 MFT 레코드 안에 들어가기도 합니다. 복구 방법은 [삭제 데이터 복구](../../../03-techniques/analysis/data-recovery/index.md) 에서 다룹니다.
- **쉽게 고칠 수 있습니다.** 글자 파일이라 메모장으로도 주소를 바꿀 수 있으므로 수정 시각과 USN 저널 기록을 함께 봅니다. 조작 흔적을 보는 법은 [증거를 없애려 했나](../../../04-scenarios/activity/anti-forensics/index.md) 에서 다룹니다.
- **폴더를 옮겼을 수 있습니다.** 기본 위치만 보지 않고 `User Shell Folders` 의 `Favorites` 값을 확인합니다.
- **옛 엣지는 버전에 따라 저장 방식이 다릅니다.** 옛 버전은 패키지 폴더 안 `Favorites` 에 `.url` 을 두고, 새 버전은 `spartan.edb` 에 둡니다. IE 즐겨찾기 폴더의 `.url` 만 찾으면 옛 엣지 즐겨찾기를 놓칩니다. 패키지 폴더를 따로 모읍니다.
- **`MenuOrder` 키를 해석하지 않습니다.** 형식을 확인하지 못한 키입니다.

## 직접 분석해 보기

### 헥스로 한 번

`.url` 에는 공개 명세가 없어서, 아래 바이트는 위에서 본 `Bing.url` 의 글자를 ASCII 로 옮기고 줄 끝에 CR LF 를 붙여 만든 예시입니다. 검체에서 뜬 헥스가 아닙니다.

```
오프셋  00 01 02 03 04 05 06 07 08 09 0A 0B 0C 0D 0E 0F
0x00    5B 7B 30 30 30 32 31 34 41 30 2D 30 30 30 30 2D   [{000214A0-0000-
0x10    30 30 30 30 2D 43 30 30 30 2D 30 30 30 30 30 30   0000-C000-000000
0x20    30 30 30 30 34 36 7D 5D 0D 0A 50 72 6F 70 33 3D   000046}]..Prop3=
```

1. 첫 두 바이트가 `5B 7B` (`[{`) 인지 봅니다.
2. 글자 사이에 `00` 이 끼어 있지 않습니다. 한 글자가 한 바이트입니다.
3. `0D 0A` 가 줄 끝입니다. 0x28·0x29 의 `0D 0A` 에서 첫 줄이 끝납니다. 0x2A 에서 `Prop3=` 이 시작합니다.
4. `55 52 4C 3D` (`URL=`) 를 찾습니다. 그 뒤부터 `0D 0A` 앞까지가 주소입니다.

```
55 52 4C 3D 68 74 74 70 3A 2F 2F                  URL=http://
```

지운 `.url` 을 디스크에서 찾을 때는 아래 바이트도 검색합니다.

```
5B 49 6E 74 65 72 6E 65 74 53 68 6F 72 74 63 75 74 5D   [InternetShortcut]
```

### 공개 도구로 한 번

1. 사용자 프로필의 `Favorites` 폴더를 하위 폴더까지 통째로 사본으로 뜹니다.
2. 같은 사용자의 NTUSER.DAT 를 레지스트리 뷰어로 열어 `User Shell Folders` 의 `Favorites` 값을 확인합니다.
3. 사본에서 `.url` 파일을 텍스트 편집기로 엽니다. 파일이 많으면 `findstr /s /i "URL=" *.url` 이나 `grep` 같은 검색 도구로 `URL=` 줄을 한꺼번에 뽑습니다.
4. 공개 MFT 파서로 `Favorites` 폴더 아래 파일의 시각을 뽑아 `.url` 목록과 합칩니다.
5. 옛 엣지가 있던 PC 면 패키지 폴더를 통째로 모으고, `spartan.edb` 사본을 ESE 뷰어로 엽니다. 잠긴 ESE 파일의 사본을 뜨는 법은 [웹캐시 DB (WebCacheV01.dat)](webcachev01-dat.md) 에서 다룹니다.

## 교차 검증

| 아티팩트 | 알려 주는 것 | 링크 |
|---|---|---|
| 웹캐시 DB | 즐겨찾기 주소에 실제로 방문한 기록이 있는지 봅니다 | [웹캐시 DB (WebCacheV01.dat)](webcachev01-dat.md) |
| 옛 기록 파일 | IE 9 까지 쓰던 시스템에서 같은 주소의 방문 기록을 봅니다 | [옛 기록 파일 (index.dat)](index-dat.md) |
| 주소창 입력 주소 | 같은 주소를 주소창에 직접 입력했는지 봅니다 | [주소창 입력 주소 (TypedURLs·TypedURLsTime)](typedurls-typedurlstime.md) |
| 마스터 파일 테이블 | `.url` 파일이 생긴 때와 바뀐 때를 봅니다 | [마스터 파일 테이블](../../filesystem/mft.md) |
| USN 변경 저널 | `.url` 을 만들고 지우고 이름을 바꾼 기록을 봅니다 | [USN 변경 저널](../../filesystem/usnjrnl.md) |
| 휴지통 | 지운 `.url` 이 남아 있는지 봅니다 | [휴지통](../../file-folder-usage/recycle-bin.md) |
| 폴더 인덱스와 슬랙 | 즐겨찾기 폴더에서 지운 파일 이름의 흔적을 봅니다 | [폴더 인덱스와 슬랙](../../filesystem/i30.md) |
| 섀도 복사본 | 이전 시점의 즐겨찾기 폴더와 비교합니다 | [섀도 복사본 활용](../../../03-techniques/analysis/volume-shadow-copy-analysis.md) |
| 다른 브라우저 | 같은 주소를 다른 브라우저 즐겨찾기에도 넣었는지 봅니다 | [크롬 계열 브라우저](../chrome-edge-whale/index.md), [파이어폭스](../firefox/index.md) |

웹 사용 전체를 재구성하는 흐름은 [웹 사용 행위 재구성](../../../04-scenarios/activity/web-activity.md) 에 있습니다.

## 실습

IE 를 쓴 공개 검체(NIST CFReDS 등)에서 사용자 프로필 폴더와 NTUSER.DAT 를 꺼내 아래 질문을 풀어 봅니다.

1. 검체의 Windows 버전은 무엇입니까? `User Shell Folders` 의 `Favorites` 값은 어느 폴더를 가리킵니까?
2. 즐겨찾기 폴더와 하위 폴더에 `.url` 파일이 몇 개 있습니까?
3. 처음부터 들어 있던 것으로 보이는 항목과 사용자가 추가한 것으로 보이는 항목을 나눠 봅니다. 무엇을 근거로 나눴습니까?
4. `.url` 한 개를 헥스로 열어 `URL=` 줄의 주소를 직접 읽어 봅니다. 도구가 보여 주는 주소와 같습니까?
5. 즐겨찾기 주소 가운데 방문 기록에도 있는 주소는 무엇입니까? 방문 시각과 `.url` 의 만든 시각은 어느 쪽이 앞섭니까?
6. 옛 엣지 패키지 폴더가 있습니까? 있다면 `spartan.edb` 는 어느 경로에 있습니까?

## 참고 문헌

1. Forensafe 블로그, 옛 엣지(EdgeHTML) 아티팩트 설명 글 (옛 엣지 즐겨찾기의 `spartan.edb`·옛 버전의 `.url`, `Favorites`·`Recovery`·`Datastore` 폴더 경로). https://www.forensafe.com/blogs/microsoftedge.html
2. EricZimmerman/KapeFiles, *Targets/Browsers/Edge.tkape* (옛 엣지 패키지 폴더 수집 범위). https://raw.githubusercontent.com/EricZimmerman/KapeFiles/master/Targets/Browsers/Edge.tkape
