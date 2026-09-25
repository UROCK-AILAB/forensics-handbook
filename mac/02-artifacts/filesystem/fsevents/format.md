---
title: "파일 형식 (.fseventsd)"
parent: "파일 시스템 이벤트"
grand_parent: "아티팩트 · 파일 시스템"
nav_order: 940
---

# 파일 형식 (.fseventsd)

`.fseventsd` 폴더의 이벤트 파일은 여러 멤버로 된 GZIP 파일이고, 풀어 보면 12바이트 페이지 헤더 뒤로 경로와 이벤트 ID·플래그가 붙은 레코드가 이어집니다. 레코드 버전은 세 가지이고 버전이 올라갈 때마다 고정 길이 부분에 노드 ID와 UID가 차례로 붙습니다.

## 무엇이 들어 있나

fseventsd 데몬은 볼륨에서 일어난 파일 시스템 변경 알림을 모아 이 폴더에 파일로 씁니다. 레코드 하나에는 바뀐 경로와 이벤트 ID, 무엇이 바뀌었는지 나타내는 플래그가 들어 있지만 시각 칸은 없습니다 [1]. 날짜를 어림하는 방법은 [해석 함정 (Pitfalls)](pitfalls.md)에서, 플래그 값을 읽는 법은 [이벤트 플래그 읽기 (Flags)](flags.md)에서 다룹니다.

## 위치

공개 분석 도구 FSEventsParser는 아래 두 경로에서 이벤트 파일을 찾습니다 [2].

```
/.fseventsd
/System/Volumes/Data/.fseventsd
```

두 번째 경로는 시스템 볼륨과 데이터 볼륨이 나뉜 구조에서 데이터 볼륨 쪽 위치이고, 이 구조는 [볼륨 그룹과 펌링크 (Volume Group·Firmlinks)](../../../01-foundations/disk-volume/volume-group-firmlinks.md)에서 설명합니다. 이벤트 파일은 Mac 본체뿐 아니라 Mac에 꽂았던 외장 저장 장치에서도 나옵니다 [5].

같은 폴더의 `fseventsd-uuid` 파일은 이벤트 파일이 아니라서 FSEventsParser는 이 파일을 건너뜁니다 [2].

## 파일 구조

이벤트 파일 하나는 여러 멤버로 된 GZIP 파일이고, 압축을 풀면 디스크 로그 스트림(페이지)이 하나 이상 나옵니다 [1]. 숫자는 모두 little-endian으로 저장하고, 경로 문자열은 확장 ASCII(단일·다중 바이트)이며 NULL 바이트로 끝납니다 [1]. 기록된 경로는 앞에 `/` 가 붙지 않아서 `private/var/log/asl` 처럼 보입니다 [2].

GZIP 헤더에는 수정 시각 칸이 있지만, plaso 코드 주석은 fseventsd가 파일을 쓸 때 이 칸을 채우지 않는 것으로 보인다고 적고 있습니다 [4]. 코드 주석에 적힌 관찰이라서 명세로 확정된 사실은 아닙니다.

### 페이지 헤더 (12바이트)

| 오프셋 | 크기 | 내용 |
|---|---|---|
| 0 | 4 | 서명. 바이트로는 `1SLD`, `2SLD`, `3SLD` 이고 little-endian 정수로 읽으면 DLS1·DLS2·DLS3 |
| 4 | 4 | 알 수 없음(패딩) |
| 8 | 4 | 페이지(스트림) 크기, uint32 LE |

libyal 문서에는 `1SLD` 와 `2SLD` 만 있고 `3SLD` 는 FSEventsParser 코드에 있습니다 [1][2]. FSEventsParser는 헤더의 8~11번째 바이트(`buf[8:12]`)를 `<I` 로 읽어 페이지 길이로 씁니다 [2].

### 레코드

레코드는 NULL로 끝나는 경로 바로 뒤에 고정 길이 부분이 붙는 모양이고, 고정 길이 부분의 크기는 서명이 정합니다 [1][2].

| 레코드 버전 | 서명 | 고정 부분 | 구성 | 해당 macOS |
|---|---|---|---|---|
| 1 | `1SLD` | 12바이트 | 이벤트 ID 8 + 플래그 4 | Mac OS X 10.5 ~ macOS 10.12 [1][4] |
| 2 | `2SLD` | 20바이트 | 이벤트 ID 8 + 플래그 4 + 노드 ID 8 | macOS 10.13 High Sierra [1][2][4] |
| 3 | `3SLD` | 24바이트 | 이벤트 ID 8 + 플래그 4 + 노드 ID 8 + UID 4 | macOS 14 Sonoma (FSEventsParser 코드 주석 기준) [2] |

고정 부분 안의 자리와 FSEventsParser가 읽는 형식은 아래와 같습니다 [2].

| 고정 부분 오프셋 | 크기 | 내용 | FSEventsParser 읽는 형식 |
|---|---|---|---|
| 0 | 8 | 이벤트 ID | `<Q` |
| 8 | 4 | 플래그 | `>I` (빅엔디언으로 읽음) |
| 12 | 8 | 노드 ID (버전 2 이상) | `<q` |
| 20 | 4 | UID (버전 3) | `<i` |

플래그 칸은 디스크에 little-endian으로 들어 있지만 FSEventsParser는 빅엔디언으로 읽어서, 같은 값이 도구마다 다른 16진수로 보입니다. 그 대조표는 [이벤트 플래그 읽기 (Flags)](flags.md)에 있습니다.

