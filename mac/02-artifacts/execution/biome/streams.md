---
title: "저장 위치와 스트림"
parent: "바이옴"
grand_parent: "아티팩트 · 프로그램 실행 흔적"
nav_order: 710
---

# 저장 위치와 스트림 (Streams)

Biome 저장소는 `streams` 폴더 아래 `restricted`·`public` 폴더에 스트림 이름을 그대로 딴 폴더를 두고, 스트림마다 `local` 폴더에는 이 기기의 기록을, `remote` 폴더에는 같은 계정의 다른 기기에서 넘어온 기록을 SEGB 파일로 담습니다 [2][5].

## 무엇을 기록하나 · 왜 생기나

스트림 (Stream)은 한 가지 종류의 사건을 모아 두는 단위이고, 폴더 이름이 곧 스트림 이름입니다 [5]. 스트림 폴더 안의 SEGB 파일에는 사건 하나가 기록 하나로 쌓이고, 기록 안의 데이터는 대개 protobuf입니다 [4]. 어떤 사건을 담는지는 스트림마다 다르고, iOS에서 포렌식 가치가 있는 스트림 84개는 기기 상태, 연결 기기·네트워크, 위치, 앱 사용, 앱 데이터의 다섯 분류로 나눌 수 있습니다 [3].

macOS·iOS 공용인 mac_apt BIOME 플러그인은 `App.InFocus`, `App.WebUsage`, `Device.Wireless.Bluetooth`, `Device.Wireless.WiFi`, `Notification.Usage`, `Safari.*`, `ScreenTime.AppUsage`, `SystemSettings.SearchTerms`, `App.Intent` 스트림을 해석합니다 [5]. 플러그인이 두 OS를 함께 다루므로, 이 스트림이 macOS에 모두 있는지는 실제 데이터로 확인합니다. 이 가운데 `App.InFocus` 는 [앱 사용 스트림 (App.InFocus)](app-infocus.md)에서 따로 다룹니다. iOS용 iLEAPP은 `_DKEvent.App.InFocus`, `ProactiveHarvesting.Mail`, `ProactiveHarvesting.Messages`, `Messages.Read`, `ScreenTime.AppUsage`, `Keyboard.TokenFrequency` 같은 스트림을 모듈로 읽습니다 [2].

기록 보존 기간은 iOS 자료만 있습니다. iOS에서 대부분 스트림의 활성 기록은 28일 동안 남고, `Device.Metadata`·`Device.Timezone` 은 최대 10개월, `Discoverability.Signals` 는 약 9개월 남습니다 [3]. macOS의 보존 기간은 실제 데이터로 확인해야 합니다.

## 위치와 폴더 구조

macOS의 Biome 저장소는 아래 두 위치에 있습니다 [5].

```
/private/var/db/biome/streams/      시스템
~/Library/Biome/streams/            사용자별 (코드상 {home}/Library/Biome/streams/)
```

두 위치 모두 그 아래에 `restricted` 와 `public` 폴더가 있고, 그 안의 폴더 하나가 스트림 하나입니다 [5]. 앱 사용 스트림을 예로 들면 파일은 아래 자리에 있습니다 [2][5].

```
.../streams/restricted/App.InFocus/local/<파일>
.../streams/restricted/App.InFocus/remote/<기기 식별자>/<파일>
```

| 폴더·파일 | 뜻 | 도구 처리 |
|---|---|---|
| `local/` | 이 기기에서 쓴 SEGB 파일 [2][5] | 읽음 |
| `remote/` 아래 기기 식별자 폴더 | 같은 계정의 다른 기기에서 동기화돼 온 기록이고 이 기기의 사건이 아님 [2] | iLEAPP은 출처를 따로 표시 |
| `tombstone` 폴더 | 안에 남는 내용은 실제 데이터에서 열어 확인 | mac_apt·iLEAPP 모두 건너뜀 [2][5] |
| 크기 0 파일 | — | mac_apt·iLEAPP 모두 건너뜀 [2][5] |
| `.` 으로 시작하는 숨김 파일 | — | iLEAPP은 건너뛰고 [2], mac_apt 코드에는 따로 거르는 부분이 없음 [5] |

SEGB 파일 이름은 숫자이고 파일을 만든 시각을 나타냅니다 [4]. 파일 이름을 정수로 읽어 1,000,000으로 나누면 맥 절대 시각(2001-01-01 기준 초)이 되므로, 파일 이름은 마이크로초 단위 맥 절대 시각입니다 [5].

## 구조

SEGB 파일에는 v1과 v2 두 가지가 있고, 매직 `SEGB` 가 어디 있는지로 구분합니다. v1은 헤더 끝(오프셋 52)에, v2는 파일 맨 앞(오프셋 0)에 매직이 있습니다 [1]. 형식 전체와 읽는 법은 [SEGB 형식 (SEGB)](../../../01-foundations/data-formats/segb.md)에서 다루고, 여기서는 Biome 파일을 열어 기록과 상태 값을 찾는 데 필요한 만큼만 정리합니다.

