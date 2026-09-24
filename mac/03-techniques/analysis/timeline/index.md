---
title: "타임라인 작성"
parent: "기법 · 분석"
nav_order: 2030
has_children: true
has_toc: false
---

# 타임라인 작성 (Timeline)

맥의 파일 시스템 시각, 통합 로그, 앱 데이터 속 시각을 한 기준으로 맞춰 한 줄로 세우고, 조작된 시각을 가려내 "무엇이 어떤 순서로 일어났나" 를 기록이 말하는 만큼 재구성하는 방법을 모았습니다.

## 왜 중요한가

타임라인의 재료가 되는 시각은 크게 세 곳에서 나옵니다. APFS 아이노드에 적힌 파일 시각 [1], macOS 10.12 Sierra 에서 도입된 통합 로그의 항목 시각 [2][3], plist·SQLite 같은 앱 데이터 안에 적힌 시각 [5] 이고, 한 가지만으로는 "어느 파일이 바뀌었나" 와 "어느 프로세스가 무엇을 했나" 를 함께 답하지 못해서 여러 출처를 겹쳐 봐야 합니다.

출처마다 시각을 세는 기준도 달라서, APFS 는 1970-01-01 UTC 기준 나노초 [1], HFS+ 는 1904-01-01 GMT 기준 초 [4], 맥 절대 시각은 2001-01-01 GMT 기준 초 [5] 로 세고, 통합 로그는 부팅 뒤 카운터를 timesync 기록으로 벽시계 시각으로 바꿔야 합니다 [2]. 파일 변경 순서를 알려 주는 [파일 시스템 이벤트 (FSEvents)](../../../02-artifacts/filesystem/fsevents/index.md) 에는 아예 시각 칸이 없어서 다른 출처로 시각을 채웁니다.

시각 값은 바꿀 수도 있습니다. 파일 소유자는 생성·수정·접근·추가 시각을 설정할 수 있지만 변경 시각(ctime)만은 설정 시도가 무시되고 [6], 이런 차이가 조작을 가려내는 실마리가 됩니다.

## 한눈에 보기

| 시각 출처 | 위치 | macOS 버전 | 알려 주는 것 |
|---|---|---|---|
| APFS 아이노드·디렉터리 레코드 | APFS 볼륨 메타데이터 | APFS 로 포맷한 볼륨 | 파일마다 생성·수정·변경·접근 시각과 폴더에 추가된 시각 |
| HFS+ 카탈로그 | HFS+ 볼륨(구형 볼륨·외장 디스크) | 볼륨에 따라 | 파일·폴더의 생성·내용 수정·속성 수정·접근·백업 시각 |
| FSEvents | 볼륨의 FSEvents 기록 | 레코드 버전마다 다름(FSEvents 페이지) | 바뀐 경로와 변경 종류, 이벤트 순서(시각 없음) |
| 통합 로그 | `/private/var/db/diagnostics/`, `/private/var/db/uuidtext/` [2] | 10.12 Sierra 부터 [3] | 어느 프로세스가 언제 어떤 메시지를 남겼는지 |
| 앱 데이터 속 시각 | 앱별 plist·SQLite | 앱마다 다름 | 앱이 스스로 기록한 사건 시각(기준 시점이 제각각) |

> 그림 자리: 파일 시스템 시각·통합 로그·앱 데이터 세 줄기가 시각 정규화를 거쳐 한 타임라인으로 모이고, 그 위에서 조작 흔적을 점검하는 흐름

## 읽는 순서

1. [파일 시스템 타임라인 (APFS·FSEvents)](filesystem-timeline.md) — APFS 아이노드의 네 시각과 `date_added` 를 뽑고, 시각 없는 FSEvents 를 순서 정보로 겹치는 절차를 봅니다.
2. [통합 로그 타임라인 (Unified Log)](unified-log-timeline.md) — 로그 아카이브를 모아 시간 구간과 시간대를 정해 뽑고, 기준점이 될 사건을 찍는 절차를 봅니다.
3. [시각 정규화 (Time Normalization)](time-normalization.md) — 1904·1970·2001 기준 시각과 부팅 뒤 카운터를 UTC 한 기준으로 바꾸고, 기록 당시 시간대와 시계 설정을 확인하는 법을 봅니다.
4. [시각 조작 흔적 (Timestomping)](timestomping.md) — 바꿀 수 있는 칸과 바꿀 수 없는 칸을 구분하고, 변경 시각·나노초·다른 출처와의 어긋남으로 조작을 의심하는 법을 봅니다.

## 함께 볼 페이지

- [APFS 구조 (APFS)](../../../01-foundations/disk-volume/apfs/index.md)
- [통합 로그 형식 (Unified Log)](../../../01-foundations/data-formats/unified-log/index.md)
- [맥의 시각 값 (Mac Absolute Time·Unix·HFS)](../../../01-foundations/value-decoding/mac-time-values.md)
- [시간대와 시계 설정 (Time Zone·NTP)](../../../02-artifacts/system-account/time-zone.md)
- [스냅숏과 백업 비교 (Snapshot·Time Machine Diff)](../snapshot-diff.md)
- [맥 사용 시간 재구성 (켜짐·잠자기·로그인) (Usage Time)](../../../04-scenarios/activity/usage-time.md)
- [증거를 없애려 했나 (Anti-Forensics)](../../../04-scenarios/activity/anti-forensics/index.md)

## 참고 문헌

1. libyal libfsapfs — Apple File System (APFS) format — https://raw.githubusercontent.com/libyal/libfsapfs/main/documentation/Apple%20File%20System%20(APFS).asciidoc
2. libyal dtformats — Apple Unified Logging and Activity Tracing formats — https://raw.githubusercontent.com/libyal/dtformats/main/documentation/Apple%20Unified%20Logging%20and%20Activity%20Tracing%20formats.asciidoc
3. Mandiant (Alexander Holcomb), Reviewing macOS Unified Logs (2022-08-31) — https://cloud.google.com/blog/topics/threat-intelligence/reviewing-macos-unified-logs
4. Apple Technical Note TN1150, HFS Plus Volume Format — https://developer.apple.com/library/archive/technotes/tn/tn1150.html
5. Apple Developer, CFAbsoluteTime (문서 JSON) — https://developer.apple.com/tutorials/data/documentation/corefoundation/cfabsolutetime.json
6. setattrlist(2) man 페이지 — https://keith.github.io/xcode-man-pages/setattrlist.2.html
