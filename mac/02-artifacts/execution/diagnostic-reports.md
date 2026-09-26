---
title: "충돌·진단 보고서"
parent: "아티팩트 · 프로그램 실행 흔적"
nav_order: 750
---

# 충돌·진단 보고서 (DiagnosticReports)

충돌 보고서 (Crash Report)는 프로세스가 비정상으로 끝날 때 macOS 가 남기는 파일이고, macOS 12 Monterey 부터는 JSON 을 담은 `.ips` 파일로 저장되어 죽은 프로세스의 실행 파일 경로·부모 프로세스·시작 시각·충돌 시각·적재된 라이브러리까지 한 파일에서 읽을 수 있습니다.

## 무엇을 기록하나 · 왜 생기나

앱이 충돌하면 운영체제가 그 순간의 프로세스 정보를 보고서로 남기고, iOS 15·macOS 12 부터는 이 보고서를 JSON 형식으로 `.ips` 확장자 파일에 저장합니다 [1]. 보고서에는 충돌한 프로세스의 이름과 실행 파일 경로, 프로세스 ID, 부모 프로세스, 프로세스가 시작된 시각과 충돌한 시각, 프로세스가 끝난 방식, 스레드별 백트레이스, 적재된 바이너리 이미지 목록이 들어 있습니다 [1]. 메모리를 많이 써서 끝난 경우에는 `JetsamEvent_` 로 시작하고 뒤에 날짜·시각이 붙는 이름의 보고서가 따로 생깁니다 [2].

`.crash` 파일도 있지만, 보고서를 보낼 때는 `.ips` 가 있으면 `.crash` 대신 `.ips` 를 보냅니다 [2]. `.spin`, `.hang`, `.diag` 같은 다른 확장자의 보고서는 이 페이지에서 다루지 않습니다.

프로그램 실행 흔적으로 보면, 충돌 보고서에는 그 실행 파일이 이 맥에서 돌다가 이 시각에 끝났다는 내용과 실행 파일 경로가 함께 남아서, 실행 파일을 지운 뒤에도 보고서로 경로를 찾을 수 있습니다.

## 위치와 버전별 차이

보고서 폴더는 콘솔 앱으로 찾습니다. 응용 프로그램의 유틸리티 폴더에서 콘솔 앱을 열고 "Crash Reports" 를 고른 뒤, 파일 이름을 오른쪽 클릭해 "Reveal in Finder" 를 누르면 보고서가 있는 폴더가 열립니다 [2]. 라이브 맥에서는 이 방법으로 실제 폴더를 확인해 보고서에 적습니다. 디스크 이미지에서는 `.ips`·`.crash` 확장자와 `JetsamEvent_` 이름으로 볼륨 전체를 찾고, 찾은 폴더가 사용자 쪽인지 시스템 쪽인지를 경로로 판단합니다.

| macOS 버전 | 보고서 형식 |
|---|---|
| 10.15 Catalina, 11 Big Sur | 앱 충돌 보고서를 JSON `.ips` 로 저장하기 이전 [1]. 이때의 `.crash` 텍스트 구조는 이 페이지에서 다루지 않음 |
| 12 Monterey 이후 | 앱 충돌 보고서를 JSON 으로 `.ips` 파일에 저장 [1] |

보고서를 몇 개까지, 얼마 동안 두는지, 제출한 보고서를 다른 폴더로 옮기는지는 공개 자료에 없어 검체에서 확인합니다.

## 구조

`.ips` 파일에는 JSON 객체가 두 개 있습니다. 첫 줄은 사건(incident) 정보를 담은 메타데이터 객체이고, 나머지 줄 전체가 충돌 보고서 본문 객체입니다 [1]. 보통 JSON 파서는 객체 하나만 기대해서, 첫 줄과 나머지를 따로 읽어야 합니다 [1].

### 첫 줄: 메타데이터 객체

| 키 | 형 | 뜻 [1] |
|---|---|---|
| `name` | 문자열 | 보고서 대상 프로세스 이름(보통 실행 파일 이름) |
| `bug_type` | 문자열 | 보고서 종류. 충돌 보고서는 `309`, 스택샷은 `288` |
| `bundleID` | 문자열 | 번들 식별자 |
| `build_version` | 문자열 | 번들 버전 문자열 |
| `incident_id` | 문자열 | 보고서 고유 ID. 두 보고서가 같은 값을 쓰지 않음 |
| `platform` | 숫자 | 플랫폼(아래 표) |
| `timestamp` | 문자열 | 로그 시스템이 보고서를 추적하려고 만든 날짜·시각 |

`309` 말고 다른 종류도 있고, `288` 은 스택샷입니다 [1]. 나머지 값의 뜻은 공개 자료에 없습니다.

| `platform` 값 | 플랫폼 [1] |
|---|---|
| 1 | macOS |
| 2 | iOS (Apple silicon 맥에서 도는 iOS 앱 포함) |
| 3 | tvOS |
| 4 | watchOS |
| 6 | Mac Catalyst |
| 7 | iOS 시뮬레이터 |
| 8 | tvOS 시뮬레이터 |
| 9 | watchOS 시뮬레이터 |

