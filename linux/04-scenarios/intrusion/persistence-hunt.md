---
title: "무엇이 계속 살아남게 했나"
parent: "시나리오 · 침해"
nav_order: 1080
---

# 무엇이 계속 살아남게 했나 (Persistence Hunt)

재부팅·로그인·정해진 시각·장치 연결 같은 계기가 올 때마다 공격자의 코드를 다시 실행하게 만든 장치를 찾고, 그 장치를 언제 누가 만들었으며 실제로 돌았는지까지 가리는 조사입니다.

## 조사 질문

침입이 확인된 서버에서 "공격자가 다시 돌아오거나 코드를 계속 돌릴 수 있게 남겨 둔 것이 있는가" 를 묻습니다. 지속성 (persistence) 장치 하나를 찾았다고 끝나지 않고, 계기별로 빠짐없이 훑은 뒤 장치마다 세 가지를 답합니다. 누가 만든 것인지(패키지가 깐 것인지 사람이 만든 것인지), 언제 만들었는지, 실제로 실행된 기록이 있는지입니다.

이 쪽은 찾는 순서와 해석만 다룹니다. 장치마다 파일 형식·로그 문구·함정은 아티팩트 사전의 지속성 갈래 아홉 쪽에 있고, 여기서는 그 쪽으로 링크합니다. 침입 경로와 침입 시각은 [SSH 로 들어왔나](ssh-intrusion.md), [웹 서버가 뚫렸나](web-compromise.md), [권한을 올렸나](privilege-escalation.md) 에서 먼저 잡아 두면 이 쪽의 기준 시각으로 씁니다.

## 먼저 확인할 것

**배포판과 판.** 같은 장치라도 경로가 배포판마다 다릅니다. 사용자 crontab 은 Ubuntu 에서 `/var/spool/cron/crontabs/사용자이름`, RHEL 에서 `/var/spool/cron/사용자이름` 입니다[1][2]. rc.local 실제 파일은 Ubuntu 가 `/etc/rc.local`, RHEL 9 가 `/etc/rc.d/rc.local` 이고, RHEL 9 의 `/etc/rc.local` 은 그 파일을 가리키는 링크입니다[8][9]. 이런 차이는 아래 표에 모아 두었습니다.

**시간대.** 파일 시스템 시각(mtime·ctime·btime)은 UTC 기준 epoch 값이고[17], cron 로그와 Debian crontab 머리의 설치 시각은 현지 시각입니다([cron·anacron·at](../../02-artifacts/persistence/cron-at.md)). 검체의 시간대를 [호스트 이름·시간대·로캘](../../02-artifacts/system-info/hostname-timezone.md) 에서 먼저 정합니다.

**사용자.** `/root` 를 포함해 모든 홈 폴더를 목록으로 뽑아 둡니다. 사용자 crontab, 사용자 systemd 유닛, `~/.ssh/`, 셸 시작 파일, 데스크톱 자동 실행이 모두 홈 폴더 아래에 있습니다. 로그인하지 않아도 사용자 유닛을 돌리게 하는 linger 표시는 `/var/lib/systemd/linger/사용자이름` 파일이라[7], 이 폴더도 함께 봅니다.

**수집 범위.** 전원을 끈 뒤 뜬 디스크 이미지에는 `/run` 아래가 없습니다. 생성기 출력(`/run/systemd/generator*`), 일시 유닛(`/run/systemd/transient`), Ubuntu 의 `/run/motd.dynamic` 이 그렇습니다[6][14]. 이 폴더들이 필요하면 [라이브 응답 수집](../../03-techniques/acquisition/live-response.md) 결과나 메모리 이미지에서 찾고, 디스크 이미지에서는 이 폴더를 만드는 쪽(생성기 실행 파일, rc.local, `/etc/update-motd.d/`)을 봅니다. 패키지 데이터베이스(`/var/lib/dpkg/`, `/var/lib/rpm/`)도 수집 범위에 들어 있어야 뒤의 패키지 대조를 할 수 있습니다.

## 볼 아티팩트와 순서

### 계기별로 찾을 곳

