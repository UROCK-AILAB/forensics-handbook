---
title: "권한 사용 기록"
parent: "설치된 앱"
grand_parent: "아티팩트 · 앱 설치·사용 흔적"
nav_order: 450
---

# 권한 사용 기록 (AppOps·Privacy Dashboard)

앱이 카메라·마이크·위치 같은 민감한 기능을 실제로 쓰면 시스템의 앱 작업 서비스(AppOps)가 그 접근을 기록하고, 이 기록은 `/data/system/` 의 `appops.xml`·`appops_accesses.xml` 과 `/data/system/appops/discrete/` 폴더에 남습니다 [1][4][6]. 삼성 기기에서는 개인정보 보호 대시보드 앱의 `permission_db` 에도 접근 기록이 따로 쌓입니다 [3][15]. 이 페이지에서는 어느 앱이 무엇을 언제 썼는지를 이 파일들에서 읽는 방법과, 버전마다 달라지는 위치·보존 기간을 정리합니다.

## 무엇을 기록하나 · 왜 생기나

[앱 권한 부여 기록](runtime-permissions.md)의 `runtime-permissions.xml` 에는 앱이 권한을 받았는지만 적히고 시각이 없습니다. 권한을 받은 앱이 그 기능을 실제로 쓰는 순간에는 AppOps 가 작업(op) 번호와 시각, 그때 앱이 화면 앞에 있었는지 뒤에 있었는지를 따로 적습니다 [1][6]. 그래서 "이 앱이 마이크 권한이 있었나" 가 아니라 "이 앱이 몇 시에 마이크를 썼나" 에 답하는 기록이 됩니다.

기록은 목적이 다른 세 종류입니다. 첫째는 작업마다 마지막 접근·거부 시각만 남기는 최근 접근 기록이고, 둘째는 Android 12 에 들어온 개인정보 보호 대시보드(Privacy Dashboard)가 쓰는 접근 이력(discrete)입니다 [7][13]. 셋째는 작업을 허용할지 막을지 정한 모드 값인데, 이 값에는 시각이 없습니다 [2]. 삼성의 `permission_db` 는 여기에 더해 제조사 앱이 따로 남기는 접근 기록입니다 [3][15].

## 위치와 버전별 차이

| 위치 | Android 버전 | 담긴 것 |
|---|---|---|
| `/data/system/appops.xml` | Android 13 이하 | 작업마다 모드와 마지막 접근·거부 시각 [1][2][5][14] |
| `/data/system/appops.xml` | Android 14 | 모드만 남음. 접근 기록은 아래 파일로 나뉨 [1] |
| `/data/system/appops_accesses.xml` | Android 14 부터 | 작업마다 마지막 접근·거부 시각, 앱 상태, 대리 호출 정보 [1][9] |
| `/data/system/appops/discrete/` 의 파일들 | Android 12 부터 | 위치·카메라·마이크 같은 일부 작업의 접근 이력 [6][7][13] |
| `/data/misc/apexdata/com.android.permission/access.abx`, `/data/misc_de/<사용자ID>/apexdata/com.android.permission/access.abx` | Android 15 부터 | 작업 모드와 권한 부여 상태. 시각 없음 [2] |
| `com.samsung.android.privacydashboard` 앱 데이터 폴더의 `databases/permission_db` | 삼성 Android 13~15 이미지에서 확인 [3] | 앱·권한 그룹·접근 시각·백그라운드 여부 [3] |

ALEAPP 가 시험한 추출본 39개 가운데 `appops_accesses.xml` 은 Android 14 이상인 25개에 모두 있었고 Android 13 이하인 11개에는 없었습니다 [1]. `access.abx` 는 Android 15 부터 켜지는 권한 서비스가 쓰는 파일이라서, 같은 시험에서 이 파일이 있던 22개 추출본은 모두 Android 15 이상이었습니다 [2]. Android 15 이후에도 `appops.xml` 이 남는 기기가 있어서, 같은 시험에서 삼성 이미지 한 개에 이 파일이 남아 있었습니다 [2].

