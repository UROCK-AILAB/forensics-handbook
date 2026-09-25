---
title: "로그인 기록"
parent: "아티팩트 · 로그인과 계정"
nav_order: 330
---

# 로그인 기록 (wtmp·btmp·lastlog)

wtmp 는 대화형 로그인·로그아웃·부팅 이력을, btmp 는 실패한 로그인 시도를, lastlog 는 계정마다 마지막 로그인 한 건을 담는 이진 파일이고, 어느 프로그램이 어떤 경우에 쓰는지 알아야 "기록이 없다" 를 바르게 읽을 수 있습니다.

## 무엇을 기록하나 · 왜 생기나

이 파일들은 한 데몬이 모아 쓰는 로그가 아닙니다. 로그인을 처리하는 프로그램이 저마다 직접 레코드를 덧붙이거나 고쳐 쓰므로, 어떤 로그인이 남는지는 프로그램마다 다릅니다. 레코드 구조와 `ut_type` 값, 파일을 만드는 tmpfiles 설정은 [로그인 기록 파일 형식](../../01-foundations/logging/utmp-wtmp-format.md)에 있고, 이 쪽은 누가 언제 쓰는지와 조사에서 어떻게 읽는지를 다룹니다.

| 프로그램 | 언제 쓰나 | 파일 | 레코드 모양 |
|---|---|---|---|
| sshd | 가상 터미널(pty)을 받은 세션이 열릴 때 | utmp·wtmp, lastlog | USER_PROCESS, 터미널 `pts/N`, 사용자는 실제 계정 이름, 호스트는 원격 주소 |
| sshd | pty 세션이 끝날 때 | utmp·wtmp | DEAD_PROCESS, 사용자·호스트 칸은 비움 |
| sshd | 암호·키보드 대화식 인증 실패, 없는 사용자 이름 | btmp | LOGIN_PROCESS, 터미널 `ssh:notty`, 사용자는 클라이언트가 보낸 문자열 |
| su (util-linux) | 인증에 실패할 때만 | btmp | 사용자는 바꾸려던 대상 계정, 터미널은 su 를 실행한 터미널 |
| 콘솔 login | 로그인 성공·실패 | utmp·wtmp, btmp | 아래 "위치와 버전별 차이" 참고 |
| pam_lastlog | PAM 세션 단계 | lastlog | `nowtmp` 옵션이 없으면 wtmp 도 씀[17] |
| systemd-update-utmp | 부팅·종료·런레벨 변화 | utmp·wtmp | [부팅과 종료 기록](../system-info/boot-shutdown.md) 참고 |
| useradd | 계정을 만들 때 | lastlog (faillog) | 새 UID 칸을 0 으로 지움 |

sshd 는 pty 를 할당한 직후에만 로그인 레코드를 씁니다. 모니터 프로세스가 pty 를 받은 다음 `record_login()` 을 부르고, 세션이 끝나면 pty 가 있던 세션에만 `record_logout()` 을 부릅니다[1][3]. 그래서 `ssh 호스트 명령` 처럼 명령만 실행한 세션, scp, sftp 처럼 pty 를 요청하지 않는 세션은 wtmp 와 lastlog 에 남지 않습니다. 이런 세션도 인증 로그의 `Accepted …` 줄과 `pam_unix(sshd:session)` 줄은 남으므로 [sshd 로그](ssh/sshd-logs.md)에서 찾습니다. lastlog 지원을 넣어 빌드한 sshd 는 로그인 레코드를 쓸 때 lastlog 칸도 함께 고칩니다[1].

sshd 의 btmp 기록은 Linux 빌드에서 켜집니다. configure 가 Linux 대상에서 `/var/log/btmp` 경로와 btmp 사용을 정의하고, 이 둘이 있으면 실패 기록 기능이 켜집니다[1]. 기록 조건은 두 가지입니다[1][2]. 하나는 인증에 실패했고 방식이 `password`, `keyboard-interactive`, `challenge-response` 가운데 하나일 때이고, 다른 하나는 없는 사용자 이름으로 접속했을 때(`Invalid user`)입니다. 공개 키 인증 실패는 btmp 에 남지 않습니다. 이 조건은 OpenSSH 8.7p1, 9.6p1, 최신 소스가 모두 같습니다[1][2].

