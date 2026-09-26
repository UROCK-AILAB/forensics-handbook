---
title: "로그인 기록 파일 형식"
parent: "기반 · 로그 체계"
nav_order: 250
---

# 로그인 기록 파일 형식 (utmp·wtmp·btmp·lastlog)

utmp·wtmp·btmp 는 같은 고정 길이 이진 레코드를 차례로 붙인 파일이고, lastlog 는 UID 를 번호로 삼아 사용자마다 마지막 로그인 한 건만 두는 별도 형식입니다.

## 이 형식을 쓰는 아티팩트

네 파일은 이름이 비슷하지만 담는 내용과 수명이 다릅니다. utmp 는 "지금 누가 로그인해 있는가" 를 담고, 세션이 끝나면 같은 칸을 고쳐 씁니다[1]. wtmp 는 로그인·로그아웃·재부팅·종료를 계속 덧붙이는 이력 파일이고, 형식은 utmp 와 똑같습니다[1]. btmp 는 실패한 로그인 시도를 같은 형식으로 덧붙이며 `lastb` 가 읽습니다[6][8]. lastlog 는 사용자마다 마지막 로그인 한 건만 남깁니다[9].

| 파일 | 경로 | systemd tmpfiles 줄 | 담는 것 |
|---|---|---|---|
| utmp | `/run/utmp` (`/var/run` 은 `../run` 을 가리키는 링크라서 `/var/run/utmp` 로도 보임) | `f+! /run/utmp 0664 root utmp -` | 지금 열린 세션 |
| wtmp | `/var/log/wtmp` | `f /var/log/wtmp 0664 root utmp -` | 로그인·로그아웃·부팅·종료 이력 |
| btmp | `/var/log/btmp` | `f /var/log/btmp 0660 root utmp -` | 실패한 로그인 시도 |
| lastlog | `/var/log/lastlog` | `f /var/log/lastlog 0664 root utmp -` | UID 별 마지막 로그인 |

위 tmpfiles 줄은 upstream systemd 기준이고, systemd 를 utmp 지원(`ENABLE_UTMP`)으로 빌드했을 때만 들어갑니다[2]. RHEL 9 의 systemd 소스(252판)는 wtmp·btmp·lastlog 세 줄이 같고, utmp 줄만 예전 표기인 `F! /run/utmp 0664 root utmp -` 로 쓰는데 `F` 는 `f+` 와 같은 뜻입니다[4]. `f` 는 파일이 없을 때만 만들고, `f+` 는 만들거나 길이를 0으로 자르며, `!` 가 붙은 줄은 부팅 때만 실행합니다[3]. 그래서 utmp 는 부팅할 때마다 비워지고, btmp 는 권한이 0660 이라 root 와 utmp 그룹이 아닌 사용자는 읽을 수 없습니다[2].

