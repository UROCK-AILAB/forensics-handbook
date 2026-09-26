---
title: "부팅과 종료 기록"
parent: "아티팩트 · 시스템 정보"
nav_order: 300
---

# 부팅과 종료 기록 (Boot·Shutdown)

Linux 는 부팅과 종료를 한 곳에 모아 두지 않고 저널·wtmp·감사 로그·파일 시스템 슈퍼블록·커널 메모리에 따로 남기므로, 이 기록들을 맞춰 보며 켜져 있던 구간을 복원합니다.

## 무엇을 기록하나 · 왜 생기나

systemd 저널은 항목마다 그 항목이 나온 부팅의 ID 를 붙이고, 부팅 완료·종료 시작·절전 같은 순간에는 정해진 메시지 ID 가 있는 항목을 남깁니다[2][3]. wtmp 에는 부팅할 때마다 `reboot` 라는 가짜 사용자가 로그인한 레코드가 쌓이고, 종료와 런레벨 변화도 들어갑니다[5][6]. systemd 환경에서는 systemd-update-utmp.service 가 재부팅과 종료 요청을 utmp·wtmp 와 감사 로그에 함께 씁니다[7]. ext4 슈퍼블록에는 마지막으로 마운트한 시각과 제대로 마운트 해제했는지가 남습니다[11]. 살아 있는 시스템에서는 커널이 부팅 시각과 부팅 ID 를 `/proc` 로 보여 줍니다[13][14].

이 기록들은 쓰는 주체가 다르고 사라지는 조건도 달라서, 하나가 지워지거나 비어 있어도 다른 쪽이 남는 경우가 많습니다. 어느 부팅에 어떤 일이 있었는지, 전원이 비정상으로 끊겼는지, 시스템이 꺼져 있던 공백이 있는지를 가릴 때 이 쪽의 기록을 씁니다.

## 위치와 버전별 차이

| 기록원 | 위치 | Ubuntu 24.04 LTS | RHEL 9 |
|---|---|---|---|
| systemd 저널 | `/var/log/journal/` 아래, 휘발 저장이면 `/run/log/journal/` 아래[18] | 공통 | 공통. 아래 메시지 ID 가 RHEL 9 카탈로그에도 같음[4] |
| wtmp | `/var/log/wtmp` (순환본 포함)[6][17] | 공통 | 공통 |
| wtmpdb | `/var/lib/wtmpdb/` 아래 SQLite[8] | 검체에 있는지 확인 | 검체에 있는지 확인 |
| 감사 로그 | `/var/log/audit/` 아래[19] | 검체에서 auditd 사용 여부 확인 | 검체에서 auditd 사용 여부 확인 |
| boot.log | `/var/log/boot.log` | 검체의 `/etc/rsyslog.d/` 에 `local7` 규칙이 있는지 확인 | rsyslog 기본 설정에 `local7.*` 를 이 파일로 보내는 규칙이 있음[10] |
| ext4 슈퍼블록 | 각 볼륨 시작에서 1024바이트 뒤[11] | 루트가 ext4 인 경우 | 루트 파일 시스템 종류를 검체에서 확인 |
| 라이브 | `/proc/stat` 의 `btime`, `/proc/uptime`, `/proc/sys/kernel/random/boot_id` | 같음 | 같음 |

저널이 디스크에 남는지, 기본 보존 한도가 얼마인지는 [systemd 저널](../../01-foundations/logging/systemd-journal/index.md) 에서 다룹니다. `/run/log/journal/` 에 둔 휘발 저널은 재부팅하면 사라지므로[18], 휘발 저장만 쓰는 시스템을 끈 뒤 만든 이미지에는 이전 부팅의 저널이 없습니다. `_RUNTIME_SCOPE=` 필드는 systemd 252 부터 있고, `initrd` 면 initrd 안에서, `system` 이면 실제 루트 파일 시스템으로 넘어간 뒤 만든 항목입니다[2].

## 구조

### 저널: 부팅 ID 와 카탈로그 메시지

