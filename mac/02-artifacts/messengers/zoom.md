---
title: "줌"
parent: "아티팩트 · 메시지·메신저"
nav_order: 1480
---

# 줌 (Zoom)

줌 맥 앱은 `/Applications/zoom.us.app` 에 설치되고 번들 ID `us.zoom.xos` 이름으로 사용자 홈의 `Library` 곳곳에 폴더와 파일을 남기고, 이 흔적은 설치 여부와 사용 흔적을 확인하는 출발점이 됩니다. 회의 내용과 대화 DB의 구조는 공개된 분석 자료가 없습니다.

## 무엇을 기록하나 · 왜 생기나

줌은 화상 회의 앱입니다. 삭제 목록으로 보면 앱 번들과 함께 업데이터·데몬 같은 백그라운드 항목이 시스템 영역에 생기고, 사용자 홈 아래에는 데이터·설정·캐시·쿠키·로그 폴더가 생깁니다. 아래 경로 대부분은 Homebrew 의 줌 설치 정의 파일이 앱을 지울 때 치우는 경로 목록에 들어 있고[1], 앱 번들 구조와 설치 방식은 줌 4.6.8 을 기준으로 합니다[2]. 삭제 목록은 경로가 있다는 것만 알려 주고, 각 경로 안에 무엇이 들어 있는지는 알려 주지 않습니다.

분석가가 이 흔적으로 답할 수 있는 질문은 "이 맥에 줌이 설치된 적이 있나", "어느 사용자 계정에서 실행했나", "카메라·마이크를 쓸 수 있게 설정돼 있었나" 정도이고, "누구와 무슨 회의를 했나" 는 아래에서 설명하듯 이 흔적만으로 답하기 어렵습니다.

## 위치와 버전별 차이

### 앱과 설치 흔적

| 항목 | 경로·값 | 출처 |
|---|---|---|
| 앱 번들 | `/Applications/zoom.us.app` | [1][2] |
| 설치 중에 쓰인 사용자 홈 경로 | `~/Applications/zoom.us.app` (4.6.8 설치 도우미 스크립트 `runwithroot` 의 인자) | [2] |
| 실행 파일 | `/Applications/zoom.us.app/Contents/MacOS/zoom.us` | [2] |
| 번들 ID | `us.zoom.xos` | [1][2] |
| 패키지 영수증 ID | `us.zoom.pkg.videomeeting` | [1] |
| 설치 로그 | `~/Library/Logs/zoominstall.log` | [1] |

번들 ID 읽는 법은 [번들 ID와 팀 ID](../../01-foundations/value-decoding/bundle-team-id.md), 영수증은 [설치한 앱과 영수증](../system-account/installed-apps-receipts.md)에서 다룹니다.

### 백그라운드 항목

| 항목 | 경로·값 | 출처 |
|---|---|---|
| launchctl 라벨 | `us.zoom.updater`, `us.zoom.updater.login.check`, `us.zoom.ZoomDaemon` | [1] |
| 권한 있는 도우미 도구 | `/Library/PrivilegedHelperTools/us.zoom.ZoomDaemon` | [1] |
| 브라우저 플러그인 | `/Library/Internet Plug-Ins/ZoomUsPlugIn.plugin`, `~/Library/Internet Plug-Ins/ZoomUsPlugIn.plugin` | [1] |
| 업데이터 폴더 | `~/Library/Application Support/ZoomUpdater` | [1] |

라벨 세 개의 plist 가 `/Library/LaunchDaemons` 와 `/Library/LaunchAgents` 중 어디에 있는지와 파일 이름은 공개된 자료에 없습니다. 실제 기기에서는 두 폴더를 모두 열어 라벨이 같은 항목을 찾고, 읽는 법은 [실행 에이전트·데몬](../persistence/launchd/index.md)을 따릅니다.

### 사용자 데이터

