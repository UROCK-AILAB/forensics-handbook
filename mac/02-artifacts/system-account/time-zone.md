---
title: "시간대와 시계 설정"
parent: "아티팩트 · 시스템·계정"
nav_order: 470
---

# 시간대와 시계 설정 (Time Zone·NTP)

`/private/etc/localtime` 이 가리키는 시간대 파일과 `/Library/Preferences/.GlobalPreferences.plist` 의 선택 도시 기록으로 이 맥의 현재 시간대를 확인하고, 다른 흔적의 UTC 시각을 현지 시각으로 바꿀 기준을 정합니다.

## 무엇을 기록하나 · 왜 생기나

맥은 사용자가 시스템 설정 → 일반 → 날짜와 시간에서 고른 값에 따라 시간대와 시계를 맞춥니다. [4] 이 화면에는 "시간 및 날짜 자동으로 설정" (Set time and date automatically) 과 "현재 위치를 사용하여 자동으로 시간대 설정" (Set time zone automatically using your current location) 옵션이 있고, 앞의 옵션을 켜면 지역에 맞는 네트워크 시간 서버를 입력합니다. [4] 이 화면 구성은 macOS 10.15 Catalina 부터 최신판까지 해당합니다. [4]

설정의 결과는 두 곳에 남습니다. 하나는 `/private/etc/localtime`(`/etc/localtime`) 이라는 심볼릭 링크로, 지역별 시간대 파일을 가리키고, 이 링크가 가리키는 대상으로 현재 시스템 시간대를 알 수 있습니다. [1][3] 링크 대상은 10.9 에서 `/usr/share/zoneinfo/` 아래이고 [3], macOS 10.13 High Sierra 부터는 `/var/db/timezone/zoneinfo/` 아래입니다. [1] 다른 하나는 `/Library/Preferences/.GlobalPreferences.plist` 로, 시스템 로케일과 시간대 정보 [2], 지역 시간대와 지리 좌표 같은 전역 설정 [3] 이 들어 있습니다.

많은 흔적의 시각은 UTC 로 저장되거나 기준이 따로 있어서, 보고서에 현지 시각으로 적으려면 이 맥이 어느 시간대로 설정되어 있었는지부터 알아야 합니다. 시각 값의 기준과 읽는 법은 [맥의 시각 값](../../01-foundations/value-decoding/mac-time-values.md) 페이지에 있고, 이 페이지는 그 변환에 쓸 시간대를 찾는 법을 다룹니다.

## 위치와 버전별 차이

| 기록 | 위치 | 알려 주는 것 |
|---|---|---|
| 시간대 링크 | `/private/etc/localtime` (`/etc/localtime`) | 가리키는 대상 `/var/db/timezone/zoneinfo/<지역>`(10.13 이후) 또는 `/usr/share/zoneinfo/<지역>`(이전) 이 현재 시스템 시간대 [1][3] |
| 전역 기본 설정 | `/Library/Preferences/.GlobalPreferences.plist` | 선택 도시와 그 좌표, 시간대 이름, 국가, 로케일 [1][2][3] |

시간 서버 설정이 디스크의 어느 파일에 남는지, 기본 시간 서버가 무엇인지, 시계 동기화를 맡는 데몬이 어떤 상태 파일과 로그를 남기는지, 자동 시간대 설정의 켜짐 여부가 어느 plist 에 들어가는지는 공개된 분석 자료가 없습니다. 네트워크 시간 설정은 라이브 시스템에서 명령으로 확인합니다(아래 "라이브 시스템에서"). 링크 대상의 앞부분은 버전에 따라 다르니, 대상 경로는 실제 데이터에서 읽은 그대로 적습니다.

## 구조

### localtime 링크

`/private/etc/localtime` 은 내용이 아니라 링크 대상 경로가 핵심인 파일입니다. 링크 대상은 `/var/db/timezone/zoneinfo/<지역>` 이나 `/usr/share/zoneinfo/<지역>` 모양이고 [1][3], mac_apt 도 이 두 앞부분을 떼어 내고 `zoneinfo/` 뒤의 `<지역>` 부분을 시간대 이름으로 냅니다. [1] 심볼릭 링크가 파일 시스템에 어떻게 저장되는지는 [APFS 구조](../../01-foundations/disk-volume/apfs/index.md) 페이지에 있습니다.

### .GlobalPreferences.plist

이 파일에서 시간대와 지역을 알려 주는 키는 다음과 같습니다. [1] plist 를 여는 법은 [속성 목록 파일](../../01-foundations/data-formats/plist/index.md) 페이지에 있습니다.