| 계기 | 찾을 곳 | 알려 주는 것 | 링크 |
|---|---|---|---|
| 정해진 시각 | 사용자 crontab, `/etc/crontab`, `/etc/cron.d/*`, `/etc/cron.{hourly,daily,weekly,monthly}/`, `/etc/anacrontab`, at 잡 | 명령·주기·실행 계정, at 잡의 실행 예정 시각 | [cron·anacron·at](../../02-artifacts/persistence/cron-at.md) |
| 부팅·서비스 | 시스템 유닛 검색 경로(`/etc/systemd/system`, `/usr/local/lib/systemd/system`, `/usr/lib/systemd/system` 등), `.wants/` 링크, `이름.service.d/*.conf` 드롭인, 타이머 | 부팅 때나 정해진 시각에 켜지는 서비스와 그 실행 명령 | [systemd 서비스와 타이머](../../02-artifacts/persistence/systemd-units.md) |
| 부팅(생성기) | `/etc/systemd/system-generators/*`, `/usr/local/lib/systemd/system-generators/*` 등 | 부팅 초기에 유닛을 만들어 내는 실행 파일[6] | [systemd 서비스와 타이머](../../02-artifacts/persistence/systemd-units.md) |
| 부팅(옛 방식) | init 스크립트, `rcN.d` 링크, rc.local | systemd 가 호환 기능으로 돌리는 스크립트 | [init 스크립트와 rc.local](../../02-artifacts/persistence/sysv-init.md) |
| 사용자 서비스 | `~/.config/systemd/user/`, `/etc/systemd/user/` 등, linger 표시 | 그 사용자의 사용자 관리자가 돌리는 유닛[6][7] | [systemd 서비스와 타이머](../../02-artifacts/persistence/systemd-units.md) |
| 셸 로그인 | `~/.bashrc`, `~/.profile`, `/etc/profile.d/*` 등 | 대화형 셸이 뜰 때마다 읽는 명령 | [셸 시작 파일](../../02-artifacts/persistence/shell-startup.md) |
| SSH 로그인 | `~/.ssh/authorized_keys`(키 옵션 포함), `~/.ssh/rc`, `/etc/ssh/sshrc`, `~/.ssh/environment` | 들어올 수 있는 키, 로그인 때 도는 명령 | 아래 "로그인 때 도는 것" |
| SSH 로그인(Ubuntu) | `/etc/update-motd.d/*` | SSH 로그인마다 도는 스크립트 | 아래 "로그인 때 도는 것" |
| 모든 동적 실행 | `/etc/ld.so.preload` | 동적 링크 프로그램마다 먼저 싣는 라이브러리 | [공유 라이브러리 가로채기](../../02-artifacts/persistence/ld-preload.md) |
| 인증 | `/etc/pam.d/*`, PAM 모듈 `.so` 파일 | 인증·세션 단계에 끼워 넣은 모듈이나 명령 | [PAM 모듈 변조](../../02-artifacts/persistence/pam-backdoor.md) |
| 커널 | `/etc/modules-load.d/*.conf`, `/etc/modprobe.d/*`, 적재된 모듈 | 부팅 때 싣는 모듈, 모듈을 실을 때 대신 도는 명령 | [커널 모듈](../../02-artifacts/persistence/kernel-modules.md), [루트킷 찾기](../../03-techniques/analysis/rootkit-detection.md) |
| 장치 연결 | `/etc/udev/rules.d/*` 의 `RUN` | 장치가 붙거나 바뀔 때 도는 명령 | [udev 규칙](../../02-artifacts/persistence/udev-rules.md) |
| 데스크톱 로그인 | `~/.config/autostart/*.desktop`, `/etc/xdg/autostart/` | 그래픽 세션이 뜰 때 도는 프로그램 | [데스크톱 자동 실행](../../02-artifacts/persistence/xdg-autostart.md) |
| 권한 규칙 | `/etc/sudoers.d/*`, polkit 규칙(`/etc/polkit-1`, `/usr/share/polkit-1`, `/var/lib/polkit-1` 등)[22] | 암호 없이 권한을 얻게 풀어 둔 규칙 | [sudo 설정](../../01-foundations/users-auth/sudoers.md) |
| 컨테이너 | 재시작 정책이 걸린 컨테이너 | 데몬이 뜰 때마다 다시 뜨는 컨테이너 | [Docker](../../02-artifacts/containers/docker/index.md) |

