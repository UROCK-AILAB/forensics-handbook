---
title: "어떤 앱을 언제 썼나"
parent: "시나리오 · 행위 재구성"
nav_order: 2290
---

# 어떤 앱을 언제 썼나 (App Usage)

## 조사 질문

이 맥에서 어떤 앱을 언제 실행했고, 얼마 동안 화면 앞에 띄워 두고 썼는지 묻습니다. 침해 사고에서는 의심스러운 앱이 처음 실행된 시각을 찾는 데 쓰고, 행위 재구성에서는 문서를 열거나 메시지를 보낸 시간대에 어떤 앱이 앞에 있었는지 맞춰 보는 데 씁니다.

통합 로그 (Unified Log)에는 프로세스 실행만 따로 적는 기록 형식이 없고, 기록 한 건에 붙는 값도 pid·euid·실행 파일 UUID 정도라서 명령줄 인자나 부모 프로세스 칸이 없습니다 [4][5]. 그래서 앱이 앞에 있던 구간, 앱을 받고 처음 실행을 승인한 기록, 실행을 요청한 로그, 최근 목록처럼 성격이 다른 흔적을 겹쳐서 답을 만듭니다. 흔적 하나하나의 구조는 각 아티팩트 페이지에서 다루고, 이 페이지는 그 흔적들을 어떤 순서로 보고 어떻게 맞춰 보는지만 다룹니다.

## 먼저 확인할 것

OS 버전은 [OS 버전과 설치 기록](../../02-artifacts/system-account/os-version-install-history.md)에서 먼저 확인합니다. 흔적마다 확인된 macOS 범위가 달라서, 버전에 따라 먼저 열어 볼 곳이 바뀝니다. 표에 없는 버전은 검체에서 확인합니다.

| 흔적 | 확인된 macOS 범위 |
|---|---|
| knowledgeC `/app/inFocus` | 10.13 ~ 10.16 [2] |
| knowledgeC `/app/usage` | 10.14 ~ 10.16 [2] |
| 화면 사용 시간 DB | 10.15, 10.16 [2] |
| 전원 로그 앱 정보 | 10.15, 10.16 [2] |
| 최근 앱 목록 `.sfl2` | 10.13 이상 (`.sfl` 은 10.11부터) [11] |
| 충돌 보고서 `.ips` JSON 형식 | 12 이상 [13] |
| 기본 셸 zsh | 10.15 이상 [14] |
| 앱 번들의 `com.apple.provenance` | 13 Ventura 이상 [9] |
| RunningBoard 앱 실행 로그 | 15.6, 26.5.2 [16][17] |

macOS 11 이후 knowledgeC 에 앱 기록이 계속 쌓이는지와 바이옴 (Biome)이 macOS 에서 어느 버전부터 쓰였는지는 공개된 자료가 없어서, 검체마다 두 곳을 모두 열어 보고 어느 쪽에 기록이 있는지부터 봅니다.

시간대는 [시간대와 시계 설정](../../02-artifacts/system-account/time-zone.md)에서 확인합니다. knowledgeC·바이옴·화면 사용 시간 DB·격리 이벤트 DB는 맥 절대 시각을 쓰고, 앱 번들의 격리 속성은 유닉스 시각을 16진 문자열로 적고, 전원 로그는 유닉스 시각에 보정 표를 따로 씁니다 [1][2][8]. 통합 로그 시각은 timesync 정보로 벽시계 시각으로 바꿔야 해서 [5], 모든 시각을 한 기준으로 바꿔 적어 두어야 뒤에서 대조할 수 있습니다([맥의 시각 값](../../01-foundations/value-decoding/mac-time-values.md)).

