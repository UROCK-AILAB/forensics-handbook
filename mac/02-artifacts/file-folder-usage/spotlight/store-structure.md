---
title: "색인 저장소 구조"
parent: "스포트라이트"
grand_parent: "아티팩트 · 파일·폴더 사용 흔적"
nav_order: 840
---

# 색인 저장소 구조 (.Spotlight-V100·store.db)

스포트라이트 색인은 볼륨마다 `.Spotlight-V100` 폴더에, 사용자마다 `CoreSpotlight` 폴더에 저장되고, 그 안의 `store.db` 는 SQLite가 아니라 `8tsd` 시그니처로 시작하는 자체 형식이라서 4096바이트 페이지 단위로 따라가며 읽어야 합니다.

## 무엇을 기록하나 · 왜 생기나

스포트라이트는 파일 시스템의 내용과 앱 데이터를 검색하려고 색인을 만들고 [2], 색인 저장소에는 항목마다 식별자·부모 식별자·마지막 갱신 시각과 속성 값 묶음이 레코드로 들어 있습니다 [1]. 속성 값 하나하나의 뜻은 [메타데이터 속성 (kMDItem)](metadata-attributes.md)에서 다루고, 이 페이지는 그 값이 파일 안에 어떻게 들어 있는지를 다룹니다.

공개된 형식 명세는 Mac OS X 10.7 Lion부터 macOS 13 Ventura까지를 다룹니다 [1]. macOS 14 이후에 형식이 바뀌었는지는 실제 데이터로 확인해야 합니다.

## 위치와 버전별 차이

색인 저장소는 볼륨 단위와 사용자 단위로 나뉩니다. 볼륨 단위 저장소는 볼륨 최상위의 `.Spotlight-V100` 아래 UUID 이름 폴더에 있고 [1][2][3], 사용자 단위 저장소는 macOS 10.13부터 생긴 CoreSpotlight 색인입니다 [2].

| 구분 | 경로 | 버전·비고 |
|---|---|---|
| 볼륨 단위 | `/.Spotlight-V100/Store-V2/<UUID>/` | [1][2][3] |
| 볼륨 단위(옛 형식) | `/.Spotlight-V100/Store-V1/Stores/` | [3] |
| 데이터 볼륨 | `/System/Volumes/Data/.Spotlight-V100/Store-V2/` | [3] |
| 부트 볼륨 | `/private/var/db/Spotlight-V100/BootVolume/Store-V2/<UUID>/` | 10.15 Catalina의 읽기 전용 볼륨용 [1][3] |
| 프리부트 | `/private/var/db/Spotlight-V100/Preboot` | 13 Ventura의 Preboot 볼륨용 [3] |
| 사용자 단위 | `~/Library/Metadata/CoreSpotlight/index.spotlightV3/` | 10.13 이후 [1][2][3] |
| 사용자 단위(보호 등급별) | `~/Library/Metadata/CoreSpotlight/NSFileProtectionComplete/index.spotlightV3/` 외 2개(아래) | 12 이후 [3] |
| 도움말(helpd) 색인 | `~/Library/Caches/com.apple.helpd/index.spotlightV3/` [1], `~/Library/Caches/com.apple.helpd/` 아래 보호 등급 폴더 세 곳의 `index.spotlightV3/` [3] | 보호 등급 폴더는 12 이후 [3] |

macOS 12 이후 보호 등급별 하위 폴더는 아래 세 곳입니다 [3].

```
~/Library/Metadata/CoreSpotlight/NSFileProtectionComplete/index.spotlightV3/
~/Library/Metadata/CoreSpotlight/NSFileProtectionCompleteUnlessOpen/index.spotlightV3/
~/Library/Metadata/CoreSpotlight/NSFileProtectionCompleteUntilFirstUserAuthentication/index.spotlightV3/
```

데이터 볼륨 경로에 나오는 시스템 볼륨과 데이터 볼륨의 구분은 [볼륨 그룹과 펌링크 (Volume Group·Firmlinks)](../../../01-foundations/disk-volume/volume-group-firmlinks.md)에서 설명합니다. 비교하자면 iOS의 CoreSpotlight 색인은 `/private/var/mobile/Library/Spotlight/CoreSpotlight/NSFileProtectionComplete/index.spotlightV2` 처럼 보호 등급 세 가지로 나뉜 곳에 있습니다 [2][3].

## 파일 구성

