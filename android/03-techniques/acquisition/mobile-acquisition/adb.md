---
title: "ADB로 볼 수 있는 것"
parent: "모바일 증거 확보"
grand_parent: "기법 · 조사 절차·증거 확보"
nav_order: 1330
---

# ADB로 볼 수 있는 것 (ADB)

안드로이드 디버그 브리지 (Android Debug Bridge, adb) 로 기기에서 무엇을 읽을 수 있는지, 쓰려면 어떤 조건이 필요한지, 쓰고 나면 기기에 어떤 흔적이 남는지를 정리합니다. 공식 문서와 현행 AOSP 소스(frameworks/base 의 main 가지)로 확인한 내용은 그대로 쓰고, 실제 폰에서 루팅하지 않고 부트로더도 잠긴 채 adb 일반 셸 권한(UID 2000)으로 읽은 내용에는 확인 범위를 붙였습니다. 잠금을 풀거나 보안을 우회하는 방법은 다루지 않습니다.

## 한 줄 요약

adb 는 USB 디버깅을 켜고 잠금을 풀어 연결한 컴퓨터를 허용한 기기에서만 쓸 수 있고, 루팅하지 않은 기기의 일반 셸 권한으로는 dumpsys·logcat·설정 값·공유 저장소처럼 시스템이 내어 주는 범위를 읽습니다.

## adb 의 구성

adb 는 기기와 통신하는 명령줄 도구이고, 컴퓨터에서 명령을 보내는 클라이언트, 기기에서 명령을 실행하는 백그라운드 프로세스인 데몬 adbd, 컴퓨터에서 둘 사이의 통신을 관리하는 서버의 세 부분으로 돌아갑니다 [1]. 서버는 컴퓨터의 로컬 TCP 5037 포트에서 기다리고, 연결된 기기 목록은 `adb devices -l` 로 보고 서버는 `adb kill-server` 로 멈춥니다 [1].

## 쓸 수 있는 조건

| 조건 | 해당 버전 | 내용 |
|---|---|---|
| 개발자 옵션 | Android 4.2(API 17) 이상 | 개발자 옵션 화면이 기본으로 숨어 있고, 설정의 개발자 옵션에서 USB 디버깅을 켜야 USB 로 쓸 수 있습니다 [1] |
| 컴퓨터 허용 | Android 4.2.2 이상 | 연결할 때 컴퓨터의 RSA 키를 받아들일지 묻는 창이 뜨고, 기기 잠금을 풀고 이 창에서 허용해야 adb 명령이 됩니다 [1] |
| 무선 디버깅 | 휴대폰은 Android 11(API 30) 이상 | 컴퓨터와 기기가 같은 무선 네트워크에 있어야 합니다 [1] |

두 조건을 합치면 adb 수집은 개발자 옵션과 USB 디버깅이 켜져 있고, 잠금을 풀어 허용 창에서 컴퓨터를 받아들일 수 있을 때만 됩니다. 이 정리는 [1]에서 끌어낸 해석입니다. 잠금 해제 여부가 수집 범위 전체에 주는 영향은 [수집 방식 비교](methods.md) 페이지에 있습니다.

## 켜면 남는 흔적

관찰한 폰의 설정에는 adb 와 개발자 옵션에 관련된 이름의 키가 아래처럼 있었습니다 (확인 범위: Android 16, One UI 8.5). 각 값의 뜻은 출처로 확인하지 않았습니다.

| 어디서 | 키 이름 |
|---|---|
| settings global | `adb_enabled`, `adb_wifi_enabled`, `adb_allowed_connection_time`, `development_settings_enabled` |
| settings secure | `rampart_blocked_adb_cmd`, `rampart_snapshot_adb_enabled`, `rampart_snapshot_adb_wifi_enabled` |

secure 쪽 `rampart_` 키는 삼성 기능과 관련 있어 보이지만 어떤 기능인지는 확인하지 못했습니다. 조사자가 adb 를 켜면 이런 설정 값도 바뀌어서, 수집 전 상태를 기록해 두지 않으면 나중에 누가 언제 켰는지를 가를 수 없습니다. 이 판단은 관찰한 키 이름과 [1]을 합쳐 끌어낸 해석입니다. 설정 값을 읽는 법은 [설정 값](../../../02-artifacts/system-account/settings.md) 페이지에 있습니다.

## 절차