### 배포판마다 다른 경로

| 항목 | Ubuntu 24.04 LTS | RHEL 9 |
|---|---|---|
| 사용자 crontab | `/var/spool/cron/crontabs/사용자이름`[2] | `/var/spool/cron/사용자이름`[1] |
| at 잡 | 빌드할 때 configure 가 정하고, `/var/spool/atjobs` 가 없고 `/var/spool/cron` 이 있으면 `/var/spool/cron/atjobs` 입니다. 검체에서 실제 폴더를 확인합니다[5] | `/var/spool/at`[4] |
| rc.local | `/etc/rc.local`[8] | `/etc/rc.d/rc.local`, 패키지가 권한 `0644` 로 설치[9] |
| 로그인 때 도는 motd 스크립트 | `/etc/update-motd.d/`[13][14] | sshd PAM 설정에 `pam_motd.so` 줄은 있지만[25], 스크립트 폴더를 돌리는 update-motd 패치가 pam 패키지에 없음[26] |

### 로그인 때 도는 것

SSH 로 로그인할 때 sshd 가 실행하는 것은 [SSH 로 들어왔나](ssh-intrusion.md) 에서 넘겨받은 부분이라 여기서 모아 둡니다. 설정 키와 키 옵션의 뜻은 [SSH](../../02-artifacts/logins/ssh/index.md) 아래 쪽에 있습니다.

- **키 옵션 `command="…"`.** 이 키로 인증하면 사용자가 보낸 명령 대신 이 명령을 실행합니다[12]. 백업 전용 키 같은 정상 용도도 있어서, 옵션이 있다는 사실보다 명령의 내용과 키가 들어간 시각을 봅니다.
- **`~/.ssh/rc`.** 이 파일이 있고 `PermitUserRC` 가 켜져 있으면(기본 `yes`) 사용자의 셸이나 명령보다 먼저 실행되고, 없으면 `/etc/ssh/sshrc` 가 실행됩니다[12]. 키 옵션 `restrict`·`no-user-rc` 가 붙은 키로 들어오면 `~/.ssh/rc` 를 돌리지 않습니다[12].
- **`~/.ssh/environment` 와 `environment="…"`.** 로그인 환경 변수를 더하지만 `PermitUserEnvironment` 가 켜져 있을 때만 적용되고 기본은 `no` 입니다[12]. 설정 조각에서 이 값을 바꾼 흔적과 함께 봅니다.
- **Ubuntu 의 update-motd.** Ubuntu 24.04 의 `/etc/pam.d/sshd` 에는 `session optional pam_motd.so motd=/run/motd.dynamic` 줄이 있습니다[13]. Ubuntu 가 붙인 `pam_motd` 패치는 `noupdate` 옵션이 없으면 세션을 열 때 `run-parts --lsbsysinit /etc/update-motd.d > /run/motd.dynamic.new` 를 실행하고, 성공하면 결과를 `/run/motd.dynamic` 으로 바꿔 놓습니다[14]. 그래서 `/etc/update-motd.d/` 에 더한 스크립트는 SSH 로그인마다 돌고, authorized_keys 만 보면 놓칩니다. 라이브 시스템이면 `/run/motd.dynamic` 의 수정 시각이 이 스크립트들이 마지막으로 끝까지 돈 때에 가까울 가능성이 있습니다.

### 실제로 돌았는지 보여 주는 짝 기록

장치가 있다는 것과 그 장치가 실행됐다는 것은 다른 사실이라, 장치마다 짝이 되는 실행 기록을 찾습니다.

