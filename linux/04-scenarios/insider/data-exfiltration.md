---
title: "자료를 밖으로 옮겼나"
parent: "시나리오 · 유출·은폐"
nav_order: 1090
---

# 자료를 밖으로 옮겼나 (Data Exfiltration)

## 조사 질문

이 호스트의 자료가 언제, 어느 계정으로, 어떤 경로로 밖으로 나갔는지를 묻습니다. 경로는 크게 외부 저장 장치, SSH 계열 전송(scp·sftp·rsync), 클라우드 동기화·전송 프로그램, 메일·브라우저 업로드로 나눠 봅니다.

기록 대부분은 "장치가 붙었다", "세션이 열렸다", "명령을 쳤다", "설정이 있다" 까지만 말합니다. "그 파일이 나갔다" 까지 말하는 기록은 설정을 바꿔 둔 검체에서만 나오는 경우가 많으므로, 조사는 각 경로에서 어느 단계까지 기록이 남는지를 먼저 가르는 데서 시작합니다. 이 쪽은 조사 순서와 해석만 다루고, 로그 줄의 구조와 파일 형식은 아래 표의 아티팩트 쪽에서 다룹니다.

## 먼저 확인할 것

**배포판과 프로그램 판.** 판은 [배포판과 버전](../../02-artifacts/system-info/os-release.md)과 패키지 기록([dpkg·apt](../../02-artifacts/packages/dpkg-apt.md), [rpm·dnf](../../02-artifacts/packages/rpm-dnf.md))으로 정합니다. 이 쪽에서 판이 중요한 프로그램은 둘입니다. OpenSSH 는 Ubuntu 24.04 패키지가 9.6p1 이고[5], CentOS Stream 9 패키지가 9.9p1 입니다[6]. udisks 는 판에 따라 사용자 번호가 들어간 마운트 줄을 남기지 않을 수 있으므로, 판별 차이는 [마운트 기록](../../02-artifacts/devices/mounts.md)에서 확인합니다.

**로그 수준 설정.** 전송과 관련된 sshd 줄 대부분은 기본 수준보다 한 단계 높은 `VERBOSE` 에서만 나옵니다. sshd 의 `LogLevel` 기본값은 `INFO` 이고[4], sftp-server 의 `-l` 기본값은 `ERROR` 입니다[2]. 그래서 로그를 뒤지기 전에 검체의 `/etc/ssh/sshd_config` 와 `sshd_config.d/` 조각에서 `LogLevel` 과 `Subsystem sftp` 줄부터 읽습니다([sshd 설정](../../02-artifacts/logins/ssh/sshd-config.md)).

| 항목 | Ubuntu 24.04 | RHEL 9 계열 |
|---|---|---|
| 기본 `Subsystem sftp` 줄 | `/usr/lib/openssh/sftp-server`[5] | 검체의 설정에서 확인. 패키지는 sftp-server 를 `/usr/libexec/openssh/sftp-server` 에 설치[6] |
| sshd 로그 분야 | 기본 `AUTH`[4] → `/var/log/auth.log` | 패키지 설정이 `SyslogFacility AUTHPRIV` 로 바꿈[6] → `/var/log/secure` |
| sftp-server 로그 분야(`-f` 기본 `AUTH`)[2] | `/var/log/auth.log` | RHEL 의 secure 규칙은 authpriv 만 고르므로 `/var/log/messages` |

분야별로 어느 파일에 들어가는지는 [인증 로그](../../02-artifacts/logins/auth-log.md)의 rsyslog 규칙 표를 따릅니다. 기본 `Subsystem` 줄에는 `-l` 인자가 없으므로, 두 배포판 모두 기본 설치에서는 sftp 로 오간 파일별 기록이 남지 않습니다.

**시간대.** 저널은 UTC 로 저장하고, RHEL 의 전통 형식 syslog 줄에는 연도와 시간대가 없습니다. 장치 기록, 인증 로그, 셸 기록을 한 줄로 세우기 전에 [호스트 이름·시간대](../../02-artifacts/system-info/hostname-timezone.md)에서 검체의 시간대를 정합니다.

