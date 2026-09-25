---
title: "프로세스 회계"
parent: "아티팩트 · 실행 흔적"
nav_order: 470
---

# 프로세스 회계 (acct·pacct)

프로세스 회계 (process accounting) 를 켜 두면 커널이 프로세스가 끝날 때마다 명령 이름·사용자·시작 시각·실행 시간을 64바이트 레코드 하나로 회계 파일(`pacct`)에 덧붙입니다[1][2][3].

## 무엇을 기록하나 · 왜 생기나

커널을 `CONFIG_BSD_PROCESS_ACCT` 옵션으로 빌드하고 `acct(2)` 시스템 콜에 파일 이름을 넘기면 회계가 켜지고, NULL 을 넘기면 꺼집니다[1][2]. 회계를 켜려면 `CAP_SYS_PACCT` 권한이 필요합니다[2]. 켜져 있는 동안 커널은 프로세스가 끝날 때마다 그 프로세스의 정보를 레코드 하나로 파일 끝에 덧붙입니다[1][2]. 그래서 레코드는 시작 순서가 아니라 끝난 순서로 쌓입니다[1]. Linux 2.6.10 부터는 스레드가 여러 개인 프로세스도 마지막 스레드가 끝날 때 레코드 하나만 남깁니다[1].

레코드에 들어가는 명령 이름은 마지막으로 실행한 프로그램의 파일 이름 부분(`comm`)뿐입니다[1][5]. 전체 경로와 명령줄 인수는 남지 않습니다. 셸 기록이나 감사 로그처럼 "무엇을 입력했는가" 를 보여 주는 기록이 아니라, "어떤 이름의 프로세스가 누구 권한으로 언제부터 얼마 동안 돌다가 어떻게 끝났는가" 를 보여 주는 기록입니다.

Debian·Ubuntu 계열과 RHEL 9 에서 회계 파일은 따로 까는 회계 패키지(`acct`, `psacct`)가 만들고 그 패키지의 서비스가 켭니다[8][9]. 두 패키지 모두 설치할 때 빈 `pacct` 파일을 만들어 두므로[8][9], 파일이 있으면 패키지를 깐 것이고 파일에 레코드가 쌓여 있으면 회계가 실제로 켜져 있던 것입니다.

## 위치와 버전별 차이

두 계열은 패키지 이름, 파일 위치, 권한, 순환 방식이 다릅니다[8][9].

| 항목 | Debian·Ubuntu 계열 (`acct` 패키지) | RHEL 9 (`psacct` 패키지) |
|---|---|---|
| 회계 파일 | `/var/log/account/pacct` | `/var/account/pacct` |
| 서비스 | `acct.service` 가 `/usr/sbin/accton /var/log/account/pacct` 로 켜고 `accton off` 로 끔 | `psacct.service` 가 `accton-create` 로 파일을 만든 뒤 `/usr/sbin/accton /var/account/pacct` 로 켜고, reload 때 다시 `accton`, stop 때 `accton off` |
| 서비스 시작 조건 | `ConditionPathExists=/var/log/account` | `ConditionPathExists=/var/account` |
| 파일 권한 | 0640, root:adm | 0600, root:root |
| 순환 | `/etc/cron.daily/acct` 가 `savelog -g adm -m 0640 -u root -c ${ACCT_LOGGING}` 로 돌리고 서비스를 다시 시작 | `/etc/logrotate.d/psacct`: daily, rotate 31, compress, delaycompress, notifempty, `create 0600 root root`, 순환 뒤 서비스 reload |
| 보관 설정 | `/etc/default/acct` 의 `ACCT_LOGGING="30"`, 켜기 설정 `ACCT_ENABLE="1"` | logrotate 의 `rotate 31` |
| `sa` 요약 파일 | 검체의 `/var/log/account/` 목록으로 확인 | `/var/account/savacct`, `/var/account/usracct` |

RHEL 9 의 `psacct` 에는 `accton`, `sa`, `lastcomm`, `dump-acct`, `dump-utmp`, `ac` 가 들어 있습니다[8]. Debian 계열에서 `savelog` 가 순환한 파일의 이름은 검체의 `/var/log/account/` 목록으로 확인합니다. RHEL 9 의 순환 파일 이름과 `delaycompress` 가 압축을 한 번 미루는 방식은 [로그 순환](../../01-foundations/logging/logrotate.md) 에서 다룹니다.

