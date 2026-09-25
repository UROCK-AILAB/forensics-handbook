---
title: "스파이웨어 흔적 찾기"
parent: "악성 코드·스파이웨어 흔적"
grand_parent: "기법 · 분석"
nav_order: 1370
---

# 스파이웨어 흔적 찾기 (MVT)

MVT(Mobile Verification Toolkit)로 백업·sysdiagnose·전체 파일 시스템 추출을 모듈별로 파싱해 공개 지표와 대조하고, 지표에 걸리지 않아도 프로세스 기록과 shutdown.log 에서 이상한 실행 흔적을 찾는 방법입니다.

## 언제 쓰나

Apple 위협 알림을 받았거나, 언론인·활동가처럼 국가·용병형 스파이웨어의 표적이 될 만한 사람이 감염을 의심할 때 씁니다. 위협 알림이 어떤 경로로 오는지는 [악성 코드·스파이웨어 흔적](index.md) 허브에 정리했습니다. 구성 프로파일·권한·위치 요청 기록은 [구성 프로파일과 설정으로 찾기](profiles-settings.md) 가, 가까운 사람이 설치한 감시 앱은 [감시 앱 흔적](stalkerware.md) 이 맡습니다.

이 페이지에서 "" 가 붙은 경로와 이름은 암호화하지 않은 로컬 백업에서 이름만 확인한 것이고, 값은 보지 않았습니다.

## 절차

1. **자료를 모읍니다.** mvt-ios 는 로컬 백업, 전체 파일 시스템 추출, sysdiagnose 를 모두 입력으로 받습니다 [1]. 백업은 가능하면 암호화 백업으로 받습니다. MVT 문서는 모듈마다 "Backup (encrypted)" 표시를 달아 두었고, 통화 기록(Calls), Safari 방문 기록(SafariHistory), SafariBrowserState, InteractionC, Analytics, ShutdownLog 는 백업에서는 암호화 백업일 때만 나온다고 적었습니다 [1]. 받은 백업이 암호화됐는지는 `Manifest.plist` 의 `IsEncrypted` 키로 확인합니다. sysdiagnose 는 기기를 재부팅하거나 iOS 를 올리기 전에 받습니다. 그 까닭은 아래 shutdown.log 절에 있고, 받는 법은 [sysdiagnose 묶음](../../../01-foundations/backups/sysdiagnose.md) 에 있습니다.

2. **지표를 준비합니다.** MVT 가 읽는 지표는 STIX2 형식 파일(.stix2 또는 .json)이고, `--iocs` 로 여러 개를 넣을 수 있습니다 [2]. `mvt download-iocs` 로 공개 지표를 받고, `MVT_STIX2` 환경 변수에 콜론으로 구분한 경로를 넣어 두면 실행할 때마다 자동으로 불러옵니다 [2]. 공개 지표 저장소로는 AmnestyTech/investigations(Pegasus, Predator 등), mvt-project/mvt-indicators, Te-k/stalkerware-indicators(주로 Android 스토커웨어)가 있습니다 [2].

