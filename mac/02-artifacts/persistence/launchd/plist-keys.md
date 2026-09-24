---
title: "plist 키 해석"
parent: "실행 에이전트·데몬"
grand_parent: "아티팩트 · 자동 실행·지속성"
nav_order: 580
---

# plist 키 해석 (ProgramArguments·RunAtLoad·KeepAlive)

실행 에이전트·데몬의 plist는 무엇을 실행할지(`Program`·`ProgramArguments`)와 언제 실행할지(`RunAtLoad`·`KeepAlive`·`StartInterval` 등)를 키로 적은 설정 파일이고, 분석에서는 이 키들로 실제 실행 파일과 실행 조건을 읽어 냅니다.

## 무엇을 기록하나

plist 한 개가 launchd 작업(job) 하나이고, 키 목록과 뜻은 launchd.plist(5) man 페이지 [1]를 기준으로 삼습니다. Apple의 보관 문서 [2]는 2016년 9월에 마지막으로 고친 문서라서 필수 키 표 정도만 함께 봅니다. 파일이 놓이는 폴더와 도메인은 [위치와 적용 범위 (Locations)](locations.md)에, plist 형식 자체는 [속성 목록 파일 (Property List)](../../../01-foundations/data-formats/plist/index.md)에 있습니다.

## 무엇을 실행하나

아래 표와 다음 절의 표에서 형식 칸의 — 는 이 페이지의 출처에서 형식을 확인하지 못한 키입니다.

| 키 | 형식 | 뜻 [1] |
|---|---|---|
| `Label` | string (필수) | launchd 안에서 작업을 하나로 가려내는 이름 |
| `Program` | string | execv(3)의 첫 인자로 넘기는 실행 파일 절대 경로. `ProgramArguments`·`BundleProgram` 이 없으면 필수 |
| `ProgramArguments` | array of strings | execvp(3)의 두 번째 인자(argv). 첫 요소가 argv[0]. `Program` 이 없으면 필수 |
| `BundleProgram` | string | 앱 번들 기준 상대 경로. SMAppService로 설치한 plist에서만 지원 |
| `EnableGlobbing` | boolean | 실행 전에 glob(3)으로 인자를 펼침 |
| `WorkingDirectory` | — | 작업 디렉터리 |
| `EnvironmentVariables` | dictionary of strings | 환경 변수 |
| `StandardOutPath`·`StandardErrorPath` | — | 표준 출력·표준 오류를 적을 파일 |
| `UserName`·`GroupName` | — | 실행 계정·그룹. 시스템 도메인에서만 쓰임 |
| `InitGroups` | — | 기본값 true |

Apple 보관 문서의 표는 `Label` 과 `ProgramArguments` 를 필수로, `inetdCompatibility` 를 inetd에서 띄우는 작업일 때만 필수로 적습니다 [2]. man 페이지는 `Program` 이나 `BundleProgram` 만 있어도 되는 것으로 적고 있어서, 실제 파일에서는 세 키 가운데 어느 것이 있는지 모두 확인합니다.

실제로 실행되는 파일을 가릴 때는 `Program` 과 `ProgramArguments` 의 관계를 조심합니다. man 페이지는 `Program` 이 없을 때만 `ProgramArguments` 의 첫 요소를 실행 파일로 쓴다고 적습니다 [1]. 그래서 `Program` 이 있으면 그 경로가 실행 파일이고, `ProgramArguments` 의 첫 요소는 프로세스에 넘기는 argv[0] 문자열일 뿐입니다. 그래서 두 키가 모두 있고 값이 다르면 `Program` 쪽을 실행 파일로 적고, `ProgramArguments[0]` 은 프로세스 목록에 보일 이름으로 따로 적습니다. `EnableGlobbing` 이 true면 인자의 와일드카드가 실행 전에 펼쳐지므로 [1], plist에 적힌 문자열과 실제로 넘어간 인자가 다를 수 있습니다.

`StandardOutPath` 에 적힌 파일은 없으면 새로 만들어지고, 소유자는 `UserName`·`GroupName` 을, 권한은 `Umask` 를 따릅니다 [1]. 이 출력 파일은 작업이 돌면서 남긴 흔적이 될 수 있어서 경로를 따라가 확인할 만합니다(필자 해석).

## 언제 실행하나