Debian 계열은 `/etc/cron.daily/acct` 가 순환을 마친 뒤 매일 `invoke-rc.d acct restart` 로 서비스를 다시 시작하므로, 부팅 뒤 서비스를 한 번 멈춘 것만으로는 회계가 계속 꺼져 있지 않습니다[9]. 그래서 서비스를 멈춘 흔적이 있어도 다음 cron.daily 실행 뒤에는 회계가 다시 켜졌을 수 있습니다.

수집 도구가 이 파일을 알아서 챙기는지도 봐야 합니다. UAC 의 `acct.yaml` 은 FreeBSD·NetBSD·OpenBSD 의 `/var/account/` 아래 파일(`acct*`, `usracct`, `savacct`)과 Solaris 의 `/var/adm/` 아래 파일(`pacct*`, `acct`, `exacct`)만 정의하고 Linux 항목은 없습니다[10]. `/var/log` 를 통째로 모으면 Debian 계열의 `/var/log/account/` 는 함께 들어오지만, RHEL 의 `/var/account/` 는 따로 지정해서 모아야 합니다.

## 구조

### 판 구별

레코드 모양은 커널 빌드 옵션에 따라 둘로 나뉩니다. `CONFIG_BSD_PROCESS_ACCT_V3` 로 빌드하면 3판 (`struct acct_v3`) 을 쓰고, 아니면 2판 (`struct acct`, m68k 는 1판) 을 씁니다[4]. 두 판 모두 레코드 하나가 64바이트이고 파일 머리는 따로 없어서, 파일 크기는 64의 배수입니다(아래 오프셋은 커널 헤더의 구조체로 계산한 값입니다)[3].

판은 레코드 둘째 바이트 `ac_version` 으로 가립니다. 커널은 여기에 판 번호와 바이트 순서 표시(빅엔디언이면 0x80, 리틀엔디언이면 0x00)를 OR 해서 넣습니다[3][5]. x86_64 검체라면 둘째 바이트가 `03` 이면 3판, `02` 이면 2판입니다. 어느 판으로 빌드했는지는 검체의 `/boot/config-*` 에서 `CONFIG_BSD_PROCESS_ACCT_V3` 로도 확인할 수 있습니다.

### 3판 레코드 (acct_v3)

| 오프셋 | 크기 | 필드 | 뜻 |
|---|---|---|---|
| 0 | 1 | `ac_flag` | 플래그(아래 표) |
| 1 | 1 | `ac_version` | 판 번호와 바이트 순서 |
| 2 | 2 | `ac_tty` | 제어 터미널 장치 번호, 없으면 0 |
| 4 | 4 | `ac_exitcode` | 종료 상태 |
| 8 | 4 | `ac_uid` | 실제 UID (real UID) |
| 12 | 4 | `ac_gid` | 실제 GID |
| 16 | 4 | `ac_pid` | 프로세스 ID |
| 20 | 4 | `ac_ppid` | 부모 프로세스 ID |
| 24 | 4 | `ac_btime` | 시작 시각(epoch 초) |
| 28 | 4 | `ac_etime` | 경과 시간, IEEE 754 단정밀도 실수 |
| 32 | 2 | `ac_utime` | 사용자 모드 CPU 시간(comp_t) |
| 34 | 2 | `ac_stime` | 커널 모드 CPU 시간(comp_t) |
| 36 | 2 | `ac_mem` | 메모리(kB, comp_t) |
| 38 | 2 | `ac_io` | 쓰지 않음 |
| 40 | 2 | `ac_rw` | 쓰지 않음 |
| 42 | 2 | `ac_minflt` | 가벼운 페이지 폴트 수(comp_t) |
| 44 | 2 | `ac_majflt` | 무거운 페이지 폴트 수(comp_t) |
| 46 | 2 | `ac_swaps` | 쓰지 않음 |
| 48 | 16 | `ac_comm` | 명령 이름, NUL 로 끝남 |

필드 배치는 커널 헤더 `include/uapi/linux/acct.h` 를 따르고[3], `ac_io`·`ac_rw`·`ac_swaps` 는 커널이 채우지 않아 늘 0입니다[1][5]. `ac_mem` 은 이름과 달리 평균값이 아니라 프로세스가 끝날 때 잡혀 있던 가상 메모리 영역 크기를 1024로 나눈 값입니다[5].

