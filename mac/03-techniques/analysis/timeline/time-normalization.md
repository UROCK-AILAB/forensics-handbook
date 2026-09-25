---
title: "시각 정규화"
parent: "타임라인 작성"
grand_parent: "기법 · 분석"
nav_order: 2060
---

# 시각 정규화 (Time Normalization)

파일 시스템, 통합 로그, 앱 데이터가 저마다 다른 기준 시점과 단위로 적은 시각을 UTC 한 기준으로 바꾸고, 시간대와 시계 설정까지 확인해 한 타임라인에 나란히 놓을 수 있게 만드는 방법을 다룹니다.

## 언제 쓰나

출처가 둘 이상인 타임라인을 만들 때마다 씁니다. 맥에서는 APFS 가 1970년, HFS+ 가 1904년, 앱 데이터의 맥 절대 시각이 2001년을 기준으로 시각을 세고, 통합 로그는 부팅 뒤 카운터를 따로 바꿔야 해서, 값을 그대로 나란히 놓으면 수십 년이 어긋나거나 순서가 뒤집힙니다. 각 시각 값을 읽는 법과 헥스 예시는 [맥의 시각 값 (Mac Absolute Time·Unix·HFS)](../../../01-foundations/value-decoding/mac-time-values.md) 에서 다루고, 이 페이지는 여러 출처를 한 기준으로 맞추는 절차만 봅니다.

## 출처별 기준 시점

| 이름 | 기준 시점 | 단위·형 | 어디서 |
|---|---|---|---|
| APFS 아이노드·디렉터리 레코드·슈퍼블록 시각 | 1970-01-01 00:00:00 UTC | 나노초, 부호 있는 64비트 [1] | APFS 메타데이터 |
| 통합 로그 timesync 벽시계 칸 | 1970 (POSIX 기준) | 나노초, 8바이트 [2] | `.timesync` |
| tracev3 헤더 POSIX 시각 | 1970 | 초, 부호 있는 4바이트 [2] | `.tracev3` 헤더 |
| 마크 연속 시각 | 부팅 시점(부트 레코드 기준 0) | 인텔 맥은 나노초, 애플 실리콘 맥은 틱이라 타임베이스로 변환 [2][3] | tracev3·timesync |
| HFS+ 시각 | 1904-01-01 00:00:00 GMT | 초, UInt32 [5] | HFS+ 카탈로그·볼륨 헤더 |
| 맥 절대 시각 (CFAbsoluteTime) | 2001-01-01 00:00:00 GMT | 초, 실수(CFTimeInterval) [6] | plist·SQLite 등 앱 데이터 |

맥 절대 시각은 2001-01-01 00:00:00 GMT 기준 초이고, 음수는 그 이전, 양수는 그 이후를 뜻합니다 [6]. 1970 기준으로 바꾸는 상수는 2001 기준이면 978,307,200초(1970~2000 의 31년, 윤일 8일을 더한 11,323일 × 86,400초)이고, HFS+ 기준이면 2,082,844,800초(1904~1969 의 66년, 윤일 17일을 더한 24,107일 × 86,400초)입니다.

## 절차

1. **출처마다 기준 시점과 단위를 적습니다.** 타임라인에 넣을 출처마다 위 표에서 기준 시점, 단위(초·나노초·틱), 정수인지 실수인지, UTC 인지 현지 시각인지를 적습니다. 도구가 이미 바꿔 준 값이라면 도구가 어느 기준으로 해석했는지도 함께 적습니다.

2. **1970 UTC 기준으로 바꿉니다.** 맥 절대 시각에는 978,307,200을 더하고, HFS+ 시각에서는 2,082,844,800을 빼고, APFS 나노초는 10억으로 나눕니다. 명세로 만든 예시로 맥 절대 시각 `700000000` 은 1970 기준 `1678307200` 초가 되어 2023-03-08 20:26:40 UTC 이고, HFS+ 값 `3786912000` 은 1970 기준 `1704067200` 초가 되어 2024-01-01 00:00:00 UTC 입니다. 원래 값은 지우지 않고 옆 칸에 남깁니다.

3. **0 과 범위를 벗어난 값을 가려냅니다.** APFS 는 설정하지 않은 시각을 0 으로 두고 [1], 옛 Mac OS 가 만든 HFS+ 파일의 accessDate 도 0 이라서 [5], 변환하면 각각 1970-01-01 과 1904-01-01 이 나옵니다. 이 값은 사건이 아니라 빈칸으로 표시합니다. HFS+ 가 나타낼 수 있는 가장 늦은 시각은 2040-02-06 06:28:15 GMT 이고 윤초는 반영하지 않습니다 [5].

4. **현지 시각으로 적힌 칸을 따로 다룹니다.** HFS+ 에서는 볼륨 헤더의 createDate 만 볼륨 식별자로 쓰이기 때문에 GMT 가 아니라 현지 시각으로 저장하고, 볼륨 헤더의 modifyDate·backupDate·checkedDate 와 카탈로그 시각은 GMT 입니다 [5]. 이 칸 하나는 당시 시간대를 알아낸 뒤 그만큼 빼거나 더해서 UTC 로 바꿉니다.