btmp 레코드를 쓰기 전에 sshd 는 몇 가지를 확인합니다[1]. root 권한으로 돌지 않으면 쓰지 않고, 파일을 덧붙이기 모드로만 열어서 파일이 없으면 만들지 않고 넘어갑니다. 파일 소유자가 root 가 아니거나 그룹 실행 권한 또는 기타 사용자 권한이 하나라도 있으면 인증 로그에 `Excess permission or bad ownership on file /var/log/btmp` 를 남기고 쓰지 않습니다. 레코드에는 터미널 `ssh:notty`, 클라이언트가 보낸 사용자 이름, 원격 호스트, 초 단위 시각, 원격 주소가 들어가고 `ut_id` 는 비웁니다[1]. 호스트 칸은 `UseDNS` 가 기본값 `no` 이면 이름이 아니라 주소 문자열입니다[1][3].

su 는 PAM 인증이나 계정 확인이 실패하면 btmp 에 레코드를 하나 덧붙입니다[4]. 사용자 칸에는 su 로 바꾸려던 대상 계정 이름이, 터미널 칸에는 su 를 실행한 터미널 이름이 들어가고, 시각은 마이크로초까지 채웁니다[4]. su 는 lastlog 에 쓰지 않고[4], su 코드에는 wtmp 를 쓰는 부분도 없습니다. 그래서 su 성공은 su 자체가 세 파일 어디에도 쓰지 않고, [sudo·su 사용 기록](sudo-su.md)의 인증 로그 줄로 찾습니다.

useradd 는 새 UID 의 lastlog·faillog 칸을 0 으로 지웁니다[6]. 이전에 지운 사용자의 칸을 새 사용자가 물려받지 않게 하려는 동작이고, `-l`(`--no-log-init`)을 주거나 `/etc/default/useradd` 의 `LOG_INIT` 를 `no` 로 두면 하지 않습니다[6]. 그 UID 를 쓰는 사용자가 이미 있거나, lastlog 파일이 그 칸 위치보다 짧거나, UID 가 `LASTLOG_UID_MAX` 보다 크면 건드리지 않습니다[6]. 계정 생성 흔적 전체는 [계정 생성·변경 흔적](account-changes.md)에 있습니다.

## 위치와 버전별 차이

네 파일의 경로는 두 기준 배포판이 같습니다. wtmp 는 `/var/log/wtmp`, btmp 는 `/var/log/btmp`, lastlog 는 `/var/log/lastlog`, utmp 는 `/run/utmp` 이고, 파일을 만드는 규칙과 권한은 [로그인 기록 파일 형식](../../01-foundations/logging/utmp-wtmp-format.md)에 있습니다. 배포판마다 다른 것은 파일을 쓰는 프로그램과 설정입니다.

| 항목 | Ubuntu 24.04 | RHEL 9 |
|---|---|---|
| OpenSSH | 9.6p1[8] | 처음 8.7p1, CentOS Stream 9 는 2025-09 에 9.9p1 로 올림[9]. 검체에서 `rpm -q openssh-server` 로 확인 |
| 콘솔 `login` | shadow 의 login 패키지[7] | util-linux[11] |
| 콘솔 login 의 lastlog | `/etc/pam.d/login` 의 `session optional pam_lastlog.so`[7] | `/etc/pam.d/login`·`postlogin` 을 검체에서 확인 |
| `/etc/pam.d/sshd` | pam_lastlog 없음, sshd 가 lastlog 를 직접 씀[8][1] | `password-auth`·`postlogin` 을 include[9]. 내용은 검체에서 확인 |
| `login.defs` 의 `FTMP_FILE` | `/var/log/btmp`[7] | "Currently FTMP_FILE is not supported" 주석만 있음[10] |
| `lastlog` 명령 | login 패키지[7] | shadow-utils[10] |
| `faillog` 명령 | login 패키지, `FAILLOG_ENAB yes`[7] | 패키지에서 뺌[10] |
| `last`·`lastb`·`utmpdump` | util-linux[11] | util-linux 2.37.4[11] |
| wtmp·btmp 순환 | 검체의 `/etc/logrotate.d/wtmp`·`btmp` 로 확인 | 월 단위, 한 세대, btmp 는 `create 0660 root utmp`, wtmp 는 `create 0664 root utmp`·`minsize 1M`, 전역 `dateext`[12] |