| 장치 | 짝 기록 | 링크 |
|---|---|---|
| cron | 잡 시작 `CMD` 줄. RHEL 의 cronie 는 `(사용자) 이벤트 (내용)` 모양으로 남기고, `crontab` 명령으로 바꾸면 `REPLACE`·`BEGIN EDIT`·`END EDIT` 줄이 남습니다[1] | [cron·anacron·at](../../02-artifacts/persistence/cron-at.md) |
| systemd 서비스·타이머 | 저널의 유닛 시작 메시지와 `INVOCATION_ID`, 타이머 stamp 파일, 감사 로그의 `SERVICE_START`(1130)·`SERVICE_STOP`(1131)[10][11] | [systemd 서비스와 타이머](../../02-artifacts/persistence/systemd-units.md) |
| SSH 로그인 때 도는 것 | sshd 인증 성공 줄, pam_unix 세션 줄, wtmp | [인증 로그](../../02-artifacts/logins/auth-log.md), [로그인 기록](../../02-artifacts/logins/wtmp-btmp-lastlog.md) |
| 무엇이든 | 감사 로그 실행 레코드, 프로세스 회계 | [감사 로그의 실행 기록](../../02-artifacts/execution/auditd-execve.md), [프로세스 회계](../../02-artifacts/execution/process-accounting.md) |
| 라이브·메모리 | 지금 도는 프로세스와 부모 관계 | [실행 중인 프로세스 (/proc)](../../02-artifacts/execution/proc.md), [메모리 분석](../../03-techniques/analysis/memory-analysis.md) |

## 분석 흐름

1. **기준 시각을 정합니다.** 침입 경로를 다룬 쪽에서 잡은 첫 침입 시각을 UTC 로 적어 둡니다. 이 시각이 없으면 가장 이른 이상 로그인이나 가장 이른 이상 파일을 임시 기준으로 삼습니다.

2. **계기별 목록을 만듭니다.** 위 표의 위치를 하나도 빼지 않고 파일 목록(경로·소유자·권한·크기·mtime·ctime·btime)으로 뽑습니다. 수집 도구 하나에 기대면 빈틈이 생깁니다. ForensicArtifacts 의 `LinuxScheduleFiles`, `LinuxServices`, `LinuxLoaderSystemPreloadFile`, `KernelModules`, `LinuxUdevRules`, `LinuxPamConfigs`, `XDGAutostartEntries`, `SSHAuthorizedKeysFiles` 같은 정의가 계기마다 있지만[21], 서비스 정의는 디렉터리 바로 아래 `*.service` 만 가리켜 드롭인, `/usr/local/lib/systemd/system`, 생성기 실행 파일이 빠지고, `system.attached` 를 `systemd.attached` 로 적어 두었습니다[6][21]. 도구별 빈틈은 각 아티팩트 쪽의 함정 절에 있습니다.

3. **패키지가 깐 것과 사람이 만든 것을 가릅니다.** 목록의 파일마다 소속 패키지를 찾습니다. Debian·Ubuntu 는 `dpkg-query -S`(`dpkg -S`)가 그 파일이 든 패키지를 찾고[16], RHEL 은 `rpm -q -f` 가 같은 일을 합니다[15]. 소속 패키지가 없는 파일이 이 조사의 중심 후보입니다. 소속 패키지가 있으면 `rpm -V`·`dpkg -V` 로 설치 뒤에 바뀌었는지 봅니다. `rpm -V` 는 파일마다 아홉 글자를 찍고, 자리마다 `S` 크기, `M` 모드(권한·파일 종류), `5` 다이제스트, `D` 장치 번호, `L` 링크 대상, `U` 사용자, `G` 그룹, `T` 수정 시각, `P` capabilities 가 다르다는 뜻이며 `.` 은 통과, `?` 는 검사할 수 없었다는 뜻입니다[15]. `dpkg -V` 는 dpkg 1.17.2 부터 있고, 지금은 데이터베이스에 md5sum 이 있는 파일의 md5sum 하나만 실제로 비교합니다[16]. 출력 읽는 법과 기준값을 믿을 수 있는지는 [패키지 파일 변조 확인](../../02-artifacts/packages/package-verify.md) 에 있습니다.

4. **만든 시각을 좁힙니다.** 후보 파일의 btime(파일을 만든 때, 뒤에 바뀌지 않음)과 ctime(내용이나 소유자·권한 같은 아이노드 정보를 바꿀 때 바뀜)을 mtime 과 함께 봅니다[17]. `.wants/` 링크처럼 켜 둘 때 생기는 링크는 링크 자체의 시각을 읽습니다. 기준이 되는 파일을 정해 그 뒤에 더해진 파일을 찾는 방법도 있습니다. 발표된 한 침해 사례에서는 `/var/log/lastlog` 를 기준 파일로 삼아 `find 루트 -type f -newercm 기준파일` 로 로그인 뒤에 더해진 파일을 찾았고, 그 사례에서 PHP 웹셸이 systemd 서비스로 등록돼 있었습니다[23]. 파일 시각을 한 시간축에 올리는 방법은 [타임라인 만들기](../../03-techniques/analysis/timeline.md) 에 있습니다.

