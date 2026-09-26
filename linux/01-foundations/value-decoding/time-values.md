---
title: "Linux 의 시각 값"
parent: "기반 · 값 해석"
nav_order: 260
---

# Linux 의 시각 값 (epoch·나노초·마이크로초)

Linux 의 시각 값은 대부분 1970-01-01 00:00:00 UTC 부터 센 수이지만, 단위(초·밀리초·마이크로초·나노초·일·클록 틱)와 0점(epoch·부팅 순간·1901년), 바이트 순서가 기록마다 달라서 값마다 셋을 먼저 정하고 풀어야 합니다.

## 이 형식을 쓰는 아티팩트

유닉스 시각 (Unix time) 은 1970-01-01 00:00:00 UTC 를 0으로 두고 센 값이고, 그 자체에는 시간대가 없습니다[6]. 파일 시스템의 아이노드 시각, systemd 저널, 로그인 기록, 감사 로그, 셸 기록이 이 값을 씁니다. 반면 커널 메시지 버퍼와 `/proc` 의 프로세스 시작 시각은 부팅 순간을 0으로 두고, 패키지 관리자 로그처럼 사람이 읽는 날짜 문자열을 현지 시각으로 쓰는 기록도 있습니다.

아래 표는 기록별로 단위와 기준을 모은 것입니다. 각 형식의 나머지 구조는 표의 링크에서 다룹니다.

| 기록 | 필드 | 단위·폭 | 0점 | 시간대 |
|---|---|---|---|---|
| ext4 아이노드 | `i_atime`·`i_ctime`·`i_mtime`·`i_dtime` | 부호 있는 32비트 초, 리틀 엔디언 | 1970 epoch | UTC[1] |
| ext4 큰 아이노드 | `i_[cma]time_extra`, `i_crtime`, `i_crtime_extra` | 초 확장 2비트 + 나노초 30비트 | 1970 epoch | UTC[1] |
| ext4 슈퍼블록 | `s_mtime`·`s_wtime`·`s_lastcheck`·`s_mkfs_time` 등 | 32비트 초 + `_hi` 8비트 | 1970 epoch | UTC[2] |
| jbd2 커밋 블록 | `h_commit_sec`·`h_commit_nsec` | 64비트 초 + 32비트 나노초, 빅 엔디언 | 1970 epoch | UTC[3] |
| XFS (기존) | `di_atime`·`di_mtime`·`di_ctime`·`di_crtime` | 부호 있는 32비트 초 + 32비트 나노초, 빅 엔디언 | 1970 epoch | UTC[4] |
| XFS (bigtime) | 같은 필드 | 부호 없는 64비트 나노초, 빅 엔디언 | 1901-12-13 20:45:52 UTC | UTC[4] |
| Btrfs 아이노드 항목 | `atime`·`ctime`·`mtime`·`otime` | 64비트 초 + 32비트 나노초, 리틀 엔디언 | 1970 epoch | UTC[5] |
| systemd 저널 | 항목의 `realtime` / `monotonic` | 64비트 마이크로초 | epoch / 부팅 | UTC / 없음[8] |
| 커널 메시지 (`/dev/kmsg`) | 머리의 세 번째 필드 | 마이크로초 | 부팅 | 없음[11] |
| `/proc/stat` | `btime` | 초 | 1970 epoch | UTC[12] |
| `/proc/PID/stat` | 22번째 `starttime` | 클록 틱 | 부팅 | 없음[12] |
| utmp·wtmp·btmp | `ut_tv` | 초 + 마이크로초 | 1970 epoch | UTC[13] |
| lastlog | `ll_time` | 32비트 초 | 1970 epoch | UTC[22] |
| wtmpdb·lastlog2 (SQLite) | `Login`·`Logout` / `Time` | 마이크로초 / 초 | 1970 epoch | UTC[22] |
| `/etc/shadow` | 3번째(마지막 변경), 8번째(계정 만료) | 일(day) | 1970-01-01 | UTC[14] |
| 감사 로그 | `msg=audit(초.밀리초:일련번호)` | 초 + 밀리초 | 1970 epoch | UTC[21] |
| bash 기록 | `#` 뒤 숫자 줄 | 초 | 1970 epoch | UTC[15][21] |
| zsh 확장 기록 | `: 시작:걸린시간;명령` | 초 | 1970 epoch | UTC[21] |
| dpkg.log | `2016-08-03 15:25:53` 형식 | 초 | — | 현지 시각[21] |
| apt history.log | `Start-Date:`·`End-Date:` | 초 | — | 현지 시각[21] |

