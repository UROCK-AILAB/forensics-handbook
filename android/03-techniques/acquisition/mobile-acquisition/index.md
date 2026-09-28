---
title: "모바일 증거 확보"
parent: "기법 · 조사 절차·증거 확보"
nav_order: 1300
has_children: true
has_toc: false
---

# 모바일 증거 확보 (Acquisition)

Android 기기에서 데이터를 바꾸지 않고 꺼내는 방법을 수집 방식, 압수와 보관, ADB, 백업, 결과물 형식과 해시로 나눠 안내하는 허브 페이지입니다.

## 왜 중요한가

증거 보존 (Preservation)은 기기와 이동식 매체의 데이터를 바꾸지 않고 보관하는 과정이고, 법과학 절차의 첫 단계입니다[4]. 모바일 기기는 켜져 있는 동안 기기 시계 같은 정보를 계속 갱신하고, 새로 들어오는 전화·문자도 기기의 저장 상태를 바꿀 수 있습니다[4]. 그래서 같은 기기를 연달아 두 번 수집해도 전체 데이터의 해시는 달라지지만, 개별 파일·디렉터리처럼 항목별로 계산한 해시가 대체로 같게 나옵니다[4].

Android 10 이상으로 출시되는 기기는 모두 파일 단위 암호화 (File-Based Encryption, FBE)를 써야 하고, 기본 저장 위치인 CE (Credential Encrypted) 영역은 사용자가 기기 잠금을 푼 뒤에만 쓸 수 있습니다[1]. 이 때문에 Android 10 이후 기기에서는 사용자가 잠금을 풀었는지에 따라 수집할 수 있는 범위가 크게 갈리고, 압수할 때 전원과 통신을 어떻게 다루는지가 뒤의 수집 전체에 영향을 줄 수 있습니다.

수집 범위를 정할 때는 앱 수도 함께 봅니다. 기기 한 대에 시스템 앱 486개, 사용자가 설치한 앱 168개처럼 앱이 수백 개 있을 수 있고, 앱마다 백업을 끄거나 백업 규칙을 따로 정할 수 있어[3] 경로 하나로 모든 앱 데이터를 얻는다고 볼 수 없습니다.

## 한눈에 보기

수집 도구는 NIST 분류로 다섯 단계로 나뉘고, 위 단계로 갈수록 더 기술적이고 기기를 더 건드리며 시간과 비용이 더 듭니다[4]. 아래 표는 그 분류에 Android 에서 흔히 쓰는 ADB 와 백업 경로를 더해 정리한 것입니다.

| 수집 경로 | 조건 | 얻는 것 | 자세히 |
|---|---|---|---|
| 수동 추출 (Manual Extraction, NIST 1단계) | 기기 화면을 조작할 수 있어야 함 | 화면에 띄운 내용의 기록 | [수집 방식 비교](methods.md) |
| 논리 추출 (Logical Extraction, NIST 2단계) | 운영체제를 거쳐 읽음 | 파일 시스템 파티션 위의 디렉터리·파일 | [수집 방식 비교](methods.md) |
| 물리 추출 (NIST 3~5단계: Hex Dumping/JTAG, Chip-Off, Micro Read) | 고급 교육과 장비, 기기를 더 건드림 | 메모리 칩의 복사본·이미지, 삭제된 객체와 미할당 영역의 잔재(파싱·복호·해석이 따로 필요함) | [수집 방식 비교](methods.md) |
| ADB | USB 디버깅이 켜져 있고, 잠금을 푼 상태에서 컴퓨터의 RSA 키를 허용해야 함 | 셸 권한으로 읽히는 파일, dumpsys·logcat·버그 리포트 출력 | [ADB로 볼 수 있는 것](adb.md) |
| Google 계정 백업 | 사용자가 백업을 켰을 때 Google 계정에 저장됨 | 앱과 앱 데이터, 통화 기록, 연락처, 기기 설정, SMS·MMS[6] | [백업으로 수집](backups.md) |
| 기기 간 전송 (D2D) | 앱이 클라우드 백업과 다른 규칙을 줄 수 있음 | 앱이 전송 대상으로 정한 파일 | [백업으로 수집](backups.md) |

Android 버전과 제조사에 따라 달라지는 점은 아래와 같고, 자세한 내용은 오른쪽 페이지에 있습니다.

