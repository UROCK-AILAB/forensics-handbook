---
title: "앱 오류·종료 기록"
parent: "아티팩트 · 앱 설치·사용 흔적"
nav_order: 530
---

# 앱 오류·종료 기록 (DropBox·tombstones·ANR)

앱이 죽거나 멈추면 시스템은 DropBox 에 오류 기록을, 네이티브 코드가 죽으면 tombstones 에 충돌 기록을, 앱이 응답하지 않으면 ANR 기록을 남기고, 이 기록들은 그 시각에 그 앱이 실제로 돌고 있었다는 흔적이 됩니다 [1][2][3].

## 무엇을 기록하나 · 왜 생기나

이 기록들은 개발자와 제조사가 오류를 고치려고 남기는 진단용 기록이지만, 포렌식에서는 "그 시각에 그 앱의 프로세스가 실행 중이었다" 는 흔적으로 씁니다. 사용자가 앱을 지운 뒤에도 오류 기록에 앱 이름이 남아 있을 수 있어서, [악성 앱 흔적 분석](../../03-techniques/analysis/malicious-app-triage/index.md) 에서도 찾아볼 곳입니다.

세 기록은 생기는 조건이 다릅니다. DropBox 는 시스템 서비스(DropBoxManagerService)가 태그를 붙여 여러 종류의 진단 기록을 모으는 저장소입니다 [1]. tombstone 은 네이티브(C/C++) 코드가 충돌했을 때 남는 파일이고, 같은 충돌 정보가 logcat 의 crash 버퍼와 DropBox 에도 들어갑니다 [2]. ANR(Application Not Responding) 은 앱이 정해진 시간 안에 응답하지 않을 때 생기고, 그 경우는 아래와 같습니다 [3].

| 경우 | 조건 |
|---|---|
| 입력 | 입력 이벤트에 5초 안에 응답하지 않음 |
| 서비스 | `onCreate`, `onStartCommand`, `onBind` 가 몇 초 안에 끝나지 않음 |
| 전경 서비스 | `startForegroundService` 뒤 5초 안에 `startForeground` 를 부르지 않음 |
| 브로드캐스트 | 앞에 보이는 앱의 BroadcastReceiver 가 5초 안에 끝나지 않음 |
| 작업 | JobService 가 몇 초 안에 반환하지 않음 |

작업(JobScheduler) ANR 은 기기 버전이 아니라 앱이 대상으로 삼는 버전(target SDK)에 따라 다르게 처리되는데, Android 14 이상을 대상으로 하는 앱에는 명시적으로 알리고 13 이하를 대상으로 하는 앱에는 알리지 않고 조용히 처리합니다 [3].

## 위치와 버전별 차이

| 기록 | 위치 | 보관 |
|---|---|---|
| DropBox | `/data/system/dropbox` [1] | 3일, 최대 1000개(저사양 램 기기 300개), 용량 한도 있음 [1] |
| tombstones | `/data/tombstones/` [2] | 개수 한도가 있어 새 충돌이 나면 오래된 파일을 지움 [2] |
| ANR (예전) | `/data/anr/traces.txt` 한 파일 [3] | 공개 자료 없음 |
| ANR (새 버전) | `/data/anr/anr_*` 여러 파일 [3] | 공개 자료 없음 |
| logcat crash 버퍼 | 메모리 버퍼 | 버퍼 크기만큼 |

DropBox 의 기본 보존 상수는 `DEFAULT_AGE_SECONDS = 3 * 86400`, `DEFAULT_MAX_FILES = 1000` 이고, 용량 한도 `DEFAULT_QUOTA_KB` 는 userdebug 빌드에서 `20 * 1024`, 그 밖에서는 `10 * 1024` 입니다 [1]. tombstone 보관 개수, `.pb` 형식이 들어온 버전, ANR 기록이 한 파일에서 여러 파일로 바뀐 버전은 공개 문서에 나와 있지 않습니다 [3].

세 디렉터리 모두 시스템 영역이라 adb 일반 권한으로 바로 읽기 어렵고, `/data/anr` 를 adb 로 직접 읽을 때도 `adb root` 를 씁니다 [3]. 일반 기기에서는 `adb bugreport` 나 개발자 옵션의 "버그 신고" 로 받습니다 [3]. 버그 리포트 짜임새는 [버그 리포트 (bugreport)](../logs/bugreport.md) 페이지에서 다룹니다. adb 일반 권한으로 `dumpsys dropbox` 를 읽을 수 있는지는 기기에서 확인합니다.

삼성 기기에서 오류 로그를 따로 모으는 위치가 더 있는지는 공개 문서에 나와 있지 않습니다. 삼성 기기에서 보이는 관련 설정 키는 아래와 같습니다.