노드 ID는 High Sierra에서 추가된 파일 시스템 노드 ID이고, 버전 1 레코드에는 이 칸이 없어서 도구 결과에서 비어 보입니다 [5]. UID 칸은 FSEventsParser 코드 주석에 "UID introduced with Sonoma" 라고만 적혀 있고 [2], 어떤 UID인지 밝힌 문서는 참고 문헌에 없어서 사용자 계정으로 단정하지 않습니다.

### 이벤트 ID

이벤트 ID는 64비트 값이고 시간 순서대로 매겨집니다 [3][5]. Apple 문서는 이벤트 ID가 2^64에 가까워지면 처음으로 되돌아가고, 이때 API 쪽에서 `kFSEventStreamEventFlagEventIdsWrapped` 플래그로 알린다고 설명합니다 [3]. 이벤트 ID는 순서를 알려 줄 뿐 시각이 아니고, 다른 컴퓨터에서 쓰던 디스크를 붙였을 때 ID가 어떻게 이어지는지는 [해석 함정 (Pitfalls)](pitfalls.md)에서 다룹니다.

## 직접 분석해 보기

### 헥스로 한 번

아래 바이트는 실제 검체가 아니라 명세 [1]에 맞춰 만든 예시입니다. GZIP을 푼 뒤의 내용이고, 버전 2 페이지에 레코드 하나가 들어 있는 모양입니다. `??` 는 뜻이 알려지지 않은 칸이고 `SS` 는 페이지 크기 자리입니다.

```
오프셋  00 01 02 03 04 05 06 07 08 09 0A 0B 0C 0D 0E 0F
000000  32 53 4C 44 ?? ?? ?? ?? SS SS SS SS 55 73 65 72   2SLD........User
000010  73 2F 78 78 78 2F 61 2E 74 78 74 00 56 34 12 00   s/xxx/a.txt.V4..
000020  00 00 00 00 01 00 80 00 DE BC 0A 00 00 00 00 00   ................
```

읽는 순서는 다음과 같습니다.

1. 0x00~0x03의 `32 53 4C 44` 는 서명 `2SLD` 라서 고정 부분이 20바이트인 버전 2 레코드가 이어집니다.
2. 0x08~0x0B는 페이지 크기이고 uint32 LE로 읽습니다.
3. 0x0C부터 NULL(0x1B)까지가 경로 `Users/xxx/a.txt` 이고(사용자 이름 자리는 `xxx` 로 가렸습니다), 앞에 `/` 가 없습니다.
4. 0x1C~0x23의 `56 34 12 00 00 00 00 00` 은 이벤트 ID이고 LE로 읽으면 0x123456(1193046)입니다.
5. 0x24~0x27의 `01 00 80 00` 은 플래그이고 LE로 읽으면 0x00800001입니다. 이 값을 푸는 법은 [이벤트 플래그 읽기 (Flags)](flags.md)에 있습니다.
6. 0x28~0x2F의 `DE BC 0A 00 00 00 00 00` 은 노드 ID이고 LE로 읽으면 0xABCDE(703710)입니다.
7. 다음 레코드는 0x30부터 같은 방식으로 이어집니다.

### 공개 도구로 한 번

FSEventsParser(Nicole Ibrahim, 버전 4.1, Apache 2.0)는 `1SLD`·`2SLD`·`3SLD` 를 모두 읽고, `.fseventsd` 폴더를 통째로 넣을 수도 있고 dfVFS로 디스크 이미지를 바로 넣을 수도 있습니다 [2]. 결과 칸은 `id`, `node_id`, `fs_uid`, `fullpath`, `type`, `flags`, `approx_dates_plus_minus_one_day`, `source`, `source_modified_time` 이고, 상세 출력에는 `id_hex`, `filename`, `mask`, `dls_version`, `record_end_offset` 이 더 붙습니다 [2]. 폴더를 복사해서 넣을 때는 파일 수정 시각을 보존해야 날짜 추정이 동작하고, 그 이유는 [해석 함정 (Pitfalls)](pitfalls.md)에 있습니다.

plaso에는 `fseventsd` 파서가 있고, 코드 설명은 `1SLD` 와 `2SLD` 만 언급합니다 [4].

이벤트 파일이 GZIP 형식이라서 비할당 영역에서 GZIP을 카빙하면 지워진 이벤트 파일을 찾을 수 있습니다 [5]. 카빙 방법은 [삭제 데이터 복구 (Data Recovery)](../../../03-techniques/analysis/data-recovery/index.md)에서, 카빙한 결과를 읽을 때의 주의점은 [해석 함정 (Pitfalls)](pitfalls.md)에서 다룹니다.

## 참고 문헌

1. libyal dtformats — MacOS File System Events Disk Log Stream format — https://github.com/libyal/dtformats/blob/main/documentation/MacOS%20File%20System%20Events%20Disk%20Log%20Stream%20format.asciidoc
2. FSEventsParser 4.1 소스 (Nicole Ibrahim) — https://raw.githubusercontent.com/dlcowen/FSEventsParser/master/FSEParser_V4.1.py
3. Apple, File System Events Programming Guide — Using the File System Events API — https://developer.apple.com/library/archive/documentation/Darwin/Conceptual/FSEvents_ProgGuide/UsingtheFSEventsFramework/UsingtheFSEventsFramework.html
4. plaso fseventsd 파서 소스 — https://raw.githubusercontent.com/log2timeline/plaso/main/plaso/parsers/fseventsd.py
5. FSEventsParser README — https://raw.githubusercontent.com/dlcowen/FSEventsParser/master/README.md