형식별 설명은 [ext4](../filesystem/ext4/index.md), [XFS](../filesystem/xfs.md), [Btrfs](../filesystem/btrfs.md), [systemd 저널](../logging/systemd-journal/index.md), [로그인 기록 파일 형식](../logging/utmp-wtmp-format.md), [감사 로그 형식](../logging/auditd-format.md), [계정 파일](../users-auth/passwd-shadow-group.md)에 있습니다. 연도와 시간대가 빠진 전통 syslog 시각과 rsyslog 의 RFC 3339 시각은 [syslog 형식과 rsyslog](../logging/syslog-rsyslog.md)에서, logrotate 상태 파일의 시각은 [로그 순환](../logging/logrotate.md)에서 다룹니다.

## 구조

### ext4 아이노드 시각

아이노드의 앞 128바이트에는 ctime·atime·mtime·dtime 네 시각이 부호 있는 32비트 초로 들어갑니다[1]. 아이노드가 128바이트보다 크고 `i_extra_isize` 가 해당 필드까지 덮으면, ctime·atime·mtime 은 `_extra` 32비트 필드로 넓혀집니다[1]. `_extra` 의 아래 2비트는 초를 34비트로 늘리는 epoch 비트이고, 위 30비트는 나노초입니다[1]. 만든 시각 (crtime) 도 같은 방식으로 64비트이고, dtime 은 넓히지 않아 초 단위만 남습니다[1].

| 오프셋 | 필드 | 뜻 |
|---|---|---|
| 0x08 | `i_atime` | 마지막 접근 |
| 0x0C | `i_ctime` | 아이노드 정보 변경 |
| 0x10 | `i_mtime` | 내용 변경 |
| 0x14 | `i_dtime` | 삭제 |
| 0x84 | `i_ctime_extra` | ctime 의 epoch 비트·나노초 |
| 0x88 | `i_mtime_extra` | mtime 의 epoch 비트·나노초 |
| 0x8C | `i_atime_extra` | atime 의 epoch 비트·나노초 |
| 0x90 | `i_crtime` | 만든 시각(초) |
| 0x94 | `i_crtime_extra` | crtime 의 epoch 비트·나노초 |

초 값은 "부호 있는 32비트 값 + 2^32 × epoch 비트" 로 풉니다[1]. 그래서 epoch 비트 00 은 1901-12-13 부터 2038-01-19 까지, 01 은 2038-01-19 부터 2174-02-25 까지 이어지고, 11 까지 쓰면 2446-05-10 에 닿습니다[1]. 나노초는 `_extra` 를 오른쪽으로 2비트 민 값입니다[1][25].

슈퍼블록의 시각은 32비트 초에 `s_wtime_hi`(0x274)·`s_mtime_hi`(0x275)·`s_mkfs_time_hi`(0x276)·`s_lastcheck_hi`(0x277) 같은 상위 8비트 필드를 붙여 늘립니다[2]. 기본 필드의 오프셋은 `s_mtime` 0x2C, `s_wtime` 0x30, `s_lastcheck` 0x40, `s_mkfs_time` 0x108 입니다[2].

jbd2 저널은 ext4 와 달리 모든 필드를 빅 엔디언으로 쓰고, 커밋 블록의 0x30 에 `h_commit_sec`(64비트 초), 0x38 에 `h_commit_nsec`(32비트 나노초)를 둡니다[3].

### XFS 와 Btrfs

XFS 아이노드의 시각 필드는 빅 엔디언 64비트 `xfs_timestamp_t` 입니다[4]. 기존 형식에서는 이 8바이트가 부호 있는 32비트 초 `t_sec` 와 32비트 나노초 `t_nsec` 로 나뉘고, 범위는 1901-12-13 20:45:52 UTC 부터 2038-01-19 03:14:07 UTC 까지입니다[4].

