---
title: "커널 로그"
parent: "아티팩트 · 시스템 정보"
nav_order: 320
---

# 커널 로그 (dmesg·kern.log)

커널이 남긴 메시지는 메모리의 링 버퍼에 쌓였다가 저널과 syslog 파일로 옮겨지므로, 장치 인식·모듈 적재·오류 같은 커널 사건을 부팅 기준 시각과 함께 복원할 수 있습니다.

## 무엇을 기록하나 · 왜 생기나

커널은 `printk()` 로 낸 메시지를 등급과 상관없이 크기가 정해진 원형 버퍼에 담습니다[2]. 이 버퍼를 흔히 커널 링 버퍼 (kernel ring buffer) 라고 부르고, 크기는 커널 설정 `CONFIG_LOG_BUF_SHIFT` 로 정하며 부팅 인자 `log_buf_len` 으로 바꿀 수 있습니다[2][14]. 버퍼가 차면 오래된 메시지를 레코드 단위로 통째 덮어씁니다[1].

디스크·USB 장치 인식, 드라이버와 커널 모듈 적재, 프로세스의 세그폴트[3], 커널 오류 보고(Oops)[5] 같은 사건이 이 버퍼에 남습니다. 버퍼는 메모리에만 있어서 꺼지면 사라지지만, systemd-journald 가 `/dev/kmsg` 를 읽어 저널에 옮기고 rsyslog 가 텍스트 파일로도 쓰므로 디스크 이미지에서도 볼 수 있습니다[6][9][10].

커널 메시지만 있는 것도 아닙니다. 사용자 공간 프로그램도 `/dev/kmsg` 에 써서 버퍼에 메시지를 넣을 수 있습니다[1]. 이 경우에는 아래 구조 절에서 설명하는 facility 로 출처를 구분합니다.

## 위치와 버전별 차이

| 항목 | Ubuntu 24.04 LTS | RHEL 9 |
|---|---|---|
| 커널 버퍼 읽는 곳(라이브) | `/dev/kmsg`, `/proc/kmsg`, `dmesg` | 같음 |
| 저널 | journald 가 기본 네임스페이스에서 `/dev/kmsg` 를 읽음(`ReadKMsg=` 기본 켬)[6] | 같음 |
| rsyslog 가 커널 메시지를 받는 길 | `imklog` 모듈, `permitnonkernelfacility="on"`[9] | `imklog` 는 주석 처리돼 있고, 설정 주석대로 같은 메시지를 `imjournal` 로 저널에서 받음[10] |
| 커널 전용 파일 | `/var/log/kern.log` (`kern.*`)[9] | 없음 |
| 함께 들어가는 파일 | `/var/log/syslog` (`*.*;auth,authpriv.none`)[9] | `/var/log/messages` (`*.info;mail.none;authpriv.none;cron.none`)[10] |
| 파일 권한 | `kern.log` 0640, 소유 syslog, 그룹 adm[9] | 분석 대상에서 확인 |
| 순환 | `kern.log` 를 rotate 4, weekly, compress, delaycompress 로 순환[9] | `messages` 가 rsyslog 순환 목록에 있고 주기는 전역 설정을 따름[10] |
| 파일 줄의 시각 | rsyslog 기본 파일 형식([syslog 형식과 rsyslog](../../01-foundations/logging/syslog-rsyslog.md)) | `RSYSLOG_TraditionalFileFormat`[10], 연도·시간대가 없는 옛 형식([syslog 형식과 rsyslog](../../01-foundations/logging/syslog-rsyslog.md)) |

RHEL 9 에는 커널 메시지만 모은 파일이 없어서 `messages` 에서 다른 서비스 줄과 섞여 나옵니다. Ubuntu 에서는 같은 커널 줄이 `kern.log` 와 `syslog` 두 곳에 들어갑니다[9]. 도구가 모으는 경로 정의도 이렇게 나뉘어 있어서, ForensicArtifacts 는 `/var/log/kern*`, `/var/log/messages*`, `/var/log/syslog*` 를 서로 다른 항목으로 둡니다[11]. 순환된 옛 파일의 이름 규칙은 [로그 순환](../../01-foundations/logging/logrotate.md), 저널이 디스크에 남는 조건은 [systemd 저널](../../01-foundations/logging/systemd-journal/index.md) 에서 다룹니다.

## 구조

### kmsg 레코드

`/dev/kmsg` 에서 읽으면 레코드 하나가 한 줄로 나옵니다[1].