`discrete` 폴더의 기록 대상과 보존 기간은 AOSP 소스의 기본값이 버전마다 다릅니다 [6][7][8][18].

| AOSP 소스 | 기본으로 기록하는 작업 | 기본 보존 기간 |
|---|---|---|
| android-12.0.0_r1 | FINE_LOCATION, COARSE_LOCATION, CAMERA, RECORD_AUDIO, PHONE_CALL_MICROPHONE, PHONE_CALL_CAMERA | 24시간 |
| android-13.0.0_r1, android-14.0.0_r1 | 위 여섯 가지와 RECEIVE_AMBIENT_TRIGGER_AUDIO(120) | 7일 |
| main | 위 일곱 가지와 EMERGENCY_LOCATION, RECEIVE_SANDBOX_TRIGGER_AUDIO, RESERVED_FOR_TESTING | 7일 |

보존 기간과 기록 대상은 DeviceConfig 의 privacy 영역에 있는 `discrete_history_cutoff_millis`·`discrete_history_ops_cslist` 값으로 바꿀 수 있고, 디버그 빌드가 아니면 보존 기간은 30일을 넘지 못합니다 [6]. 그래서 같은 버전이라도 기기마다 남은 기간이 다를 수 있으니, 실제 폴더에서 가장 오래된 파일 이름의 시각을 확인합니다. Android 12 Pixel 3 에서는 폴더 전체가 24시간 치였고, 대시보드도 위치·카메라·마이크 세 가지만 보여 줬습니다 [13].

삼성 `permission_db` 는 여러 삼성 기기에서 약 7일 치가 남았고, `discrete` 폴더에 없는 권한 접근도 들어 있는 것으로 보입니다 [15]. 기기마다 남은 기간은 실제 DB 에서 가장 오래된 행의 시각으로 확인합니다.

## 구조

### appops_accesses.xml (Android 14 부터)

파일은 안드로이드 바이너리 XML(ABX)로 저장되고 [1][9], 요소는 `app-ops` → `pkg` → `uid` → `op` → `st` 순서로 들어 있습니다 [9].

| 요소 | 속성 | 담긴 것 |
|---|---|---|
| `app-ops` | v | 형식 버전(1) [9] |
| `pkg` | n | 패키지 이름 [9] |
| `uid` | n | 앱의 UID [9] |
| `op` | n | 작업 번호. 예: 0 COARSE_LOCATION, 1 FINE_LOCATION, 26 CAMERA, 27 RECORD_AUDIO [1][9] |
| `st` | n | 앱 상태와 호출 방식을 합친 키. 앱 상태 값을 31비트 왼쪽으로 민 값에 호출 방식 비트를 더한 수입니다 [1][16] |
| `st` | t, r, d | 마지막 접근 시각, 마지막 거부 시각, 접근 지속 시간. 모두 밀리초이고 0 보다 클 때만 씁니다 [9] |
| `st` | id | 속성 태그(attribution tag). 앱이 기능 안에서 나눠 붙인 이름입니다 [1][9] |
| `st` | pp, pu, pc | 다른 앱을 대신해 접근했을 때 대리 앱의 패키지·UID·속성 태그 [9] |
| `st` | dv, pdv | 기본 기기가 아닌 가상 기기의 ID [9] |

작업 번호와 이름의 대응은 Android 11·13·14·15 와 main 에서 같습니다 [1]. ALEAPP 는 `op` 의 `m` 속성을 작업 모드로 읽고, 모드가 기본값과 다를 때만 적힌다고 설명합니다 [1]. 현행 AOSP main 의 쓰기 코드에는 `m` 속성이 없으니, 이 속성이 있는지는 실제 파일에서 확인합니다 [9].