사용자 범위는 누구의 홈 폴더를 볼지 정하는 일입니다. knowledgeC 는 사용자 DB `~/Library/Application Support/Knowledge/knowledgeC.db` 와 시스템 DB `/private/var/db/CoreDuet/Knowledge/knowledgeC.db` 가 따로 있어서 둘 다 확인합니다 [1][2]. 최근 앱 목록과 앱 저장 상태도 사용자 홈 아래에 있습니다. 수집 범위에는 통합 로그의 `/private/var/db/diagnostics/` 와 `/private/var/db/uuidtext/` 가 함께 들어 있는지 확인합니다([맥 증거 확보](../../03-techniques/process-acquisition/evidence-acquisition/index.md)).

## 볼 아티팩트와 순서

| 순서 | 아티팩트 | 알려 주는 것 | 링크 |
|---|---|---|---|
| 1 | knowledgeC `/app/inFocus`·`/app/usage` | 앞에 있던 앱의 번들 ID와 시작·끝 시각 | [KnowledgeC](../../02-artifacts/execution/knowledgec/index.md) |
| 2 | 바이옴 `App.InFocus` 스트림 | 앱 초점이 바뀐 시각과 번들 ID | [바이옴](../../02-artifacts/execution/biome/index.md) |
| 3 | 화면 사용 시간 `RMAdminStore-Local.sqlite`·`RMAdminStore-Cloud.sqlite` | 앱별 한 시간 단위 사용 시간(초) | [화면 사용 시간](../../02-artifacts/execution/screen-time.md) |
| 4 | 앱 번들의 `com.apple.quarantine`, 격리 이벤트 DB | 앱을 받은 경로·시각과 첫 실행 승인 여부 | [격리 속성과 다운로드 기록](../../02-artifacts/filesystem/quarantine/index.md) |
| 5 | ExecPolicy 의 `provenance_tracking` 표 | 게이트키퍼 (Gatekeeper)가 평가한 앱의 cdhash·번들 ID·팀 ID | [실행 정책 평가 기록](../../02-artifacts/execution/execpolicy-gatekeeper.md) |
| 6 | 통합 로그의 LaunchServices·RunningBoard 기록 | 앱 실행을 요청하고 띄운 과정 | [통합 로그의 프로세스 실행 기록](../../02-artifacts/execution/unified-log-process.md) |
| 7 | 전원 로그 `CurrentPowerlog.PLSQL` | 앱 이름·번들 ID·버전 | [전원 로그](../../02-artifacts/execution/powerlog.md) |
| 8 | 최근 앱 목록 `com.apple.LSSharedFileList.RecentApplications.sfl2` | 최근에 쓴 앱 | [최근 항목](../../02-artifacts/file-folder-usage/recent-items/index.md) |
| 9 | 앱 저장 상태 `~/Library/Saved Application State/` | 창 제목, 열어 둔 문서·폴더 | [앱 저장 상태](../../02-artifacts/file-folder-usage/saved-application-state.md) |
| 10 | 스포트라이트 검색 기록 `com.apple.spotlight.Shortcuts.v3` | 검색창에 친 글자로 연 앱과 `LAST_USED` 값 | [스포트라이트](../../02-artifacts/file-folder-usage/spotlight/index.md) |
| 11 | 충돌 보고서 `.ips` | `procPath`·`parentProc`·`procLaunch`·`captureTime` | [충돌·진단 보고서](../../02-artifacts/execution/diagnostic-reports.md) |
| 12 | `~/.zsh_history` | 터미널에서 친 명령 | [터미널 명령 기록](../../02-artifacts/execution/shell-history.md) |

1~3번은 앱을 쓴 구간을 시각과 함께 알려 주는 흔적이라 먼저 보고, 4~6번은 특정 앱이 언제 들어와 처음 실행됐는지 좁힐 때 봅니다. 7~12번은 앞의 흔적이 비어 있거나 보관 기간이 지났을 때 보강하는 자료입니다. 바이옴 경로는 `~/Library/Biome/streams/restricted/App.InFocus/local/` 이고 [7], 스포트라이트 검색 기록은 macOS 14 이후 `~/Library/Group Containers/group.com.apple.spotlight/` 아래에 있습니다 [12].

## 분석 흐름