5. **실제로 돌았는지 확인합니다.** 위 "짝 기록" 표로 장치마다 실행 흔적을 찾습니다. cron 이면 그 명령의 `CMD` 줄이, systemd 유닛이면 그 유닛의 시작 메시지와 stamp 파일이, SSH 로그인 때 도는 것이면 그 계정의 로그인 시각이 짝입니다. 짝 기록이 첫 실행 시각을 알려 주면, 그 시각이 4단계에서 좁힌 만든 시각보다 뒤인지 맞춰 봅니다.

6. **보호 장치를 봅니다.** 지우거나 고치지 못하게 불변 (immutable) 속성 `i` 를 걸어 둔 파일이 있는지 봅니다. 이 속성이 걸린 파일은 지우거나 이름을 바꾸거나 쓰기로 열 수 없고, root 나 `CAP_LINUX_IMMUTABLE` 이 있는 프로세스만 이 속성을 걸거나 풀 수 있습니다[18]. 라이브에서는 `lsattr` 로 보고[18], Velociraptor `Linux.Forensics.ImmutableFiles` 는 ext4 를 직접 읽어 이 플래그가 선 파일을 찾습니다[19]. 이 아티팩트의 기본 검색 범위는 `/home/*` 뿐이라, `SearchFilesGlob` 을 위 표의 지속성 경로로 넓혀 돌립니다[19]. 속성을 읽는 법은 [권한·확장 속성·ACL·Capabilities](../../01-foundations/filesystem/permissions-xattr.md) 에 있습니다.

7. **목록을 닫습니다.** 장치마다 "위치 · 소속 패키지 · 만든 시각 · 실행 기록 · 실행 계정" 을 한 줄로 적습니다. 실행 파일이나 스크립트가 가리키는 대상 파일도 같은 방법으로 가르고, 해시를 떠서 [해시·YARA 검사](../../03-techniques/analysis/hash-yara.md) 로 넘깁니다.

## 흔한 오판

- **도구 결과가 깨끗하면 없다고 봅니다.** dissect.target `services` 는 `/etc/systemd/system`, `/lib/systemd/system`, `/usr/lib/systemd/system` 바로 아래 파일만 읽고 `.d` 로 끝나는 드롭인 폴더는 건너뜁니다[20]. `/usr/local/lib/systemd/system`, 사용자 유닛, 생성기는 이 결과에 나오지 않습니다. cron 쪽도 dissect.target `cronjobs` 는 at 잡과 anacron 시각 파일을 읽지 않고[20], Velociraptor `Linux.Sys.Crontab` 의 기본 검색 범위는 `/etc/crontab`, `/etc/cron.d/**`, `/var/at/tabs/**`, `/var/spool/cron/**` 와 `/etc/cron.{daily,hourly,monthly,weekly}/*` 입니다[19]. 결과가 비었을 때는 도구가 어디를 봤는지부터 확인합니다.
- **파일이 있으면 실행됐다고 봅니다.** Debian 계열 cron 은 `/etc/cron.d/` 안 파일 이름에 점이 들어 있으면 실행하지 않습니다[3]. rc.local 은 실행 권한이 있을 때만 `rc-local.service` 로 이어지고[8], RHEL 9 는 이 파일을 `0644` 로 깝니다[9]. XDG 자동 실행 항목은 `Hidden=true` 이거나 `TryExec` 가 가리키는 프로그램이 없으면 실행하지 않습니다[24]. 짝 기록이 없으면 "설정이 있었다" 까지만 씁니다.
- **SSH 지속성을 authorized_keys 에서만 찾습니다.** `command=` 옵션, `~/.ssh/rc`, `/etc/ssh/sshrc`, Ubuntu 의 `/etc/update-motd.d/` 도 SSH 로그인 때 돕니다[12][14]. 키 파일 말고도 `AuthorizedKeysCommand` 로 키를 받을 수 있으므로 [SSH](../../02-artifacts/logins/ssh/index.md) 쪽의 설명대로 sshd 설정도 봅니다.
- **`rpm -V`·`dpkg -V` 가 조용하면 손대지 않았다고 봅니다.** 두 명령은 패키지에 든 파일만 검사하므로 새로 더한 파일은 결과에 나오지 않습니다[15][16]. `dpkg -V` 는 무결성 검사일 뿐 보안 검증이 아닙니다[16]. RHEL 9 의 systemd 패키지는 rc.local 을 `%verify(owner group) %config(noreplace)` 로 표시했고[9], `%verify` 는 `rpm -V` 가 보는 항목을 정하는 지시어라[15] 이 파일은 내용이나 권한을 바꿔도 `rpm -V` 에 나오지 않을 가능성이 있습니다.
- **mtime 을 심은 시각으로 단정합니다.** mtime 은 `utime` 같은 호출로 바꿀 수 있습니다[17]. ctime·btime, 링크 자체의 시각, cron·저널의 짝 기록과 맞춰 봅니다. 시각 조작은 [시각을 조작했나](../insider/time-manipulation.md) 에서 다룹니다.
- **`crontab` 로그가 없으면 crontab 을 바꾸지 않았다고 봅니다.** `REPLACE`·`END EDIT` 는 `crontab` 명령만 남기므로[1], spool 파일이나 `/etc/cron.d/` 를 직접 고치면 이 줄이 없습니다.
- **하나 찾고 멈춥니다.** 한 장치를 지워도 다른 장치가 다시 만들어 놓는 구성도 있으므로 계기별 목록을 끝까지 채웁니다.

