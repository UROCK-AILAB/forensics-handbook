---
title: "권한을 올렸나"
parent: "시나리오 · 침해"
nav_order: 1050
---

# 권한을 올렸나 (Privilege Escalation)

일반 계정이나 웹 서버 계정으로 들어온 사람이 root 권한을 얻었는지, 얻었다면 sudo·su·pkexec 같은 정해진 통로를 썼는지 아니면 설정 약점이나 취약점을 썼는지, 그리고 언제였는지를 판별하는 절차입니다.

## 조사 질문

- 어느 계정이 언제 root(또는 다른 계정)의 권한으로 무엇을 실행했나?
- 그 권한은 sudo·su·pkexec 처럼 허용된 통로로 얻었나, 아니면 sudoers 규칙 추가·UID 0 계정·SUID 파일·파일 capability·커널 취약점처럼 통로 밖에서 얻었나?
- root 로 한 행위를 처음 로그인한 계정까지 이을 수 있나?

## 먼저 확인할 것

**배포판과 sudo 판.** 기록이 남는 파일과 첫 사용 흔적이 배포판마다 다르므로, 분석 대상의 배포판과 sudo 판부터 확인합니다. 두 기준 배포판 모두 sudo 를 syslog 의 `authpriv` 분야로 기록하고 Linux 감사 연동을 켜서 빌드합니다[2][3].

| 항목 | Ubuntu 24.04 LTS | RHEL 9 계열 |
|---|---|---|
| sudo 판 | 1.9.15p5[2] | 1.9.17p2(CentOS Stream 9 기준)[3] |
| 기본 관리자 규칙 | `%admin ALL=(ALL) ALL`, `%sudo ALL=(ALL:ALL) ALL`[2] | `%wheel ALL=(ALL) ALL`[3] |
| 추가 규칙 폴더 | `@includedir /etc/sudoers.d`[2] | `#includedir /etc/sudoers.d`[3] |
| sudo 줄이 남는 파일 | `/var/log/auth.log` | `/var/log/secure` |
| su 성공·실패 줄이 남는 파일 | `/var/log/auth.log` | `/var/log/messages` |
| 첫 사용 흔적 파일 | `~/.sudo_as_admin_successful`(`--enable-admin-flag`)[1][2], 강의 파일 없음(`--without-lecture`)[2] | 강의 표시 파일(빌드 옵션에 lecture 지정 없음)[3] |

RHEL 의 `#includedir` 는 주석이 아니라 sudo 1.9.1 이전 판과 맞추려고 남겨 둔 끌어오기 줄입니다[1]. 파일 배치의 근거와 강의 파일 경로는 [sudo·su 사용 기록](../../02-artifacts/logins/sudo-su.md), 기본 sudoers 전체는 [sudo 설정 (sudoers)](../../01-foundations/users-auth/sudoers.md) 에 있습니다.

**기록 설정.** sudoers 에 `log_subcmds`·`log_input`·`log_output`·`logfile` 이 있는지 봅니다. `log_subcmds` 는 sudo 1.9.8 부터 있고 기본은 꺼져 있으며, 켜져 있어야 sudo 로 띄운 셸 안에서 실행한 명령이 sudo 기록에 남습니다[1]. 감사 데몬이 돌았는지와 어떤 규칙이 있었는지도 함께 확인합니다([감사 로그 형식](../../01-foundations/logging/auditd-format.md)).

**시간대.** Ubuntu 24.04 의 rsyslog 기본 줄은 시간대 오프셋을 담지만, RHEL 9 가 쓰는 전통 형식 줄에는 연도와 시간대가 없습니다([인증 로그 (auth.log·secure)](../../02-artifacts/logins/auth-log.md)). 감사 로그는 epoch 초, 저널은 UTC 마이크로초로 적으므로 한 타임라인에 올리기 전에 기준을 맞춥니다([Linux 의 시각 값](../../01-foundations/value-decoding/time-values.md), [호스트 이름·시간대·로캘](../../02-artifacts/system-info/hostname-timezone.md)).

**수집 범위.** SUID 파일 목록, capability 목록, 프로세스 자격 증명은 라이브에서 거둔 것과 이미지에서 다시 뽑은 것이 범위가 다를 수 있습니다. 수집 도구가 어느 폴더까지 봤는지 먼저 적어 둡니다(아래 흔한 오판 참고).

## 볼 아티팩트와 순서