1. 조사 기간을 정하고 knowledgeC 와 바이옴 `App.InFocus` 에서 번들 ID별로 앞에 있던 구간을 뽑습니다. 바이옴의 `remote/<기기 ID>/` 폴더 기록은 같은 계정을 쓰는 다른 기기의 사건이라 이 맥의 사용으로 세지 않습니다 [6].
2. 화면 사용 시간 DB에서 같은 앱의 시간 단위 사용량을 뽑아 1단계 구간과 어긋나지 않는지 봅니다.
3. 의심스러운 앱이라면 앱 번들의 격리 속성과 격리 이벤트 DB에서 앱을 받은 경로와 시각을 확인합니다. 격리 속성 플래그가 `0081` 에서 `00c1` 로 바뀌어 있으면 사용자가 앱을 열어 게이트키퍼 확인을 통과했다는 뜻이고(0x40 USER_APPROVED), 첫 실행 뒤에도 속성은 지워지지 않고 남습니다 [8][9][10]. ExecPolicy 의 `provenance_tracking` 표에서 같은 앱의 cdhash·팀 ID도 찾습니다 [9].
4. 통합 로그를 서브시스템으로 좁혀 실행 요청과 실행 과정을 찾습니다(아래 절).
5. 앱 저장 상태의 창 제목, 최근 앱 목록, 스포트라이트 검색 기록, 충돌 보고서로 앱 안에서 무엇을 열었는지와 실행 흔적을 보강합니다.
6. 터미널에서 띄운 명령은 1~3단계의 흔적에 남지 않아서, 셸 기록과 통합 로그로 따로 찾습니다.
7. `/display/isBacklit`(0 꺼짐, 1 켜짐)와 `/device/isLocked`(macOS 10.15부터, 0 해제, 1 잠김) 스트림을 1단계 구간과 겹쳐 봅니다 [2]. 화면이 켜져 있고 잠겨 있지 않던 구간인지로 사람이 앞에 있었을 가능성을 가늠할 수 있습니다. 모든 시각은 한 [타임라인](../../03-techniques/analysis/timeline/index.md)에 올립니다.

### 통합 로그에서 앱 실행 과정 찾기

macOS 26.5.2 Tahoe 에서 파인더로 앱을 더블클릭해 열면, 파인더가 LaunchServices 에 요청하고, LaunchServices 가 RunningBoard 를 거쳐 실행을 요청하고, AMFI 평가·게이트키퍼 평가·TCC 확인·공증 티켓 확인을 차례로 거친 뒤 launchd 가 실제 프로세스를 띄웁니다. 이 과정에 서브시스템 `com.apple.launchservices` 와 `com.apple.runningboard` 가 나옵니다 [17]. 단계마다 찍히는 메시지 문구는 판마다 다를 수 있어 검체에서 확인합니다.

macOS 15.6 에서는 `com.apple.runningboard` 로 거른 뒤, 새로 뜬 앱은 "constructed job", 앱 생명 주기 사건은 "acquiring assertion", 앱 확장은 "extension overlay" 문구로 찾습니다 [16]. 메시지 예는 다음과 같습니다.

```
Acquiring assertion targeting app application.co.eclecticlight.Cormorant.10809046.10809052(501)
```

macOS 15.6 에서 4분 동안 앱을 쓰는 사이 로그 항목이 5만 건 넘게 생겼습니다 [16]. 넓게 뽑으면 양이 너무 많아서 서브시스템과 번들 ID로 먼저 좁히는 편이 낫습니다. 이 메시지들의 로그 수준과 보관 기간, macOS 10.15 ~ 14 에서도 같은 서브시스템과 문구를 쓰는지는 공개된 자료가 없어서, 15.6·26.5.2 밖의 검체에서는 테스트 기기로 먼저 재현해 봅니다([도구 검증](../../03-techniques/reporting/tool-validation.md)).

로그인할 때 로그인 항목이 자동으로 실행된 기록은 서브시스템 `com.apple.loginwindow.logging` 의 `performAutolaunch` 메시지로 찾습니다 [15]. 이 기록과 겹치는 실행이라면 사용자가 직접 띄운 것이 아닐 수 있어서, [로그인 항목](../../02-artifacts/persistence/login-items.md)과 함께 봅니다.