```
우선순위,순번,타임스탬프,플래그;본문
```

쉼표로 나뉜 앞부분은 우선순위(syslog 등급과 facility), 64비트 순번, 부팅 뒤 흐른 마이크로초(monotonic), 플래그입니다[1]. 플래그는 기본이 `-` 이고 `c` 는 줄 조각입니다[1]. 세미콜론 뒤가 본문이고 줄바꿈으로 끝나며, 출력할 수 없는 문자와 `\` 는 `\x00` 처럼 16진 이스케이프로 바뀝니다[1]. 공백으로 시작하는 다음 줄은 기계가 읽을 문맥을 `SUBSYSTEM=`·`DEVICE=` 같은 키=값으로 덧붙인 것입니다[1]. 아래는 명세에 실린 예시입니다[1].

```
7,160,424069,-;pci_root PNP0A03:00: host bridge window [io  0x0000-0x0cf7] (ignored)
 SUBSYSTEM=acpi
 DEVICE=+acpi:PNP0A03:00
6,339,5140900,-;NET: Registered protocol family 10
30,340,5690716,-;udevd[80]: starting version 181
```

우선순위 숫자는 아래 3비트가 등급, 그 위 비트가 facility 입니다[1]. `30` 은 facility 3(daemon), 등급 6(info)이라서 마지막 줄은 커널이 아니라 udevd 가 쓴 줄입니다[1][14]. 사용자 공간이 `/dev/kmsg` 에 쓸 때 우선순위를 안 붙이면 facility 가 1(user)이 되고, facility 0(kern)으로는 아예 쓸 수 없습니다[1]. 그래서 facility 가 kern 인 레코드는 커널이 낸 것입니다.

`DEVICE=` 값은 블록 장치 `b12:8`(주·부 번호), 문자 장치 `c127:3`, 네트워크 장치 `n8`(인터페이스 번호), 그 밖의 장치 `+sound:card0`(서브시스템:장치 이름) 형식입니다[1].

### 등급

| 값 | 이름 | 뜻[2] |
|---|---|---|
| 0 | emerg | 시스템을 쓸 수 없음 |
| 1 | alert | 바로 조치해야 함 |
| 2 | crit | 심각한 상태 |
| 3 | err | 오류 |
| 4 | warn(warning) | 경고 |
| 5 | notice | 정상이지만 눈여겨볼 상태 |
| 6 | info | 정보 |
| 7 | debug | 디버그 |

등급을 적지 않은 `printk()` 메시지는 `default_message_loglevel` 을 받고, 이 값은 설정 `CONFIG_DEFAULT_MESSAGE_LOGLEVEL`(기본 4)로 정합니다[2]. `/proc/sys/kernel/printk` 의 네 값은 차례로 `console_loglevel`, `default_message_loglevel`, `minimum_console_loglevel`, `default_console_loglevel` 입니다[5]. 콘솔에 찍히는 등급만 가르는 값이라, 버퍼에는 등급과 상관없이 모두 들어갑니다[2].

### syslog(2) 형식 줄

3.5 미만 커널의 버퍼는 `<등급facility>[   초.마이크로초] 본문` 형식의 줄을 줄바꿈으로 이어 붙인 문자 배열이고, Volatility 3 은 이 줄을 `<(\d+)>\[\s*(\d+\.\d+)\]\s(.*?)$` 정규식으로 나눕니다[14]. `dmesg -r` 은 등급 접두사를 떼지 않고 찍으며, 읽는 방법과 관계없이 `/dev/kmsg` 형식이 아닌 `syslog(2)` 형식으로 냅니다[3]. 만든 예시는 다음과 같습니다.

```
<6>[    5.140900] NET: Registered protocol family 10
```

### 저널에 들어간 커널 메시지

journald 가 커널에서 읽은 항목은 `_TRANSPORT=kernel` 입니다[7]. 커널 항목에는 `_KERNEL_DEVICE=`(kmsg `DEVICE=` 와 같은 b·c·n·+ 표기), `_KERNEL_SUBSYSTEM=`, `_UDEV_SYSNAME=`, `_UDEV_DEVNODE=`, `_UDEV_DEVLINK=` 필드가 붙을 수 있습니다[7]. 저널 항목의 공통 필드와 파일 구조는 [systemd 저널](../../01-foundations/logging/systemd-journal/index.md) 에서 다룹니다.

### taint 값

커널이 정상 상태에서 벗어난 적이 있으면 `/proc/sys/kernel/tainted` 가 0 이 아닌 값이 되고, 각 비트에 해당하는 글자가 Oops 보고의 "Tainted" 줄에 찍힙니다[5]. 조사에 자주 쓰는 비트는 다음과 같습니다[5].

| 값 | 글자 | 뜻 |
|---|---|---|
| 1 | P | 독점 라이선스 모듈을 적재함 |
| 2 | F | 모듈을 강제로 적재함 |
| 8 | R | 모듈을 강제로 제거함 |
| 64 | U | 사용자 공간 프로그램이 taint 를 요청함 |
| 128 | D | 최근 OOPS 나 BUG 로 커널이 죽음 |
| 512 | W | 커널이 경고를 냄 |
| 4096 | O | 트리 밖에서 빌드한 모듈을 적재함 |
| 8192 | E | 서명 없는 모듈을 적재함 |
| 32768 | K | 라이브 패치를 적용함 |

값은 비트를 OR 한 것이라 4096+8192=12288 이면 O 와 E 가 함께 켜진 상태입니다. 모듈 흔적을 해석하는 법은 [커널 모듈](../persistence/kernel-modules.md) 에서 다룹니다.

## 증거로서 의미

### 증명하는 것

커널 로그는 이 부팅에서 부팅 뒤 몇 초에 커널이 장치를 인식했는지, 어떤 모듈을 적재했는지, 어느 프로세스가 세그폴트로 끝났는지를 보여 줍니다. facility 가 kern 인 레코드는 사용자 공간이 흉내 낼 수 없으므로 커널이 낸 기록입니다[1]. 저널에 옮겨진 항목은 부팅 ID 와 함께 저장돼 어느 부팅의 일인지 구분할 수 있습니다([부팅과 종료 기록](boot-shutdown.md)). taint 값에 O·E 비트가 켜져 있으면 이 부팅 동안 트리 밖 모듈이나 서명 없는 모듈이 적재된 적이 있다는 뜻입니다[5].

보고서에는 "이 부팅에서 부팅 뒤 이 시점에 이 장치를 인식한 커널 메시지가 있다" 처럼 기록으로 확인되는 만큼만 씁니다.

### 증명하지 못하는 것

링 버퍼만 볼 때 이미 덮어쓴 메시지는 남지 않습니다[1]. 누가 장치를 꽂았는지, 모듈을 누가 적재했는지는 커널 로그만으로 알 수 없어서 로그인·명령 기록과 맞춰 봐야 합니다. facility 가 user 나 daemon 인 줄은 사용자 공간 프로그램이 쓴 것이라 커널 사건이 아닙니다[1]. `dmesg -T` 로 바꾼 실제 시각은 절전을 거친 시스템에서 틀릴 수 있습니다[3].

## 시각 해석

| 값 | 기준 | 바뀌는 때 |
|---|---|---|
| kmsg 레코드 타임스탬프 | 부팅 뒤 마이크로초(monotonic)[1] | 커널이 레코드를 버퍼에 넣을 때 |
| `dmesg` 기본 출력 | 부팅 뒤 초(`raw`)[3] | 같음 |
| `dmesg -T`, `--time-format iso` | 현지 시각으로 바꾼 값, iso 는 UTC 오프셋 포함[3] | 출력할 때 계산 |
| 저널 `__REALTIME_TIMESTAMP` | UTC 마이크로초[7] | journald 가 항목을 받을 때 |
| 저널 `__MONOTONIC_TIMESTAMP` | monotonic 시계 마이크로초, `_BOOT_ID` 와 짝[7] | 같음 |
| `kern.log`·`messages` 줄 앞 시각 | rsyslog 템플릿이 정한 형식 | rsyslog 가 줄을 쓸 때 |

`dmesg -T` 는 지금의 boottime·monotonic 시계 차이로 타임스탬프를 보정해 사람이 읽는 시각을 냅니다[3]. 절전·복귀 뒤에 이 기준이 갱신되지 않으므로, 마지막 복귀 뒤에 나온 메시지에만 맞습니다[3]. `--time-format iso` 의 `YYYY-MM-DD<T>HH:MM:SS,<microseconds><-+><timezone offset from UTC>` 형식도 같은 문제가 있습니다[3]. 그래서 라이브에서 받은 `dmesg -T` 결과를 보고서의 시각으로 그대로 쓰지 않습니다.

디스크 이미지에서는 저널의 `__REALTIME_TIMESTAMP`(UTC)를 기준으로 삼고, 부팅 뒤 경과 시간은 같은 부팅 안의 순서를 잡는 데 씁니다. 경과 시간을 실제 시각으로 바꾸려면 [부팅과 종료 기록](boot-shutdown.md) 에서 구한 부팅 시각에 더하되, 사이에 절전이 끼었으면 그만큼 어긋납니다. `_SOURCE_BOOTTIME_TIMESTAMP=` 는 systemd 257 에서 생긴 필드라[7] 그보다 낮은 판의 저널에는 없습니다.

RHEL 9 의 `messages` 는 전통 형식이라[10] 연도와 시간대가 없으므로 [호스트 이름·시간대·로캘](hostname-timezone.md) 에서 확인한 시간대와 파일 시각으로 연도를 채웁니다. 시각 값 변환은 [Linux 의 시각 값](../../01-foundations/value-decoding/time-values.md) 에서 다룹니다.

## 함정과 한계

- `journalctl -k`(`--dmesg`)는 `_TRANSPORT=kernel` 을 거르면서 `--boot=0` 을 함께 뜻합니다[8]. 이미지에서 꺼낸 저널을 볼 때 부팅을 지정하지 않으면 마지막 부팅만 나오므로, `--list-boots` 로 부팅을 먼저 뽑고 `-b` 로 하나씩 봅니다([journalctl 로 읽기](../../01-foundations/logging/systemd-journal/journalctl.md)).
- 버퍼를 비우는 `syslog(2)` 명령 `SYSLOG_ACTION_CLEAR`(5)는 버퍼를 실제로 지우지 않고, 전부 읽기(3)·읽고 비우기(4)가 돌려줄 범위만 바꿉니다[2]. `/dev/kmsg` 는 열고 바로 읽으면 버퍼의 첫 메시지부터 주고, `SEEK_DATA` 를 써야 마지막 CLEAR 뒤로 건너뜁니다[1]. 그래서 `dmesg -C` 뒤에도 덮어쓰이기 전의 메시지는 버퍼에 남아 있을 가능성이 있고, 메모리 이미지로 확인할 수 있습니다.
- `/proc/kmsg` 읽기는 읽은 바이트가 버퍼에서 사라지는 읽기라 한 번만 읽을 수 있습니다[2]. 루트만 읽을 수 있고 한 프로세스만 읽어야 하므로[4], 라이브 수집에서는 이 파일을 열지 않고 `dmesg` 를 씁니다.
- `/proc/sys/kernel/dmesg_restrict` 가 1 이면 `CAP_SYSLOG` 가 없는 사용자는 `dmesg` 를 못 씁니다[5]. `dmesg` 가 권한 거부로 끝나는 이유는 대개 이 설정입니다[3].
- 라이브 수집 중에 받은 `dmesg` 에는 수집하면서 생긴 메시지도 섞일 수 있습니다. 메모리 수집 도구가 커널 모듈을 적재하는 경우가 그 예이고, 이는 [메모리 수집](../../03-techniques/acquisition/memory-acquisition.md) 에서 다룹니다.
- Ubuntu 의 `imklog` 는 `permitnonkernelfacility="on"` 이라[9] kmsg 에 들어간 사용자 공간 줄도 rsyslog 로 넘어가고, facility 규칙에 따라 `kern.log` 가 아닌 파일로 갈 수 있습니다. journald 도 `ForwardToKMsg=` 를 켜면 저널 메시지를 kmsg 로 보내지만, systemd 기본값은 wall 전달만 켜져 있습니다[6].
- 등급 이름 표기가 도구마다 다릅니다. Volatility 3 은 `warn`[14], `syslog(2)` 문서는 `KERN_WARNING`[2] 으로 적습니다.
- dissect 의 messages 플러그인은 `/var/log/` 와 `/var/log/installer/` 에서 `syslog*`, `messages*`, `cloud-init.log*` 만 읽고 `kern.log` 는 읽지 않습니다[12]. Ubuntu 에서는 같은 줄이 `syslog` 에도 있지만, `kern.log` 에만 남은 순환본을 놓치지 않도록 따로 봅니다.

## 직접 분석해 보기

### 헥스로 한 번: kmsg 레코드

아래는 명세의 예시 레코드 한 줄을 바이트로 적은 것입니다(명세로 만든 예시).

```
00000000: 3330 2c33 3430 2c35 3639 3037 3136 2c2d  30,340,5690716,-
00000010: 3b75 6465 7664 5b38 305d 3a20 7374 6172  ;udevd[80]: star
00000020: 7469 6e67 2076 6572 7369 6f6e 2031 3831  ting version 181
00000030: 0a                                       .
```

1. 첫 쉼표(0x02) 앞 `33 30` 은 ASCII "30" 입니다. 30 을 2진수로 풀면 아래 3비트가 6(info), 나머지 30÷8=3 이 facility daemon 입니다. facility 가 0 이 아니라서 커널이 아닌 사용자 공간 프로그램이 쓴 레코드입니다[1].
2. 두 번째 필드 "340" 은 순번입니다. 앞 레코드 순번이 339 라면 그 사이에 잃은 레코드는 없습니다. 순번이 건너뛰면 버퍼가 그만큼 덮어써졌다는 뜻입니다[1].
3. 세 번째 필드 "5690716" 은 부팅 뒤 5,690,716마이크로초, 곧 5.690716초입니다[1].
4. 0x0F 의 `2d`(`-`)는 조각이 아닌 온전한 레코드라는 표시이고, 0x10 의 `3b`(`;`) 뒤부터 0x30 의 `0a` 앞까지가 본문입니다[1].

라이브에서 버퍼를 이 형식 그대로 받으려면 `dd if=/dev/kmsg iflag=nonblock` 처럼 `/dev/kmsg` 를 직접 읽습니다[3].

### 공개 도구로 한 번

```
dmesg -x --time-format raw
dmesg -K kmsg-saved.bin -x
journalctl -D /mnt/evidence/var/log/journal --list-boots
journalctl -D /mnt/evidence/var/log/journal -k -b -3 -o short-iso
journalctl -D /mnt/evidence/var/log/journal _TRANSPORT=kernel -o verbose
vol -f memory.lime linux.kmsg
```

`dmesg -x` 는 facility 와 등급을 이름으로 풀어 찍고, `-k`·`-u` 로 커널 메시지와 사용자 공간 메시지를 나눠 볼 수 있습니다[3]. `-K` 는 저장해 둔 kmsg 형식 파일을 읽으며 레코드는 NUL 바이트로 구분돼 있어야 하고, `-F` 는 syslog 형식 파일을 읽습니다[3]. `-J` 는 JSON 으로 내고 시각은 `sec.usec` 형식으로만 나옵니다[3]. UAC 는 라이브에서 `dmesg` 결과와 `/proc/sys/kernel/tainted`, `dmesg | grep -i taint`, `grep "(.*)" /proc/modules` 결과를 받습니다[13].

저널에서는 `-k` 로 커널 항목만 거르고 `-b` 로 부팅을 고릅니다[8]. `-o verbose` 로 보면 `_KERNEL_DEVICE`·`_KERNEL_SUBSYSTEM` 필드까지 나와 어느 장치의 메시지인지 구분할 수 있습니다[7][8].

메모리 이미지에서는 Volatility 3 의 `linux.kmsg` 가 커널 판에 맞춰 버퍼 구조를 고릅니다[14]. 3.5 미만은 문자 배열 `log_buf`, 3.5~3.11 은 구조체 `log`, 3.11~5.10 은 `printk_log`, 5.10 부터는 설명자 링과 본문 링으로 나뉜 `printk_ringbuffer` 를 읽습니다[14]. 5.10 이상에서는 설명자 상태가 committed 나 finalized 인 레코드만 냅니다[14]. 출력 열은 facility, level, timestamp(`초.마이크로초`), caller, 본문이고, caller 는 호출한 CPU 나 태스크를 `CPU(n)`·`Task(pid)` 로 적고, 판에 따라 커널을 `CONFIG_PRINTK_CALLER` 로 빌드했을 때만 나옵니다[14]. 메모리 분석의 일반 절차는 [메모리 분석](../../03-techniques/analysis/memory-analysis.md) 에서 다룹니다.

## 교차 검증

| 맞춰 볼 기록 | 확인할 것 |
|---|---|
| 커널 로그 장치 인식 ↔ [USB 장치 연결 기록](../devices/usb.md)·[마운트 기록](../devices/mounts.md) | 장치를 인식한 시점과 마운트한 시점 |
| taint 비트·모듈 적재 메시지 ↔ [커널 모듈](../persistence/kernel-modules.md) | 트리 밖·서명 없는 모듈이 어떤 파일에서 왔는지 |
| 저널 커널 항목 ↔ `kern.log`·`messages` | 같은 메시지가 두 곳에 있는지. 한쪽에만 없으면 파일 삭제·순환 가능성 |
| 커널 로그 첫 줄 ↔ [부팅과 종료 기록](boot-shutdown.md) | 부팅 시각의 일치, 경과 시간을 실제 시각으로 바꿀 기준 |
| 메모리의 `linux.kmsg` ↔ 디스크의 저널 | 디스크에 없는 최근 메시지, 비운 뒤 남은 메시지 |

누가 로그를 지웠는지 판단하는 흐름은 [흔적을 지웠나](../../04-scenarios/insider/anti-forensics.md), 여러 로그를 시간순으로 합치는 법은 [타임라인 만들기](../../03-techniques/analysis/timeline.md) 와 [로그 분석](../../03-techniques/analysis/log-analysis.md) 에서 다룹니다.

## 실습

NIST CFReDS 등에 공개된 Linux 디스크·메모리 이미지로 다음 질문을 풀어 봅니다.

1. 저널에 커널 항목(`_TRANSPORT=kernel`)이 있는 부팅은 몇 번이고, 각 부팅의 커널 첫 메시지 시각은 언제인가?
2. `kern.log`(Ubuntu) 또는 `messages`(RHEL)의 커널 줄과 저널의 커널 항목은 같은 기간을 덮는가?
3. 이동식 저장 장치를 인식한 커널 메시지가 있다면, 그 부팅의 부팅 뒤 경과 시간과 저널의 실제 시각은 각각 얼마인가?
4. 커널 로그에 taint 를 언급한 줄이 있는가? 있다면 어떤 모듈 때문인가?
5. 메모리 이미지가 있다면 `linux.kmsg` 결과에만 있고 디스크 저널에는 없는 메시지가 있는가?

## 참고 문헌

1. Linux kernel, Documentation/ABI/testing/dev-kmsg. https://github.com/torvalds/linux/blob/master/Documentation/ABI/testing/dev-kmsg
2. syslog(2), Linux man-pages. https://github.com/mkerrisk/man-pages/blob/master/man2/syslog.2
3. util-linux, dmesg(1). https://github.com/util-linux/util-linux/blob/master/sys-utils/dmesg.1.adoc
4. proc(5), Linux man-pages. https://github.com/mkerrisk/man-pages/blob/master/man5/proc.5
5. Linux kernel, Documentation/admin-guide/sysctl/kernel.rst. https://github.com/torvalds/linux/blob/master/Documentation/admin-guide/sysctl/kernel.rst
6. systemd, man/journald.conf.xml. https://github.com/systemd/systemd/blob/main/man/journald.conf.xml
7. systemd, man/systemd.journal-fields.xml. https://github.com/systemd/systemd/blob/main/man/systemd.journal-fields.xml
8. systemd, man/journalctl.xml. https://github.com/systemd/systemd/blob/main/man/journalctl.xml
9. rsyslog-pkg-ubuntu, noble 패키지 설정(rsyslog.conf·50-default.conf·00rsyslog.conf·rsyslog.logrotate). https://github.com/rsyslog/rsyslog-pkg-ubuntu/tree/master/rsyslog/noble/v8-stable/debian
10. CentOS Stream 9 rsyslog 패키지, rsyslog.conf·rsyslog.log. https://gitlab.com/redhat/centos-stream/rpms/rsyslog/-/blob/c9s/rsyslog.conf , https://gitlab.com/redhat/centos-stream/rpms/rsyslog/-/blob/c9s/rsyslog.log
11. ForensicArtifacts, artifacts/data/linux.yaml. https://github.com/ForensicArtifacts/artifacts/blob/main/artifacts/data/linux.yaml
12. fox-it dissect.target, dissect/target/plugins/os/unix/log/messages.py. https://github.com/fox-it/dissect.target/blob/main/dissect/target/plugins/os/unix/log/messages.py
13. UAC, artifacts/live_response/hardware/dmesg.yaml·system/kernel_tainted_state.yaml. https://github.com/tclahr/uac/tree/main/artifacts
14. Volatility 3, volatility3/framework/plugins/linux/kmsg.py. https://github.com/volatilityfoundation/volatility3/blob/develop/volatility3/framework/plugins/linux/kmsg.py
