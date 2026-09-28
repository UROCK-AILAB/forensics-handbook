---
title: "팀즈"
parent: "아티팩트 · 메시지·메신저"
nav_order: 1420
---

# 팀즈 (Microsoft Teams)

맥의 새 Teams는 `~/Library/Group Containers/UBF8T346G9.com.microsoft.teams` 와 `~/Library/Containers/com.microsoft.teams2` 두 곳에, 클래식 Teams는 `~/Library/Application Support/Microsoft/Teams` 에 데이터를 두고, Microsoft가 캐시라고 부르는 이 폴더들에는 진단 로그도 들어 있습니다 [1].

## 무엇을 기록하나 · 왜 생기나

Teams 앱은 실행하면서 사용자 폴더 안에 캐시 폴더를 만들고, Microsoft는 문제가 생겼을 때 이 폴더를 지우는 방법을 공식 안내로 설명합니다 [1]. 같은 안내에서 Microsoft는 대화가 보이지 않는 문제처럼 원인을 찾아야 하는 경우에는 캐시를 지우지 말라고 하는데, 캐시를 지우면 원인 분석에 필요한 진단 로그까지 지워지기 때문입니다 [1]. 이 설명이 이 폴더들에 진단 로그가 들어 있다는 공식 근거가 됩니다.

캐시를 지운 뒤 앱을 다시 켜면 Teams가 캐시 파일을 다시 만듭니다 [1]. 폴더 안에 어떤 파일이 어떤 형식으로 들어 있는지, 곧 WebView 계열 폴더나 IndexedDB(LevelDB), `MSTeams_*.log` 같은 로그 파일이 있는지는 실제 폴더를 열어 확인합니다.

## 위치와 버전별 차이

Microsoft 안내에 나온 폴더는 아래와 같습니다 [1]. 이 안내는 2026-09-14에 갱신된 판입니다.

| Teams 판 | 맥 데이터 폴더 |
|---|---|
| 새 Teams | `~/Library/Group Containers/UBF8T346G9.com.microsoft.teams` |
| 새 Teams | `~/Library/Containers/com.microsoft.teams2` |
| 클래식 Teams | `~/Library/Application Support/Microsoft/Teams` |

새 Teams는 두 폴더를 함께 쓰니 둘 다 수집하고, 새 Teams로 옮겨 간 맥에는 클래식 폴더가 남아 있을 수 있으니 세 곳을 모두 봅니다. 새 Teams의 번들 ID가 컨테이너 폴더 이름대로 `com.microsoft.teams2` 인지는 앱 번들의 `Info.plist` 에서 직접 읽어 확인합니다. 읽는 법은 [앱 번들 정보 (Info.plist·Code Signature)](../embedded-metadata/app-bundle.md)와 [번들 ID와 팀 ID (Bundle ID·Team ID)](../../01-foundations/value-decoding/bundle-team-id.md)에 있습니다.

윈도우판은 클래식이 `%appdata%\Microsoft\Teams`, 새 Teams가 `%userprofile%\appdata\local\Packages\MSTeams_8wekyb3d8bbwe\LocalCache\Microsoft\MSTeams` 를 씁니다 [1].

macOS 버전이 다른 기기에서도 위 세 곳을 모두 찾아보고, 실제로 데이터가 있는 폴더를 보고서에 적습니다.

## 구조

새 Teams 폴더 안의 세부 구조와 클래식 Teams의 IndexedDB·`Local Storage` 경로와 형식은 실제 폴더에서 확인합니다. 폴더 안에서 LevelDB로 보이는 폴더를 찾으면 [LevelDB와 IndexedDB (LevelDB·IndexedDB)](../../01-foundations/data-formats/leveldb-indexeddb.md)의 방법으로 읽고, SQLite 파일은 [SQLite 데이터베이스 (SQLite)](../../01-foundations/data-formats/sqlite/index.md), plist는 [속성 목록 파일 (Property List)](../../01-foundations/data-formats/plist/index.md)을 봅니다. 파일 이름이나 폴더 이름에서 뜻을 짐작하지 말고, 파일마다 형식을 먼저 가린 뒤에 엽니다.

## 증거로서 의미

**증명하는 것.** 위 폴더가 있으면 이 사용자 계정에서 Teams 앱이 실행되어 데이터를 남긴 적이 있고, 폴더 위치로 새 Teams인지 클래식 Teams인지를 가를 수 있습니다 [1]. 폴더 안에 진단 로그가 남아 있으면 앱이 동작한 기록을 그 로그가 적은 만큼 읽을 수 있습니다.

**증명하지 못하는 것.** 캐시 폴더에 대화가 전부 들어 있다고 볼 수 없어서, 폴더에 없는 대화를 "없었다" 고 말할 수 없습니다. 폴더가 있다는 사실만으로 특정 회의에 참석했거나 특정 상대와 대화했다고 말할 수도 없습니다.

보고서에는 "`○○` 폴더에 ○○시각부터 ○○시각까지의 Teams 진단 로그가 남아 있다" 처럼 기록으로 확인되는 만큼만 씁니다.

## 시각 해석

