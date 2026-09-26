---
title: "캐시와 웹 데이터"
parent: "사파리"
grand_parent: "아티팩트 · 인터넷·브라우저"
nav_order: 1190
---

# 캐시와 웹 데이터 (Cache·WebKit)

사파리가 웹 페이지를 불러오면서 남기는 캐시 DB `Cache.db`, 쿠키 파일 `Cookies.binarycookies`, 웹 아이콘 DB, 사이트별 설정 DB 는 방문 기록과 따로 저장되고, 그중 쿠키 파일은 형식이 공개돼 있어서 도메인마다 쿠키가 만들어진 시각과 만료 시각을 헥스로 직접 읽을 수 있습니다.

## 무엇을 기록하나

이 페이지의 파일들은 사용자가 무엇을 봤는지 적으려고 만든 기록이 아니라, 페이지를 빨리 다시 불러오고 로그인 상태나 사이트 설정을 이어 가려고 사파리와 WebKit 이 쌓아 두는 데이터입니다. 방문 기록과 따로 저장되는 만큼 기록 지우기 뒤에 무엇이 남는지도 파일마다 따로 따져야 합니다(아래 "함정과 한계").

## 위치

위치는 아래와 같습니다 [1]. 캐시와 쿠키는 옛 위치와 사파리 샌드박스 컨테이너 위치 두 곳에 있을 수 있어서 둘 다 확인합니다.

| 파일 | 위치 [1] |
|---|---|
| 캐시 DB | `~/Library/Caches/com.apple.Safari/Cache.db` (+ `-wal`) |
| 캐시 DB(컨테이너) | `~/Library/Containers/com.apple.Safari/Data/Library/Caches/com.apple.Safari/Cache.db` (+ `-wal`) |
| 쿠키 | `~/Library/Cookies/Cookies.binarycookies` |
| 쿠키(컨테이너) | `~/Library/Containers/com.apple.Safari/Data/Library/Cookies/Cookies.binarycookies` |
| 웹 아이콘 | `~/Library/Safari/Favicon Cache/favicons.db` (+ `-wal`) |
| 터치 아이콘 | `~/Library/Safari/Touch Icons Cache/TouchIconCacheSettings.db` (+ `-wal`) |
| 사이트별 설정 | `~/Library/Safari/PerSitePreferences.db` (+ `-wal`) |

`Cache.db`, `favicons.db`, `TouchIconCacheSettings.db`, `PerSitePreferences.db` 는 SQLite 이지만 안의 표와 열 이름, 캐시 본문이 따로 저장되는 폴더는 실제 데이터로 확인해야 합니다. SQLite 파일을 여는 법은 [SQLite 데이터베이스 (SQLite)](../../../01-foundations/data-formats/sqlite/index.md)에서 다룹니다. LocalStorage·IndexedDB 같은 WebKit 웹사이트 데이터의 위치도 실제 데이터로 확인하고, 형식 일반은 [LevelDB와 IndexedDB (LevelDB·IndexedDB)](../../../01-foundations/data-formats/leveldb-indexeddb.md)에 있습니다.

## 구조 — Cookies.binarycookies

### 파일 머리

| 오프셋 | 크기 | 내용 | 바이트 순서 |
|---|---|---|---|
| 0 | 4 | 시그니처 `cook` | — |
| 4 | 4 | 페이지 수 | big-endian |
| 8 | 4 × 페이지 수 | 페이지마다의 크기 | big-endian |

머리 뒤에 페이지가 이어지고, 파일 맨 끝 8바이트는 뜻이 밝혀지지 않았습니다(체크섬으로 추정) [2].

### 페이지

| 오프셋 | 크기 | 내용 |
|---|---|---|
| 0 | 4 | 페이지 시그니처 `00 00 01 00` |
| 4 | 4 | 쿠키 수 |
| 8 | 4 × 쿠키 수 | 쿠키 레코드 오프셋 배열(little-endian) |