`st` 의 키에서 앱 상태 값은 100 PERSISTENT, 200 TOP, 300 FOREGROUND_SERVICE_LOCATION, 400 FOREGROUND_SERVICE, 500 FOREGROUND, 600 BACKGROUND, 700 CACHED 이고, 호출 방식 비트는 0x1 SELF(앱이 직접), 0x2 TRUSTED_PROXY, 0x4 UNTRUSTED_PROXY, 0x8 TRUSTED_PROXIED, 0x10 UNTRUSTED_PROXIED 입니다 [1]. 앱 상태로 화면 앞에서 쓴 접근과 캐시 상태에서 쓴 접근을 구분할 수 있습니다 [1].

시스템은 작업·속성 태그·앱 상태·호출 방식의 조합마다 마지막 접근 시각과 마지막 거부 시각만 꺼내 쓰므로, 한 키에는 시각 값이 하나씩만 있습니다 [9]. 그래서 이 파일로는 "마지막으로 언제" 는 알 수 있지만 "몇 번" 은 알 수 없습니다.

### appops.xml (Android 13 이하)

Android 10 이후 형식은 `pkg` → `uid` → `op` 아래 하위 요소에 `t`(접근 시각), `r`(거부 시각), `id`, `pp`, `pu` 가 붙은 모양이고, ALEAPP 의 appops 모듈이 이 값들을 읽습니다 [5]. Android 14 에서 파일이 둘로 나뉜 뒤 접근 기록은 위의 `appops_accesses.xml` 로 옮겨 갔습니다 [1].

Android 9 이하 형식은 시각이 `op` 요소에 바로 붙습니다 [5]. 이때 접근 시각은 앱 상태별로 `tp`(PERSISTENT), `tt`(TOP), `tfs`(FOREGROUND_SERVICE), `tf`(FOREGROUND), `tb`(BACKGROUND), `tc`(CACHED) 에 나뉘어 적히고, 거부 시각도 같은 방식으로 `rp`, `rt`, `rfs`, `rf`, `rb`, `rc` 에 적힙니다 [12]. ALEAPP 의 옛 형식 모듈은 `t` 로 시작하는 접근 시각만 읽고 `r` 로 시작하는 거부 시각은 표에 넣지 않습니다 [5].

### discrete 폴더 (Android 12 부터)

폴더 안의 파일은 확장자가 없고, 이름은 파일을 쓴 시각(Unix 밀리초) 뒤에 `tl` 을 붙인 형식입니다(예: `1767227400000tl`, 만든 예시) [6][13]. 파일 내용은 ABX 입니다 [13]. 시스템은 메모리에 모아 둔 접근을 저장할 때마다 새 파일 하나로 쓰고, 그때 보존 기간보다 오래된 이름의 파일을 지웁니다 [6].

| 요소 | 속성 | 담긴 것 |
|---|---|---|
| `h` | v, lc | 형식 버전(1), 가장 큰 대리 호출 연결(attribution chain) 번호 [6] |
| `u` | ui | UID [6] |
| `p` | pn | 패키지 이름 [6] |
| `o` | op | 작업 번호 [6] |
| `a` | at | 속성 태그(없으면 속성도 없음) [6] |
| `e` | nt | 접근 시각(Unix 밀리초) [6] |
| `e` | nd | 지속 시간(밀리초). 지속 시간이 없는 접근은 속성을 쓰지 않습니다 [6] |
| `e` | us, f | 앱 상태, 호출 방식 비트 [6] |
| `e` | af, ci, di | 대리 호출 연결 플래그, 대리 호출 연결 번호, 가상 기기 ID. 기본값이면 쓰지 않습니다 [6] |

기본 설정에서는 앱이 직접 쓴 접근(SELF)과 믿을 수 있는 대리 호출(TRUSTED_PROXY, TRUSTED_PROXIED)만 이 폴더에 적습니다 [6]. 같은 1분 구간 안에서 앱 상태·호출 방식·대리 호출 연결 값이 같고 지속 시간을 1분 단위로 올림한 값도 같은 접근이 또 오면 새 항목을 만들지 않습니다 [6]. 같은 `appops` 폴더에는 작업별 합계를 적는 `history` 폴더도 있습니다 [11].

