---
title: "파일 형식 (SFL2·SFL3)"
parent: "최근 항목"
grand_parent: "아티팩트 · 파일·폴더 사용 흔적"
nav_order: 800
---

# 파일 형식 (SFL2·SFL3)

최근 항목 파일(`.sfl2`·`.sfl3`)은 NSKeyedArchiver 로 저장한 바이너리 plist 이고, `items` 배열의 항목마다 표시 이름·고유 ID와 함께 대상 파일을 가리키는 북마크(bookmark) 데이터가 들어 있어서, 분석은 대부분 이 북마크를 풀어 경로·볼륨·시각을 읽는 일입니다.

## 무엇이 들어 있나

`com.apple.sharedfilelist` 폴더의 목록 파일은 모두 같은 틀을 씁니다 [1][5]. 목록 하나가 파일 하나이고, 파일 안에는 항목 배열과 목록 속성이 있으며, 항목에는 이름·ID·표시 여부와 대상 파일의 북마크가 들어 있습니다. 어떤 목록 파일이 어느 폴더에 있고 macOS 버전마다 확장자가 어떻게 바뀌었는지는 허브 [최근 항목 (Shared File Lists)](index.md)의 표에 정리했습니다.

형식은 크게 두 갈래입니다. 1판 `.sfl` 은 루트에 `version` 값이 있습니다 [1]. `.sfl2`·`.sfl3`·`.sfl4` 는 공개 도구 mac_apt 가 세 형식의 항목 키가 같다고 보고 한 함수(`ReadSFL2Plist`)로 `items` 배열을 읽습니다 [1]. `.sfl4` 가 나오는 macOS 버전은 공개 자료가 없어 검체에서 확인합니다.

## 바깥 틀

파일은 `bplist00` 으로 시작하는 바이너리 plist 이고, 그 안의 객체는 NSKeyedArchiver 방식으로 직렬화돼 있습니다 [1][4][5]. NSKeyedArchiver 는 객체를 UID 로 서로 가리키게 저장하는 방식이라서, 바이너리 plist 를 그냥 열면 이름과 값이 떨어져 보입니다. 바이너리 plist 와 NSKeyedArchiver 를 읽는 법은 [속성 목록 파일 (Property List)](../../../01-foundations/data-formats/plist/index.md)에서 다룹니다.

`.sfl3` 는 항목 딕셔너리를 NSKeyedArchiver 식 `NSDictionary` 로 담습니다 [5]. 키는 `NS.keys`, 값은 `NS.objects` 라는 두 배열에 같은 순서로 들어 있고, 배열 안의 값은 실제 값이 아니라 UID 참조입니다 [5]. 그래서 키와 값을 번호로 짝지은 뒤 UID 를 따라가야 값이 나옵니다.

### 루트 키

| 형식 | 루트 키 | 내용 | 출처 |
|---|---|---|---|
| `.sfl` | `items`, 속성 딕셔너리, `version` | 속성 안에 `com.apple.LSSharedFileList.MaxAmount`(목록 최대 개수) | [1][2] |
| `.sfl2` | `items`, `properties` | `properties` 안에 `com.apple.LSSharedFileList.MaxAmount` 가 있을 수 있음 | [2] |
| `.sfl3` | 공개 자료 없음 | mac_apt 는 `.sfl2` 와 같은 방식으로 `items` 를 읽음 | [1] |

## 항목(item) 키

| 형식 | 키 | 뜻 | 출처 |
|---|---|---|---|
| `.sfl` | `name` | 표시 이름 | [1][2] |
| `.sfl` | `URL` → `NS.relative` | 대상 URL | [1][2] |
| `.sfl` | `order` | 순서 값 | [2] |
| `.sfl` | `uniqueIdentifier` → `NS.uuidbytes` | 고유 ID | [2] |
| `.sfl` | `bookmark` | 북마크 데이터 | [2] |
| `.sfl2` 이상 | `Name` | 표시 이름. 없을 수 있고, 그때는 북마크에서 이름을 얻음 | [1][2][5] |
| `.sfl2` 이상 | `uuid` | 항목 고유 ID(문자열) | [1][2][5] |
| `.sfl2` 이상 | `visibility` | 표시 여부 | [2][4] |
| `.sfl2` 이상 | `Bookmark` | 북마크 데이터. 바로 데이터이거나 `NS.data` 가 든 딕셔너리 | [1][2][5] |
| `.sfl2` 이상 | `CustomItemProperties` | 추가 속성 딕셔너리 | [1][2] |
| `.sfl2` 이상 | `CustomItemProperties` → `com.apple.LSSharedFileList.DateLastSeen` | mac_apt 가 "Date Last Seen" 으로 뽑는 날짜 | [1] |

