---
title: "충돌·진단 기록"
parent: "아티팩트 · 앱 설치·사용 흔적"
nav_order: 440
---

# 충돌·진단 기록 (Analytics·Crash Logs)

## 한 줄 요약

충돌·진단 기록은 앱이나 시스템 프로세스가 충돌하거나 강제로 끝났을 때 iOS 가 남기는 보고서와 분석 데이터이고, iOS 15 부터 JSON 으로 저장되는 `.ips` 보고서에서 어떤 프로세스가 언제 시작해 언제 끝났는지, 누가 끝냈는지, 어떤 OS 빌드였는지를 읽을 수 있습니다.

## 무엇을 기록하나 · 왜 생기나

기기 안에서 만들어진 충돌 보고서와 진단 로그는 설정의 "분석 및 향상 (Analytics & Improvements)" 아래 "분석 데이터 (Analytics Data)" 에서 볼 수 있고, 기기를 Mac 이나 Windows 컴퓨터에 연결해 옮길 수도 있습니다[1]. 로그 이름은 충돌 보고서가 앱 실행 파일 이름 뒤에 날짜·시각을 붙인 꼴이고, 메모리를 너무 많이 써서 종료된 경우는 `JetsamEvent_` 로 시작합니다[1]. 확장자는 흔히 `.crash` 와 `.ips` 입니다[1]. 짝 지은 Apple Watch 의 충돌 보고서도 iPhone 에서 볼 수 있습니다[1].

```
<앱 실행 파일 이름>_<날짜시각>.ips
JetsamEvent_<날짜시각>.ips
```

Xcode 의 Organizer 로는 오지 않아 기기에서 따로 얻어야 하는 보고서에는 워치독(앱 실행이 느린 경우 등), 잘못된 코드 서명으로 난 충돌, 과열, jetsam(메모리 과다) 보고서가 있습니다[1]. 기기를 조사할 때는 이 종류들이 기기에 남아 있는지 따로 챙겨 봅니다.

충돌 보고서 밖에도 분석 데이터가 여럿 있습니다. MVT 는 네트워크·인증서 고정 (pinning)·TLS 실패 같은 분석 정보를 담은 SQLite, 프로세스별 데이터 사용 이력 plist, iOS 업데이트 이력을 담은 `.ips`, 종료할 때 SIGTERM 뒤에도 끝나지 않은 프로세스의 PID·경로를 담은 `shutdown.log` 를 읽습니다[3].

## 위치와 버전별 차이

### 버전별 형식

| iOS | 충돌 보고서 형식 | 출처 |
|---|---|---|
| 버전 밝히지 않음 | 확장자는 흔히 `.crash`·`.ips`. iOS 14 이하 본문 형식은 검체에서 확인 | [1] |
| 15 이후 | `.ips` 확장자의 JSON. iOS 15·macOS 12 부터 | [2] |

### MVT 가 읽는 분석 데이터

MVT 모듈별 경로와 수집 방식은 다음과 같습니다[3].

| 모듈 | 경로 | 담긴 것 | 얻는 수집 방식 |
|---|---|---|---|
| Analytics | `private/var/Keychains/Analytics/*.db` (SQLite) | 네트워크·인증서 고정·TLS 실패 등 분석 정보 | 암호화 백업, 전체 덤프 |
| OSAnalyticsADDaily | `private/var/mobile/Library/Preferences/com.apple.osanalytics.addaily.plist` | 프로세스별 데이터 사용 이력 | 일반 백업, 전체 덤프 |
| IOSVersionHistory | `private/var/db/analyticsd/Analytics-Journal-*.ips` | iOS 업데이트 이력 | 일반 백업, 전체 덤프 |
| ShutdownLog | `private/var/db/diagnostics/shutdown.log` | 종료 때 끝나지 않은 프로세스의 PID·경로 | 암호화 백업, 전체 덤프 |

`shutdown.log` 를 읽는 법과 버전별 동작은 [sysdiagnose 묶음](../../01-foundations/backups/sysdiagnose.md) 에서 다룹니다. 앱 충돌 보고서 `.ips` 가 기기 안 어느 폴더에 저장되는지는 수집한 검체에서 `.ips` 파일을 이름으로 찾아 실제 경로를 적습니다.

### 로컬 백업에 보이는 것

로컬 백업에는 `.ips` 파일도, `Logs/CrashReporter` 경로도 없을 수 있어서, 백업만 보고 충돌 보고서 본문이 없다고 판단하지 않습니다. 백업에는 진단과 이름이 닿는 설정 plist 와 도메인이 있습니다.

