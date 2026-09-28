---
title: "삼성 전원·재부팅·초기화 로그"
parent: "아티팩트 · 삼성 기기 전용"
nav_order: 1180
---

# 삼성 전원·재부팅·초기화 로그

삼성 기기는 전원을 끄거나 다시 켤 때마다 시각과 사유를 `/data/log/power_off_reset_reason.txt` 에 적고, 복구 모드 (Recovery) 에 들어갈 때마다 그 요청 내용을 `/efs/recovery/history` 에 쌓습니다. `history` 에는 공장 초기화를 한 뒤에도 그 전의 초기화 기록이 여러 건 남습니다. 삼성 기기가 아니어도 Android 프레임워크는 종료 요청이 어디서 왔는지를 `/data/system/shutdown-checkpoints/` 에 남깁니다.

## 무엇을 기록하나 · 왜 생기나

전원 관련 기록은 "언제 꺼졌나" 뿐 아니라 "왜 꺼졌나" 를 알려 준다는 점에서 쓸모가 있습니다. 디지털 웰빙 같은 앱 사용 기록에도 켜고 끈 시각은 남지만, 배터리가 다 닳아서 꺼졌는지, 사람이 전원 메뉴로 껐는지, 업데이트 때문에 다시 켜졌는지는 나오지 않습니다[7]. 이 페이지의 파일들은 그 사유를 문자열로 적어 둡니다.

| 파일 | 만드는 쪽 | 담긴 내용 |
|---|---|---|
| `/data/log/power_off_reset_reason.txt` | 삼성 | 끄기(SHUTDOWN)·다시 시작(REBOOT)·켜기(ON) 사건과 사유[7][8] |
| `/data/log/power_off_reset_reason_backup.txt` | 삼성 | 위 파일보다 앞선 기간의 같은 기록[7][8] |
| `/efs/recovery/history` | 삼성 | 복구 모드 진입 기록. 공장 초기화, 펌웨어 업데이트(FOTA) 요청이 여기 남습니다[3][6] |
| `/data/log/recovery_history.log` | 삼성 | ALEAPP 가 `history` 와 같은 규칙으로 읽는 복구 기록[4][9] |
| `/data/system/shutdown-checkpoints/checkpoints-*` | AOSP | 종료·재부팅 요청을 보낸 곳과 호출 경로[10][11] |

## 위치와 버전별 차이

| 파일 | 위치한 영역 | 공장 초기화 뒤 | ALEAPP 시험 자료의 기기 |
|---|---|---|---|
| `power_off_reset_reason*.txt` | 사용자 데이터 영역 `/data/log/` | `/data` 와 함께 지워질 가능성이 있습니다 | 삼성, Android 10·13·14[1] |
| `history` | `/efs/recovery/` | 남습니다. Android 10 에서 11 로 올린 뒤에도 앞선 초기화 기록이 남았습니다[6] | 삼성, Android 10·14·15[3] |
| `recovery_history.log` | 사용자 데이터 영역 `/data/log/` | `/data` 와 함께 지워질 가능성이 있습니다 | — |
| `checkpoints-*` | 사용자 데이터 영역 `/data/system/` | `/data` 와 함께 지워질 가능성이 있습니다 | 픽셀·포코 등, Android 13~16[5] |

`history` 와 `eRR.p` 는 전체 파일 시스템 추출에서만 나옵니다[6][7]. 나머지 파일도 `/data` 아래에 있으므로 전체 파일 시스템 추출본에서 찾습니다. 추출 방식은 [모바일 증거 확보](../../03-techniques/acquisition/mobile-acquisition/index.md) 에서 다룹니다.

종료 체크포인트 기록 코드는 2020년 6월 AOSP 에 들어왔습니다[13]. AOSP 프레임워크 코드라서 삼성 기기에도 이 폴더가 있을 가능성이 있지만, 실제 기기에서 확인합니다.

## 구조

### power_off_reset_reason.txt

