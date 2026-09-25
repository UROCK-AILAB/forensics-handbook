---
title: "sysdiagnose 묶음"
parent: "기반 · 백업 형식"
nav_order: 260
---

# sysdiagnose 묶음 (sysdiagnose)

## 한 줄 요약

sysdiagnose 묶음 (sysdiagnose)은 디버깅과 문제 해결을 위해 기기가 시스템 로그와 DB 를 모아 `.tar.gz` 파일 하나로 묶은 것이고 [2], 로컬 백업이나 전체 이미지 없이도 통합 로그 일부와 Shutdown.log 를 얻을 수 있어 스파이웨어 1차 점검에 쓰입니다 [2].

## 이 형식을 쓰는 아티팩트

묶음 하나의 크기는 대략 200~400MB 이고, 만드는 데 몇 분이 걸립니다 [2]. 안에는 충돌 보고서, 메모리 사용 정보, 커널 로그, 통합 로그(unified log)의 일부가 들어 있습니다. 가장 큰 부분은 `system_logs.logarchive` 이고, 그 밖에 로그, 충돌, 요약, Wi-Fi 연결 정보를 담은 폴더가 있습니다 [3]. 폴더 이름 하나하나는 이 페이지의 자료로 확인하지 못해서 적지 않습니다.

| 들어 있는 것 | 자세히 볼 페이지 |
|---|---|
| 통합 로그 일부(`system_logs.logarchive`) | [통합 로그 형식](../data-formats/unified-log.md), [통합 로그에서 찾을 것](../../02-artifacts/logs/unified-log-events.md) |
| Shutdown.log(`system_logs.logarchive` 의 `Extra` 폴더) [2] | 이 페이지의 "Shutdown.log" 절, [sysdiagnose 안의 로그](../../02-artifacts/logs/sysdiagnose-logs.md) |
| 충돌 보고서, 커널 로그 | [충돌·진단 기록](../../02-artifacts/app-usage/diagnostics.md) |
| Wi-Fi 연결 정보 | [와이파이 기록](../../02-artifacts/network/wifi.md) |

Apple 개발자 사이트는 iOS·iPadOS 용 수집 안내를 "sysdiagnose Logging Instructions" PDF 로 제공합니다 [1]. 이 PDF 는 열어 보지 않았습니다.

## 구조

### 만드는 방법

두 음량 버튼과 측면 버튼을 함께 눌렀다가 떼면(약 250ms) 수집이 시작되고, 아이폰은 짧은 진동으로 알리면서 스크린숏도 함께 찍습니다 [3]. Elcomsoft 는 1초보다 오래 누르면 sysdiagnose 대신 기기가 잠긴다고 적었습니다 [3]. 버튼 대신 설정의 손쉬운 사용 → 터치 → AssistiveTouch 에서 최상위 메뉴에 "분석(Analytics)" 을 넣고 그것으로 시작할 수도 있고, 수집 중에는 화면 위쪽에 회색 막대가 보입니다 [3]. 수집이 끝날 때까지 Elcomsoft 는 10분쯤 기다리라고 안내합니다 [3].

### 위치와 파일 이름

기기 안에서는 아래 폴더에 저장합니다 [3].

```
/private/var/mobile/Library/Logs/CrashReporter/DiagnosticLogs/sysdiagnose/
```

[3]에 실린 파일 이름 예시는 아래와 같습니다.

```
sysdiagnose_2025.06.24_11-01-29+0200_iPhone-OS_iPhone_22F76.tar.gz
```

날짜와 시각 뒤에 UTC 와의 차이(`+0200`)가 붙고, 그 뒤에 플랫폼 이름(`iPhone-OS`), 기기 종류, OS 빌드 번호가 옵니다 [3]. OS 버전 숫자는 이름에 없지만 빌드 번호로 버전을 알 수 있어서, 묶음을 풀지 않고도 언제 어떤 OS 에서 만들었는지 알 수 있습니다([3]의 예시에서 끌어낸 해석).

## 읽는 법

### 꺼내기

