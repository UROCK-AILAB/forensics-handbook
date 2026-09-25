---
title: "sysdiagnose 안의 로그"
parent: "아티팩트 · 로그"
nav_order: 1100
---

# sysdiagnose 안의 로그 (sysdiagnose Logs)

## 한 줄 요약

sysdiagnose 묶음에는 통합 로그 보관본, 프로세스 목록, 충돌 기록, 설치·활성화 로그, Wi-Fi 설정 같은 진단 파일이 함께 들어 있고, 그 가운데 Shutdown.log 는 재부팅 때 끝나지 않고 남아 있던 프로세스를 경로와 함께 적어 두어 스파이웨어 감염을 가볍게 가려내는 데 쓰입니다.

## 무엇을 기록하나 · 왜 생기나

sysdiagnose 는 기기 상태를 진단하려고 여러 로그와 설정 파일을 한 번에 모은 `.tar.gz` 묶음이고, 크기는 200~400MB, 만드는 데 보통 몇 분이 걸립니다[1]. Apple 은 개발자 페이지에서 iOS·iPadOS 용 sysdiagnose 안내 PDF(`sysdiagnose_Logging_Instructions.pdf`)와 로깅 프로파일 `loggingiOS.mobileconfig` 를 내려받게 해 둡니다[3]. 만든 묶음은 설정의 개인정보 보호·분석 메뉴에서 찾을 수 있고, 메뉴 이름은 iOS 버전마다 다릅니다[1].

묶음은 사용자가 직접 만들어야 생깁니다. 기기가 스스로 주기적으로 만드는지는 확인한 자료가 없어서, 조사 대상 기기에 이미 만들어진 묶음이 있을 것이라고 기대하지 않습니다. 묶음을 만드는 순서와 여는 법은 [sysdiagnose 묶음](../../01-foundations/backups/sysdiagnose.md) 에서 다루고, 이 페이지는 묶음 안의 로그가 무엇을 알려 주는지를 다룹니다.

## 위치와 버전별 차이

### 묶음 안의 파일

EC-DIGIT-CSIRC 의 공개 분석 도구 sysdiagnose 가 묶음에서 읽는 파일은 다음과 같습니다[2]. 묶음 안의 정확한 하위 경로는 출처에 없어서 파일 이름만 적습니다.

| 갈래 | 파일 | 알려 주는 것 |
|---|---|---|
| 프로세스 | `ps.txt`, `ps_thread.txt`, `taskinfo.txt` | 묶음을 만든 순간 돌던 프로세스와 스레드 |
| 시스템 | SystemVersion plist | OS 버전 |
| 통합 로그 | `system_logs.logarchive` 폴더 | 시스템 전체 로그. [통합 로그에서 찾을 것](unified-log-events.md) 에서 다룹니다 |
| 전원 | powerlogs DB | 전원 로그. [전원 로그](../app-usage/powerlog.md) 에서 다룹니다 |
| 충돌 | crashes 폴더의 `.ips` 파일 | 충돌 기록. [충돌·진단 기록](../app-usage/diagnostics.md) 에서 다룹니다 |
| 재부팅 | `shutdown.log` | 재부팅 때 남아 있던 프로세스. 아래 "구조" 에서 다룹니다 |
| 상태 덤프 | `spindump-nosymbols`, `swcutil_show`, `remotectl_dumpstate`, `security-sysdiagnose.txt` | 각 구성 요소의 상태 출력 |
| 실행 파일 | UUIDToBinaryLocations plist | UUID 와 실행 파일 경로의 짝 |
| Wi-Fi | wifi_scan 파일, com.apple.wifi plist, Known Wifi Networks plist | 주변 네트워크와 저장한 네트워크. [와이파이 기록](../network/wifi.md) 에서 다룹니다 |
| 설치·활성화 | lockdownd 로그, mobileactivation 로그, mobile_installation 로그, 앱 설치 로그, iTunes Store 로그 | 기기 연결·활성화·앱 설치 기록 |
| 그 밖 | Accessibility TCC, brctl(iCloud Drive), containermanagerd 로그, olddsc, networkextension plist, networkextensioncache plist | 권한·동기화·컨테이너·네트워크 확장 상태 |

UUIDToBinaryLocations plist 는 UUID 만 적힌 기록을 읽을 때 실행 파일 경로를 찾아보는 데 쓸 수 있습니다.

### 버전별 차이

| iOS 버전 | 확인한 내용 |
|---|---|
| 13·14 | EC-DIGIT-CSIRC 도구가 "확인 필요" 로 남겨 두었습니다[2] |
| 15·16·17·18·26 | EC-DIGIT-CSIRC 도구가 시험한 버전입니다[2] |
| 27.0 | 로컬 백업에 sysdiagnose 관련 도메인이 보였습니다(아래 표). 묶음 자체는 관찰하지 않았습니다 |