### access.abx (Android 15 부터)

Android 15 부터 권한 상태를 맡는 서비스가 사용자별 `access.abx` 를 쓰고, 시스템용 파일도 따로 하나 씁니다 [2]. 사용자 파일에서 권한 사용과 관련된 부분은 세 곳입니다 [2].

| 부분 | 담긴 것 |
|---|---|
| `app-id-app-ops` → `app-id`(id) → `app-op`(name, mode) | 앱 ID 에 걸린 작업 모드 [2] |
| `package-app-ops` → `package`(name) → `app-op`(name, mode) | 패키지 이름에 걸린 작업 모드 [2] |
| `app-id-permissions` → `app-id`(id) → `permission`(name, flags) | 권한 부여 상태 [2] |

작업은 `android:camera` 같은 문자열로 적혀서, 번호로 적는 `appops_accesses.xml` 과 맞추려면 문자열을 번호로 바꿔야 합니다 [2]. 대부분은 소문자 이름에 `android:` 를 붙인 모양이지만, `android:monitor_location_high_power`(42 MONITOR_HIGH_POWER_LOCATION), `android:receive_ambient_trigger_audio`(120 RECEIVE_SOUNDTRIGGER_AUDIO)처럼 이름이 다른 작업이 있습니다 [2]. 모드 값은 0 ALLOWED, 1 IGNORED, 2 ERRORED, 3 DEFAULT, 4 FOREGROUND 이고, 기본값과 다를 때만 적히며 기본값으로 돌아가면 항목이 지워집니다 [2]. `app-id-app-ops` 와 `app-id-permissions` 에는 앱 ID 만 있어서 패키지 이름은 `packages.xml` 의 userId 로 찾고, 여러 앱이 같은 ID 를 나눠 쓰면 `shared-user` 이름(예: `android.uid.system`)이 나옵니다 [2].

`app-id-permissions` 의 flags 는 [앱 권한 부여 기록](runtime-permissions.md)의 PackageManager 비트와 번호가 다른 권한 서비스 자체의 비트입니다 [2].

```
0x1 INSTALL_GRANTED        0x100 SYSTEM_FIXED                  0x10000  SYSTEM_EXEMPT
0x2 INSTALL_REVOKED        0x200 PREGRANT                      0x20000  UPGRADE_EXEMPT
0x4 PROTECTION_GRANTED     0x400 LEGACY_GRANTED                0x40000  RESTRICTION_REVOKED
0x8 ROLE                   0x800 IMPLICIT_GRANTED              0x80000  SOFT_RESTRICTED
0x10 RUNTIME_GRANTED       0x1000 IMPLICIT                     0x100000 APP_OP_REVOKED
0x20 USER_SET              0x2000 USER_SENSITIVE_WHEN_GRANTED  0x200000 ONE_TIME
0x40 USER_FIXED            0x4000 USER_SENSITIVE_WHEN_REVOKED  0x400000 HIBERNATION
0x80 POLICY_FIXED          0x8000 INSTALLER_EXEMPT             0x800000 USER_SELECTED
```

부여 여부는 INSTALL_GRANTED 가 있으면 부여, 없고 INSTALL_REVOKED 가 있으면 미부여, PROTECTION_GRANTED·LEGACY_GRANTED·IMPLICIT_GRANTED 가 있으면 부여, RESTRICTION_REVOKED 가 있으면 미부여, 나머지는 RUNTIME_GRANTED 로 정합니다 [2]. Android 15 이상 추출본 22개 가운데 21개에서 같은 폴더의 `runtime-permissions.xml` 은 권한 항목이 하나도 없는 948~1,160바이트짜리 파일이었습니다 [2]. 나머지 한 개인 삼성 Android 15 이미지에서는 두 파일에 모두 권한 항목이 있었고, 앱 ID 와 권한 이름으로 맞춰 보면 11,912행은 부여 여부가 같고 185행은 달랐습니다 [2]. 그래서 Android 15 이상에서는 권한 부여 상태를 `access.abx` 에서 먼저 보고, 두 파일이 모두 차 있으면 한쪽 값만 옮겨 쓰지 않습니다.