bigtime 기능이 켜지면 같은 8바이트가 부호 없는 64비트 나노초 카운터가 되고, 0점은 1970 이 아니라 1901-12-13 20:45:52 UTC 입니다[4]. 이 값을 10^9 로 나눈 초에서 2^31(`XFS_BIGTIME_EPOCH_OFFSET`)을 빼면 유닉스 초가 되고, 최대 2486-07-02 20:20:24 UTC 까지 나타냅니다[4]. bigtime 은 슈퍼블록의 `XFS_SB_FEAT_INCOMPAT_BIGTIME` 과 아이노드 `di_flags2` 의 `XFS_DIFLAG2_BIGTIME`(3번 비트)로 알 수 있습니다[4]. 만든 시각은 `di_crtime` 입니다[4].

Btrfs 아이노드 항목에는 `btrfs_timespec` 네 개(`atime`·`ctime`·`mtime`·`otime`)가 있고, 각각 리틀 엔디언 64비트 초와 32비트 나노초입니다[5].

### 저널과 커널이 쓰는 두 가지 시계

systemd 저널 파일은 모든 시각을 마이크로초로 저장합니다[8]. 실제 시각 시계(wall clock) 값 (realtime) 은 1970 epoch 기준 `CLOCK_REALTIME` 이고, 단조 시계 값 (monotonic) 은 `CLOCK_MONOTONIC` 이라서 부팅 ID(`boot_id`)와 짝을 지어야 뜻이 있습니다[8]. 단조 시계는 대개 부팅 순간부터 세지만 컨테이너 안에서는 그렇지 않습니다[8]. 파일 머리에는 `head_entry_realtime`·`tail_entry_realtime`·`tail_entry_monotonic` 이 있고, 항목(ENTRY)마다 `realtime`·`monotonic` 이 있습니다[8].

내보낸 필드에서는 `__REALTIME_TIMESTAMP=` 가 journald 가 항목을 받은 순간의 UTC 마이크로초이고, `_SOURCE_REALTIME_TIMESTAMP=` 는 받은 시각과 다른 값이 있을 때 남기는, 메시지의 가장 이른 믿을 만한 시각입니다[9]. `__REALTIME_TIMESTAMP=` 는 이 값보다 대개 조금 늦습니다[9]. systemd v257 부터는 `CLOCK_BOOTTIME` 기준 `_SOURCE_BOOTTIME_TIMESTAMP=` 도 있습니다[9].

`/dev/kmsg` 의 한 줄은 `우선순위,순번,시각,플래그;메시지` 형식이고, 시각은 부팅 뒤 흐른 단조 시계 마이크로초입니다[11]. 예를 들어 `6,339,5140900,-;NET: Registered protocol family 10` 의 5140900 은 부팅 뒤 약 5.14초입니다[11].

`/proc/stat` 의 `btime` 은 부팅 시각을 1970 epoch 초로 담습니다[12]. `/proc/PID/stat` 의 22번째 필드 `starttime` 은 부팅 뒤 프로세스가 시작한 시점이고, Linux 2.6 부터는 `sysconf(_SC_CLK_TCK)` 로 나눠야 초가 되는 클록 틱 단위입니다(그 전은 jiffies)[12]. `/proc/uptime` 의 두 수는 잠자기를 포함한 가동 시간과 idle 시간이고 단위는 초입니다[12].

### 로그인·계정·명령 기록

utmp 레코드의 `ut_tv` 는 x86-64 처럼 32비트 시각 호환을 켠 환경에서 32비트 초와 32비트 마이크로초이고, 그 밖의 64비트 환경에서는 `struct timeval` 입니다[13]. 레코드 크기와 오프셋은 [로그인 기록 파일 형식](../logging/utmp-wtmp-format.md)에 있습니다.

`/etc/shadow` 의 마지막 변경일과 계정 만료일은 1970-01-01 부터 센 일수입니다[14]. 마지막 변경일 0 은 "다음 로그인 때 비밀번호를 바꿔야 함" 이고, 빈칸은 비밀번호 나이 기능을 끈 것입니다[14]. 계정 만료일 0 은 "만료 없음" 으로도 "1970-01-01 만료" 로도 읽힐 수 있어서 쓰지 말라고 되어 있습니다[14].