콘솔 로그인 실패가 btmp 에 남는지는 두 배포판이 다를 수 있습니다. RHEL 9 의 util-linux login 은 인증에 실패하면 btmp 에 씁니다([로그인 기록 파일 형식](../../01-foundations/logging/utmp-wtmp-format.md)). Ubuntu 24.04 의 shadow login 은 `FTMP_FILE` 로 btmp 에 쓰는 코드가 PAM 을 쓰지 않는 빌드 쪽에만 있고, PAM 빌드에서는 syslog 에 `FAILED LOGIN (N) on '터미널' FOR '이름', 사유` 모양의 줄만 남깁니다[5]. Ubuntu 는 `/etc/pam.d/login` 을 싣는 PAM 구성이라서[7], 콘솔 로그인 실패가 btmp 에 없을 가능성이 있습니다. 검체에서 `lastb` 결과에 `tty` 로 시작하는 터미널이 있는지로 확인합니다.

RHEL 9 는 logrotate 의 전역 `dateext` 때문에 회전한 파일 이름이 `btmp-20250101`, `wtmp-20250101` 처럼 날짜형입니다[12]. 수집할 때 `wtmp*`, `btmp*` 처럼 이름 뒤를 열어 두어야 회전본까지 모입니다([로그 순환](../../01-foundations/logging/logrotate.md)).

## 구조

레코드 구조는 [로그인 기록 파일 형식](../../01-foundations/logging/utmp-wtmp-format.md)에서 설명합니다. 조사에서 알아 둘 것은 프로그램마다 칸을 채우는 방식입니다.

| 레코드 | `ut_type` | `ut_line` | `ut_user` | `ut_host` | 시각 |
|---|---|---|---|---|---|
| sshd 로그인 (wtmp) | 7 USER_PROCESS | `pts/N` | 계정 이름(passwd 의 이름) | 원격 주소 | 초와 마이크로초 |
| sshd 로그아웃 (wtmp) | 8 DEAD_PROCESS | `pts/N` | 비움 | 비움 | 초와 마이크로초 |
| sshd 실패 (btmp) | 6 LOGIN_PROCESS | `ssh:notty` | 클라이언트가 보낸 문자열 | 원격 주소 | 초, 마이크로초는 0 |
| su 실패 (btmp) | 6 LOGIN_PROCESS | su 를 실행한 터미널 | 대상 계정, 없으면 `(unknown)` | 비움 | 초와 마이크로초 |

sshd 는 `construct_utmp()`·`record_failed_login()` 에서[1], su 는 `log_btmp()` 에서[4] 이 칸들을 채웁니다. sshd 로그아웃 레코드는 같은 `ut_line`·`ut_pid` 의 로그인 레코드와 짝을 짓습니다. `sshd -u 길이` 는 호스트 칸에 넣을 이름 길이의 한도를 정하고, 이름이 더 길면 주소를 넣습니다[3].

## 증거로서 의미

### 증명하는 것

wtmp 의 USER_PROCESS 레코드는 그 시각에 그 계정으로 그 터미널·원격 주소에서 대화형(pty) 세션이 열렸다는 기록입니다. sshd 가 쓴 레코드의 사용자 칸은 인증을 마친 계정 이름이라서, btmp 와 달리 실제 계정을 가리킵니다[1].

btmp 의 `ssh:notty` 레코드는 그 시각에 그 원격 주소에서 그 이름으로 암호 또는 키보드 대화식 인증에 실패했거나, 없는 사용자 이름으로 접속을 시도했다는 기록입니다[1]. su 의 btmp 레코드는 그 터미널에서 그 계정으로 바꾸려다 인증에 실패했다는 기록입니다[4].

lastlog 는 계정마다 마지막 로그인 한 건의 시각·터미널·호스트를 보여 줍니다.

### 증명하지 못하는 것

wtmp 에 없다고 로그인이 없었던 것은 아닙니다. pty 없는 ssh 세션·scp·sftp, su 성공은 처음부터 wtmp 에 쓰지 않습니다[1][4]. 공개 키 인증 실패는 btmp 에 쓰지 않습니다[1]. btmp 파일이 없거나 권한이 맞지 않으면 sshd 는 실패를 기록하지 않습니다[1].

btmp 의 사용자 칸은 계정이 있다는 뜻이 아닙니다. 클라이언트가 보낸 문자열을 그대로 넣으므로[1] 없는 이름, 오타, 비밀번호를 이름 칸에 넣은 입력까지 들어갈 수 있습니다. 레코드 수도 시도 횟수와 같지 않을 수 있습니다. 없는 이름으로 접속해 암호를 한 번 틀리면 `Invalid user` 단계와 `Failed password` 단계에서 각각 기록 함수를 부르므로 레코드가 두 건 생길 수 있습니다[1].