| 도메인 :: 경로 | 키 |
|---|---|
| `RootDomain :: Library/Preferences/com.apple.CrashReporter.plist` | `ExcResourceDiagInfo_<프로세스 이름>` (datetime) 23개(`akd`, `bird`, `geod`, `cloudd` 등 시스템 프로세스), `patternMatchServiceCrashes.bootUUID` (str) |
| `HomeDomain :: Library/Preferences/com.apple.ReportCrashService.plist` | `memoryExceptionProcesses.bootUUID` (str), `patternMatchServiceCrashes.bootUUID` (str) |
| `RootDomain :: Library/Preferences/com.apple.ReportCrash.plist` | `TrialCache` 아래 `experiments`, `lastCheckTime`, `rollouts` |
| `HomeDomain :: Library/Preferences/com.apple.osanalytics.addaily.plist` | `netUsageBaseline` 아래에 프로세스·번들 ID 이름이 키로 있음 |
| `HomeDomain :: Library/Preferences/com.apple.analyticsagent.plist` | `AppUsageSyncTime` (float), `ODDAssistantLLMSiriDigestSyncTime` (float) |

`com.apple.osanalyticshelper.plist` 의 키는 [sysdiagnose 묶음](../../01-foundations/backups/sysdiagnose.md) 에 정리되어 있습니다. `bbtrace.` 로 시작하는 키는 `CrashReporter.plist` 가 아니라 `WirelessDomain :: Library/Preferences/com.apple.AppleBasebandManager.plist` 아래에 있습니다.

관련 도메인으로는 `SysSharedContainerDomain-systemgroup.com.apple.osanalytics`(항목 3개), `…ReportMemoryException`(항목 3개), `…powerexceptions`(항목 4개), `SysContainerDomain-com.apple.metrickitd`(항목 11개), `AppDomain-com.apple.DiagnosticsReporter`, `AppDomainPlugin-com.apple.DiagnosticExtensions.CrashLogs`·`LowMemory`·`Panic`·`HangTracer` 가 있습니다. 이 키와 도메인의 뜻과 내용을 밝힌 공개 자료는 없습니다.

## 구조

iOS 15 이후 `.ips` 파일에는 JSON 객체가 두 개 있고, 첫 줄은 IPS 메타데이터, 나머지는 보고서 본문입니다[2]. 메타데이터의 `bug_type` 이 309 면 충돌 보고서, 288 이면 스택샷입니다[2]. 부분별 키와 뜻은 다음과 같습니다[2].

| 부분 | 키 | 뜻 |
|---|---|---|
| 메타데이터 | `name`, `bug_type`, `bundleID`, `build_version`, `incident_id`, `platform`, `timestamp` | `platform` 2 는 iOS. `timestamp` 는 기록을 관리하려는 값 |
| 본문 | `captureTime` | 충돌 시각 |
| 본문 | `procLaunch` | 프로세스가 시작한 시각 |
| 본문 | `procName`, `procPath`, `pid`, `parentProc`, `parentPid` | 프로세스와 부모 프로세스 |
| 본문 | `bundleInfo` (`CFBundleIdentifier`, `CFBundleShortVersionString`, `CFBundleVersion`) | 번들 ID 와 앱 버전 |
| 본문 | `storeInfo` (`applicationVariant`, `itemID`, `deviceIdentifierForVendor`) | `itemID` 는 스토어에서 앱을 가리키는 Apple 식별자, `deviceIdentifierForVendor` 는 TestFlight 빌드에만 있음 |
| 본문 | `exception` (`type`, `signal`, `codes`, `subtype`, `message`) | 예외 정보 |
| 본문 | `termination` (`byProc`, `byPid`, `code`, `indicator`, `namespace`, `flags`) | 종료 정보. `byProc`·`byPid` 는 프로세스를 끝낸 쪽 |
| 본문 | `osVersion` (`train`, `build`, `releaseType`, `isEmbedded`), `modelCode` | OS 빌드와 기종 |
| 본문 | `uptime` | 부팅 뒤 흐른 초 |
| 본문 | `crashReporterKey` | 기기별 익명 식별자 |
| 본문 | `incident`, `usedImages`, `threads`, `vmSummary` 등 | 그 밖의 키 |

`crashReporterKey` 는 같은 기기의 보고서끼리 값이 같고, 기기를 지우면 바뀝니다[2].

## 증거로서 의미