감사 로그의 `msg=audit(1105758604.519:420)` 는 1970 epoch 초 1105758604 와 밀리초 519, 이벤트 일련번호 420 입니다[21]. bash 는 `HISTTIMEFORMAT` 이 설정돼 있을 때만 기록 파일에 시각을 쓰고, 기록 주석 문자로 시각 줄을 명령 줄과 구분합니다[15]. 그래서 `.bash_history` 에서는 `#` 뒤에 9~10자리 epoch 초가 오는 줄이 바로 아래 명령의 시각입니다[21]. zsh 확장 기록은 `: 시작초:걸린초;명령` 형식입니다[21].

## 읽는 법

값을 풀기 전에 세 가지를 정합니다. 단위(초인지, 1000배·100만 배·10억 배인지), 0점(1970, 부팅 순간, 1901년), 바이트 순서(ext4·Btrfs·저널은 리틀 엔디언, jbd2·XFS 는 빅 엔디언)입니다. 자릿수로 단위를 어림할 수 있는데, 2001년부터 2286년 사이의 epoch 초는 10자리이고, 밀리초는 13자리, 마이크로초는 16자리, 나노초는 19자리입니다.

### 헥스로 한 번: ext4

아래 바이트는 명세로 만든 예시입니다. 아이노드의 0x10(`i_mtime`)과 0x88(`i_mtime_extra`)만 보입니다.

```text
0x10: 50 f6 d3 67            i_mtime       (리틀 엔디언 0x67D3F650)
0x88: 54 34 6f 1d            i_mtime_extra (리틀 엔디언 0x1D6F3454)
```

1. `i_mtime` 0x67D3F650 은 부호 있는 32비트로 1741944400 입니다.
2. `i_mtime_extra` 0x1D6F3454 의 아래 2비트는 00 이라서 초에 더할 것이 없습니다.
3. 0x1D6F3454 를 오른쪽으로 2비트 밀면 0x075BCD15 = 123456789 나노초입니다.
4. 결과는 2025-03-14 09:26:40.123456789 UTC 입니다.

epoch 비트가 쓰이는 예도 명세로 만들어 봅니다. `i_mtime` 이 `80 7e aa 83`, `i_mtime_extra` 가 `01 00 00 00` 이면, 부호 있는 32비트 값 −2085978496 에 2^32 × 1 을 더해 2208988800, 곧 2040-01-01 00:00:00 UTC 입니다[1]. epoch 비트를 무시하고 부호 있는 값만 쓰면 1903-11-25 17:31:44 UTC 로 잘못 나옵니다.

### 헥스로 한 번: XFS bigtime

명세로 만든 예시로, bigtime 아이노드의 `di_mtime` 8바이트가 `35 fa 06 33 fa 48 85 00` 이라고 합니다. 빅 엔디언 값 3889428048500000000 을 10^9 로 나누면 3889428048초와 나머지 500000000 나노초이고, 초에서 2^31 을 빼면 1741944400, 곧 2025-03-14 09:26:40.5 UTC 입니다[4]. 같은 8바이트를 기존 형식으로 읽으면 `t_sec` 가 0x35FA0633 이 되어 전혀 다른 날짜가 나오므로, 먼저 bigtime 여부를 봅니다.

### 저널 마이크로초

저널 항목의 `realtime` 이 `40 16 30 09 4a 30 06 00`(명세로 만든 예시)이면 리틀 엔디언 1741944400123456 마이크로초이고, 10^6 으로 나누면 2025-03-14 09:26:40.123456 UTC 입니다[8].

### 부팅 기준 값을 실제 시각으로 바꾸기

부팅 기준 값은 부팅 시각을 더해야 실제 시각이 됩니다. 프로세스 시작 시각은 `btime + starttime ÷ CLK_TCK` 로 구합니다[12]. 커널이 procfs 로 부팅 시각의 초만 내보내므로 ps 같은 도구도 초 단위 부팅 시각을 쓰고, Volatility 3 도 메모리에서 프로세스 시작 시각을 구할 때 부팅 시각의 마이크로초를 버리고 더합니다[23]. 저널의 단조 시계 값은 같은 `_BOOT_ID` 안에서만 서로 비교할 수 있습니다[8][9].

