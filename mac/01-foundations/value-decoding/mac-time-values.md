---
title: "맥의 시각 값"
parent: "기반 · 값 읽는 법"
nav_order: 300
---

# 맥의 시각 값 (Mac Absolute Time·Unix·HFS)

## 한 줄 요약

맥의 시각 값은 2001년, 1970년, 1904년 가운데 어느 날을 기준으로 삼는지와 단위(초·나노초·1/65536초)가 저장 형식마다 달라서, 값 하나를 읽을 때마다 기준 시각과 단위부터 정하고 상수 하나로 유닉스 시각에 맞춰 바꿔야 합니다.

## 이 형식을 쓰는 아티팩트

이 페이지에서 원문으로 확인한 곳은 아래 다섯 가지입니다.

| 이름 | 기준 시각 | 단위·형식 | 쓰는 곳 | 구조 페이지 |
|---|---|---|---|---|
| 맥 절대 시각 (CFAbsoluteTime) | 2001-01-01 00:00:00 | 초, 실수 (CFTimeInterval) | Core Foundation·Foundation 날짜, 북마크 데이터의 날짜 | [파일 참조 데이터](alias-bookmark.md) |
| APFS 시각 | 1970-01-01 00:00 UTC | 나노초, uint64 | APFS 의 모든 시각 필드 | [APFS 구조](../disk-volume/apfs/index.md) |
| HFS+ 시각 | 1904-01-01 00:00 GMT | 초, UInt32 | HFS+ 파일 시스템 (볼륨 헤더 createDate 만 현지 시각) | [HFS+ 구조](../disk-volume/hfs-plus.md) |
| Alias v2 날짜 | 1904-01-01 00:00:00 UTC | 초, 4바이트 | Alias 레코드 | [파일 참조 데이터](alias-bookmark.md) |
| Alias v3 날짜 | 1904-01-01 00:00:00 UTC | 1/65536초, 8바이트 | Alias 레코드 | [파일 참조 데이터](alias-bookmark.md) |

plist·SQLite 안에 저장한 날짜, 메시지·크롬 계열 브라우저·격리 속성의 시각, 통합 로그의 시각이 어느 기준을 쓰는지는 이 페이지에서 확인하지 않았습니다. 해당 형식은 [속성 목록 파일](../data-formats/plist/index.md), [SQLite 데이터베이스](../data-formats/sqlite/index.md), [통합 로그 형식](../data-formats/unified-log/index.md) 과 각 아티팩트 페이지에서 다룹니다.

macOS 버전에 따라 기준 시각이 바뀐다는 자료는 찾지 못했고, 차이는 버전보다 파일 시스템(HFS+ 인지 APFS 인지)과 저장 형식에서 생깁니다.

## 구조

### 맥 절대 시각

Apple 의 Core Foundation 공개 소스(CFDate.h)는 절대 시각을 기준 날짜 "00:00:00 1 January 2001" 부터 흐른 시간 간격으로 정의하고, 자료형은 초 단위 실수인 CFTimeInterval 입니다. 같은 소스의 CFDate.c 에는 다른 기준 시각과의 차이가 상수로 들어 있습니다.

| 상수 | 값 (초) | 쓰임 |
|---|---|---|
| `kCFAbsoluteTimeIntervalSince1970` | 978307200.0 | 맥 절대 시각 + 이 값 = 유닉스 시각 |
| `kCFAbsoluteTimeIntervalSince1904` | 3061152000.0 | 1904 기준 시각과 2001 기준 시각의 차이 |

`CFAbsoluteTimeGetCurrent` 는 `gettimeofday` 로 얻은 유닉스 초에서 `kCFAbsoluteTimeIntervalSince1970` 을 빼서 현재 맥 절대 시각을 만들고, 마이크로초는 초로 바꿔 더합니다. 유닉스 시각과 상수 하나만큼 차이 나는 값이라서 덧셈 한 번으로 바꿀 수 있습니다. 두 상수로 계산하면 1904 기준 시각과 유닉스 시각의 차이는 3061152000 − 978307200 = 2082844800 초입니다.