| 항목 | 경로 | 출처 |
|---|---|---|
| 사용자 데이터 폴더 | `~/Library/Application Support/zoom.us` | [1] |
| 홈 바로 아래 숨김 폴더 | `~/.zoomus` | [1] |
| 문서·데스크탑의 줌 폴더 | `~/Documents/Zoom`, `~/Desktop/Zoom` | [1] |
| 설정 plist | `~/Library/Preferences/us.zoom.*.plist`, `~/Library/Preferences/ZoomChat.plist` | [1] |
| 캐시 | `~/Library/Caches/us.zoom.xos` | [1] |
| 쿠키·HTTP 저장소 | `~/Library/Cookies/us.zoom.xos.binarycookies`, `~/Library/HTTPStorages/us.zoom.xos`, `~/Library/HTTPStorages/us.zoom.xos.binarycookies` | [1] |
| WebKit 데이터 | `~/Library/WebKit/us.zoom.xos` | [1] |
| 창 상태 | `~/Library/Saved Application State/us.zoom.xos.savedState` | [1] |
| 최근 문서 목록 | `~/Library/Application Support/com.apple.sharedfilelist/com.apple.LSSharedFileList.ApplicationRecentDocuments/us.zoom*.sfl*` | [1] |
| iCloud 컨테이너 | `~/Library/Application Support/CloudDocs/session/containers/iCloud.us.zoom.videomeetings` 와 같은 이름의 `.plist` | [1] |
| 앱 확장·그룹 컨테이너 | `~/Library/Application Scripts/*.ZoomClient3rd`, `~/Library/Group Containers/*.ZoomClient3rd` | [1] |

### 로그와 충돌 보고

| 항목 | 경로 | 출처 |
|---|---|---|
| 앱 로그 | `~/Library/Logs/zoom.us` | [1] |
| 줌 전화 기능 로그로 보이는 폴더 | `~/Library/Logs/ZoomPhone` | [1] |
| 충돌 보고 | `/Library/Logs/DiagnosticReports/zoom.us*`, `~/Library/Application Support/CrashReporter/zoom.us*` | [1] |

### 버전별 차이

macOS 10.15 Catalina 이후 버전마다 경로나 DB 가 달라지는지는 공개된 자료가 없습니다. 줌 앱 버전에 따라서는 설치 패키지 이름이 다릅니다.

| 자료 시점 | 줌 버전 | 설치 패키지 이름 | 출처 |
|---|---|---|---|
| 2020년 3월 | 4.6.8 | `Zoom.pkg` | [2] |
| 2026년 9월 | 7.2.1.88329 (Homebrew 정의 표기) | `zoomusInstallerFull.pkg` | [1] |

## 구조

앱 번들 안에서는 실행 파일 `Contents/MacOS/zoom.us` 와 라이브러리가 들어 있는 `/Applications/zoom.us.app/Contents/Frameworks` 폴더가 확인됩니다[2]. 줌 4.6.8 의 앱 서명 권한 (entitlement) 목록에는 `com.apple.security.device.audio-input`, `com.apple.security.device.camera`, `com.apple.security.automation.apple-events` 가 들어 있어서 앱이 마이크·카메라를 쓰고 다른 앱에 Apple 이벤트를 보낼 수 있게 서명돼 있다는 점을 알 수 있습니다[2]. 같은 목록에는 `com.apple.security.cs.disable-library-validation` 과 `com.apple.security.cs.disable-executable-page-protection` 도 있는데[2], 앞의 것이 있으면 서명이 다른 라이브러리도 앱 안으로 읽어 들일 수 있어서 `Contents/Frameworks` 의 파일 변조를 따로 확인해야 합니다. 서명과 권한 목록을 읽는 법은 [앱 번들 정보](../embedded-metadata/app-bundle.md)와 [서명·공증·무결성 보호](../../01-foundations/protection/codesign-notarization-sip.md)에 있습니다.

사용자 데이터 폴더 `~/Library/Application Support/zoom.us` 의 속 구조는 공개된 분석 자료가 없습니다. 이 폴더 아래 `data` 하위 폴더에 `zoomus.enc.db`, `zoommeeting.enc.db` 같은 이름의 대화·회의 DB 가 있다고 흔히 알려져 있지만, 이 파일 이름과 DB 암호화 방식(SQLCipher 여부), 키를 키체인의 어느 항목에 두는지, 표·열 이름, 시각 값의 기준은 모두 실제 데이터로 확인해야 합니다. 분석 대상에서 이 폴더를 찾으면 파일 머리를 [SQLite 데이터베이스](../../01-foundations/data-formats/sqlite/index.md) 형식과 먼저 대조해 평문 SQLite 인지부터 판별하고, 암호화돼 있으면 [암호화된 증거 다루기](../../03-techniques/analysis/encrypted-evidence/index.md)의 절차로 넘어갑니다.