기기에서 묶음을 꺼내려면 기기를 잠금 해제하고 분석용 컴퓨터와 페어링해야 하고, 페어링할 때 기기 암호를 입력해야 합니다 [3]. [3]은 수집 도구로 충돌 로그 영역을 TAR 로 받아 오는 방법을 소개했습니다. AirDrop 이나 컴퓨터로 옮기는 Apple 공식 절차는 [1]의 PDF 에 있을 것으로 보이지만 확인하지 못했습니다. 증거 확보 절차 전반은 [모바일 증거 확보](../../03-techniques/acquisition/mobile-acquisition/index.md) 페이지에서 다룹니다.

### Shutdown.log

`.tar.gz` 를 풀면 `system_logs.logarchive` 안의 `Extra` 폴더에 Shutdown.log 가 있습니다 [2]. 기기를 다시 켤 때마다 정상 재부팅을 늦춘 프로세스를 프로세스 ID, 파일 경로와 함께 적고, 항목마다 Unix 타임스탬프가 붙습니다 [2]. Unix 타임스탬프는 UTC 기준 초라서, 파일 이름의 현지 시각과 비교할 때는 시간대를 맞춘 뒤 봅니다.

Kaspersky 는 이 로그에서 두 가지를 의심 신호로 꼽았습니다 [2]. 하나는 수상한 경로에서 실행된 프로세스이고, 다른 하나는 재부팅을 오래 붙잡는 프로세스입니다.

| 신호 | 내용 | 출처 |
|---|---|---|
| 수상한 경로 | `/private/var/db/` 에서 실행된 프로세스(Pegasus, Reign), `/private/var/tmp/` 에서 실행된 프로세스(Predator) | [2] |
| Pegasus 흔적 예 | `/private/var/db/com.apple.xpc.roleaccountd.staging/rolexd` | [2] |
| Pegasus 흔적 예 | `/private/var/db/com.apple.xpc.roleaccountd.staging/com.apple.WebKit.Networking` | [4] |
| 오래 붙잡는 프로세스 | 재부팅 지연 알림이 네 번보다 많으면 살펴볼 만하고, 감염되지 않은 기기에서도 두세 번은 나올 수 있음 | [2] |
| 비어 있는 로그 | 2022년 무렵부터 Pegasus 운영자가 Shutdown.log 를 통째로 지웠다고 해서, 비워진 로그 자체를 의심 신호로 봄 | [4] |

iVerify 는 iOS 18 이하에서 containermanagerd 로그의 부팅 기록과 Shutdown.log 를 맞춰 보고 서로 어긋나는 곳을 찾는 방법도 썼고, containermanagerd 로그는 몇 주 치가 남을 수 있다고 적었습니다 [4]. 스파이웨어 점검 절차 전체는 [악성 코드·스파이웨어 흔적](../../03-techniques/analysis/spyware-triage/index.md)과 [스파이웨어 감염 흔적](../../04-scenarios/incident/spyware.md) 페이지에서 다룹니다.

## 포렌식에서 중요한 점

통합 로그 항목은 수명(TTL)이 짧아 몇 분이나 몇 시간 만에 사라지기도 하고, Elcomsoft 는 흔히 말하는 "30일 보관" 이 대체로 틀렸다고 적었습니다 [3]. 그래서 sysdiagnose 는 사건 직후 빨리 만들수록 남는 기록이 많습니다([3]에서 끌어낸 해석).

Kaspersky 는 로컬 백업이나 전체 이미지보다 Shutdown.log 를 얻기가 쉽다는 점을 이 방법의 장점으로 꼽았습니다 [2]. 기기 전체를 확보하기 어려운 상황에서도 사용자가 직접 만든 sysdiagnose 로 1차 점검을 할 수 있다는 뜻입니다.

### 버전별 차이

| iOS | Shutdown.log | 출처 |
|---|---|---|
| iOS 18 까지 | 재부팅할 때마다 항목이 덧붙어 기록이 쌓임 | [4] |
| iOS 26 | 재부팅할 때마다 덮어써서 이전 기록이 사라짐 | [4] |