CFDate.c 의 저작권 표기는 1998-2014 이고, 최신 macOS 에 들어간 비공개 구현이 이 소스와 같은지는 확인하지 못했습니다. 상수 값은 기준 날짜 두 개 사이의 거리를 적은 정의값이라 바뀔 이유가 없다고 봅니다(필자 판단). CFDate.h 주석에는 GMT·UTC 라는 말이 없고, 맥 절대 시각이 윤초를 반영하는지도 확인하지 못했습니다.

### APFS 시각

Apple File System Reference(2020-06-22 판)는 APFS 시각을 `uint64_t` 로 두고 "1970년 1월 1일 0:00 UTC 부터 흐른 나노초, 윤초는 무시" 로 정의합니다. 이 형식을 쓰는 필드는 아래와 같습니다.

| 구조체 | 필드 | 뜻 |
|---|---|---|
| 아이노드 `j_inode_val_t` | `create_time` | 만든 시각 |
| | `mod_time` | 내용을 마지막으로 수정한 시각 |
| | `change_time` | 속성(attributes)을 마지막으로 바꾼 시각 |
| | `access_time` | 마지막 접근 시각, 갱신 방식은 `APFS_FEATURE_STRICTATIME` 에 따름 |
| 디렉터리 항목 `j_drec_val_t` | `date_added` | 항목이 그 폴더에 들어온 시각 |
| 볼륨 슈퍼블록 | `apfs_unmount_time` | 마지막으로 마운트를 해제한 시각 |
| | `apfs_last_mod_time` | 볼륨을 마지막으로 수정한 시각 |
| `apfs_modified_by_t` | `timestamp` | 볼륨을 수정한 소프트웨어를 기록한 시각 |
| 스냅숏 메타데이터 | `create_time`, `change_time` | 스냅숏을 만든 시각, 바꾼 시각 |

`apfs_modified_by[]` 배열은 가장 최근 기록이 0번에 오고, `apfs_formatted_by` 는 볼륨을 만들 때 한 번만 기록합니다.

### HFS+ 시각

Technical Note TN1150 은 HFS+ 날짜를 부호 없는 32비트 정수(`UInt32`)로 두고 "1904년 1월 1일 자정 GMT 부터 흐른 초" 로 정의합니다. 윤초는 넣지 않고, 4로 나누어떨어지는 해마다 윤일을 넣습니다. 32비트라서 표현할 수 있는 마지막 시각은 2040-02-06 06:28:15 GMT 입니다.

HFS+ 이전의 옛 HFS 는 같은 값을 현지 시각으로 저장했고, HFS+ 에서도 볼륨 헤더의 `createDate` 하나만은 현지 시각으로 저장합니다. TN1150 은 그 이유로, 백업 도구 등이 볼륨 생성일을 볼륨을 알아보는 값처럼 쓰는데 GMT 로 두면 시간대나 서머타임 설정이 바뀔 때 값이 달라 보인다는 점을 듭니다.

### Alias 레코드와 북마크의 날짜

Alias 레코드는 전체가 빅엔디언이고, v2 는 볼륨 날짜와 대상 생성 날짜를 1904-01-01 00:00:00 UTC 기준 초(4바이트)로, v3 는 같은 기준의 1/65536초(8바이트)로 적습니다. 북마크 데이터는 나머지 필드가 리틀엔디언인데 날짜(형식 코드 0x0400)만 빅엔디언 IEEE double 이고, 값은 2001-01-01 00:00:00 UTC 기준 초, 곧 맥 절대 시각입니다. 두 형식의 UTC 기준은 mac_alias 문서가 적은 것이고, Apple 문서로는 확인하지 못했습니다. 두 형식에서 날짜가 놓이는 자리는 [파일 참조 데이터](alias-bookmark.md)에 정리했습니다.

## 읽는 법

값을 만나면 먼저 기준과 단위를 정하고 아래 식으로 유닉스 초(UTC)로 바꿉니다.