lastlog 는 이력이 아니라 마지막 한 건입니다. 로그인할 때마다 덮어쓰고, 관리자가 `lastlog -S`·`-C` 로 바꾸거나 지울 수 있고[6], useradd 가 재사용 UID 의 칸을 0 으로 지웁니다[6]([로그인 기록 파일 형식](../../01-foundations/logging/utmp-wtmp-format.md)).

보고서에는 "○○ 계정으로 ○시 ○분에 192.0.2.10 에서 pts/1 로 대화형 세션이 열린 기록이 wtmp 에 있다" 처럼 기록이 말하는 만큼만 씁니다.

## 시각 해석

`ut_tv` 와 lastlog 의 `ll_time` 은 Unix epoch 초라서 UTC 입니다([Linux 의 시각 값](../../01-foundations/value-decoding/time-values.md)). sshd 의 wtmp 로그인 시각은 인증이 끝나고 pty 를 할당한 순간이고, 로그아웃 시각은 세션을 정리하는 순간입니다[1]. sshd 는 wtmp 레코드에는 마이크로초까지 채우지만 btmp 레코드에는 초까지만 채우고[1], su 는 btmp 레코드에 마이크로초까지 채웁니다[4].

`last` 와 `lastb` 는 명령을 실행한 기계의 시간대로 시각을 보여 줍니다. 떼어 온 파일을 분석 기계에서 읽을 때는 `--time-format iso` 로 시간대 오프셋까지 찍어 둡니다[13]. lastlog 의 시각은 로그인할 때마다 바뀌고, `lastlog -S` 를 실행하면 그 순간 시각으로 바뀝니다[6].

레코드 시각은 기록 순간의 시스템 시계이므로, 시계를 바꾸면 그 뒤 레코드도 함께 밀립니다. 시계를 바꾼 흔적은 [시각을 조작했나](../../04-scenarios/insider/time-manipulation.md)에서 다룹니다.

## 함정과 한계

- btmp 권한을 바꾸면(예: `0664`) sshd 는 실패를 기록하지 않고 `Excess permission or bad ownership on file /var/log/btmp` 를 인증 로그에 남깁니다[1]. btmp 가 조용한데 이 줄이 있으면, 이 줄이 기록이 멈춘 이유입니다.
- btmp·wtmp 를 지우면 sshd 는 새로 만들지 않으므로 기록이 멈춥니다[1]. 다음 부팅 때 systemd-tmpfiles 가 빈 파일을 다시 만들 수 있어서, 비어 있는 새 파일이 있다고 지운 적이 없다고 볼 수는 없습니다([로그인 기록 파일 형식](../../01-foundations/logging/utmp-wtmp-format.md)). 파일의 아이노드 생성 시각과 첫 레코드 시각을 비교합니다.
- 지운 계정의 UID 를 useradd 가 다시 쓰면 옛 lastlog 칸이 0 으로 지워집니다[6].
- RHEL 9 의 btmp·wtmp 는 월 단위로 돌리고 한 세대만 남기므로[12], 두 달보다 오래된 기록은 회전으로 사라졌을 가능성이 있습니다. wtmp 는 1MB 보다 작으면 돌리지 않으므로[12] 오래된 레코드가 남아 있기도 합니다.
- Ubuntu 24.04 의 콘솔 로그인 실패는 btmp 에 없을 가능성이 있습니다(위 "위치와 버전별 차이").
- 흔적을 지우는 행위 전반은 [흔적을 지웠나](../../04-scenarios/insider/anti-forensics.md)에서 다룹니다.

## 직접 분석해 보기

### 헥스로 한 번

아래는 sshd 의 btmp 레코드를 명세와 코드대로 만든 예시입니다(만든 예시: 사용자 `admin`, 원격 주소 `198.51.100.7`, PID 2201). 0 으로만 된 줄은 `*` 로 줄였습니다.

```
00000000: 0600 0000 9908 0000 7373 683a 6e6f 7474  ........ssh:nott
00000010: 7900 0000 0000 0000 0000 0000 0000 0000  y...............
00000020: 0000 0000 0000 0000 0000 0000 6164 6d69  ............admi
00000030: 6e00 0000 0000 0000 0000 0000 0000 0000  n...............
00000040: 0000 0000 0000 0000 0000 0000 3139 382e  ............198.
00000050: 3531 2e31 3030 2e37 0000 0000 0000 0000  51.100.7........
00000060: 0000 0000 0000 0000 0000 0000 0000 0000  ................
*
00000150: 0000 0000 05b9 5569 0000 0000 c633 6407  ......Ui.....3d.
00000160: 0000 0000 0000 0000 0000 0000 0000 0000  ................
00000170: 0000 0000 0000 0000 0000 0000 0000 0000  ................
```

