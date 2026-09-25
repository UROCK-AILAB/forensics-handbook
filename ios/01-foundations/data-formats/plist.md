---
title: "속성 목록 파일"
parent: "기반 · 데이터 저장 형식"
nav_order: 140
---

# 속성 목록 파일 (plist·NSKeyedArchiver)

## 한 줄 요약

속성 목록 파일 (property list, plist) 은 iOS 설정과 백업 정보를 담는 기본 형식이고, 그 안에 객체 그래프를 한 겹 더 싸 넣는 NSKeyedArchiver 형식이 자주 겹쳐 들어 있어 두 층을 차례로 풀어야 값이 보입니다.

Apple 은 포렌식용 공식 명세를 내지 않았습니다. 바이너리 plist 는 Apple 공개 소스 CF 의 `CFBinaryPList.c` 주석이 사실상 명세 구실을 하고[3], NSKeyedArchiver 구조는 공개 도구 자료에서 가져왔습니다[1].

## 이 형식을 쓰는 아티팩트

실제 아이폰 로컬 백업을 보면 plist 가 어디에나 있습니다. 백업 폴더 맨 위에는 `Info.plist`, `Manifest.plist`, `Status.plist` 가 있고, Apple 영역에서 이름을 적어 둔 plist 1,006개 가운데 728개가 `Library/Preferences/` 아래에 있습니다. 백업 최상위 파일의 키와 뜻은 [로컬 백업](../backups/local-backup/index.md)에서, 앱과 시스템 설정 plist 의 해석은 [설정 값](../../02-artifacts/system-account/preferences.md)에서 다룹니다.

같은 관찰에서 plist 1,006개를 백업 도메인별로 나누면 아래와 같습니다.

| 도메인 | plist 수 | 도메인 | plist 수 |
|---|---|---|---|
| HomeDomain | 667 | SysContainerDomain | 8 |
| AppDomain | 137 | SystemPreferencesDomain | 7 |
| AppDomainPlugin | 57 | ProtectedDomain | 4 |
| RootDomain | 51 | InstallDomain | 2 |
| AppDomainGroup | 29 | ManagedPreferencesDomain | 2 |
| SysSharedContainerDomain | 16 | DatabaseDomain | 1 |
| WirelessDomain | 14 | KeychainDomain | 1 |
| CameraRollDomain | 10 | | |

키 값의 형식도 여러 가지가 섞여 있습니다. 같은 백업에서 키마다 붙은 형식을 세면 int 1,024개, bool 955개, str 772개, list 459개, datetime 458개, bytes 360개, float 309개였고, 사전(dict) 형식 값도 있었습니다. 이 가운데 bytes 형식 값이 분석에서 특히 중요합니다. `com.apple.ap.AppStore.plist` 의 `AppStoreSLPContentSnapshot`, `com.apple.Fitness.plist` 의 `OnboardingCoordinatorCriteria`, `com.apple.biomesyncd.plist` 의 `CC_OncePerBootBackingData`, `com.apple.siriinferenced.plist` 의 `appIntentsBiomeBookmark`·`appIntentsTranscriptBiomeBookmark` 가 bytes 형식이었습니다. 값을 읽지 않았기 때문에 이 bytes 안이 NSKeyedArchiver 인지, 바이너리 plist 인지, [프로토콜 버퍼](protobuf.md)인지는 알 수 없습니다. 같은 관찰은 각 plist 가 XML 인지 바이너리인지도 기록하지 않았습니다.

plist 는 파일 밖의 다른 아티팩트에도 쓰입니다. iOS 16 을 조사한 자료에 따르면 [바이옴](../../02-artifacts/app-usage/biome/index.md) 스트림 폴더의 메타데이터 파일이 NSKeyedArchiver 형식 plist 이고, 보관 기간인 `maxAge` 값(흔히 2,419,200초, 곧 28일)을 담습니다[2].

## 구조

### 바이너리 plist

바이너리 plist 는 헤더, 객체 표 (object table), 오프셋 표 (offset table), 트레일러 (trailer) 순서로 이어집니다[3]. 파일 앞 8바이트가 `bplist00` 이라서 이 문자열로 바이너리 plist 인지 알아봅니다. 앞 6바이트 `bplist` 가 매직이고 뒤 2바이트 `00` 이 형식 버전입니다[1][3].