### 2판 레코드 (acct)

2판은 앞쪽에 16비트 UID·GID 를 두고, 뒤쪽에 32비트 UID·GID 를 한 번 더 둡니다[3]. PID 와 부모 PID 칸이 없다는 점이 3판과 가장 크게 다릅니다.

| 오프셋 | 필드 | 오프셋 | 필드 |
|---|---|---|---|
| 0 | `ac_flag` (1) | 26 | `ac_majflt` (2) |
| 1 | `ac_version` (1) | 28 | `ac_swaps` (2) |
| 2 | `ac_uid16` (2) | 30 | `ac_ahz` (2) |
| 4 | `ac_gid16` (2) | 32 | `ac_exitcode` (4) |
| 6 | `ac_tty` (2) | 36 | `ac_comm` (17) |
| 8 | `ac_btime` (4) | 53 | `ac_etime_hi` (1) |
| 12 | `ac_utime` (2) | 54 | `ac_etime_lo` (2) |
| 14 | `ac_stime` (2) | 56 | `ac_uid` (4) |
| 16 | `ac_etime` (2) | 60 | `ac_gid` (4) |
| 18~24 | `ac_mem`·`ac_io`·`ac_rw`·`ac_minflt` (각 2) | | |

`acct(5)` 매뉴얼에 실린 `struct acct` 는 C 라이브러리 헤더 모양이라 커널 헤더와 필드 배치가 다릅니다[1][3]. 오프셋은 커널 헤더로 셉니다. 2판의 `ac_ahz` 에는 시간 단위(초당 틱 수)가 들어 있습니다[3][5].

### 플래그와 comp_t

| 비트 | 이름 | 켜지는 경우 |
|---|---|---|
| 0x01 | `AFORK` | fork 한 뒤 exec 없이 끝남 |
| 0x02 | `ASU` | 슈퍼유저 권한을 썼음 |
| 0x08 | `ACORE` | 코어 덤프를 남김 |
| 0x10 | `AXSIG` | 시그널을 받고 끝남 |

커널이 실제로 켜는 비트는 이 넷입니다[3][5]. 헤더에는 `ACOMPAT`(0x04)와 `AGROUP`(0x20)도 정의되어 있지만 `kernel/acct.c` 가 켜지 않습니다[3][5].

`comp_t` 는 16비트 값으로, 위 3비트가 8진 지수이고 아래 13비트가 가수입니다[1][3]. 정수로 바꾸는 식은 `v = (c & 0x1fff) << (((c >> 13) & 0x7) * 3)` 입니다[1]. CPU 시간과 경과 시간의 단위는 틱 (clock tick) 이고, 3판은 초당 100틱으로 고정되어 있습니다[1][4].

## 증거로서 의미

### 증명하는 것

- 회계가 켜진 동안 `comm` 이름(최대 15글자)의 프로세스가 끝났다는 것과, 그 프로세스의 실제 UID·GID
- 시작 시각과 경과 시간, CPU 를 쓴 양, 종료 상태
- `ASU` 가 켜져 있으면 그 프로세스가 슈퍼유저 권한을 썼다는 것, `AXSIG` 가 켜져 있으면 시그널을 받고 끝났다는 것
- 3판이면 PID 와 부모 PID 로 어느 프로세스가 무엇을 띄웠는지 이을 수 있다는 것
- `ac_tty` 가 0이 아니면 제어 터미널이 있었다는 것(대화형 세션일 가능성)

### 증명하지 못하는 것

- 전체 경로와 명령줄 인수: `/tmp/ls` 와 `/usr/bin/ls` 는 둘 다 `ls` 로만 남습니다.
- 아직 끝나지 않은 프로세스: 수집 시점에 돌고 있던 프로세스와 시스템이 갑자기 멈출(crash) 때 돌던 프로세스는 기록되지 않습니다[2].
- 셸 내장 명령: `history -c` 나 `cd` 처럼 새 프로세스를 띄우지 않는 명령은 남지 않습니다. 이 점은 [셸 명령 기록](shell-history/index.md) 에서 다룹니다.
- 명령 이름의 진위: 프로세스는 자기 `comm` 값을 바꿀 수 있습니다[7].
- 효과 UID: `ac_uid` 는 실제 UID 라서[3][5], setuid 프로그램처럼 효과 UID 만 바뀐 권한은 이 칸에 드러나지 않습니다. 권한을 올린 경위는 `ASU` 비트와 [sudo·su 사용 기록](../logins/sudo-su.md) 으로 따로 봅니다.
- 회계를 켜기 전, 끈 동안, 멈춘 동안(아래 "함정과 한계")의 실행