| 키 | 자리 |
|---|---|
| `CountryCode`, `Latitude`, `Longitude`, `Name`, `RegionalCode`, `TimeZoneName`, `Version` | `com.apple.preferences.timezone.selected_city` 사전 안 |
| `Country` | 최상위 |
| `AppleLocale` | 최상위 |
| `com.apple.TimeZonePref.Last_Selected_City` | 최상위 |

`selected_city` 사전의 `TimeZoneName` 과 `Name` 을 함께 보면 어느 도시를 기준으로 어느 시간대가 잡혔는지 알 수 있고, `Latitude`·`Longitude` 는 그 도시의 좌표입니다. `Last_Selected_City` 값의 형식은 공개된 자료가 없으니 실제 데이터에서 나온 값을 그대로 적습니다.

## 증거로서 의미

**증명하는 것.** `localtime` 링크와 `selected_city` 의 `TimeZoneName` 은 이미지를 뜬 시점에 이 맥에 설정된 시간대를 알려 줍니다. [1][3] 두 값이 같으면 다른 흔적의 UTC 시각을 현지 시각으로 바꿀 때 그 시간대를 쓰고, 보고서에 어느 파일에서 확인했는지 함께 적습니다. `Country` 와 `AppleLocale` 은 사용자가 쓰는 지역과 언어 설정을 보여 줍니다. [1]

**증명하지 못하는 것.** 두 기록 모두 현재 설정만 담고 이전 설정을 남기지 않아서, 사건 당시에도 같은 시간대였다고 단정할 수 없습니다. 노트북을 들고 다른 시간대로 옮겼거나 사용자가 설정을 바꿨다면, 그 전의 기록은 다른 시간대로 표시되었을 수 있습니다. `Latitude`·`Longitude` 는 키 이름대로 선택된 도시의 좌표이고, 이 값을 기기가 실제로 있던 위치로 읽을 근거는 없습니다. 자동 시간대 설정이 위치 서비스를 쓰는지도 Apple 설명서에 적혀 있지 않습니다. [4]

보고서에는 "이미지 확보 시점의 `/private/etc/localtime` 은 무엇을 가리키고, 아래 시각은 이 시간대로 바꾼 값이다" 처럼 변환 기준을 밝혀 씁니다.

## 시각 해석

이 페이지의 기록은 설정값이라 시각 필드가 따로 없습니다. 시간대가 바뀐 시점을 알고 싶으면 `.GlobalPreferences.plist` 와 `localtime` 링크의 파일 시스템 시각을 참고할 수 있지만, `.GlobalPreferences.plist` 에는 시간대 말고도 로케일 같은 다른 전역 설정이 함께 들어 있어서 [2][3] 파일 수정 시각을 곧 시간대를 바꾼 시각으로 보지 않습니다. 이전 설정은 [스냅숏과 백업 비교](../../03-techniques/analysis/snapshot-diff.md) 로 찾아보고, 시간대가 중간에 바뀐 사건을 다룰 때는 [타임라인 작성](../../03-techniques/analysis/timeline/index.md) 에서 구간마다 다른 시간대를 적용합니다.

시계가 틀려 있었는지도 따로 따져야 합니다. 네트워크 시간 설정이 꺼져 있으면 시계가 실제 시각과 어긋났을 수 있고, 그 어긋남은 시간대 설정으로는 드러나지 않습니다. 이미지를 뜰 때 기기 시계와 기준 시계를 함께 적어 두고, 확보 절차 전반은 [맥 증거 확보](../../03-techniques/process-acquisition/evidence-acquisition/index.md) 페이지를 따릅니다.

## 함정과 한계

이미지를 분석 컴퓨터에 마운트한 뒤 `localtime` 을 도구로 "열면", 링크가 절대 경로라서 분석 컴퓨터 자신의 시간대 파일을 따라갈 수 있습니다. 링크를 따라가지 말고 링크에 적힌 대상 경로 문자열을 읽어서 시간대 이름을 적습니다.

`localtime` 링크와 `TimeZoneName` 이 서로 다르면 어느 한쪽이 나중에 바뀌었거나 손댄 흔적일 수 있지만, 두 기록이 언제 어떻게 갱신되는지는 공개된 자료가 없습니다. 둘을 모두 보고서에 적고, 어느 쪽을 변환 기준으로 삼았는지 밝힙니다.

도구가 시각을 보여 줄 때 분석 컴퓨터의 시간대로 바꿔 표시하는 일이 흔해서, 보고서에 옮긴 시각이 분석 대상 기기의 시간대인지 분석 컴퓨터의 시간대인지 헷갈리기 쉽습니다. 타임라인은 UTC 로 만들고, 현지 시각은 이 페이지에서 확인한 시간대로 따로 표시합니다.

## 직접 분석해 보기

### 헥스로 한 번

