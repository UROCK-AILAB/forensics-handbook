---
title: "logcat"
parent: "아티팩트 · 로그"
nav_order: 1200
---

# logcat

logcat (logcat) 은 시스템 프로세스 `logd` 가 메모리에 두는 순환 버퍼에서 앱과 시스템이 남긴 로그 줄을 꺼내 보여 주는 도구이고, 그 출력에는 수집 시점에 가까운 짧은 시간대에 어떤 프로세스가 어떤 태그로 무엇을 적었는지가 시각·PID·TID·수준과 함께 남습니다 [1].

## 무엇을 기록하나 · 왜 생기나

Android 로그는 `logd` 가 관리하는 구조화된 순환 버퍼 여러 개로 이루어져 있습니다 [1]. 앱은 `android.util.Log` 로, 플랫폼 코드는 숨은 API 인 `android.util.Slog` 로, 무선·전화 쪽 코드는 `android.telephony.Rlog` 로, 시스템 진단 이벤트는 `android.util.EventLog` 로 로그를 남깁니다 [2]. 네이티브 코드는 liblog 매크로를 쓰는데, 매크로 이름에 따라 들어가는 버퍼가 갈려서 `ALOGV`·`ALOGW` 는 main, `RLOGD`·`RLOGE` 는 radio, `SLOGI`·`SLOGW` 는 system 버퍼로 갑니다 [2].

개발자가 동작을 확인하거나 문제를 고치려고 남기는 기록이라 줄 내용은 앱마다 제각각이지만, 시각·PID·TID·수준·태그는 줄마다 같은 자리에 찍힙니다. 로그에 이메일·전화번호·이름 같은 개인 정보를 남기지 말라는 권고가 있지만 [2], 모든 앱이 이 권고를 지킨다는 보장은 없습니다. 로그 내용에 개인 정보가 섞여 있을 수 있다고 보고 다룹니다.

로그 접근은 `android.permission.READ_LOGS` 를 포함해 모두 제한되고, 서드파티 앱은 시스템 로그를 읽을 수 없습니다 [2]. 예외는 시스템 UID, 네이티브 프로세스, `DropBoxManager` 같은 특정 API 입니다 [2]. 앱 권한 구조는 [앱 샌드박스와 권한](../../01-foundations/security-model/sandbox-permissions.md) 에서 다룹니다.

## 위치와 버전별 차이

logcat 로그는 파일이 아니라 `logd` 의 메모리 버퍼에 있습니다. `-b` 로 고르는 버퍼는 아래와 같습니다 [1].

| 버퍼 | 담는 내용 | 기본 출력 |
|---|---|---|
| `main` | 앱 로그 대부분. system·crash 메시지는 없음 | 포함 |
| `system` | 시스템 메시지 | 포함 |
| `crash` | 충돌 메시지 | 포함 |
| `radio` | 무선·전화 관련 메시지 | 빠짐 |
| `events` | 해석한 바이너리 시스템 이벤트 | 빠짐 |
| `default` | main + system + crash | — |
| `all` | 모든 버퍼 | — |

events 버퍼는 [이벤트 로그 버퍼 (events)](events-buffer.md) 에서 따로 다룹니다. `-b` 로 고르는 버퍼에는 `kernel` 이 없습니다 [1]. logd 설정 `ro.logd.kernel` 은 klogd 데몬을 켜는 속성입니다 [3].

기기에 따라 버퍼 크기 목록에 `main`, `system`, `crash`, `kernel` 네 줄만 나오고 events·radio 가 빠질 수 있습니다. 목록에 없다고 events·radio 버퍼가 없는 것은 아니어서, 이런 기기에서도 adb 일반 셸 권한으로 main·system·events·crash·radio 다섯 버퍼의 줄을 읽을 수 있습니다.

버퍼 크기와 파일 저장은 logd 설정 속성으로 정합니다 [3].

| 속성 | 뜻 |
|---|---|
| `ro.logd.size` | 기본 크기. 기본값 256KB 이고, 256KB 보다 큰 기본값은 잘 확장되지 않음 |
| `persist.logd.size` | 시작할 때 쓰는 전체 기본 크기 |
| `persist.logd.size.<버퍼>` | 버퍼별 크기 |
| `ro.config.low_ram` | 켜져 있으면 256K 대신 64K |
| `ro.logd.filter` | 먼저 지울 항목. 기본값 `"~! ~1000/!"` |
| `persist.logd.logpersistd` | 값이 `logcatd` 이면 logd 안에서 `logcat -f` 를 실행해 파일로 남김 |
| `logd.logpersistd.size` | 파일로 남길 때 크기(MB) |
| `logd.logpersistd.rotate_kbytes` | 파일 하나의 크기(KB) |
| `ro.logd.auditd` | SELinux 감사 메시지 수집. 기본값 true |
| `ro.logd.auditd.dmesg` | 감사 메시지를 dmesg 로도 보냄. 기본값 true |

파일로 남기는 기능을 켰을 때 저장되는 경로와 삼성 기기의 기본 버퍼 크기는 실제 기기에서 확인합니다.