## 시각 해석

`ac_btime` 은 프로세스가 끝날 때 커널이 "지금 시각(초) − 경과 시간" 으로 거꾸로 계산해 넣는 값입니다[5]. 시작할 때 적어 둔 값이 아니라서, 프로세스가 도는 사이에 시스템 시계를 옮기면 기록된 시작 시각이 실제와 어긋날 가능성이 있습니다. 값은 1970년부터 초로 센 32비트 부호 없는 정수이고 UTC 기준이라, 현지 시각은 검체의 시간대 설정으로 따로 바꿉니다[3][5]. 시각 값 일반은 [Linux 의 시각 값](../../01-foundations/value-decoding/time-values.md) 을 봅니다.

종료 시각은 파일에 없고, `ac_btime + 경과 시간(초)` 으로 계산합니다. 3판의 경과 시간은 초당 100틱 단위의 실수라서 100으로 나누면 초가 됩니다[4][5]. 2판은 `ac_etime` 이 16비트 `comp_t` 라서, 커널이 같은 경과 시간을 24비트 `comp2_t`(5비트 2진 지수, 20비트 가수)로 한 번 더 인코딩해 `ac_etime_hi`·`ac_etime_lo` 에 나눠 둡니다[3][5]. 2판의 틱 단위는 `ac_ahz` 값으로 나눕니다[3][5].

파일 순서는 끝난 순서라서, 오래 돈 부모 프로세스는 자식보다 뒤에 나옵니다[1]. 타임라인에 넣을 때는 시작 시각과 종료 시각을 둘 다 계산하고 시작 시각 순으로 다시 정렬하면 부모와 자식을 따라가기 쉽습니다. 타임라인 만드는 법은 [타임라인 만들기](../../03-techniques/analysis/timeline.md) 에서 다룹니다.

## 함정과 한계

회계는 켜져 있어도 도중에 멈출 수 있습니다. 회계 파일이 있는 파일 시스템의 여유 공간이 `lowwater`% 아래로 떨어지면 멈추고, `highwater`% 이상으로 돌아오면 다시 기록하며, 여유 공간은 `frequency` 초마다 봅니다[6]. 세 값은 `/proc/sys/kernel/acct` 에 있고 기본값은 `4 2 30` 입니다[6][7]. 멈출 때와 다시 시작할 때 커널은 `Process accounting paused`, `Process accounting resumed` 를 남기므로 [커널 로그](../system-info/kernel-log.md) 에서 빈 구간을 찾을 수 있습니다[5]. 파일 시스템이 얼어 있는(frozen) 동안에도 레코드를 쓰지 않고 넘어갑니다[5].

서비스를 멈추거나 `accton off` 를 실행해도 회계가 꺼집니다[8][9]. 서비스를 멈춘 흔적은 [systemd 저널](../../01-foundations/logging/systemd-journal/index.md) 에서 확인하고, `acct(2)` 호출은 감사 규칙의 쓰기 분류에 들어가므로[11] 감시 규칙이 있었다면 [감사 로그의 파일 감시](../file-activity/auditd-watches.md) 에도 남습니다. 회계 파일 자체를 지우거나 비운 흔적은 [흔적을 지웠나](../../04-scenarios/insider/anti-forensics.md) 에서 다룹니다.

UID·GID 는 회계 파일을 연 쪽의 사용자 네임스페이스 기준 값으로 바꿔 적고, PID 는 회계를 켠 쪽의 PID 네임스페이스 기준 번호입니다[5]. 커널은 끝난 프로세스의 PID 네임스페이스부터 부모 쪽으로 올라가며 회계가 켜진 곳마다 레코드를 씁니다[5]. 그래서 호스트에서 회계를 켜 두면 컨테이너 안에서 끝난 프로세스도 호스트 쪽 PID 로 호스트 파일에 남고, 컨테이너 안에서 본 PID 와 다릅니다. 컨테이너 흔적 전반은 [Docker](../containers/docker/index.md) 를 봅니다.