**증명하는 것.** 보고서 한 건은 이 번들 ID·버전의 프로세스가 `procLaunch` 에 시작해 `captureTime` 에 충돌했고, 그때 OS 빌드와 기종이 무엇이었는지를 보여 줍니다[2]. `termination` 에는 어떤 프로세스가 끝냈는지가, `parentProc` 에는 부모 프로세스가 남습니다[2]. `crashReporterKey` 가 같은 보고서들은 같은 기기에서 나왔다고 볼 수 있고, 한 기기의 보고서들 사이에서 값이 바뀌면 그 사이에 기기를 지웠을 가능성을 살펴볼 근거가 됩니다[2]. `storeInfo.itemID` 로 앱을 스토어 항목과 이을 수 있습니다[2].

**증명하지 못하는 것.** 충돌 보고서는 사용자가 무엇을 하다가 충돌했는지 알려 주지 않고, 앱이 충돌했다는 사실만으로 악성 행위나 공격이 있었다고 말할 수 없습니다. 보고서가 없다고 그 앱을 쓰지 않았다고 말할 수도 없습니다. 이름에 진단이 들어간 plist 키들은 뜻이 밝혀지지 않아서, 키가 있다는 사실 말고는 증거로 쓰지 않습니다.

보고서에는 "앱이 공격을 받았다" 대신 "번들 ID `com.example.app` 버전 이 값의 프로세스가 이 시각에 시작해 이 시각에 이 예외로 종료된 보고서가 있다" 처럼 씁니다.

## 시각 해석

실행과 종료 시각은 본문의 `procLaunch` 와 `captureTime` 을 쓰고, 메타데이터의 `timestamp` 는 기록을 관리하려는 값이라 사건 시각으로 쓰지 않습니다[2]. 두 칸의 문자열 형식과 시간대 표기는 검체에서 확인합니다. 값을 그대로 옮기고, 시간대 표시가 있는지부터 봅니다.

`uptime` 은 부팅 뒤 흐른 초라서[2], `captureTime` 에서 `uptime` 을 빼면 그 보고서 기준으로 기기를 켠 무렵을 어림할 수 있습니다. 여러 보고서에서 어림한 부팅 시각이 크게 다르면 그 사이에 재부팅이 있었다는 뜻일 수 있고, 재부팅 기록은 [통합 로그에서 찾을 것](../logs/unified-log-events.md) 과 맞춰 봅니다.

백업 plist 의 `ExcResourceDiagInfo_…` 는 `datetime` 형이라 도구가 날짜로 풀어 주지만 무슨 시각인지는 알려져 있지 않고, `analyticsagent.plist` 의 두 키는 `float` 형이라 기준점을 따로 확인해야 합니다. 시각 기준은 [시각 값](../../01-foundations/value-decoding/time-values.md) 에서 다룹니다.

## 함정과 한계

**메타데이터 시각을 사건 시각으로 쓰지 않습니다.** 첫 줄의 `timestamp` 는 기록 관리용 값입니다[2].

**`bug_type` 부터 봅니다.** 같은 `.ips` 확장자라도 309 는 충돌 보고서, 288 은 스택샷이고[2], iOS 업데이트 이력처럼 충돌과 관계없는 내용도 `.ips` 로 저장됩니다[3]. 확장자만 보고 모두 충돌로 세지 않습니다.

**iOS 14 이하 보고서는 형식이 다를 수 있습니다.** JSON 형식은 iOS 15 부터라서[2], 그 전 보고서에 이 페이지의 키가 그대로 있다고 보지 않습니다.

**수집 방식에 따라 얻는 범위가 다릅니다.** MVT 의 Analytics 와 ShutdownLog 모듈은 암호화 백업이나 전체 덤프에서만 동작합니다[3]. 암호화하지 않은 백업에서 이 기록이 없으면 수집 방식 때문인지부터 확인합니다([모바일 증거 확보](../../03-techniques/acquisition/mobile-acquisition/index.md)).

**지우기와 조작.** 기기를 지우면 `crashReporterKey` 가 바뀌어서[2], 수집 전에 초기화한 기기라면 새 값의 보고서만 남을 수 있습니다. 초기화 흔적은 [초기화와 복원 흔적](../system-account/erase-restore.md), 증거 인멸 판단은 [증거를 없애려 했나](../../04-scenarios/activity/anti-forensics/index.md) 에서 봅니다.

## 직접 분석해 보기

### 헥스로 한 번