### 삼성 permission_db

`permissionAccessInformations` 표에 접근한 앱과 권한, 접근 시각이 들어 있고 [15], ALEAPP 는 아래 열을 읽습니다 [3].

| 열 | 담긴 것 |
|---|---|
| ACCESS_TIME | 접근 시각(Unix 시각) [3] |
| PACKAGE_NAME | 접근한 앱 [3] |
| PERMISSION_GROUP_ID | 권한 그룹 [3] |
| OPERATION_CODE | 작업 코드(정수, ALEAPP 는 풀지 않고 그대로 냄) [3] |
| BACKGROUND | 백그라운드에서 접근했는지 [3] |
| PROXY_NAME, PROXY_ATTRIBUTION_TAG | 대리 호출 정보 [3] |
| UID | 앱의 UID. 옛 One UI 에는 이 열이 없습니다 [3] |

OPERATION_CODE 가 AOSP 작업 번호와 같은 체계일 가능성이 있지만, 같은 시각의 `discrete` 기록과 번호를 맞춰 보고 판단합니다. 버전마다 열이 다를 수 있으니 `PRAGMA table_info(permissionAccessInformations)` 로 열을 먼저 확인합니다.

## 증거로서 의미

| 증명하는 것 | 증명하지 못하는 것 |
|---|---|
| 이 UID·패키지가 이 시각에 카메라·마이크·위치 같은 작업을 썼거나 거부당했다는 기록 | 카메라로 무엇을 찍었는지, 마이크로 무엇을 녹음했는지 |
| 접근 때 앱이 화면 앞(TOP)이었는지, 백그라운드·캐시 상태였는지 | 사용자가 직접 그 기능을 켰는지(앱 상태만 적힘) |
| 다른 앱을 대신한 접근이면 대리 앱이 누구였는지 | `appops_accesses.xml` 에 없는 시각에 접근이 없었다는 것(마지막 값만 남음) |
| `discrete` 에 남은 기간 안의 접근 이력 | 보존 기간 밖이나 기록 대상이 아닌 작업의 접근 |
| `access.abx` 에 적힌 시점의 작업 모드와 권한 부여 상태 | 모드나 권한이 언제 바뀌었는지(`access.abx` 에 시각 없음) [2] |

보고서에는 "앱이 몰래 녹음했다" 가 아니라 "`discrete` 기록에 이 패키지가 2026-01-01 00:00:00 UTC 에 RECORD_AUDIO 작업을 95초 동안 쓴 항목이 있고, 앱 상태 값은 200(TOP)이다(만든 예시)" 처럼 기록으로 확인되는 만큼만 씁니다.

## 시각 해석

`appops.xml`·`appops_accesses.xml` 의 `t`·`r` 와 `discrete` 의 `nt` 는 모두 Unix 밀리초이고 UTC 기준입니다 [1][4][6]. 개인정보 보호 대시보드 화면은 같은 값을 기기 시간대로 바꿔 보여 줍니다 [13]. 시간대를 맞추는 방법은 [시간대와 시각 설정](../../system-account/time-zone.md), 값 읽는 법은 [시각 값](../../../01-foundations/value-decoding/time-values.md) 페이지에 있습니다.

`nt` 에는 접근 시각이 밀리초까지 그대로 저장됩니다. 1분 단위로 내린 시각은 중복을 거를 때와 API 로 기록을 돌려줄 때 쓰므로, 대시보드처럼 API 로 읽는 화면의 시각은 파일의 `nt` 와 1분 안에서 다를 수 있습니다 [6]. `nd` 가 있으면 `nt` 에 `nd` 를 더해 접근이 끝난 무렵을 추정할 수 있습니다. `discrete` 파일 이름의 시각은 접근 시각이 아니라 메모리의 기록을 파일로 쓴 시각이라서, 파일 안의 항목은 그보다 앞선 시각입니다 [6].