저장소 폴더의 주 파일은 `store.db` 와 `.store.db` 이고 [1], 확장자 없이 `store`, `.store` 로 있기도 합니다 [2]. 두 파일이 어떻게 다른지는 알려져 있지 않고, 헤더 플래그 가운데 일부는 `.store.db` 에서만 보입니다 [1]. mac_apt는 `.store.db` 를 처리할 때 `store.db` 에 없거나 바뀐 항목만 따로 출력합니다 [3]. 이 동작으로 보아 `.store.db` 에 `store.db` 보다 새 항목이 들어 있을 수 있습니다.

macOS 10.15부터는 데이터베이스 스트림 맵 파일이 함께 생기고, 파일 이름의 `#` 자리에 들어가는 번호가 내용을 나눕니다 [1].

```
dbStr-#.map.buckets
dbStr-#.map.data
dbStr-#.map.header
dbStr-#.map.offsets
```

| 번호 | 내용 |
|---|---|
| 1 | 메타데이터 형식 |
| 2 | 메타데이터 값 |
| 3 | 알 수 없는 값(종류 0x41) |
| 4 | 메타데이터 목록 |
| 5 | 지역화 문자열 |

iOS 색인을 읽으려면 dbStr 파일이 꼭 필요하므로 폴더를 통째로 수집합니다 [2]. 수집 방법은 [맥 증거 확보 (Acquisition)](../../../03-techniques/process-acquisition/evidence-acquisition/index.md)에서 다룹니다.

## 구조

숫자는 little-endian으로 저장하고, 파일 안의 위치는 블록 번호에 0x1000을 곱해서 구합니다(4096바이트 페이지) [1].

### store.db 파일 헤더

헤더는 파일 처음 4096바이트 안에 있고 최소 720바이트입니다 [1].

| 오프셋 | 크기 | 내용 |
|---|---|---|
| 0 | 4 | 시그니처 `8tsd`(little-endian 정수로 읽으면 "dst8") |
| 4 | 4 | 플래그 |
| 36 | 4 | 맵 오프셋 |
| 40 | 4 | 맵 크기 |
| 44 | 4 | 페이지 크기 |
| 48 | 4 | 메타데이터 속성 형식 표 블록 번호 |
| 52 | 4 | 메타데이터 속성 값 표 블록 번호 |
| 56 | 4 | 알 수 없는 표 블록 번호 |
| 60 | 4 | 메타데이터 목록 표 블록 번호 |
| 64 | 4 | 지역화 문자열 표 블록 번호 |
| 324 | 256 | 경로(뜻이 알려지지 않음) |

### 맵 페이지 헤더 (20바이트)

| 오프셋 | 크기 | 내용 |
|---|---|---|
| 0 | 4 | `1mdb` 또는 `2mbd`(little-endian으로 "dbm1"·"dbm2") |
| 4 | 4 | 페이지 크기 |
| 8 | 4 | 맵 값 개수 |

두 시그니처가 어떻게 다른지는 알려져 있지 않습니다 [1].

### 속성 표 페이지 헤더 (20바이트)

| 오프셋 | 크기 | 내용 |
|---|---|---|
| 0 | 4 | `2pbd`("dbp2") |
| 4 | 4 | 페이지 크기 |
| 8 | 4 | 사용 중인 페이지 크기 |
| 12 | 4 | 속성 표 종류 |
| 16 | 4 | 압축 풀린 페이지 크기(압축하지 않았으면 0) |

속성 표 종류 값은 아래와 같습니다 [1].

| 값 | 내용 |
|---|---|
| 0x00000009 | 데이터 레코드(zlib+DEFLATE 압축) |
| 0x00000011 | 메타데이터 속성 형식 |
| 0x00000021 | 메타데이터 속성 값 |
| 0x00000041 | 알 수 없는 값 |
| 0x00000081 | 메타데이터 목록 또는 지역화 문자열 |
| 0x00001000 | LZ4 압축 플래그 |

### 압축 표시

페이지 내용이 `\x78` 로 시작하면 zlib+DEFLATE이고, LZ4는 블록 앞머리 4바이트로 구분해서 `bv41` 은 압축한 블록, `bv4-` 는 압축하지 않은 블록, `bv4$` 는 스트림 끝입니다 [1]. LZ4 블록 헤더는 12바이트이고 0에 `bv41`(4바이트), 4에 압축 풀린 크기(4바이트), 8에 LZ4 압축 크기(4바이트)가 옵니다 [1]. spotlight_parser는 LZFSE 라이브러리도 요구하므로 [2] LZFSE로 압축한 페이지도 있을 수 있습니다. 어느 페이지인지는 실제 데이터로 확인해야 합니다. 각 압축 형식은 [압축 형식 (LZFSE·LZ4·zlib)](../../../01-foundations/value-decoding/compression.md)에서 설명합니다.