파일은 일반 텍스트이고, 사건 한 건이 `|` 로 나눈 한 줄입니다. 한 줄은 시각, 사건 종류, 상태, 사유나 부가 정보 순서입니다. 끄기(`SHUTDOWN`)·다시 시작(`REBOOT`) 줄은 맨 앞에 `HH:MM:SS` 시각이 한 번 더 붙고, 켜기(`ON`) 줄에는 붙지 않습니다[1][7]. 아래는 Galaxy S22(Android 13) 기기의 줄 모양을 따라 사건 줄만 모은 예시입니다(만든 예시)[7].

```
21:30:14  2026-01-10 21:30:14+0900 | SHUTDOWN |       | REASON: userrequested
2026-01-10 21:35:22+0900 |    ON    | NP    | S901NKSU2XXXX / OFFSRC: PWRHOLD / ONSRC: PWRON / RSTSTAT: PINRESET RSVD31 [213]
21:40:04  2026-01-10 21:40:04+0900 |  REBOOT  |       | REASON: userrequested
2026-01-10 21:41:05+0900 |    ON    | RP    | S901NKSU2XXXX / OFFSRC: - / ONSRC: PWRON / RSTSTAT: SWRESET [214]
```

사건 종류와 필드 값은 아래와 같습니다. 약어의 뜻은 삼성이 밝힌 것이 아니라 한 분석가가 시험 결과를 보고 붙인 해석입니다[7].

| 필드 값 | 나온 조건 (Galaxy S22, Android 12·13 시험)[7] |
|---|---|
| `SHUTDOWN` + `REASON: userrequested` | 전원 메뉴에서 전원 끄기 |
| `REBOOT` + `REASON: userrequested` | 전원 메뉴에서 다시 시작 |
| `SHUTDOWN` 또는 `REBOOT` + `REASON: shell` | `adb shell reboot -p` 같은 adb 명령 |
| `REBOOT` + `REASON: fastboot`, `REASON: recovery` | fastboot·복구 모드로 다시 시작 |
| `SHUTDOWN` + `REASON: no power` | 배터리가 다 닳아 꺼짐[7][8] |
| `ON` + `NP` | 전원이 없던 상태에서 켜짐. "no power" 일 가능성이 있습니다 |
| `ON` + `RP` | 다시 시작 과정에서 켜짐. "reboot power" 일 가능성이 있습니다 |
| `LPM` | 꺼진 채 충전기에 연결된 상태. "low power mode" 일 가능성이 있습니다 |
| `OFFSRC: PWRHOLD` | 전원 메뉴로 끈 뒤 켤 때 나왔고, adb 명령으로 끈 뒤 충전 화면에서도 나왔습니다 |
| `ONSRC: PWRON` | 전원 버튼으로 켬 |
| `ONSRC: ACOKB`, `ONSRC: INST_ACOK` | 충전기에 연결된 상태에서 켜짐. 충전 방식(벽 충전기·컴퓨터 USB)에 따라 나뉘는지는 시험 결과가 일정하지 않았습니다 |

`ON` 줄에는 모델·펌웨어 빌드 문자열(예: `S901BXXU2BVJA`)과 대괄호 안의 번호가 붙고, 충전 화면에서 남은 줄에는 `4053000(81%)` 처럼 배터리 잔량이 붙습니다[7].

사건 줄 앞뒤에는 다른 줄도 섞여 있습니다. 전원 메뉴로 끄거나 다시 시작할 때, 배터리가 다 닳아 꺼질 때, 업데이트로 복구 모드에 들어갈 때는 사건 줄보다 몇 초 앞선 `24/04/07 09:47:09` 형식(`yy/mm/dd HH:MM:SS`)의 시각 줄과 `reason : userrequested` 같은 사유 줄이 먼저 나오고, 그 뒤에 `java.lang.Exception: It is not an exception!! just save the trace for process which called shutdown thread!!` 로 시작하는 호출 경로가 붙습니다. 호출 경로에는 전원 끄기면 `ShutdownThread.shutdown(`, 다시 시작이면 `ShutdownThread.reboot(` 가 찍히고, 전원 메뉴에서 고른 경우에는 `StatusBarManagerService` 가, 배터리가 다 닳은 경우에는 `ShutdownThread.systemShutdown` 과 `BatteryService` 가 함께 찍힙니다. `adb shell reboot -p` 로 끈 사건에는 이 줄들이 없고 사건 줄만 있습니다. 사건 줄 뒤에는 `terminating init service start`, `volume shutdown end` 같은 종료 단계 줄이 시각과 함께 이어집니다[7].