| 순서 | 아티팩트 | 알려 주는 것 | 페이지 |
|---|---|---|---|
| 1 | 인증 로그의 sudo·su·pkexec 줄과 PAM 세션 줄 | 어느 계정이 누구 권한으로 무엇을 요청했고 허용·거부됐는지 | [sudo·su 사용 기록](../../02-artifacts/logins/sudo-su.md), [인증 로그](../../02-artifacts/logins/auth-log.md) |
| 2 | `/etc/sudoers`, `/etc/sudoers.d/`, 그룹 파일 | 허용된 권한과 새로 더한 규칙 | [sudo 설정](../../01-foundations/users-auth/sudoers.md), [계정 파일](../../01-foundations/users-auth/passwd-shadow-group.md) |
| 3 | 계정 변경 흔적 | UID 0 계정 추가, sudo·wheel·admin 그룹 가입 | [계정 생성·변경 흔적](../../02-artifacts/logins/account-changes.md) |
| 4 | 감사 로그(`USER_CMD`, `ANOM_ROOT_TRANS`, 실행 레코드의 `auid` 와 `uid`) | 로그인한 계정과 실제로 쓴 권한의 차이 | [감사 로그의 실행 기록](../../02-artifacts/execution/auditd-execve.md) |
| 5 | SUID·SGID 파일과 capability 가 붙은 파일 | 새로 생긴 권한 파일 | [권한·확장 속성·ACL·Capabilities](../../01-foundations/filesystem/permissions-xattr.md) |
| 6 | 커널 로그, 코어 덤프, taint 값 | 취약점 공격 프로그램이 죽거나 커널이 이상해진 흔적 | [커널 로그](../../02-artifacts/system-info/kernel-log.md), [커널 모듈](../../02-artifacts/persistence/kernel-modules.md) |
| 7 | 메모리 | 프로세스 자격 증명과 capability | [메모리 분석](../../03-techniques/analysis/memory-analysis.md) |

감사 로그에서 권한 상승과 이어지는 레코드 종류는 다음과 같습니다[6]. 실제로 남는지는 감사 규칙과 각 프로그램의 빌드에 달려 있습니다.

| 종류 | 번호 | 뜻 |
|---|---|---|
| `USER_CMD` | 1123 | 사용자 셸 명령과 인수(sudo 가 남김) |
| `ANOM_ROOT_TRANS` | 2117 | 사용자가 root 가 됨 |
| `USER_ROLE_CHANGE` | 2300 | SELinux 역할 바꿈 |
| `BPRM_FCAPS` | 1321 | 파일 capability 로 권한이 늘어남 |
| `CAPSET` | 1322 | 프로세스 capability 설정 |
| `ANOM_ABEND` | 1701 | 프로세스가 비정상으로 끝남 |
| `ADD_USER`·`ADD_GROUP`·`USER_MGMT` | 1114·1116·1102 | 계정·그룹 추가, 계정 속성 바꿈 |

## 분석 흐름

1. **통로 기록으로 시점 후보를 좁힙니다.** 인증 로그에서 sudo 허용 줄의 `USER=root`, su 의 `(to root)`, pkexec 줄의 `[USER=root]` 를 모읍니다. sudo 허용 줄은 `username : TTY=… ; PWD=… ; USER=… ; COMMAND=…` 모양이고[1], su 줄은 서식 `%s(to %s) %s on %s` 로 만들어집니다[4]. pkexec 줄은 공개 파서가 `사용자: Executing command [USER=…] [TTY=…] [CWD=…] [COMMAND=…]` 모양으로 읽습니다[7]. 각 줄 옆의 PAM 세션 줄 `session opened for user %s(uid=%s) by %s(uid=%lu)` 에서 `by` 뒤의 이름은 로그인 이름이고, 괄호 안의 uid 는 요청한 프로세스의 실제 UID 입니다[5]. 거부 줄(`user NOT in sudoers`, `command not allowed`, `3 incorrect password attempts` 등)[1]과 `FAILED SU`[4] 도 함께 모읍니다. 권한 없는 계정이 여러 번 시도한 뒤 다른 방법으로 넘어갔을 수 있기 때문입니다.

   ```
   (Ubuntu 24.04, 만든 예시. 필드 사이 공백 폭은 모양만 보여 줌)
   2026-03-12T14:31:02.410032+09:00 web01 sudo:   www-data : user NOT in sudoers ; TTY=unknown ; PWD=/var/www/html ; USER=root ; COMMAND=/usr/bin/id
   2026-03-12T14:31:40.004512+09:00 web01 sudo:    alice : TTY=pts/1 ; PWD=/home/alice ; USER=root ; COMMAND=/usr/bin/bash
   2026-03-12T14:31:40.010877+09:00 web01 sudo: pam_unix(sudo:session): session opened for user root(uid=0) by alice(uid=1001)
   2026-03-12T14:40:15.221307+09:00 web01 su[4120]: (to root) alice on pts/1
   ```