1. adb 를 켜기 전에 개발자 옵션과 USB 디버깅이 이미 켜져 있었는지 화면으로 확인하고, 조작하는 모습과 함께 기록합니다. 기록 방법은 [압수와 보관](seizure-handling.md) 페이지를 따릅니다.
2. `adb devices -l` 로 기기가 연결됐는지 확인합니다 [1].
3. `adb shell` 뒤에 명령을 붙여 하나씩 실행하고, 명령마다 실행한 시각을 기록합니다. `adb shell` 만 치면 대화형 셸이 열리고, 설치된 패키지 목록은 `pm list packages` 로 봅니다 [1].
4. `adb bugreport` 로 버그 리포트를 받습니다 [2].
5. 필요한 파일은 `adb pull` 로 폴더째 복사합니다. `adb push` 는 반대 방향이라 수집에는 쓰지 않습니다 [1].
6. 받은 결과물마다 해시를 계산합니다. 방법은 [결과물 형식과 해시](formats-hash.md) 페이지에 있습니다.

## 일반 셸 권한으로 읽은 것

아래는 모두 루팅하지 않고 부트로더가 잠긴 폰에서 adb 일반 셸로 읽은 출력입니다 (확인 범위: Android 16, One UI 8.5). 줄 수는 읽은 때의 값이라 기기와 시점에 따라 달라집니다.

| 출력 | 크기 | 담긴 것 | 자세히 |
|---|---|---|---|
| `dumpsys usagestats` | 약 7,546줄 | 최근 몇 시간의 이벤트(`ACTIVITY_RESUMED`, `SCREEN_INTERACTIVE`, `KEYGUARD_SHOWN` 등) | [앱 사용 기록](../../../02-artifacts/app-usage/usagestats/index.md) |
| `dumpsys package` | 약 192,000줄 | Database versions(`sdkVersion`, `buildFingerprint` 등), Known Packages 등 | [설치된 앱](../../../02-artifacts/app-usage/packages/index.md) |
| `dumpsys batterystats` | 약 98,027줄 | — | [배터리 사용 기록](../../../02-artifacts/app-usage/batterystats.md) |
| `dumpsys notification` | 약 4,750줄 | — | [알림 기록](../../../02-artifacts/app-usage/notification-history.md) |
| `dumpsys wifi` | 약 10,850줄 | — | [와이파이 설정과 접속 기록](../../../02-artifacts/network/wifi.md) |
| `dumpsys bluetooth_manager` | 약 16,690줄 | — | [블루투스 장치](../../../02-artifacts/network/bluetooth.md) |
| `dumpsys account` | 약 415줄 | 계정 목록과 "Accounts History" 표 | [계정](../../../02-artifacts/system-account/accounts/index.md) |
| `dumpsys user` | 약 789줄 | 사용자별 State, Created, Last logged in, Start time, Unlock time, Last entered foreground 등 | [사용자와 프로필](../../../02-artifacts/system-account/users-profiles.md) |
| settings | global 596개, secure 464개, system 582개 키 | 키 목록 | [설정 값](../../../02-artifacts/system-account/settings.md) |
| `/sdcard` | — | 폴더 목록 | [공용 저장 공간](../../../01-foundations/storage/shared-storage.md) |
| logcat | — | main, system, crash, kernel 버퍼의 크기와, main, system, events, crash, radio 버퍼의 로그 | [logcat](../../../02-artifacts/logs/logcat.md) |

`dumpsys account` 의 "Accounts History" 표에는 AccountId, Action_Type, timestamp, UID, TableName, Key 칸이 있었고, 동작 값으로 `action_account_add`, `action_account_remove`, `action_called_account_add`, `action_called_account_remove`, `action_authenticator_remove`, `action_clear_password` 가 보였습니다 (확인 범위: Android 16, One UI 8.5).

dumpsys 와 logcat 은 지금 메모리에 있는 상태를 보여 주어서 저장된 파일과 범위가 다르고, usagestats 출력이 "Last ## hour events" 처럼 최근 몇 시간만 담는 것이 그 예입니다 (확인 범위: Android 16, One UI 8.5). 같은 일반 셸 권한으로 `/data/data` 나 `/data/system_ce` 같은 보호 경로를 읽을 수 있는지는 확인하지 않았습니다. dumpsys 출력을 읽는 법은 [dumpsys 출력](../../../02-artifacts/logs/dumpsys.md) 페이지에 있습니다.