`power_off_reset_reason_backup.txt` 는 같은 형식이고, 본 파일보다 앞선 사건을 담습니다. 복구 모드로 다시 시작한 사건은 사건 줄에 `REASON: recovery` 만 남지만, 앞선 `reason : recovery-update` 줄을 보면 업데이트 때문이었다는 것까지 알 수 있습니다. 이런 줄은 두 텍스트 파일 어느 쪽에나 있을 수 있어서 둘 다 봅니다[7].

같은 사건은 `/data/system/users/service/data/eRR.p` 에도 남습니다. 이 파일에는 끄기·다시 시작 줄 앞의 `HH:MM:SS` 시각과 호출 경로 줄이 없습니다[7]. 이 파일은 Android 9 기기에서도 보이고, 커널 패닉 (Kernel Panic) 은 앞선 끄기 줄 없이 `KP` 와 `PANIC: Oops: Fatal exception` 으로 남습니다[7]. 초기화 뒤에는 가장 최근 초기화 시각이 이 파일에 UTC 로 한 번 찍힙니다[6].

### /efs/recovery/history

복구 모드에 들어갈 때마다 기록 한 건이 쌓입니다. 한 건은 `+ [태그 | 시각 | 빌드]` 모양의 첫 줄로 시작하고, 그 아래에 복구 모드로 넘긴 명령 줄 인자와 재부팅 사유가 붙습니다. 옛 기기는 한 건 끝에 `-` 한 줄을 두고, 새 기기는 구분 줄 없이 다음 기록의 `+` 줄로 이어집니다. 첫 줄에 `|` 가 없는 더 오래된 형식도 있습니다[3].

설정 화면에서 공장 초기화를 하면 아래 모양의 기록이 남습니다. 값은 Galaxy A30(Android 10) 기록 모양을 따라 만든 예시입니다(만든 예시)[6].

```
+ [oj | 2026/01/10 12:39:52 | A305NKSU4XXXX]
--wipe_data
--requested_time=2026/01/10 21:39:27.062
--reason=MasterClearConfirm,2026-01-10T21:39:27Z
--locale=ko-KR
RP
reboot_reason=Reboot:1382 RecoverySystemMasterClearConfirm,2026-01-10T21:39:27Z
[S]   22.4G
[E]   22.4G
-
```

사용자가 버튼 조합으로 복구 모드에 들어가 초기화하면 기록이 훨씬 짧습니다. 아래 첫 기록은 복구 모드에 들어간 때이고, 둘째 기록은 초기화 뒤 다시 켠 때입니다. `--wipe_data` 줄이 없다는 점을 눈여겨봅니다(만든 예시)[6].

```
+ [tr | 2026/01/11 10:48:33 | A305NKSU4XXXX]
NP
reboot_reason=BL:Recovery Mode Set by key
[S]   22.4G
[E]   22.4G
-
+ [OZ | 2026/01/11 10:49:55 | A305NKSU4XXXX]
RP
reboot_reason=UNKNOWN
[S]   22.4G
[E]   22.4G
-
```

ALEAPP 가 읽는 줄은 아래와 같습니다[3][4].

| 줄 | 뜻 |
|---|---|
| `--wipe_data` | 사용자 데이터를 지우라는 요청. 공장 초기화 기록입니다 |
| `--prompt_and_wipe_data` | 이것도 공장 초기화 기록입니다 |
| `--reason=` | 요청 사유 문자열 |
| `--requested_time=` | 요청 시각 |
| `--locale=` | 기기 언어 설정 |
| `--carry_out=open_fota` | 펌웨어 업데이트(FOTA) 기록 |
| `--update_org_package=`, `--update_package=` | 업데이트 패키지 값 |
| `reboot_reason=` 또는 `reboot reason:` | 재부팅 사유 |

`--reason=` 값으로 초기화를 누가 요청했는지 나눌 수 있습니다. ALEAPP `sWipehist` 모듈은 아래처럼 나눕니다[4].