iVerify 는 iOS 26 으로 올리기 전에 sysdiagnose 를 만들어 저장해 두라고 권했습니다 [4]. 업데이트 뒤에 받은 묶음에서 옛 재부팅 기록이 없더라도 흔적을 지운 것으로 단정하지 않습니다. iOS 27 에서 Shutdown.log 가 어떻게 동작하는지, iOS 15~18 사이에 묶음 안 폴더 구성이 바뀌었는지는 이 페이지의 자료로 확인하지 못했습니다.

### 로컬 백업에 남는 관련 흔적

로컬 백업에는 sysdiagnose 묶음 파일이 없었고, 도메인 목록에 `AppDomainPlugin-com.apple.DiagnosticExtensions.sysdiagnose`(항목 4개)가 있었을 뿐입니다. 같은 백업에는 `…DiagnosticExtensions.CrashLogs`, `.Panic`, `.StackShot`, `.WiFi`, `.Cellular`, `.CoreLocation`, `.ScreenTime`, `.VPN`, `.Messages` 같은 진단 확장 컨테이너도 많았지만, 각 컨테이너에 무엇이 있는지와 sysdiagnose 의 어느 부분을 채우는지는 확인하지 못했습니다.

값은 읽지 않았지만 진단과 관련된 설정 plist 도 있었습니다. 키의 뜻은 확인하지 못했습니다.

| 파일 | 키 |
|---|---|
| `RootDomain :: Library/Preferences/com.apple.CrashReporter.plist` | `ExcResourceDiagInfo_<프로세스 이름>`(datetime) 키 여럿. 예: `ExcResourceDiagInfo_cloudd`, `ExcResourceDiagInfo_geod` |
| `RootDomain :: Library/Preferences/com.apple.osanalyticshelper.plist` | `stability-monitor.lastBuild`(str), `stability-monitor.lastBuild-hasSupplementalBuild`(bool), `retryCount`(int), `stability-monitor.baselineCrashCount`, `lastSuccess`(float), `stability-monitor.baselineVersions`, `stability-monitor.baselineUptime` |
| `HomeDomain :: Library/Preferences/OTACrashCopier.plist` | `taskingLastSuccessfulRequest` |

## 함정

로컬 백업만 받으면 sysdiagnose 묶음은 얻지 못합니다. 묶음이 필요하면 기기에서 따로 만들어 꺼내야 합니다.

sysdiagnose 에 담긴 통합 로그는 전체가 아니라 일부이고 [3], 수명이 짧은 항목은 이미 사라졌을 수 있습니다. 로그에 기록이 없다는 사실을 "그 일이 없었다" 는 근거로 쓰지 않습니다.

Shutdown.log 의 수상한 경로는 알려진 스파이웨어 사례에서 나온 신호라서, 목록에 없는 경로라고 깨끗하다고 볼 수는 없고, 목록에 걸렸다고 곧바로 감염이라고 쓰지도 않습니다. 보고서에는 "이 시각의 재부팅에서 이 경로의 프로세스가 재부팅을 늦춘 기록이 있다" 처럼 기록 그대로 씁니다.

## 도구

Kaspersky 는 Shutdown.log 를 다루는 공개 도구 iShutdown 을 냈습니다 [2]. `iShutdown_detect` 는 이상 항목을 찾고, `iShutdown_parse` 는 Shutdown.log 를 꺼내 CSV 로 만들고, `iShutdown_stats` 는 재부팅 횟수 통계를 냅니다 [2]. 도구 결과는 풀어 둔 Shutdown.log 원문과 한 번 맞춰 봅니다.

## 참고 문헌

1. Apple Developer, "Profiles and Logs" (sysdiagnose, iOS). https://developer.apple.com/bug-reporting/profiles-and-logs/?platform=ios&name=sysdiagnose
2. Kaspersky Securelist, "Detecting iOS malware via Shutdown.log file". https://securelist.com/shutdown-log-lightweight-ios-malware-detection-method/111734/
3. ElcomSoft blog, "Extracting and Analyzing Apple sysdiagnose Logs" (2025-06). https://blog.elcomsoft.com/2025/06/extracting-and-analyzing-apple-unified-logs/
4. iVerify, "Key IOCs for Pegasus and Predator Spyware Cleaned With iOS 26 Update". https://iverify.com/blog/key-iocs-for-pegasus-and-predator-spyware-cleaned-with-ios-26-update