### 현지 시각으로 바꾸기

UTC 값을 사람이 읽는 시각으로 바꿀 때는 분석 PC 가 아니라 분석 대상 시스템의 시간대를 씁니다. systemd 기준으로 시스템 시간대는 `/etc/localtime` 이 가리키는 `/usr/share/zoneinfo/` 아래 파일 이름에서 정하고, 이 파일이 없으면 UTC 이며, 프로그램마다 `$TZ` 로 덮어쓸 수 있습니다[17]. `timedatectl set-local-rtc 1` 이면 하드웨어 시계 (RTC) 를 현지 시각으로 두는데, 이 설정은 `/etc/adjtime` 의 세 번째 줄에 남습니다[18]. 분석 대상에서 시간대를 찾는 순서는 도구마다 다르고, 자세한 위치는 [호스트 이름·시간대·로캘](../../02-artifacts/system-info/hostname-timezone.md)에 있습니다.

## 포렌식에서 중요한 점

### 무엇이 바뀔 때 바뀌나

atime 은 `execve`·`mknod`·`pipe`·`utime`, 0바이트를 넘는 `read` 로 바뀌고, `mmap` 같은 다른 경로로는 바뀔 수도 안 바뀔 수도 있습니다[6]. `noatime`·`nodiratime`·`relatime` 으로 마운트했거나 `O_NOATIME` 으로 열면 atime 이 바뀌지 않습니다[6]. relatime 은 mtime 이나 ctime 이 atime 보다 새롭거나 atime 이 정해진 간격(기본 1일)보다 오래됐을 때만 atime 을 고칩니다[25].

mtime 은 `mknod`·`truncate`·`utime`, 0바이트를 넘는 `write` 로 바뀌고, 디렉터리는 안에서 파일을 만들거나 지울 때 바뀝니다[6]. 소유자·그룹·링크 수·권한을 바꾸는 것으로는 mtime 이 바뀌지 않습니다[6]. ctime 은 쓰기와 아이노드 정보(소유자·그룹·링크 수·권한 등) 변경 때 바뀝니다[6]. 만든 시각 (btime) 은 파일을 만들 때 정해지고 그 뒤로 바뀌지 않으며, `stat` 구조체에는 없고 `statx` 의 `stx_btime` 으로만 나옵니다[6][7]. 파일 시스템이 btime 을 주지 못하면 `stx_mask` 의 `STATX_BTIME` 비트가 꺼지고 자리 채우는 값이 들어갈 수 있습니다[7]. ext4 의 crtime 과 dtime 은 `stat()` 으로 보이지 않고 `debugfs` 로 볼 수 있습니다[1].

ext4 에서 파일을 지우는 시험에서는 `i_ctime_extra`·`i_mtime_extra` 의 나노초가 삭제 순간의 값으로 새로 쓰였고, `i_atime_extra`·`i_crtime_extra` 는 그대로였습니다[25].

### 시계를 바꾼 흔적

utmp·wtmp 의 `ut_type` 3(NEW_TIME)과 4(OLD_TIME)은 시스템 시계를 바꾼 뒤와 앞의 시각이고, 2(BOOT_TIME)는 부팅 시각입니다[13]. 저널 파일의 항목은 일련번호 순서로 쓰이고, 같은 부팅 안에서는 단조 시계 값도 커지기만 하며, 실제 시각 시계 값은 시계를 고친 때의 건너뜀을 빼면 커지기만 합니다[8]. 그래서 같은 `boot_id` 안에서 단조 시계는 커지는데 실제 시각 시계가 뒤로 가는 곳은 시계를 바꾼 지점일 가능성이 있습니다. 판단 절차는 [시각을 조작했나](../../04-scenarios/insider/time-manipulation.md)에서 다룹니다.

### 조작과 숨기기