| `--reason=` 에 든 문자열 | 요청한 곳 |
|---|---|
| `MasterClearConfirm` | 기기 설정 화면 |
| `Fmm.RemoteWipeOut` | 삼성 내 디바이스 찾기 (Find My Mobile) 원격 초기화 |
| `Find My Device wiping device remotely` | 구글 내 기기 찾기 (Find My Device) 원격 초기화 |

첫 줄의 두 글자 태그(`Fx`, `tr`, `OZ` 등)는 기록마다 다르고[6], ALEAPP 도 뜻을 풀지 않고 적힌 그대로 보여 줍니다[3].

### /data/log/recovery_history.log

ALEAPP `sWipehist` 모듈은 이 파일을 `history` 와 같은 규칙(`+` 로 시작하는 첫 줄, `--wipe_data`, `--reason=`, `reboot_reason=`)으로 읽습니다[4]. 그래서 형식이 `history` 와 비슷할 가능성이 있지만, 실제 파일로 줄 모양을 먼저 확인합니다. 이 파일은 `/data` 아래에 있어서, 초기화 전 기록을 찾을 때는 `/efs/recovery/history` 를 봅니다.

### /data/system/shutdown-checkpoints/

Android 프레임워크는 종료나 재부팅 요청이 들어올 때마다 요청 한 건을 메모리에 적어 둡니다. 전원 메뉴 대화상자를 띄울 때도 요청을 먼저 적는데, 사용자가 대화상자에서 취소해도 이 기록은 남습니다[11]. 실제 종료가 시작되면 모아 둔 요청을 파일 하나로 씁니다[11].

| 항목 | 값 (현행 AOSP 기준)[10][11] |
|---|---|
| 파일 이름 | `/data/system/shutdown-checkpoints/checkpoints-` 뒤에 파일을 쓴 시각(유닉스 밀리초) |
| 파일 개수 | 최대 20개. 넘으면 이름 순으로 가장 오래된 파일부터 지웁니다 |
| 한 파일 안의 요청 수 | 최대 100건. 넘으면 가장 오래된 요청부터 버립니다. 부팅 뒤 메모리에 모은 요청이라, 한 파일에 그 부팅 동안의 요청이 들어갑니다 |

요청 한 건은 `Shutdown request from` 줄로 시작합니다. 요청을 보낸 곳은 `SYSTEM`(시스템 서버 안), `BINDER`(다른 프로세스가 PowerManager 로 요청), `INTENT`(인텐트로 요청) 세 가지입니다. `BINDER` 는 요청한 프로세스 이름과 PID 를, `INTENT` 는 인텐트 이름과 패키지 이름을, `SYSTEM` 은 호출 경로를 덧붙입니다[10][12]. 아래는 코드의 출력 형식으로 만든 예시입니다(만든 예시).

```
Shutdown request from BINDER for reason userrequested at 2026-01-10 21:30:09.412 KST (epoch=1768048209412)
com.android.server.power.PowerManagerService$BinderService.shutdown
From process com.android.systemui (pid=2345)
```

## 증거로서 의미

### 증명하는 것

`power_off_reset_reason.txt` 의 한 줄은 기기 시계 기준으로 그 시각에 기기가 꺼지거나 다시 시작했고, 시스템이 그 사유를 `userrequested`, `shell`, `no power` 같은 문자열로 적었다는 것을 알려 줍니다. `no power` 뒤에 배터리 0% 가 붙은 줄이 이어지면 배터리가 다 닳아 꺼진 경우로 읽을 수 있고, `userrequested` 는 전원 메뉴로 끈 경우와 맞습니다[7]. Galaxy S22 는 측면 버튼과 볼륨 아래 버튼을 함께 눌러야 전원 메뉴가 열려서, 우연히 이 순서로 끄기는 어렵습니다[7].

`/efs/recovery/history` 는 공장 초기화가 몇 번, 언제 요청됐는지를 초기화 뒤에도 알려 줍니다. `--reason=` 값으로 설정 화면에서 했는지, 원격 초기화였는지도 나눌 수 있습니다[4][6]. 초기화 한 번만 알려 주는 bootstat `factory_reset` 파일([초기화 흔적](../system-account/factory-reset.md))과 달리, 여기에는 앞선 초기화도 함께 남습니다.