3. **모듈 결과를 봅니다.** 지표에 걸린 항목부터 보고, 걸린 것이 없어도 아래 모듈의 결과는 따로 훑습니다. 표는 MVT 문서의 모듈 가운데 이 페이지에서 쓰는 것만 골랐고, 전체 목록은 [1] 의 표에 있습니다. 마지막 칸은 관찰한 백업(암호화 안 함)에서 해당 파일을 찾았는지입니다.

   | 모듈 | 읽는 파일 (MVT 문서) [1] | 알려 주는 것 [1] | 관찰한 백업 |
   |---|---|---|---|
   | Datausage | `/private/var/wireless/Library/Databases/DataUsage.sqlite` | 프로세스별 네트워크 사용량 | `WirelessDomain :: Library/Databases/DataUsage.sqlite` 있음 |
   | Netusage | `/private/var/networkd/netusage.sqlite` | 프로세스별 네트워크 사용량 | 없음 |
   | OSAnalyticsADDaily | `/private/var/mobile/Library/Preferences/com.apple.osanalytics.addaily.plist` | 프로세스별 데이터 사용 이력 | `HomeDomain :: Library/Preferences/com.apple.osanalytics.addaily.plist` 있음 |
   | ShutdownLog | `/private/var/db/diagnostics/shutdown.log` | 종료할 때 SIGTERM 을 받은 프로세스. 백업은 암호화 백업만 | 관찰 메모에 없음. sysdiagnose 에도 들어 있음 [4] |
   | IDStatusCache | `/private/var/mobile/Library/Preferences/com.apple.identityservices.idstatuscache.plist` | 백업에서는 iOS 14.7 이전만 | 없음 |
   | SMS, SMSAttachments | `/private/var/mobile/Library/SMS/sms.db` | 메시지 속 링크와 첨부 | `HomeDomain :: Library/SMS/sms.db` 있음 |
   | Shortcuts | `/private/var/mobile/Library/Shortcuts/Shortcuts.sqlite` | 단축어 앱의 기록 | `HomeDomain :: Library/Shortcuts/Shortcuts.sqlite` 있음 |
   | WebkitResourceLoadStatistics | `observations.db` | 접속한 도메인과 시각 | `AppDomain-com.apple.mobilesafari :: Library/WebKit/WebsiteData/ResourceLoadStatistics/observations.db` 있음 |
   | WebkitSessionResourceLog | `full_browsing_session_resourceLog.plist` | 방문한 도메인이 불러온 리소스 | 관찰 메모에 없음 |
   | SafariHistory | `/private/var/mobile/Library/Safari/History.db` 또는 앱 컨테이너 안 `History.db` | 방문 기록 (암호화 백업) | 없음 |
   | VersionHistory | `/private/var/db/analyticsd/Analytics-Journal-*.ips` | iOS 업데이트 이력 | 관찰 메모에 없음 |
   | Manifest | 백업의 `Manifest.db` | 파일 경로의 도메인 이름을 지표와 대조 | `Files`, `Properties` 표 있음 |
   | CacheFiles | `*Cache.db` | HTTP 요청·응답 | 파일별 확인 안 함 |

   `OSAnalyticsADDaily` 파일에는 최상위 키 `netUsageBaseline` 아래에 프로세스·번들 ID 이름이 키로 들어 있었습니다.

4. **프로세스 기록의 불일치를 봅니다.** Amnesty 는 2021년 Pegasus 조사에서 `DataUsage.sqlite` 와 `netusage.sqlite` 의 프로세스 기록을 핵심 근거로 썼습니다 [3]. 악성 프로세스의 이름은 `ZPROCESS` 표에서 지워졌는데 `ZLIVEUSAGE` 표의 대응 행은 남아 있었고, Amnesty 는 깨끗한 아이폰에서는 이런 불일치를 보지 못했다고 적었습니다 [3]. 그래서 `ZLIVEUSAGE` 행 가운데 `ZPROCESS` 에 짝이 없는 행을 찾습니다. 2021년 보고서는 `ZLIVEUSAGE` 가 `ZPROCESS` 를 프로세스 ID 로 가리킨다고 설명했지만 [3], 관찰한 iOS 27.0 백업의 `ZLIVEUSAGE` 에는 `ZHASPROCESS` 와 함께 `ZBUNDLENAME`, `ZPROCNAME` 칸도 있었습니다. 두 표를 잇는 칸이 `ZHASPROCESS` 인지는 확인하지 못했고, 표 구조는 [앱별 데이터 사용량](../../../02-artifacts/network/data-usage.md) 에서 다룹니다.

   Amnesty 가 의심 프로세스로 든 이름은 `bh`, `roleaccountd`, `stagingd`, `msgacntd`, `gatekeeperd`, `PDPDialogs`, `rolexd` 이고, 정상 iOS 프로세스와 이름이 비슷한 `aggregatenotd`(정상은 `aggregated`), `ckkeyrollfd`(`ckkeyrolld`), `launchafd`(`launchd`)도 있었습니다 [3]. 악성 실행 파일은 `/private/var/db/com.apple.xpc.roleaccountd.staging/` 에 있었습니다 [3]. Amnesty 는 그 밖에 Safari 방문 기록(전체 리디렉션 경로는 남지 않음), Favicon 캐시, SessionResourceLog, `com.apple.identityservices.idstatuscache.plist`(앱이 조회한 Apple ID 기록), `com.apple.CrashReporter.plist`, WebKit IndexedDB·LocalStorage 폴더, `/private/var/wireless/Library/Caches/com.apple.coretelephony/Cache.db` 도 썼습니다 [3]. `com.apple.CrashReporter.plist` 는 감염 뒤에 쓰인 것으로 보았고, 충돌 보고를 끄려는 목적으로 추정했습니다 [3].