`touch` 는 ctime 을 원하는 값으로 정할 수 없고 btime 은 아예 바꿀 수 없습니다[16]. atime·mtime 을 `utime` 류로 되돌리면 아이노드 정보를 바꾼 것이라 그 순간 ctime 이 새로 찍힐 가능성이 있습니다[6]. 그래서 mtime 을 되돌린 파일은 ctime 이 mtime 보다 뒤에 남을 가능성이 있습니다.

ext4 나노초 필드는 데이터를 숨기는 데 쓰일 수 있습니다[25]. 암호화한 데이터를 atime·crtime 의 나노초에 넣은 시험에서는 아래 10비트의 엔트로피가 정상 값과 구별되지 않았습니다[25]. 대신 새로 만든 파일은 atime 과 crtime 의 나노초가 같은데 숨긴 뒤에는 달라지고, 필드를 고치면 아이노드 체크섬이 틀어져 `e2fsck` 가 잡습니다[25]. epoch 비트에 숨기면 날짜가 2038년 뒤로 넘어가 눈에 띕니다[25].

### 기록으로 확인되는 만큼

시각 값이 증명하는 것은 그 값을 쓴 주체(커널·journald·auditd 등)의 시계가 그 순간 가리킨 값입니다. 저널에서 `realtime`·`monotonic`·`boot_id` 가 함께 있으면 한 부팅 안의 순서도 알 수 있습니다[8]. 시계가 맞았다는 것, 그 시각에 사람이 앞에 있었다는 것은 증명하지 못합니다. 현지 시각으로 쓴 로그는 기록할 때의 시간대를 알아야 UTC 로 바꿀 수 있고, 단조 시계·커널 메시지·`starttime` 은 부팅 시각 없이는 날짜로 바꿀 수 없습니다.

## 함정

단위를 섞기 쉽습니다. 초(ext4·lastlog·bash), 밀리초(감사 로그), 마이크로초(저널·utmp 의 `tv_usec`·wtmpdb·`/dev/kmsg`), 나노초(ext4 `_extra`·XFS bigtime·Btrfs), 일(shadow), 클록 틱(`starttime`)이 한 시스템에 섞여 있습니다.

ext4 의 `_extra` 필드는 나노초를 그대로 담지 않습니다. 2비트를 밀어 나노초를 얻고, 아래 2비트는 초에 더합니다[1][25].

dtime 이 작은 정수면 시각이 아닐 수 있습니다. `orphan_file` 기능이 없는 ext4 에서는 열린 채 링크가 끊긴 고아 아이노드의 dtime 필드에 다음 고아 아이노드 번호(끝이면 0)가 들어갑니다[1]. `EA_INODE` 플래그가 선 아이노드는 확장 속성 값을 담는 아이노드라서 `i_atime` 에는 값의 체크섬, `i_ctime` 에는 참조 수의 아래 32비트, `i_mtime` 에는 소유 아이노드 번호가 들어갑니다[1].

2038년 뒤 날짜를 풀고 쓰는 데 오래된 버그가 있고, 커널 3.12·e2fsprogs 1.42.8 에서도 고쳐지지 않은 것으로 보입니다[1]. 64비트 커널은 1901~1970 날짜에 epoch 비트 11 을 잘못 씁니다[1]. 1970년 이전 파일 시각이 2300년대로 보이면 이 버그일 가능성이 있습니다.

도구마다 ext4 해석이 다릅니다. Sleuth Kit 의 `ext2fs.cpp` 는 32비트 초를 부호 없는 값으로 읽고, `_extra` 에서는 나노초만 가져와 epoch 비트를 초에 더하지 않습니다[19]. 그래서 1970년 이전 값은 2038~2106년으로, 2106년 뒤 값은 2^32초(약 136년)의 배수만큼 앞 날짜로 보입니다. TSK 4.4.2 의 `istat` 도 epoch 비트를 반영하지 않아 2038년 뒤 시각을 잘못 풉니다[25]. dtime 의 나노초는 늘 0으로 채웁니다[19]. XFS 는 `xfs.cpp` 가 `di_mtime`·`di_atime`·`di_ctime` 의 `t_sec`·`t_nsec` 만 옮기고 crtime 과 bigtime 처리가 코드에 없으므로[20], bigtime 볼륨이면 다른 도구 결과와 맞춰 봅니다.