`checkpoints-*` 파일은 종료 요청을 어느 프로세스·패키지가 보냈는지 알려 줍니다[10].

### 증명하지 못하는 것

`userrequested` 는 누군가 전원 메뉴 같은 사용자 화면으로 요청했다는 뜻이지, 누가 눌렀는지는 알려 주지 않습니다. `shell` 도 adb 같은 셸 명령으로 끈 것까지만 알려 주고, 명령을 보낸 사람이나 컴퓨터는 알려 주지 않습니다. 초기화를 왜 했는지도 이 기록으로는 알 수 없습니다. 기기를 초기화할 정당한 이유는 많아서, 초기화 기록이 곧 증거를 없애려 한 행동이라는 뜻은 아닙니다[6].

`history` 에 `--wipe_data` 가 없다고 초기화가 없었다고 할 수도 없습니다. 복구 모드에서 버튼으로 한 초기화는 `--wipe_data` 줄 없이 `reboot_reason=BL:Recovery Mode Set by key` 로만 남습니다[6].

보고서에는 "피의자가 전원을 껐다" 가 아니라 "기기 시계 기준 (시각)에 `REASON: userrequested` 인 종료 기록이 있다" 처럼 기록으로 확인되는 만큼만 씁니다.

## 시각 해석

같은 삼성 기록 안에서도 줄마다 시각 기준이 다릅니다.

| 파일·필드 | 기준 |
|---|---|
| `power_off_reset_reason.txt` 사건 줄 | 기기 현지 시각 + UTC 차이(`-0400`, `+0900` 등)[1][7] |
| 같은 파일, 꺼진 채 충전 중인 줄(`NP`·`LPM`) | `+0000`. Android 가 돌지 않아 시간대를 모르는 상태로 보입니다[7] |
| 같은 파일, 배터리가 다 닳은 뒤 켜진 줄 | `2021-01-01 12:00:07` 처럼 시계가 초기화된 값이 나올 수 있습니다[7] |
| 같은 파일, 호출 경로 앞 `yy/mm/dd HH:MM:SS` 줄 | UTC 차이 표시 없음. 아래 "함정과 한계" 참고 |
| `history` 첫 줄 | 아래 "함정과 한계" 참고 |
| `history` 의 `--requested_time=`, `--reason=` 속 시각 | 아래 "함정과 한계" 참고 |
| `checkpoints-*` 의 `epoch=` | 유닉스 밀리초 (UTC)[10] |
| `checkpoints-*` 의 `at` 뒤 날짜 | 파일을 쓸 때 기기의 기본 시간대로 바꾼 값과 시간대 약어[10] |

모든 값은 기기 시계를 따르므로, 사용자가 시각을 바꿔 둔 동안의 기록은 그만큼 어긋납니다. 시각 조작을 찾는 법은 [시각 조작 흔적](../../03-techniques/analysis/timeline/time-manipulation.md), 기기 시간대는 [시간대와 시각 설정](../system-account/time-zone.md) 에서 다룹니다.

## 함정과 한계

**시각 기준이 출처마다 다르게 적혀 있습니다.** ALEAPP `sRecoveryhist` 모듈 설명은 `history` 의 시각이 기기 현지 시각이라고 적습니다[3]. 그런데 UTC-4 지역의 Galaxy A30 기록에서는 첫 줄 시각이 `--requested_time=` 보다 4시간 늦었고, 실제 초기화 시각은 `--requested_time=` 과 `--reason=` 속 시각과 맞았습니다[6]. 이 기기에서는 첫 줄이 UTC, 두 요청 시각이 현지 시각이었던 셈이고, `--reason=` 속 시각에는 `Z` 가 붙어 있어도 UTC 가 아니었습니다. 기기마다 다를 수 있으니, 같은 기기의 다른 기록과 맞춰 보고 기준을 정합니다.

**앞선 시각 줄을 UTC 로 읽으면 어긋납니다.** `power_off_reset_reason.txt` 의 `24/04/07 09:47:09` 형식 줄은 바로 뒤 사건 줄(현지 시각 `09:47:14-0400`)보다 5초 앞선 값이라 현지 시각으로 보입니다[7]. ALEAPP 의 옛 모듈 `oldpowerOffReset` 은 이 줄을 UTC 로 읽으므로[2], 그 결과를 쓸 때는 시간대를 다시 확인합니다.