## 보고서 문장 예

아래 값은 모두 만든 예시입니다(호스트 web01, 계정 alice, 파일 이름 `sys-update-helper.service`, 기준 시각 2026-03-12 05:05 UTC).

- "web01 의 `/etc/systemd/system/sys-update-helper.service` 는 설치된 어느 패키지에도 속하지 않고, 이 파일의 생성 시각(btime)은 2026-03-12 05:41 UTC 입니다. 같은 이름의 `multi-user.target.wants/` 링크가 같은 분에 생겼습니다."
- "같은 부팅 구간의 저널에 이 유닛이 2026-03-12 05:42 UTC 와 재부팅 뒤인 2026-03-13 00:10 UTC 에 시작된 기록이 있습니다."
- "`/home/alice/.ssh/authorized_keys` 는 2026-03-12 05:20 UTC 에 마지막으로 바뀌었고(ctime), sshd 기록에는 이 파일의 두 번째 줄 키와 지문이 같은 키로 2026-03-14 에 두 번 로그인한 기록이 있습니다."

기록은 장치가 있었고 그 시각에 돌았다는 것까지 보여 줍니다. 만든 사람은 파일 시각과 같은 시간대의 로그인·sudo·감사 기록으로 계정까지 좁힐 수 있고, 계정 뒤의 사람을 잇는 방법은 [누가 그 명령을 실행했나](../attribution/user-attribution.md) 에 있습니다. 짝 기록이 없는 장치는 "설정돼 있었다" 로만 쓰고 "실행됐다" 고 쓰지 않습니다.

## 함께 볼 페이지

- [cron·anacron·at](../../02-artifacts/persistence/cron-at.md), [systemd 서비스와 타이머](../../02-artifacts/persistence/systemd-units.md) — 가장 흔히 쓰는 두 장치의 형식·로그·함정
- [패키지 파일 변조 확인](../../02-artifacts/packages/package-verify.md) — `dpkg -V`·`debsums`·`rpm -V` 결과 읽기
- [SSH](../../02-artifacts/logins/ssh/index.md) — authorized_keys 와 sshd 설정
- [루트킷 찾기](../../03-techniques/analysis/rootkit-detection.md) — 커널 모듈과 숨긴 프로세스
- [타임라인 만들기](../../03-techniques/analysis/timeline.md) — 장치를 만든 시각과 실행 기록을 한 시간축에
- [흔적을 지웠나](../insider/anti-forensics.md) — 장치를 지운 뒤 남는 흔적
- [SSH 로 들어왔나](ssh-intrusion.md), [웹 서버가 뚫렸나](web-compromise.md), [채굴기가 돌았나](cryptominer.md) — 기준 시각을 잡는 쪽

## 참고 문헌

