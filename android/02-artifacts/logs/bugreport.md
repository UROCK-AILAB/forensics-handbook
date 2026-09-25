---
title: "버그 리포트"
parent: "아티팩트 · 로그"
nav_order: 1220
---

# 버그 리포트 (bugreport)

## 한 줄 요약

버그 리포트 (bugreport) 는 만드는 순간의 dumpsys·dumpstate·logcat 출력과 기기 파일 일부를 ZIP 하나로 묶은 진단 묶음이라, 수집 시점의 시스템 상태와 메모리에 남아 있던 로그를 한꺼번에 받아 둘 수 있습니다 [1][2]. 기기에 남은 ZIP 은 누군가 버그 리포트를 만들었다는 흔적이 됩니다 [1].

## 무엇을 기록하나 · 왜 생기나

버그 리포트는 개발자가 문제를 찾으려고 만드는 묶음이라 진단 출력, 오류 로그, 시스템 메시지 로그, 모든 앱의 스택 추적(stack trace)이 들어갑니다 [1]. 본문에는 dumpsys, dumpstate, logcat 출력이 함께 들어 있습니다 [1].

AOSP 문서는 버그 리포트 안의 로그를 세 가지로 나눕니다 [2]. logcat 은 문자열 로그이고 줄마다 시각·UID·PID·수준이 붙습니다. 이벤트 로그는 바이너리 형식의 시스템 이벤트이고, VM traces 는 ANR 이나 충돌이 났을 때의 스택입니다. logcat 과 이벤트 로그 각각은 [logcat (logcat)](logcat.md) 과 [이벤트 로그 버퍼 (events)](events-buffer.md) 에서, dumpsys 출력은 [dumpsys 출력 (dumpsys)](dumpsys.md) 에서 다룹니다.

버그 리포트가 생기는 경로는 두 가지입니다. 기기의 개발자 옵션에서 "Take bug report" 를 누르고 종류를 고르면 만들어지고, 다 되면 알림이 뜹니다 [1]. PC 에서는 `adb bugreport` 뒤에 PC 쪽 저장 경로를 붙여 받고, 경로를 붙이지 않으면 현재 폴더에 저장합니다 [1].

## 위치와 버전별 차이

기기 안에서 만든 버그 리포트는 `/bugreports` 에서 찾을 수 있고, 개발자 문서는 아래처럼 목록을 보고 가져오라고 안내합니다 [1].

```
adb shell ls /bugreports/
adb pull /bugreports/bugreport-....zip
```

`/bugreports` 가 실제 저장 폴더와 어떤 관계인지는 확인하지 못했습니다. 파일 이름은 `bugreport-BUILD_ID-DATE.zip` 형식이고, 문서의 예시는 `bugreport-foo-bar.xxx.YYYY-MM-DD-HH-MM-SS.zip` 입니다 [1]. 문서는 DATE 가 어느 시점의 시각인지 따로 적지 않았지만, 만든 시각으로 보입니다(추론). 같은 폴더에는 ZIP 말고도 `bugreport-...-dumpstate_log-....txt` 와 `dumpstate-stats.txt` 가 함께 보일 수 있습니다 [1].

관찰 기기에서는 버그 리포트와 관련된 이름이 아래처럼 보였고, 각 값의 뜻은 확인하지 못했습니다 (확인 범위: SM-S937N, Android 16, One UI 8.5).

| 보인 곳 | 이름 |
|---|---|
| settings secure 키 | `bugreport_in_power_menu` |
| settings secure 키 | `dropbox:data_app_anr`, `dropbox:data_app_crash`, `dropbox:data_app_wtf` |
| `dumpsys wifi` 출력 | `mIsMultiplePrimaryBugreportTaken: false` |

`DropBoxManager` 는 앱이 시스템 로그에 접근하지 못하는 규칙의 예외로 언급되는 API 이고 [4], DropBox 에 쌓이는 충돌·ANR 기록은 [앱 오류·종료 기록 (DropBox·tombstones·ANR)](../app-usage/crash-records.md) 에서 다룹니다. 삼성 기기의 버그 리포트가 AOSP 형식과 어떻게 다른지는 확인하지 못했습니다.

## 구조

ZIP 안에는 아래 파일과 폴더가 들어 있습니다 [1].