버전·제조사 차이는 아래와 같습니다.

| 구분 | 내용 |
|---|---|
| AOSP 공통 | 버퍼 종류, 출력 형식, 우선순위 문자 [1]. 옵션은 OS 버전마다 달라서 `adb logcat --help` 로 확인 [1] |
| 삼성 One UI | settings global 에 `activity_starts_logging_enabled`, `autofill_logging_level`, settings system 에 `samsung_errorlog_agree`, `show_message_logs` 키가 있음. 각 키의 뜻은 공개 자료 없음 |

삼성 전용 로그 수집 경로와 파일 위치는 실제 기기에서 확인합니다. 설정 키를 읽는 방법은 [설정 값 (Settings Global·Secure·System)](../system-account/settings.md) 에서 다룹니다.

## 구조

기본 출력 형식은 `threadtime` 이고, 날짜·호출 시각·우선순위·태그·PID·TID 를 적습니다 [1]. 출력은 버퍼마다 시작 줄이 한 번 나오고 그 아래로 로그 줄이 이어집니다.

```
--------- beginning of main
##-## ##:##:##.### <PID> <TID> I <태그>: <내용>
--------- beginning of system
##-## ##:##:##.### <PID> <TID> D <태그>: <내용>
--------- beginning of crash
##-## ##:##:##.### <PID> <TID> F <태그>: <내용>
```

맨 앞 필드는 월-일 시:분:초.밀리초이고 연도가 없습니다.

수준 필드의 우선순위 문자는 낮은 것부터 아래 순서입니다 [1].

| 문자 | 뜻 |
|---|---|
| V | Verbose |
| D | Debug |
| I | Info |
| W | Warning |
| E | Error |
| F | Fatal |
| S | Silent. 아무것도 찍지 않음 |

`-v` 로 고르는 출력 형식은 `brief`, `long`, `process`, `raw`, `tag`, `thread`, `threadtime`, `time` 이 있고 [1], 여기에 아래 수식어를 붙일 수 있습니다 [1].

| 수식어 | 뜻 |
|---|---|
| `color` | 수준별 색 |
| `descriptive` | events 버퍼 항목에 설명을 붙임 |
| `epoch` | 1970-01-01 부터 흐른 초 |
| `monotonic` | 마지막 부팅부터 흐른 CPU 초 |
| `printable` | 출력할 수 있는 문자로 바꿈 |
| `uid` | 권한이 허락하면 UID 표시 |
| `usec` | 마이크로초까지 표시 |
| `UTC` | UTC 로 표시 |
| `year` | 연도를 붙임 |
| `zone` | 시간대를 붙임 |

## 증거로서 의미

**증명하는 것**

로그 줄 하나는 그 시각에 그 PID·TID 의 프로세스가 그 태그와 수준으로 그 내용을 적었다는 기록입니다. crash 버퍼의 F 줄은 그 시각에 치명적 오류 메시지가 남았다는 기록이고, `uid` 수식어로 UID 가 나오면 [패키지 이름과 UID](../../01-foundations/value-decoding/package-uid.md) 에 맞춰 어느 앱의 프로세스였는지 좁힐 수 있습니다.

**증명하지 못하는 것**

로그 줄은 코드가 그 줄을 찍었다는 뜻일 뿐 사람이 그 동작을 했다는 뜻이 아닙니다. 태그와 내용은 개발자가 마음대로 정해서, 같은 문구가 앱이나 버전마다 다른 뜻일 수 있습니다. 로그가 없다는 사실도 일이 없었다는 근거가 되지 못하는데, 순환 버퍼에서 밀려났거나 그 수준의 로그를 찍지 않도록 설정돼 있었을 수 있습니다. 보고서에는 "이 시각에 이 PID 의 프로세스가 이 태그로 이런 메시지를 남긴 기록이 있다" 처럼 기록으로 확인되는 만큼만 씁니다.

## 시각 해석

기본 `threadtime` 형식은 연도와 시간대를 붙이지 않습니다 [1]. 기본 출력이 기기 현지 시각인지 밝힌 공식 문서가 없으니, 수집할 때 `year`·`zone` 수식어를 붙이거나 `UTC`·`epoch` 수식어로 한 번 더 받아 두어 기준을 분명히 합니다. `monotonic` 은 마지막 부팅부터 흐른 CPU 시간이라 [1] 실제 시각(wall clock)이 아니고, 재부팅 앞뒤의 값을 서로 비교하지 않습니다.

연도는 수집 날짜와 로그가 이어진 기간으로 판단합니다. 시각 값 전반은 [시각 값](../../01-foundations/value-decoding/time-values.md), 기기 시간대 설정은 [시간대와 시각 설정 (Time Zone)](../system-account/time-zone.md) 에서 다룹니다.

## 함정과 한계

첫째, 버퍼는 메모리 순환 버퍼라서 오래된 항목은 새 항목에 밀려 사라집니다 [1]. 기본 크기가 256KB 로 작고 [3], `ro.logd.filter` 기본값은 가장 말 많은 UID 의 오래된 항목과 system 에서 가장 말 많은 PID 의 항목을 먼저 지웁니다 [3]. 로그를 많이 찍는 앱 하나 때문에 다른 앱의 기록이 먼저 사라질 수 있습니다.