**수집 범위.** 라이브 수집인지 디스크 이미지인지 확인합니다. `/run` 아래 udisks 상태 파일, 휘발 저널, 살아 있는 연결과 프로세스는 전원을 끈 이미지에 없습니다([라이브 응답 수집](../../03-techniques/acquisition/live-response.md)). 조사 대상 계정뿐 아니라 `/root` 를 포함한 모든 홈의 `~/.ssh/`, `~/.config/`, 셸 기록 파일이 수집 범위에 들어 있어야 합니다.

## 볼 아티팩트와 순서

| 순서 | 아티팩트 | 알려 주는 것 | 링크 |
|---|---|---|---|
| 1 | 인증 로그·로그인 기록 | 그 시간대에 누가 어디서 들어와 있었나 | [인증 로그](../../02-artifacts/logins/auth-log.md), [sshd 로그](../../02-artifacts/logins/ssh/sshd-logs.md), [로그인 기록](../../02-artifacts/logins/wtmp-btmp-lastlog.md) |
| 2 | 셸 명령 기록 | `scp`·`rsync`·`rclone`·`tar` 명령 문자열 | [셸 명령 기록](../../02-artifacts/execution/shell-history/index.md) |
| 3 | USB·마운트 기록 | 장치 연결, 마운트 지점, 마운트를 요청한 uid | [USB 장치 연결 기록](../../02-artifacts/devices/usb.md), [마운트 기록](../../02-artifacts/devices/mounts.md) |
| 4 | sshd·sftp 설정과 로그 | 전송 세션, 세션 바이트 수, 파일별 기록이 남는 설정인지 | [sshd 설정](../../02-artifacts/logins/ssh/sshd-config.md), [sshd 로그](../../02-artifacts/logins/ssh/sshd-logs.md) |
| 5 | known_hosts·클라이언트 설정 | 이 호스트에서 SSH 로 나간 목적지 | [known_hosts 와 클라이언트 설정](../../02-artifacts/logins/ssh/known-hosts.md) |
| 6 | 감사 로그 | 명령 실행, mount 시스템 호출, 감시 파일 읽기 | [감사 로그의 실행 기록](../../02-artifacts/execution/auditd-execve.md), [감사 로그의 파일 감시](../../02-artifacts/file-activity/auditd-watches.md) |
| 7 | 프로세스 회계 | 명령 이름·사용자·시각(인자 없음) | [프로세스 회계](../../02-artifacts/execution/process-accounting.md) |
| 8 | 동기화·전송 프로그램, 메일 클라이언트, 브라우저 | 원격 저장소 설정, 보낸 메일, 업로드 사이트 방문 | 아래 분석 흐름 5단계, [Linux 의 브라우저 프로필](../../02-artifacts/desktop/browsers.md) |
| 9 | 방화벽·VPN | 나가는 연결 기록(설정돼 있을 때) | [방화벽](../../02-artifacts/network/firewall.md), [VPN](../../02-artifacts/network/vpn.md) |
| 10 | 메모리 | 살아 있는 연결·프로세스, 아직 파일에 쓰지 않은 셸 기록 | [메모리 분석](../../03-techniques/analysis/memory-analysis.md) |

## 분석 흐름

1. **시간 창을 정합니다.** 조사 대상 계정이 로그인해 있던 시간대를 인증 로그의 `Accepted` 줄과 세션 끝 줄로 먼저 잡습니다. 이 시간 창 안에서 아래 경로를 하나씩 봅니다. scp·sftp 처럼 터미널이 없는 접속은 wtmp 에 남지 않으므로 `last` 결과만으로 시간 창을 정하지 않습니다([SSH 로 들어왔나](../intrusion/ssh-intrusion.md)).