파일을 쓰는 간격은 출처마다 다릅니다. AOSP 의 `DiscreteRegistry` 설명은 기본 30분마다 저장한다고 적었고 [6], Android 12 Pixel 3 에서는 8~17분 간격으로 새 파일이 생겼습니다 [13]. `appops_accesses.xml` 은 변경 뒤 최대 30분 늦게 쓰는 방식이라 [1][10], 확보 직전 몇십 분의 접근은 파일에 없을 수 있습니다. `access.abx` 는 변경 뒤 1~2초 안에 씁니다 [2].

삼성 `permission_db` 의 ACCESS_TIME 은 ALEAPP 가 값의 크기로 단위를 정합니다. 10자리 이하는 초, 11~13자리는 밀리초, 14~16자리는 마이크로초로 보고, 모두 초 단위로 잘라 표에 냅니다 [3][17]. 밀리초가 필요하면 DB 의 원래 값을 직접 읽습니다.

## 함정과 한계

앱을 지우면 AOSP 는 `discrete` 폴더를 통째로 지우고, 지운 앱을 뺀 나머지 기록을 새 파일 하나로 다시 씁니다 [6][10][11]. Android 12 Pixel 3 에서도 앱을 지우자 폴더가 비워졌습니다 [13]. 이 경우 폴더에 파일이 하나뿐이고 이름의 시각이 앱을 지운 무렵일 가능성이 있으니, 파일 개수와 이름 시각을 [설치된 앱](index.md) 기록과 맞춰 봅니다.

`appops_accesses.xml` 에는 확보 당시 설치돼 있지 않은 패키지가 남을 수 있습니다. ALEAPP 의 Android 15 시험 에뮬레이터에서는 파일에 나온 패키지 317개 가운데 2개가 설치돼 있지 않았고, 그중 하나는 `pm uninstall` 로 지운 앱이었습니다 [1].

ALEAPP 의 discreteNative 모듈은 `o` 요소마다 마지막 `e` 요소 하나만 표에 넣습니다 [4]. 한 작업에 접근이 여러 번 적혀 있어도 표에는 한 줄만 나오니, 접근 횟수를 셀 때는 파일을 직접 풉니다. 이 모듈은 작업 번호 1·26·27 만 이름으로 바꾸고 나머지는 번호로 냅니다 [4].

Android 16·17 Pixel 에서는 AOSP main 표에 없는 작업 번호(164, 166 등)가, Android 15 샤오미에서는 10008 같은 제조사 번호가 `appops_accesses.xml` 에 나왔습니다 [1]. 표에 없는 번호는 이름을 짐작해 붙이지 않고 번호 그대로 보고합니다.

`access.abx` 에 작업 모드가 없으면 기본 모드가 적용된 상태라는 뜻이지, 막혔거나 설정한 적이 없다는 뜻이 아닙니다 [2]. 이 파일의 `access.abx.reservecopy` 사본은 다른 시점의 상태라서 본 파일과 섞어 읽지 않습니다 [2].

## 직접 분석해 보기

### 파일로 따라가기

1. `/data/system/appops_accesses.xml`(Android 14 이상) 또는 `appops.xml`, `/data/system/appops/discrete/` 폴더 전체, 삼성이면 `permission_db` 와 `-wal` 파일을 함께 확보합니다.
2. 파일 앞 4바이트가 `41 42 58 00` 이면 ABX 이니 [안드로이드 바이너리 XML (ABX)](../../../01-foundations/data-formats/abx.md) 페이지의 방법으로 텍스트 XML 로 풉니다.
3. `discrete` 파일 이름을 시각순으로 정렬해 가장 오래된 파일과 가장 새 파일의 시각으로 남아 있는 기간을 확인합니다.
4. 찾는 앱의 `p`(discrete) 또는 `pkg`(appops_accesses)를 열고 작업 번호 26(CAMERA), 27(RECORD_AUDIO), 0·1(위치)을 찾습니다.

