---
title: "초기화"
parent: "증거를 없애려 했나"
grand_parent: "시나리오 · 행위 재구성"
nav_order: 1650
---

# 초기화 (Factory Reset)

기기를 공장 초기화했는지, 했다면 언제쯤인지를 판별하는 흐름을 정리합니다. 소스에 나온 동작은 현행 AOSP(frameworks/base 의 main 가지) 기준이고, 버전에 따라 다를 수 있습니다. 초기화 흔적 하나하나의 구조는 [초기화 흔적 (Factory Reset)](../../../02-artifacts/system-account/factory-reset.md) 아티팩트 페이지에 있고, 이 페이지는 그 흔적을 조사 순서로 엮는 데 집중합니다.

## 조사 질문

"이 기기를 초기화한 적이 있는가, 있다면 언제쯤인가, 초기화 이전 기록이 어디에든 남았는가" 를 묻습니다. 초기화는 사용자 데이터 영역을 지우는 동작이라서 `/data` 아래 기록은 초기화 이전 것이 남지 않는다고 보는 것이 일반적입니다. 파일 단위로 무엇이 남는지는 실제 기기로 확인해야 합니다. 그래서 답은 대개 "지금 남은 기록이 언제부터 시작하는가" 에서 거꾸로 찾게 되고, 이 판단은 해석입니다.

## 먼저 확인할 것

- **OS 버전과 빌드**: 복구 모드의 동작과 기록 위치가 기기마다 달라서 [기기 정보와 빌드](../../../02-artifacts/system-account/device-build.md) 부터 봅니다. `/cache` 파티션이 없는 기기(A/B 기기 등)에서 복구 기록이 어디에 남는지는 실제 기기에서 확인합니다. A/B 구조는 [파티션과 저장 영역](../../../01-foundations/storage/partitions/index.md) 에 있습니다.
- **기기 시각이 맞았는지**: 초기화 사유에 붙는 시각이 기기 시스템 시계 기준이라서, 시각을 바꾼 흔적이 있으면 [시각 바꾸기](time-change.md) 를 먼저 봅니다.
- **사용자와 관리 여부**: 회사 폰처럼 관리 기기라면 초기화 제한이 걸려 있었을 수 있습니다(아래 "시스템이 초기화를 처리하는 방식" 참고).
- **수집 범위**: adb 일반 권한 출력만 있는지, 전체 파일 시스템 사본이 있는지에 따라 볼 수 있는 곳이 크게 다릅니다. 방법별 차이는 [모바일 증거 확보](../../../03-techniques/acquisition/mobile-acquisition/index.md) 에 있습니다.

## 시스템이 초기화를 처리하는 방식

초기화 요청은 `RecoverySystem.rebootWipeUserData()` 가 받아서 복구 모드(recovery)에 명령을 넘기고 재부팅합니다 [1]. 넘기는 인자는 아래와 같습니다 [1].

```
--wipe_data
--reason=<사유>,<시각>        (사유가 있을 때)
--locale=<언어 태그>
--shutdown_after              (필요할 때)
--keep_memtag_mode            (필요할 때)
```

사유 뒤의 시각은 `yyyy-MM-ddTHH:mm:ssZ` 형식이고 `System.currentTimeMillis()`, 곧 기기 시스템 시계로 만든 값이며, 사유 문자열 속의 널 문자와 줄바꿈은 `?` 로 바뀝니다 [1]. 이 문자열이 복구 로그에 그대로 남는지는 실제 기기의 복구 기록에서 확인합니다.

시스템은 초기화 전에 `android.intent.action.MASTER_CLEAR_NOTIFICATION` 방송을 보내고, 이 방송을 받으려면 `android.Manifest.permission.MASTER_CLEAR` 권한이 필요합니다 [1]. 사용자 제한 `UserManager.DISALLOW_FACTORY_RESET` 이 걸려 있으면 강제(force) 요청이 아닌 한 "Wiping data is not allowed for this user." 로 거부합니다 [1]. 관리 기기에서 초기화 흔적이 나왔다면 이 제한이 그때 걸려 있었는지를 함께 따져 볼 만합니다.

복구 기록의 경로 상수는 다음과 같습니다 [1].

| 상수 | 값 |
|---|---|
| RECOVERY_DIR | `/cache/recovery` |
| LOG_FILE | `/cache/recovery/log` |
| LAST_PREFIX | `last_` |
| LAST_INSTALL_PATH | `last_install` |

