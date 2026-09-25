---
title: "앱 사용 기록"
parent: "아티팩트 · 앱 설치·사용 흔적"
nav_order: 450
has_children: true
has_toc: false
---

# 앱 사용 기록 (usagestats)

## 한 줄 요약

앱 사용 기록(usagestats)은 시스템 서비스(UsageStatsService)가 앱 화면 전환, 화면 켜짐과 꺼짐, 잠금 화면, 알림, 포그라운드 서비스 같은 사건을 기기 시계 기준 밀리초로 적고 일·주·월·연 구간(interval)으로 묶어 저장하는 기록입니다 [1][2].

## 왜 중요한가

usagestats 에는 두 층의 기록이 들어 있습니다. 하나는 개별 이벤트(event_log)로, 어느 패키지의 화면이 언제 앞으로 나오고 언제 사라졌는지, 화면이 언제 켜지고 잠금 화면이 언제 숨었는지를 한 건씩 적습니다. 다른 하나는 패키지별 누적 통계로, 마지막 사용 시각과 총 사용 시간, 실행 횟수 같은 값을 모읍니다 [2][3]. 그래서 "어떤 앱을 언제 썼나", "폰을 언제 켜서 얼마나 썼나" 같은 질문에 앱 자체의 데이터와 따로 답할 수 있는 시스템 쪽 기록이 됩니다.

다만 이벤트는 시스템이 며칠만 보관하고 [4], 사용자의 조작과 시스템의 동작이 한 목록에 섞여 있어서 읽는 법을 알고 봐야 합니다. 앱이 이 기록을 API(UsageStatsManager)로 읽으려면 PACKAGE_USAGE_STATS 권한이 필요하고, 앱이 권한을 선언해도 사용자가 설정 앱에서 따로 허용해야 합니다 [4]. 공개 파서로는 ALEAPP 의 usagestats 모듈이 XML 과 프로토콜 버퍼 파일을 모두 읽습니다 [5].

## 한눈에 보기

| 위치 | Android 버전 | 알려 주는 것 |
|---|---|---|
| `/data/system_ce/<사용자ID>/usagestats/` | 현행 AOSP 기준(옮긴 시점은 확인 못 함) | 구간별 개별 이벤트와 패키지별 누적 통계, 이름 대응표(`mappings`) |
| `/data/system/usagestats/<사용자ID>/` | 예전 위치, 새 위치로 옮긴 뒤 지움 | 옮기기 전의 같은 기록 (`/data/system/usagestats/` 폴더 자체는 전체 사용자 공용 파일을 두는 곳으로 계속 씀) |
| `dumpsys usagestats` 출력 | Android 16 에서 관찰 | 최근 몇 시간의 이벤트와 메모리의 일간 통계 (확인 범위: Android 16, One UI 8.5) |

파일 형식은 버전 1~3이 XML, 4가 프로토콜 버퍼, 5가 패키지 이름을 번호로 바꿔 저장하는 프로토콜 버퍼 V2 이고, 현행 AOSP 의 기본은 버전 5입니다 [1]. 경로와 형식의 자세한 내용은 아래 "파일 구조" 페이지에 있습니다.

## 읽는 순서

1. [파일 구조 (usagestats)](structure.md) — 폴더와 파일 구성, 형식 버전, 보관 기간, 프로토콜 버퍼 V2 의 칸, 파일 안 시각을 절대 시각으로 바꾸는 법, 라이브 기기의 dumpsys 출력 모양을 다룹니다.
2. [이벤트 종류 (Event Types)](event-types.md) — 0~31번 이벤트의 이름과 뜻, 이벤트마다 붙는 칸, 대기 버킷 값, 조회하는 앱에 따라 가려지는 정보를 정리합니다.
3. [해석 함정 (Pitfalls)](pitfalls.md) — 증명하는 것과 증명하지 못하는 것, 시각 변경, 사용자 조작으로 오해하기 쉬운 이벤트, 빠지거나 겹치는 기록, 보고서 문장 예를 다룹니다.

## 함께 볼 페이지

- [디지털 웰빙 (Digital Wellbeing)](../digital-wellbeing.md), [배터리 사용 기록 (batterystats)](../batterystats.md), [알림 기록 (Notification History)](../notification-history.md), [최근 앱 화면 (Recents·Snapshots)](../recents-snapshots.md) — 같은 사용 행위를 다른 쪽에서 남기는 기록
- [프로토콜 버퍼 (Protocol Buffers)](../../../01-foundations/data-formats/protobuf.md), [시각 값](../../../01-foundations/value-decoding/time-values.md), [패키지 이름과 UID](../../../01-foundations/value-decoding/package-uid.md) — 파일을 직접 읽을 때 필요한 기초
- [dumpsys 출력 (dumpsys)](../../logs/dumpsys.md) — 라이브 기기에서 서비스 상태를 뽑는 방법
- [어떤 앱을 언제 썼나 (App Usage)](../../../04-scenarios/activity/app-usage.md), [폰 사용 시간 재구성 (Usage Time)](../../../04-scenarios/activity/usage-time.md) — 이 기록을 쓰는 조사 시나리오

## 참고 문헌

1. UsageStatsDatabase.java — AOSP frameworks/base (GitHub 미러, main), https://raw.githubusercontent.com/aosp-mirror/platform_frameworks_base/main/services/usage/java/com/android/server/usage/UsageStatsDatabase.java
2. usagestatsservice_v2.proto — AOSP frameworks/base (GitHub 미러, main), https://raw.githubusercontent.com/aosp-mirror/platform_frameworks_base/main/core/proto/android/server/usagestatsservice_v2.proto
3. UsageEvents.java — AOSP frameworks/base (GitHub 미러, main), https://raw.githubusercontent.com/aosp-mirror/platform_frameworks_base/main/core/java/android/app/usage/UsageEvents.java
4. UsageStatsManager.java — AOSP frameworks/base (GitHub 미러, main), https://raw.githubusercontent.com/aosp-mirror/platform_frameworks_base/main/core/java/android/app/usage/UsageStatsManager.java
5. ALEAPP usagestats.py — abrignoni/ALEAPP, https://raw.githubusercontent.com/abrignoni/ALEAPP/main/scripts/artifacts/usagestats.py