`~/Documents/Zoom` 과 `~/Desktop/Zoom` 은 로컬 녹화 저장 폴더로 알려져 있지만, 이 용도와 녹화 파일 이름·하위 폴더 이름 규칙은 실제 데이터로 확인합니다. 설정 plist 는 이름이 와일드카드로만 알려져 있어서 개별 파일 이름과 키는 실제 기기에서 직접 열어 보고, 형식은 [속성 목록 파일](../../01-foundations/data-formats/plist/index.md)을 따릅니다. 앱 로그 폴더의 파일 이름·형식·보존 기간과, 통합 로그 (Unified Log)에서 줌이 쓰는 서브시스템 이름도 공개된 자료가 없습니다.

> 그림 자리: 줌 설치 후 시스템 영역(앱 번들·PrivilegedHelperTools·launchd)과 사용자 홈(Application Support·Preferences·Caches·Logs)에 생기는 경로를 한 장에 나눠 보여 주는 트리

## 증거로서 의미

### 증명하는 것

앱 번들, 패키지 영수증 `us.zoom.pkg.videomeeting`, 도우미 도구 `us.zoom.ZoomDaemon`, 라벨이 `us.zoom.` 으로 시작하는 launchd 항목이 있으면 이 맥에 줌이 설치된 적이 있다는 기록이 됩니다. 사용자 홈 아래에 `us.zoom.xos` 이름의 캐시·쿠키·창 상태 폴더나 `~/Library/Application Support/zoom.us` 가 있으면 그 계정의 홈에 줌 관련 파일이 만들어졌다는 기록이 되고, 계정마다 이 폴더가 있는지 비교해 어느 계정에서 줌을 썼는지 좁힐 수 있습니다. `~/Library/Logs/zoominstall.log` 가 있는 홈은 그 계정 환경에서 설치 과정이 돌았다는 단서가 됩니다.

### 증명하지 못하는 것

이 경로들만으로는 어떤 회의에 들어갔는지, 누구와 대화했는지, 회의를 녹화했는지를 말할 수 없습니다. 대화·회의 DB 와 녹화 파일의 형식이 알려져 있지 않기 때문이고, 흔히 거론되는 파일 이름에 기대어 "녹화했다", "대화했다" 고 쓰지 않습니다. 서명 권한에 카메라·마이크가 있다는 점도 앱이 그 장치를 쓸 수 있게 만들어졌다는 뜻일 뿐이고, 사용자가 접근을 승인했는지나 실제로 켰는지는 [개인 정보 보호 권한](../credentials/tcc/index.md) 같은 다른 기록으로 확인합니다. TCC 데이터베이스에 줌의 `client` 값이 `us.zoom.xos` 로 남는지와, 카메라·마이크를 켠 시각이 통합 로그에 남는지는 실제 데이터로 확인합니다.

보고서에는 "이 계정의 홈에 줌 사용자 데이터 폴더가 있고, 폴더의 만든 시각은 이때다" 처럼 기록이 보여 주는 만큼만 씁니다.

## 시각 해석

줌 고유 기록의 시각 기준(유닉스 초인지 밀리초인지, UTC 인지 현지 시각인지)은 DB·로그 모두 공개된 자료가 없습니다. 확실히 쓸 수 있는 시각은 위 경로들의 파일 시스템 시각이고, 앱 번들이나 사용자 데이터 폴더의 만든 시각과 바뀐 시각을 [APFS 구조](../../01-foundations/disk-volume/apfs/index.md)에서 읽어 설치·첫 실행·마지막 사용 시점의 범위를 잡습니다. 값 변환과 UTC·현지 시각 구분은 [맥의 시각 값](../../01-foundations/value-decoding/mac-time-values.md)을 따르고, 보고서에는 [시간대와 시계 설정](../system-account/time-zone.md)을 함께 적습니다. 폴더의 바뀐 시각은 안쪽 파일이 새로 생기거나 지워질 때도 움직일 수 있어서, 폴더 시각 하나를 곧바로 "마지막 회의 시각" 으로 읽지 않습니다.