아래는 소스의 쓰기 형식으로 만든 예시이고, 실제 기기에서 나온 값이 아닙니다(만든 예시).

```
discrete/1767227400000tl 를 푼 결과
<h v="1" lc="0">
  <u ui="10234">
    <p pn="com.example.recorder">
      <o op="27">
        <a>
          <e nt="1767225600000" nd="95000" us="200" f="1" />

nt 1767225600000 = 2026-01-01 00:00:00 UTC
nd 95000         = 95초
us 200 = TOP (화면 앞),  f 1 = SELF (앱이 직접)
```

```
appops_accesses.xml 을 푼 결과
<pkg n="com.example.recorder">
  <uid n="10234">
    <op n="26">
      <st n="429496729601" t="1767225600000" d="12000" />

n 429496729601 >> 31        = 200 (TOP)
n 429496729601 & 0xFFFFFFFF = 1 (SELF)
```

### 공개 도구로 따라가기

ALEAPP 에는 이 기록을 읽는 모듈이 나뉘어 있습니다. appOpsAccesses 는 `appops_accesses.xml` 을 [1], appops 는 `appops.xml` 을 [5], discreteNative 는 `discrete` 폴더를 [4], permissionAccessState 는 `access.abx` 와 `packages.xml` 을 [2], samsungPrivacyDashboard 는 `permission_db` 를 읽습니다 [3]. appOpsAccesses 는 `st` 의 키를 앱 상태와 호출 방식으로 풀어 주고, permissionAccessState 는 flags 를 이름으로 풀어 부여 여부를 계산합니다 [1][2]. 실행 중인 기기에서는 `dumpsys appops` 가 패키지와 작업 이름을 찍으니 [1], 파일에서 푼 결과와 맞춰 봅니다. 출력을 뽑는 방법은 [dumpsys 출력](../../logs/dumpsys.md) 페이지에 있습니다.

## 교차 검증

- [앱 권한 부여 기록 (Runtime Permissions)](runtime-permissions.md) — 접근한 앱이 그 권한을 받은 상태였는지
- [설치 출처와 설치 시각](install-source-time.md) — 접근한 앱이 언제, 어디서 들어왔는지
- [앱 사용 기록 (usagestats)](../usagestats/index.md), [디지털 웰빙 (Digital Wellbeing)](../digital-wellbeing.md) — 같은 시각에 앱이 화면에 떠 있었는지
- [빅스비 (Bixby)](../../samsung/bixby.md) — 삼성 기기에서 마이크를 쓴 음성 명령 시각
- [몰래 설치된 감시 앱 (Stalkerware)](../../../04-scenarios/incident/stalkerware.md) — 백그라운드 마이크·위치 접근을 찾는 조사

## 실습

사용자 데이터가 들어 있는 공개 시험 데이터(NIST CFReDS 등)나 직접 만든 시험 기기의 추출본으로 풀어 봅니다.

1. 기기의 Android 버전에 맞춰 `appops.xml`, `appops_accesses.xml`, `access.abx` 가운데 어느 파일이 있습니까? 각 파일은 ABX 입니까?
2. `discrete` 폴더에서 가장 오래된 파일과 가장 새 파일의 이름 시각은 며칠 차이입니까? 그 기간이 버전 기본값(24시간 또는 7일)과 맞습니까?
3. 카메라(26)나 마이크(27)를 쓴 앱 가운데 앱 상태가 BACKGROUND(600)나 CACHED(700)인 항목이 있습니까? 그 시각에 usagestats 에서 그 앱이 화면 앞에 있었습니까?
4. 삼성 기기라면 `permission_db` 에만 있고 `discrete` 에는 없는 접근이 있습니까?

## 참고 문헌