2. **sudo 로 연 셸 안의 행위를 따로 찾습니다.** `COMMAND=/usr/bin/bash` 처럼 셸을 연 줄 뒤의 명령은 `log_subcmds` 나 입출력 기록이 없으면 sudo 기록에 남지 않습니다[1]. 이 구간은 [셸 명령 기록](../../02-artifacts/execution/shell-history/index.md) 과 감사 로그의 실행 레코드로 채웁니다.

3. **통로 기록이 없는 root 행위를 로그인 계정까지 잇습니다.** root 소유의 새 파일, root crontab 변경처럼 root 로 한 행위가 있는데 sudo·su·pkexec 줄이 없으면, 감사 로그의 실행 레코드에서 `auid` 가 일반 계정인데 `uid`·`euid` 가 0 인 이벤트를 찾습니다. `auid` 는 로그인 때 정해져 su·sudo 뒤에도 그대로 따라가므로([감사 로그의 실행 기록](../../02-artifacts/execution/auditd-execve.md)), 통로 기록 없이 이런 이벤트가 나오면 통로 밖에서 권한을 얻었을 가능성이 있습니다. `ses` 로 같은 로그인 세션의 앞뒤 명령을 묶어 봅니다.

4. **설정 쪽 변화를 봅니다.** `/etc/sudoers.d/` 에 새 파일이 생겼는지, 기존 규칙에 `NOPASSWD` 가 붙었는지 봅니다. 이 폴더에서 이름에 `.` 이 들어가거나 `~` 로 끝나는 파일은 sudo 가 읽지 않으므로, 파일이 있다고 규칙이 적용된 것은 아닙니다([sudo 설정](../../01-foundations/users-auth/sudoers.md)). `/etc/passwd` 에서 UID 0 인 둘째 계정, 그룹 파일에서 sudo·wheel·admin 그룹에 새로 들어간 계정을 찾고, 인증 로그의 `add '…' to group '…'` 같은 줄로 시각을 잡습니다([계정 생성·변경 흔적](../../02-artifacts/logins/account-changes.md)). polkit 설정 폴더(`/etc/polkit-1`, `/usr/share/polkit-1`, `/usr/lib/polkit-1`, `/var/lib/polkit-1`)도 공개 수집 도구가 지속성 후보로 모으는 곳이라 함께 봅니다[8].

5. **권한 파일을 봅니다.** SUID·SGID 비트가 켜진 파일과 capability 가 붙은 파일 목록을 만들고, 패키지가 설치한 파일과 대조해 나머지를 골라냅니다([패키지 파일 변조 확인](../../02-artifacts/packages/package-verify.md)). `/tmp`, `/dev/shm`, 홈 폴더, 웹 문서 폴더에 있는 SUID 파일은 먼저 봅니다([임시 폴더와 메모리 파일 시스템](../../02-artifacts/file-activity/tmp-shm.md)). 파일 capability 로 권한이 늘어난 실행은 감사 규칙이 있었다면 `BPRM_FCAPS` 로 남습니다[6].

6. **취약점 흔적을 봅니다.** 로그인 시각 뒤에 생긴 실행 파일을 찾고, 그 무렵 프로세스가 비정상으로 끝난 기록을 봅니다. systemd-coredump 가 코어 덤프를 받는 시스템이면 저널에 `MESSAGE_ID=fc2e22bc6ee647b6b90729ab34a250b1` 항목이 남고, `COREDUMP_PID`·`COREDUMP_UID`·`COREDUMP_SIGNAL_NAME`·`COREDUMP_EXE`·`COREDUMP_CMDLINE`·`COREDUMP_FILENAME` 에 죽은 프로세스와 덤프 파일이 적힙니다[10]. 덤프 파일은 `/var/lib/systemd/coredump/` 에 저장되고 기본으로 며칠 뒤 지워지며, 저널 항목과 덤프 파일은 따로 지워지므로 한쪽만 남아 있을 수 있습니다[10]. 코어 덤프를 systemd-coredump 가 받는지는 `/proc/sys/kernel/core_pattern` 으로 정해지고 systemd 는 `/usr/lib/sysctl.d/50-coredump.conf` 로 이 값을 설정하므로[10], 라이브 응답 결과나 설정 파일에서 이 값을 확인합니다. 커널 쪽 이상은 커널 로그의 Oops 줄과 taint 값으로 봅니다([커널 로그](../../02-artifacts/system-info/kernel-log.md)).

   한 사례 발표에서는 로그인 기록 파일의 수정 시각을 기준으로 그 뒤에 바뀐 파일을 찾아 공격에 쓴 실행 파일을 골라냈고, 결론은 커널 취약점(CVE-2017-16995)을 이용한 권한 상승이었습니다[12]. 같은 사례에서 지운 파일은 ext4 저널을 `debugfs` 로 뽑아 `ext4magic` 으로 되살렸습니다[12]([지운 파일 되살리기](../../03-techniques/analysis/file-recovery.md)).