페이지는 머리, 쿠키 레코드 배열, 4바이트 `00 00 00 00` 꼬리로 나뉩니다 [2]. 이 4바이트가 페이지 안 어디에 오는지와 레코드 오프셋을 어디서부터 세는지는 알려져 있지 않습니다.

### 쿠키 레코드

레코드 안의 숫자는 little-endian 입니다 [2].

| 오프셋 | 크기 | 내용 |
|---|---|---|
| 0 | 4 | 레코드 크기 |
| 8 | 4 | 플래그. `0x1` = Secure, `0x4` = HttpOnly |
| 16 | 4 | URL(도메인) 문자열 오프셋 |
| 20 | 4 | 이름 문자열 오프셋 |
| 24 | 4 | 경로 문자열 오프셋 |
| 28 | 4 | 값 문자열 오프셋 |
| 40 | 8 | 만료 시각(double) |
| 48 | 8 | 생성 시각(double) |
| 56 | 가변 | URL·이름·경로 문자열과 값 데이터 |

네 문자열 오프셋은 레코드 시작부터 센 값입니다 [2]. 오프셋 4, 12 와 값이 0 인 32~39 의 뜻은 알려져 있지 않고, 플래그 `0x2` 의 뜻도 밝혀지지 않았습니다 [2]. 두 시각은 맥 절대 시각, 곧 2001-01-01 00:00:00 UTC 부터 흐른 초를 double 로 적은 값입니다 [2].

## 증거로서 의미

**증명하는 것.** 쿠키 레코드가 있으면 그 도메인·경로의 이름이 붙은 쿠키가 이 파일에 저장돼 있고, 생성 시각에 만들어져 만료 시각까지 유효하도록 설정됐다는 뜻입니다 [2]. 플래그로 Secure·HttpOnly 여부를 알 수 있습니다 [2]. 방문 기록을 지운 기기에서도 쿠키의 도메인과 생성 시각은 어느 사이트와 언제 주고받았는지를 짐작하는 단서가 될 수 있습니다. 다만 기록 지우기가 쿠키도 지우는지는 실제 기기로 확인해야 합니다.

**증명하지 못하는 것.** 쿠키의 도메인은 사용자가 주소창에 연 사이트가 아닐 수 있습니다. 한 페이지가 다른 도메인의 자원을 불러오면 그 도메인의 쿠키가 생길 수 있어서, 쿠키 도메인 목록을 방문한 사이트 목록으로 쓰지 않습니다. 쿠키의 값은 사이트가 정한 것이라 그 뜻을 이 파일만으로 풀 수 없고, 값에 인증 정보가 들어 있을 수 있으니 보고서와 작업 기록에 값을 그대로 옮기지 않습니다.

`favicons.db` 와 스냅샷처럼 기록 지우기가 지우는 데이터가 남아 있다면 [3], 그 뒤에 새로 쌓인 것인지 지우기가 없었던 것인지를 방문 기록과 함께 따져 봅니다.

## 시각 해석

쿠키의 생성 시각과 만료 시각은 모두 맥 절대 시각 double 이고 UTC 기준입니다 [2]. 생성 시각은 그 쿠키가 만들어진 때이고, 사이트가 같은 이름의 쿠키를 새로 써 준 뒤에 이 값이 어떻게 바뀌는지는 실제 데이터로 확인해야 합니다. 유닉스 시각으로 바꾸려면 978307200 을 더하고, 시각 값 전반은 [맥의 시각 값 (Mac Absolute Time·Unix·HFS)](../../../01-foundations/value-decoding/mac-time-values.md)을 봅니다.

## 함정과 한계

**기록 지우기의 범위가 파일마다 다릅니다.** 기록 지우기는 웹페이지 아이콘과 열린 페이지 스냅샷을 지웁니다 [3]. 캐시 파일 자체와 쿠키를 지우는지는 공개 자료가 없어서, 이 페이지의 파일이 남아 있다는 사실만으로 "기록을 지우지 않았다" 고 쓰지 않습니다. 지우기 대상 전체는 [방문 기록 (History.db)](history.md)에 정리했습니다.