## 흔한 오판

- **knowledgeC·바이옴에 없으면 실행하지 않았다고 보는 경우.** knowledgeC 앱 기록에는 GUI 앱만 남고 터미널에서 띄운 명령이나 백그라운드 프로세스는 남지 않습니다 [1]. 보관 기간도 knowledgeC 는 약 4주(macOS 10.13 기준), 바이옴은 대부분 28일(iOS 기준)이라 조사 기간이 길면 앞부분이 비어 있을 수 있습니다 [1][6]. macOS 최신판의 보관 기간은 검체에서 확인합니다.
- **다른 기기의 기록을 이 맥의 사용으로 세는 경우.** 바이옴 `remote/` 폴더 기록은 다른 기기의 사건입니다 [6]. 화면 사용 시간 DB에는 기기 종류를 적는 칸 `ZCOREDEVICE.ZPLATFORM`(1 macOS, 2 iOS, 4 Apple Watch)이 있어서 다른 기기 기록이 섞일 수 있습니다 [3]. 행마다 기기 칸을 확인합니다.
- **최근 앱 목록의 순서를 실행 시각으로 읽는 경우.** `.sfl2` 항목에는 앱을 연 시각을 적는 칸이 알려져 있지 않습니다 [11].
- **앱 저장 상태 폴더의 시각을 앱을 연 시각으로 쓰는 경우.** 이 폴더에서 얻는 시각은 `windows.plist` 파일의 수정 시각뿐입니다 [11].
- **셸 기록의 명령에 시각을 붙이는 경우.** 기본 `/etc/zshrc` 는 `EXTENDED_HISTORY` 를 켜지 않아서 `.zsh_history` 에는 명령 순서만 남고 시각이 없습니다. 기본값은 `HISTSIZE=2000`, `SAVEHIST=1000` 입니다 [14].
- **`App.InFocus` 상태 값을 명세로 읽는 경우.** 상태 값 0과 1의 뜻은 iLEAPP·mac_apt 의 해석이고, Apple 이 공개한 명세는 없습니다 [6][7].
- **격리 속성이 있으면 실행했다고 보는 경우.** 격리 속성은 앱을 받은 기록이고, 사용자가 열어 승인했는지는 0x40 비트로 따로 봅니다 [8][10].

## 보고서 문장 예

> 사용자 ○○의 knowledgeC.db `/app/inFocus` 스트림에 번들 ID "○○" 앱이 ○○○○년 ○월 ○일 ○시 ○분부터 ○시 ○분까지(UTC로 바꾼 시각) 앞에 있던 기록이 있습니다. 같은 앱 번들의 격리 속성에는 사용자가 게이트키퍼 확인을 통과했음을 뜻하는 비트(0x40)가 켜져 있고, 격리 이벤트 DB에는 이 앱을 ○시 ○분에 받은 기록이 있습니다. 이 기록들만으로는 앱 안에서 어떤 작업을 했는지는 알 수 없습니다.

## 함께 볼 페이지

- [KnowledgeC (knowledgeC.db)](../../02-artifacts/execution/knowledgec/index.md) — 앱 사용 구간 기록의 구조
- [바이옴 (Biome)](../../02-artifacts/execution/biome/index.md) — `App.InFocus` 스트림과 SEGB 형식
- [통합 로그의 프로세스 실행 기록 (Process Events)](../../02-artifacts/execution/unified-log-process.md) — 실행 기록을 로그에서 찾는 법
- [맥 사용 시간 재구성 (Usage Time)](usage-time.md) — 켜짐·잠자기·로그인 구간
- [그 시각에 맥을 쓴 사람이 누구인가 (User Attribution)](user-attribution.md) — 앱을 쓴 사람을 가리는 법
- [악성 코드는 어디서 들어왔나 (Initial Access)](../incident/initial-access.md) — 의심 앱이 들어온 경로