새 배포판에는 이진 파일 대신 SQLite 를 쓰는 형식도 있습니다. wtmpdb 는 `/var/lib/wtmpdb/` 아래 `.db` 파일의 `wtmp` 테이블에 `Login`·`Logout`(마이크로초)·`Type`·`User`·`TTY`·`RemoteHost`·`Service` 열을 두고, lastlog2 는 `/var/lib/lastlog/lastlog2.db` 의 `Lastlog2` 테이블에 `Name`·`Time`·`TTY`·`RemoteHost`·`Service` 열을 둡니다[13][14]. wtmpdb 의 `Type` 은 0 EMPTY, 1 BOOT_TIME, 2 RUNLEVEL, 3 USER_PROCESS 로, utmp 의 번호와 다릅니다[13]. Ubuntu 24.04 와 RHEL 9 검체에서는 두 파일이 있는지부터 확인하고, 있으면 SQLite 로 엽니다([SQLite 데이터베이스](https://urock-ailab.github.io/forensics-handbook/windows/01-foundations/database-log-formats/sqlite/index.html)).

## 구조

### utmp 레코드 (utmp·wtmp·btmp 공통)

파일 머리는 없고 레코드가 처음부터 끝까지 이어집니다[1]. x86-64 처럼 64비트이면서 32비트 시각 호환을 켠 환경과 32비트 환경에서는 레코드 하나가 384바이트이고, 정수는 리틀 엔디언입니다[1][12][15].

| 오프셋 | 크기 | 필드 | 뜻 |
|---|---|---|---|
| 0 | 2 (+2 채움) | `ut_type` | 레코드 종류 (아래 표) |
| 4 | 4 | `ut_pid` | 로그인 프로세스 PID |
| 8 | 32 | `ut_line` | 터미널 장치 이름에서 `/dev/` 를 뺀 것 (`pts/0`, `tty1`) |
| 40 | 4 | `ut_id` | 터미널 이름 끝부분 또는 inittab ID |
| 44 | 32 | `ut_user` | 사용자 이름 |
| 76 | 256 | `ut_host` | 원격 호스트 이름, 런레벨 레코드에서는 커널 버전 |
| 332 | 2 + 2 | `ut_exit` | `e_termination`, `e_exit` (DEAD_PROCESS 용, Linux init 은 쓰지 않음) |
| 336 | 4 | `ut_session` | 세션 ID |
| 340 | 4 | `ut_tv.tv_sec` | 기록 시각, Unix epoch 초 |
| 344 | 4 | `ut_tv.tv_usec` | 기록 시각의 마이크로초 |
| 348 | 16 | `ut_addr_v6` | 원격 주소, IPv4 는 첫 4바이트만 씀 |
| 364 | 20 | `__unused` | 예비 |

문자열 필드는 칸보다 짧으면 NUL 로 끝나고, 칸을 꽉 채우면 NUL 이 없습니다[1]. 그래서 사용자 이름과 터미널 이름은 32바이트, 호스트 이름은 256바이트를 넘는 부분이 잘려 저장됩니다[6].

이 레이아웃은 기계에 따라 다릅니다[1]. aarch64 처럼 32비트 시각 호환이 없는 64비트 환경에서는 `ut_session`·`tv_sec`·`tv_usec` 가 각각 8바이트가 되어 레코드가 400바이트이고, s390x 처럼 빅 엔디언인 64비트 환경도 있습니다[12]. 400바이트 레이아웃에서는 336 에 세션(8), 344 에 초(8), 352 에 마이크로초(8), 360 에 주소(16), 376 에 예비(24)가 옵니다[12].

`ut_type` 값은 다음과 같습니다[1].

| 값 | 이름 | 뜻 |
|---|---|---|
| 0 | EMPTY | 유효한 정보 없음 |
| 1 | RUN_LVL | 런레벨 바뀜 |
| 2 | BOOT_TIME | 부팅 시각 |
| 3 | NEW_TIME | 시계를 바꾼 뒤 시각 |
| 4 | OLD_TIME | 시계를 바꾸기 전 시각 |
| 5 | INIT_PROCESS | init 이 띄운 프로세스 |
| 6 | LOGIN_PROCESS | 사용자 로그인을 맡은 세션 리더 프로세스 |
| 7 | USER_PROCESS | 로그인한 사용자 프로세스 |
| 8 | DEAD_PROCESS | 끝난 프로세스 |
| 9 | ACCOUNTING | 구현되지 않음 |

### wtmp 만의 약속

wtmp 는 utmp 와 형식이 같지만 몇 가지 약속이 더 있습니다[1]. 사용자 이름이 빈 레코드는 그 터미널에서 로그아웃했다는 뜻입니다. 터미널 이름이 `~` 이고 사용자 이름이 `reboot` 나 `shutdown` 이면 재부팅이나 종료입니다. 터미널 이름 `|` 와 `}` 한 쌍은 `date` 로 시계를 바꿀 때 바꾸기 전과 바꾼 뒤 시각을 남긴 것입니다. 부팅할 때마다 `reboot` 라는 가짜 사용자가 로그인하므로 `last reboot` 로 부팅 이력을 볼 수 있습니다[6]. systemd 환경에서는 systemd-update-utmp 가 재부팅과 종료 요청을 utmp·wtmp 와 감사 로그에 씁니다[5].

### 누가 언제 쓰나

utmp 칸 하나는 수명 동안 여러 번 고쳐 쓰입니다[1]. init 이 INIT_PROCESS 로 칸을 만들고, getty 가 PID 로 칸을 찾아 LOGIN_PROCESS 로 바꾸고 `ut_line` 을 채웁니다. login 은 인증이 끝나면 USER_PROCESS 로 바꾸고 `ut_host`·`ut_addr` 를 채웁니다. 프로세스가 끝나면 init 이 DEAD_PROCESS 로 바꾸고 `ut_user`·`ut_host`·시각을 NUL 로 지웁니다. util-linux 의 login 은 utmp 칸을 고친 뒤 같은 레코드를 wtmp 끝에 덧붙입니다[8].

btmp 레코드도 util-linux 의 login 이 인증에 실패할 때 씁니다[8]. 종류 칸에는 LOGIN_PROCESS 를 넣지만 이 값에는 뜻이 없고, 사용자 이름·터미널·`ut_id`·시각(초와 마이크로초)·PID·호스트와 주소를 채웁니다[8]. 없는 사용자로 실패하면 `/etc/login.defs` 의 `LOG_UNKFAIL_ENAB` 이 꺼져 있을 때(기본값) 이름 대신 `(unknown)` 을 넣습니다[8].

### lastlog 레코드

lastlog 는 UID 번째 칸에 그 사용자의 마지막 로그인을 두는 파일이라, 레코드 오프셋은 `UID × 292` 입니다[14]. 레코드 하나는 다음과 같습니다[8][14].

| 오프셋 | 크기 | 필드 | 뜻 |
|---|---|---|---|
| 0 | 4 | `ll_time` | 마지막 로그인 시각, Unix epoch 초 |
| 4 | 32 | `ll_line` | 터미널 (`pts/0` 등) |
| 36 | 256 | `ll_host` | 원격 호스트 |

`ll_time` 이 0 이면 로그인 기록이 없는 칸입니다[14]. 이 파일은 희소 파일(sparse file)이라서 UID 가 큰 사용자가 있으면 `ls -l` 로 보는 크기가 커지지만, 디스크에서 실제로 쓰는 공간은 작고 `ls -s` 로 확인합니다[9]. 292바이트는 시각 필드가 4바이트일 때의 크기이고[14], 시각 필드가 더 큰 환경에서는 레코드 크기도 다를 가능성이 있습니다.

lastlog 는 pam_lastlog 가 세션 단계에서 갱신합니다[11]. `/etc/login.defs` 의 `LASTLOG_UID_MAX` 보다 큰 UID 는 갱신하지 않고, `noupdate` 옵션이면 어떤 파일도 갱신하지 않으며, `nowtmp` 옵션이면 wtmp 를 쓰지 않습니다[11]. 실패 횟수와 한도를 담는 shadow 의 `/var/log/faillog` 는 이와 다른 별도 파일입니다[10].

## 읽는 법

### 헥스로 한 번

아래는 명세대로 만든 384바이트 USER_PROCESS 레코드입니다(만든 예시: 사용자 `alice`, 터미널 `pts/0`, 호스트 `192.0.2.10`, PID 0x1234). 0으로만 된 줄은 `*` 로 줄였습니다.

```
00000000: 0700 0000 3412 0000 7074 732f 3000 0000  ....4...pts/0...
00000010: 0000 0000 0000 0000 0000 0000 0000 0000  ................
00000020: 0000 0000 0000 0000 3000 0000 616c 6963  ........0...alic
00000030: 6500 0000 0000 0000 0000 0000 0000 0000  e...............
00000040: 0000 0000 0000 0000 0000 0000 3139 322e  ............192.
00000050: 302e 322e 3130 0000 0000 0000 0000 0000  0.2.10..........
00000060: 0000 0000 0000 0000 0000 0000 0000 0000  ................
*
00000150: 3412 0000 00b9 5569 90d0 0300 c000 020a  4.....Ui........
00000160: 0000 0000 0000 0000 0000 0000 0000 0000  ................
00000170: 0000 0000 0000 0000 0000 0000 0000 0000  ................
```

1. 0x00 의 `07 00` 이 `ut_type` 7(USER_PROCESS)이고, 0x04 의 `34 12 00 00` 이 PID 0x1234 입니다.
2. 0x08 부터 `pts/0`, 0x28(40) 에 `ut_id`, 0x2C(44) 부터 사용자 이름 `alice`, 0x4C(76) 부터 호스트 `192.0.2.10` 이 NUL 로 끝납니다.
3. 0x150(336) 의 `34 12 00 00` 이 세션 ID 0x1234, 0x154(340) 의 `00 b9 55 69` 가 리틀 엔디언으로 0x6955B900 = 1767225600 초이고 2026-01-01 00:00:00 UTC 입니다. 0x158(344) 의 `90 d0 03 00` 은 250000 마이크로초라서 기록 시각은 00:00:00.25 UTC 입니다.
4. 0x15C(348) 의 `c0 00 02 0a` 가 IPv4 주소 192.0.2.10 이고, 뒤 12바이트는 0 입니다.

lastlog 는 UID 를 알면 곧바로 칸을 찾아갑니다. UID 1000 이면 1000 × 292 = 292000 = 0x474A0 입니다. 아래도 명세대로 만든 예시입니다.

```
000474a0: 00b9 5569 7074 732f 3000 0000 0000 0000  ..Uipts/0.......
000474b0: 0000 0000 0000 0000 0000 0000 0000 0000  ................
000474c0: 0000 0000 3139 322e 302e 322e 3130 0000  ....192.0.2.10..
```

처음 4바이트가 마지막 로그인 시각(2026-01-01 00:00:00 UTC), 이어서 터미널 `pts/0`, 0x474C4(칸 안 36) 부터 호스트입니다. 이 칸이 어느 사용자인지는 `/etc/passwd` 의 UID 로 잇습니다([UID·GID 와 사용자 이름 잇기](../value-decoding/uid-gid.md)).

### 명령으로 한 번

수집한 파일은 `-f` 로 넘겨 읽습니다. `last` 는 기본으로 `/var/log/wtmp` 를, `lastb` 는 `/var/log/btmp` 를 읽고, `-f` 는 여러 번 줄 수 있습니다[6].

```
last -f wtmp -F -w -x -i
last -f wtmp --time-format iso
lastb -f btmp -F -w
utmpdump wtmp
```

`-F` 는 날짜와 시각을 모두 보여 주고, `-w` 는 이름을 자르지 않고, `-x` 는 종료와 런레벨 변화까지 보여 주고, `-i` 는 호스트 대신 IP 를 보여 줍니다[6]. `--time-format iso` 는 시간대가 붙은 ISO-8601 로 찍어서, 다른 시스템에서 결과를 볼 때 알맞습니다[6]. `utmpdump` 는 레코드를 가공 없이 텍스트로 보여 줍니다[7]. util-linux 2.28 까지는 `ctime` 형식으로 찍었고, 그 뒤 판은 밀리초까지 있는 ISO-8601 UTC 로 찍습니다[7].

`lastlog` 명령은 실행한 시스템의 `/etc/passwd` 순서로 출력합니다[9]. 떼어 온 파일은 위처럼 UID 칸을 직접 읽거나, 마운트한 이미지의 루트를 `-R` 로 지정하거나, passwd 와 함께 읽는 도구를 씁니다[9][14].

## 포렌식에서 중요한 점

### 증명하는 것

wtmp 의 USER_PROCESS 레코드는 그 시각에 그 터미널·호스트에서 그 이름으로 세션이 열렸다는 기록입니다[1]. 로그아웃은 같은 터미널의 이름 빈 레코드나 DEAD_PROCESS 레코드로 짝을 짓습니다[1]. btmp 레코드는 그 이름으로 로그인에 실패한 시도가 있었다는 기록입니다[8]. lastlog 는 UID 마다 마지막으로 로그인한 시각·터미널·호스트 한 건을 보여 줍니다[9].

### 증명하지 못하는 것

파일이 없다고 로그인이 없었던 것은 아닙니다. 이 파일들을 쓰는 프로그램은 파일을 만들지 않으므로, 파일이 지워지면 기록이 그냥 멈춥니다[1][6]. 반대로 systemd-tmpfiles 는 부팅 때 파일이 없으면 빈 파일로 다시 만들어서[3][19], 지웠던 wtmp 가 다음 부팅 뒤에 빈 파일로 다시 있을 수 있습니다. 모든 프로그램이 utmp 에 기록하지도 않고[1], pam_lastlog 를 `nowtmp`·`noupdate` 로 설정하면 해당 파일이 갱신되지 않습니다[11].

btmp 의 사용자 이름은 실제 계정이 아니라 입력한 문자열입니다[8]. 로그인 실패 가운데 가장 흔한 것은 사용자 이름 자리에 비밀번호를 넣는 경우라서, util-linux 의 login 은 `LOG_UNKFAIL_ENAB` 이 꺼져 있으면 없는 이름을 `(unknown)` 으로 바꿔 넣습니다[8]. 이 설정을 켠 시스템의 btmp 에는 비밀번호가 사용자 이름 칸에 남아 있을 가능성이 있습니다. lastlog 는 마지막 한 건만 남기고 이전 로그인은 덮어씁니다[9]. 또 `lastlog -S -u 사용자` 는 현재 시각으로 설정하고 `lastlog -C -u 사용자` 는 그 칸을 지우므로, 관리자가 값을 바꿀 수 있습니다[9].

### 시각 해석

`ut_tv` 와 `ll_time` 은 Unix epoch 기준 초라서 UTC 로 읽고, 현지 시각은 검체의 시간대 설정으로 따로 바꿉니다[1][12]([Linux 의 시각 값](../value-decoding/time-values.md)). 시각은 레코드를 쓴 순간의 시스템 시계이므로, 시계를 바꾸면 그 뒤 레코드의 시각도 함께 바뀝니다. 시계를 바꾼 흔적은 wtmp 의 `|`·`}` 레코드(OLD_TIME·NEW_TIME)로 남을 수 있습니다[1]([시각을 조작했나](../../04-scenarios/insider/time-manipulation.md)).

### 지운 데이터·손상

utmp 는 부팅 때마다 비워지므로 지난 부팅의 세션은 남지 않습니다[2][3]. 전원을 끈 뒤 만든 디스크 이미지에서는 비어 있거나 없을 가능성이 있어, 라이브 수집 때 따로 받습니다[17]. utmp 칸에서 세션이 끝나면 사용자 이름·호스트·시각을 NUL 로 지우므로, 지난 세션의 정보는 wtmp 에서 찾습니다[1].

`utmpdump -r` 은 텍스트로 뽑아 고친 내용을 다시 이진 파일로 되돌리는 기능이고, 디버깅용으로만 만든 기능입니다[7]. `utmpdump` 의 텍스트 출력은 기록 조작을 살피는 데 쓰이고[17], 다시 쓴 wtmp 인지는 아래 교차 검증 로그와 대조해 가립니다. 2.28 까지의 판이 찍은 `ctime` 텍스트를 이진으로 되돌리면 시각이 시간대 차이만큼 밀릴 수 있습니다[7]. 레코드가 시간대 차이만큼 한꺼번에 밀려 있으면 이렇게 다시 쓴 파일일 가능성이 있습니다.

## 함정

- 레코드 크기를 맞춰야 합니다. aarch64 검체의 400바이트 레코드를 384바이트로 읽으면 두 번째 레코드부터 필드가 어긋납니다[12]. 파일 크기가 384 와 400 중 어느 쪽으로 나누어떨어지는지 먼저 봅니다.
- 도구마다 값을 바꿔 보여 줍니다. plaso 는 터미널 `~` 를 `system boot` 로, 빈 호스트와 `:0` 을 `localhost` 로 바꿔 출력합니다[12]. dissect 는 마이크로초를 버리고 초만 쓰며, IPv4 인지 IPv6 인지를 `ut_host` 문자열로 가늠합니다[13].
- `last` 의 기본 출력은 사용자 이름을 8자, 호스트를 16자에서 자르고 끝에 `*` 를 붙이므로 `-w` 를 줍니다[6].
- 빈 레코드와 0으로만 채운 파일은 오류가 아니라 유효한 형식입니다[6].
- wtmp 와 btmp 는 로그 순환(logrotate) 대상입니다. logrotate 의 upstream 예시 설정은 둘 다 월 단위로 순환하고 한 세대만 남기며, wtmp 에는 `minsize 1M` 이 붙어 있습니다[18]. `wtmp.1` 이나 날짜가 붙은 이름, `.gz` 압축본까지 모읍니다([로그 순환](logrotate.md)).
- lastlog 는 순환하면 안 되는 파일이고, 희소 파일을 알아보지 못하는 도구는 따로 옵션을 줘야 제대로 다룹니다[9].
- lastlog 는 현재 passwd 에 있는 사용자만 출력하므로, 지운 계정의 칸이 파일에 남아 있어도 `lastlog` 명령으로는 보이지 않습니다[9].

## 도구

| 도구 | 읽는 파일 | 참고 |
|---|---|---|
| util-linux `last`·`lastb`·`utmpdump` | wtmp·btmp·utmp | 수집한 파일은 `-f`, 압축본은 `zcat` 으로 풀어 넘김[6][7][17] |
| shadow `lastlog` | `/var/log/lastlog` | 실행 중인 시스템의 passwd 기준[9] |
| plaso `utmp` 파서 | utmp·wtmp·btmp | 첫 16개 레코드로 384·400바이트·빅 엔디언 레이아웃을 가려내고, 깨진 레코드는 건너뜀[12] |
| dissect.target `wtmp`·`btmp`·`lastlog` | `var/log/wtmp*`, `var/lib/wtmpdb/wtmp*`, `var/run/utmp*`, `var/log/btmp*`, `var/log/lastlog*`, `var/lib/lastlog/lastlog2*` | wtmp·btmp 는 압축본도 열고, 384바이트 레이아웃만 읽음[13][14] |
| Velociraptor `Linux.Sys.LastUserLogin` | `/var/log/wtmp*` | 384바이트 프로필, 기본은 USER_PROCESS·LOGIN_PROCESS 만, 같은 PID·터미널의 DEAD_PROCESS 로 로그아웃 시각을 짝지음[15] |
| ForensicArtifacts `LinuxUtmpFiles`·`LinuxWtmp`·`LinuxLastlogFile` | `/var/log/btmp*`, `/var/log/wtmp*`, `/var/run/utmp*`, `/var/log/lastlog` | 수집 경로 정의[16] |
| UAC | `/var/run/utmp` 파일, `last`·`lastb`·`lastlog`·`utmpdump` 실행 결과 | 라이브 수집[17] |

교차 검증에는 인증 로그의 sshd·PAM 줄([인증 로그](../../02-artifacts/logins/auth-log.md)), 감사 로그의 로그인 이벤트([감사 로그 형식](auditd-format.md)), 저널의 systemd-logind 세션 기록([systemd 저널](systemd-journal/index.md))을 씁니다. 조사에서 이 파일들을 어떻게 해석하는지는 [로그인 기록](../../02-artifacts/logins/wtmp-btmp-lastlog.md)에서, 다른 기록과 시간순으로 엮는 방법은 [타임라인 만들기](../../03-techniques/analysis/timeline.md)에서 다룹니다.

## 참고 문헌

1. utmp(5), Linux man-pages. https://github.com/mkerrisk/man-pages/blob/master/man5/utmp.5
2. systemd, `tmpfiles.d/systemd.conf.in`·`tmpfiles.d/var.conf.in`. https://github.com/systemd/systemd/tree/main/tmpfiles.d
3. systemd, tmpfiles.d(5). https://github.com/systemd/systemd/blob/main/man/tmpfiles.d.xml
4. RHEL 9 systemd source-git(252), `tmpfiles.d/var.conf.in`·`tmpfiles.d/systemd.conf.in`·`src/tmpfiles/tmpfiles.c`. https://github.com/redhat-plumbers/systemd-rhel9
5. systemd, systemd-update-utmp.service(8). https://github.com/systemd/systemd/blob/main/man/systemd-update-utmp.service.xml
6. util-linux, last(1). https://github.com/util-linux/util-linux/blob/master/login-utils/last.1.adoc
7. util-linux, utmpdump(1). https://github.com/util-linux/util-linux/blob/master/login-utils/utmpdump.1.adoc
8. util-linux, `login.c`. https://github.com/util-linux/util-linux/blob/master/login-utils/login.c
9. shadow, lastlog(8). https://github.com/shadow-maint/shadow/blob/master/man/lastlog.8.xml
10. shadow, faillog(8). https://github.com/shadow-maint/shadow/blob/master/man/faillog.8.xml
11. Linux-PAM, pam_lastlog(8). https://github.com/linux-pam/linux-pam/blob/master/modules/pam_lastlog/pam_lastlog.8.xml
12. plaso, `parsers/utmp.py`·`parsers/utmp.yaml`. https://github.com/log2timeline/plaso/blob/main/plaso/parsers/utmp.py
13. dissect.target, `plugins/os/unix/log/utmp.py`. https://github.com/fox-it/dissect.target/blob/main/dissect/target/plugins/os/unix/log/utmp.py
14. dissect.target, `plugins/os/unix/log/lastlog.py`. https://github.com/fox-it/dissect.target/blob/main/dissect/target/plugins/os/unix/log/lastlog.py
15. Velociraptor, `Linux/Sys/LastUserLogin.yaml`. https://github.com/Velocidex/velociraptor/blob/master/artifacts/definitions/Linux/Sys/LastUserLogin.yaml
16. ForensicArtifacts, `artifacts/data/linux.yaml`. https://github.com/ForensicArtifacts/artifacts/blob/main/artifacts/data/linux.yaml
17. UAC, `artifacts/files/system/utmp.yaml`, `live_response/system/last.yaml`·`lastb.yaml`·`lastlog.yaml`·`utmpdump.yaml`. https://github.com/tclahr/uac/tree/main/artifacts
18. logrotate, `examples/wtmp`·`examples/btmp`. https://github.com/logrotate/logrotate/tree/main/examples
19. systemd, systemd-tmpfiles(8). https://github.com/systemd/systemd/blob/main/man/systemd-tmpfiles.xml