`AFORK` 가 켜진 레코드는 exec 없이 끝난 프로세스라서, 명령 이름이 부모에게서 물려받은 이름일 가능성이 있습니다. 셸이 서브셸을 만들면 `bash` 같은 이름으로 여러 줄이 생길 수 있으니, 이런 줄을 따로 실행한 `bash` 로 읽지 않습니다.

UID 를 사용자 이름으로 바꿀 때는 수집 시점의 `/etc/passwd` 를 씁니다. 그 뒤에 계정을 지우거나 번호를 다시 썼다면 이름이 달라질 수 있으므로 [계정 파일](../../01-foundations/users-auth/passwd-shadow-group.md) 과 계정 변경 흔적을 함께 봅니다.

## 직접 분석해 보기

### 헥스로 한 번

아래는 커널 헤더의 3판 구조체로 만든 예시 레코드 하나입니다(리틀엔디언, 모든 값은 지어낸 값입니다).

```text
00000000  02 03 01 88 00 00 00 00 e8 03 00 00 e8 03 00 00
00000010  92 10 00 00 68 10 00 00 00 b9 55 69 00 00 16 43
00000020  0c 00 05 00 00 2a 00 00 00 00 2c 01 00 00 00 00
00000030  63 75 72 6c 00 00 00 00 00 00 00 00 00 00 00 00
```

| 오프셋 | 바이트 | 읽은 값 |
|---|---|---|
| 0x00 | `02` | `ASU` — 슈퍼유저 권한을 썼음 |
| 0x01 | `03` | 3판, 리틀엔디언 |
| 0x02 | `01 88` | 제어 터미널 장치 번호 0x8801 |
| 0x04 | `00 00 00 00` | 종료 상태 0 |
| 0x08 | `e8 03 00 00` | UID 1000 |
| 0x0C | `e8 03 00 00` | GID 1000 |
| 0x10 | `92 10 00 00` | PID 4242 |
| 0x14 | `68 10 00 00` | 부모 PID 4200 |
| 0x18 | `00 b9 55 69` | 0x6955B900 = 1767225600 → 2026-01-01 00:00:00 UTC |
| 0x1C | `00 00 16 43` | 실수 0x43160000 = 150.0틱 → 1.5초 |
| 0x20 | `0c 00` | 사용자 CPU 12틱 |
| 0x22 | `05 00` | 커널 CPU 5틱 |
| 0x24 | `00 2a` | comp_t 0x2A00 → 지수 1, 가수 0xA00(2560) → 2560 × 8 = 20480 kB |
| 0x2A | `2c 01` | 가벼운 페이지 폴트 300 |
| 0x30 | `63 75 72 6c 00` | `curl` |

이 레코드는 "UID 1000 의 `curl` 이라는 이름의 프로세스가 2026-01-01 00:00:00 UTC 에 시작해 1.5초 뒤 정상 종료했고, 슈퍼유저 권한을 쓴 적이 있다" 까지만 말합니다. 종료 시각은 00:00:01.5 UTC 로 계산합니다.

### 도구로 한 번

RHEL 9 의 `psacct` 에 들어 있는 `lastcomm`, `sa`, `dump-acct` 로 회계 파일을 읽을 수 있습니다[8]. 이 도구들은 분석하는 기계의 시간대로 시각을 보여 줄 수 있으므로, 결과를 보고서에 옮기기 전에 헥스로 레코드 몇 개의 `ac_btime` 을 맞춰 봅니다.

도구가 없는 환경에서는 표준 라이브러리만으로 3판 파일을 읽을 수 있습니다. 아래 스크립트는 커널 헤더의 구조체를 그대로 옮긴 것입니다[3].