## 참고 문헌

1. Sarah Edwards, "Knowledge is Power! Using the macOS/iOS knowledgeC.db Database to Determine Precise User and Application Usage" (mac4n6.com, 2018-08-05) — https://www.mac4n6.com/blog/2018/8/5/knowledge-is-power-using-the-knowledgecdb-database-on-macos-and-ios-to-determine-precise-user-and-application-usage
2. APOLLO 모듈 knowledge_app_inFocus.txt, knowledge_app_usage.txt, knowledge_device_is_backlit.txt, knowledge_device_locked.txt, powerlog_app_info_macos.txt, screentime_timed_items.txt (Sarah Edwards) — https://raw.githubusercontent.com/mac4n6/APOLLO/master/modules/knowledge_app_inFocus.txt 외 같은 폴더
3. APOLLO 모듈 screentime_timed_items.txt — https://raw.githubusercontent.com/mac4n6/APOLLO/master/modules/screentime_timed_items.txt
4. Apple Developer — OSLogEntryFromProcess — https://developer.apple.com/tutorials/data/documentation/oslog/oslogentryfromprocess.json
5. libyal dtformats — Apple Unified Logging and Activity Tracing formats — https://raw.githubusercontent.com/libyal/dtformats/main/documentation/Apple%20Unified%20Logging%20and%20Activity%20Tracing%20formats.asciidoc
6. Mattia Epifani, "84 Streams Later, Part 2: Inside Apple Biome" (2026-07-27) — https://blog.digital-forensics.it/2026/07/84-streams-later-part-2-inside-apple.html , iLEAPP — https://github.com/abrignoni/iLEAPP
7. mac_apt (Yogesh Khatri), plugins/biome.py — https://github.com/ydkhatri/mac_apt/blob/master/plugins/biome.py
8. Howard Oakley, "xattr: com.apple.quarantine, the quarantine flag" (2017-12-11) — https://eclecticlight.co/2017/12/11/xattr-com-apple-quarantine-the-quarantine-flag/
9. Howard Oakley, "Ventura has changed app quarantine with a new xattr" (2023-03-13) — https://eclecticlight.co/2023/03/13/ventura-has-changed-app-quarantine-with-a-new-xattr/
10. WebKit 소스 QuarantineSPI.h — https://raw.githubusercontent.com/WebKit/WebKit/main/Source/WebCore/PAL/pal/spi/mac/QuarantineSPI.h
11. macMRU-Parser `macMRU.py` (Sarah Edwards) — https://raw.githubusercontent.com/mac4n6/macMRU-Parser/master/macMRU.py , mac_apt `plugins/recentitems.py`·`plugins/savedstate.py` — https://github.com/ydkhatri/mac_apt/blob/master/plugins/savedstate.py
12. mac_apt 플러그인 spotlightshortcuts.py — https://raw.githubusercontent.com/ydkhatri/mac_apt/master/plugins/spotlightshortcuts.py
13. Apple Developer Documentation, "Interpreting the JSON format of a crash report" — https://developer.apple.com/tutorials/data/documentation/xcode/interpreting-the-json-format-of-a-crash-report.json
14. Apple Support, "Use zsh as the default shell on your Mac" (102360) — https://support.apple.com/en-us/102360 , Apple 공개 소스 zsh `zshrc` — https://raw.githubusercontent.com/apple-oss-distributions/zsh/main/zshrc
15. Mandiant (Alexander Holcomb), "Reviewing macOS Unified Logs" (2022-08-31) — https://cloud.google.com/blog/topics/threat-intelligence/reviewing-macos-unified-logs
16. Howard Oakley, "What does RunningBoard do? 5 Log insights" (2025-08-07) — https://eclecticlight.co/2025/08/07/what-does-runningboard-do-5-log-insights/
17. Howard Oakley, "How does an app launch? An exploration with LogUI" (2026-07-27) — https://eclecticlight.co/2026/07/27/how-does-an-app-launch-an-exploration-with-logui/