| 키 | 형식 | 뜻 [1] |
|---|---|---|
| `RunAtLoad` | boolean | 작업을 적재할 때 한 번 띄움. 기본값 false |
| `KeepAlive` | boolean 또는 dictionary | 계속 살려 둘지, 조건에 따라 살려 둘지. 기본값 false |
| `StartInterval` | integer | N초마다 실행 |
| `StartCalendarInterval` | dictionary 또는 그 배열 | Minute·Hour·Day·Weekday·Month로 정한 때에 실행 |
| `StartOnMount` | boolean | 파일 시스템이 마운트될 때마다 실행 |
| `WatchPaths` | array of strings | 나열한 경로 중 하나가 바뀌면 실행 |
| `QueueDirectories` | array of strings | 디렉터리가 비어 있지 않은 동안 살려 둠 |
| `LaunchOnlyOnce` | boolean | 딱 한 번만 실행 |
| `LaunchEvents`·`MachServices`·`Sockets` | — | 상위 이벤트·Mach 서비스·소켓 요청이 올 때 띄움 |
| `ThrottleInterval` | integer | 기본 10초 제한을 바꿈. 이 간격보다 자주 띄우지 않음 |
| `ProcessType` | — | Background·Standard·Adaptive·Interactive. 값에 따라 자원 제한이 달라짐 |
| `AbandonProcessGroup` | boolean | true면 작업이 끝날 때 같은 프로세스 그룹의 남은 프로세스를 죽이지 않음 |

`KeepAlive` 를 dictionary로 쓰면 조건별로 살려 둡니다.

| `KeepAlive` 하위 키 | 뜻 [1] |
|---|---|
| `SuccessfulExit` | true면 종료 코드 0으로 끝났을 때 다시 띄우고, false면 0이 아닐 때 다시 띄움 |
| `Crashed` | SIGILL·SIGSEGV 같은 크래시 신호로 끝났을 때 다시 띄움 |
| `PathState` | dictionary of booleans. 값이 true인 경로가 있는 동안 살려 둠 |
| `OtherJobEnabled` | dictionary of booleans. 지정한 다른 작업이 적재돼 있는 동안 살려 둠 |
| `AfterInitialDemand` | true면 다른 이유로 처음 뜨기 전까지는 살려 두지 않음. 기본값 false |
| `NetworkState` | 더 이상 구현되지 않음 |

지속성 관점에서 가장 먼저 볼 조합은 `RunAtLoad` 와 `KeepAlive` 입니다. `RunAtLoad` 가 true면 부팅이나 로그인으로 적재되는 순간 한 번 뜨고, `KeepAlive` 가 true면 프로세스가 끝나도 launchd가 다시 띄웁니다 [1]. `AbandonProcessGroup` 이 true면 작업이 끝난 뒤에도 그 작업이 만든 자식 프로세스가 남을 수 있습니다 [1].

## 상태·기타 키

| 키 | 뜻 |
|---|---|
| `Disabled` | 기본으로 적재할지 여부 [1]. launchctl로 바꾼 상태는 plist 밖에 저장됨([위치와 적용 범위](locations.md)) |
| `AssociatedBundleIdentifiers` | string 또는 array. 시스템 설정의 로그인 항목 화면에서 이 작업과 연결해 보여 줄 번들 [1] |
| `inetdCompatibility` | dictionary. inetd에서 띄운 것처럼 동작하는 데몬 [1] |
| `Debug` | boolean. launchd 로그 마스크를 잠시 LOG_DEBUG로 바꿈 [1] |
| `OnDemand`·`ServiceIPC` | 더 이상 쓰지 않음(deprecated) [1] |
| `LimitLoadToHosts`·`LimitLoadFromHosts` | 지원하지 않음 [1] |

`AssociatedBundleIdentifiers` 는 백그라운드 작업 관리 기록의 `associatedBundleIdentifiers` 속성과 이름이 같아서 [4], plist와 그 기록을 맞춰 볼 때 연결 고리가 됩니다. 기록 쪽 구조는 [백그라운드 작업 관리 (BTM·Background Items)](background-task-management.md)에 있습니다.

## 예시로 읽어 보기

아래 plist는 man 페이지 [1]의 키 정의로 만든 예시이고, 실제 검체에서 나온 파일이 아닙니다. 최상위 dictionary 부분만 옮겼고, 레이블과 경로는 설명용으로 지은 이름입니다.

```xml
<dict>
  <key>Label</key>
  <string>com.example.helper</string>
  <key>Program</key>
  <string>/Users/Shared/example/helper</string>
  <key>ProgramArguments</key>
  <array>
    <string>updater</string>
    <string>--quiet</string>
  </array>
  <key>RunAtLoad</key>
  <true/>
  <key>KeepAlive</key>
  <dict>
    <key>SuccessfulExit</key>
    <false/>
  </dict>
  <key>StandardOutPath</key>
  <string>/tmp/example-helper.log</string>
</dict>
```

이 예시에서 실행 파일은 `Program` 에 적힌 `/Users/Shared/example/helper` 이고, 프로세스에 넘어가는 argv[0]은 `updater` 입니다. `RunAtLoad` 가 true라서 적재될 때 한 번 뜨고, `KeepAlive` 의 `SuccessfulExit` 가 false라서 종료 코드가 0이 아니면 다시 뜹니다. 표준 출력은 `/tmp/example-helper.log` 에 쌓이므로 이 파일도 함께 확인합니다.

## 증거로서 의미

**증명하는 것.** plist는 launchd가 이 작업을 적재하면 어떤 파일을 어떤 인자로, 어떤 조건에서 실행하도록 설정돼 있었는지를 보여 줍니다. 시스템 도메인 작업이면 `UserName`·`GroupName` 으로 어느 계정으로 실행하도록 설정됐는지도 알 수 있습니다.