`visibility` 값은 0=보임, 1=숨김, 2=고정(Pinned)이라는 설명이 SFL-Parser README 에 있지만 [4], 이 README 는 다른 설명 몇 곳이 다른 자료와 맞지 않아서 이 값 뜻도 검체나 다른 자료로 확인한 뒤에 씁니다. `Bookmark` 는 바로 데이터인 경우와 `NS.data` 딕셔너리인 경우가 있어서 [1][5], 직접 파서를 짤 때도 두 경우를 모두 처리합니다.

항목 가운데 몇 가지는 공개 도구가 일부러 건너뜁니다. `.sfl` 에서 URL 이 `x-apple-findertag` 로 시작하는 항목은 파인더 태그라서 mac_apt 가 건너뛰고, ProjectsItems 목록은 태그 이름과 색만 담아서 역시 읽지 않습니다 [1]. RecentHosts 목록 항목에는 북마크가 없어서 macMRU 도 이 파일에서만 북마크를 읽지 않습니다 [2].

## 북마크 데이터

북마크는 대상 파일을 다시 찾으려고 경로·볼륨 정보·파일 ID를 묶어 둔 데이터이고, 최근 항목에서 증거로 쓰는 값 대부분이 여기서 나옵니다. 북마크 형식 전체는 [파일 참조 데이터 (Alias·Bookmark)](../../../01-foundations/value-decoding/alias-bookmark.md)에서 다루고, 여기서는 최근 항목을 읽는 데 필요한 만큼만 정리합니다 [3].

맨 앞 4바이트 매직은 `book` 이고 옛 형식은 `alis` 입니다. mac_apt 는 매직이 `book` 이 아니면 북마크로 읽지 않습니다 [1][3]. 따로 적지 않은 숫자는 little-endian 입니다 [3].

| 오프셋 | 크기 | 내용 |
|---|---|---|
| 0 | 4 | 매직 (`book` 또는 `alis`) |
| 4 | 4 | 전체 크기 |
| 8 | 4 | 알 수 없음 (0x10040000) |
| 12 | 4 | 머리 크기 (48) |
| 16 | 32 | 예약 |

파일 안의 오프셋은 모두 이 48바이트 머리가 끝나는 곳을 기준으로 셉니다. 머리 바로 뒤, 오프셋 48의 4바이트가 첫 TOC 의 위치입니다 [3]. TOC 머리에는 TOC 크기에서 8을 뺀 값, 매직 0xFFFFFFFE, 식별자, 다음 TOC 오프셋, 항목 수가 이 순서로 들어 있습니다 [3]. TOC 머리 크기는 명세 본문에 적힌 값과 표의 칸 수가 서로 맞지 않으니, 파서를 짤 때는 칸 순서대로 읽습니다 [3].

TOC 항목은 12바이트로, 키 4바이트, 데이터 레코드 오프셋 4바이트, 예약 4바이트이고, TOC 는 키 순서로 정렬돼 있어야 합니다 [3]. 키의 최상위 비트(0x80000000)가 켜져 있으면 `key & 0x7fffffff` 가 키 이름 문자열 레코드의 오프셋입니다 [3]. 데이터 레코드는 길이 4바이트, 형식 코드 4바이트, 데이터 순서입니다 [3].

| 형식 코드 | 데이터 |
|---|---|
| 0x0101 | 문자열(UTF-8) |
| 0x0201 | 바이트 |
| 0x0301 ~ 0x0306 | 숫자 |
| 0x0400 | 날짜 |
| 0x0500 / 0x0501 | 거짓 / 참 |
| 0x0601 | 배열 |
| 0x0701 | 딕셔너리 |
| 0x0801 | UUID |
| 0x0901 / 0x0902 | URL / 상대 URL |

