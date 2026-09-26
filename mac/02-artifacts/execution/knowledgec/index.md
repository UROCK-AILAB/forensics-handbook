---
title: "KnowledgeC"
parent: "아티팩트 · 프로그램 실행 흔적"
nav_order: 660
has_children: true
has_toc: false
---

# KnowledgeC (knowledgeC.db)

KnowledgeC (knowledgeC.db)는 macOS가 앱 사용, 화면 켜짐, 잠금 같은 사용 패턴을 시작·끝 시각이 있는 구간으로 모아 두는 SQLite 데이터베이스이고, 시스템 쪽과 사용자 쪽에 파일이 하나씩 있습니다.

## 왜 중요한가

앱이 앞에 나와 있던 구간을 초 단위 시작·끝 시각으로 남겨서, 어떤 앱을 언제 얼마나 썼는지를 촘촘하게 보여 줍니다 [1]. 같은 표에 화면 백라이트와 잠금 상태도 구간으로 들어 있어서, 앱 사용 구간을 그 시간대의 Mac 상태와 한 타임라인에 놓고 읽을 수 있습니다 [1].

다만 앱 기록은 GUI 앱만 남아서 터미널에서 친 명령이나 백그라운드 실행은 알 수 없고, macOS 10.13 기준으로 약 4주치만 들어 있습니다 [1]. Apple은 이 DB를 공식 문서로 설명하지 않아서, 표와 열의 뜻은 macOS 10.13 기준 공개 분석 자료와 공개 도구 APOLLO의 모듈 SQL로 알려져 있습니다 [1][3].

## 한눈에 보기

| 항목 | 내용 |
|---|---|
| 위치 | 시스템 쪽 `/private/var/db/CoreDuet/Knowledge/knowledgeC.db`, 사용자 쪽 `~/Library/Application Support/Knowledge/knowledgeC.db` (macOS 10.13 기준) [1] |
| 형식 | SQLite. 기록 본체는 ZOBJECT 표이고 ZSOURCE·ZSTRUCTUREDMETADATA 표가 딸림 [1] |
| 시각 | 맥 절대 시각(2001-01-01 00:00:00 UTC부터 센 초) [1] |
| macOS 버전 | 10.13 [1]부터 10.16 [3]까지 알려져 있음. 그 뒤 버전은 실제 데이터로 확인 |
| 알려 주는 것 | 앞에 나와 있던 GUI 앱과 그 구간, 앱 안의 활동 제목, 사파리 URL, 화면 백라이트·잠금·전원 연결 상태 구간 |
| 알려 주지 않는 것 | 터미널 명령, 백그라운드 프로세스 실행, 화면 앞에 있던 사람 |
| 공개 도구 | APOLLO(Apple Pattern of Life Lazy Output'er, Sarah Edwards). knowledgeC용 모듈이 `knowledge_` 로 시작하는 파일 78개로 공개되어 있음 [1][2] |

iOS는 DB 하나로 합쳐 `/private/var/mobile/Library/CoreDuet/Knowledge/` 에 두고, 물리 수집이나 탈옥 기기에서만 얻을 수 있으며 iTunes 백업에는 들어 있지 않습니다 [1].

macOS 11 이후에도 두 경로가 그대로인지, DB를 읽을 때 루트 권한이나 전체 디스크 접근 권한이 필요한지, `-wal`·`-shm` 파일을 어떻게 다뤄야 하는지는 실제 기기에서 확인해야 합니다. 최근 macOS에서는 사용 기록이 바이옴 (Biome)으로 옮겨 갔다는 이야기가 있으니, 최신 기기에서는 두 곳을 모두 찾아봅니다.

APOLLO는 BSD 계열 라이선스(인용 조항)와 GPL v3 이상 가운데 하나를 골라 쓰는 공개 도구입니다 [3].

## 읽는 순서

1. [표와 스트림 구조 (ZOBJECT·Stream)](structure.md) — ZOBJECT·ZSOURCE·ZSTRUCTUREDMETADATA 표의 관계와 주요 열, 스트림 이름과 나오는 버전, 맥 절대 시각을 푸는 법을 다룹니다.
2. [앱 사용 기록 (App Usage)](app-usage.md) — `/app/inFocus`·`/app/usage`·`/app/activity`·`/safari/history` 로 어떤 앱을 언제 얼마나 썼는지 읽고, 무엇을 증명하지 못하는지 정리합니다.
3. [화면·잠금 상태 (Display·Device Lock)](device-state.md) — `/display/isBacklit`·`/device/isLocked`·`/device/isPluggedIn` 의 값과 버전 차이, 앱 사용 구간과 겹쳐 읽는 법을 다룹니다.

## 함께 볼 페이지

- [SQLite 데이터베이스 (SQLite)](../../../01-foundations/data-formats/sqlite/index.md) — DB 파일 자체를 읽을 때
- [맥의 시각 값 (Mac Absolute Time·Unix·HFS)](../../../01-foundations/value-decoding/mac-time-values.md) — 시각 값을 바꿀 때
- [바이옴 (Biome)](../biome/index.md) — 같은 분류의 다른 실행 흔적
- [화면 사용 시간 (Screen Time)](../screen-time.md) — 앱 사용 구간을 다른 기록과 맞춰 볼 때
- [어떤 앱을 언제 썼나 (App Usage)](../../../04-scenarios/activity/app-usage.md) — 조사 시나리오
- [맥 사용 시간 재구성 (켜짐·잠자기·로그인) (Usage Time)](../../../04-scenarios/activity/usage-time.md) — 조사 시나리오

## 참고 문헌

1. Sarah Edwards, "Knowledge is Power! Using the macOS/iOS knowledgeC.db Database to Determine Precise User and Application Usage" (mac4n6.com, 2018-08-05) — https://www.mac4n6.com/blog/2018/8/5/knowledge-is-power-using-the-knowledgecdb-database-on-macos-and-ios-to-determine-precise-user-and-application-usage
2. APOLLO 저장소 modules 폴더 목록 (GitHub API) — https://api.github.com/repos/mac4n6/APOLLO/contents/modules
3. APOLLO 모듈 knowledge_app_usage.txt — https://raw.githubusercontent.com/mac4n6/APOLLO/master/modules/knowledge_app_usage.txt