`_BOOT_ID=` 는 그 항목이 만들어진 부팅의 커널 부팅 ID 이고 128비트 16진 문자열입니다[2]. `__MONOTONIC_TIMESTAMP=` 는 journald 가 항목을 받은 순간의 monotonic 시계 값(마이크로초)이고, 항목을 가리키는 주소로 쓰려면 `_BOOT_ID` 와 짝을 지어야 합니다[2]. `journalctl --list-boots` 는 부팅 순번(현재 부팅 기준 상대값), 부팅 ID, 그 부팅의 첫 메시지와 마지막 메시지 시각을 표로 냅니다[1]. 순번이 검체에서 어떻게 풀리는지는 [journalctl 로 읽기](../../01-foundations/logging/systemd-journal/journalctl.md) 에서 다룹니다.

부팅·종료와 관련된 카탈로그 메시지는 다음과 같습니다. 여덟 개 모두 RHEL 9 의 systemd 252 카탈로그에도 같은 ID 로 있습니다[3][4].

| `MESSAGE_ID` | 제목 | 뜻 |
|---|---|---|
| `f77379a8490b408bbe5f6940505a777b` | The journal has been started | 저널 프로세스가 파일을 열고 기록을 받기 시작함[3] |
| `b07a249cd024414a82dd00cd181378ff` | System start-up is now complete | 부팅 때 시작하도록 걸린 서비스가 모두 시작됨. 커널·initrd·사용자 공간에 걸린 시간을 `@KERNEL_USEC@`·`@INITRD_USEC@`·`@USERSPACE_USEC@` 마이크로초로 담음[3] |
| `7c8a41f37b764941a0e1780b1be2f037` | Initial clock synchronization | 그 부팅에서 처음 NTP 동기화를 얻고 시계 조정을 시작함[3] |
| `6bbd95ee977941e497c48be27c254128` | System sleep state @SLEEP@ entered | 절전 상태에 들어감[3] |
| `8811e6df2a8e40f58a94cea26f8ebf14` | System sleep state @SLEEP@ left | 절전 상태에서 나옴[3] |
| `98268866d1d54a499c4e98921d93bc40` | System shutdown initiated | 종료가 시작되어 모든 서비스를 멈추고 파일 시스템을 해제하는 중[3] |
| `d93fb3c9c24d451a97cea615ce59c00b` | The journal has been stopped | 저널 프로세스가 열린 파일을 모두 닫음[3] |
| `c7a787079b354eaaa9e77b371893cd27` | Time change | 시스템 시계를 바꿈[3]([호스트 이름·시간대·로캘](hostname-timezone.md)) |

### wtmp·wtmpdb

wtmp 에서 터미널 이름이 `~` 이고 사용자 이름이 `reboot` 나 `shutdown` 인 레코드가 재부팅과 종료입니다[5]. 레코드 종류 가운데 1(RUN_LVL)은 런레벨 변화, 2(BOOT_TIME)는 부팅 시각이고, 런레벨 레코드의 `ut_host` 칸에는 원격 호스트 대신 커널 판이 들어갑니다[5]. 그래서 런레벨 레코드를 차례로 보면 그때 돌던 커널 판까지 알 수 있습니다. 레코드의 바이트 배치는 [로그인 기록 파일 형식](../../01-foundations/logging/utmp-wtmp-format.md) 에서 다룹니다.

SQLite 형식인 wtmpdb 는 종류 번호가 1 BOOT_TIME, 2 RUNLEVEL 이라 utmp 와 1·2 가 뒤바뀌어 있습니다[8]. 두 형식을 한 표에 섞을 때는 번호가 아니라 이름으로 맞춥니다.

### 감사 로그

감사 이벤트 종류 1127 `SYSTEM_BOOT`, 1128 `SYSTEM_SHUTDOWN`, 1129 `SYSTEM_RUNLEVEL` 이 부팅·종료·런레벨 변화이고, 셋 다 발생원(ORIGIN)이 USER 인 메시지입니다[9]. 레코드 줄의 모양과 시각 칸은 [감사 로그 형식](../../01-foundations/logging/auditd-format.md) 에서 다룹니다.

### ext4 슈퍼블록

슈퍼블록은 볼륨 시작에서 1024바이트 뒤에 있습니다[11]. 부팅·종료와 관련된 칸은 다음과 같고, 오프셋은 슈퍼블록 시작 기준입니다[11]. 슈퍼블록 전체 구조는 [ext4](../../01-foundations/filesystem/ext4/index.md) 에서 다룹니다.