### 데이터 레코드 (종류 0x09 안)

| 오프셋 | 크기 | 내용 |
|---|---|---|
| 0 | 4 | 레코드 데이터 크기 |
| 4 | 가변 | 식별자(파일 시스템 식별자, 예: HFS의 CNID) |
| 뒤이어 | 1 | 데이터 레코드 플래그 |
| 뒤이어 | 가변 | 항목 식별자 |
| 뒤이어 | 가변 | 부모 식별자(부모 항목의 파일 시스템 식별자) |
| 뒤이어 | 가변 | 마지막 갱신 시각(1970-01-01 기준 마이크로초, UTC로 가정) |
| 뒤이어 | 가변 | 속성 배열 |

플래그 0x01은 식별자가 0인 레코드에서 보이고, 0x02·0x10·0x20·0x40은 뜻이 알려져 있지 않습니다 [1]. 레코드에는 전체 경로가 없어서 부모 식별자를 따라 올라가며 경로를 다시 만듭니다(mac_apt의 `RecursiveGetFullPath`) [3]. 부트 볼륨 저장소는 이 식별자와 부모 식별자가 big-endian입니다 [3].

### 메타데이터 속성 형식 항목 (종류 0x11)

속성 이름과 그 값의 형식을 정하는 항목입니다 [1].

| 오프셋 | 크기 | 내용 |
|---|---|---|
| 0 | 4 | 표 인덱스 |
| 4 | 1 | 값 형식 |
| 5 | 1 | 속성 형식 |
| 6 | 가변 | 키 이름(UTF-8) |

값 형식 필드는 아래 값 가운데 하나입니다 [1].

| 값 | 형식 |
|---|---|
| 0x00 | 불리언(가변 크기 정수) |
| 0x07 | 가변 크기 정수 |
| 0x09 | 32비트 실수 |
| 0x0a | 64비트 실수 |
| 0x0b | 문자열(UTF-8, NULL로 끝남) |
| 0x0c | 날짜·시각(64비트 실수, Cocoa 시각) |
| 0x0e | 바이너리 |
| 0x0f | 속성 값 또는 목록 참조 |

### dbStr-#.map.header (56바이트)

| 오프셋 | 크기 | 내용 |
|---|---|---|
| 0 | 8 | 시그니처 `\x00PataD\x00\x00` |
| 20 | 4 | `dbStr-#.map.data` 크기 |
| 24 | 4 | 버킷 개수 |
| 28 | 4 | 오프셋 개수 |

## 시각 해석

한 저장소 안에 기준이 다른 시각 두 가지가 섞여 있습니다 [1]. 속성 값 가운데 값 형식이 0x0c인 날짜는 2001-01-01 기준 초를 64비트 실수로 적은 Cocoa 시각(맥 절대 시각)이고, 레코드 앞머리의 마지막 갱신 시각은 1970-01-01 기준 마이크로초라서 유닉스 시각입니다. 레코드 갱신 시각은 UTC로 읽습니다 [1][3]. 두 기준을 섞어 계산하면 31년가량 어긋나거나 단위가 백만 배 달라지니, 값을 읽을 때 어느 필드에서 나온 값인지 먼저 확인합니다. 두 시각 체계는 [맥의 시각 값 (Mac Absolute Time·Unix·HFS)](../../../01-foundations/value-decoding/mac-time-values.md)에서 자세히 다룹니다.

레코드 갱신 시각은 색인 항목이 마지막으로 갱신된 때를 가리키고, 파일을 연 시각이나 고친 시각과 같은 뜻이 아닙니다. 사용과 관련된 날짜는 속성 값 쪽에 따로 있고, 그 뜻은 [메타데이터 속성 (kMDItem)](metadata-attributes.md)에서 설명합니다.

## 증거로서 의미

### 증명하는 것