`~/Library/Logs/zoominstall.log` 안의 시각 형식과 기준도 공개된 자료가 없습니다. 로그를 열어 시각이 보이면 파일 시스템 시각과 영수증 정보를 나란히 놓고 서로 맞는지 봅니다.

## 함정과 한계

첫째, 위 경로 대부분은 Homebrew 의 삭제 목록에 있는 경로입니다[1]. 목록은 "지울 때 치우는 곳" 이라서 모든 경로가 한 기기에 동시에 생긴다는 보장은 없고, 줌 버전과 사용한 기능(줌 전화, iCloud 연동, 앱 확장)에 따라 일부만 있을 수 있습니다.

둘째, 줌 4.6.8 을 표준 사용자 계정으로 설치할 때 설치 도우미 스크립트에 `/Applications/zoom.us.app` 과 함께 사용자 홈의 `~/Applications/zoom.us.app` 경로가 넘어갑니다[2]. 설치 방식에 따라 앱이 사용자 홈 쪽에 놓일 수 있다는 뜻이지만 어느 조건에서 그곳에 남는지는 알려져 있지 않으므로, 시스템 앱 폴더만 보고 "줌 없음" 으로 판단하지 않고 두 곳을 모두 봅니다.

셋째, 삭제 목록이 곧 흔적을 지우는 목록이기도 합니다. 누군가 이 목록대로 앱과 데이터를 지웠다면 위 경로가 한꺼번에 사라지고, 그래도 [파일 시스템 이벤트](../filesystem/fsevents/index.md), [타임 머신](../filesystem/time-machine/index.md) 백업, APFS 스냅숏에는 지우기 전 경로가 남아 있을 수 있습니다. 모든 경로가 없다는 사실만으로 설치된 적이 없다고 결론 내리지 않고, [증거를 없애려 했나](../../04-scenarios/activity/anti-forensics/index.md)의 순서로 지운 흔적을 찾습니다.

넷째, 줌 4.6.8 에는 설치 방식과 라이브러리 로드에 관한 보안 문제가 있었습니다[2]. 침해 사고를 조사할 때는 설치 도우미와 앱 번들 안 `Contents/Frameworks` 폴더의 파일이 변조되지 않았는지 코드 서명 검증으로 확인하고, 검증 방법은 [서명·공증·무결성 보호](../../01-foundations/protection/codesign-notarization-sip.md)와 [악성 코드 흔적 분석](../../03-techniques/analysis/malware-triage/index.md)을 따릅니다.

다섯째, 흔히 인용되는 DB 이름(`zoomus.enc.db` 등)과 녹화 폴더 설명은 공개된 분석 자료가 없습니다. 보고서에 쓰려면 해당 기기와 줌 버전에서 직접 확인한 결과를 근거로 삼습니다.

## 직접 분석해 보기

### 헥스로 한 번

줌 DB 와 설정 파일의 내부 구조는 공개된 자료가 없어, 여기서는 줌 고유 형식의 헥스 예시 대신 실제 기기에서 찾은 파일이 어떤 형식인지 판별하는 데 헥스를 씁니다. `~/Library/Preferences` 의 줌 plist 는 첫 바이트를 [속성 목록 파일](../../01-foundations/data-formats/plist/index.md)의 머리와 대조해 바이너리 plist 인지 XML 인지 판별하고, `~/Library/Application Support/zoom.us` 아래 파일은 [SQLite 데이터베이스](../../01-foundations/data-formats/sqlite/index.md)의 머리와 대조합니다. 머리가 SQLite 와 맞지 않고 바이트가 고르게 흩어져 보이면 암호화됐을 가능성을 기록해 두지만, 어떤 방식인지는 알 수 없으므로 보고서에는 추정으로 적습니다.

### 공개 도구로 한 번

macOS 기본 명령만으로 설치 흔적을 확인할 수 있습니다.

```sh
# 패키지 영수증 정보 (라이브 시스템)
pkgutil --pkg-info us.zoom.pkg.videomeeting

# 사용자 홈의 줌 관련 경로가 있는지 한 번에 보기
ls -la ~/Library/Application\ Support/zoom.us ~/Library/Caches/us.zoom.xos ~/Library/Logs/zoom.us
```