`.GlobalPreferences.plist` 를 헥스 편집기로 열고 `TimeZoneName` 이나 `selected_city` 를 검색하면 키 문자열이 있는 자리를 찾을 수 있습니다. 키와 값을 잇는 오프셋 표를 따라가 문자열 값과 좌표 값을 읽는 절차는 [속성 목록 파일](../../01-foundations/data-formats/plist/index.md) 페이지에 있습니다. `localtime` 링크의 대상 문자열이 파일 시스템 어디에 저장되는지는 [APFS 구조](../../01-foundations/disk-volume/apfs/index.md) 페이지를 봅니다.

> 그림 자리: 헥스 편집기에서 `selected_city` 사전의 `TimeZoneName` 키와 이어지는 값 문자열을 표시한 화면(명세로 만든 예시 파일 기준)

### 공개 도구로 한 번

mac_apt 의 `BASICINFO` 플러그인은 `localtime` 링크와 `.GlobalPreferences.plist` 의 위 키를 읽어 기본 정보로 냅니다. [1] 도구가 링크 대상을 어떻게 읽었는지 확인하려면, 이미지를 읽기 전용으로 마운트하고 `ls -l` 로 링크 문자열을 직접 봅니다.

### 라이브 시스템에서

켜져 있는 맥에서는 `systemsetup` 명령으로 현재 값을 조회할 수 있고, 관리자 권한(sudo)이 필요합니다. [5]

| 옵션 | 돌려주는 값 |
|---|---|
| `systemsetup -gettimezone` | 현재 시간대 |
| `systemsetup -listtimezones` | 고를 수 있는 시간대 목록 |
| `systemsetup -getusingnetworktime` | 네트워크 시간 사용 켜짐·꺼짐 |
| `systemsetup -getnetworktimeserver` | 설정된 시간 서버 |
| `systemsetup -getdate`, `systemsetup -gettime` | 기기의 현재 날짜와 시각 |

`-getdate`·`-gettime` 결과는 기준 시계와 함께 적어 두면 기기 시계가 얼마나 어긋났는지 보여 주는 자료가 됩니다. 조사 중에는 값을 돌려주는 `-get...`·`-list...` 옵션만 쓰고, 라이브 대응 전반의 순서는 [라이브 대응](../../03-techniques/process-acquisition/live-response/index.md) 페이지를 따릅니다.

## 교차 검증

| 함께 볼 기록 | 맞춰 볼 내용 |
|---|---|
| [맥의 시각 값](../../01-foundations/value-decoding/mac-time-values.md) | 각 흔적의 시각이 UTC 인지 현지 시각인지 |
| [통합 로그에서 찾을 것](../logs/unified-log-events/index.md) | 같은 사건을 적은 로그 시각과 변환한 시각이 맞는지 |
| [와이파이 기록](../network/wifi.md) | 접속한 네트워크의 지역이 설정된 시간대와 어울리는지 |
| [OS 버전과 설치 기록](os-version-install-history.md) | 설치 이력 시각을 현지 시각으로 바꿀 때 |
| [타임라인 작성](../../03-techniques/analysis/timeline/index.md) | 시간대가 바뀐 구간을 나눠 적용하는 법 |

## 실습

공개 시험 자료(NIST CFReDS 등)의 맥 이미지로 다음 질문을 풀어 봅니다.

1. 이미지에서 `/private/etc/localtime` 링크의 대상 문자열을 읽고, 시간대 이름을 적어 봅니다.
2. `.GlobalPreferences.plist` 의 `selected_city` 사전에서 `Name` 과 `TimeZoneName` 을 읽어 1번 결과와 같은지 비교합니다.
3. 다른 페이지에서 UTC 로 저장된다고 확인한 시각 하나를 골라, 확인한 시간대로 바꾼 값을 도구 표시와 맞춰 봅니다.
4. 이미지에 스냅숏이나 백업이 있다면 이전 시점의 `localtime` 링크와 비교해, 시간대가 바뀐 적이 있는지 확인합니다.

## 참고 문헌

1. mac_apt `BASICINFO` 플러그인 소스 (Yogesh Khatri) — https://raw.githubusercontent.com/ydkhatri/mac_apt/master/plugins/basicinfo.py
2. ForensicArtifacts `macos.yaml` (MacOSGlobalPreferencesPlistFile) — https://raw.githubusercontent.com/ForensicArtifacts/artifacts/main/artifacts/data/macos.yaml
3. Forensics Wiki, Mac OS X 10.9 artifacts location — https://forensics.wiki/mac_os_x_10.9_artifacts_location/
4. Apple 지원, Mac 사용 설명서 — Set the date and time on Mac — https://support.apple.com/guide/mac-help/set-the-date-and-time-mchlp2996/mac
5. SS64, systemsetup 명령 설명 — https://ss64.com/mac/systemsetup.html
