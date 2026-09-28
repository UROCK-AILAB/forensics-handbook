---
title: "슬랙"
parent: "아티팩트 · 메시지·메신저"
nav_order: 1410
---

# 슬랙 (Slack)

맥 슬랙은 번들 ID가 `com.tinyspeck.slackmacgap` 인 앱이고 [1], 대화 자료는 Chromium 방식 IndexedDB(LevelDB)로 사용자 `Library` 아래 `Slack/IndexedDB/` 에 남는다고 알려져 있습니다 [2].

## 무엇을 기록하나 · 왜 생기나

슬랙 데스크톱 앱은 Chromium(Electron) 기반이라서, 앱이 화면에 보여 준 대화 자료가 Chrome과 같은 IndexedDB 형식으로 로컬에 남습니다 [2]. 슬랙은 이 밖에도 진단 보고서, Application Scripts, 캐시, 환경설정, 쿠키, 번들 ID 기준의 WebKit 데이터를 남기고 사용자 `Library` 아래 공유 컨테이너도 씁니다 [1]. 이 자리들은 Homebrew가 앱을 지울 때 함께 지우는 자리이기도 합니다 [1]. 각 자리의 정확한 경로 문자열은 실제 기기에서 확인합니다.

서버의 메시지가 로컬에 전부 내려와 있는지, 아니면 앱이 필요한 만큼만 받아 캐시하는지는 로컬 기록만으로 알 수 없습니다. 그래서 로컬에 남은 자료는 "이 맥의 슬랙 앱이 캐시한 자료" 로 다루고, 워크스페이스 대화 전체로 보지 않습니다.

## 위치와 버전별 차이

IndexedDB 위치는 받은 경로에 따라 아래와 같습니다 [2].

| 받은 경로 | IndexedDB 위치 |
|---|---|
| 직접 받은 판 | `~/Library/Application Support/Slack/IndexedDB/*.leveldb` |
| App Store판 | `~/Library/Containers/com.tinyspeck.slackmacgap/Data/Library/Application Support/Slack/IndexedDB/*.leveldb` |

두 판이 서로 다른 폴더를 쓰니 실제 기기에서 두 곳을 모두 봅니다. `root-state.json`, `storage/`, `logs/` 같은 그 밖의 파일과 폴더 이름, 그 안의 내용은 실제 데이터로 확인합니다.

Homebrew는 macOS 버전마다 설치하는 슬랙의 마지막 지원판을 따로 적어 두었고, 모두 ARM64와 x64 판이 있습니다 [1].

| macOS | Homebrew가 적은 마지막 지원판 |
|---|---|
| Big Sur 이하 | 4.45.69 |
| Monterey | 4.51.191 |
| Ventura 이후 | 4.52.162 |

분석 대상의 macOS 버전으로 설치될 수 있는 슬랙 버전의 범위를 추정할 수 있지만, 실제 설치된 버전은 앱 번들의 `Info.plist` 에서 확인합니다. 읽는 법은 [앱 번들 정보 (Info.plist·Code Signature)](../embedded-metadata/app-bundle.md)에 있습니다.

## 구조

IndexedDB 자료는 Chromium 방식 IndexedDB이고 그 아래 저장소는 LevelDB라서, ccl_chromium_reader로 읽을 수 있습니다 [2]. LevelDB 파일과 IndexedDB 레코드의 구조는 [LevelDB와 IndexedDB (LevelDB·IndexedDB)](../../01-foundations/data-formats/leveldb-indexeddb.md)에서 다루고, Chromium 계열 앱의 저장 방식 전반은 [크롬·엣지·웨일 (Chromium 계열)](../browsers/chromium/index.md)을 봅니다.

환경설정 도메인은 `com.tinyspeck.slackmacgap` 이고, 관리자가 데스크톱 앱 설정을 배포할 때도 이 도메인을 씁니다 [2]. `defaults read com.tinyspeck.slackmacgap` 로 설정을 읽을 수 있습니다 [2]. 수집한 이미지에서는 `defaults` 대신 이 이름의 plist 파일을 찾아 [속성 목록 파일 (Property List)](../../01-foundations/data-formats/plist/index.md)의 방법으로 읽고, 관리자가 배포한 설정은 [구성 프로파일 (Configuration Profiles·MDM)](../persistence/configuration-profiles.md)에서 함께 봅니다.

## 증거로서 의미

**증명하는 것.** 슬랙 데이터 폴더가 있으면 이 사용자 계정에서 슬랙 앱을 실행해 자료를 남긴 적이 있고, 폴더 위치로 App Store판인지 직접 받은 판인지를 가를 수 있습니다 [2]. IndexedDB에서 메시지 레코드를 읽어 내면 그 내용이 이 맥의 앱 저장소에 캐시되어 있었다는 사실을 보여 줍니다.

**증명하지 못하는 것.** 로컬 캐시에 없는 메시지를 "보내지 않았다" 거나 "없었다" 고 말할 수 없습니다. 레코드가 있다는 사실만으로 사용자가 그 메시지를 읽었다고 말할 수도 없습니다.

쿠키와 세션 저장소는 공격자가 노리는 대상입니다 [2]. 방어 쪽에서는 슬랙 앱이 아닌 프로세스가 이 폴더를 읽거나 복사한 흔적을 탐지 대상으로 보고, [정보 탈취 악성 코드 (Infostealer)](../../04-scenarios/incident/infostealer.md)의 흐름으로 확인합니다.

보고서에는 "`○○` 경로의 IndexedDB에서 ○○ 워크스페이스 채널의 메시지 레코드 ○○건을 읽었다" 처럼 기록으로 확인되는 만큼만 씁니다.