| 항목 | SEGB v1 [1] | SEGB v2 [1][4] |
|---|---|---|
| 파일 헤더 | 56바이트. 오프셋 0에 데이터 끝 오프셋(uint32 LE), 오프셋 52에 매직 | 32바이트. 오프셋 0 매직, 오프셋 4 기록 개수(int32 LE), 오프셋 8 파일 생성 시각(double), 나머지 16바이트 |
| 기록 헤더 | 32바이트, `<iiddIi`: 기록 길이, 상태, 시각1, 시각2, CRC32, 미상 | 8바이트: CRC32(uint32), 미상(int32) |
| 상태와 시각이 있는 곳 | 기록 헤더 안 | 파일 끝 트레일러 |
| 트레일러 | 없음 | 파일 끝에서 (기록 개수 × 16)바이트. 항목마다 기록 끝 오프셋(int32, 헤더 끝 기준), 상태(int32), 기록 생성 시각(double) |
| 정렬 | 8바이트 경계 | 4바이트 경계 |

v1의 CRC32는 기록 데이터에 zlib crc32를 적용한 값입니다 [1]. v2 헤더의 나머지 16바이트는 내부용 12바이트와 패딩 4바이트입니다 [4].

### 기록 상태 값

| 값 | 뜻 | ccl_segb 처리 |
|---|---|---|
| 1 | Written (기록됨) | 읽음 |
| 3 | Deleted (삭제됨) | 읽음 |
| 4 | Unknown. 빈 기록 | 읽지 않고 건너뜀 |

출처는 [1][4]이고, 처리 열은 ccl_segb 코드 기준입니다 [1]. v2 트레일러를 읽을 때는 몇 가지를 더 봐야 합니다 [1]. 상태 0에 끝 오프셋도 0인 빈 항목이 끼어 있을 수 있어 건너뛰고, 트레일러 항목 둘이 같은 끝 오프셋을 가리킬 수도 있습니다(기록됐다가 나중에 삭제 표시된 기록 등). 오래된 트레일러 항목이 이미 다시 쓰인 영역을 가리키면 그 자리에 원래 데이터는 남아 있지 않습니다.

## 시각 해석

한 파일 안에서 시각을 볼 수 있는 자리는 세 곳이고, 모두 맥 절대 시각입니다 [1][5].

| 자리 | 뜻 | 단위 |
|---|---|---|
| 파일 이름 | 파일을 만든 시각 [4][5] | 마이크로초 (정수) |
| v2 헤더 오프셋 8 | 파일 생성 시각 [1][4] | 초 (double) |
| v1 기록 헤더의 시각1·시각2, v2 트레일러의 시각 | 기록마다의 시각 [1][4] | 초 (double) |

v1 기록 헤더의 두 시각은 각각의 뜻이 정해져 있지 않으므로, 보고서에는 값만 옮기고 뜻을 단정하지 않습니다. 시각의 기준 시점은 2001-01-01입니다 [1].

시간대도 도구마다 다르게 붙습니다. ccl_segb는 시간대 정보 없는 날짜·시각 값을 만들고, iLEAPP은 이 값에 UTC를 붙여 표시합니다 [1][2]. 여러 도구의 결과를 한 타임라인에 넣을 때는 각 도구가 시간대를 어떻게 붙였는지 먼저 맞춥니다.

기록 안의 protobuf 데이터에도 따로 시각 필드가 들어 있는 스트림이 있고, SEGB 기록 시각과 뜻이 다를 수 있습니다. 앱 사용 스트림의 예는 [앱 사용 스트림 (App.InFocus)](app-infocus.md)에서 다룹니다. 맥 절대 시각을 푸는 법은 [맥의 시각 값 (Mac Absolute Time·Unix·HFS)](../../../01-foundations/value-decoding/mac-time-values.md)에 있습니다.

## 함정과 한계

삭제 표시(상태 3)된 기록도 시각은 남아 있지만, 도구마다 이 기록을 다르게 다룹니다. iLEAPP은 Deleted 기록을 시각만 있는 행으로 보고하고 [2], mac_apt는 Deleted 기록을 아예 출력하지 않아서 [5] 같은 파일을 넣어도 도구마다 결과 행 수가 다를 수 있습니다. 행 수가 다르다고 한쪽 도구가 틀렸다고 보기 전에 상태 값을 먼저 확인합니다.

기록 내용이 0으로 지워진 뒤에도 쓰기 시각은 남아 있을 수 있습니다 [3]. 그래서 지운 흔적을 찾을 때는 내용이 빈 기록의 시각도 목록에 넣습니다.

`remote` 폴더의 기록은 이 기기가 아니라 같은 계정의 다른 기기에서 일어난 사건입니다 [2]. 폴더를 구분하지 않고 통째로 읽으면 다른 기기의 사건이 이 맥의 사건처럼 섞여서, 결과에 출처 폴더를 열로 남기는 도구를 쓰거나 `local` 과 `remote` 를 나눠 읽습니다.

어느 macOS부터 Biome과 SEGB v1·v2를 쓰는지, macOS의 보존 기간, 위 스트림이 macOS에 모두 있는지, Biome에 기록을 쓰는 프로세스 이름은 실제 데이터로 확인해야 합니다. `tombstone` 폴더는 공개 도구가 건너뛰는 폴더라도 수집할 때 함께 가져와 안에 무엇이 남는지 확인합니다.