버전마다 어떤 파일이 새로 생기거나 빠지는지는 확인한 자료가 없습니다.

### 로컬 백업에 보이는 진단 흔적

관찰한 로컬 백업에는 sysdiagnose 와 같은 계열의 진단 확장 도메인이 여럿 있었습니다. 이 도메인들에 sysdiagnose 묶음이 들어 있다는 근거는 없고, 항목이 4개씩이라 확장 컨테이너의 빈 틀로 보이지만 추론입니다. 백업에서 `.ips` 파일이나 `shutdown.log` 는 관찰 메모에 나오지 않았습니다.

| 도메인 | 항목 수 |
|---|---|
| `AppDomainPlugin-com.apple.DiagnosticExtensions.sysdiagnose` | 4 |
| `AppDomainPlugin-com.apple.DiagnosticExtensions.CrashLogs`, `.Panic`, `.StackShot`, `.tailspin`, `.Microstackshot`, `.LowMemory`, `.HangTracer`, `.Sandbox`, `.WiFi`, `.VPN` 등 | 각 4 |
| `SysSharedContainerDomain-systemgroup.com.apple.osanalytics` | 3 |
| `SysSharedContainerDomain-systemgroup.com.apple.mobile.installationhelperlogs` | 5 |
| `SysSharedContainerDomain-systemgroup.com.apple.sharedpclogging` | 3 |

진단 관련 설정 파일에는 다음 키가 있었습니다. 값은 읽지 않았고, 키의 뜻은 자료로 확인하지 못해 풀지 않습니다.

| 도메인 :: 경로 | 관찰한 키 |
|---|---|
| `RootDomain :: Library/Preferences/com.apple.CrashReporter.plist` | `ExcResourceDiagInfo_` 뒤에 프로세스 이름이 붙은 키 여러 개(datetime; 관찰 예 akd, bird, geod, recentsd, webprivacyd, cloudd, passwordbreachd), `NANDTaskScheduler_Priority` (int), `defTS` (int) |
| `RootDomain :: Library/Preferences/com.apple.osanalyticshelper.plist` | `stability-monitor.lastBuild` (str), `stability-monitor.lastBuild-hasSupplementalBuild` (bool), `retryCount` (int), `stability-monitor.baselineCrashCount` (dict), `lastSuccess` (float), `stability-monitor.baselineVersions` (dict), `stability-monitor.baselineUptime` (dict) |
| `HomeDomain :: Library/Preferences/com.apple.osanalytics.addaily.plist` | `netUsageBaseline` (프로세스·번들 이름별 사전) |

`ExcResourceDiagInfo_` 키는 이름으로 보아 프로세스별 자원 초과 진단 시각일 수 있지만 출처로 확인하지 못했고, 키에 붙은 프로세스 이름은 통합 로그에서 거를 후보로만 씁니다. 백업 구조는 [로컬 백업](../../01-foundations/backups/local-backup/index.md), plist 읽는 법은 [속성 목록 파일](../../01-foundations/data-formats/plist.md) 에서 다룹니다.

## 구조

### Shutdown.log

Shutdown.log 는 묶음 안 `system_logs.logarchive` 폴더의 `Extra` 하위 폴더에 있는 글자 파일이고, 재부팅할 때마다 기록이 이어서 쌓입니다[1]. 재부팅이 시작될 때 아직 돌고 있는 "client" 프로세스를 PID 와 실행 파일 경로로 남기고, 종료를 준비하며 메모리 버퍼를 비우는 시점을 UNIX 시각으로 적습니다[1]. 정상 재부팅을 늦춘 프로세스가 여기 남아서, 기기에 몰래 머무는 프로세스를 찾는 데 쓸 수 있습니다[1].

Kaspersky 는 알려진 스파이웨어 감염 사례에서 이 파일에 남은 경로를 비교했습니다[1].

| 사례 | Shutdown.log 에 나타난 경로 |
|---|---|
| Pegasus, Reign | `/private/var/db/` 아래 |
| Predator | `/private/var/tmp/` 아래 |

출처가 Pegasus 사례에서 든 경로는 다음과 같습니다[1].

```
/private/var/db/com.apple.xpc.roleaccountd.staging/rolexd
```

Kaspersky 의 공개 도구 iShutdown 은 한 번의 재부팅 전에 지연(delay)이 3번 이상 있거나, `/private/var/db/`·`/private/var/tmp/` 아래 경로의 프로세스가 남아 있으면 이상으로 봅니다[4]. 다만 Kaspersky 글은 감염되지 않은 기기에서도 재부팅 한 번에 지연 알림이 두세 번 나온 적이 있고, 의심스러웠던 것은 네 번을 넘는 경우였다고 적었습니다[1]. 그래서 지연 횟수만으로 판정하지 않고 경로와 함께 봅니다. 로그 한 줄의 정확한 문구는 확인한 자료에 인용이 없어서 이 페이지에는 줄 예시를 싣지 않습니다.