### 나머지: 본문 객체

| 키 | 뜻 [1] |
|---|---|
| `procName` | 충돌한 프로세스의 실행 파일 이름 |
| `procPath` | 디스크의 실행 파일 위치. 사용자를 알 수 있는 경로 부분은 자리표시 값으로 바뀜 |
| `pid` | 충돌한 프로세스 ID |
| `parentProc`, `parentPid` | 이 프로세스를 띄운 부모 프로세스의 이름과 ID |
| `procLaunch` | 프로세스가 시작된 날짜·시각 |
| `captureTime` | 충돌한 날짜·시각 |
| `cpuType` | ARM-64, ARM, X86-64, X86 중 하나 |
| `modelCode` | 기기 모델 |
| `crashReporterKey` | 기기별 익명 식별자. 같은 기기의 보고서는 값이 같고, 기기를 지우면 바뀜 |
| `coalitionID`, `coalitionName` | 프로세스가 속한 coalition 의 ID 와 이름 |
| `incident` | 보고서 고유 ID |
| `exception` | 프로세스가 어떻게 끝났는지 |
| `termination` | 다른 쪽이 프로세스를 끝낸 경우의 정보 |
| `faultingThread` | 충돌한 스레드 번호 |
| `isCorpse` | 하드웨어 트랩이 아닌 충돌. 운영체제가 프로세스를 끝냈거나 프로세스가 `abort()` 를 부른 경우 |
| `isNonFatal` | 치명적이지 않아 프로세스가 끝나지 않음 |
| `isSimulated` | 실제 충돌은 아니지만 OS 가 종료를 요청했을 수 있음 |
| `threads`, `usedImages` | 스레드별 백트레이스, 적재된 바이너리 이미지 목록 |
| `osVersion`, `bundleInfo`, `storeInfo` | OS 버전, 번들 정보, 스토어 정보 |
| `vmSummary`, `vmregioninfo`, `lastExceptionBacktrace` | 가상 메모리 요약, 메모리 접근 문제 때의 영역 정보, 언어 예외 백트레이스 |

## 증거로서 의미

**증명하는 것.** `procPath`·`parentProc`·`procLaunch`·`captureTime` 을 함께 읽으면 "어떤 실행 파일이, 어떤 부모 프로세스에서 떠서, 언제 시작해, 언제 죽었나" 를 한 보고서에서 얻습니다 [1]. `usedImages` 에는 그 프로세스에 적재된 바이너리 목록이 있어서, 원래 앱에 없는 라이브러리가 들어 있으면 주입된 코드를 의심할 단서가 될 수 있습니다. `crashReporterKey` 는 같은 기기에서 나온 보고서끼리 같아서 [1], 다른 곳에서 모은 보고서가 이 맥의 것인지 맞춰 볼 때 씁니다.

**증명하지 못하는 것.** 충돌 보고서는 충돌 같은 문제가 있을 때 만드는 보고서라서, 문제 없이 끝난 실행은 여기서 찾을 수 없습니다. `procPath` 는 사용자를 알 수 있는 경로 부분을 자리표시 값으로 가려서 [1], 보고서만으로 어느 사용자 계정의 실행 파일이었는지 특정하기 어렵습니다. 사용자는 보고서가 있는 폴더 위치와 [그 시각에 맥을 쓴 사람이 누구인가 (User Attribution)](../../04-scenarios/activity/user-attribution.md)의 방법으로 좁힙니다. `isSimulated` 가 참이면 실제 충돌이 아니었을 수 있습니다 [1].

보고서에는 "이 보고서에 이 경로의 실행 파일(부모 프로세스 X)이 이 시각에 시작해 이 시각에 비정상 종료한 기록이 있다" 처럼 쓰고, 충돌 원인은 `exception` 과 `termination` 에 적힌 만큼만 옮깁니다.

## 시각 해석

한 보고서에 시각이 세 개 있습니다. `procLaunch` 는 프로세스가 시작된 때, `captureTime` 은 충돌한 때이고 [1], 메타데이터의 `timestamp` 는 로그 시스템이 보고서를 추적하려고 만든 날짜·시각이라서, 시작·종료 시각은 `procLaunch`·`captureTime` 으로 정합니다 [1]. 실행 흔적으로는 `procLaunch` 가 가장 직접적인 값이고, `procLaunch` 에서 `captureTime` 까지가 그 프로세스가 살아 있던 구간입니다.

세 값의 문자열 형식과 시간대 표기는 검체에서 확인합니다. 값에 시간대 오프셋이 붙어 있는지 먼저 보고, 없으면 [시간대와 시계 설정 (Time Zone·NTP)](../system-account/time-zone.md)과 같은 시각의 다른 기록으로 기준을 정합니다.

## 함정과 한계