**개인 정보 보호 브라우징의 쿠키는 남지 않습니다.** 개인 정보 보호 브라우징에서는 쿠키와 웹사이트 데이터의 변경을 저장하지 않습니다 [4]. 나머지 동작은 [개인 정보 보호 브라우징 (Private Browsing)](private-browsing.md)에서 다룹니다.

**쿠키 파일이 두 곳에 있을 수 있습니다.** 옛 위치와 컨테이너 위치의 파일을 모두 읽고, 같은 쿠키가 양쪽에 있으면 생성 시각을 비교해 어느 쪽이 나중에 쓰였는지 봅니다.

## 직접 분석해 보기

### 헥스로 따라가기

아래는 형식 문서 [2]의 구조에 맞춰 만든 예시이고, 실제 기기에서 나온 값이 아닙니다. 쿠키 한 개가 든 페이지 한 개짜리 파일입니다. 문자열 오프셋은 형식 문서대로 레코드 시작 기준으로 세었고, 문서에 적혀 있지 않은 두 가지(레코드 오프셋은 페이지 시작 기준, 4바이트 `00 00 00 00` 은 레코드 오프셋 배열 바로 뒤)는 예시를 만들려고 정한 것이라 실제 파일에서 확인합니다. 아래 코드는 레코드 오프셋 배열로 레코드를 찾아서 이 4바이트의 자리에 기대지 않습니다.

```text
파일 머리 (big-endian)
00000000  63 6F 6F 6B                 "cook"
00000004  00 00 00 01                 페이지 수 = 1
00000008  00 00 00 70                 1번 페이지 크기 = 0x70 (112)

페이지 (파일 오프셋 0x0C 부터, 아래 오프셋은 페이지 기준)
+00  00 00 01 00                      페이지 시그니처
+04  01 00 00 00                      쿠키 수 = 1
+08  10 00 00 00                      1번 레코드 오프셋 = 0x10
+0C  00 00 00 00                      00 00 00 00 (자리는 예시로 정함)

쿠키 레코드 (페이지 +0x10 부터, 아래 오프셋은 레코드 기준, little-endian)
+00  60 00 00 00                      레코드 크기 = 0x60 (96)
+04  00 00 00 00                      뜻 모름
+08  05 00 00 00                      플래그 = 0x5 → Secure(0x1) + HttpOnly(0x4)
+0C  00 00 00 00                      뜻 모름
+10  38 00 00 00                      URL 오프셋 = 0x38
+14  48 00 00 00                      이름 오프셋 = 0x48
+18  50 00 00 00                      경로 오프셋 = 0x50
+1C  58 00 00 00                      값 오프셋 = 0x58
+20  00 00 00 00 00 00 00 00          뜻 모름(값 0)
+28  00 00 00 C0 1D C8 C8 41          만료 = 831536000.0 → 2027-05-09 06:13:20 UTC
+30  00 00 00 00 84 D7 C7 41          생성 = 800000000.0 → 2026-05-09 06:13:20 UTC
+38  ...                              URL·이름·경로·값 문자열

파일 끝 8바이트                        뜻 모름(체크섬 추정)
```

페이지 크기 0x70 은 페이지 머리와 4바이트 `00 00 00 00` 을 합한 16바이트에 레코드 96바이트를 더한 값입니다. 시각 double 은 little-endian 이라서 바이트를 거꾸로 읽어 `41 C7 D7 84 00 00 00 00` 을 IEEE 754 double 로 풀면 800000000.0 이 되고, 2001-01-01 00:00:00 UTC 에 800000000 초를 더하면 2026-05-09 06:13:20 UTC 입니다.

### 코드로 읽기

아래 파이썬 코드는 위 구조를 그대로 옮긴 것입니다. 문자열이 어디서 끝나는지는 알려져 있지 않아서, 문자열 오프셋을 정렬해 다음 문자열 시작(마지막은 레코드 끝)까지를 한 문자열로 보고 끝의 NUL 바이트를 떼어 냅니다.