## 직접 분석해 보기

### 헥스로 한 번

아래 바이트는 실제 데이터가 아니라 명세 [1][4]에 맞춰 만든 예시입니다. 파일 이름이 `747000000000000` 인 v2 파일에 기록 하나가 들어 있는 모양이고, `??` 는 뜻이 알려지지 않은 필드, `CC` 는 CRC32 자리, `DD` 는 기록 데이터(protobuf) 자리입니다.

```
오프셋  00 01 02 03 04 05 06 07 08 09 0A 0B 0C 0D 0E 0F
000000  53 45 47 42 01 00 00 00 00 00 00 60 28 43 C6 41   SEGB.......`(C.A
000010  ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ??   ................
000020  CC CC CC CC ?? ?? ?? ?? DD DD DD DD               ............
        ... 빈 영역 ...
파일 끝-16  0C 00 00 00 01 00 00 00 00 00 C0 9D 28 43 C6 41   ............(C.A
```

읽는 순서는 다음과 같습니다.

1. 파일 이름 `747000000000000` 을 1,000,000으로 나누면 747000000초이고, 2001-01-01 00:00:00부터 세면 2024-09-02 20:00:00입니다 [5].
2. 0x00~0x03의 `53 45 47 42` 가 매직 `SEGB` 라서 v2 파일입니다. v1이라면 이 자리에 데이터 끝 오프셋이 오고 매직은 0x34(52)에 있습니다 [1].
3. 0x04~0x07의 `01 00 00 00` 은 기록 개수이고 LE로 읽으면 1입니다. 트레일러는 파일 끝에서 1 × 16 = 16바이트입니다.
4. 0x08~0x0F의 `00 00 00 60 28 43 C6 41` 은 파일 생성 시각이고 LE double로 읽으면 747000000.0초, 곧 2024-09-02 20:00:00입니다.
5. 0x10~0x1F는 헤더의 나머지 16바이트입니다.
6. 트레일러의 첫 4바이트 `0C 00 00 00` 은 기록 끝 오프셋 12이고 헤더 끝(0x20) 기준이라서, 기록은 0x20~0x2B에 있습니다. 앞 8바이트는 기록 헤더(CRC32와 미상 필드), 나머지 4바이트가 데이터입니다.
7. 트레일러의 다음 4바이트 `01 00 00 00` 은 상태 1(Written)입니다.
8. 트레일러의 마지막 8바이트 `00 00 C0 9D 28 43 C6 41` 은 기록 생성 시각이고 LE double로 읽으면 747000123.5초, 곧 2024-09-02 20:02:03.5입니다.

1·4·8번의 날짜는 시간대 표시가 없는 값입니다. iLEAPP처럼 UTC로 붙여 읽을지는 위 "시각 해석" 절을 따릅니다.

### 공개 도구로 한 번

ccl_segb(CCL Forensics, Alex Caithness)는 SEGB v1·v2 파일을 기록 단위로 읽는 Python 모듈이라서 [1], 스트림 해석기가 따로 없는 스트림도 기록과 상태·시각까지는 꺼내 볼 수 있습니다. 기록 데이터는 protobuf라서 정의 파일 없이 필드 번호 기준으로 풀어야 하고, iLEAPP과 mac_apt도 blackboxprotobuf로 이렇게 풉니다 [2][5].

mac_apt BIOME 플러그인(Yogesh Khatri)은 MACOS·IOS·ARTIFACTONLY 세 모드로 동작하고, 위 스트림들을 해석해 결과를 냅니다 [5]. iOS 쪽은 iLEAPP이 스트림별 모듈로 읽습니다 [2].

수집 도구로는 UAC의 Biome 수집 정의(`artifacts/files/system/biome.yaml`)와 LETHAL-FORENSICS/macos-collector의 `tools/Biome_Timeline` 이 있습니다 [6].

## 참고 문헌

1. ccl-segb (CCL Forensics, Alex Caithness) — README, ccl_segb1.py, ccl_segb2.py, ccl_segb_common.py — https://github.com/cclgroupltd/ccl-segb
2. iLEAPP — scripts/artifacts/biomeInfocus.py, biomeDKInfocus.py, biomeStreams.py, scripts/ilapfuncs.py — https://github.com/abrignoni/iLEAPP
3. Mattia Epifani, "84 Streams Later, Part 2: Inside Apple Biome" (2026-07-27) — https://blog.digital-forensics.it/2026/07/84-streams-later-part-2-inside-apple.html
4. Shai Shapira (Cellebrite), "Understanding and Decoding the Newest iOS SEGB Format" (2023-10-16) — https://cellebrite.com/en/understanding-and-decoding-the-newest-ios-segb-format/
5. mac_apt (Yogesh Khatri), plugins/biome.py v1.1 — https://github.com/ydkhatri/mac_apt/blob/master/plugins/biome.py
6. GitHub 코드 검색 "Library/Biome/streams" 결과 목록 — https://github.com/search?q=%22Library%2FBiome%2Fstreams%22&type=code