5. **shutdown.log 를 봅니다.** 아래 절의 방법으로 sysdiagnose 안의 shutdown.log 에서 `/private/var/db/` 나 `/private/var/tmp/` 아래 경로로 실행된 프로세스가 있는지 찾습니다.

6. **시간순으로 모읍니다.** 걸린 항목과 이상한 프로세스를 [타임라인 작성](../timeline/index.md) 방식으로 메시지 수신, Safari 방문, 업데이트 이력과 나란히 놓습니다. 링크가 들어온 경로를 따지는 순서는 [악성 코드는 어디서 들어왔나](../../../04-scenarios/incident/initial-access.md) 에 있습니다.

## shutdown.log

shutdown.log 는 sysdiagnose 압축 파일 안 `system_logs.logarchive\Extra` 에 있습니다 [4]. Kaspersky 는 sysdiagnose 가 보통 200~400MB 크기의 .tar.gz 로 몇 분 안에 만들어진다고 적었습니다 [4]. 재부팅이 시작될 때 아직 돌고 있는 "client" 프로세스를 PID 와 파일 경로로 기록하고, 시각은 UNIX 형식입니다 [4]. Pegasus 와 Reign 감염에서는 `/private/var/db/` 아래에서 실행된 경로가, Predator 감염에서는 `/private/var/tmp/` 아래 경로가 보였습니다 [4]. iVerify 가 든 2022년 Pegasus 지표 예는 shutdown.log 안의 `/private/var/db/com.apple.xpc.roleaccountd.staging/com.apple.WebKit.Networking` 항목입니다 [5]. Kaspersky 는 iShutdown_detect, iShutdown_parse, iShutdown_stats 로 이루어진 Python3 스크립트(iShutdown)를 GitHub 에 공개했습니다 [4].

| iOS 버전 | shutdown.log 보존 |
|---|---|
| iOS 18 이하 | 재부팅마다 덧붙여 누적 [5] |
| iOS 26 | 재부팅마다 덮어씀. iOS 26 으로 올린 뒤 재부팅하면 예전 감염 흔적이 사라짐 [5] |
| iOS 27 | 덮어쓰기가 그대로인지 확인하지 못함 |

iVerify 는 iOS 26 으로 올리기 전에 sysdiagnose 를 받아 두라고 권합니다 [5]. iOS 18 이하에서는 containermanagerd 로그가 부팅 이벤트를 담고 몇 주 동안 남을 수 있다고도 적었습니다 [5].

## 도구

MVT 의 mvt-ios 가 백업·전체 파일 시스템 추출·sysdiagnose 를 모듈별로 파싱합니다 [1]. shutdown.log 는 Kaspersky 의 iShutdown 스크립트로 따로 볼 수 있습니다 [4]. 모듈 결과를 원본과 맞춰 볼 때는 sqlite3 로 `DataUsage.sqlite` 를 직접 열어 `ZPROCESS` 와 `ZLIVEUSAGE` 를 비교합니다. 도구 결과를 보고서에 쓰기 전에 확인하는 방법은 [도구 검증](../../reporting/tool-validation.md) 에 있습니다.

## 함정과 한계