```python
import datetime
import struct

EPOCH = datetime.datetime(2001, 1, 1, tzinfo=datetime.timezone.utc)

def cocoa(sec):
    return EPOCH + datetime.timedelta(seconds=sec)

def read_cookies(path):
    with open(path, "rb") as f:
        data = f.read()
    assert data[:4] == b"cook"
    npages = struct.unpack(">I", data[4:8])[0]
    sizes = struct.unpack(">%dI" % npages, data[8:8 + 4 * npages])
    pos = 8 + 4 * npages
    for size in sizes:
        page = data[pos:pos + size]
        pos += size
        assert page[:4] == b"\x00\x00\x01\x00"
        count = struct.unpack("<I", page[4:8])[0]
        for off in struct.unpack("<%dI" % count, page[8:8 + 4 * count]):
            rec_size = struct.unpack("<I", page[off:off + 4])[0]
            rec = page[off:off + rec_size]
            flags = struct.unpack("<I", rec[8:12])[0]
            str_offs = struct.unpack("<4I", rec[16:32])   # URL, 이름, 경로, 값
            expires, created = struct.unpack("<2d", rec[40:56])
            bounds = sorted(set(str_offs)) + [rec_size]
            def text(o):
                end = bounds[bounds.index(o) + 1]
                return rec[o:end].rstrip(b"\x00").decode("utf-8", "replace")
            url, name, cpath, value = (text(o) for o in str_offs)
            yield url, name, cpath, flags, cocoa(created), cocoa(expires)

for row in read_cookies("Cookies.binarycookies"):
    print(*row, sep=" | ")
```

값(`value`)은 인증 정보일 수 있어서 출력에서 뺐습니다. 공개 파서를 쓸 때도 위 예시 파일처럼 값을 아는 입력으로 결과를 먼저 맞춰 봅니다. 방법은 [도구 검증 (Tool Validation)](../../../03-techniques/reporting/tool-validation.md)에 있습니다.

## 교차 검증

| 함께 볼 것 | 이유 |
|---|---|
| [방문 기록 (History.db)](history.md) | 쿠키 도메인의 방문 기록과 시각 |
| [탭과 세션 (Tabs·Sessions)](tabs-sessions.md) | 탭 스냅샷, 열려 있던 탭 |
| [개인 정보 보호 브라우징 (Private Browsing)](private-browsing.md) | 쿠키가 남지 않는 경우 |
| [콘텐츠 검색 (Content Search)](../../../03-techniques/analysis/content-search.md) | 캐시 파일 안에서 주소·문자열 찾기 |
| [웹 사용 행위 재구성 (Web Activity)](../../../04-scenarios/activity/web-activity.md) | 브라우저 흔적을 묶어 읽는 순서 |

## 실습

공개 맥 시험 이미지에서 이 페이지의 파일을 모아 아래 질문을 풀어 봅니다.

1. `Cookies.binarycookies` 가 옛 위치와 컨테이너 가운데 어디에 있고, 페이지 수와 쿠키 수는 몇 개인가
2. 생성 시각이 가장 이른 쿠키와 가장 늦은 쿠키의 도메인은 무엇이고, 방문 기록에 같은 도메인이 있는가
3. Secure 와 HttpOnly 가 둘 다 켜진 쿠키는 몇 개인가
4. `Cache.db` 를 SQLite 로 열어 표 목록을 적고, 방문 기록의 주소가 들어 있는 표가 있는지 찾아보라

## 참고 문헌

1. ForensicArtifacts 정의 파일 webbrowser.yaml — https://raw.githubusercontent.com/ForensicArtifacts/artifacts/main/artifacts/data/webbrowser.yaml
2. libyal dtformats — Safari Cookies (binarycookies) format — https://github.com/libyal/dtformats/blob/main/documentation/Safari%20Cookies.asciidoc
3. Apple Support, Safari 사용 설명서(Mac) — Clear your browsing history in Safari on Mac — https://support.apple.com/guide/safari/clear-your-browsing-history-sfri47acf5d6/mac
4. Apple Support, Safari 사용 설명서(Mac) — Browse privately in Safari on Mac — https://support.apple.com/guide/safari/browse-privately-ibrw1069/mac