## 시각 해석

IndexedDB 레코드 안의 메시지 시각 형식은 실제 레코드에서 확인합니다. 레코드에서 시각으로 보이는 값을 찾으면 기준점과 단위를 [맥의 시각 값 (Mac Absolute Time·Unix·HFS)](../../01-foundations/value-decoding/mac-time-values.md)의 방법으로 검증하고, 슬랙 화면이나 다른 참여자의 기록과 몇 건을 맞춰 본 뒤에 씁니다.

`.leveldb` 폴더 안 파일의 파일 시스템 시각은 저장소가 바뀐 시각이라서 메시지 시각과 다릅니다. 두 시각을 섞지 않고 따로 적습니다.

## 함정과 한계

저장 위치는 받은 경로에 따라 다르니, 실제 기기에 그 경로가 있는지 먼저 확인하고 보고서에는 확인한 경로를 씁니다.

지운 메시지가 LevelDB에 남는지는 실제 데이터로 확인해야 합니다. LevelDB에 지운 레코드가 남는 방식은 [LevelDB와 IndexedDB (LevelDB·IndexedDB)](../../01-foundations/data-formats/leveldb-indexeddb.md)에서 확인하고, 쓰는 도구가 지운 레코드까지 보여 주는지를 도구 설명에서 확인합니다.

Homebrew로 앱을 지우면서 zap 삭제까지 했다면 위 목록의 캐시·환경설정·쿠키가 함께 지워집니다 [1]. 이때는 [타임 머신 (Time Machine)](../filesystem/time-machine/index.md)과 [스냅숏과 백업 비교 (Snapshot·Time Machine Diff)](../../03-techniques/analysis/snapshot-diff.md)에서 이전 판을 찾습니다.

윈도우판 슬랙의 경로와 저장 형식은 맥에 그대로 옮기지 않습니다 [2].

## 직접 분석해 보기

**헥스로 한 번.**

1. 두 후보 위치 아래 `IndexedDB/` 폴더를 통째로 수집하고 사본에서 작업합니다.
2. `.leveldb` 폴더의 파일 목록을 크기·시각과 함께 적습니다.
3. 헥스 보기로 폴더 안 파일을 열어 채널 이름이나 메시지 문장처럼 사람이 읽을 수 있는 문자열이 보이는지 확인합니다. 보이지 않는다고 자료가 없다고 판단하지 않고, 레코드 구조는 [LevelDB와 IndexedDB (LevelDB·IndexedDB)](../../01-foundations/data-formats/leveldb-indexeddb.md)를 보며 읽습니다.

```sh
ls -laT "<IndexedDB 폴더>"/*.leveldb
xxd "<IndexedDB 폴더>/<파일 이름>" | less
```

**공개 도구로 한 번.** 같은 사본을 ccl_chromium_reader로 읽어 [2] 저장소와 레코드 목록을 뽑고, 헥스에서 본 문자열이 도구 결과의 어느 레코드에 들어 있는지 맞춰 봅니다. 도구의 결과는 [도구 검증 (Tool Validation)](../../03-techniques/reporting/tool-validation.md)의 방법으로 확인합니다.

## 교차 검증

| 함께 볼 자료 | 확인할 것 |
|---|---|
| [설치한 앱과 영수증 (Applications·Receipts)](../system-account/installed-apps-receipts.md) | App Store판인지 직접 받은 판인지, 설치 시각 |
| [어떤 앱을 언제 썼나 (App Usage)](../../04-scenarios/activity/app-usage.md) | 앱을 실행한 시각 |
| [충돌·진단 보고서 (DiagnosticReports)](../execution/diagnostic-reports.md) | 슬랙 앱의 진단 보고서와 그 시각 |
| [격리 속성과 다운로드 기록 (Quarantine)](../filesystem/quarantine/index.md) | 슬랙으로 받아 저장한 파일에 붙은 속성 |
| [앱별 네트워크 사용량 (netusage)](../network/netusage.md) | 앱이 주고받은 데이터 양 |
| [정보 탈취 악성 코드 (Infostealer)](../../04-scenarios/incident/infostealer.md) | 쿠키·세션 폴더에 다른 프로세스가 접근한 흔적 |

## 실습

슬랙을 설치한 시험용 맥 또는 공개 시험 이미지(NIST CFReDS 등)에서 아래 질문을 풀어 봅니다.

1. IndexedDB 폴더는 두 후보 위치 중 어디에 있고, 그 위치로 보아 어느 판을 설치했는가?
2. 앱 번들의 버전은 무엇이고, 그 맥의 macOS 버전에서 Homebrew가 적은 마지막 지원판과 어떻게 맞는가?
3. ccl_chromium_reader로 읽은 레코드 가운데 워크스페이스나 채널 이름으로 보이는 값은 무엇인가?
4. `com.tinyspeck.slackmacgap` 환경설정 plist는 어디에 있고, 관리자가 배포한 설정 흔적이 있는가?

## 참고 문헌

1. Homebrew/homebrew-cask `Casks/s/slack.rb` (GitHub) — https://raw.githubusercontent.com/Homebrew/homebrew-cask/master/Casks/s/slack.rb
2. Brave Search 결과 화면 "Slack macOS forensic artifacts com.tinyspeck.slackmacgap IndexedDB" (검색 요약문만 봄, 원문 미확인) — https://search.brave.com/search?q=Slack+macOS+forensic+artifacts+%22com.tinyspeck.slackmacgap%22+IndexedDB