포렌식에서 주로 보는 키는 아래와 같습니다 [3]. macMRU 도 같은 키 번호로 결과를 냅니다 [2].

| 키 | 내용 |
|---|---|
| 0x1003 | 대상 URL |
| 0x1004 | 대상 경로(경로 조각 배열) |
| 0x1005 | 대상 CNID 경로(CNID 배열) |
| 0x1010 | 대상 플래그 |
| 0x1020 | 대상 파일 이름 |
| 0x1030 | 대상 CNID |
| 0x1040 | 대상 생성 시각(날짜) |
| 0x2002 | 볼륨 경로 |
| 0x2005 | 볼륨 URL |
| 0x2010 | 볼륨 이름 |
| 0x2011 | 볼륨 UUID(UUID 형식이 아닌 문자열) |
| 0x2012 | 볼륨 크기(8바이트 정수) |
| 0x2013 | 볼륨 생성 시각(날짜) |
| 0x2020 | 볼륨 플래그 |
| 0x2030 | 루트 볼륨 여부 |
| 0x2050 | 볼륨 마운트 지점(URL) |
| 0xc001 | 상위 폴더 위치(경로 배열 안 번호) |
| 0xc011 | 북마크를 만든 사용자 이름 |
| 0xc012 | 북마크를 만든 사용자 UID |
| 0xd010 | 생성 옵션 |
| 0xf017 | 표시 이름 |
| 0xf030 | 북마크 생성 시각(64비트 실수, 2001-01-01 기준 초) |
| 0xf080 / 0xf081 | 샌드박스 읽기쓰기 / 읽기전용 확장 |

mac_apt 는 이 가운데 경로(0x1004 조각을 `/` 로 이음), 대상 생성 시각, 볼륨 이름·크기·생성 시각·UUID 를 뽑고, 0x1003 URL 이 `file:///` 로 시작하지 않으면 smb·afp·ftp 같은 파일 밖 URL 로 따로 적습니다 [1].

SFL-Parser README 는 북마크 키를 "0x0500 경로 조각, 0x1010 볼륨 UUID, 0x2000 보안 확장" 으로 적고 `.sfl3` 에만 있는 새 키도 소개하지만 [4], 이 번호는 mac_alias 문서의 키 체계(0x1004 경로, 0x2011 볼륨 UUID, 0xf080·0xf081 샌드박스 확장)와 맞지 않습니다 [3]. 위 키 표는 mac_alias 문서의 키 체계입니다.

## 증거로서 의미

**증명하는 것.** 목록 파일에 항목이 있으면, 그 사용자 계정의 목록에 이 대상이 한 번 이상 등록됐다는 기록입니다. 북마크의 경로·볼륨 이름·볼륨 UUID·볼륨 크기로 대상이 어느 볼륨에 있었는지를 좁힐 수 있고, 볼륨 칸을 보면 외장 저장 장치나 네트워크 볼륨 위의 파일을 내장 디스크 파일과 나눠 볼 수 있습니다 [1][3]. 명세에 있는 것은 볼륨 칸까지이고, 이 칸으로 외장·네트워크를 가르는 것은 해석입니다. 0xc011·0xc012 에는 북마크를 만든 사용자 이름과 UID 가 들어 있습니다 [3].

**증명하지 못하는 것.** 파일 내용을 읽었는지, 몇 번 열었는지, 언제 열었는지는 항목만으로 알 수 없습니다. 북마크의 경로는 북마크를 만들 때의 경로라서 지금 그 자리에 파일이 있다는 뜻도 아닙니다. 사용자 폴더 안에 파일이 있다는 사실과 그 계정을 쓴 사람이 누구인지도 다른 문제이고, 이는 [그 시각에 맥을 쓴 사람이 누구인가 (User Attribution)](../../../04-scenarios/activity/user-attribution.md)에서 따로 따집니다.

## 시각 해석