7. **메모리가 있으면 자격 증명을 봅니다.** Volatility 3 의 `linux.malware.check_creds` 는 여러 프로세스가 자격 증명 구조체를 함께 쓰고 있는지 검사하고(옛 이름 `linux.check_creds` 에는 2026-06-07 에 없앤다는 표시가 붙어 있음), `linux.capabilities` 는 프로세스마다 inheritable·permitted·effective·bounding·ambient 집합을 보여 줍니다[11]. 해석은 [메모리 분석](../../03-techniques/analysis/memory-analysis.md) 에서 다룹니다.

8. **한 타임라인으로 묶습니다.** 로그인 → 권한 상승 → root 행위 순서가 시각으로 맞는지 [타임라인 만들기](../../03-techniques/analysis/timeline.md) 로 확인합니다.

## 흔한 오판

- **"sudo 기록에 명령이 없으니 root 로 아무것도 안 했다."** `sudo -i`, `sudo bash` 로 연 셸 안의 명령은 `log_subcmds`(기본 꺼짐)가 켜져 있어야 sudo 기록에 남습니다[1]. 셸 기록과 감사 로그로 확인합니다.
- **"sudo 줄의 사용자 이름이 곧 그 사람이다."** 줄에 적힌 것은 계정 이름입니다. root 가 sudo 를 실행하고 `SUDO_USER` 환경 변수가 있으면 sudoers 는 그 값을 실제 사용자로 봅니다[1]. 계정과 사람을 잇는 방법은 [누가 그 명령을 실행했나](../attribution/user-attribution.md) 에서 다룹니다.
- **"Ubuntu 에 강의 파일이 없으니 sudo 를 처음 쓴 적도 없다."** Ubuntu 의 sudo 는 `--without-lecture` 로 빌드해 강의 파일을 만들지 않습니다[2]. 대신 admin 플래그 파일 `~/.sudo_as_admin_successful` 을 봅니다[1][2].
- **"수집 도구의 SUID 결과가 깨끗하다."** Velociraptor `Linux.Sys.SUID` 는 기본 검색 범위가 `/usr/**` 라서[9] `/tmp`·`/home`·`/var` 의 SUID 파일은 나오지 않습니다. UAC 는 `/` 전체에서 찾습니다(proc 파일 시스템 제외)[8].
- **"root 사용자 목록 도구에 sudo 그룹 구성원이 나온다."** Velociraptor `Linux.Users.RootUsers` 는 설명이 "sudo 그룹에 추가된 사용자" 지만 실제 조건은 `id -Gn` 결과에 `root` 가 들어간 사용자입니다[9]. sudo·wheel 그룹 구성원은 그룹 파일로 직접 봅니다.
- **"su 에 성공했으면 로그인 기록에도 있다."** su 성공은 로그인 기록 파일에 남지 않고, 실패만 btmp 에 대상 계정 이름으로 덧붙습니다[4]([로그인 기록 (wtmp·btmp·lastlog)](../../02-artifacts/logins/wtmp-btmp-lastlog.md)).
- **"SUID 파일이 있으니 그걸로 권한을 올렸다."** `nosuid` 로 마운트한 곳에서는 SUID 비트와 파일 capability 가 먹지 않습니다([권한·확장 속성·ACL·Capabilities](../../01-foundations/filesystem/permissions-xattr.md)). 파일이 있다는 것은 실행했다는 뜻도 아니므로 실행 기록과 함께 봅니다.

## 보고서 문장 예

아래 값은 모두 만든 예시입니다.