| 설정 영역 | 키 이름 |
|---|---|
| secure | `dropbox:data_app_anr`, `dropbox:data_app_crash`, `dropbox:data_app_wtf` |
| secure | `anr_show_background` |

AOSP 는 DropBox 태그를 켜고 끄는 값을 Global 설정의 `dropbox:<태그>` 키에서 `enabled`·`disabled` 로 읽습니다 [1]. 그런데 삼성 기기에서는 같은 이름의 키가 secure 목록에 있으니 두 영역을 모두 봅니다. 설정 값 읽는 법은 [설정 값](../system-account/settings.md) 페이지에 있습니다.

## 구조

### DropBox 파일 이름

DropBox 의 파일 하나는 항목 하나이고, 이름은 `태그@시각` 에 확장자를 붙인 모양입니다 [1]. 태그는 URI 인코딩하고 시각은 밀리초입니다 [1].

| 확장자 | 뜻 |
|---|---|
| `.txt` | 텍스트 항목 |
| `.dat` | 바이너리 항목 |
| `.gz` 추가 | 압축한 항목 (예: `.txt.gz`) |
| `.lost` | 내용이 지워지고 이름만 남은 항목 |

`.lost` 파일은 내용 없이 "이 태그의 항목이 이 시각에 있었다" 는 사실만 남깁니다 [1]. 태그 이름의 전체 목록과 뜻은 공개 문서에 정리돼 있지 않고, 설정 키에는 `data_app_anr`, `data_app_crash`, `data_app_wtf` 같은 태그가 보입니다.

### tombstone 내용

tombstone 은 `tombstone_06` 처럼 번호 붙은 파일이고, 사람이 읽는 텍스트와 프로토콜 버퍼(`.pb`) 두 형식이 있습니다 [2]. 텍스트 판에는 아래 내용이 들어갑니다 [2].

| 부분 | 내용 |
|---|---|
| 빌드 | `Build fingerprint:` 줄, 하드웨어, ABI |
| 프로세스 | pid, tid, 스레드 이름, 프로세스 이름 |
| 원인 | 시그널 종류와 코드, 오류 주소, abort 메시지(있을 때) |
| 상태 | 레지스터, 스택 백트레이스 |

빌드 지문은 [기기 정보와 빌드](../system-account/device-build.md) 페이지의 값과 맞춰 볼 수 있습니다.

### logcat crash 버퍼

logcat 에는 `main`, `system`, `crash`, `kernel` 버퍼가 있고, crash 버퍼 한 줄은 아래 모양입니다.

```
[crash] ##-## ##:##:##.### <PID> <TID> F <태그>: <내용>
```

logcat 형식 전반은 [logcat (logcat)](../logs/logcat.md) 페이지에서 다룹니다.

## 증거로서 의미

**증명하는 것**

오류 기록에 앱 이름이나 프로세스 이름이 있으면 그 시각에 그 앱의 프로세스가 돌고 있었다는 기록입니다. 이미 지운 앱이 오류 기록에 남아 있으면 그 앱이 한때 기기에서 실행됐다는 근거가 되고, tombstone 의 빌드 지문은 충돌 당시 기기 소프트웨어 판을 알려 줍니다. ANR 기록은 앱이 정해진 시간 안에 응답하지 않은 순간이 있었다는 뜻입니다.

**증명하지 못하는 것**

프로세스가 돌았다는 기록은 사용자가 그 앱을 열었다는 뜻이 아닙니다. 서비스나 작업만으로도 프로세스가 뜨고, 그러다 죽어도 같은 기록이 남습니다. 오류가 사용자 조작 때문인지, 앱 결함 때문인지, 누군가 일부러 일으켰는지도 이 기록만으로는 구분하지 못합니다. 보고서에는 "이 시각에 이 프로세스 이름으로 충돌 기록이 있다" 처럼 기록으로 확인되는 만큼만 씁니다.

## 시각 해석

DropBox 파일 이름의 시각은 항목을 만들 때 `System.currentTimeMillis()` 로 얻은 값이라 [1] 유닉스 에포크 밀리초(UTC 기준)이고, 실제 시각 시계(wall clock) 값이라서 기기 시계를 바꾸면 그 뒤 파일 이름 시각도 따라 바뀝니다. logcat crash 버퍼 줄의 시각은 연도가 없는 월-일 시각이라, 연도는 수집 날짜로 채우고 연말·연초에 걸친 기록은 특히 조심합니다. tombstone 과 ANR 파일 안 시각의 형식은 실제 기기에서 확인합니다. 시각 값 전반은 [시각 값](../../01-foundations/value-decoding/time-values.md) 페이지에 있습니다.

## 함정과 한계

첫째, DropBox 는 기본 3일만 보관합니다 [1]. 사건과 수집 사이가 길면 사건 시각의 항목은 이미 지워졌을 가능성이 크고, 남은 기록이 없다고 충돌이 없었다고 말할 수 없습니다.