`date -d @초` 는 분석 PC 의 시간대로 보여 줍니다. 4450342530 은 UTC 로 2111-01-10 14:15:30 인데, 이 값을 `date -d @4450342530` 으로 바꾼 시험에서는 `Sat Jan 10 15:15:30 2111` 이 나왔습니다[25]. 한 시간 차이는 명령을 실행한 PC 의 시간대 때문일 가능성이 있습니다. 비교할 때는 `date -u -d @초` 처럼 UTC 로 고정합니다.

shadow 의 0 은 도구가 뜻을 잃기 쉽습니다. dissect.target 은 마지막 변경일과 만료일이 0이면 "없음" 으로 처리하므로 "다음 로그인 때 바꿔야 함" 이라는 뜻이 결과에 남지 않습니다[22].

utmp·lastlog 의 32비트 초는 2038년에 넘칩니다. utmp(5)는 `ut_tv` 의 `tv_sec` 를 `int32_t` 로 정의하지만, dissect.target 은 utmp 의 `tv_sec` 와 lastlog 의 `ll_time` 을 `uint32` 로 읽습니다[13][22].

현지 시각으로 쓰는 로그는 시간대를 따로 붙여야 합니다. plaso 도 dpkg.log 와 apt history.log 의 시각에 현지 시각 표시(`is_local_time`)를 붙입니다[21].

## 도구

| 도구 | 쓰는 곳 |
|---|---|
| `debugfs -R 'stat <INODE>'` | ext4 아이노드의 crtime·dtime 까지 보기[1] |
| `stat`, `ls --time-style=full-iso` | 나노초와 시간대 오프셋 표시(`+%Y-%m-%d %H:%M:%S.%N %z`). `stat -c '%W'` 는 btime 을 모르면 `0`, `%w` 는 `-` 를 냄. `%.3X` 처럼 소수 자릿수를 정하면 남는 자리는 버림[16] |
| `journalctl --utc`, `-o short-iso-precise`, `-o short-unix`, `-o short-monotonic` | 저널 시각을 UTC·마이크로초·epoch·단조 시계로 보기. `-o export`·`-o json` 은 `--output-fields=` 로 필드를 줄여도 `__REALTIME_TIMESTAMP`·`__MONOTONIC_TIMESTAMP`·`_BOOT_ID` 를 출력[10] |
| Sleuth Kit `istat` | 아이노드 시각 보기. 위 함정 참고[19][20] |
| plaso | 로그별 단위 처리. 감사 로그는 밀리초 값으로, dpkg·apt 는 현지 시각으로 다룸[21] |
| dissect.target | utmp 는 초, wtmpdb 는 마이크로초로 변환[22] |
| Volatility 3 `linux.boottime`·`linux.pslist`·`linux.kmsg` | 메모리에서 부팅 시각과 프로세스 시작 시각 계산, time namespace 마다 부팅 시각 표시. kmsg 는 나노초를 커널 `print_time` 과 같게 버림해 `초.마이크로초` 로 표시[23] |
| UAC | 파일 시각을 `stat -c` 로 뽑은 bodyfile(아래)에 epoch 초로 수집. 시간대는 라이브면 먼저 `$TZ`·`timedatectl` 을 보고, 그다음 `/etc/localtime` 링크 대상 → `/usr/share/zoneinfo/` 파일과 MD5 비교 → `/etc/timezone` 순으로 찾음[24] |

UAC bodyfile 한 줄은 `0|%N|%i|%A|%u|%g|%s|%X|%Y|%Z|%W` 형식 문자열로 만들어지므로, 뒤의 네 필드가 atime·mtime·ctime·btime 의 epoch 초입니다[24][16].