부팅이 끝나면 `handleAftermath()` 가 `/cache/recovery` 안에서 `last_` 로 시작하는 파일과 `last_install` 을 남기고(업데이트 패키지를 남겨 둘 때는 블록 맵·uncrypt 파일도 남김) 나머지를 지웁니다 [1]. 그래서 초기화 뒤에 이 폴더를 수집했다면 `last_` 로 시작하는 파일이 살펴볼 대상입니다. 그 안에 무엇이 어떤 형식으로 적히는지와 복구 모드가 어떤 파티션을 어떻게 지우는지는 수집한 파일을 직접 열어 확인합니다.

## 볼 아티팩트와 순서

| 순서 | 아티팩트 | 알려 주는 것 | 링크 |
|---|---|---|---|
| 1 | `dumpsys user` 의 사용자 항목 | 사용자 생성·로그인·잠금 해제 시각 필드 | [사용자와 프로필](../../../02-artifacts/system-account/users-profiles.md) |
| 2 | 설치된 앱 목록과 설치 시각 | 사용자가 설치한 앱의 수와 설치 시각이 몰린 시점 | [설치된 앱](../../../02-artifacts/app-usage/packages/index.md) |
| 3 | 설정 값 | 초기 설정 완료·부팅 횟수와 관련된 키 | [설정 값](../../../02-artifacts/system-account/settings.md) |
| 4 | 각 기록의 가장 오래된 시각 | 남은 기록이 시작하는 시점 | [타임라인 작성](../../../03-techniques/analysis/timeline/index.md) |
| 5 | `/cache/recovery` 의 `last_` 파일 | 복구 모드 기록(수집했을 때만) | [초기화 흔적](../../../02-artifacts/system-account/factory-reset.md) |
| 6 | 계정·클라우드 백업 | 초기화 이전 자료가 기기 밖에 남았는지 | [클라우드 데이터](../../../03-techniques/acquisition/cloud-data.md) |

### adb 일반 권한으로 보이는 필드

adb 일반 권한 출력에서 초기화와 관련해 볼 필드는 아래와 같습니다.

| 출력 | 필드·키 |
|---|---|
| `dumpsys user` 사용자 항목 | `Created:`, `Last logged in:`, `Last logged in fingerprint:`, `Start time:`, `Unlock time:`, `Last entered foreground:`, `Has profile owner:`, `Restrictions:`, `Device policy restrictions:`, `Effective restrictions:` |
| `dumpsys package` 첫 부분 | `Database versions:` 아래 `Internal:`·`External:`, `sdkVersion`, `databaseVersion`, `buildFingerprint`, `fingerprint` |
| `settings global` | `boot_count`, `device_provisioned`, `euicc_factory_reset_timeout_millis`, `lock_reset_profile` |
| `settings secure` | `user_setup_complete`, `rampart_is_reset_by_at_command` |
| `dumpsys batterystats` | "Battery History" 첫 줄 가까이의 `RESET:TIME:` 줄 |

주 사용자(`isPrimary=true`)의 `Created:` 는 `<unknown>` 으로 나올 수 있어서 이 필드만으로 초기화 시점을 읽지 않습니다. `boot_count` 가 초기화 이후의 부팅 횟수인지는 실제 기기로 확인해야 합니다. `rampart_is_reset_by_at_command` 와 `lock_reset_profile` 은 삼성이 추가한 키로 보이며, 뜻이 정해져 있지 않으므로 보고서에는 값만 옮기고 뜻을 단정하지 않습니다.

## 분석 흐름

1. 빌드 정보와 수집 범위를 적어 두고, `/cache/recovery` 를 수집했는지 확인합니다.
2. `dumpsys user` 의 시각 필드와 `Restrictions:` 필드를 기록합니다. 초기화 제한이 이 필드에 어떤 이름으로 나오는지 단정하지 않고, 필드 값은 원문 그대로 옮겨 둡니다.
3. 사용자 설치 앱의 설치 시각을 모아 한 시점에 몰려 있는지 봅니다. 초기화 직후라면 사용자 설치 앱이 적거나 설치 시각이 모두 최근일 것이라는 판단은 해석입니다.
4. 앱 사용 기록, 사진, 메신저 DB, 와이파이·블루투스 기록 등에서 각각 가장 오래된 시각을 뽑아 한 표에 놓습니다. 여러 기록이 같은 무렵에서 시작하면 그 무렵이 초기화 시점의 단서가 됩니다(해석).
5. `last_` 로 시작하는 복구 기록 파일이 있으면 내용과 파일 시각을 옮겨 적고, 4단계의 시점과 맞춰 봅니다.
6. 초기화 이전 자료가 계정 백업이나 클라우드에 남았는지 따로 확인합니다. 구글 계정·삼성 클라우드 백업에 무엇이 남는지는 [구글 백업](../../../02-artifacts/mail-cloud/google-backup.md) 과 [삼성 클라우드와 원드라이브](../../../02-artifacts/mail-cloud/samsung-cloud-onedrive.md) 페이지를 따라갑니다.