둘째, tombstone 은 개수 한도가 있어서 [2] 충돌이 잦은 기기에서는 오래된 파일이 빨리 밀려납니다. 파일 번호가 시간 순서라고 단정하지 말고 파일 안 내용과 파일 시스템 시각을 함께 봅니다.

셋째, 태그별 기록은 설정으로 끌 수 있습니다 [1]. 특정 태그의 기록만 비어 있으면 설정 키 `dropbox:<태그>` 값을 확인합니다. 이 값이 `disabled` 로 바뀐 흔적은 [증거를 없애려 했나 (Anti-Forensics)](../../04-scenarios/activity/anti-forensics/index.md) 관점에서 살펴볼 만합니다.

넷째, logcat crash 버퍼는 파일이 아니라 logcat 버퍼라서 버퍼 크기를 넘으면 앞쪽 줄이 밀려납니다. 라이브 기기라면 다른 수집보다 먼저 남기고, 버퍼가 언제까지 남는지는 [logcat (logcat)](../logs/logcat.md) 페이지를 참고합니다.

## 직접 분석해 보기

### 파일 이름과 텍스트로 한 번

DropBox 와 tombstone 은 대부분 텍스트라서 헥스보다 파일 이름과 본문을 차례로 읽는 편이 빠릅니다.

1. 버그 리포트나 수집 사본에서 `dropbox` 폴더의 파일 목록을 뽑고, 이름을 `@` 앞의 태그와 뒤의 시각으로 나눕니다. 태그는 URI 디코딩합니다.
2. `.gz` 는 풀고, `.lost` 는 내용이 없으니 이름만 기록합니다.
3. 조사 대상 앱 이름으로 본문을 검색해 어떤 태그에 몇 번 나오는지 셉니다.
4. `tombstones` 폴더의 텍스트 판에서 `Build fingerprint:` 줄과 프로세스 이름 줄을 찾고, 대상 앱이 있으면 시그널과 백트레이스를 옮겨 적습니다.
5. `.gz` 파일은 앞 두 바이트가 gzip 서명 `1F 8B` 인지 헥스로 확인하면 확장자와 내용이 맞는지 알 수 있습니다.

### 공개 도구로 한 번

라이브 기기에서는 `dumpsys dropbox` 가 목록을 보여 주고, `-p`(`--print`) 로 전체 내용을, `-f`(`--file`) 로 파일 경로를 볼 수 있으며, `--proto` 출력과 시각 필터 옵션도 있습니다 [1]. 버그 리포트에 들어 있는 DropBox·ANR·tombstone 내용을 손으로 읽은 결과와 맞춰 봅니다.

## 교차 검증

| 함께 볼 기록 | 맞춰 볼 것 |
|---|---|
| [설치된 앱 (packages.xml)](packages/index.md) | 오류 기록의 앱이 지금 설치돼 있는지, 지워졌다면 언제인지 |
| [앱 사용 기록 (usagestats)](usagestats/index.md) | 충돌 시각 직전에 그 앱이 전경에 있었는지 |
| [배터리 사용 기록 (batterystats)](batterystats.md) | 같은 시각에 그 앱의 작업이 돌고 있었는지 |
| [logcat (logcat)](../logs/logcat.md) | crash 버퍼와 main·system 버퍼의 앞뒤 줄 |
| [이벤트 로그 버퍼 (events)](../logs/events-buffer.md) | 같은 시각의 시스템 이벤트 |

침해 사고 흐름은 [악성 앱은 어디서 들어왔나 (Initial Access)](../../04-scenarios/incident/initial-access.md) 에서 다룹니다.

## 실습

공개 안드로이드 시험 데이터(NIST CFReDS 등)에 버그 리포트나 `/data/system/dropbox`, `/data/tombstones/` 가 들어 있으면 아래 질문을 풀어 봅니다.

1. DropBox 파일을 태그별로 세면 어떤 태그가 가장 많고, 가장 이른 파일과 가장 늦은 파일의 시각 차이는 며칠입니까?
2. `.lost` 파일이 있습니까? 있다면 어떤 태그입니까?
3. tombstone 의 `Build fingerprint:` 가 기기 빌드 정보와 같습니까?
4. 오류 기록에만 나오고 설치 앱 목록에는 없는 앱이 있습니까?

## 참고 문헌

1. AOSP frameworks/base — DropBoxManagerService.java — https://raw.githubusercontent.com/aosp-mirror/platform_frameworks_base/main/services/core/java/com/android/server/DropBoxManagerService.java
2. Android Open Source Project — Diagnose native crashes — https://source.android.com/docs/core/tests/debug/native-crash
3. Android Developers — ANRs — https://developer.android.com/topic/performance/vitals/anr