- **두 객체.** `.ips` 파일 전체를 JSON 하나로 읽으면 파서가 실패하거나 첫 객체만 읽습니다 [1]. 도구가 메타데이터만 보여 주면 본문을 놓친 상태입니다.
- **가려진 경로.** `procPath` 의 사용자 부분은 자리표시 값이라서 [1], 경로 그대로 디스크에서 찾으면 없을 수 있습니다.
- **macOS 12 이전.** 이 페이지의 키 설명은 JSON 형식 기준이고 [1], 그 이전 `.crash` 텍스트 보고서에는 그대로 맞지 않습니다.
- **지워지기 쉬움.** 보고서는 평범한 파일이라 지우거나 보관 기간이 지나 사라질 수 있습니다. 보관 규칙은 공개 자료에 없으니, 보고서가 없다는 사실만으로 충돌이 없었다고 쓰지 않습니다.
- **다른 기기의 보고서.** `platform` 값이 시뮬레이터(7·8·9)이면 개발 환경에서 생긴 보고서입니다 [1]. `crashReporterKey` 가 다른 보고서가 섞여 있으면 다른 기기에서 옮겨 온 파일일 수도 있고, 기기를 지우면 이 값이 바뀌어서 [1] 같은 맥을 지우기 전에 생긴 보고서일 수도 있습니다.

## 직접 분석해 보기

### 텍스트로 한 번

명세로 만든 예시로, `.ips` 파일의 첫 줄은 아래처럼 한 줄짜리 JSON 객체입니다. 값은 형식만 보여 주려고 지어낸 자리표시입니다.

```
{"name":"ExampleApp","bug_type":"309","bundleID":"com.example.app","build_version":"1","incident_id":"(보고서 ID)","platform":1,"timestamp":"(날짜·시각)"}
{
  "procName" : "ExampleApp",
  "procPath" : "(자리표시 값이 섞인 경로)",
  ...
}
```

첫 줄에서 `bug_type` 이 `309` 인지 확인하고, 둘째 줄부터 끝까지를 따로 한 객체로 읽습니다 [1]. 헥스로 보면 첫 바이트는 `{` 인 `7b` 이고, 첫 줄 끝의 줄바꿈 바이트가 두 객체를 나눕니다.

### 공개 도구로 한 번

`head`, `tail`, `jq` 같은 공개 도구로 두 객체를 나눠 읽습니다.

```sh
head -n 1 Example.ips | jq '{name, bug_type, bundleID, incident_id, platform, timestamp}'

tail -n +2 Example.ips | jq '{procName, procPath, pid, parentProc, parentPid,
  procLaunch, captureTime, exception, termination, crashReporterKey}'

tail -n +2 Example.ips | jq '.usedImages'
```

여러 파일을 타임라인에 넣을 때는 파일마다 `procLaunch`·`captureTime`·`procPath`·`parentProc` 을 한 줄로 뽑아 모읍니다. 타임라인 작성은 [타임라인 작성 (Timeline)](../../03-techniques/analysis/timeline/index.md)에서 다룹니다.

## 교차 검증

| 함께 볼 아티팩트 | 맞춰 볼 것 |
|---|---|
| [통합 로그의 프로세스 실행 기록 (Process Events)](unified-log-process.md) | `procLaunch` 무렵의 실행 기록과 부모 프로세스 |
| [실행 정책 평가 기록 (ExecPolicy·Gatekeeper)](execpolicy-gatekeeper.md) | 같은 번들 식별자가 실행 정책 기록에 있는지 |
| [앱 번들 정보 (Info.plist·Code Signature)](../embedded-metadata/app-bundle.md) | `bundleInfo`·`build_version` 과 디스크의 번들 정보 |
| [격리 속성과 다운로드 기록 (Quarantine)](../filesystem/quarantine/index.md) | 충돌한 실행 파일이 어디서 왔는지 |
| [악성 코드 흔적 분석 (Malware Triage)](../../03-techniques/analysis/malware-triage/index.md) | `usedImages` 에 낯선 라이브러리가 있을 때 살펴볼 순서 |

## 실습

공개 검체(NIST CFReDS 등) 가운데 macOS 12 이후 이미지로 풀어 봅니다.

1. 볼륨 전체에서 `.ips` 파일을 찾아 폴더별로 몇 개인지 세어 보세요.
2. 각 파일의 첫 줄에서 `bug_type` 값별로 개수를 세고, `309`·`288` 이 아닌 값을 적어 보세요.
3. 충돌 보고서마다 `procPath`·`parentProc`·`procLaunch`·`captureTime` 을 뽑아 표로 만들어 보세요.
4. `crashReporterKey` 값이 몇 가지인지 확인하고, 둘 이상이면 어느 보고서가 다른지 찾아보세요.

## 참고 문헌

1. Apple Developer Documentation, "Interpreting the JSON format of a crash report" — https://developer.apple.com/tutorials/data/documentation/xcode/interpreting-the-json-format-of-a-crash-report.json
2. Apple Developer Documentation, "Acquiring crash reports and diagnostic logs" — https://developer.apple.com/tutorials/data/documentation/xcode/acquiring-crash-reports-and-diagnostic-logs.json