| 버전·제조사 | 달라지는 점 | 자세히 |
|---|---|---|
| Android 4.2.2 (API 17) 이상 | adb 로 연결하면 컴퓨터의 RSA 키를 받아들일지 묻는 창이 뜨고, 잠금을 풀어 허용해야 adb 명령이 됨[2] | [ADB](adb.md) |
| Android 6.0 (API 23) 이상을 대상으로 하는 앱 | 앱 데이터 자동 백업 (Auto Backup)에 자동으로 들어감[3] | [백업](backups.md) |
| Android 7.0 | FBE 지원 시작[1] | [수집 방식 비교](methods.md) |
| Android 9 이상 | 사용자가 백업을 켜고 화면 잠금을 설정했으면 Auto Backup 을 기기 PIN·패턴·비밀번호로 종단간 암호화함[3] | [백업](backups.md) |
| Android 10 이상으로 출시된 기기 | FBE 필수, CE 영역은 잠금 해제 뒤에만 쓸 수 있음[1] | [수집 방식 비교](methods.md), [압수와 보관](seizure-handling.md) |
| Android 11 (API 30) 이상 휴대폰 | 같은 무선 네트워크에서 무선 디버깅을 쓸 수 있음[2] | [ADB](adb.md) |
| Android 12 (API 31) 이상 | 12 이상을 대상으로 하는 앱은 adb backup 에서 앱 데이터가 빠지고(debuggable 앱만 예외)[5], 백업 규칙을 클라우드 백업과 기기 간 전송으로 나눠 정함[3] | [ADB](adb.md), [백업](backups.md) |
| 삼성 One UI | settings global·secure 에 Smart Switch 관련 키가 있음 | [백업](backups.md) |

## 읽는 순서

방식의 차이를 먼저 익히고, 현장에서 기기를 다루는 법을 본 다음, 경로별 수집과 결과물 관리로 넘어가는 순서입니다.

1. [수집 방식 비교 (논리·파일 시스템·물리)](methods.md) — NIST 다섯 단계 분류와, FBE 의 CE·DE 영역이 수집 범위를 어떻게 가르는지 다룹니다.
2. [압수와 보관 (전원·통신 차단)](seizure-handling.md) — 비행기 모드·전원 끄기·차폐 용기의 단점과, 기기 시각과 연결된 컴퓨터를 다루는 법을 정리합니다.
3. [ADB로 볼 수 있는 것 (ADB)](adb.md) — adb 구조와 켜는 조건, 일반 셸 권한으로 읽히는 출력, adb 를 켤 때 바뀌는 설정 키를 봅니다.
4. [백업으로 수집 (Google 백업·Smart Switch)](backups.md) — Google 계정 백업과 Auto Backup 이 담는 것과 빼는 것, 기기에 남는 백업 관련 설정 키를 다룹니다.
5. [결과물 형식과 해시 (Extraction Formats·Hash)](formats-hash.md) — adb backup 파일과 버그 리포트의 형식, 분석 도구가 받는 입력 형식, 해시로 무결성을 지키는 방법을 설명합니다.

## 함께 볼 페이지

- [조사 절차 (Investigation Process)](../investigation-process.md) — 증거 확보 앞뒤의 조사 흐름
- [클라우드 데이터 (Google Takeout 등)](../cloud-data.md) — 기기 밖 계정에 남은 데이터
- [저장 공간 암호화 (Encryption)](../../../01-foundations/storage/encryption/index.md) — FBE 와 CE·DE 영역의 구조
- [공용 저장 공간 (Shared Storage·/sdcard)](../../../01-foundations/storage/shared-storage.md) — adb 로 흔히 읽는 공용 폴더
- [사용자와 프로필 (Multi-user·users)](../../../02-artifacts/system-account/users-profiles.md) — 사용자마다 따로 있는 데이터 경로
- [보안 폴더와 작업 프로필 (Secure Folder·Work Profile)](../../../01-foundations/security-model/secure-folder-work-profile.md)
- [설정 값 (Settings Global·Secure·System)](../../../02-artifacts/system-account/settings.md) — 수집 전후로 바뀌는 설정 키
- [구글 백업 (Google Backup)](../../../02-artifacts/mail-cloud/google-backup.md)
- [dumpsys 출력 (dumpsys)](../../../02-artifacts/logs/dumpsys.md), [logcat (logcat)](../../../02-artifacts/logs/logcat.md), [버그 리포트 (bugreport)](../../../02-artifacts/logs/bugreport.md)
- [도구 검증 (Tool Validation)](../../reporting/tool-validation.md), [포렌식 보고서 (Forensic Report)](../../reporting/forensic-report.md)

## 참고 문헌

1. File-based encryption — Android Open Source Project, https://source.android.com/docs/security/features/encryption/file-based
2. Android Debug Bridge (adb) — Android Developers, https://developer.android.com/tools/adb
3. Back up user data with Auto Backup — Android Developers, https://developer.android.com/identity/data/autobackup
4. NIST SP 800-101 Rev.1, Guidelines on Mobile Device Forensics (Ayers, Brothers, Jansen, 2014), https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-101r1.pdf
5. Behavior changes: apps targeting Android 12 — Android Developers, https://developer.android.com/about/versions/12/behavior-changes-12
6. Back up or restore data on your Android device — Google Android Help, https://support.google.com/android/answer/2819582?hl=en