1. 0x00 의 `06 00` 이 LOGIN_PROCESS 이고, 0x04 의 `99 08 00 00` 이 PID 2201 입니다.
2. 0x08 부터 `ssh:notty` 가 있고, 0x28 의 `ut_id` 4바이트는 0 입니다. sshd 는 `ssh:notty` 일 때 이 칸을 비웁니다[1].
3. 0x2C 부터 사용자 이름 `admin`, 0x4C 부터 호스트 `198.51.100.7` 이 NUL 로 끝납니다.
4. 0x154 의 `05 b9 55 69` 는 1767225605 초로 2026-01-01 00:00:05 UTC 이고, 0x158 의 마이크로초는 0 입니다.
5. 0x15C 의 `c6 33 64 07` 이 원격 주소 198.51.100.7 입니다.

USER_PROCESS 레코드와 lastlog 칸을 헥스로 읽는 예는 [로그인 기록 파일 형식](../../01-foundations/logging/utmp-wtmp-format.md)에 있습니다.

### 공개 도구로 한 번

떼어 온 파일은 `-f` 로 넘깁니다[13].

```
last -f wtmp -F -w -i --time-format iso
lastb -f btmp -F -w -i --time-format iso
utmpdump btmp
```

`lastb` 결과에서 터미널이 `ssh:notty` 인 줄은 sshd 의 원격 인증 실패이고, `pts/N` 이나 `tty1` 인 줄은 su 나 콘솔 login 의 실패입니다. `last` 결과에서 같은 원격 주소가 여러 번 나오면 [sshd 로그](ssh/sshd-logs.md)의 `Accepted` 줄과 시각을 맞춰 봅니다. plaso·dissect·Velociraptor 가 이 파일들을 읽는 방식과 차이는 [로그인 기록 파일 형식](../../01-foundations/logging/utmp-wtmp-format.md)의 도구 표에 있습니다.

## 교차 검증

| 이 기록 | 함께 볼 기록 | 맞춰 볼 것 |
|---|---|---|
| wtmp USER_PROCESS (sshd) | [sshd 로그](ssh/sshd-logs.md)의 `Accepted …`, [인증 로그](auth-log.md)의 `pam_unix(sshd:session): session opened` | 같은 초, 같은 계정·원격 주소 |
| wtmp USER_PROCESS | systemd-logind 의 `New session N of user 이름.`[14] | 저널 MESSAGE_ID `8d45620c1a4348dbb17410da57c60c66`[14]([systemd 저널](../../01-foundations/logging/systemd-journal/index.md)) |
| wtmp 로그인·로그아웃 | 감사 로그 USER_AUTH(1100)·CRED_ACQ(1103)·USER_START(1105)·USER_LOGIN(1112)[15] | [감사 로그 형식](../../01-foundations/logging/auditd-format.md) |
| btmp `ssh:notty` | sshd 의 `Invalid user …`, `Failed password …` | 이름·원격 주소·시각 |
| btmp (su) | [sudo·su 사용 기록](sudo-su.md)의 su 실패 줄 | 대상 계정·터미널 |
| lastlog | wtmp 의 마지막 USER_PROCESS | 두 시각이 다르면 어느 한쪽이 바뀌었거나 순환으로 빠졌을 가능성 |

wtmp·btmp·lastlog 로 로그인을 먼저 확인한 뒤, 그 로그인 시각보다 뒤에 생기거나 바뀐 파일을 찾는 흐름도 있습니다. `find … -newercm …/var/log/lastlog` 처럼 lastlog 의 시각을 기준점으로 삼는 방법입니다[16]. 여러 기록을 시간순으로 엮는 방법은 [타임라인 만들기](../../03-techniques/analysis/timeline.md)에, SSH 침입 조사 흐름은 [SSH 로 들어왔나](../../04-scenarios/intrusion/ssh-intrusion.md)에 있습니다.

## 실습

공개 Linux 검체(NIST CFReDS 등)나 직접 만든 가상 머신 이미지로 아래 질문을 풀어 봅니다.