5. **기록 당시 시간대를 확인합니다.** 통합 로그는 tracev3 헤더와 timesync 레코드마다 시간대 오프셋(분)과 일광절약 플래그를 함께 적어서 [2], 기록 당시 맥이 어느 시간대로 설정돼 있었는지 알아내는 근거로 쓸 수 있습니다. 맥의 시간대 설정은 [시간대와 시계 설정 (Time Zone·NTP)](../../../02-artifacts/system-account/time-zone.md) 에서 확인하고, 두 결과가 다르면 어느 쪽을 따랐는지 적습니다.

6. **시계가 맞았는지 따집니다.** 시스템 설정의 일반 메뉴 속 날짜 및 시간 화면에는 네트워크 시간 서버로 "날짜와 시간 자동으로 설정" 과 "현재 위치를 사용하여 자동으로 시간대 설정" 항목이 있습니다(macOS 12 Monterey 이후) [7]. 자동 설정이 꺼져 있었다면 맥 시계가 실제 시각과 어긋났을 수 있어서, 외부 서버 기록이나 메일 헤더처럼 맥 밖에서 찍힌 시각과 몇 군데 맞춰 봅니다. 시간 서버와 동기화한 기록이 맥 어디에 남는지는 공개 자료가 없어 검체에서 확인합니다.

7. **표시할 때만 현지 시각으로 바꿉니다.** 타임라인 원본은 UTC 로 두고, 보고서에 현지 시각을 쓸 때는 `+09:00` 처럼 오프셋을 함께 적습니다. `log show` 는 `--timezone` 을 주지 않으면 항목이 기록될 당시의 시간대로 보여 주므로 [4], 통합 로그는 `--timezone UTC` 로 뽑고 뽑는 방법은 [통합 로그 타임라인 (Unified Log)](unified-log-timeline.md) 을 따릅니다.

> 그림 자리: 1904·1970·2001 세 기준 시점을 한 시간 축에 놓고, 같은 순간이 세 기준에서 각각 어떤 숫자가 되는지 보인 그림

## 도구

변환은 어느 스크립트 언어로든 덧셈·뺄셈 몇 줄이면 되지만, 도구가 대신 바꿔 준 값은 기준 시점을 잘못 골랐는지 확인하기 어렵습니다. 위 예시처럼 원래 값과 답을 아는 값 몇 개를 도구에 넣어 결과가 맞는지 보고, 그 과정은 [도구 검증 (Tool Validation)](../../reporting/tool-validation.md) 방식으로 남깁니다.

## 함정과 한계

기준 시점을 잘못 고르면 1970 과 2001 사이인 31년, 1904 와 1970 사이인 66년만큼 통째로 밀리는데, 결과가 그럴듯한 날짜로 나오기도 해서 눈으로만 보면 놓칩니다. 맥 절대 시각은 음수도 올바른 값이라서 [6] 2001년 이전 날짜가 나왔다고 곧바로 오류로 보지 않고, 반대로 실수인 맥 절대 시각과 정수인 APFS 나노초를 같은 칸에 섞으면 단위 차이로 자릿수가 크게 어긋납니다.

일광절약 시간이 바뀌는 날에는 현지 시각이 한 시간 겹치거나 비어서, 현지 시각으로만 적힌 값은 두 가지로 해석될 수 있습니다. 시스템 시간대 설정이 저장되는 위치는 [시간대와 시계 설정 (Time Zone·NTP)](../../../02-artifacts/system-account/time-zone.md) 에서 보고, 브라우저 기록의 시각 형식은 [사파리 (Safari)](../../../02-artifacts/browsers/safari/index.md), [크롬·엣지·웨일 (Chromium 계열)](../../../02-artifacts/browsers/chromium/index.md), [파이어폭스 (Firefox)](../../../02-artifacts/browsers/firefox.md) 페이지를 따릅니다.

## 결과를 어떻게 해석하나

정규화한 타임라인은 "여러 기록의 시각을 같은 기준으로 놓으면 이 순서가 된다" 를 보여 줄 뿐이고, 맥 시계 자체가 틀렸다면 모든 줄이 함께 밀려 있을 수 있습니다. 보고서에는 출처마다 쓴 기준 시점과 변환 상수, 시간대를 어떻게 확인했는지를 적고, "HFS+ 카탈로그의 contentModDate 값을 1904 GMT 기준으로 해석하면 2024-01-01 00:00:00 UTC 이다" 처럼 원래 값과 해석 기준을 함께 씁니다.

## 참고 문헌

1. libyal libfsapfs — Apple File System (APFS) format — https://raw.githubusercontent.com/libyal/libfsapfs/main/documentation/Apple%20File%20System%20(APFS).asciidoc
2. libyal dtformats — Apple Unified Logging and Activity Tracing formats — https://raw.githubusercontent.com/libyal/dtformats/main/documentation/Apple%20Unified%20Logging%20and%20Activity%20Tracing%20formats.asciidoc
3. Mandiant (Alexander Holcomb), Reviewing macOS Unified Logs (2022-08-31) — https://cloud.google.com/blog/topics/threat-intelligence/reviewing-macos-unified-logs
4. log(1) man 페이지 — https://keith.github.io/xcode-man-pages/log.1.html
5. Apple Technical Note TN1150, HFS Plus Volume Format — https://developer.apple.com/library/archive/technotes/tn/tn1150.html
6. Apple Developer, CFAbsoluteTime (문서 JSON) — https://developer.apple.com/tutorials/data/documentation/corefoundation/cfabsolutetime.json
7. Apple 지원, Mac 사용 설명서 — 날짜와 시간 자동 설정 — https://support.apple.com/guide/mac-help/set-the-date-and-time-automatically-mchlp2996/mac