## 증거로서 의미

### 증명하는 것

sysdiagnose 는 묶음을 만든 순간의 프로세스 목록·설정·로그를 담아서, 그 시점에 기기에서 무엇이 돌고 있었는지 보여 줍니다. Shutdown.log 는 각 재부팅 때 늦게까지 남아 있던 프로세스의 PID 와 경로, 버퍼를 비운 시각을 보여 줍니다[1]. 경로가 `/private/var/db/`·`/private/var/tmp/` 아래이면 알려진 스파이웨어 사례와 같은 모양이라는 사실까지 말할 수 있습니다[1][4].

### 증명하지 못하는 것

Shutdown.log 에 이상한 경로가 있다고 감염이 확정되지는 않고, 없다고 감염이 없다고 말할 수도 없습니다. 이 방법은 Kaspersky 가 "가벼운 탐지 방법" 으로 소개한 것이고[1], 재부팅이 있어야 기록이 생기며[1] 기록을 얼마나 오래 남기는지는 확인한 자료가 없습니다. 통합 로그는 저장 한도 안에서만 남아서[5] 묶음을 늦게 만들수록 앞선 기록이 빠졌을 수 있습니다. 프로세스 목록은 만든 순간의 상태라서 그 전에 끝난 프로세스는 담지 않습니다.

보고서에는 "스파이웨어에 감염되었다" 가 아니라 "이 시각의 재부팅 기록에 `/private/var/tmp/` 아래 경로의 프로세스가 남아 있었고, 이는 알려진 사례와 같은 모양이다" 처럼 기록이 말하는 만큼만 씁니다. 판정과 후속 조사는 [스파이웨어 감염 흔적](../../04-scenarios/incident/spyware.md) 에서 다룹니다.

## 시각 해석

Shutdown.log 의 버퍼 비우기 시각은 UNIX 시각이라서[1] 1970-01-01 UTC 부터 센 초로 읽고, 현지 시각으로 옮길 때는 기기 시간대를 적용합니다. 묶음 안 파일마다 시각 형식이 다르고 통합 로그의 시각 해석은 [통합 로그에서 찾을 것](unified-log-events.md) 에서 다룹니다.

로컬 백업의 `osanalyticshelper.plist` 에 있는 `lastSuccess` 는 형식이 float 라 Mac 절대 시각(2001-01-01 기준 초)일 가능성이 있지만 확인하지 못했습니다. 두 기준을 섞으면 31년이 어긋나서, 값을 읽을 때 두 기준으로 모두 바꿔 보고 다른 기록과 맞는 쪽을 고릅니다. 시각 값 종류는 [시각 값](../../01-foundations/value-decoding/time-values.md) 에서 다룹니다.

## 함정과 한계

- **있을 것이라는 기대.** 묶음은 사용자가 만들어야 생기고, 버튼 조합·파일 이름 형식·정확한 설정 경로는 Apple 안내 PDF 를 열지 못해 이 페이지에서 확인하지 못했습니다.
- **만든 시점의 사진.** 묶음은 만든 순간의 상태이고, 통합 로그는 저장 한도가 있어[5] 오래된 기록이 빠질 수 있습니다. 보존 기간은 확인한 자료가 없습니다.
- **재부팅이 있어야 하는 기록.** Shutdown.log 는 재부팅할 때만 쌓여서[1], 오래 재부팅하지 않은 기기에서는 관심 기간의 기록이 없을 수 있습니다.
- **하위 경로.** 공개 도구가 읽는 파일 이름은 알지만 묶음 안의 하위 경로는 출처에 없어서[2], 도구가 파일을 찾지 못하면 이름으로 직접 찾아봅니다.
- **로컬 백업과 혼동.** 로컬 백업의 진단 확장 도메인은 이름만 sysdiagnose 와 비슷하고, 묶음이 들어 있다는 근거는 없습니다.

## 직접 분석해 보기

### 헥스로

묶음은 `.tar.gz` 라서 원본의 해시를 떠 둔 뒤 사본을 보통의 압축 해제 도구로 풀고, Shutdown.log 는 글자 파일이라 헥스 편집기 대신 글자 편집기로 엽니다. 줄 문구를 인용한 자료가 없어서 헥스·글자 예시는 싣지 않습니다.

### 공개 도구로

Kaspersky 의 iShutdown 은 세 부분으로 나뉩니다[1][4].