2. **셸 기록에서 전송 명령을 찾습니다.** `scp`, `sftp`, `rsync`, `rclone`, `tar`, `zip`, `curl`, `wget` 같은 명령 줄은 무엇을 어디로 옮기려 했는지를 가장 직접 보여 줍니다. 셸 기록에는 줄마다 시각이 없는 경우가 많고 일부 명령은 저장되지 않으므로, 시각과 빠짐 조건은 [셸 명령 기록](../../02-artifacts/execution/shell-history/index.md)과 [기록 지우기와 끄기](../../02-artifacts/execution/shell-history/evasion.md)에서 확인합니다. 감사 규칙이 있는 검체라면 [감사 로그의 실행 기록](../../02-artifacts/execution/auditd-execve.md)에서 같은 명령의 인자와 시각을 맞춰 봅니다. [프로세스 회계](../../02-artifacts/execution/process-accounting.md)에는 명령 이름만 있고 인자가 없으므로 "그 시각에 `scp` 가 실행됐다" 까지만 보여 줍니다.

3. **외부 저장 장치를 봅니다.** 커널은 USB 장치를 붙일 때 `New USB device found, idVendor=%04x, idProduct=%04x, bcdDevice=%2x.%02x`, 뗄 때 `USB disconnect, device number %d` 를 남깁니다[7]. 시리얼 번호와 `sd` 장치 이름으로 잇는 방법은 [USB 장치 연결 기록](../../02-artifacts/devices/usb.md)에서 다룹니다. 데스크톱에서 자동 마운트했다면 udisks 2.9.4 는 `Mounted %s at %s on behalf of uid %u` 와 `Unmounted %s on behalf of uid %u` 를 남기고, fstab 항목이면 `(system)` 이 붙습니다[8]. 장치 기록 가운데 사용자 번호가 들어가는 것은 사실상 이 줄뿐이므로 연결 시각과 로그인 시간 창을 이 줄로 잇습니다.

    감사 규칙이 있는 검체라면 mount 시스템 호출도 봅니다. audit-userspace 가 싣는 STIG 예시 규칙에는 로그인 사용자(`auid>=1000`)의 `mount`·`mount_setattr` 호출을 `key=export` 로 남기는 줄이 있고[9], 이 규칙이 검체의 `/etc/audit/rules.d/` 에 있으면 `ausearch -k export` 로 찾습니다. 이 규칙은 예시일 뿐 배포판 기본 설정이 아닙니다. 이 규칙으로 마운트를 요청한 사용자를 바르게 남기려면 자동 마운트를 모두 끄고 손으로 마운트해야 하므로[9], 데스크톱 자동 마운트는 이 키로 잡히지 않을 가능성이 있습니다.