북마크 안의 날짜(형식 0x0400)는 **big-endian** IEEE double 이고, 2001-01-01 00:00:00 UTC 부터 흐른 초, 곧 맥 절대 시각입니다 [3]. 북마크의 다른 숫자가 little-endian 이라서 날짜만 바이트 순서가 반대인 점을 놓치기 쉽습니다. 맥 절대 시각을 바꾸는 법은 [맥의 시각 값 (Mac Absolute Time·Unix·HFS)](../../../01-foundations/value-decoding/mac-time-values.md)을 봅니다.

| 값 | 뜻 | 주의 |
|---|---|---|
| 0x1040 대상 생성 시각 | 대상 파일이 만들어진 시각 | 파일을 연 시각이 아님 |
| 0x2013 볼륨 생성 시각 | 대상이 있던 볼륨이 만들어진 시각 | 같은 외장 장치를 다른 기록과 맞출 때 씀 |
| 0xf030 북마크 생성 시각 | 북마크를 만든 시각 [3] | 목록에 처음 넣은 시각과 같은지는 검체에서 확인 |
| `DateLastSeen` | mac_apt 가 "Date Last Seen" 으로 내는 날짜 [1] | 언제 기록·갱신되는지, 시각 기준이 무엇인지 공개 자료 없음. 검체에서 확인 |

항목마다 "파일을 연 시각" 칸이 있다는 공개 자료는 없습니다. 목록 안의 순서, 목록 파일의 수정 시각, `DateLastSeen` 으로 어림할 수는 있지만 추정일 뿐이고, `.sfl2` 이상에서 배열 앞쪽이 최신인지도 알려져 있지 않습니다. 그래서 보고서에는 "이 시각에 열었다" 가 아니라 "이 목록 파일이 이 시각에 마지막으로 바뀌었고 그때 목록에 이 항목이 있었다" 처럼 기록이 말하는 만큼만 씁니다.

## 함정과 한계

- `.sfl3` 의 루트 키 구성과 `.sfl3`·`.sfl4` 가 쓰이기 시작한 macOS 버전은 공개 자료가 없어 검체로 확인해야 합니다. 버전별 설명은 도구 코드 주석과 도움말에서 나온 것이라, 검체의 macOS 버전과 맞춰 봅니다.
- `CustomItemProperties` 는 빈 딕셔너리로 나오는 경우가 있어서 [2], 비어 있어도 이상한 일은 아닙니다.
- 공개 도구는 태그 항목, ProjectsItems 목록, 매직이 `book` 이 아닌 북마크를 건너뜁니다 [1]. 도구 결과에 없는 항목이 원본 파일에는 있을 수 있으니 필요하면 원본 plist 를 함께 봅니다.
- SFL-Parser README 에는 북마크 키 번호처럼 다른 자료와 맞지 않거나 다른 자료로 확인되지 않는 설명이 섞여 있어서 [4], 이 README 에만 나오는 값은 그대로 옮기지 않습니다.

## 직접 분석해 보기

### 헥스로 한 번

아래는 북마크 구조 [3]에 맞춰 만든 예시이고, 실제 검체에서 뽑은 값이 아닙니다. 전체 크기와 첫 TOC 오프셋은 설명을 위해 넣은 숫자입니다.

```
00000000  62 6f 6f 6b 68 03 00 00  00 00 04 10 30 00 00 00  |bookh.......0...|
00000010  00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00  |................|
00000020  00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00  |................|
00000030  04 03 00 00 ...
```

맨 앞 `62 6f 6f 6b` 가 매직 `book` 이고, `68 03 00 00` 은 little-endian 으로 읽어 전체 크기 0x368 입니다. `00 00 04 10` 은 0x10040000, `30 00 00 00` 은 머리 크기 48 입니다. 오프셋 0x30 의 `04 03 00 00` 은 첫 TOC 위치 0x304 이고, 오프셋은 머리 끝 기준이라 파일 안 실제 위치는 0x30 + 0x304 = 0x334 입니다.

날짜 레코드는 이렇게 생깁니다(역시 명세로 만든 예시).

```
08 00 00 00   00 04 00 00   41 c5 cb 8e cc 00 00 00
길이 8        형식 0x0400    big-endian double
```