둘째, 재부팅 뒤에도 버퍼 내용이 남는지는 공식 문서에 나와 있지 않습니다. 메모리 버퍼라는 점을 생각해 기기를 끄거나 다시 켜기 전에 먼저 받는 편이 안전하고, 받은 시각을 수집 기록에 적어 둡니다.

셋째, 태그별 로그 수준은 `setprop log.tag.<TAG>` 로 바꿀 수 있고, `persist.log.tag.<TAG>` 는 재부팅 뒤에도 남습니다 [2]. 분석 대상 기기에 `persist.log.tag.` 로 시작하는 속성이 있으면 누군가 로그 수준을 바꾼 흔적일 수 있다고 보고(추론), 그 태그의 로그가 적거나 없는 이유를 따로 따져 봅니다. `persist.logd.size` 계열 값이 기본보다 작게 잡혀 있을 때도 로그가 짧게 남는 이유가 될 수 있습니다(추론). 이런 흔적은 [증거를 없애려 했나 (Anti-Forensics)](../../04-scenarios/activity/anti-forensics/index.md) 에서 다른 기록과 함께 봅니다.

넷째, logcat 옵션은 OS 버전마다 다릅니다 [1]. 다른 기기에서 쓰던 명령을 그대로 쓰지 말고 `adb logcat --help` 로 먼저 확인합니다.

## 직접 분석해 보기

### 텍스트로 한 번

logd 버퍼의 바이너리 형식은 공개 문서가 없어서 헥스 따라가기 대신 텍스트 출력을 직접 읽습니다.

1. `adb logcat --help` 로 그 기기에서 쓸 수 있는 옵션을 확인합니다. 특히 버퍼를 한 번 쏟아 내고 끝내는 `-d` 가 있는지 봅니다. `-d` 없이 부르면 명령이 끝나지 않고 새 줄을 계속 받습니다.
2. `adb logcat -d -b all -v threadtime` 출력을 파일로 받고, 같은 방식으로 `year`·`zone` 수식어를 붙인 출력도 받아 둡니다.
3. `--------- beginning of` 줄로 버퍼 경계를 나누고, 버퍼마다 가장 이른 줄의 시각을 적어 둡니다. 이 시각보다 앞선 일은 이 출력으로 판단할 수 없습니다.
4. 조사할 시간대의 줄에서 PID 를 모으고, 같은 PID 가 찍은 태그와 수준을 묶어 봅니다.

### 공개 도구로 한 번

logcat 자체가 공개 도구입니다. `-b crash` 로 충돌 버퍼만 받고, `-v uid` 로 UID 를 함께 받아 앞에서 모은 PID 와 맞춰 봅니다. `-v uid` 는 권한이 허락할 때만 UID 를 보여 주니 [1], UID 가 비어 있으면 권한 때문일 수 있다고 적어 둡니다.

## 교차 검증

| 함께 볼 기록 | 맞춰 볼 것 |
|---|---|
| [이벤트 로그 버퍼 (events)](events-buffer.md) | 같은 PID 의 프로세스 시작·종료 시각 |
| [버그 리포트 (bugreport)](bugreport.md) | 버그 리포트 안의 logcat 과 직접 받은 logcat 의 겹치는 구간 |
| [앱 오류·종료 기록 (DropBox·tombstones·ANR)](../app-usage/crash-records.md) | crash 버퍼의 F 줄과 같은 시각의 충돌 기록 |
| [앱 사용 기록 (usagestats)](../app-usage/usagestats/index.md) | 로그를 남긴 앱이 그 시각에 전경에 있었는지 |
| [설정 값 (Settings Global·Secure·System)](../system-account/settings.md) | 로그 관련 설정 키 |

여러 기록의 시각을 한 줄로 늘어놓는 방법은 [타임라인 작성 (Timeline)](../../03-techniques/analysis/timeline/index.md) 에서 다룹니다.

## 실습

공개 안드로이드 시험 이미지(NIST CFReDS 등)에 logcat 출력이나 버그 리포트가 들어 있으면 아래 질문을 풀어 봅니다.

1. 버퍼마다 가장 이른 줄의 시각은 언제이고, 버퍼마다 남은 기간은 얼마나 차이가 납니까?
2. 가장 많은 줄을 남긴 태그나 PID 는 무엇이고, 그 때문에 다른 기록이 밀려났을 가능성이 있습니까?
3. crash 버퍼에 F 줄이 있다면 같은 시각의 events 버퍼에 어떤 프로세스 종료 기록이 있습니까?

## 참고 문헌

1. Android Developers — Logcat command-line tool — https://developer.android.com/tools/logcat
2. Android Open Source Project — Understanding logging — https://source.android.com/docs/core/tests/debug/understanding-logging
3. AOSP system/logging — logd README.property (main) — https://android.googlesource.com/platform/system/logging/+/refs/heads/main/logd/README.property
