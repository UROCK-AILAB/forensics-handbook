---
title: "타임라인 작성"
parent: "기법 · 분석"
nav_order: 1410
has_children: true
has_toc: false
---

# 타임라인 작성 (Timeline)

## 한 줄 요약

Android 기기 곳곳에 남은 기록의 시각을 한 기준으로 옮기고, 서로 맞물려 한 줄로 세운 뒤, 그 사이에 기기 시계가 바뀌었는지까지 확인해 사건 순서를 재구성하는 작업입니다.

## 왜 중요한가

앱 사용·위치·연락처럼 조사 질문은 대부분 "무엇이 먼저였나", "그 시각에 무엇을 했나" 를 묻고, 그 답의 바탕이 타임라인입니다. 그런데 Android 기록은 한 가지 시계로 적히지 않습니다. 벽시계 (wall clock, `System.currentTimeMillis()`) 는 유닉스 에포크부터 밀리초를 세지만 사용자나 통신망이 바꿀 수 있어서 앞뒤로 갑자기 뛸 수 있고, `SystemClock.elapsedRealtime()` 같은 부팅 기준 시계는 단조 증가하지만 부팅할 때마다 0부터 다시 셉니다 [1]. 그래서 기록마다 어느 시계를 썼는지부터 가려야 하고, 벽시계 기록은 시계가 바뀐 시점 앞뒤를 같은 기준으로 볼 수 없습니다.

표기도 기록마다 다릅니다. 관찰한 폰에서는 유닉스 밀리초 정수, 한글이 섞인 현지 형식 문자열, 시간대 오프셋이 붙은 문자열, 연도가 빠진 "월-일 시:분:초" 줄이 한 기기 안에 함께 나왔습니다. 이 차이를 맞추지 않고 값을 그대로 정렬하면 순서와 간격이 틀어집니다.

자동 시각 맞춤은 `time_detector` 서비스가, 자동 시간대 맞춤은 `time_zone_detector` 서비스가 맡습니다 [2]. 시계가 어느 경로로 언제 바뀌었는지는 이 서비스들의 기록으로 확인하고, 자세한 내용은 [시각 조작 흔적](time-manipulation.md) 페이지에 있습니다.

## 한눈에 보기

타임라인 재료가 되는 대표 기록입니다. "관찰" 로 적은 행은 실제 폰의 출력 모양으로 확인한 것입니다.

| 기록 | 보는 곳 | Android 버전 | 타임라인에 알려 주는 것 |
|---|---|---|---|
| 앱 사용 기록 이벤트 | `dumpsys usagestats`, 원본 파일 | 관찰: Android 16 | 앱 전환, 화면 켜짐·꺼짐, 잠금 화면, 알림이 일어난 순간. 원본은 유닉스 밀리초이고 dumpsys 는 사람이 읽는 문자열로 찍음 |
| logcat | `adb logcat` | 관찰: Android 16 | 시스템·앱이 남긴 로그 줄. 기본 형식에는 연도와 시간대가 없음 |
| 서비스 상태 기록 | `dumpsys notification`·`batterystats`·`wifi`·`bluetooth_manager`·`account`·`user` | 관찰: Android 16 | 알림 생성, 화면·전원 상태, 와이파이·블루투스 상태 변화, 계정 추가·삭제, 사용자 잠금 해제 같은 시각 |
| 시각 맞춤 서비스 | `adb shell cmd time_detector dump` [2] | Android 10 이상 [2] | 자동 맞춤 상태, 시각 하한·상한, 시각 변경 로그, 출처(통신망·NTP·GNSS 등)별 최근 시각 제안 이력 |
| NTP 시각 서비스 | `adb shell cmd network_time_update_service dump` [3] | 여러 NTP 서버는 Android 14 이상, 13 이하는 서버 하나 [3] | NTP 로 시각을 맞추는 서비스의 상태 |

기록별 표기 모양과 시계 종류는 [시각 정규화](time-normalization.md), 같은 사건이 어느 기록들에 함께 남는지는 [여러 기록 엮기](correlation.md) 에 정리했습니다. 일반 adb 셸 권한으로 `cmd time_detector dump` 를 실행할 수 있는지는 확인하지 못했습니다.

> 그림 자리: 벽시계 축과 부팅 기준 축을 나란히 그리고, 부팅 경계에서 부팅 기준 값이 0으로 돌아가는 모습과 벽시계가 한 번 뒤로 뛴 구간을 표시한 그림

## 읽는 순서

1. [시각 정규화 (Time Normalization)](time-normalization.md) — 기록마다 다른 시계·단위·기준점·시간대를 UTC 로 옮기고, 원래 값과 표기를 옆에 남기는 방법입니다.
2. [여러 기록 엮기 (Correlation)](correlation.md) — 부팅 경계와 두 시계를 함께 적은 기록을 찾아 서로 다른 기록을 한 줄로 세우고, 연도가 빠진 줄을 채우고, 같은 사건끼리 맞춰 보는 방법입니다.
3. [시각 조작 흔적 (Time Manipulation)](time-manipulation.md) — 벽시계가 언제 어느 경로로 바뀌었는지 시각 맞춤 서비스의 기록과 기록 사이 모순으로 확인하는 방법입니다.

## 함께 볼 페이지

- [시각 값 (Unix 밀리초·Chrome 시각·기타)](../../../01-foundations/value-decoding/time-values.md) — 기준점별 변환 공식
- [시간대와 시각 설정 (Time Zone)](../../../02-artifacts/system-account/time-zone.md) — 기기의 시간대 설정과 그 의미
- [설정 값 (Settings Global·Secure·System)](../../../02-artifacts/system-account/settings.md) — `auto_time` 같은 설정 키를 읽는 법
- [앱 사용 기록 (usagestats)](../../../02-artifacts/app-usage/usagestats/index.md) — 타임라인 뼈대로 자주 쓰는 이벤트 기록
- [logcat (logcat)](../../../02-artifacts/logs/logcat.md), [dumpsys 출력 (dumpsys)](../../../02-artifacts/logs/dumpsys.md) — 로그와 서비스 상태 기록
- [폰 사용 시간 재구성 (Usage Time)](../../../04-scenarios/activity/usage-time.md), [증거를 없애려 했나 (Anti-Forensics)](../../../04-scenarios/activity/anti-forensics/index.md) — 타임라인을 쓰는 조사 시나리오
- [포렌식 보고서 (Forensic Report)](../../reporting/forensic-report.md) — 시각을 보고서에 적는 틀

## 참고 문헌

1. SystemClock.java — AOSP frameworks/base (GitHub 미러, main), https://raw.githubusercontent.com/aosp-mirror/platform_frameworks_base/main/core/java/android/os/SystemClock.java
2. Time detection overview — Android Open Source Project, https://source.android.com/docs/core/connect/time
3. Network time detection — Android Open Source Project, https://source.android.com/docs/core/connect/time/network-time-detection