`pkgutil` 결과에 어떤 항목(설치 시각 등)이 나오는지는 [설치한 앱과 영수증](../system-account/installed-apps-receipts.md)에서 확인합니다. 앱 번들의 서명과 서명 권한 목록은 `codesign` 으로 출력해 위 구조 절의 권한과 비교하고, plist 는 `plutil` 로 사람이 읽는 형식으로 바꿔 봅니다. 디스크 이미지라면 같은 경로를 마운트한 볼륨 기준으로 바꿔 확인하고, 라이브 시스템에서 명령을 돌리면 접근 시각이 바뀔 수 있으니 [라이브 대응](../../03-techniques/process-acquisition/live-response/index.md)의 순서를 따릅니다.

## 교차 검증

| 함께 볼 아티팩트 | 확인할 것 |
|---|---|
| [설치한 앱과 영수증](../system-account/installed-apps-receipts.md) | 영수증 `us.zoom.pkg.videomeeting` 과 설치 시점 |
| [설치 로그](../logs/install-log.md) | 줌 설치 기록이 남는지 (실제 데이터로 확인) |
| [격리 속성과 다운로드 기록](../filesystem/quarantine/index.md) | 설치 패키지를 내려받은 출처와 시각 |
| [실행 에이전트·데몬](../persistence/launchd/index.md) | `us.zoom.` 라벨 항목과 plist 위치 |
| [KnowledgeC](../execution/knowledgec/index.md), [바이옴](../execution/biome/index.md) | 번들 ID `us.zoom.xos` 로 앱을 쓴 시간대 |
| [앱 저장 상태](../file-folder-usage/saved-application-state.md) | `us.zoom.xos.savedState` 폴더의 시각 |
| [최근 항목](../file-folder-usage/recent-items/index.md) | `us.zoom*.sfl*` 목록에 남은 문서 |
| [개인 정보 보호 권한](../credentials/tcc/index.md) | 카메라·마이크 접근 승인 기록 |
| [충돌·진단 보고서](../execution/diagnostic-reports.md) | `zoom.us*` 충돌 보고의 시각과 버전 |
| [앱별 네트워크 사용량](../network/netusage.md) | 줌 프로세스가 주고받은 데이터 양과 시간대 |

앱을 쓴 시간대를 재구성하는 흐름은 [어떤 앱을 언제 썼나](../../04-scenarios/activity/app-usage.md), 연락 상대를 찾는 흐름은 [누구와 연락을 주고받았나](../../04-scenarios/activity/communication.md)에 있습니다.

## 실습

NIST CFReDS 처럼 공개된 맥 시험 이미지 가운데 줌이 설치된 것을 골라 아래 질문을 풀어 봅니다. 이미지마다 줌이 있는지는 먼저 확인합니다.

1. 앱 번들이 `/Applications` 와 사용자 홈의 `~/Applications` 중 어디에 있고, 영수증 `us.zoom.pkg.videomeeting` 이 남아 있나요?
2. `us.zoom.` 으로 시작하는 launchd 항목의 plist 는 `/Library/LaunchDaemons` 와 `/Library/LaunchAgents` 중 어디에 있고, 파일 이름은 무엇인가요?
3. 어느 사용자 계정의 홈에 `~/Library/Application Support/zoom.us` 가 있고, 그 폴더의 만든 시각은 현지 시각으로 언제인가요?
4. 사용자 데이터 폴더 아래 파일은 평문 SQLite 인가요, 아니면 SQLite 머리가 보이지 않나요?
5. KnowledgeC 나 바이옴의 `us.zoom.xos` 사용 시간대와 앱 저장 상태 폴더의 시각이 서로 맞나요?

## 참고 문헌

1. Homebrew/homebrew-cask, `Casks/z/zoom.rb` (줌 설치·삭제 정의) — https://raw.githubusercontent.com/Homebrew/homebrew-cask/master/Casks/z/zoom.rb
2. Objective-See, "The 'S' in Zoom, Stands for Security" (2020-03-30) — https://objective-see.org/blog/blog_0x56.html