| 오프셋 | 크기 | 필드 | 뜻 |
|---|---|---|---|
| 0x2C | 4 | `s_mtime` | 마지막 마운트 시각, epoch 초 |
| 0x30 | 4 | `s_wtime` | 마지막 쓰기 시각, epoch 초 |
| 0x34 | 2 | `s_mnt_count` | 마지막 fsck 뒤 마운트 횟수 |
| 0x38 | 2 | `s_magic` | 0xEF53 |
| 0x3A | 2 | `s_state` | 0x0001 제대로 마운트 해제됨, 0x0002 오류 발견, 0x0004 고아 아이노드 복구 중 |
| 0x40 | 4 | `s_lastcheck` | 마지막 검사 시각, epoch 초 |
| 0x60 | 4 | `s_feature_incompat` | 0x4 가 켜져 있으면 복구가 필요한 파일 시스템(INCOMPAT_RECOVER) |
| 0x88 | 64 | `s_last_mounted` | 마지막으로 마운트한 폴더 |
| 0x274 | 1 | `s_wtime_hi` | `s_wtime` 의 상위 8비트 |
| 0x275 | 1 | `s_mtime_hi` | `s_mtime` 의 상위 8비트 |

### 라이브 시스템과 메모리

`/proc/stat` 의 `btime` 줄은 시스템이 부팅한 시각이고 UTC 기준 epoch 초입니다[13]. `/proc/uptime` 에는 부팅 뒤 흐른 초(절전한 시간 포함)와 idle 프로세스가 쓴 시간이 들어 있습니다[13]. `/proc/sys/kernel/random/boot_id` 는 처음 읽을 때 만든 UUID 이고 그 뒤로는 바뀌지 않습니다[14]. UAC 는 라이브 수집에서 `uptime` 과 `uptime -s`(yyyy-mm-dd HH:MM:SS) 결과를 받습니다[17].

메모리 이미지에서는 Volatility 3 의 `linux.boottime` 이 태스크의 시간 네임스페이스마다 부팅 시각을 계산하고, 타임라인에는 "System boot time for time namespace …" 로 냅니다[15]. 시간 네임스페이스가 없는 5.6 미만 커널에서도 동작합니다[15].

## 증거로서 의미

### 증명하는 것

저널의 부팅 ID 별 첫·마지막 메시지 시각은 그 부팅 동안 저널이 기록을 받은 범위입니다[1]. "System start-up is now complete" 는 부팅 때 걸린 서비스가 모두 시작된 시각이고, "System shutdown initiated" 는 종료가 시작된 시각입니다[3]. wtmp 의 `reboot` 레코드와 감사 로그의 `SYSTEM_BOOT` 는 systemd-update-utmp 같은 프로그램이 그 시각에 부팅을 기록했다는 뜻입니다[5][7][9]. ext4 슈퍼블록의 `s_state` 에 0x0001 이 없거나 `s_feature_incompat` 에 0x4 가 켜져 있으면, 이미지를 만든 순간 이 파일 시스템은 제대로 마운트 해제된 상태가 아니었습니다[11].

보고서에는 "이 부팅 ID 의 저널 기록은 이 시각부터 이 시각까지 있다", "이 시각에 종료가 시작되었다는 기록이 있다" 처럼 기록이 말하는 만큼만 씁니다.

### 증명하지 못하는 것

"System shutdown initiated" 는 종료가 시작되었다는 기록일 뿐 끝났다는 기록이 아닙니다[3]. "System start-up is now complete" 도 시스템이 한가해졌다는 뜻이 아니고, 서비스는 그 뒤에도 시작 작업을 계속할 수 있습니다[3]. 전원 차단이나 커널 패닉처럼 종료 기록 없이 끝난 부팅은 마지막 메시지 시각만 남고, 실제로 꺼진 시각은 그 뒤 어느 때입니다. wtmp 는 파일이 없으면 아무것도 기록하지 않으므로, wtmp 에 부팅이 없다고 부팅이 없었던 것은 아닙니다[6].