| 원래 값 | 유닉스 초로 바꾸는 식 |
|---|---|
| 맥 절대 시각 (초, 실수) | 값 + 978307200 |
| APFS 시각 (나노초) | 값 ÷ 1,000,000,000 |
| HFS+ 시각, Alias v2 날짜 (1904 기준 초) | 값 − 2082844800 |
| Alias v3 날짜 (1904 기준 1/65536초) | 값 ÷ 65536 − 2082844800 |

HFS+ 볼륨 헤더의 `createDate` 는 이 식으로 바꾼 결과가 UTC 가 아니라 그 맥의 현지 시각이라서, 시간대를 따로 확인해야 합니다. 시간대 설정은 [시간대와 시계 설정](../../02-artifacts/system-account/time-zone.md)에서 다룹니다.

아래 헥스는 명세로 만든 예시이고, 특정 검체에서 나온 값이 아닙니다. 세 값 모두 2023-03-08 20:26:40 UTC 를 가리키도록 계산했습니다.

```text
북마크 날짜 (형식 코드 0x0400, 빅엔디언 double, 맥 절대 시각)
41 C4 DC 93 80 00 00 00   → 700000000.0 초
                          → 700000000 + 978307200 = 1678307200 (유닉스 초)
                          → 2023-03-08 20:26:40 UTC

Alias v2 대상 생성 날짜 (빅엔디언 4바이트, 1904 기준 초)
E0 2E A0 00               → 3761152000 초
                          → 3761152000 − 2082844800 = 1678307200 (유닉스 초)
                          → 2023-03-08 20:26:40 UTC

APFS 시각 (나노초, 10진수로 적음)
1678307200123456789       → 1678307200.123456789 초 (유닉스 초)
                          → 2023-03-08 20:26:40.123456789 UTC
```

맥 절대 시각 0 은 2001-01-01 00:00:00 이고 유닉스 초로는 978307200 이라서, 도구 결과를 검산할 때 이 한 쌍을 먼저 넣어 봅니다.

## 포렌식에서 중요한 점

APFS 디렉터리 항목의 `date_added` 는 항목이 그 폴더에 들어온 시각이고, 같은 폴더 안에서 이름만 바꾸면 갱신되지 않습니다. 파일을 만든 시각이나 내용을 고친 시각과 따로 놀 수 있어서, 파일이 언제 이 폴더로 옮겨졌는지 가늠할 때 씁니다(필자 판단). 명세 문장이 "다른 폴더로 옮기지 않고 이름을 바꾸는 경우" 를 들고 있어 다른 폴더로 옮기면 갱신된다고 읽히지만, 이 동작은 확인하지 못했습니다.

아이노드의 네 시각은 바뀌는 계기가 서로 다릅니다. `mod_time` 은 내용을 고칠 때, `change_time` 은 속성을 바꿀 때 달라지고, `access_time` 은 `APFS_FEATURE_STRICTATIME` 설정에 따라 갱신 방식이 달라서 접근 시각이 오래돼 보여도 그동안 열지 않았다고 말할 수 없습니다. 볼륨 슈퍼블록의 `apfs_unmount_time`·`apfs_last_mod_time` 과 `apfs_modified_by[]` 기록은 볼륨을 어느 소프트웨어가 언제 마지막으로 만졌는지 보여 주고, 스냅숏의 `create_time` 은 [스냅숏과 백업 비교](../../03-techniques/analysis/snapshot-diff.md)에서 비교 기준점이 됩니다.

HFS+ 로 포맷한 외장 디스크나 옛 볼륨을 다룰 때는 볼륨 헤더 `createDate` 만 현지 시각이라서 다른 시각과 한 타임라인에 올리면 시간대만큼 어긋나서, 이 값은 따로 표시해 두고 맥의 시간대를 확인한 뒤에 올립니다.

지우거나 손상된 데이터에서 시각 값을 찾을 때는 위 형식의 범위를 걸러 내는 기준으로 씁니다. 8바이트 빅엔디언 double 을 맥 절대 시각으로 읽어 조사 기간 안에 드는지, 8바이트 나노초 값이 조사 기간의 유닉스 시각 범위에 드는지를 보면 우연히 맞은 바이트를 줄일 수 있습니다. 여러 형식의 시각을 한 줄로 모으는 방법은 [타임라인 작성](../../03-techniques/analysis/timeline/index.md)에서 다룹니다.