1. cronie, `configure.ac`·`src/misc.c`·`src/crontab.c`·`src/do_command.c`. https://github.com/cronie-crond/cronie
2. Ubuntu cron 패키지(noble), `debian/patches/Debian-paths-and-commands.patch`. https://git.launchpad.net/ubuntu/+source/cron/tree/debian/patches?h=ubuntu/noble
3. vixie-cron(Debian cron 3.0pl1 계열), `cron.8`. https://github.com/svagner/vixie-cron
4. CentOS Stream 9 at 패키지, `at.spec`. https://gitlab.com/redhat/centos-stream/rpms/at/-/blob/c9s/at.spec
5. Debian at, `configure.ac`. https://salsa.debian.org/debian/at
6. systemd, `man/systemd.unit.xml`·`man/systemd.generator.xml`. https://github.com/systemd/systemd/tree/main/man
7. systemd, `src/login/logind-dbus.c`. https://github.com/systemd/systemd/blob/main/src/login/logind-dbus.c
8. systemd v255, `man/systemd-rc-local-generator.xml`·`meson_options.txt`. https://github.com/systemd/systemd/tree/v255
9. CentOS Stream 9 systemd 패키지, `systemd.spec`. https://gitlab.com/redhat/centos-stream/rpms/systemd/-/blob/c9s/systemd.spec
10. systemd, `src/core/service.c`. https://github.com/systemd/systemd/blob/main/src/core/service.c
11. linux-audit, audit-documentation `specs/messages/message-dictionary.csv`. https://github.com/linux-audit/audit-documentation/tree/main/specs
12. OpenSSH portable, `sshd.8`·`sshd_config.5`. https://github.com/openssh/openssh-portable
13. Ubuntu openssh 패키지(noble-updates), `debian/openssh-server.sshd.pam.in`. https://git.launchpad.net/ubuntu/+source/openssh/tree/debian?h=ubuntu/noble-updates
14. Ubuntu pam 패키지(noble), `debian/patches/update-motd`. https://git.launchpad.net/ubuntu/+source/pam/tree/debian/patches/update-motd?h=ubuntu/noble
15. RPM, `docs/man/rpm.8.scd`·`docs/man/rpm-spec.5.scd`. https://github.com/rpm-software-management/rpm/tree/master/docs/man
16. dpkg, `man/dpkg.pod`·`man/dpkg-query.pod`. https://github.com/guillemj/dpkg/tree/main/man
17. man-pages, `man7/inode.7`. https://github.com/mkerrisk/man-pages/blob/master/man7/inode.7
18. e2fsprogs, `misc/chattr.1.in`. https://github.com/tytso/e2fsprogs/blob/master/misc/chattr.1.in
19. Velociraptor, `artifacts/definitions/Linux/Forensics/ImmutableFiles.yaml`·`Linux/Sys/Crontab.yaml`. https://github.com/Velocidex/velociraptor/tree/master/artifacts/definitions/Linux
20. dissect.target, `plugins/os/unix/linux/services.py`·`plugins/os/unix/cronjobs.py`. https://github.com/fox-it/dissect.target/tree/main/dissect/target/plugins/os/unix
21. ForensicArtifacts, `artifacts/data/linux.yaml`. https://github.com/ForensicArtifacts/artifacts/blob/main/artifacts/data/linux.yaml
22. UAC, `artifacts/files/system/polkit.yaml`. https://github.com/tclahr/uac/blob/main/artifacts/files/system/polkit.yaml
23. Ali Hadi, Mariam Khader, Thomas Claflin, "Learning Linux Forensic Analysis and Why it Matters", DFRWS 발표 자료. https://dfrws.org/presentation/learning-linux-forensic-analysis-and-why-it-matters/
24. freedesktop.org, Desktop Application Autostart Specification, `autostart-spec.xml`. https://gitlab.freedesktop.org/xdg/xdg-specs/-/blob/master/autostart/autostart-spec.xml
25. CentOS Stream 9 openssh 패키지, `sshd.pam`. https://gitlab.com/redhat/centos-stream/rpms/openssh/-/tree/c9s
26. CentOS Stream 9 pam 패키지, `pam.spec`. https://gitlab.com/redhat/centos-stream/rpms/pam/-/blob/c9s/pam.spec