## 흔한 오판

**가장 오래된 기록을 곧 초기화 시각으로 적는 경우.** 기록마다 보관 기간이 달라서 오래된 기록이 스스로 지워졌을 수도 있고, 새로 산 기기도 기록이 최근에서 시작합니다. 여러 기록의 시작점이 한 무렵에 모이는지, 그리고 그보다 앞선 기록이 기기 밖(클라우드·다른 기기)에 있는지를 함께 봐야 "그 무렵 이후의 기록만 남았다" 까지 말할 수 있습니다.

**`RESET:TIME:` 줄을 초기화로 읽는 경우.** batterystats 의 이 줄은 배터리 통계를 비운 시각이고, 초기화와 별개일 수 있습니다. 자세한 구조는 [배터리 사용 기록](../../../02-artifacts/app-usage/batterystats.md) 에 있습니다.

**`Created:` 가 `<unknown>` 이라서 초기화가 없었다고 보는 경우.** 주 사용자의 이 필드는 `<unknown>` 으로 나올 수 있으니, 이 필드 값으로 초기화가 있었는지 없었는지 판단하지 않습니다.

**초기화 사유 속 시각을 실제 시각으로 믿는 경우.** 사유에 붙는 시각은 기기 시스템 시계 기준이라서 [1] 기기 시각을 바꿔 둔 상태였다면 그만큼 어긋납니다.

**초기화했으니 복구할 것이 없다고 포기하는 경우.** 기기 밖, 곧 클라우드·상대방 기기·PC 백업에 같은 자료가 있을 수 있습니다. 공장 초기화 보호(FRP)에 쓰는 계정 정보가 남는 영역은 이 페이지에서 다루지 않습니다.

## 보고서 문장 예

기록으로 확인되는 만큼만 씁니다. "피의자가 (날짜)에 증거를 없애려고 초기화했다" 는 기록으로 확인되는 것 이상을 적은 문장입니다.

> 사용자가 설치한 앱의 설치 시각과 앱 사용 기록, 사진, 와이파이 접속 기록의 가장 오래된 시각이 모두 기기 시계 기준 (날짜) 무렵에서 시작합니다. 이 기기에는 그보다 앞선 기록이 남아 있지 않으며, 이는 그 무렵 기기를 초기화했거나 새로 쓰기 시작한 경우와 맞지만 두 경우를 이 기록만으로 가릴 수는 없습니다.

## 함께 볼 페이지

- 초기화 흔적 아티팩트 설명은 [초기화 흔적 (Factory Reset)](../../../02-artifacts/system-account/factory-reset.md), 사용자 데이터 영역의 암호화 구조는 [저장 공간 암호화](../../../01-foundations/storage/encryption/index.md) 에 있습니다.
- 초기화 대신 앱이나 자료만 지운 경우는 [앱 지우기](app-removal.md) 와 [메시지·사진 지우기](content-deletion.md) 를 봅니다.
- 삼성 기기에서 초기화 뒤에도 남는 초기화 요청 기록과 전원·재부팅 사유는 [삼성 전원·재부팅·초기화 로그](../../../02-artifacts/samsung/power-reset-logs.md) 에 있습니다.
- 이 묶음 전체의 길잡이는 [증거를 없애려 했나](index.md) 입니다.
- `dumpsys` 출력을 받는 방법과 읽는 법은 [dumpsys 출력](../../../02-artifacts/logs/dumpsys.md) 에 있습니다.

## 참고 문헌

1. RecoverySystem.java — AOSP frameworks/base (GitHub 미러, main), https://raw.githubusercontent.com/aosp-mirror/platform_frameworks_base/main/core/java/android/os/RecoverySystem.java