마지막 8바이트를 big-endian double 로 읽으면 731323800.0 이고, 2001-01-01 00:00:00 UTC 에 이 초를 더하면 2024-03-05 09:30:00 UTC 입니다. 같은 8바이트를 little-endian 으로 읽으면 엉뚱한 값이 나오니, 날짜가 말이 안 되는 값으로 보이면 바이트 순서부터 의심합니다.

### 공개 도구로 한 번

공개 도구 가운데 mac_apt 의 `RECENTITEMS` 플러그인(1.5)은 `.sfl` 과 `.sfl2`~`.sfl4` 를 함께 읽고 북마크에서 경로·볼륨 정보·생성 시각을 뽑아 줍니다 [1]. SFL-Parser 는 `.sfl3`·`.sfl4` 전용이고 [4], exhume_artefacts 는 `.sfl`·`.sfl2`·`.sfl3` 를 읽어 `macos.recent.item` 이라는 종류로 결과를 냅니다 [5]. 도구가 낸 경로와 시각을 헥스에서 직접 푼 값과 한두 항목만이라도 맞춰 보면, 바이트 순서나 키 번호를 잘못 읽은 도구를 가려낼 수 있습니다. 도구를 검증하는 절차는 [도구 검증 (Tool Validation)](../../../03-techniques/reporting/tool-validation.md)에서 다룹니다.

## 교차 검증

- [식별자 읽기 (UUID·UID·GUID)](../../../01-foundations/value-decoding/uuid-uid.md) — 항목 `uuid` 와 볼륨 UUID 를 읽을 때
- [USB 저장 장치 (USB Storage)](../../external-devices/usb/index.md) — 북마크의 볼륨 이름·UUID·크기를 장치 연결 기록과 맞출 때
- [공유 폴더 연결 기록 (SMB·AFP)](../../network/network-shares.md) — 파일 밖 URL 이 가리키는 서버를 확인할 때
- [파일 시스템 이벤트 (FSEvents)](../../filesystem/fsevents/index.md) — 북마크 경로의 파일이 만들어지거나 지워진 기록을 찾을 때
- [이 파일을 누가 언제 열었나 (File Access)](../../../04-scenarios/activity/file-access.md)

## 실습

NIST CFReDS 같은 공개 검체 가운데 macOS 사용자 폴더가 들어 있는 이미지를 골라 아래 질문을 풀어 봅니다.

1. 한 사용자의 `com.apple.sharedfilelist` 폴더에서 목록 파일의 확장자는 무엇이고, 검체의 macOS 버전과 허브 표가 맞는지 확인합니다.
2. 항목 하나의 북마크를 헥스로 풀어 매직, 첫 TOC 위치, 0x1004 경로, 0x2010 볼륨 이름을 직접 읽고 공개 도구 결과와 비교합니다.
3. 북마크 안의 날짜 하나를 big-endian 과 little-endian 으로 각각 읽어 보고, 어느 쪽이 말이 되는 값인지 확인합니다.
4. 볼륨 이름이 내장 디스크와 다른 항목이 있으면, 그 볼륨이 연결된 기록을 다른 아티팩트에서 찾아봅니다.

## 참고 문헌

1. mac_apt `plugins/recentitems.py` (RECENTITEMS 1.5, Yogesh Khatri) — https://raw.githubusercontent.com/ydkhatri/mac_apt/master/plugins/recentitems.py
2. macMRU-Parser `macMRU.py` (Sarah Edwards / mac4n6, 2017) — https://raw.githubusercontent.com/mac4n6/macMRU-Parser/master/macMRU.py
3. mac_alias 문서, "Mac Bookmark Format" — https://mac-alias.readthedocs.io/en/latest/bookmark_fmt.html
4. SFL-Parser README (Hochschule für Polizei Baden-Württemberg) — https://github.com/mb4n6/SFL-Parser
5. exhume_artefacts `src/parsers/macos/sharedfilelist.rs` (forensicxlab) — https://github.com/forensicxlab/exhume_artefacts/blob/main/src/parsers/macos/sharedfilelist.rs