## 버그 리포트 받기

`adb bugreport` 뒤에 경로를 주면 그 경로에, 주지 않으면 현재 폴더에 버그 리포트를 받습니다 [2]. 기기 안에는 기본으로 `/bugreports` 아래에 `bugreport-<빌드>-YYYY-MM-DD-HH-MM-SS.zip` 과 dumpstate 로그 파일, `dumpstate-stats.txt` 가 생깁니다 [2].

| zip 안의 파일 | 담긴 것 |
|---|---|
| `bugreport-BUILD_ID-DATE.txt` | dumpsys, dumpstate, logcat 을 담은 본 파일 [2] |
| `version.txt` | Android 버전 글자 등 메타데이터 [2] |
| `systrace.txt` | systrace 를 켰을 때만 생김 [2] |
| `FS/` 폴더 | 기기 파일의 복사본. 기기의 `/dirA/dirB/fileC` 가 `FS/dirA/dirB/fileC` 로 들어감 [2] |

버그 리포트가 zip 으로 바뀐 Android 버전은 이번 출처에 없었습니다. 버그 리포트 안의 기록을 해석하는 법은 [버그 리포트](../../../02-artifacts/logs/bugreport.md) 페이지에 있습니다.

## adb backup

Android 12 부터 adb backup 의 기본 동작이 바뀌어서, Android 12(API 31) 이상을 대상으로 하는 앱은 adb backup 을 해도 앱 데이터가 빠지고 매니페스트에 `android:debuggable=true` 를 둔 앱만 들어갑니다 [3]. 현행 AOSP 는 백업 대상 자격이 없는 앱과 멈춘 상태의 앱도 대기열에서 빼는데 [4], 자격 규칙의 자세한 조건은 확인하지 못했습니다.

공유 저장소를 포함하는 옵션을 주면 `com.android.sharedstoragebackup` 패키지를 대기열에 넣어 공유 저장소를 담고, APK 와 OBB 를 넣을지도 옵션으로 정합니다 [4]. 이 옵션은 소스의 변수 이름으로만 봤고, 명령줄에 쓰는 실제 플래그 글자와 adb backup 이 몇 버전부터 사용 중단 표시가 됐는지는 확인하지 못했습니다. 만들어진 파일의 형식은 [결과물 형식과 해시](formats-hash.md) 페이지에 있습니다.

## 함정과 한계

adb 로 읽은 결과는 명령을 실행한 순간의 상태라서 같은 명령을 다시 실행하면 결과가 달라지고, 명령마다 실행 시각을 적어 두지 않으면 나중에 어느 시점의 상태인지 알 수 없습니다. 조사자가 adb 를 켜고 연결하는 일 자체도 설정 값을 바꾸니, 수집 전 상태와 한 조작을 따로 기록합니다. 일반 셸 권한으로 읽을 수 있는 범위는 제조사와 버전에 따라 다를 수 있어서 위 표는 관찰한 한 기기의 결과로만 봅니다. 도구가 기대한 대로 뽑았는지 확인하는 방법은 [도구 검증](../../reporting/tool-validation.md) 페이지에 있습니다.

## 결과를 어떻게 해석하나

dumpsys·logcat 결과는 "그 시각 메모리에 이런 상태가 있었다" 까지 말해 주고, 출력에 없는 이벤트가 기기에서 일어나지 않았다는 뜻은 아닙니다. 보고서에는 아래처럼 씁니다.

> (날짜·시각) 에 adb 일반 셸 권한으로 실행한 `dumpsys user` 출력에 (사용자 번호) 사용자의 State 가 RUNNING_UNLOCKED 로 적혀 있습니다. 이 출력은 명령을 실행한 때의 상태이고, 그 전의 잠금 상태는 이 출력만으로 알 수 없습니다.

## 참고 문헌

1. Android Debug Bridge (adb) — Android Developers, https://developer.android.com/tools/adb
2. Capture and read bug reports — Android Developers, https://developer.android.com/studio/debug/bug-report
3. Behavior changes: apps targeting Android 12 — Android Developers, https://developer.android.com/about/versions/12/behavior-changes-12
4. PerformAdbBackupTask.java — AOSP frameworks/base (GitHub 미러, main), https://raw.githubusercontent.com/aosp-mirror/platform_frameworks_base/main/services/backup/java/com/android/server/backup/fullbackup/PerformAdbBackupTask.java