색인 레코드는 이 볼륨이나 사용자 색인에 어떤 식별자와 부모 식별자의 항목이 기록돼 있었고, 그 항목에 어떤 속성 값이 붙어 있었으며, 색인이 그 항목을 언제 마지막으로 갱신했는지 보여 줍니다. 부모 식별자로 경로를 다시 만들면 항목이 어느 폴더 아래에 있었는지도 알 수 있습니다 [3].

### 증명하지 못하는 것

레코드 갱신 시각만으로는 사용자가 무엇을 했는지 말할 수 없습니다. 레코드 갱신은 색인 쪽 동작이라서 누가 파일을 열었다거나 고쳤다는 뜻으로 읽지 않습니다. 파일이 지금 디스크에 없는데 색인에만 남아 있는 경우가 있을 수 있지만, 지운 파일의 항목이 언제까지 남는지는 정해져 있지 않으므로 "지운 뒤에도 반드시 남는다" 고 보지 않습니다.

## 함정과 한계

`store.db` 와 `.store.db` 의 차이가 밝혀지지 않았고, 도구마다 두 파일을 다루는 방식도 다를 수 있습니다. mac_apt처럼 `.store.db` 에서 새로 생기거나 바뀐 항목만 뽑는 도구를 쓰면 두 파일에 똑같이 있는 항목은 한 번만 보입니다 [3]. 명세의 확인 범위가 Ventura까지라서 [1] 그 뒤 버전을 분석할 때는 도구 결과가 비거나 일부만 나오는지 먼저 확인합니다.

사용자 단위 CoreSpotlight 색인은 보호 등급 이름이 붙은 폴더로 나뉘어 있어서 [3], 한 폴더만 수집하면 나머지 등급의 색인을 놓칩니다. mac_apt는 `NSFileProtectionComplete` 와 `NSFileProtectionCompleteUnlessOpen` 폴더의 `.store.db` 는 암호화돼 있을 것으로 보고 시그니처가 맞지 않으면 건너뜁니다 [3]. 이 폴더에서 `8tsd` 시그니처가 보이지 않으면 파일이 망가졌다고 단정하지 말고 보호 등급에 따른 암호화부터 의심합니다. 부트 볼륨 저장소는 식별자 바이트 순서가 다르므로 [3] 직접 파싱할 때 따로 처리합니다.

색인은 `mdutil` 명령으로 켜고 끄고 지울 수 있습니다 [4].

| 옵션 | 동작 |
|---|---|
| `-i on`, `-i off` | 색인 상태 설정 |
| `-E` | 볼륨의 로컬 저장소 지움 |
| `-s` | 색인 상태 표시 |
| `-a` | 모든 볼륨에 적용 |
| `-p` | 네트워크 장치 캐시 비움 |
| `-v` | 자세히 출력 |

`-E` 나 `-i off` 는 색인 흔적을 없애는 동작이라서, 저장소가 비었거나 색인이 꺼져 있으면 그 자체를 확인할 사항으로 봅니다. 이 명령을 실행한 흔적이 어디에 남는지는 실제 데이터로 확인해야 하고, 다른 흔적과 함께 보는 방법은 [증거를 없애려 했나 (Anti-Forensics)](../../../04-scenarios/activity/anti-forensics/index.md)에서 다룹니다.

## 직접 분석해 보기

### 헥스로 한 번

아래 바이트는 실제 데이터가 아니라 명세 [1]에 맞춰 만든 예시입니다. `FL` 은 플래그, `MO`·`MS`·`PS` 는 맵 오프셋·맵 크기·페이지 크기, `B2`~`B5` 는 속성 값·알 수 없는 표·목록·지역화 문자열 표의 블록 번호 자리이고, `??` 는 뜻이 알려지지 않은 필드입니다.

```
오프셋  00 01 02 03 04 05 06 07 08 09 0A 0B 0C 0D 0E 0F
000000  38 74 73 64 FL FL FL FL ?? ?? ?? ?? ?? ?? ?? ??   8tsd............
000010  ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ??   ................
000020  ?? ?? ?? ?? MO MO MO MO MS MS MS MS PS PS PS PS   ................
000030  02 00 00 00 B2 B2 B2 B2 B3 B3 B3 B3 B4 B4 B4 B4   ................
000040  B5 B5 B5 B5 ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ??   ................
```

1. 0x00~0x03의 `38 74 73 64` 는 시그니처 `8tsd` 라서 스포트라이트 저장소 파일입니다.
2. 0x24·0x28·0x2C에서 맵 오프셋·맵 크기·페이지 크기를 각각 uint32 LE로 읽습니다.
3. 0x30~0x33의 `02 00 00 00` 은 메타데이터 속성 형식 표의 블록 번호 2이고, 0x1000을 곱하면 파일 오프셋 0x2000입니다.