| 도구 | 하는 일 | 입력 |
|---|---|---|
| `iShutdown_detect` | 이상 항목을 찾습니다 | sysdiagnose `.tar.gz` |
| `iShutdown_parse` | 기록을 CSV 로 뽑고 해시 요약과 원본을 함께 남깁니다 | sysdiagnose `.tar.gz` |
| `iShutdown_stats` | 월별 재부팅 횟수, 처음과 마지막 재부팅 시각을 셉니다 | 묶음에서 풀어 낸 `shutdown.log` |

EC-DIGIT-CSIRC 의 sysdiagnose 도구는 묶음 전체를 읽어, 설치 앱 목록(apps), 여러 출처의 프로세스 목록 교차 비교(ps_everywhere·ps_matrix), Timesketch 타임라인, Wi-Fi 위치(GPX·KML), YARA 검사를 돌립니다[2]. 여러 파일에 나오는 프로세스를 한 표로 모아 보면 어느 한 파일에만 나오는 프로세스를 가려낼 수 있습니다.

분석 순서는 다음과 같습니다.

1. 묶음의 해시를 떠 두고 사본을 풉니다.
2. SystemVersion plist 로 OS 버전을 확인합니다.
3. iShutdown 으로 이상 항목과 재부팅 통계를 뽑고, 재부팅 시각이 사용자가 기억하는 재부팅과 맞는지 봅니다.
4. 이상 경로의 프로세스를 `ps.txt`·UUIDToBinaryLocations plist·crashes 폴더의 `.ips` 에서 다시 찾습니다.
5. 그 프로세스 이름으로 `system_logs.logarchive` 를 거릅니다. 방법은 [통합 로그에서 찾을 것](unified-log-events.md) 에서 다룹니다.

## 교차 검증

| 함께 볼 아티팩트 | 맞춰 볼 것 |
|---|---|
| [통합 로그에서 찾을 것](unified-log-events.md) | Shutdown.log 가 가리킨 프로세스가 같은 부팅 안에서 남긴 레코드 |
| [충돌·진단 기록](../app-usage/diagnostics.md) | 같은 프로세스의 충돌 기록과 시각 |
| [설치된 앱](../app-usage/installed-apps.md) | 묶음의 앱 설치 로그와 설치 앱 목록 |
| [전원 로그](../app-usage/powerlog.md) | 묶음 안 powerlogs DB 의 앱 실행 시간대 |
| [와이파이 기록](../network/wifi.md) | 묶음의 Wi-Fi 파일과 기기에 저장한 네트워크 |
| [설정 값](../system-account/preferences.md) | 관찰한 로컬 백업의 `HomeDomain :: Library/Preferences/com.apple.springboard.plist` 에 `SBLastKnownShutdownDate` (datetime) 키가 있었습니다. 이름으로 보아 마지막 종료 시각일 수 있지만 뜻은 확인하지 못했고, Shutdown.log 의 마지막 재부팅 시각과 비교해 볼 후보입니다 |

감염 의심 기기에서 이 파일들을 보는 순서는 [악성 코드·스파이웨어 흔적](../../03-techniques/analysis/spyware-triage/index.md), 여러 기록을 한 시간 축에 놓는 방법은 [타임라인 작성](../../03-techniques/analysis/timeline/index.md) 에서 다룹니다.

## 실습

sysdiagnose 묶음이 들어 있는 공개 검체를 구했다면 다음 질문으로 풀어 봅니다. 공개 검체에 따라 묶음이 없을 수 있어서, 먼저 `.tar.gz` 가 있는지부터 확인합니다.

1. SystemVersion plist 가 가리키는 OS 버전은 무엇이고, EC-DIGIT-CSIRC 도구가 시험한 버전에 들어갑니까?
2. Shutdown.log 에 기록된 재부팅은 몇 번이고, 처음과 마지막 재부팅은 언제입니까?
3. 재부팅 한 번에 지연이 3번 이상 나온 경우가 있습니까? 있다면 그때 남아 있던 프로세스는 무엇입니까?
4. `/private/var/db/` 나 `/private/var/tmp/` 아래 경로의 프로세스가 있습니까? 있다면 `ps.txt` 와 통합 로그에서도 같은 이름이 나옵니까?

## 참고 문헌

1. Kaspersky Securelist, "A lightweight method to detect potential iOS malware" — https://securelist.com/shutdown-log-lightweight-ios-malware-detection-method/111734/
2. EC-DIGIT-CSIRC, sysdiagnose (GitHub README) — https://github.com/EC-DIGIT-CSIRC/sysdiagnose
3. Apple Developer, Profiles and Logs (iOS) — https://developer.apple.com/bug-reporting/profiles-and-logs/?platform=ios
4. Kaspersky, iShutdown (GitHub README) — https://github.com/KasperskyLab/iShutdown
5. Apple Developer Documentation, "Generating Log Messages from Your Code" — https://developer.apple.com/tutorials/data/documentation/os/generating-log-messages-from-your-code.json