캐시를 지운 뒤 다시 켜면 Teams가 캐시 파일을 다시 만들어서 [1], 캐시 폴더와 파일의 생성 시각은 앱을 설치한 시각이 아니라 마지막으로 캐시가 다시 만들어진 시각일 수 있습니다. 설치 시각은 [설치한 앱과 영수증 (Applications·Receipts)](../system-account/installed-apps-receipts.md)에서 따로 확인하고, 폴더가 언제 지워지고 다시 생겼는지는 [파일 시스템 이벤트 (FSEvents)](../filesystem/fsevents/index.md)로 봅니다.

진단 로그 안의 시각이 UTC인지 현지 시각인지는 같은 시각의 다른 기록, 예를 들어 [어떤 앱을 언제 썼나 (App Usage)](../../04-scenarios/activity/app-usage.md)에서 얻은 앱 실행 시각과 몇 건을 맞춰 보고 정합니다. 파일 시스템 시각을 읽는 법은 [APFS 구조 (APFS)](../../01-foundations/disk-volume/apfs/index.md)에 있습니다.

## 함정과 한계

Microsoft가 캐시 삭제를 문제 해결 방법으로 공식 안내하는 만큼 [1], 캐시가 지워진 흔적을 곧바로 증거 인멸로 읽지 않습니다. 다만 캐시를 지우면 진단 로그도 함께 지워지니 [1], 사용자가 캐시를 지운 적이 있다면 그 이전 기간의 로그가 비어 있을 수 있습니다. 로그가 비는 기간이 있으면 그 무렵 폴더가 지워진 흔적을 [파일 시스템 이벤트 (FSEvents)](../filesystem/fsevents/index.md)와 [휴지통 (.Trash)](../file-folder-usage/trash.md)에서 찾고, 지운 이유를 판단하는 흐름은 [증거를 없애려 했나 (Anti-Forensics)](../../04-scenarios/activity/anti-forensics/index.md)에서 봅니다.

지워진 캐시의 이전 판은 [타임 머신 (Time Machine)](../filesystem/time-machine/index.md)과 [스냅숏과 백업 비교 (Snapshot·Time Machine Diff)](../../03-techniques/analysis/snapshot-diff.md)에서 찾을 수 있습니다.

## 직접 분석해 보기

**헥스로 한 번.**

1. 세 폴더를 통째로 수집하고 사본에서 작업합니다.
2. 폴더마다 파일 목록을 크기·시각과 함께 적습니다.
3. 파일마다 첫 16바이트를 찍어 형식을 판별합니다. 평문 SQLite는 `SQLite format 3` 과 널 바이트 하나로 시작하고, 아래는 SQLite 파일 형식 명세로 만든 예시이며 실제 데이터에서 나온 값이 아닙니다.

```
00000000  53 51 4c 69 74 65 20 66 6f 72 6d 61 74 20 33 00  |SQLite format 3.|
```

```sh
find "<Teams 폴더>" -type f -exec sh -c 'printf "%s  " "$1"; xxd -p -l 16 "$1"' _ {} \;
```

**공개 도구로 한 번.** `file` 명령으로 같은 파일들의 형식을 다시 확인하고, 이름에 `log` 가 들어간 글자 파일은 사본을 텍스트 편집기로 열어 첫 줄과 마지막 줄의 시각을 적습니다. LevelDB 폴더가 나오면 [LevelDB와 IndexedDB (LevelDB·IndexedDB)](../../01-foundations/data-formats/leveldb-indexeddb.md)에 소개된 공개 도구로 읽고, 결과는 [도구 검증 (Tool Validation)](../../03-techniques/reporting/tool-validation.md)의 방법으로 확인합니다.

## 교차 검증

| 함께 볼 자료 | 확인할 것 |
|---|---|
| [설치한 앱과 영수증 (Applications·Receipts)](../system-account/installed-apps-receipts.md) | 새 Teams와 클래식 Teams의 설치 시각 |
| [어떤 앱을 언제 썼나 (App Usage)](../../04-scenarios/activity/app-usage.md) | 앱을 실행한 시각 |
| [파일 시스템 이벤트 (FSEvents)](../filesystem/fsevents/index.md) | 캐시 폴더가 지워지고 다시 생긴 시각 |
| [충돌·진단 보고서 (DiagnosticReports)](../execution/diagnostic-reports.md) | Teams 앱의 진단 보고서와 그 시각 |
| [앱별 네트워크 사용량 (netusage)](../network/netusage.md) | 앱이 주고받은 데이터 양 |
| [줌 (Zoom)](zoom.md) | 같은 시간대에 쓴 다른 회의 앱 |

## 실습

Teams를 설치한 시험용 맥 또는 공개 시험 이미지(NIST CFReDS 등)에서 아래 질문을 풀어 봅니다.

1. 세 폴더 가운데 어느 폴더가 있고, 그 조합으로 보아 새 Teams와 클래식 Teams 중 무엇을 썼는가?
2. 앱 번들의 `CFBundleIdentifier` 값은 무엇이고, 컨테이너 폴더 이름과 같은가?
3. 폴더 안 파일 가운데 첫 16바이트가 SQLite 평문 서명인 파일은 몇 개인가?
4. 캐시 폴더의 생성 시각과 앱 설치 기록의 시각은 같은가, 다르다면 그 사이에 캐시가 다시 만들어진 흔적이 있는가?

## 참고 문헌

1. Microsoft Learn, "Clear the Teams client cache" (2026-09-14 갱신) — https://learn.microsoft.com/en-us/troubleshoot/microsoftteams/teams-administration/clear-teams-cache