**도구가 모든 줄을 보여 주지 않습니다.** ALEAPP `powerOffReset` 모듈은 `REASON:` 이 든 줄만 읽어서, 켜기(`ON`)·`NP`·`LPM` 줄은 결과에 나오지 않습니다[1]. `sWipehist` 모듈은 `--wipe_data` 나 `--prompt_and_wipe_data` 가 있고 그 뒤에 `reboot_reason=` 줄이 오는 기록만 내보내서, 복구 모드에서 버튼으로 한 초기화는 빠집니다[4]. 복구 모드 기록 전체를 보려면 `sRecoveryhist` 모듈 결과나 원본 파일을 함께 봅니다[3].

**파일 하나만 보면 기간이 짧습니다.** `power_off_reset_reason.txt` 에 없는 앞선 사건이 `_backup.txt` 에 있으므로 두 파일을 합쳐 봅니다[7]. `checkpoints-*` 는 최대 20개만 남아서 종료가 잦은 기기에서는 오래된 요청이 지워집니다[10].

**취소한 요청도 기록됩니다.** 체크포인트는 전원 메뉴 대화상자를 띄울 때 먼저 적으므로, 한 파일에 든 요청이 모두 실제 종료로 이어졌다고 볼 수 없습니다[11].

## 직접 분석해 보기

### 텍스트로 한 번

세 파일 모두 일반 텍스트라서 편집기로 열어 읽습니다. `history` 에서 초기화 기록만 뽑으려면 첫 줄과 초기화 관련 줄을 함께 찾습니다.

```
grep -n -E '^\+|--wipe_data|--prompt_and_wipe_data|--reason=|--requested_time=|reboot_reason' /추출본/efs/recovery/history
grep -n -E 'REASON:|\| +ON +\||LPM' /추출본/data/log/power_off_reset_reason*.txt
grep -n 'Shutdown request from' /추출본/data/system/shutdown-checkpoints/checkpoints-*
```

체크포인트 파일 이름 뒤 숫자는 유닉스 밀리초라서 `date -u -d @1768048209` 처럼 앞 10자리로 날짜를 확인합니다(만든 예시). 유닉스 시각을 읽는 법은 [시각 값](../../01-foundations/value-decoding/time-values.md) 에 있습니다.

### 공개 도구로 한 번

ALEAPP 에서 아래 모듈을 켜고 추출본을 넣습니다[1][3][4][5].

| 모듈 | 읽는 파일 | 결과 열 |
|---|---|---|
| `powerOffReset` | `*/log/power_off_reset_reason.txt`, `*/log/power_off_reset_reason_backup.txt` | Timestamp (Local), Timezone Offset, Action, Reason |
| `sRecoveryhist` | `*/efs/recovery/history` | Timestamp, Request Timestamp, Build, Entry Tag (as stored), Wipe, Prompt & Wipe, Reason, Reboot Reason, Locale, Carry Out, Update ORG, Update PKG |
| `sWipehist` | `*/efs/recovery/history`, `*/data/log/recovery_history.log` | Timestamp, Wipe, Prompt & Wipe, Reason, Provider, Reboot Reason, Locale, Request Timestamp |
| `shutdown_checkpoints` | `*/system/shutdown-checkpoints/checkpoints-*` | Timestamp(UTC 로 바꾼 `epoch=`), Requestor, Entry |

도구 결과는 위 "함정과 한계" 의 빠지는 줄을 원본 파일과 맞춰 봅니다([도구 검증](../../03-techniques/reporting/tool-validation.md)).

## 교차 검증

| 함께 볼 아티팩트 | 맞춰 볼 것 |
|---|---|
| [초기화 흔적](../system-account/factory-reset.md) | bootstat `factory_reset` 시각과 `history` 의 가장 최근 `--wipe_data` 기록 |
| [디지털 웰빙](../app-usage/digital-wellbeing.md) | 기기 켜기·끄기 이벤트 시각과 `power_off_reset_reason.txt` 의 사건 시각 |
| [배터리 사용 기록](../app-usage/batterystats.md) | 배터리 잔량 흐름과 `REASON: no power` 기록 |
| [기기 정보와 빌드](../system-account/device-build.md) | `history` 첫 줄의 빌드 문자열이 바뀐 시점과 `--carry_out=open_fota` 기록 |
| [앱 오류·종료 기록](../app-usage/crash-records.md) | 커널 패닉·비정상 종료 무렵의 다른 기록 |