| 항목 | 내용 |
|---|---|
| `bugreport-BUILD_ID-DATE.txt` | 본문. dumpsys, dumpstate, logcat 출력 |
| `version.txt` | Android 릴리스 정보 |
| `systrace.txt` | systrace 를 켰을 때만 생김 |
| `FS/` | 기기 파일의 복사본. 원래 경로를 그대로 따름 |

`FS/` 는 기기의 `/dirA/dirB/fileC` 를 `FS/dirA/dirB/fileC` 로 담습니다 [1]. 폴더 경로가 기기 경로와 같아서, 이 안의 파일이 기기 어디에서 왔는지는 경로로 바로 알 수 있습니다.

본문은 여러 절로 나뉘고, ANR 을 볼 때는 "VM TRACES AT LAST ANR" 절에서 앱이 멈춘 순간의 메인 스레드 상태를 봅니다 [2]. 그 밖의 절을 나누는 구분 문자열은 확인하지 못해서 여기에 적지 않습니다.

> 그림 자리: 버그 리포트 ZIP 안의 본문·version.txt·FS/ 가 각각 기기의 어떤 기록에서 오는지 잇는 그림

## 증거로서 의미

**증명하는 것**

본문의 dumpsys 출력은 버그 리포트를 만든 순간 각 시스템 서비스가 내놓은 상태이고, 본문의 logcat 은 그 순간 메모리 버퍼에 남아 있던 로그입니다. 수집 도구로 버그 리포트를 받으면 이 둘을 한 시점에 묶어 둘 수 있어서, 서비스별로 따로 받을 때보다 시점이 어긋날 여지가 적습니다(추론). 검체의 `/bugreports` 에 ZIP 이 있다면 버그 리포트를 만든 적이 있다는 기록이고 [1], 파일 이름의 날짜·시각이 만든 때를 가리킨다고 보입니다(추론). 파일 이름은 나중에 바꿀 수 있으니 본문 안의 시각과 맞춰 봅니다.

**증명하지 못하는 것**

버그 리포트 안의 logcat 은 만든 시점의 메모리 버퍼 내용이라, 그보다 오래된 항목은 이미 밀려나 없을 수 있습니다(순환 버퍼 [3] 에서 나온 추론). 버그 리포트 안에 어떤 로그가 없다는 사실로 그 일이 없었다고 판단하지 않습니다. 기기에 남은 ZIP 도 누가 만들었는지, 개발자 옵션에서 만들었는지 adb 로 만들었는지는 이름만으로 알 수 없습니다. 보고서에는 "이 시각에 만든 버그 리포트에 이런 기록이 들어 있다" 처럼 씁니다.

## 시각 해석

ZIP 이름의 날짜·시각은 만든 시각으로 보이지만(추론), 어느 시간대 기준인지는 확인하지 못했습니다. 본문 안의 logcat 줄은 연도 없이 찍힐 수 있으니 [3], 연도는 ZIP 이름의 날짜를 기준으로 판단합니다. `version.txt` 에는 Android 릴리스 정보만 있어서 [1] 연도를 정하는 근거로 쓰지 않습니다. 본문의 여러 절은 각 서비스가 제 방식으로 시각을 찍으니, 절마다 시간대와 형식을 따로 확인합니다. 시각 값 전반은 [시각 값](../../01-foundations/value-decoding/time-values.md) 에서 다룹니다.

## 함정과 한계

첫째, 버그 리포트를 만들면 `/bugreports` 에 새 ZIP 이 생깁니다 [1]. 수집하려고 만든 버그 리포트도 기기에 흔적을 남기니, 만든 시각과 방법을 수집 기록에 적어 두어 검체에 원래 있던 ZIP 과 구별합니다. 그 밖에 알림 기록 같은 다른 흔적이 남는지는 확인하지 못했습니다. 수집 절차 전반은 [모바일 증거 확보 (Acquisition)](../../03-techniques/acquisition/mobile-acquisition/index.md) 에서 다룹니다.

둘째, 재부팅 흔적을 볼 때 런타임 재시작과 진짜 재부팅을 구분해야 합니다 [2]. 런타임 재시작은 `system_server` 가 죽었다가 다시 뜬 것이고, 진짜 재부팅은 커널 충돌 같은 이유로 기기 전체가 다시 시작한 것입니다 [2]. 둘을 섞으면 "기기를 껐다 켰다" 는 잘못된 문장이 나옵니다.