`s_state` 가 깨끗하지 않은 이유는 전원이 끊긴 경우만이 아닙니다. 켜져 있는 시스템에서 디스크 이미지를 떴을 때도 같은 상태로 보일 가능성이 있으므로, 이미지를 어떻게 만들었는지와 함께 판단합니다. `s_mtime` 은 마지막 마운트 시각이라 재마운트로도 바뀔 수 있어 부팅 시각과 같다고 단정하지 않습니다.

## 시각 해석

| 값 | 기준 | 바뀌는 때 |
|---|---|---|
| 저널 `__REALTIME_TIMESTAMP` | UTC epoch 마이크로초 | journald 가 항목을 받을 때[2] |
| 저널 `__MONOTONIC_TIMESTAMP` | monotonic 시계 마이크로초, `_BOOT_ID` 와 짝 | 같음[2] |
| wtmp `ut_tv` | UTC epoch 초·마이크로초 | 레코드를 쓸 때[5] |
| ext4 `s_mtime`·`s_wtime` | UTC epoch 초, 상위 8비트는 0x275·0x274 | 마운트할 때, 슈퍼블록을 쓸 때[11] |
| `/proc/stat` `btime` | UTC epoch 초 | 부팅할 때[13] |
| boot.log | rsyslog 가 쓰는 줄의 시각 형식 | 메시지를 받을 때 |

저널 시각을 바꾸는 법은 [journalctl 로 읽기](../../01-foundations/logging/systemd-journal/journalctl.md), epoch 값을 날짜로 바꾸는 법은 [Linux 의 시각 값](../../01-foundations/value-decoding/time-values.md), syslog 줄의 시각은 [syslog 형식과 rsyslog](../../01-foundations/logging/syslog-rsyslog.md) 에서 다룹니다.

부팅 직후에는 시계가 아직 NTP 로 맞춰지지 않았을 수 있습니다. 이 구간의 벽시계 시각은 "Initial clock synchronization" 메시지[3] 앞뒤를 비교해 어긋남을 가늠하고, 같은 부팅 안에서는 monotonic 값으로 순서를 잡습니다. `journalctl --header` 는 시계가 틀린 채 부팅해 순서가 어긋난 항목을 찾는 데 쓸모가 있습니다[1].

## 함정과 한계

- `/proc/uptime` 은 절전한 시간을 포함합니다[13]. 반면 `dmesg` 가 사람이 읽는 시각으로 바꾼 값은 절전·복귀 뒤에 맞지 않을 수 있습니다[16]. 커널 로그 시각은 [커널 로그](kernel-log.md) 에서 다룹니다.
- wtmp 와 wtmpdb 는 부팅·런레벨 종류 번호가 서로 뒤바뀌어 있습니다[8].
- 저널 순번 `-b -1` 은 저널 끝에서 센 값이라, 다른 기계의 저널을 볼 때는 `--list-boots` 로 부팅 ID 를 먼저 뽑고 그 ID 로 고릅니다[1].
- Volatility 3 `linux.boottime` 은 시간 네임스페이스마다 부팅 시각을 따로 냅니다[15]. 결과가 여러 줄이면 시간 네임스페이스를 따로 둔 프로세스(컨테이너 등)가 있을 가능성이 있습니다.
- journald 는 비정상으로 멈췄거나 파일이 손상된 것을 알아채면 그 파일 이름 끝을 `.journal~` 로 바꾸고 새 파일에 씁니다[18]. 자세한 조건은 [손상·삭제된 저널](../../01-foundations/logging/systemd-journal/corruption.md) 에서 다룹니다.
- wtmp 는 로그 순환 대상이라 오래된 부팅은 `wtmp.1`·압축본에 있습니다([로그 순환](../../01-foundations/logging/logrotate.md)). 저널도 보존 한도에 따라 오래된 파일을 스스로 지우므로, 첫 부팅 기록은 남아 있지 않을 가능성이 큽니다.

## 직접 분석해 보기

### 헥스로 한 번: ext4 슈퍼블록

아래는 명세로 만든 슈퍼블록 일부입니다(만든 예시). 오프셋은 파티션 시작 기준이고, 부팅·종료와 관계없는 칸은 0 으로 두었습니다.