```python
import struct, datetime, sys

V3 = struct.Struct('<BBHIIIIIIfHHHHHHHH16s')   # 64바이트

def comp_t(c):
    return (c & 0x1fff) << (((c >> 13) & 0x7) * 3)

data = open(sys.argv[1], 'rb').read()
for off in range(0, len(data) - 63, 64):
    r = V3.unpack_from(data, off)
    if r[1] & 0x7f != 3:
        print(off, 'not v3'); continue
    start = datetime.datetime.fromtimestamp(r[8], datetime.timezone.utc)
    sec = r[9] / 100
    print(off, r[18].rstrip(b'\0').decode(errors='replace'),
          'uid=%d pid=%d ppid=%d' % (r[4], r[6], r[7]),
          'start=%s' % start.isoformat(), 'elapsed=%.2fs' % sec,
          'flag=0x%02x' % r[0], 'mem=%dkB' % comp_t(r[12]))
```

## 교차 검증

| 함께 볼 아티팩트 | 채워 주는 것 |
|---|---|
| [감사 로그의 실행 기록](auditd-execve.md) | 전체 경로·인수, 효과 UID, 감사 ID |
| [셸 명령 기록](shell-history/index.md) | 입력한 명령줄, 내장 명령 |
| [실행 중인 프로세스](proc.md) | 아직 끝나지 않아 회계에 없는 프로세스 |
| [로그인 기록](../logins/wtmp-btmp-lastlog.md) | 같은 터미널·같은 시간대의 로그인 세션 |
| [sudo·su 사용 기록](../logins/sudo-su.md) | `ASU` 레코드의 권한 상승 경위 |
| [커널 로그](../system-info/kernel-log.md) | 회계 멈춤·재개 메시지 |
| [systemd 저널](../../01-foundations/logging/systemd-journal/index.md) | `acct`·`psacct` 서비스의 시작·중지 |

## 실습

실습용 가상 머신에 `acct` 또는 `psacct` 를 깔고 서비스를 켠 뒤 몇 가지 명령을 실행하고, 이미지로 떠서 아래 질문을 풀어 봅니다.

1. 회계 파일 둘째 바이트로 판을 가리고, `/boot/config-*` 의 `CONFIG_BSD_PROCESS_ACCT_V3` 와 맞는지 확인합니다.
2. `sudo` 로 실행한 명령의 레코드에서 `ac_uid` 와 `ASU` 비트가 어떻게 남는지 봅니다.
3. 오래 돈 셸의 레코드가 그 셸에서 실행한 명령들보다 파일 뒤쪽에 나오는지 보고, 3판이면 PID·부모 PID 로 이어 봅니다.
4. `ls` 를 다른 폴더로 복사해 실행한 뒤 원래 `ls` 와 레코드로 구별할 수 있는지 봅니다.
5. 서비스를 멈췄다 켠 구간이 회계 파일과 저널에 각각 어떻게 드러나는지 비교합니다.

## 참고 문헌

1. Linux man-pages, acct(5). https://github.com/mkerrisk/man-pages/blob/master/man5/acct.5
2. Linux man-pages, acct(2). https://github.com/mkerrisk/man-pages/blob/master/man2/acct.2
3. Linux 커널, include/uapi/linux/acct.h. https://github.com/torvalds/linux/blob/master/include/uapi/linux/acct.h
4. Linux 커널, include/linux/acct.h. https://github.com/torvalds/linux/blob/master/include/linux/acct.h
5. Linux 커널, kernel/acct.c. https://github.com/torvalds/linux/blob/master/kernel/acct.c
6. Linux 커널 문서, Documentation/admin-guide/sysctl/kernel.rst (acct). https://github.com/torvalds/linux/blob/master/Documentation/admin-guide/sysctl/kernel.rst
7. Linux man-pages, proc(5). https://github.com/mkerrisk/man-pages/blob/master/man5/proc.5
8. psacct 6.6.4-13 (RHEL 9 호환 소스, OpenELA el9 브랜치): SPECS/psacct.spec, SOURCES/psacct.service, SOURCES/psacct-logrotate.in, SOURCES/accton-create. https://github.com/openela-main/psacct/tree/el9
9. acct 6.6.4 Debian 패키징(deepin-community 사본): debian/acct.service, debian/acct.postinst, debian/acct.cron.daily, debian/acct.default. https://github.com/deepin-community/acct/tree/master/debian
10. UAC, artifacts/files/system/acct.yaml. https://github.com/tclahr/uac/blob/main/artifacts/files/system/acct.yaml
11. Linux 커널, include/asm-generic/audit_write.h. https://github.com/torvalds/linux/blob/master/include/asm-generic/audit_write.h