| 부분 | 내용 |
|---|---|
| 헤더 | 오프셋 0 부터 8바이트, ASCII `bplist00` |
| 객체 표 | 객체들이 차례로 놓입니다. 각 객체는 마커 바이트 하나로 시작합니다 |
| 오프셋 표 | 객체마다 파일 안 바이트 위치를 적은 목록입니다. 칸 하나의 크기는 트레일러가 정합니다 |
| 트레일러 | 오프셋 칸 크기, 객체 참조 크기, 객체 수, 최상위 객체 번호, 오프셋 표 위치 |

트레일러 안의 정확한 바이트 배치는 이 페이지의 출처에서 분명하게 확인하지 못해서 오프셋을 적지 않습니다.

객체의 형식은 마커 바이트의 위 4비트가 정하고, 아래 4비트는 형식에 따라 크기나 개수를 나타냅니다[3].

| 마커(2진수) | 형식 | 아래 4비트와 뒤따르는 내용 |
|---|---|---|
| `0000 0000` | null | 없음. CF 주석은 형식 버전 `1?` 에서만 쓴다고 적었습니다 |
| `0000 1000` | false | 없음 |
| `0000 1001` | true | 없음 |
| `0001 0nnn` | int | 2^nnn 바이트 정수, 빅 엔디언 |
| `0010 0nnn` | real | 2^nnn 바이트 실수, 빅 엔디언 |
| `0011 0011` | date | 8바이트 실수, 빅 엔디언 |
| `0100 nnnn` | data | nnnn 이 바이트 수이고, `1111` 이면 뒤에 int 로 개수가 옴 |
| `0101 nnnn` | ASCII 문자열 | nnnn 이 글자 수(`1111` 이면 int 개수가 옴), 1글자 1바이트 |
| `0110 nnnn` | 유니코드 문자열 | nnnn 이 글자 수(`1111` 이면 int 개수가 옴), 1글자 2바이트 빅 엔디언 |
| `1000 nnnn` | uid | nnnn+1 바이트 |
| `1010 nnnn` | array | 원소 |
| `1100 nnnn` | set | 원소. CF 주석은 형식 버전 `1?` 에서만 쓴다고 적었습니다 |
| `1101 nnnn` | dict | 키와 값 |

array·set·dict 는 값을 바로 품지 않고 다른 객체의 번호를 가리키며, 이 번호 한 칸의 크기가 트레일러의 "객체 참조 크기" 입니다[3]. null 과 set 은 CF 주석에서 형식 버전 `1?` 전용으로 표시돼 있어서, 흔히 보는 `bplist00` 파일에서는 나오지 않는다고 보는 편이 맞습니다[3]. date 객체는 CF 주석에 "8바이트 실수, 빅 엔디언" 으로만 적혀 있고 기준 시점은 적혀 있지 않으며, 이를 벽시계 시각으로 바꾸는 법은 [시각 값](../value-decoding/time-values.md)에서 다룹니다.

### NSKeyedArchiver

NSKeyedArchiver 는 plist 자료 모델 위에 한 겹 더 올린 직렬화 형식입니다. 최상위 사전에 네 키가 있습니다[1].

| 키 | 내용 |
|---|---|
| `$archiver` | 문자열 `NSKeyedArchiver` |
| `$version` | 버전 숫자(예: 100000) |
| `$objects` | 모든 객체를 번호 순서로 담은 배열 |
| `$top` | `root` 키의 UID 가 주 객체를 가리킴 |

객체끼리는 값을 직접 품지 않고 UID 로 서로를 가리키며, UID 값이 곧 `$objects` 배열의 번호입니다[1][3]. 아래는 이 설명대로 만든 예시이고, 특정 파일에서 나온 값이 아닙니다.

```
$archiver = "NSKeyedArchiver"
$version  = 100000
$top      = { root = UID(1) }
$objects  = [ ..., (1번: 주 객체), ... ]
```

자주 보는 클래스는 공개 도구 ccl_bplist 가 아래처럼 풉니다[1].

| 클래스 | 푸는 법 |
|---|---|
| NSDate | `NS.time` 값을 날짜·시각으로 바꿈 |
| NSDictionary·NSMutableDictionary | `NS.keys` 와 `NS.objects` 를 짝지음 |
| NSArray·NSMutableArray | `NS.objects` 를 차례로 늘어놓음 |
| 문자열 `$null` | 값 없음 |

## 읽는 법