4. **SSH 계열 전송을 봅니다.** OpenSSH 9.0 부터 scp 는 기본으로 SFTP 프로토콜을 쓰고, `-O` 를 주면 옛 SCP 프로토콜을 씁니다[1]. 그래서 보낸 쪽 클라이언트가 9.0 이상이면 받는 서버의 로그에서 scp 전송도 sftp 서브시스템 세션으로 보일 가능성이 높습니다. sshd 가 남기는 줄은 다음과 같고, 줄 서식은 OpenSSH 8.7p1·9.6p1·최신 코드에서 같습니다[3].

    | 줄 | 수준 | 뜻 |
    |---|---|---|
    | `Starting session: subsystem 'sftp' for 이름 from IP port 포트 id N` | VERBOSE | sftp 서브시스템 세션을 열었습니다 |
    | `Starting session: command for 이름 from IP port 포트 id N` | VERBOSE | 명령 하나를 실행하는 세션이고, 명령 문자열은 남기지 않습니다 |
    | `subsystem request for sftp by user 이름` | debug2 | 기본 설정에서는 남지 않습니다. 실패일 때만 `… failed, …` 줄이 INFO 로 남습니다 |
    | `Close session: user 이름 from IP port 포트 id N` | VERBOSE | 세션을 닫았습니다 |
    | `Transferred: sent N, received M bytes` | VERBOSE | 연결이 끝날 때 연결 전체의 송수신 바이트 수입니다 |

    명령 세션에 명령 문자열이 없는 것은 코드가 사생활 보호를 이유로 일부러 뺀 것입니다[3]. `Transferred:` 는 sshd 가 보낸 바이트를 `sent`, 받은 바이트를 `received` 로 적으므로, 서버에서 자료를 가져간 경우는 `sent` 쪽이 큽니다[3]. 이 값은 패킷 단위로 센 연결 전체의 양이라서 파일 하나의 크기와 맞지 않습니다.

    sftp-server 에 `-l INFO` 이상을 준 검체라면 파일 단위 기록이 남습니다. INFO 수준에서 남는 줄은 아래와 같습니다[2].

    ```
    session opened for local user 이름 from [IP]
    open "경로" flags READ mode 0NNN
    close "경로" bytes read N written M
    remove name "경로"
    rename old "경로" new "경로"
    mkdir name "경로" mode 0NNN
    set "경로" modtime 시각
    session closed for local user 이름 from [IP]
    ```

    `flags` 자리에는 `READ`, `WRITE`, `APPEND`, `CREATE`, `TRUNCATE`, `EXCL` 가운데 해당하는 것을 쉼표로 이어 적습니다[2]. `close` 줄의 `bytes read` 는 서버 쪽 파일에서 읽어 클라이언트로 보낸 양이고, `bytes written` 은 클라이언트에서 받아 파일에 쓴 양입니다[2]. 서버에서 파일을 가져갔는지는 `read` 쪽으로 봅니다. `set "경로" modtime` 은 클라이언트가 파일의 수정 시각을 맞춰 달라고 요청한 흔적이며, 시각 해석은 [시각을 조작했나](time-manipulation.md)와 이어집니다. `internal-sftp` 는 sshd 안에서 돌지만 sshd 의 `LogLevel` 과 `SyslogFacility` 를 따르지 않으므로 로그 수준과 분야를 인자로 따로 줘야 합니다[4].

    이 호스트가 보낸 쪽이라면 목적지는 계정의 `~/.ssh/known_hosts` 와 `~/.ssh/config` 에 남습니다. Ubuntu 는 `/etc/ssh/ssh_config` 에 `HashKnownHosts yes` 를 넣어 두므로 호스트 이름과 주소가 해시로 저장됩니다[5]. 후보 목적지를 해시해 맞추는 방법은 [known_hosts 와 클라이언트 설정](../../02-artifacts/logins/ssh/known-hosts.md)에서 다룹니다. Velociraptor `Linux.Ssh.KnownHosts` 는 사용자마다 `.ssh/known_hosts*` 를 찾아 항목별로 호스트·키 종류·공개 키를 내고, 여러 호스트에서 모은 호스트 공개 키로 해시된 이름을 풀어 보는 질의도 함께 싣습니다[13].