1. ALEAPP appOpsAccesses.py — abrignoni/ALEAPP, https://github.com/abrignoni/ALEAPP/blob/main/scripts/artifacts/appOpsAccesses.py
2. ALEAPP permissionAccessState.py — abrignoni/ALEAPP, https://github.com/abrignoni/ALEAPP/blob/main/scripts/artifacts/permissionAccessState.py
3. ALEAPP samsungPrivacyDashboard.py — abrignoni/ALEAPP, https://github.com/abrignoni/ALEAPP/blob/main/scripts/artifacts/samsungPrivacyDashboard.py
4. ALEAPP discreteNative.py — abrignoni/ALEAPP, https://github.com/abrignoni/ALEAPP/blob/main/scripts/artifacts/discreteNative.py
5. ALEAPP appops.py — abrignoni/ALEAPP, https://github.com/abrignoni/ALEAPP/blob/main/scripts/artifacts/appops.py
6. DiscreteRegistry.java — AOSP frameworks/base (GitHub 미러, main), https://raw.githubusercontent.com/aosp-mirror/platform_frameworks_base/main/services/core/java/com/android/server/appop/DiscreteRegistry.java
7. DiscreteRegistry.java — AOSP frameworks/base (GitHub 미러, android-12.0.0_r1), https://raw.githubusercontent.com/aosp-mirror/platform_frameworks_base/android-12.0.0_r1/services/core/java/com/android/server/appop/DiscreteRegistry.java
8. DiscreteRegistry.java — AOSP frameworks/base (GitHub 미러, android-13.0.0_r1), https://raw.githubusercontent.com/aosp-mirror/platform_frameworks_base/android-13.0.0_r1/services/core/java/com/android/server/appop/DiscreteRegistry.java
9. AppOpsRecentAccessPersistence.java — AOSP frameworks/base (GitHub 미러, main), https://raw.githubusercontent.com/aosp-mirror/platform_frameworks_base/main/services/core/java/com/android/server/appop/AppOpsRecentAccessPersistence.java
10. AppOpsService.java — AOSP frameworks/base (GitHub 미러, main), https://raw.githubusercontent.com/aosp-mirror/platform_frameworks_base/main/services/core/java/com/android/server/appop/AppOpsService.java
11. HistoricalRegistry.java — AOSP frameworks/base (GitHub 미러, main), https://raw.githubusercontent.com/aosp-mirror/platform_frameworks_base/main/services/core/java/com/android/server/appop/HistoricalRegistry.java
12. AppOpsService.java — AOSP frameworks/base (GitHub 미러, android-9.0.0_r1), https://raw.githubusercontent.com/aosp-mirror/platform_frameworks_base/android-9.0.0_r1/services/core/java/com/android/server/AppOpsService.java
13. The Binary Hick, "Snooping on Android 12's Privacy Dashboard", 2022-01-22, https://thebinaryhick.blog/2022/01/22/snooping-on-android-12s-privacy-dashboard/
14. Forensafe, "Android Application Operations", https://forensafe.com/blogs/android-application-operations.html
15. Mattia Epifani, "Beyond the Known: A Call to Forensic Research on Samsung Android Artifacts", digital-forensics.it, 2025-11-07, https://blog.digital-forensics.it/2025/11/beyond-known-call-to-forensic-research.html
16. AppOpsManager.java — AOSP frameworks/base (GitHub 미러, main), https://raw.githubusercontent.com/aosp-mirror/platform_frameworks_base/main/core/java/android/app/AppOpsManager.java
17. ALEAPP ilapfuncs.py (convert_unix_ts_to_utc) — abrignoni/ALEAPP, https://github.com/abrignoni/ALEAPP/blob/main/scripts/ilapfuncs.py
18. DiscreteRegistry.java — AOSP frameworks/base (GitHub 미러, android-14.0.0_r1), https://raw.githubusercontent.com/aosp-mirror/platform_frameworks_base/android-14.0.0_r1/services/core/java/com/android/server/appop/DiscreteRegistry.java