아래는 명세로 만든 예시이고 특정 검체에서 나온 값이 아닙니다. JSON 형식 `.ips` 는 첫 바이트가 `{`(`0x7B`)이고, 메타데이터 객체가 한 줄로 끝나 줄바꿈(`0x0A`) 뒤에 본문 객체가 다시 `{` 로 시작합니다[2].

```
00000000  7B ...                     {  (메타데이터 한 줄)
          ... 7D 0A 7B ...           } 줄바꿈 {  (본문 시작)
```

키 모양은 다음과 같고, 값은 모두 줄임표로 비워 두었습니다. 값이 문자열인지 숫자인지도 검체에서 확인합니다.

```
{"name":"…","bug_type":"…","bundleID":"…","build_version":"…","incident_id":"…","platform":…,"timestamp":"…"}
{
  "captureTime" : "…",
  "procLaunch" : "…",
  "procName" : "…",
  "bundleInfo" : { "CFBundleIdentifier" : "…" },
  "termination" : { "byProc" : "…" },
  "crashReporterKey" : "…",
  "uptime" : …
}
```

### 공개 도구로 한 번

두 객체를 따로 읽어야 해서, Python 표준 라이브러리 `json` 으로 첫 줄과 나머지를 나눠 엽니다.

```python
import json, sys
with open(sys.argv[1], encoding="utf-8") as f:
    meta = json.loads(f.readline())
    body = json.loads(f.read())
print(meta.get("bug_type"), meta.get("bundleID"))
print(body.get("procLaunch"), body.get("captureTime"), body.get("uptime"))
print(body.get("termination"), body.get("crashReporterKey"))
```

보고서가 여러 개면 `crashReporterKey` 와 `osVersion` 별로 묶어 기기와 OS 빌드가 바뀐 지점을 찾습니다. 분석 데이터 쪽은 MVT 의 Analytics, OSAnalyticsADDaily, IOSVersionHistory, ShutdownLog 모듈이 읽어 줍니다[3]. 스파이웨어 점검에서 이 모듈들을 쓰는 흐름은 [악성 코드·스파이웨어 흔적](../../03-techniques/analysis/spyware-triage/index.md) 에 있습니다.

## 교차 검증

충돌 시각 앞뒤의 시스템 기록은 [통합 로그에서 찾을 것](../logs/unified-log-events.md) 과 [sysdiagnose 안의 로그](../logs/sysdiagnose-logs.md), 그 시각의 앱 실행 상태는 [전원 로그](powerlog.md) 와 [바이옴](biome/index.md) 에서 봅니다. 번들 ID 와 `itemID` 는 [설치된 앱](installed-apps.md) 과 [앱 스토어 기록](app-store.md), `modelCode` 와 OS 빌드는 [기기 정보](../system-account/device-info.md) 와 맞춥니다. 조사 흐름은 [스파이웨어 감염 흔적](../../04-scenarios/incident/spyware.md) 과 [악성 코드는 어디서 들어왔나](../../04-scenarios/incident/initial-access.md) 를 봅니다.

## 실습

공개 검체(NIST CFReDS 등의 iOS 이미지)나 직접 받은 sysdiagnose 에 `.ips` 파일이 있다면 다음 질문을 풀어 봅니다.

1. `.ips` 파일이 모두 몇 개이고, `bug_type` 별로 몇 개씩입니까?
2. `bug_type` 309 보고서 가운데 가장 이른 `captureTime` 과 가장 늦은 `captureTime` 은 언제입니까?
3. 모든 보고서의 `crashReporterKey` 가 같습니까? 다르다면 값이 바뀐 앞뒤 보고서의 `osVersion.build` 는 무엇입니까?
4. `captureTime` 에서 `uptime` 을 뺀 부팅 시각이 보고서마다 비슷합니까?
5. `termination.byProc` 에 나오는 프로세스 이름은 무엇이고, `JetsamEvent_` 로 시작하는 보고서는 몇 개입니까?

## 참고 문헌

- [1] Acquiring crash reports and diagnostic logs — Apple Developer Documentation — https://developer.apple.com/tutorials/data/documentation/xcode/acquiring-crash-reports-and-diagnostic-logs.md
- [2] Interpreting the JSON format of a crash report — Apple Developer Documentation — https://developer.apple.com/tutorials/data/documentation/xcode/interpreting-the-json-format-of-a-crash-report.md
- [3] Records extracted by mvt-ios — Mobile Verification Toolkit — https://docs.mvt.re/en/latest/ios/records/