0x2000으로 가면 속성 표 페이지 헤더가 나옵니다. 이 예시도 명세로 만든 것이고 `PS` 는 페이지 크기, `UU` 는 사용 중인 페이지 크기 자리입니다.

```
오프셋  00 01 02 03 04 05 06 07 08 09 0A 0B 0C 0D 0E 0F
002000  32 70 62 64 PS PS PS PS UU UU UU UU 11 00 00 00   2pbd............
002010  00 00 00 00 ...
```

4. 0x2000~0x2003의 `32 70 62 64` 는 `2pbd` 라서 속성 표 페이지입니다.
5. 0x200C~0x200F의 `11 00 00 00` 은 종류 0x11이라서 메타데이터 속성 형식 항목이 이어집니다.
6. 0x2010~0x2013이 0이라서 이 페이지는 압축하지 않았습니다. 0x2014부터 12바이트는 속성 표 헤더(다음 블록 오프셋 4바이트, 뜻을 모르는 8바이트)이고, 그 뒤 0x2020부터 첫 항목(표 인덱스 4바이트, 값 형식 1바이트, 속성 형식 1바이트, 키 이름)이 이어집니다 [1].

종류가 0x09인 데이터 레코드 페이지는 압축돼 있어서, 헤더 뒤가 `78` 이면 zlib으로, `bv41` 이면 LZ4로 먼저 풀고 나서 레코드를 읽습니다 [1].

### 공개 도구로 한 번

spotlight_parser(Yogesh Khatri, GPL v3)는 Python 3.7 이상에서 돌고 lz4와 pyliblzfse 라이브러리가 필요하며, 결과를 텍스트로 냅니다 [2]. SQLite 출력 같은 기능이 필요하면 mac_apt를 씁니다 [2]. mac_apt의 SPOTLIGHT 플러그인은 사용자·볼륨·iOS 색인을 읽고 [3], 위 표의 경로들을 스스로 찾아 들어가며 부모 식별자로 전체 경로를 다시 만듭니다.

## 교차 검증

색인 레코드에서 뽑은 경로와 시각은 다른 흔적과 맞춰 봐야 뜻이 분명해집니다. 경로가 바뀌거나 지워진 기록은 [파일 시스템 이벤트 (FSEvents)](../../filesystem/fsevents/index.md)에서, 문서를 연 기록은 [최근 항목 (Shared File Lists)](../recent-items/index.md)에서 찾고, 사용자가 검색창에서 무엇을 쳤는지는 [검색 기록 (Spotlight Shortcuts)](search-history.md)에서 봅니다. 여러 기록을 한 시간축에 놓는 방법은 [타임라인 작성 (Timeline)](../../../03-techniques/analysis/timeline/index.md)에 있습니다.

## 실습

macOS 공개 시험 데이터(NIST CFReDS 등)에서 아래 질문을 풀어 봅니다.

1. 분석 대상의 macOS 버전을 먼저 확인하고, 위 표의 경로 가운데 실제로 있는 저장소 폴더를 모두 찾습니다.
2. `store.db` 의 첫 4바이트가 `8tsd` 인지 보고, 헤더에서 첫 속성 표 블록 번호를 읽어 해당 페이지의 종류 값을 확인합니다.
3. 같은 폴더의 `.store.db` 를 도구로 읽었을 때 `store.db` 와 비교해 새로 나오는 항목이 있는지 봅니다.
4. 한 항목의 레코드 갱신 시각(유닉스 마이크로초)과 속성 값 속 날짜(Cocoa 시각)를 각각 UTC로 바꿔 나란히 적어 봅니다.

## 참고 문헌

1. Apple Spotlight store database file format (libyal/dtformats, Joachim Metz, 0.0.3, 2024-01) — https://raw.githubusercontent.com/libyal/dtformats/main/documentation/Apple%20Spotlight%20store%20database%20file%20format.asciidoc
2. spotlight_parser README (Yogesh Khatri) — https://github.com/ydkhatri/spotlight_parser
3. mac_apt 플러그인 spotlight.py — https://raw.githubusercontent.com/ydkhatri/mac_apt/master/plugins/spotlight.py
4. SS64, mdutil — https://ss64.com/mac/mdutil.html