1. 파일 앞 8바이트를 봅니다. `bplist00` 이면 바이너리 plist 이고, 그렇지 않으면 XML 등 다른 표현일 수 있습니다.
2. 트레일러에서 최상위 객체 번호와 오프셋 표 위치를 읽고, 오프셋 표로 최상위 객체를 찾아 마커 바이트부터 풉니다.
3. 최상위 사전에 `$archiver`·`$objects`·`$top` 이 보이면 NSKeyedArchiver 이므로, `$top` 의 `root` UID 에서 시작해 `$objects` 번호를 따라갑니다.
4. data(bytes) 값이 나오면 그 안을 다시 확인합니다. NSKeyedArchiver 가 바이너리 plist 안에 들어 있거나 다른 plist 의 data 값 안에 들어 있는 경우가 흔해서 두 해석기를 같이 써야 합니다[1].

아래는 명세의 마커 표대로 만든 헥스 예시입니다. 파일 전체가 아니라 헤더와 객체 몇 개만 보입니다.

```
오프셋  바이트                          뜻
0x00    62 70 6C 69 73 74 30 30         "bplist00" (매직 + 버전)
0x08    55 68 65 6C 6C 6F               0101 0101 → ASCII 문자열 5글자 "hello"
0x0E    10 2A                           0001 0000 → 1바이트 int, 값 42
0x10    09                              true
0x11    80 01                           1000 0000 → 1바이트 uid, 값 1
```

## 포렌식에서 중요한 점

NSKeyedArchiver 안에는 참조가 돌고 돌아 자기 자신으로 돌아오는 구조가 있을 수 있어서, ccl_bplist 는 UID 를 모두 한꺼번에 따라가지 않고 요청할 때만 따라갑니다[1]. 직접 해석기를 짤 때도 같은 이유로 방문한 번호를 기록해 두어야 끝없이 도는 일을 막을 수 있습니다.

바이너리 plist 는 객체 위치를 파일 끝쪽의 오프셋 표와 트레일러에서 찾는 구조입니다[3]. 그래서 파일 끝이 잘리거나 덮이면 객체 표는 남아 있어도 어디서부터 읽어야 할지 알려 주는 정보를 잃습니다. 이 페이지의 출처에서는 plist 의 삭제나 손상 뒤 복구 동작을 따로 다룬 자료를 확인하지 못했습니다. 지운 파일을 되살리는 일반 절차는 [삭제 데이터 복구](../../03-techniques/analysis/data-recovery/index.md)에서 다룹니다.

## 함정

같은 종류의 시각 정보가 plist 마다 다른 형식으로 저장됩니다. `com.apple.appstored.plist` 의 `AppUsageBiomeStartDate` 는 datetime 형식이었고, `com.apple.siriinferenced.plist` 의 `BiomeEventLastBackFill` 과 `com.apple.lighthouse.pnr.PnROnDeviceWorker.plist` 의 `com.apple.biome.self.processedstreamLastBookmarkTrackTime` 은 float 형식이었습니다. float 로 저장된 시각이 어느 시점을 기준으로 센 값인지는 키마다 따로 확인해야 하고, 이 페이지의 출처로는 확인하지 못했습니다. 기준 시점이 다른 값들을 가려내는 법은 [시각 값](../value-decoding/time-values.md)에서 다룹니다.

bytes 형식 값을 그냥 넘기면 안쪽에 겹쳐 든 plist·NSKeyedArchiver·protobuf 를 놓칩니다. 도구가 bytes 를 16진수나 base64 로만 보여 주면 그 값을 따로 꺼내 앞 8바이트를 다시 확인합니다.

NSKeyedArchiver 를 바이너리 plist 해석기로만 읽으면 `$objects` 배열이 번호 순으로 늘어놓인 목록만 보입니다. 값 사이의 관계는 UID 를 따라가야 드러나므로, 배열에서 가까이 붙은 두 값을 같은 레코드로 짐작해 보고서에 쓰지 않습니다.

## 도구

공개 도구로는 CCL Group 의 파이썬 라이브러리 ccl_bplist 가 바이너리 plist 를 읽고 NSKeyedArchiver 를 풉니다[1]. 도구 결과는 위 헥스 예시처럼 마커 바이트 몇 개를 직접 따라가 맞춰 보는 방법으로 검증할 수 있고, 검증 절차는 [도구 검증](../../03-techniques/reporting/tool-validation.md)에서 다룹니다.

## 참고 문헌

1. CCL Group — ccl-bplist (GitHub README) — https://github.com/cclgroupltd/ccl-bplist
2. D20 Forensics — iOS 16 - Now You 'C' It, Now You Don't -- Breaking Down The Biomes Part 1 — https://blog.d204n6.com/2022/09/ios-16-now-you-c-it-now-you-dont.html
3. Apple 공개 소스 CF — CFBinaryPList.c (형식 설명 주석) — https://raw.githubusercontent.com/apple-oss-distributions/CF/main/CFBinaryPList.c
