---
title: "악성 앱 흔적 분석"
parent: "기법 · 분석"
nav_order: 1490
has_children: true
has_toc: false
---

# 악성 앱 흔적 분석 (Malicious App Triage)

설치된 앱 가운데 악성 앱이나 감시 앱일 수 있는 것을 권한·설정, 활동 흔적, APK 파일 세 방향으로 좁혀 가며 확인하는 분석 기법을 모은 허브입니다.

## 왜 중요한가

시스템 앱이 486개, 사용자가 설치한 앱이 168개 든 폰도 있습니다. 이만큼 많은 앱을 하나씩 열어 보기는 어려워서, 권한과 설정으로 후보를 추리고 활동 흔적과 서명으로 좁혀 가는 순서가 필요합니다. 이 묶음은 그 순서를 권한·설정에 남은 흔적, 감시 앱 (stalkerware) 의 흔적, APK 파일 확인 세 페이지로 나눠 다룹니다.

도구 쪽 사정도 바뀌었습니다. 공개 도구 MVT (Mobile Verification Toolkit) 는 adb 로 Android 기기를 직접 분석하는 기능을 없앴고, 수집 도구로 AndroidQF 를 권합니다 [1]. AndroidQF 는 Android 기기에서 자료를 모으는 단독 실행 Go 프로그램이고, 수집과 분석을 나눠 늘 같은 형식의 결과를 얻고, 모은 결과는 `mvt-android check-androidqf` 로 분석합니다 [1]. bugreport 같은 진단 로그는 형식이 Android 버전과 제조사마다 다를 수 있고, Android 백업으로 얻는 자료는 적습니다 [1]. 이 묶음은 한 가지 수집물이나 도구에 기대지 않고 여러 흔적을 맞춰 보는 순서로 짰습니다.

## 한눈에 보기

| 확인 대상 | 위치 | Android 버전·범위 | 알려 주는 것 |
|---|---|---|---|
| 권한 부여 기록 | 파일 시스템 수집본의 packages.xml | 공개 자료 없음 | 앱이 받은 권한과 부여 여부 |
| 민감한 설정 | settings 의 secure·global·system | 실제 기기로 확인 | 접근성·알림 접근·입력기·adb 같은 설정이 수집 시점에 어땠는지 |
| 제한된 설정 | 앱 정보 화면의 메뉴 (허용 상태가 남는 파일·키는 공개 자료 없음) | 일부 단계는 Android 13 이상 | 접근성 같은 설정을 앱에 허용했는지 |
| 앱 활동 | `dumpsys usagestats`·`notification`·`account` | 실제 기기로 확인 | 화면에 안 보인 채 도는 앱, 늘 떠 있는 알림, 계정 추가·삭제 |
| 공개 지표 대조 | stalkerware-indicators 저장소 | 기기 버전과 무관 | 알려진 감시 앱과 패키지 이름·해시·인증서가 같은지 |
| APK 서명 | APK 파일 | v1 은 처음부터, v2 는 Android 7.0, v3 은 9, v4 는 11부터 | 누가 서명했고 서명 뒤로 파일이 바뀌었는지 |

## 읽는 순서

1. [권한과 설정으로 찾기 (Permissions·Settings)](permissions-settings.md) — 권한 종류, packages.xml 의 권한 기록, 살펴볼 설정 키와 제한된 설정으로 후보 앱을 추립니다.
2. [감시 앱 흔적 (Stalkerware)](stalkerware.md) — 공개 지표와 대조하고, 앱 사용·알림·계정 기록에서 후보가 움직인 흔적을 읽습니다.
3. [APK 확인 (APK Check)](apk-check.md) — 서명 방식과 인증서를 확인하고 해시·인증서를 지표와 맞춥니다.

## 함께 볼 페이지

- [몰래 설치된 감시 앱 (Stalkerware)](../../../04-scenarios/incident/stalkerware.md) — 감시 앱 사건을 처음부터 끝까지 조사하는 순서
- [악성 앱은 어디서 들어왔나 (Initial Access)](../../../04-scenarios/incident/initial-access.md) — 설치 경로를 따라가는 시나리오
- [설치된 앱 (packages.xml)](../../../02-artifacts/app-usage/packages/index.md) — 설치 기록 파일의 구조
- [기기 관리자와 접근성 권한 (Device Admin·Accessibility)](../../../02-artifacts/credentials-security/device-admin-accessibility.md) — 접근성 서비스와 기기 관리자 기록
- [앱 사용 기록 (usagestats)](../../../02-artifacts/app-usage/usagestats/index.md) — 활동 흔적의 시각과 보존 기간
- [모바일 증거 확보 (Acquisition)](../../acquisition/mobile-acquisition/index.md) — adb·수집 도구로 자료를 모으는 방법

## 참고 문헌

1. MVT Android forensic methodology — Mobile Verification Toolkit docs, https://docs.mvt.re/en/latest/android/methodology/