```
00000420: 0000 0000 0000 0000 0000 0000 94a5 6869  ..............hi
00000430: ed26 6969 0c00 0000 53ef 0000 0000 0000  .&ii....S.......
00000460: c602 0000 0000 0000 0000 0000 0000 0000  ................
00000480: 0000 0000 0000 0000 2f00 0000 0000 0000  ......../.......
```

1. 0x438(슈퍼블록 0x38)의 `53 ef` 가 매직 0xEF53 이라서 이 자리가 슈퍼블록입니다.
2. 0x42C 의 `94 a5 68 69` 는 리틀 엔디언 0x6968A594 = 1768465812 초이고, `s_mtime` 은 2026-01-15 08:30:12 UTC 입니다. 0x430 의 `ed 26 69 69` 는 1768498925 초이고, `s_wtime` 은 같은 날 17:42:05 UTC 입니다. 0x674·0x675 의 상위 바이트가 0 이면 이 값 그대로 씁니다.
3. 0x434 의 `0c 00` 은 마지막 fsck 뒤 12번 마운트했다는 뜻입니다.
4. 0x43A 의 `s_state` 가 `00 00` 이라 0x0001(제대로 마운트 해제됨) 비트가 없습니다. 0x460 의 `s_feature_incompat` 0x2C6 에는 0x4(INCOMPAT_RECOVER)가 들어 있어 복구가 필요한 상태입니다.
5. 0x488 의 `2f` 는 마지막으로 `/` 에 마운트했다는 뜻이라 루트 파일 시스템입니다.

이 예시는 08:30 에 루트를 마운트했고 17:42 에 슈퍼블록을 마지막으로 썼으며, 제대로 해제하지 않은 채 이미지가 만들어진 모습입니다. 17:42 뒤에 종료 기록이 저널에 있는지 맞춰 봅니다.

### 공개 도구로 한 번

```
journalctl -D /mnt/evidence/var/log/journal --list-boots
journalctl -D /mnt/evidence/var/log/journal -o short-iso MESSAGE_ID=98268866d1d54a499c4e98921d93bc40
last -f wtmp -F -w -x
fsstat -o 2048 disk.raw
```

첫 줄은 검체 저널의 부팅 목록을 뽑고, 둘째 줄은 종료 시작 메시지만 거릅니다. 다른 메시지 ID 로 바꿔 부팅 완료·절전을 차례로 뽑을 수 있습니다. `last -x` 는 종료와 런레벨 변화 레코드까지 보여 주고[6], UAC 도 라이브에서 `last -a -F`·`last -i` 와 순환본을 `-f` 로 돌린 결과를 받습니다[17]. TSK `fsstat` 는 ext4 에서 `Last Written at`, `Last Checked at`, `Last Mounted at`, `Unmounted properly` 또는 `Unmounted Improperly`, `Last mounted on` 을 찍고, `InCompat Features:` 줄에 `Needs Recovery` 를 표시합니다[12]. 메모리 이미지는 Volatility 3 `linux.boottime` 으로 부팅 시각을 뽑습니다[15].

## 교차 검증

| 맞춰 볼 기록 | 확인할 것 |
|---|---|
| 저널 `--list-boots` ↔ wtmp `reboot` 레코드 | 부팅 수와 시각이 같은지. 한쪽에만 있는 부팅은 파일 삭제·순환·휘발 저장 가능성 |
| 저널 종료 메시지 ↔ wtmp `shutdown` ↔ 감사 로그 1128 | 정상 종료가 세 곳에 함께 남았는지 |
| 저널 마지막 메시지 ↔ ext4 `s_wtime`·`s_state` | 종료 기록 없이 끝난 부팅의 마지막 흔적 |
| 저널 부팅 첫 메시지 ↔ ext4 `s_mtime` ↔ [커널 로그](kernel-log.md) 첫 줄 | 부팅 시각의 일치 |
| wtmp 런레벨 레코드의 커널 판 ↔ [배포판과 버전](os-release.md) | 그 부팅이 어느 커널이었는지 |