- "2026-03-12 14:31:40(+09:00)에 계정 alice 가 pts/1 에서 sudo 로 root 권한의 `/usr/bin/bash` 실행을 요청해 허용된 기록이 `/var/log/auth.log` 에 있다."
- "같은 날 14:31:02(+09:00)에 계정 www-data 가 sudo 로 root 권한 실행을 요청했으나 `user NOT in sudoers` 로 거부된 기록이 있다."
- "감사 로그에 auid 1001, euid 0 인 실행 레코드가 14:52 부터 이어지고, 같은 시간대에 이 계정의 sudo·su 기록은 없다."
- "`/tmp/.cache/x`(만든 예시)는 소유자가 root 이고 SUID 비트가 켜져 있으며, 패키지 관리자가 설치한 파일이 아니다. 이 파일을 실행한 기록은 이 증거물에서 나오지 않는다."

"alice 가 root 권한을 탈취했다" 처럼 쓰지 않고, 기록으로 확인되는 계정·시각·통로까지만 씁니다.

## 함께 볼 페이지

- [SSH 로 들어왔나](ssh-intrusion.md) — 권한 상승 앞의 로그인 경로
- [웹 서버가 뚫렸나](web-compromise.md) — 웹 서버 계정에서 시작한 경우
- [무엇이 계속 살아남게 했나](persistence-hunt.md) — root 를 얻은 뒤 심은 것
- [흔적을 지웠나](../insider/anti-forensics.md) — 로그·기록 지우기
- [인증 모듈 (PAM)](../../01-foundations/users-auth/pam.md) — PAM 설정 변조
- [라이브 응답 수집](../../03-techniques/acquisition/live-response.md) — SUID·capability·프로세스 목록 거두기

## 참고 문헌

1. sudo, docs/sudoers.man.in (log_subcmds, EVENT LOGGING, SUDO_USER). https://github.com/sudo-project/sudo/blob/main/docs/sudoers.man.in
2. Ubuntu sudo 패키지(noble-updates), debian/rules·debian/etc/sudoers·changelog. https://git.launchpad.net/ubuntu/+source/sudo/tree/debian?h=ubuntu/noble-updates
3. CentOS Stream 9 sudo 패키지, sudo.spec·sudoers. https://gitlab.com/redhat/centos-stream/rpms/sudo/-/tree/c9s
4. util-linux, login-utils/su-common.c (master, v2.37.4)·su.1.adoc. https://github.com/util-linux/util-linux/blob/master/login-utils/su-common.c , https://github.com/util-linux/util-linux/blob/v2.37.4/login-utils/su-common.c , https://github.com/util-linux/util-linux/blob/master/login-utils/su.1.adoc
5. linux-pam, modules/pam_unix/pam_unix_sess.c. https://github.com/linux-pam/linux-pam/blob/master/modules/pam_unix/pam_unix_sess.c
6. linux-audit, audit-documentation specs/messages/message-dictionary.csv. https://github.com/linux-audit/audit-documentation/blob/main/specs/messages/message-dictionary.csv
7. dissect.target, plugins/os/unix/log/auth.py (PkexecService). https://github.com/fox-it/dissect.target/blob/main/dissect/target/plugins/os/unix/log/auth.py
8. UAC, artifacts/files/system/polkit.yaml·artifacts/system/suid.yaml·artifacts/system/getcap.yaml. https://github.com/tclahr/uac/blob/main/artifacts/files/system/polkit.yaml , https://github.com/tclahr/uac/blob/main/artifacts/system/suid.yaml , https://github.com/tclahr/uac/blob/main/artifacts/system/getcap.yaml
9. Velociraptor, artifacts/definitions/Linux/Sys/SUID.yaml·Users/RootUsers.yaml. https://github.com/Velocidex/velociraptor/blob/master/artifacts/definitions/Linux/Sys/SUID.yaml , https://github.com/Velocidex/velociraptor/blob/master/artifacts/definitions/Linux/Users/RootUsers.yaml
10. systemd, man/systemd-coredump.xml. https://github.com/systemd/systemd/blob/main/man/systemd-coredump.xml
11. Volatility 3, plugins/linux/check_creds.py·capabilities.py. https://github.com/volatilityfoundation/volatility3/tree/develop/volatility3/framework/plugins/linux
12. Ali Hadi, Mariam Khader, Thomas Claflin, "Learning Linux Forensic Analysis and Why it Matters", DFRWS 발표 자료. https://dfrws.org/presentation/learning-linux-forensic-analysis-and-why-it-matters/