5. **동기화·전송 프로그램을 찾습니다.** 아래 경로 가운데 rclone 은 프로그램 설명서가 밝힌 위치이고, 나머지는 공개 수집 도구가 Linux 에서 모으는 위치입니다. 내부 형식은 프로그램 판마다 다르므로 검체에서 확인합니다.

    | 프로그램 | 경로 |
    |---|---|
    | rclone | 찾는 순서대로 실행 파일과 같은 폴더의 `rclone.conf`, `$XDG_CONFIG_HOME/rclone/rclone.conf`, `~/.config/rclone/rclone.conf`, `~/.rclone.conf`[10] |
    | Dropbox | `~/.dropbox`[11] |
    | Synology Drive | `~/.SynologyDrive/data`, `~/.SynologyDrive/log`[11] |
    | QNAP Qsync | `~/.local/share/QNAP/Qsync`[11] |
    | Aspera Connect | `~/.aspera/connect/filelists`, `~/.aspera/connect/var/log`, `~/.aspera/connect/var/asperaconnect.data`[11] |
    | FileZilla | `~/.config/filezilla` 의 `*.xml*`·`*.sqlite3*`, Flatpak 판은 `~/.var/app/org.filezillaproject.Filezilla`[11] |
    | Thunderbird | `~/.thunderbird`, `~/.var/app/org.mozilla.Thunderbird`, `~/snap/thunderbird` 아래 `*/Mail/*`, `*/ImapMail/*`, `*/Attachments/*`, `global-messages-db.sqlite*`[11] |
    | wget | `~/.wget-hsts`[11] |

    rclone 설정 파일은 원격 저장소마다 `[이름]` 절과 `type = …` 줄로 이루어지고, 비밀번호는 가린(obscured) 형태로 들어갑니다[10]. 이 파일은 어떤 원격 저장소를 설정해 두었는지를 보여 줍니다. rclone 은 기본으로 로그를 표준 오류로 내보내고 `--log-file` 을 줘야 파일에 씁니다[10]. 그래서 셸 기록의 rclone 명령 줄이나 `--log-file` 로 지정한 파일이 없으면 무엇을 옮겼는지는 남지 않습니다.

    `~/.wget-hsts` 는 탭으로 나뉜 줄마다 호스트, 포트, 하위 도메인 포함 여부, 처음 더한 시각, 유효 기간을 담습니다[12]. HTTPS 로 HSTS 머리를 보낸 호스트만 남으므로 wget 으로 접속한 모든 호스트의 목록이 아닙니다. 브라우저로 올렸는지는 [Linux 의 브라우저 프로필](../../02-artifacts/desktop/browsers.md)에서 방문 기록과 다운로드 기록을 봅니다. 기록 구조는 [크롬 계열 브라우저](https://urock-ailab.github.io/forensics-handbook/windows/02-artifacts/browsers/chrome-edge-whale/index.html)와 [파이어폭스](https://urock-ailab.github.io/forensics-handbook/windows/02-artifacts/browsers/firefox/index.html) 쪽에서 다룹니다.

6. **모으고 묶은 흔적을 봅니다.** 여러 파일을 한 번에 옮기려면 대개 한곳에 모으거나 압축합니다. Velociraptor `Linux.Detection.AnomalousFiles` 는 기본으로 `/home/**,tmp/**` 에서 이름이 점으로 시작하는 파일, 10485760 바이트(10 MiB)보다 큰 파일, SUID 파일을 찾아 주므로[13], 홈과 임시 폴더에 큰 압축 파일이 생겼는지 훑는 출발점으로 씁니다. 찾은 파일의 생성·변경 시각은 [타임라인 만들기](../../03-techniques/analysis/timeline.md)로 로그인 시간 창과 맞춥니다. 지운 압축 파일은 [임시 폴더와 메모리 파일 시스템](../../02-artifacts/file-activity/tmp-shm.md), [휴지통](../../02-artifacts/file-activity/trash.md), [지운 파일 되살리기](../../03-techniques/analysis/file-recovery.md)에서 찾고, 어떤 문서를 열었는지는 [최근 연 파일](../../02-artifacts/execution/recently-used.md)과 [썸네일 캐시](../../02-artifacts/file-activity/thumbnails.md)가 거듭니다.

7. **두 호스트를 맞춥니다.** 받는 쪽 서버를 조사할 수 있다면, 보낸 쪽의 셸 기록과 받는 쪽의 인증 로그를 시각과 주소로 짝지어 봅니다. 한 침해 사례 발표에서는 한 서버의 `.bash_history` 와 다른 서버의 auth.log 를 맞춰, 공격자가 SSH 키로 다른 서버에 로그인해 옮겨 간 흐름을 찾았습니다[14].

## 흔한 오판

- **"서버 로그에 scp 가 없으니 scp 로 옮기지 않았다."** 9.0 이상 클라이언트의 scp 는 SFTP 로 동작하므로[1] 서버 쪽에는 sftp 서브시스템 세션으로 남을 수 있습니다. 반대로 `-O` 옛 방식은 서브시스템이 아닌 명령 세션(`Starting session: command`)으로 보일 가능성이 높습니다.
- **"`subsystem request for sftp` 줄이 없으니 sftp 를 쓰지 않았다."** 이 줄은 debug2 수준이라 기본 설정에서 나오지 않습니다[3]. `VERBOSE` 로 설정된 검체에서는 `Starting session: subsystem 'sftp'` 줄을 봅니다.
- **"`Transferred:` 크기가 문서 크기와 비슷하니 그 문서를 보냈다."** 이 값은 패킷 단위로 센 연결 전체의 바이트 수입니다[3]. 여러 파일과 셸 출력이 섞이므로 "양이 맞는다" 까지만 말합니다.
- **"마운트했으니 복사했다."** 커널과 udisks 줄은 연결과 마운트까지만 보여 주고, 장치에 무엇을 썼는지는 이 호스트의 로그에 없습니다. 원본 파일의 접근 시각으로 복사를 주장하려면 마운트 옵션부터 확인해야 하는데, 기본 `relatime` 에서는 접근 시각이 드물게만 바뀝니다([마운트 기록](../../02-artifacts/devices/mounts.md)).
- **"`/media/사용자/` 가 비었으니 USB 를 쓰지 않았다."** udisks 는 해제할 때 레이블 폴더를 지웁니다([마운트 기록](../../02-artifacts/devices/mounts.md)).
- **"`last` 에 없으니 접속이 없었다."** scp·sftp·명령 하나만 실행한 접속은 터미널이 없어 wtmp 에 남지 않습니다([SSH 로 들어왔나](../intrusion/ssh-intrusion.md)).
- **"known_hosts 에 있으니 자료를 보냈다."** known_hosts 항목은 그 서버에 접속한 적이 있다는 기록일 뿐입니다.
- **"동기화 폴더에 있으니 올렸다."** 동기화 폴더에 파일이 있다는 것만으로 올렸다고 하지 않고, 프로그램의 로그와 데이터베이스로 판단합니다.
- **"RHEL 의 secure 에 sftp 줄이 없으니 기록이 없다."** sftp-server 의 기본 분야는 `AUTH` 이고[2], RHEL 의 secure 규칙은 `authpriv` 만 고릅니다([인증 로그](../../02-artifacts/logins/auth-log.md)). `/var/log/messages` 와 저널을 함께 봅니다.
- **"수집 도구 목록의 경로를 그대로 쓰면 된다."** 수집 도구에는 macOS 전용 경로도 섞여 있습니다. 예를 들어 UAC 의 Google Drive·Box 항목은 `Library` 아래 macOS 경로만 모읍니다[11].

## 보고서 문장 예

아래 값은 모두 만든 예시입니다.

- "2025-03-04 14:10(UTC)부터 14:25(UTC) 사이에 계정 alice 로 198.51.100.20 에서 SSH 세션이 열려 있었고, 같은 연결이 끝날 때 sshd 가 `Transferred: sent 1288490188, received 20480 bytes` 를 남겼습니다. 이 값은 연결 전체의 양이며 어떤 파일이 오갔는지는 이 기록에 없습니다."
- "같은 날 14:02(UTC)에 USB 저장 장치(idVendor=abcd)가 연결되었고, udisks 가 uid 1000(alice)을 대신해 `/dev/sdb1` 을 `/media/alice/EXAMPLE` 에 마운트한 기록이 있습니다. 장치에 어떤 파일을 썼는지는 이 호스트의 기록으로 확인되지 않습니다."
- "sftp-server 가 `-l INFO` 로 설정된 이 서버의 `/var/log/auth.log` 에 `close "/srv/share/plan.xlsx" bytes read 48213 written 0` 줄이 있습니다. 이 시각에 이 파일을 sftp 로 읽어 간 기록입니다."

## 함께 볼 페이지

- [SSH 로 들어왔나](../intrusion/ssh-intrusion.md) — 로그인 시간 창과 인증 방법을 정하는 법
- [흔적을 지웠나](anti-forensics.md) — 옮긴 뒤 셸 기록·로그를 지운 흔적
- [시각을 조작했나](time-manipulation.md) — 파일 시각을 되돌린 흔적
- [누가 그 명령을 실행했나](../attribution/user-attribution.md) — 계정과 사람을 잇는 법
- [타임라인 만들기](../../03-techniques/analysis/timeline.md) — 여러 기록을 한 시간 축에 놓기
- [Linux 포렌식 보고서](../../03-techniques/reporting/forensic-report.md) — 기록이 말하는 만큼만 쓰는 법

## 참고 문헌

1. OpenSSH portable, scp.1 (`-O`, HISTORY). https://github.com/openssh/openssh-portable/blob/master/scp.1
2. OpenSSH portable, sftp-server.8 (`-f`, `-l`) · sftp-server.c (`handle_log_close`, `string_from_portable`, `logit` 호출). https://github.com/openssh/openssh-portable/blob/master/sftp-server.8 , https://github.com/openssh/openssh-portable/blob/master/sftp-server.c
3. OpenSSH portable, session.c · sshd-session.c, 대조용 V_9_6_P1·V_8_7_P1 태그의 session.c · sshd.c. https://github.com/openssh/openssh-portable/blob/master/session.c , https://github.com/openssh/openssh-portable/blob/master/sshd-session.c , https://github.com/openssh/openssh-portable/tree/V_9_6_P1 , https://github.com/openssh/openssh-portable/tree/V_8_7_P1
4. OpenSSH portable, sshd_config.5 (`LogLevel`, `Subsystem`) · sshd_config. https://github.com/openssh/openssh-portable/blob/master/sshd_config.5 , https://github.com/openssh/openssh-portable/blob/master/sshd_config
5. Ubuntu, openssh 패키지 noble-updates (changelog, debian-config.patch). https://git.launchpad.net/ubuntu/+source/openssh/tree/debian?h=ubuntu/noble-updates
6. CentOS Stream 9, openssh 패키지 (openssh.spec, openssh-7.7p1-redhat.patch). https://gitlab.com/redhat/centos-stream/rpms/openssh/-/tree/c9s
7. Linux, drivers/usb/core/hub.c. https://github.com/torvalds/linux/blob/master/drivers/usb/core/hub.c
8. udisks 2.9.4, src/udiskslinuxfilesystem.c. https://github.com/storaged-project/udisks/blob/udisks-2.9.4/src/udiskslinuxfilesystem.c
9. linux-audit, audit-userspace rules/30-stig.rules. https://github.com/linux-audit/audit-userspace/tree/master/rules
10. rclone, docs/content/docs.md (`--config`, `--log-file`, Logging). https://github.com/rclone/rclone/blob/master/docs/content/docs.md
11. UAC, artifacts/files/applications (rclone, dropbox, synology_drive, qnap_qsync, aspera_connect, filezilla, thunderbird, wget, google_drive, box). https://github.com/tclahr/uac/tree/main/artifacts/files/applications
12. fox-it dissect.target, dissect/target/plugins/apps/shell/wget.py. https://github.com/fox-it/dissect.target/blob/main/dissect/target/plugins/apps/shell/wget.py
13. Velocidex velociraptor, artifacts/definitions/Linux/Detection/AnomalousFiles.yaml · Linux/Ssh/KnownHosts.yaml. https://github.com/Velocidex/velociraptor/tree/master/artifacts/definitions/Linux
14. Ali Hadi, Mariam Khader, Thomas Claflin, "Learning Linux Forensic Analysis and Why it Matters", DFRWS 발표 슬라이드. https://dfrws.org/presentation/learning-linux-forensic-analysis-and-why-it-matters/