여러 기록을 한 시간 축에 놓는 절차는 [타임라인 만들기](../../03-techniques/analysis/timeline.md)에서 다룹니다. 다른 운영체제의 시각 값은 [Windows 시각 값 형식](https://urock-ailab.github.io/forensics-handbook/windows/01-foundations/value-decoding/filetime-unix-webkit-dos-ole.html), [맥의 시각 값](https://urock-ailab.github.io/forensics-handbook/mac/01-foundations/value-decoding/mac-time-values.html), [Android 시각 값](https://urock-ailab.github.io/forensics-handbook/android/01-foundations/value-decoding/time-values.html), [iOS 시각 값](https://urock-ailab.github.io/forensics-handbook/ios/01-foundations/value-decoding/time-values.html)에서 다룹니다.

## 참고 문헌

1. Linux kernel, `Documentation/filesystems/ext4/inodes.rst`. https://github.com/torvalds/linux/blob/master/Documentation/filesystems/ext4/inodes.rst
2. Linux kernel, `Documentation/filesystems/ext4/super.rst`. https://github.com/torvalds/linux/blob/master/Documentation/filesystems/ext4/super.rst
3. Linux kernel, `Documentation/filesystems/ext4/journal.rst`. https://github.com/torvalds/linux/blob/master/Documentation/filesystems/ext4/journal.rst
4. Linux kernel, `fs/xfs/libxfs/xfs_format.h`. https://github.com/torvalds/linux/blob/master/fs/xfs/libxfs/xfs_format.h
5. Linux kernel, `include/uapi/linux/btrfs_tree.h`. https://github.com/torvalds/linux/blob/master/include/uapi/linux/btrfs_tree.h
6. inode(7), Linux man-pages. https://github.com/mkerrisk/man-pages/blob/master/man7/inode.7
7. statx(2), Linux man-pages. https://github.com/mkerrisk/man-pages/blob/master/man2/statx.2
8. systemd, Journal File Format. https://github.com/systemd/systemd/blob/main/docs/JOURNAL_FILE_FORMAT.md
9. systemd, systemd.journal-fields(7). https://github.com/systemd/systemd/blob/main/man/systemd.journal-fields.xml
10. systemd, journalctl(1). https://github.com/systemd/systemd/blob/main/man/journalctl.xml
11. Linux kernel, `Documentation/ABI/testing/dev-kmsg`. https://github.com/torvalds/linux/blob/master/Documentation/ABI/testing/dev-kmsg
12. proc(5), Linux man-pages. https://github.com/mkerrisk/man-pages/blob/master/man5/proc.5
13. utmp(5), Linux man-pages. https://github.com/mkerrisk/man-pages/blob/master/man5/utmp.5
14. shadow, shadow(5). https://github.com/shadow-maint/shadow/blob/master/man/shadow.5.xml
15. bash(1). https://github.com/tianon/mirror-bash/blob/master/doc/bash.1
16. GNU coreutils manual, `doc/coreutils.texi`. https://github.com/coreutils/coreutils/blob/master/doc/coreutils.texi
17. systemd, localtime(5). https://github.com/systemd/systemd/blob/main/man/localtime.xml
18. systemd, timedatectl(1). https://github.com/systemd/systemd/blob/main/man/timedatectl.xml
19. The Sleuth Kit, `tsk/fs/ext2fs.cpp`. https://github.com/sleuthkit/sleuthkit/blob/develop/tsk/fs/ext2fs.cpp
20. The Sleuth Kit, `tsk/fs/xfs.cpp`. https://github.com/sleuthkit/sleuthkit/blob/develop/tsk/fs/xfs.cpp
21. plaso, `parsers/text_plugins/`(`dpkg.py`·`apt_history.py`·`selinux.py`·`bash_history.py`·`zsh_extended_history.py`). https://github.com/log2timeline/plaso/tree/main/plaso/parsers/text_plugins
22. dissect.target, `plugins/os/unix/log/utmp.py`·`lastlog.py`, `plugins/os/unix/shadow.py`. https://github.com/fox-it/dissect.target/tree/main/dissect/target/plugins/os/unix
23. Volatility 3, `plugins/linux/boottime.py`·`pslist.py`·`kmsg.py`, `symbols/linux/extensions/__init__.py`. https://github.com/volatilityfoundation/volatility3/tree/develop/volatility3/framework
24. UAC, `lib/setup_tools.sh`·`lib/get_timezone.sh`. https://github.com/tclahr/uac/tree/main/lib
25. Thomas Göbel, Harald Baier, "Anti-forensics in ext4: On secrecy and usability of timestamp-based data hiding", Digital Investigation 24 (2018) S111–S120. https://doi.org/10.1016/j.diin.2018.01.014