**증명하지 못하는 것.** 키는 설정일 뿐이라서 실제로 실행됐는지, 몇 번 실행됐는지는 말해 주지 않습니다. `Program` 에 적힌 파일이 지금 그 경로에 있는지, 설정 당시의 파일과 같은 파일인지도 따로 확인해야 합니다. 누가 plist를 만들었는지도 키에는 없습니다.

## 시각 해석

이 페이지의 표에 든 키 가운데 작업을 언제 설치했는지나 마지막으로 언제 실행했는지를 적는 키는 없고, 시각과 관련된 키는 실행 일정을 정하는 키뿐입니다. 이 일정 키를 실행 기록과 맞춰 볼 때는 잠자기를 조심합니다. `StartInterval` 은 맥이 잠든 동안이거나 작업이 이미 돌고 있으면 그 회차를 건너뛰고 [1], `StartCalendarInterval` 은 cron과 달리 잠든 동안 놓친 실행을 깨어난 뒤에 합니다 [1]. 그래서 `StartCalendarInterval` 작업의 실행 흔적이 정한 시각과 다른 때에 남아 있으면, 그 사이 맥이 잠들어 있었는지를 [전원·잠자기 기록 (pmset)](../../logs/power-events.md)으로 먼저 확인합니다. 잠든 사이 여러 회차가 지나갔으면 깨어난 뒤 한 번으로 합쳐 실행하므로 [1], 실행 흔적 수가 일정상 회차 수보다 적어도 이상한 일이 아닙니다.

plist를 언제 놓았는지는 키가 아니라 파일 시스템 시각이나 [파일 시스템 이벤트 (FSEvents)](../../filesystem/fsevents/index.md) 같은 다른 기록에서 찾습니다.

## 함정과 한계

`ProgramArguments[0]` 을 실행 파일로 적는 실수가 흔합니다. `Program` 이 함께 있으면 실행 파일은 `Program` 쪽이고, 프로세스 목록에 보이는 이름과 디스크의 실행 파일이 다를 수 있습니다.

`Disabled` 키가 true라고 해서 지금 꺼져 있다고 단정하지 않습니다. launchctl로 바꾼 상태는 plist 밖에 저장되고, 그 위치와 읽는 법은 [위치와 적용 범위](locations.md)에 있습니다. `NetworkState` 처럼 더 이상 구현되지 않는 키는 plist에 남아 있어도 동작에 영향을 주지 않으니 [1], 실행 조건을 정리할 때 빼고 봅니다.

## 직접 분석해 보기

라이브 시스템에서는 launchctl 하위 명령으로 plist가 아니라 launchd가 지금 알고 있는 상태를 봅니다 [3].

| 명령 | 보여 주는 것 [3] |
|---|---|
| `launchctl print` | 서비스나 도메인의 정보 |
| `launchctl blame` | 실행 중인 서비스가 왜 떴는지 |
| `launchctl list` | 예전 방식의 목록(세 칸) |

`blame` 은 디스크의 plist로는 알 수 없는 "왜 떴는가" 를 보여 주므로, 위의 실행 조건 키와 맞춰 보면 설정과 실제 동작을 함께 확인할 수 있습니다. 디스크 이미지에서는 plist를 풀어 위 세 표의 키를 채우고, 실행 파일 경로마다 [앱 번들 정보 (Info.plist·Code Signature)](../../embedded-metadata/app-bundle.md)와 서명을 확인합니다.

## 교차 검증

- [통합 로그의 프로세스 실행 기록 (Process Events)](../../execution/unified-log-process.md) — 설정한 실행 파일이 실제로 실행됐는지
- [백그라운드 작업 관리 (BTM·Background Items)](background-task-management.md) — `AssociatedBundleIdentifiers` 와 등록 기록
- [예약 작업 (cron·periodic)](../cron-periodic.md) — 일정 실행을 다른 방식으로 건 흔적
- [악성 코드 흔적 분석 (Malware Triage)](../../../03-techniques/analysis/malware-triage/index.md)
- [악성 코드 지속성 찾기 (Persistence)](../../../04-scenarios/incident/persistence.md)

## 참고 문헌

1. launchd.plist(5) man page (Xcode man pages 미러) — https://keith.github.io/xcode-man-pages/launchd.plist.5.html
2. Apple, Daemons and Services Programming Guide — Creating Launch Daemons and Agents (2016-09-13) — https://developer.apple.com/library/archive/documentation/MacOSX/Conceptual/BPSystemStartup/Chapters/CreatingLaunchdJobs.html
3. launchctl(1) man page (Xcode man pages 미러) — https://keith.github.io/xcode-man-pages/launchctl.1.html
4. Objective-See, DumpBTM 소스 `library/code/dumpBTM.m`, `library/code/dumpBT_Internal.h` (Patrick Wardle, 2023-01-20) — https://github.com/objective-see/DumpBTM/tree/main/library/code