## 함정

맥 절대 시각을 유닉스 시각으로 착각하면 결과가 978307200 초, 곧 약 31년 이르게 나와서 2023년 값이 1992년으로 보이고, 반대로 유닉스 시각에 978307200 을 한 번 더 더하면 2050년대 날짜가 나옵니다. 요즘 날짜의 1904 기준 값을 유닉스 시각으로 읽으면 2080년대 같은 먼 미래 날짜가 나옵니다. 결과가 조사 기간과 크게 어긋나면 기준 시각부터 다시 정합니다.

단위도 틀리기 쉽습니다. APFS 는 나노초라서 초로 읽으면 터무니없이 큰 값이 되고, Alias v3 날짜는 1/65536초라서 65536 으로 나누지 않으면 역시 먼 미래가 나옵니다. 북마크 날짜는 같은 구조 안의 다른 필드와 달리 빅엔디언이라서, 리틀엔디언으로 읽으면 의미 없는 실수가 나옵니다.

도구가 보여 주는 시각이 UTC 인지 분석 컴퓨터의 현지 시각인지도 확인합니다. HFS+ `createDate` 처럼 원래 현지 시각인 값을 도구가 UTC 로 여기고 다시 시간대를 더하면 두 번 옮겨진 시각이 나옵니다. 문서 안에 적힌 날짜를 믿을 수 있는지 따지는 흐름은 [이 문서의 날짜를 믿을 수 있나](../../04-scenarios/activity/document-date.md)에서 다룹니다.

## 도구

변환은 어느 언어의 날짜 함수로도 할 수 있어서 특정 도구가 필요하지 않습니다. 아래는 파이썬 표준 라이브러리만 쓴 예이고, 상수는 이 페이지의 구조 절에서 가져왔습니다.

```python
import datetime, struct

UNIX_EPOCH = datetime.datetime(1970, 1, 1, tzinfo=datetime.timezone.utc)

def from_mac_absolute(sec):          # 2001 기준 초
    return UNIX_EPOCH + datetime.timedelta(seconds=sec + 978307200)

def from_hfs(sec):                   # 1904 기준 초 (HFS+, Alias v2)
    return UNIX_EPOCH + datetime.timedelta(seconds=sec - 2082844800)

def from_apfs(ns):                   # 1970 기준 나노초
    return UNIX_EPOCH + datetime.timedelta(microseconds=ns // 1000)

# 북마크 날짜 8바이트 (빅엔디언 double)
print(from_mac_absolute(struct.unpack(">d", bytes.fromhex("41c4dc9380000000"))[0]))
```

파이썬 `datetime` 은 마이크로초까지만 담아서 APFS 나노초의 마지막 세 자리는 잘립니다. 나노초까지 보고해야 하면 정수 값을 그대로 함께 적습니다. 포렌식 도구가 내놓은 시각은 이 식으로 몇 개를 직접 다시 계산해 맞춰 보고, 그 방법은 [도구 검증](../../03-techniques/reporting/tool-validation.md)에서 다룹니다.

## 참고 문헌

1. Apple, Technical Note TN1150: HFS Plus Volume Format, https://developer.apple.com/library/archive/technotes/tn/tn1150.html
2. Apple CF 공개 소스, CFDate.c (저작권 1998-2014), https://raw.githubusercontent.com/apple-oss-distributions/CF/main/CFDate.c
3. Apple CF 공개 소스, CFDate.h, https://raw.githubusercontent.com/apple-oss-distributions/CF/main/CFDate.h
4. mac_alias 문서, Mac Bookmark Format, https://mac-alias.readthedocs.io/en/latest/bookmark_fmt.html
5. mac_alias 문서, Mac Alias Format, https://mac-alias.readthedocs.io/en/latest/alias_fmt.html
6. Apple, Apple File System Reference (2020-06-22 판), https://developer.apple.com/support/downloads/Apple-File-System-Reference.pdf