종료 메시지가 없는 부팅이 있고, 저널 폴더에 `.journal~` 파일이 있으며, 슈퍼블록에 INCOMPAT_RECOVER 가 켜져 있으면 비정상 종료였을 가능성이 높아집니다. 사람이 시계를 바꿨는지는 [시각을 조작했나](../../04-scenarios/insider/time-manipulation.md), 여러 기록을 시간순으로 합치는 법은 [타임라인 만들기](../../03-techniques/analysis/timeline.md) 에서 다룹니다. 로그인 세션과 부팅을 함께 보는 법은 [로그인 기록](../logins/wtmp-btmp-lastlog.md) 에서 다룹니다.

## 실습

NIST CFReDS 등에 공개된 Linux 디스크 이미지로 다음 질문을 풀어 봅니다.

1. 저널에 남은 부팅은 몇 번이고, 가장 이른 부팅의 첫 메시지 시각은 언제인가?
2. 종료 시작 메시지(`98268866…`)가 없는 부팅이 있는가? 있다면 그 부팅의 마지막 메시지는 무엇인가?
3. wtmp 의 `reboot` 레코드 수와 저널 부팅 수가 같은가? 다르면 어느 쪽이 먼저 끊기는가?
4. 루트 파일 시스템 슈퍼블록의 `s_mtime`·`s_wtime`·`s_state` 는 마지막 부팅의 저널 기록과 맞는가?
5. 부팅마다 wtmp 런레벨 레코드에 적힌 커널 판이 바뀐 시점이 있는가?

## 참고 문헌

1. systemd, man/journalctl.xml. https://github.com/systemd/systemd/blob/main/man/journalctl.xml
2. systemd, man/systemd.journal-fields.xml. https://github.com/systemd/systemd/blob/main/man/systemd.journal-fields.xml
3. systemd, catalog/systemd.catalog.in. https://github.com/systemd/systemd/blob/main/catalog/systemd.catalog.in
4. Red Hat, systemd-rhel9 source-git, catalog/systemd.catalog.in. https://github.com/redhat-plumbers/systemd-rhel9/blob/main/catalog/systemd.catalog.in
5. utmp(5), Linux man-pages. https://github.com/mkerrisk/man-pages/blob/master/man5/utmp.5
6. util-linux, last(1). https://github.com/util-linux/util-linux/blob/master/login-utils/last.1.adoc
7. systemd, man/systemd-update-utmp.service.xml. https://github.com/systemd/systemd/blob/main/man/systemd-update-utmp.service.xml
8. fox-it dissect.target, dissect/target/plugins/os/unix/log/utmp.py. https://github.com/fox-it/dissect.target/blob/main/dissect/target/plugins/os/unix/log/utmp.py
9. linux-audit, audit-documentation specs/messages/message-dictionary.csv. https://github.com/linux-audit/audit-documentation/blob/main/specs/messages/message-dictionary.csv
10. CentOS Stream 9 rsyslog 패키지, rsyslog.conf. https://gitlab.com/redhat/centos-stream/rpms/rsyslog/-/blob/c9s/rsyslog.conf
11. Linux kernel, Documentation/filesystems/ext4/super.rst·blockgroup.rst. https://github.com/torvalds/linux/tree/master/Documentation/filesystems/ext4
12. The Sleuth Kit, tsk/fs/ext2fs.cpp. https://github.com/sleuthkit/sleuthkit/blob/develop/tsk/fs/ext2fs.cpp
13. proc(5), Linux man-pages. https://github.com/mkerrisk/man-pages/blob/master/man5/proc.5
14. Linux kernel, Documentation/admin-guide/sysctl/kernel.rst. https://github.com/torvalds/linux/blob/master/Documentation/admin-guide/sysctl/kernel.rst
15. Volatility 3, volatility3/framework/plugins/linux/boottime.py. https://github.com/volatilityfoundation/volatility3/blob/develop/volatility3/framework/plugins/linux/boottime.py
16. util-linux, dmesg(1). https://github.com/util-linux/util-linux/blob/master/sys-utils/dmesg.1.adoc
17. UAC, artifacts/live_response/system/last.yaml·uptime.yaml. https://github.com/tclahr/uac/tree/main/artifacts
18. systemd, man/systemd-journald.service.xml. https://github.com/systemd/systemd/blob/main/man/systemd-journald.service.xml
19. ForensicArtifacts, artifacts/data/linux.yaml. https://github.com/ForensicArtifacts/artifacts/blob/main/artifacts/data/linux.yaml