초기화 시점을 좁히는 전체 흐름은 [초기화 조사 시나리오](../../04-scenarios/activity/anti-forensics/factory-reset.md) 에서 다룹니다.

## 실습

삼성 기기 전체 파일 시스템 추출본이 든 공개 시험 이미지를 골라 아래 질문을 풀어 봅니다.

1. `/efs/recovery/history` 에 기록이 몇 건 있고, 그 가운데 `--wipe_data` 가 든 기록은 몇 건입니까? `--reason=` 값은 무엇입니까?
2. 가장 최근 `--wipe_data` 기록의 첫 줄 시각과 `--requested_time=` 은 몇 시간 차이가 납니까? 이 차이는 기기 시간대와 맞습니까?
3. `power_off_reset_reason.txt` 와 `_backup.txt` 를 합치면 가장 오래된 사건은 언제입니까? `REASON:` 값은 몇 종류입니까?
4. `REASON: no power` 기록 바로 뒤 줄의 시각과 배터리 잔량은 얼마입니까?
5. ALEAPP `powerOffReset` 결과의 행 수와 원본 파일에서 `REASON:` 이 든 줄 수가 같습니까? `ON` 줄은 몇 개입니까?

## 참고 문헌

1. ALEAPP, scripts/artifacts/powerOffReset.py (GitHub main) — https://github.com/abrignoni/ALEAPP/blob/main/scripts/artifacts/powerOffReset.py
2. ALEAPP, scripts/artifacts/oldpowerOffReset.py (GitHub main) — https://github.com/abrignoni/ALEAPP/blob/main/scripts/artifacts/oldpowerOffReset.py
3. ALEAPP, scripts/artifacts/sRecoveryhist.py (GitHub main) — https://github.com/abrignoni/ALEAPP/blob/main/scripts/artifacts/sRecoveryhist.py
4. ALEAPP, scripts/artifacts/sWipehist.py (GitHub main) — https://github.com/abrignoni/ALEAPP/blob/main/scripts/artifacts/sWipehist.py
5. ALEAPP, scripts/artifacts/shutdown_checkpoints.py (GitHub main) — https://github.com/abrignoni/ALEAPP/blob/main/scripts/artifacts/shutdown_checkpoints.py
6. The Binary Hick, "Wipeout! Detecting Android Factory Resets" (2021-08-19) — https://thebinaryhick.blog/2021/08/19/wipeout-detecting-android-factory-resets/
7. The Binary Hick, "DeRR.p. Investigating Power Events on Samsung Devices" (2024-04-07) — https://thebinaryhick.blog/2024/04/07/__trashed/
8. Kevin Pagano, "Samsung Power Off Reset Logs" (2021-10-12) — https://www.stark4n6.com/2021/10/samsung-power-off-reset-logs.html
9. Forensafe, "Investigating Samsung Wipe History" (2024-12-20) — https://www.forensafe.com/blogs/SamsungWipeHistory.html
10. ShutdownCheckPoints.java — AOSP frameworks/base (main). https://raw.githubusercontent.com/aosp-mirror/platform_frameworks_base/main/services/core/java/com/android/server/power/ShutdownCheckPoints.java
11. ShutdownThread.java — AOSP frameworks/base (main). https://raw.githubusercontent.com/aosp-mirror/platform_frameworks_base/main/services/core/java/com/android/server/power/ShutdownThread.java
12. PowerManagerService.java — AOSP frameworks/base (main). https://raw.githubusercontent.com/aosp-mirror/platform_frameworks_base/main/services/core/java/com/android/server/power/PowerManagerService.java
13. "Create ShutdownCheckPoints for shutdown call logging" — AOSP frameworks/base 커밋 ea76d7e (2020-06-26). https://github.com/aosp-mirror/platform_frameworks_base/commit/ea76d7e31c994c94abad6722a2f6e7e4afb6196b