1. `lastb` 결과의 터미널 칸을 `ssh:notty` 와 그 밖으로 나누면 각각 몇 건인가? 그 밖의 줄은 su 인가 콘솔 login 인가?
2. 인증 로그에 `Accepted publickey` 줄이 있는데 같은 시각 wtmp 에 USER_PROCESS 가 없는 세션이 있는가? 있다면 그 세션은 어떤 종류였을 가능성이 있는가?
3. `/var/log/btmp` 의 소유자와 권한은 무엇인가? 인증 로그에 `Excess permission or bad ownership` 줄이 있는가?
4. lastlog 에 칸이 남아 있는 UID 가운데 지금 `/etc/passwd` 에 없는 UID 가 있는가?
5. RHEL 검체라면 `wtmp-YYYYMMDD` 회전본이 있는가? 가장 오래된 레코드는 언제인가?

## 참고 문헌

1. OpenSSH portable, `monitor.c`·`session.c`·`loginrec.c`·`auth.c`·`configure.ac`·`defines.h`. https://github.com/openssh/openssh-portable/tree/master
2. OpenSSH portable, 태그 V_9_6_P1·V_8_7_P1 의 `auth.c`. https://github.com/openssh/openssh-portable/tree/V_9_6_P1 , https://github.com/openssh/openssh-portable/tree/V_8_7_P1
3. OpenSSH, sshd(8)·sshd_config(5). https://github.com/openssh/openssh-portable/blob/master/sshd.8 , https://github.com/openssh/openssh-portable/blob/master/sshd_config.5
4. util-linux, `login-utils/su-common.c`·su(1). https://github.com/util-linux/util-linux/blob/master/login-utils/su-common.c , https://github.com/util-linux/util-linux/blob/master/login-utils/su.1.adoc
5. shadow 4.13, `src/login.c`. https://github.com/shadow-maint/shadow/blob/4.13/src/login.c
6. shadow, `src/useradd.c`·useradd(8)·lastlog(8). https://github.com/shadow-maint/shadow/blob/master/src/useradd.c , https://github.com/shadow-maint/shadow/blob/master/man/useradd.8.xml , https://github.com/shadow-maint/shadow/blob/master/man/lastlog.8.xml
7. Ubuntu noble shadow 패키지, `debian/login.pam`·`debian/login.defs`·`debian/login.install`. https://git.launchpad.net/ubuntu/+source/shadow/tree/debian?h=ubuntu/noble-updates
8. Ubuntu noble openssh 패키지, `debian/changelog`·`debian/openssh-server.sshd.pam.in`. https://git.launchpad.net/ubuntu/+source/openssh/tree/debian?h=ubuntu/noble-updates
9. CentOS Stream 9 openssh 패키지, `openssh.spec`·`sshd.pam`. https://gitlab.com/redhat/centos-stream/rpms/openssh/-/tree/c9s
10. CentOS Stream 9 shadow-utils 패키지, `shadow-utils.spec`·`shadow-utils.login.defs`. https://gitlab.com/redhat/centos-stream/rpms/shadow-utils/-/tree/c9s
11. util-linux 패키지: Ubuntu noble `debian/util-linux.install`, CentOS Stream 9 `util-linux.spec`. https://git.launchpad.net/ubuntu/+source/util-linux/tree/debian?h=ubuntu/noble-updates , https://gitlab.com/redhat/centos-stream/rpms/util-linux/-/tree/c9s
12. CentOS Stream 9 logrotate 패키지 `logrotate.spec`, logrotate 3.18.0 `examples/logrotate.conf`·`btmp`·`wtmp`. https://gitlab.com/redhat/centos-stream/rpms/logrotate/-/tree/c9s , https://github.com/logrotate/logrotate/tree/3.18.0/examples
13. util-linux, last(1). https://github.com/util-linux/util-linux/blob/master/login-utils/last.1.adoc
14. systemd v255, `src/login/logind-session.c`·`src/systemd/sd-messages.h`. https://github.com/systemd/systemd/blob/v255/src/login/logind-session.c , https://github.com/systemd/systemd/blob/main/src/systemd/sd-messages.h
15. Linux Audit, `specs/messages/message-dictionary.csv`. https://github.com/linux-audit/audit-documentation/blob/main/specs/messages/message-dictionary.csv
16. Ali Hadi, Mariam Khader, Thomas Claflin, "Learning Linux Forensic Analysis and Why it Matters", DFRWS 발표. https://dfrws.org/presentation/learning-linux-forensic-analysis-and-why-it-matters/
17. Linux-PAM, pam_lastlog(8). https://github.com/linux-pam/linux-pam/blob/master/modules/pam_lastlog/pam_lastlog.8.xml