지표 대조는 알려진 지표만 찾습니다. 걸린 것이 없으면 "쓴 지표와 일치하는 항목이 없다" 까지만 말할 수 있고, 감염이 없었다는 결론으로 넘어가지 않습니다. 정상 프로세스와 비슷한 이름은 몇 글자만 달라서 이름만 훑으면 놓치기 쉽습니다.

암호화하지 않은 백업에서는 Safari 방문 기록처럼 암호화 백업에만 들어가는 기록이 빠집니다 [1]. 관찰한 백업(암호화 안 함)에는 `History.db` 가 없었고 `observations.db` 는 있었습니다. `netusage.sqlite` 는 출처끼리 말이 다릅니다. Amnesty 는 iTunes 백업에 없다고 적었고 [3], MVT 문서 표는 Backup 에도 적용된다고 표시하며 [1], 관찰한 백업에는 없었습니다. `com.apple.identityservices.idstatuscache.plist` 도 관찰한 백업에 없었고, MVT 문서의 "백업은 iOS 14.7 이전" 과 맞습니다 [1].

Amnesty 조사는 2016년부터 iOS 14.6(2021년 7월)까지이고, iOS 14.6 까지 패치한 iPhone 12 에서도 무클릭 공격 흔적을 찾았습니다 [3]. Amnesty 는 Pegasus 가 더는 재부팅 뒤 지속하지 않는 것으로 본다고 적었고, 재부팅하면 실행 파일을 비휘발 저장소에서 찾을 수 없습니다 [3]. 실행 파일을 찾지 못해도 프로세스 기록과 shutdown.log 는 따로 확인합니다. shutdown.log 는 사용자가 재부팅해야 기록이 생기고 [4], iOS 26 부터는 재부팅마다 덮어써집니다 [5].

`DataUsage.sqlite` 의 `ZTIMESTAMP` 가 Mac 절대 시각인지는 확인하지 못했습니다. 관찰한 표는 `Z_PK`, `Z_ENT`, `Z_OPT` 칸과 `Z_METADATA` 표가 있는 Core Data 형식이었습니다. 시각을 보고서에 쓰기 전에 [시각 값](../../../01-foundations/value-decoding/time-values.md) 의 방법으로 기준을 확인합니다. `RootDomain :: Library/Preferences/com.apple.osanalyticshelper.plist` 의 `stability-monitor.` 로 시작하는 키도 관찰했지만, 탐지에 어떻게 쓰는지는 확인하지 못했습니다.

## 결과를 어떻게 해석하나

지표에 걸린 항목은 "이 파일의 이 행이 이 공개 지표의 도메인·프로세스 이름과 일치한다" 로 씁니다. 지표 없이 찾은 이상 징후는 "`ZLIVEUSAGE` 에 `ZPROCESS` 와 짝이 없는 행이 있고, Amnesty 는 깨끗한 기기에서 이런 불일치를 보지 못했다고 보고했다" 처럼 관찰과 출처를 나눠 씁니다. 어떤 스파이웨어인지, 누가 보냈는지는 이 기록만으로 증명하지 못합니다. 조사 전체의 흐름과 보고서 문장 예는 [스파이웨어 감염 흔적](../../../04-scenarios/incident/spyware.md) 시나리오에 있습니다.

## 참고 문헌

1. Records extracted by mvt-ios — Mobile Verification Toolkit — https://docs.mvt.re/en/latest/ios/records/
2. Indicators of Compromise — Mobile Verification Toolkit — https://docs.mvt.re/en/latest/iocs/
3. Forensic Methodology Report: How to catch NSO Group's Pegasus — Amnesty International Security Lab (2021-07) — https://securitylab.amnesty.org/latest/2021/07/forensic-methodology-report-how-to-catch-nso-groups-pegasus/
4. Detecting iOS malware via Shutdown.log file — Securelist (Kaspersky) — https://securelist.com/shutdown-log-lightweight-ios-malware-detection-method/111734/
5. Key IOCs for Pegasus and Predator Spyware Cleaned With iOS 26 Update — iVerify — https://iverify.com/blog/key-iocs-for-pegasus-and-predator-spyware-cleaned-with-ios-26-update