셋째, "VM TRACES AT LAST ANR" 절은 이름대로 마지막 ANR 을 담는다고 보이니(추론), 여러 번의 ANR 을 이 절 하나로 설명하지 않습니다. 시각과 PID 를 맞춰 events 의 `am_anr` 과 짝지어야 어느 앱의 어느 ANR 인지 확정할 수 있습니다 [2].

넷째, 본문에는 모든 앱의 스택 추적과 서비스 상태가 들어 있어서 [1] 조사와 무관한 개인 정보가 많이 섞입니다. 공유하거나 보고서에 붙일 때는 필요한 부분만 뽑습니다.

## 직접 분석해 보기

### 텍스트로 한 번

ZIP 파일 형식 자체는 이 페이지에서 다루지 않고, 풀어낸 본문을 텍스트로 따라갑니다.

1. ZIP 을 풀기 전에 해시를 기록하고, 사본에서 작업합니다.
2. 파일 목록에서 본문 `.txt`, `version.txt`, `systrace.txt`, `FS/` 가 있는지 확인하고 `version.txt` 로 Android 릴리스를 적어 둡니다.
3. `FS/` 아래 경로를 기기 경로로 바꿔 적고, 다른 아티팩트 페이지에서 찾는 파일이 들어 있는지 봅니다.
4. 본문에서 "VM TRACES AT LAST ANR" 을 찾아 멈춘 앱과 PID 를 적고, 본문 안의 events 로그에서 같은 PID 의 `am_anr` 을 찾습니다.
5. 본문의 logcat 에서 버퍼마다 가장 이른 줄의 시각을 적어 로그가 덮는 기간을 확인합니다.

### 공개 도구로 한 번

`adb bugreport` 자체가 공개 도구입니다 [1]. 수집할 때 `adb bugreport` 로 받은 ZIP 과, 같은 시각 가까이에 `adb logcat`·`adb shell dumpsys` 로 따로 받은 출력을 몇 곳 맞춰 보면, 버그 리포트 안의 절이 어느 명령의 출력과 같은지 확인할 수 있습니다.

## 교차 검증

| 함께 볼 기록 | 맞춰 볼 것 |
|---|---|
| [logcat (logcat)](logcat.md) | 본문 logcat 과 따로 받은 logcat 의 겹치는 구간 |
| [이벤트 로그 버퍼 (events)](events-buffer.md) | ANR 절의 PID 와 `am_anr` |
| [dumpsys 출력 (dumpsys)](dumpsys.md) | 본문의 서비스 출력과 따로 받은 dumpsys |
| [앱 오류·종료 기록 (DropBox·tombstones·ANR)](../app-usage/crash-records.md) | 같은 시각의 충돌·ANR 파일 |
| [배터리 사용 기록 (batterystats)](../app-usage/batterystats.md) | 본문의 batterystats 출력 |
| [기기 정보와 빌드 (build.prop·Build)](../system-account/device-build.md) | `version.txt` 와 기기 빌드 정보 |

## 실습

공개 안드로이드 검체(NIST CFReDS 등)에 버그 리포트 ZIP 이 들어 있으면 아래 질문을 풀어 봅니다.

1. ZIP 이름의 날짜·시각과 `version.txt` 의 릴리스는 무엇입니까?
2. `FS/` 아래에 어떤 기기 경로의 파일이 들어 있습니까?
3. "VM TRACES AT LAST ANR" 절의 앱은 무엇이고, 같은 PID 의 `am_anr` 은 언제입니까?
4. 본문 logcat 의 가장 이른 줄은 ZIP 을 만든 시각보다 얼마나 앞섭니까?

## 참고 문헌

1. Android Developers — Capture and read bug reports — https://developer.android.com/studio/debug/bug-report
2. Android Open Source Project — Read bug reports — https://source.android.com/docs/core/tests/debug/read-bug-reports
3. Android Developers — Logcat command-line tool — https://developer.android.com/tools/logcat
4. Android Open Source Project — Understanding logging — https://source.android.com/docs/core/tests/debug/understanding-logging
